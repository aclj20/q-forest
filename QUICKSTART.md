# 🚀 Quick Start Guide

Get Q-FOREST Backend API up and running in minutes!

## Prerequisites

- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Git** (for cloning the repository)

## Method 1: Automated Setup (Recommended)

### Step 1: Run Setup Script

```bash
./setup.sh
```

This script will:
- Create Python virtual environment
- Install all Python dependencies
- Create necessary directories

### Step 2: Start Backend API

```bash
cd backend
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Access API Documentation

Navigate to: **http://localhost:8000/docs**

🎉 Your API is ready to use!

---

## Method 2: Manual Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate virtual environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create directories
mkdir -p uploads results

# 6. Start server
python main.py
```

---

## 🎯 Using the API

### Method 1: Using curl

#### 1. Process an Image (Preprocessing)

```bash
curl -X POST http://localhost:8000/process \
  -F "file=@preprocessing/data/map.png" \
  -F "nodes=9"
```

Response:
```json
{
  "success": true,
  "job_id": "abc-123",
  "nodes": 9,
  "grid_size": "3x3",
  "files": {
    "visualization": "/results/abc-123/..._visualization.png",
    "benefits_csv": "/results/abc-123/..._benefits.csv",
    "costs_csv": "/results/abc-123/..._costs.csv"
  },
  "statistics": {
    "num_nodes": 9,
    "num_edges": 12,
    "density": 0.5,
    "avg_benefit": 0.45,
    "avg_cost": 65.23
  }
}
```

**Note:** Benefits are normalized 0-1, Costs are in range 30-100

#### 2. Highlight Selected Nodes (Postprocessing - NEW!)

```bash
# Create a selection matrix CSV
echo "1,0,1" > selection.csv
echo "0,1,0" >> selection.csv
echo "1,0,1" >> selection.csv

# Highlight the selected nodes
curl -X POST http://localhost:8000/highlight \
  -F "file=@preprocessing/data/map.png" \
  -F "selection_matrix=@selection.csv" \
  -F "nodes=9"
```

Response:
```json
{
  "success": true,
  "job_id": "xyz-789",
  "nodes": 9,
  "grid_size": "3x3",
  "selected_nodes": 5,
  "total_nodes": 9,
  "selection_percentage": 55.56,
  "file": {
    "highlighted_visualization": "/results/xyz-789/..._highlighted.png"
  }
}
```

**Visual Features:** 🟨 Yellow overlay on selected cells, ✅ Checkmarks on nodes

#### 3. Download Results

```bash
# Download benefits CSV
curl http://localhost:8000/download/{job_id}/{filename} -o benefits.csv

# Download costs CSV
curl http://localhost:8000/download/{job_id}/{filename} -o costs.csv

# Download visualization
curl http://localhost:8000/download/{job_id}/{filename} -o visualization.png
```

#### Get Node Options

```bash
curl http://localhost:8000/node-options
```

### Method 2: Using Python requests

```python
import requests

# Process image
with open('path/to/image.png', 'rb') as f:
    files = {'file': f}
    data = {'nodes': 9}
    response = requests.post('http://localhost:8000/process', files=files, data=data)
    result = response.json()
    
print(result)

# Download results
job_id = result['job_id']
benefits_url = f"http://localhost:8000{result['files']['benefits_csv']}"
costs_url = f"http://localhost:8000{result['files']['costs_csv']}"

benefits = requests.get(benefits_url)
with open('benefits.csv', 'wb') as f:
    f.write(benefits.content)
```

### Method 3: Using Swagger UI

1. Open http://localhost:8000/docs in browser
2. Click on `/process` endpoint
3. Click "Try it out"
4. Upload file and enter nodes count
5. Click "Execute"
6. View response and download links

---

## 📊 Valid Node Counts

Choose from these perfect square values:
- **4** = 2×2 grid (fast, minimal detail)
- **9** = 3×3 grid (default, balanced)
- **16** = 4×4 grid
- **25** = 5×5 grid
- **36** = 6×6 grid
- **49** = 7×7 grid
- **64** = 8×8 grid
- **81** = 9×9 grid
- **100** = 10×10 grid
- **121** = 11×11 grid
- **144** = 12×12 grid (slow, maximum detail)

💡 **Tip**: Start with 9 nodes for quick testing

---

## 🧪 Testing with Sample Data

```bash
# Process sample image
curl -X POST http://localhost:8000/process \
  -F "file=@preprocessing/data/map.png" \
  -F "nodes=9"

# Or use map2.png
curl -X POST http://localhost:8000/process \
  -F "file=@preprocessing/data/map2.png" \
  -F "nodes=16"
```

---

## 🛑 Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError`
```bash
# Solution: Activate virtual environment and install dependencies
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

**Error**: `Address already in use`
```bash
# Solution: Port 8000 is occupied
# Option 1: Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Option 2: Use different port
uvicorn main:app --port 8001
```

**Error**: `No module named 'image_to_graph'`
```bash
# Solution: Make sure you're in the backend directory
# The code imports from ../preprocessing/
cd backend
python main.py
```

### Image Processing Fails

**Error**: `Invalid node count`
```bash
# Solution: Use perfect squares only
# Valid: 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144
```

**Error**: `Processing timeout`
```bash
# Solution: Try smaller node count
# Large images + many nodes = longer processing time
```

**Error**: `File not found`
```bash
# Solution: Check file path is correct
# Use absolute path or path relative to where you run curl
```

---

## 🔧 API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API status |
| GET | `/health` | Health check |
| POST | `/process` | Process image (file + nodes) |
| GET | `/download/{job_id}/{filename}` | Download results |
| GET | `/node-options` | Get valid node counts |
| GET | `/docs` | Swagger UI documentation |
| GET | `/redoc` | ReDoc documentation |

---

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [backend/README.md](backend/README.md) for API details
- See [preprocessing/USAGE.md](preprocessing/USAGE.md) for CLI usage
- Explore the API at http://localhost:8000/docs

---

## 💡 Integration Examples

### Node.js/JavaScript

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const formData = new FormData();
formData.append('file', fs.createReadStream('image.png'));
formData.append('nodes', '9');

axios.post('http://localhost:8000/process', formData, {
  headers: formData.getHeaders()
})
.then(response => console.log(response.data))
.catch(error => console.error(error));
```

### Python

```python
import requests

def process_image(image_path, nodes=9):
    url = 'http://localhost:8000/process'
    files = {'file': open(image_path, 'rb')}
    data = {'nodes': nodes}
    
    response = requests.post(url, files=files, data=data)
    return response.json()

result = process_image('preprocessing/data/map.png', nodes=9)
print(result)
```

### Shell Script

```bash
#!/bin/bash

# Process image and download results
IMAGE="preprocessing/data/map.png"
NODES=9

# Process
RESULT=$(curl -s -X POST http://localhost:8000/process \
  -F "file=@$IMAGE" \
  -F "nodes=$NODES")

echo "Processing complete!"
echo "$RESULT" | jq .

# Extract job_id and download files
JOB_ID=$(echo "$RESULT" | jq -r .job_id)
echo "Job ID: $JOB_ID"

# Download results
curl "http://localhost:8000/download/$JOB_ID/..." -o benefits.csv
curl "http://localhost:8000/download/$JOB_ID/..." -o costs.csv
```

---

## 🤝 Need Help?

- Check the [GitHub Issues](https://github.com/aclj20/q-forest/issues)
- Read the API docs at http://localhost:8000/docs
- Review the full documentation in README.md

---

**Happy Analyzing! 🌲📊**
