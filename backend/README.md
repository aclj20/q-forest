# Q-FOREST Backend

FastAPI server for processing heatmap images and generating graph data.

## 🚀 Quick Start

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at `http://localhost:8000`

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛠️ API Endpoints

### Health Check

```bash
GET /
GET /health
```

Returns API status

### Process Image

```bash
POST /process
Content-Type: multipart/form-data

Parameters:
  - file: image file (PNG, JPG, JPEG)
  - nodes: integer (4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144)

Response:
{
  "success": true,
  "job_id": "uuid",
  "nodes": 9,
  "grid_size": "3x3",
  "files": {
    "visualization": "/results/{job_id}/{name}_visualization.png",
    "benefits_csv": "/results/{job_id}/{name}_benefits.csv",
    "costs_csv": "/results/{job_id}/{name}_costs.csv"
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

### Highlight Selected Nodes

```bash
POST /highlight
Content-Type: multipart/form-data

Parameters:
  - file: image file (PNG, JPG, JPEG)
  - selection_matrix: CSV file with binary matrix (1=selected, 0=not)
  - nodes: integer (4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144)

Response:
{
  "success": true,
  "job_id": "uuid",
  "nodes": 9,
  "grid_size": "3x3",
  "selected_nodes": 5,
  "total_nodes": 9,
  "selection_percentage": 55.56,
  "file": {
    "highlighted_visualization": "/results/{job_id}/{name}_highlighted.png"
  }
}
```

### Download File

```bash
GET /download/{job_id}/{filename}
```

Downloads generated CSV or PNG files

### Get Node Options

```bash
GET /node-options

Response:
{
  "options": [
    {"value": 4, "label": "4 nodes (2x2 grid)"},
    {"value": 9, "label": "9 nodes (3x3 grid)"},
    ...
  ]
}
```

### Classical Optimization

```bash
POST /optimize/classic
Content-Type: multipart/form-data

Parameters:
  - benefits_file: Benefits matrix CSV file (normalized 0-1)
  - costs_file: Costs matrix CSV file (typically 30-100)
  - budget: Budget constraint (float, positive number)

Input Format:
  - CSV files without headers
  - Square matrices (n×n)
  - Benefits range: 0.0 to 1.0
  - Costs range: any positive values (typically 30-100)
  - Both matrices must have same dimensions

Example Benefits CSV (3×3):
  0.299683,0.505233,0.517674
  0.740297,0.622298,0.617919
  0.685802,0.779734,0.803188

Example Costs CSV (3×3):
  77.044622,49.278478,67.446216
  65.284379,80.631893,91.739316
  37.920959,76.246703,84.928428

Validation:
  - Matrix shapes must match
  - Budget must be positive
  - Files must be valid CSV format

Response:
{
  "success": true,
  "job_id": "uuid",
  "status": "optimal",
  "objective_value": 2.417,
  "selected_count": 4,
  "total_nodes": 9,
  "selection_percentage": 44.44,
  "total_benefit": 2.711,
  "total_cost": 228.73,
  "budget": 200.0,
  "budget_utilization": 114.37,
  "files": {
    "solution_matrix": "/results/{job_id}/{job_id}_solution.csv",
    "solution_binary": "/results/{job_id}/{job_id}_solution_binary.csv"
  },
  "matrix_shape": [3, 3]
}

Usage Example:
curl -X POST http://localhost:8000/optimize/classic \
  -F "benefits_file=@benefits.csv" \
  -F "costs_file=@costs.csv" \
  -F "budget=200.0"

Note: The solver uses SDP relaxation and may slightly exceed the budget
constraint (typically 5-15%). This is expected behavior.
```

## 📂 Directory Structure

```
backend/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── uploads/            # Temporary file uploads
└── results/            # Generated outputs
    └── {job_id}/
        ├── *_benefits.csv
        ├── *_costs.csv
        └── *_visualization.png
```

## 🔧 Configuration

### CORS

Currently configured to allow all origins:

```python
allow_origins=["*"]
```

For production, specify exact origins:

```python
allow_origins=["https://your-frontend-domain.com"]
```

### File Storage

- Uploaded files are temporarily stored in `uploads/`
- Results are stored in `results/{job_id}/`
- Files are automatically cleaned up after upload

## 🧪 Testing

```bash
# Health check
curl http://localhost:8000/health

# Process image (generates node graph)
curl -X POST http://localhost:8000/process \
  -F "file=@test_image.png" \
  -F "nodes=9"

# Run classical optimization
curl -X POST http://localhost:8000/optimize/classic \
  -F "benefits_file=@benefits.csv" \
  -F "costs_file=@costs.csv" \
  -F "budget=250.0"

# Highlight selected nodes
curl -X POST http://localhost:8000/highlight \
  -F "file=@test_image.png" \
  -F "selection_matrix=@selection.csv" \
  -F "nodes=9"

# Get node options
curl http://localhost:8000/node-options
```

## 📦 Dependencies

- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **python-multipart**: File upload handling
- **numpy**: Numerical computing
- **opencv-python**: Image processing
- **matplotlib**: Visualization
- **networkx**: Graph algorithms
- **Pillow**: Image handling
- **cvxpy**: Convex optimization
- **pandas**: Data manipulation

## 🐛 Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (e.g., invalid node count)
- `404`: File not found
- `500`: Server error

Error responses include detail messages:

```json
{
  "detail": "Error description"
}
```

## 🔒 Security Considerations

For production deployment:

1. **CORS**: Restrict allowed origins
2. **File Upload**: Add file size limits
3. **Rate Limiting**: Implement request throttling
4. **Authentication**: Add API key or OAuth
5. **File Cleanup**: Implement periodic cleanup of old results
6. **Input Validation**: Enhanced file type checking

## 🚀 Deployment

### Using Uvicorn

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Using Gunicorn (Production)

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker (Optional)

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📊 Performance

- Typical processing time: 2-10 seconds depending on:
  - Image size
  - Number of nodes
  - Server resources

## 🔍 Monitoring

Add logging for production:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## 📄 License

MIT License

---

## 🆕 Recent Changes

### October 2025 Updates

**New Endpoints:**
- `POST /highlight` - Highlight selected nodes with yellow cell overlays

**Data Changes:**
- **Cost Range**: Updated from 0-1 to 30-100 for realistic optimization
- **Benefits**: Remain normalized 0-1 (unchanged)

**Visualization Updates:**
- Removed colorbar from preprocessing output
- Added yellow transparent overlay (35% opacity) for selected cells
- Enhanced grid lines visibility (50% opacity, 1px thick)

**Postprocessing Features:**
- Entire grid cells highlighted, not just node circles
- Gold node markers with checkmarks (✓) on selected nodes
- Legend showing selected vs. non-selected counts
- Selection statistics in API response

