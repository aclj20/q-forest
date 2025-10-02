# Q-FOREST

**Quantum-inspired Forest Optimization & Resource Evaluation System**

A Python-based API for transforming spatial heatmap images into weighted graph networks, enabling advanced optimization algorithms for resource allocation and spatial analysis.

## 🌟 Features

- **🗺️ Heatmap Analysis**: Convert spatial heatmaps into weighted graph networks
- **🎯 Smart Detection**: Advanced color detection algorithms identify high-value areas
- **📊 Multiple Outputs**: Generate benefit matrices, cost matrices, and visualizations
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
└── preprocessing/        # Core image processing
    ├── image_to_graph.py
    └── data/
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

## 🎨 How It Works

1. **Image Analysis**: The system analyzes heatmap colors (pink/magenta and green areas)
2. **Grid Generation**: Creates a grid of nodes over the image
3. **Weight Calculation**: Assigns benefit weights based on color diversity
4. **Cost Generation**: Generates random costs for optimization algorithms
5. **Graph Creation**: Builds a NetworkX graph with adjacency information
6. **Visualization**: Overlays the graph on the original image
7. **Export**: Saves matrices and visualizations

## 📊 Output Files

For each processed image, you'll get:

- `{name}_benefits.csv` - Benefits matrix (normalized 0-1)
- `{name}_costs.csv` - Costs matrix (random 0-1)
- `{name}_visualization.png` - Graph overlay on original image

## 🛠️ Technology Stack

- **FastAPI** - Python web framework
- **Uvicorn** - ASGI server
- **NumPy** - Numerical computing
- **OpenCV** - Image processing
- **NetworkX** - Graph algorithms
- **Matplotlib** - Visualization
- **Pillow** - Image handling

## 🔧 API Endpoints

- `GET /` - API status
- `GET /health` - Health check
- `POST /process` - Process uploaded image
- `GET /download/{job_id}/{filename}` - Download result files
- `GET /node-options` - Get valid node count options

## 📝 Example Use Cases

- **Forest Management**: Identify optimal locations for conservation efforts
- **Urban Planning**: Analyze resource distribution in city planning
- **Environmental Studies**: Map ecological hotspots
- **Optimization Research**: Generate input data for quantum algorithms

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

## 👨‍💻 Authors

- Original preprocessing algorithm: Ariana Lopez
- API implementation: Q-FOREST Team

## 🐛 Issues

If you encounter any issues or have suggestions, please file an issue on GitHub.

## 🎓 Citation

If you use Q-FOREST in your research, please cite:

```
Q-FOREST: Quantum-inspired Forest Optimization & Resource Evaluation System
```

---

**Made with 🌲 for better resource management**
