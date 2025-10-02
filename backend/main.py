from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import sys
import os
import shutil
import numpy as np
from pathlib import Path
import uuid
from typing import List

# Add preprocessing directory to path
sys.path.append(str(Path(__file__).parent.parent / "preprocessing"))
from image_to_graph import HeatmapToGraph

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

