# Q-FOREST

python 3.9.23 

pip install -r requirements.txt
**Quantum-inspired Forest Optimization & Resource Evaluation System**

A Python-based API for transforming spatial heatmap images into weighted graph networks, enabling advanced optimization algorithms for resource allocation and spatial analysis.

## 🌟 Features

- **🗺️ Heatmap Analysis**: Convert spatial heatmaps into weighted graph networks
- **🎯 Smart Detection**: Advanced color detection algorithms identify high-value areas
- **📊 Multiple Outputs**: Generate benefit matrices, cost matrices, and visualizations
- **🎨 Node Highlighting**: Visualize selected nodes with yellow cell overlays (NEW!)
- **🌐 REST API**: FastAPI-powered backend for easy integration
- **⚡ Fast Processing**: Python-powered backend with efficient algorithms
- **💾 Data Export**: Download results in CSV and PNG formats

## 🏗️ Project Structure

```
q-forest/
├── backend/              # Python FastAPI server
│   ├── main.py          # API endpoints
│   ├── requirements.txt # Python dependencies
│   ├── uploads/         # Temporary file storage
│   └── results/         # Generated outputs
├── preprocessing/        # Core image processing
│   ├── image_to_graph.py
│   └── data/
├── postprocessing/       # Node highlighting
│   ├── highlight_nodes.py
│   └── example_selection.csv
├── classic/             # Classical optimization
│   ├── classic_solver.py
│   └── README.md
├── quantum-knapsack/    # Quantum optimization
└── frontend/            # Web UI (not yet implemented)
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**

### Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the API server
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📖 Usage

### Using the API

#### Process an Image

```bash
curl -X POST http://localhost:8000/process \
  -F "file=@path/to/your/image.png" \
  -F "nodes=9"
```

Response:
```json
{
  "success": true,
  "job_id": "uuid-here",
  "nodes": 9,
  "grid_size": "3x3",
  "files": {
    "visualization": "/results/{job_id}/..._visualization.png",
    "benefits_csv": "/results/{job_id}/..._benefits.csv",
    "costs_csv": "/results/{job_id}/..._costs.csv"
  },
  "statistics": {
    "num_nodes": 9,
    "num_edges": 12,
    "density": 0.5,
    "avg_benefit": 0.45,
    "avg_cost": 0.52
  }
}
```

#### Download Results

```bash
# Download benefits CSV
curl http://localhost:8000/download/{job_id}/{filename} -o benefits.csv

# Download costs CSV
curl http://localhost:8000/download/{job_id}/{filename} -o costs.csv

# Download visualization
curl http://localhost:8000/download/{job_id}/{filename} -o visualization.png
```

#### Get Available Node Options

```bash
curl http://localhost:8000/node-options
```

### Using the Command Line (Direct)

```bash
cd preprocessing
source .venv/bin/activate

# Basic usage (9 nodes)
python image_to_graph.py data/map.png

# Custom node count
python image_to_graph.py data/map.png --nodes 64

# Valid node counts: 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144
```

## 🌐 Web Frontend

### Prerequisites

- **Node.js 18+**
- **npm** o **yarn**

### Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev


The frontend will be available at http://localhost:9002

### Contributing

If you're interested in building a frontend for Q-FOREST:
- The backend API is fully functional and documented
- CORS is enabled for easy integration
- Check out `TESTING.md` for API usage examples
- Contributions are welcome! Please open an issue or PR

**Recommended Frontend Setup:**
```bash
# Example structure
frontend/
├── src/
│   ├── components/
│   │   ├── ImageUpload.tsx
│   │   ├── NodeSelector.tsx
│   │   └── Results.tsx
│   ├── services/
│   │   └── api.ts          # API client for Q-FOREST backend
│   └── App.tsx
└── package.json
```

The API is ready to accept requests from any frontend application!

## 🎨 How It Works

### Preprocessing
1. **Image Analysis**: Analyzes heatmap colors (pink/magenta and green areas)
2. **Grid Generation**: Creates a grid of nodes over the image (e.g., 6×6 for 36 nodes)
3. **Weight Calculation**: Assigns benefit weights (0-1) based on color diversity
4. **Cost Generation**: Generates column-based costs (leftmost column: 30, each column +15)
5. **Graph Creation**: Builds a NetworkX graph with adjacency information
6. **Visualization**: Overlays the graph on the original image

### Optimization (Classic Solver)
1. **SDP Formulation**: Uses semidefinite programming via CVXPY
2. **Objective**: Maximize total benefit subject to budget constraint
3. **Solution**: Returns continuous values (0-1) for each node
4. **Rounding**: Converts to binary (0/1) using 0.5 threshold
5. **Non-binary Detection**: Identifies fractional values for analysis

### Postprocessing
1. **Node Highlighting**: Overlays yellow cells on selected nodes
2. **Visual Enhancement**: Adds checkmarks and enhanced grid lines
3. **Statistics**: Displays selection count and percentage
4. **Export**: Saves highlighted visualization

## 📊 Output Files

### Preprocessing Output:
For each processed image, you'll get:

- `{name}_benefits.csv` - Benefits matrix (normalized 0-1, based on heatmap color diversity)
- `{name}_costs.csv` - Costs matrix (column-based: 30, 45, 60, 75, 90, 105, ...)
- `{name}_visualization.png` - Graph overlay on original image with grid

### Optimization Output:
After running the classical solver:

- `{name}_solution_matrix.csv` - Continuous solution (values 0-1)
- `{name}_solution_binary.csv` - Binary solution (0 or 1)
- Non-binary positions report (fractional values between 0 and 1)

### Postprocessing Output:
After highlighting selected nodes:

- `{name}_highlighted.png` - Visualization with yellow cell overlays on selected nodes
- Checkmarks on selected node centers
- Selection statistics overlay

## 🛠️ Technology Stack

- **FastAPI** - Python web framework
- **Uvicorn** - ASGI server
- **NumPy** - Numerical computing
- **OpenCV** - Image processing
- **NetworkX** - Graph algorithms
- **Matplotlib** - Visualization
- **Pillow** - Image handling

## 🔧 API Endpoints

### 🚀 Recommended: Full Pipeline
- `POST /optimize/full-pipeline` - **Complete workflow** (preprocessing → optimization → highlighting)

### Individual Endpoints
- `GET /` - API status
- `GET /health` - Health check
- `POST /process` - Process uploaded image and generate node graph (preprocessing)
- `POST /optimize/classic` - Run classical SDP optimization on benefits/costs matrices
- `POST /highlight` - Highlight selected nodes on visualization (postprocessing)
- `GET /download/{job_id}/{filename}` - Download result files
- `GET /node-options` - Get valid node count options

### Full Pipeline Endpoint

The `/optimize/full-pipeline` endpoint combines all three stages in a single API call:

```bash
curl -X POST http://localhost:8000/optimize/full-pipeline \
  -F "file=@map.png" \
  -F "nodes=36" \
  -F "budget=1200"
```

**Returns:**
- Preprocessing visualization with grid overlay
- Benefits and costs matrices (CSV)
- Optimization solution (continuous and binary matrices)
- Highlighted result showing selected nodes
- Complete statistics from all three stages

See `backend/README.md` for complete API documentation.

### Postprocessing: Node Highlighting

After generating a node graph, you can highlight specific nodes based on optimization results:

```bash
curl -X POST http://localhost:8000/highlight \
  -F "file=@image.png" \
  -F "selection_matrix=@selection.csv" \
  -F "nodes=9"
```

**Selection matrix format** (CSV with 1=selected, 0=not):
```csv
1,0,1
0,1,0
1,0,1
```

**Visual Features:**
- 🟨 **Yellow Cell Overlay**: Selected grid cells highlighted with 35% transparency
- ✅ **Checkmarks**: Selected nodes marked with gold circles and checkmarks
- 📊 **Statistics**: Shows selected vs. total nodes and selection percentage

**Example Response:**
```json
{
  "success": true,
  "job_id": "uuid",
  "selected_nodes": 5,
  "total_nodes": 9,
  "selection_percentage": 55.56,
  "file": {
    "highlighted_visualization": "/results/{job_id}/highlighted.png"
  }
}
```

## 📝 Example Use Cases

### Typical Workflow:
1. **Upload heatmap** → Process with Q-FOREST (e.g., 400 nodes)
2. **Run optimization** → Use benefits (0-1) and costs (30-100) matrices with classical or quantum algorithms
3. **Get solution** → Binary matrix of selected nodes
4. **Visualize results** → Highlight selected nodes with yellow overlays

### Complete API Workflow Example:

```bash
# Step 1: Process image to generate benefits and costs matrices
curl -X POST http://localhost:8000/process \
  -F "file=@map.png" \
  -F "nodes=9" \
  > process_result.json

# Extract job_id and download matrices
JOB_ID=$(cat process_result.json | jq -r '.job_id')
curl "http://localhost:8000/results/$JOB_ID/${JOB_ID}_9nodes_benefits.csv" -o benefits.csv
curl "http://localhost:8000/results/$JOB_ID/${JOB_ID}_9nodes_costs.csv" -o costs.csv

# Step 2: Run classical optimization
curl -X POST http://localhost:8000/optimize/classic \
  -F "benefits_file=@benefits.csv" \
  -F "costs_file=@costs.csv" \
  -F "budget=250.0" \
  > optimize_result.json

# Download solution matrix
OPT_JOB_ID=$(cat optimize_result.json | jq -r '.job_id')
curl "http://localhost:8000/results/$OPT_JOB_ID/${OPT_JOB_ID}_solution_binary.csv" -o solution.csv

# Step 3: Visualize results with highlighted nodes
curl -X POST http://localhost:8000/highlight \
  -F "file=@map.png" \
  -F "selection_matrix=@solution.csv" \
  -F "nodes=9" \
  > highlight_result.json

# Download final visualization
VIZ_JOB_ID=$(cat highlight_result.json | jq -r '.job_id')
curl "http://localhost:8000/results/$VIZ_JOB_ID/${VIZ_JOB_ID}_9nodes_highlighted.png" -o final_result.png
```

### Application Domains:
- **Forest Management**: Identify optimal locations for conservation efforts
- **Urban Planning**: Analyze resource distribution in city planning
- **Environmental Studies**: Map ecological hotspots
- **Optimization Research**: Generate input data for quantum/classical algorithms
- **Resource Allocation**: Visualize and compare different solution strategies

## 🔒 Security Considerations

For production deployment:

1. **CORS**: Restrict allowed origins in `backend/main.py`
2. **File Upload**: Add file size limits
3. **Rate Limiting**: Implement request throttling
4. **Authentication**: Add API key or OAuth
5. **File Cleanup**: Implement periodic cleanup of old results

## 🚀 Deployment

### Using Uvicorn (Development)

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Using Gunicorn (Production)

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy preprocessing module
COPY preprocessing/ /app/preprocessing/

# Copy backend
COPY backend/ /app/backend/

WORKDIR /app/backend

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🐛 Issues

If you encounter any issues or have suggestions, please file an issue on GitHub.

## 🎓 Citation

If you use Q-FOREST in your research, please cite:

```
Q-FOREST: Quantum-inspired Forest Optimization & Resource Evaluation System
```

## 🆕 Recent Updates

### Version 1.1.0 (October 2025)

**✨ New Features:**
- 🎨 **Postprocessing Module**: Highlight selected nodes on visualizations
- 🟨 **Yellow Cell Overlay**: Transparent highlighting of entire grid cells
- 📊 **Enhanced API**: New `/highlight` endpoint for result visualization

**🔧 Improvements:**
- 💰 **Cost Range Updated**: Changed from 0-1 to 30-100 for realistic optimization
- 🎨 **Cleaner Visualizations**: Removed colorbar from preprocessing output
- 📈 **Better Grid Lines**: Enhanced visibility with 50% opacity

**📊 Tested Configurations:**
- ✅ Small grids: 9 nodes (3×3)
- ✅ Medium grids: 64 nodes (8×8)
- ✅ Large grids: 400 nodes (20×20)

---

**Made with 🌲 for better resource management**
