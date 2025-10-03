import sys
import shutil
import uuid
from pathlib import Path

import numpy as np
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Add preprocessing, postprocessing, and classic directories to path
sys.path.append(str(Path(__file__).parent.parent / "preprocessing"))
sys.path.append(str(Path(__file__).parent.parent / "postprocessing"))
sys.path.append(str(Path(__file__).parent.parent / "classic"))
from image_to_graph import HeatmapToGraph
from highlight_nodes import NodeHighlighter
from classic_solver import ClassicSolver

app = FastAPI(title="Q-FOREST API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for uploads and results
UPLOAD_DIR = Path("uploads")
RESULTS_DIR = Path("results")
UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/results", StaticFiles(directory="results"), name="results")


@app.get("/")
async def root():
    return {"message": "Q-FOREST API is running", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/process")
async def process_image(
    file: UploadFile = File(...),
    nodes: int = Form(...)
):
    """
    Process uploaded image and generate graph with specified number of nodes
    """
    # Validate node count is a perfect square
    sqrt_nodes = int(np.sqrt(nodes))
    if sqrt_nodes * sqrt_nodes != nodes:
        raise HTTPException(
            status_code=400,
            detail=f"{nodes} is not a perfect square. Valid values: 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144"
        )
    
    # Generate unique ID for this processing job
    job_id = str(uuid.uuid4())
    
    try:
        # Save uploaded file
        upload_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
        with upload_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create HeatmapToGraph instance
        grid_size = (sqrt_nodes, sqrt_nodes)
        converter = HeatmapToGraph(grid_size=grid_size)
        
        # Load and process image
        converter.load_image(str(upload_path))
        converter.create_grid_nodes()
        converter.create_edges(connection_type="adjacent")
        
        # Generate output paths
        base_name = f"{job_id}_{nodes}nodes"
        result_dir = RESULTS_DIR / job_id
        result_dir.mkdir(exist_ok=True)
        
        # Export matrices
        benefits_csv_path = result_dir / f"{base_name}_benefits.csv"
        costs_csv_path = result_dir / f"{base_name}_costs.csv"
        visualization_path = result_dir / f"{base_name}_visualization.png"
        
        # Get matrices
        weight_matrix, weight_normalized = converter.get_weight_matrix()
        cost_matrix = converter.get_cost_matrix()
        
        # Save CSVs
        np.savetxt(benefits_csv_path, weight_normalized, delimiter=',', fmt='%.6f')
        np.savetxt(costs_csv_path, cost_matrix, delimiter=',', fmt='%.6f')
        
        # Generate visualization
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        converter.visualize_graph_on_image(save_path=str(visualization_path), show_weights=True)
        
        # Clean up matplotlib
        import matplotlib.pyplot as plt
        plt.close('all')
        
        # Get statistics
        stats = converter.get_graph_statistics()
        
        # Return results
        return JSONResponse(content={
            "success": True,
            "job_id": job_id,
            "nodes": nodes,
            "grid_size": f"{sqrt_nodes}x{sqrt_nodes}",
            "files": {
                "visualization": f"/results/{job_id}/{base_name}_visualization.png",
                "benefits_csv": f"/results/{job_id}/{base_name}_benefits.csv",
                "costs_csv": f"/results/{job_id}/{base_name}_costs.csv"
            },
            "statistics": {
                "num_nodes": stats.get('num_nodes'),
                "num_edges": stats.get('num_edges'),
                "density": round(stats.get('density', 0), 4),
                "avg_benefit": round(float(np.mean(weight_normalized)), 4),
                "avg_cost": round(float(np.mean(cost_matrix)), 4)
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
    
    finally:
        # Clean up uploaded file
        if upload_path.exists():
            upload_path.unlink()


@app.get("/download/{job_id}/{filename}")
async def download_file(job_id: str, filename: str):
    """
    Download generated CSV or PNG files
    """
    file_path = RESULTS_DIR / job_id / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )


@app.get("/node-options")
async def get_node_options():
    """
    Get valid node count options (perfect squares)
    """
    perfect_squares = [4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144]
    return {
        "options": [
            {"value": n, "label": f"{n} nodes ({int(np.sqrt(n))}x{int(np.sqrt(n))} grid)"}
            for n in perfect_squares
        ]
    }


@app.post("/highlight")
async def highlight_nodes(
    file: UploadFile = File(...),
    selection_matrix: UploadFile = File(...),
    nodes: int = Form(...)
):
    """
    Highlight selected nodes on heatmap visualization based on binary selection matrix
    
    Parameters:
    - file: Original heatmap image (PNG, JPG, JPEG)
    - selection_matrix: CSV file with binary matrix (1=selected, 0=not selected)
    - nodes: Number of nodes (must be perfect square: 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144)
    
    Returns:
    - JSON with highlighted visualization URL and statistics
    """
    # Validate node count is a perfect square
    sqrt_nodes = int(np.sqrt(nodes))
    if sqrt_nodes * sqrt_nodes != nodes:
        raise HTTPException(
            status_code=400,
            detail=f"{nodes} is not a perfect square. Valid values: 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144"
        )
    
    # Generate unique ID for this job
    job_id = str(uuid.uuid4())
    
    try:
        # Save uploaded image
        image_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
        with image_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Save uploaded selection matrix
        matrix_path = UPLOAD_DIR / f"{job_id}_selection.csv"
        with matrix_path.open("wb") as buffer:
            shutil.copyfileobj(selection_matrix.file, buffer)
        
        # Load and validate selection matrix
        try:
            sel_matrix = np.loadtxt(matrix_path, delimiter=',')
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid selection matrix format: {str(e)}. Must be CSV with comma-separated values."
            )
        
        # Validate matrix shape
        if sel_matrix.shape != (sqrt_nodes, sqrt_nodes):
            raise HTTPException(
                status_code=400,
                detail=f"Selection matrix shape {sel_matrix.shape} must match grid size ({sqrt_nodes}x{sqrt_nodes})"
            )
        
        # Validate matrix contains only 0s and 1s
        if not np.all(np.isin(sel_matrix, [0, 1])):
            raise HTTPException(
                status_code=400,
                detail="Selection matrix must contain only 0s and 1s"
            )
        
        # Create output directory
        result_dir = RESULTS_DIR / job_id
        result_dir.mkdir(exist_ok=True)
        
        # Generate output path
        base_name = f"{job_id}_{nodes}nodes"
        output_path = result_dir / f"{base_name}_highlighted.png"
        
        # Create highlighter and process
        grid_size = (sqrt_nodes, sqrt_nodes)
        highlighter = NodeHighlighter(str(image_path), grid_size)
        highlighter.load_and_process()
        
        # Highlight selected nodes
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        highlighter.highlight_selected_nodes(
            selection_matrix=sel_matrix,
            output_path=str(output_path),
            highlight_color=(255, 215, 0),  # Gold
            highlight_size=300
        )
        
        # Clean up matplotlib
        import matplotlib.pyplot as plt
        plt.close('all')
        
        # Count selected nodes
        selected_count = int(np.sum(sel_matrix))
        total_nodes = nodes
        
        # Return results
        return JSONResponse(content={
            "success": True,
            "job_id": job_id,
            "nodes": nodes,
            "grid_size": f"{sqrt_nodes}x{sqrt_nodes}",
            "selected_nodes": selected_count,
            "total_nodes": total_nodes,
            "selection_percentage": round((selected_count / total_nodes) * 100, 2),
            "file": {
                "highlighted_visualization": f"/results/{job_id}/{base_name}_highlighted.png"
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error highlighting nodes: {str(e)}")
    
    finally:
        # Clean up uploaded files
        if image_path.exists():
            image_path.unlink()
        if matrix_path.exists():
            matrix_path.unlink()


@app.post("/optimize/classic")
async def optimize_classic(
    benefits_file: UploadFile = File(...),
    costs_file: UploadFile = File(...),
    budget: float = Form(...)
):
    """
    Run classical optimization using semidefinite programming (SDP)
    
    Parameters:
    - benefits_file: Benefits matrix CSV file (normalized 0-1)
    - costs_file: Costs matrix CSV file (typically 30-100)
    - budget: Budget constraint (total cost allowed)
    
    Returns:
    - JSON with solution matrix and statistics
    """
    # Generate unique ID for this job
    job_id = str(uuid.uuid4())
    
    try:
        # Save uploaded files
        benefits_path = UPLOAD_DIR / f"{job_id}_benefits.csv"
        costs_path = UPLOAD_DIR / f"{job_id}_costs.csv"
        
        with benefits_path.open("wb") as buffer:
            shutil.copyfileobj(benefits_file.file, buffer)
        
        with costs_path.open("wb") as buffer:
            shutil.copyfileobj(costs_file.file, buffer)
        
        # Load matrices
        try:
            import pandas as pd
            benefits = pd.read_csv(benefits_path, header=None).values
            costs = pd.read_csv(costs_path, header=None).values
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid CSV format: {str(e)}"
            )
        
        # Validate matrix shapes match
        if benefits.shape != costs.shape:
            raise HTTPException(
                status_code=400,
                detail=f"Benefits shape {benefits.shape} must match costs shape {costs.shape}"
            )
        
        # Validate budget is positive
        if budget <= 0:
            raise HTTPException(
                status_code=400,
                detail="Budget must be positive"
            )
        
        # Create output directory
        result_dir = RESULTS_DIR / job_id
        result_dir.mkdir(exist_ok=True)
        
        # Run classical optimization
        solver = ClassicSolver()
        result = solver.solve(
            benefits=benefits,
            costs=costs,
            budget=budget,
            verbose=False  # Don't print to console in API
        )
        
        # Save solution matrix
        solution_path = result_dir / f"{job_id}_solution.csv"
        np.savetxt(solution_path, result['solution_matrix'], delimiter=',', fmt='%.5f')
        
        # Convert solution to binary for easier use
        binary_solution = (result['solution_matrix'] > 0.5).astype(int)
        binary_path = result_dir / f"{job_id}_solution_binary.csv"
        np.savetxt(binary_path, binary_solution, delimiter=',', fmt='%d')
        
        # Return results
        return JSONResponse(content={
            "success": True,
            "job_id": job_id,
            "status": result['status'],
            "objective_value": result['objective_value'],
            "selected_count": result['selected_count'],
            "total_nodes": int(benefits.size),
            "selection_percentage": round((result['selected_count'] / benefits.size) * 100, 2),
            "total_benefit": result['total_benefit'],
            "total_cost": result['total_cost'],
            "budget": result['budget'],
            "budget_utilization": round(result['budget_utilization'], 2),
            "files": {
                "solution_matrix": f"/results/{job_id}/{job_id}_solution.csv",
                "solution_binary": f"/results/{job_id}/{job_id}_solution_binary.csv"
            },
            "matrix_shape": list(benefits.shape)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running optimization: {str(e)}")
    
    finally:
        # Clean up uploaded files
        if benefits_path.exists():
            benefits_path.unlink()
        if costs_path.exists():
            costs_path.unlink()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
