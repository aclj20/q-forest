# 🧪 Testing Q-FOREST API

Complete guide for testing all endpoints with multiple methods.

## 🚀 Step 1: Start the Server

First, make sure the backend server is running:

```bash
cd backend

# Activate virtual environment
source .venv/bin/activate

# If you haven't set up yet, run:
# python3 -m venv .venv
# source .venv/bin/activate
# pip install -r requirements.txt

# Start the server
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 📋 Method 1: Interactive Swagger UI (Recommended for Beginners)

### Open in Browser

Navigate to: **http://localhost:8000/docs**

### Testing Each Endpoint:

#### 1. Test Health Check
- Click on `GET /health`
- Click **"Try it out"**
- Click **"Execute"**
- See response: `{"status": "healthy"}`

#### 2. Test Process Endpoint
- Click on `POST /process`
- Click **"Try it out"**
- Click **"Choose File"** and select an image (e.g., `../preprocessing/data/map.png`)
- Enter `nodes`: `9`
- Click **"Execute"**
- View the response with job_id and file URLs

#### 3. Test Download Endpoint
- Copy the `job_id` from the previous response
- Click on `GET /download/{job_id}/{filename}`
- Click **"Try it out"**
- Enter the `job_id`
- Enter `filename` from the response (e.g., `abc-123_9nodes_benefits.csv`)
- Click **"Execute"**
- Download the file

---

## 📋 Method 2: Using curl (Command Line)

Open a **new terminal** (keep the server running in the first one)

### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{"status":"healthy"}
```

### 2. Get Node Options

```bash
curl http://localhost:8000/node-options
```

**Response:**
```json
{
  "options": [
    {"value": 4, "label": "4 nodes (2x2 grid)"},
    {"value": 9, "label": "9 nodes (3x3 grid)"},
    ...
  ]
}
```

### 3. Process Image

```bash
# From the q-forest root directory
curl -X POST http://localhost:8000/process \
  -F "file=@preprocessing/data/map.png" \
  -F "nodes=9"
```

**Response:**
```json
{
  "success": true,
  "job_id": "abc-123-xyz",
  "nodes": 9,
  "grid_size": "3x3",
  "files": {
    "visualization": "/results/abc-123-xyz/abc-123-xyz_9nodes_visualization.png",
    "benefits_csv": "/results/abc-123-xyz/abc-123-xyz_9nodes_benefits.csv",
    "costs_csv": "/results/abc-123-xyz/abc-123-xyz_9nodes_costs.csv"
  },
  "statistics": {
    "num_nodes": 9,
    "num_edges": 12,
    "density": 0.3333,
    "avg_benefit": 0.4567,
    "avg_cost": 0.5234
  }
}
```

### 4. Download Files

Using the `job_id` from the response above:

```bash
# Download benefits CSV
curl http://localhost:8000/results/abc-123-xyz/abc-123-xyz_9nodes_benefits.csv -o benefits.csv

# Download costs CSV
curl http://localhost:8000/results/abc-123-xyz/abc-123-xyz_9nodes_costs.csv -o costs.csv

# Download visualization
curl http://localhost:8000/results/abc-123-xyz/abc-123-xyz_9nodes_visualization.png -o viz.png
```

**Or using the download endpoint:**
```bash
curl http://localhost:8000/download/abc-123-xyz/abc-123-xyz_9nodes_benefits.csv -o benefits.csv
```

---

## 📋 Method 3: Using Python

Create a test script `test_api.py`:

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

# Test 1: Health Check
print("1. Testing health check...")
response = requests.get(f"{BASE_URL}/health")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}\n")

# Test 2: Get Node Options
print("2. Getting node options...")
response = requests.get(f"{BASE_URL}/node-options")
print(f"   Status: {response.status_code}")
print(f"   Options: {len(response.json()['options'])} available\n")

# Test 3: Process Image
print("3. Processing image...")
with open('../preprocessing/data/map.png', 'rb') as f:
    files = {'file': ('map.png', f, 'image/png')}
    data = {'nodes': 9}
    response = requests.post(f"{BASE_URL}/process", files=files, data=data)

if response.status_code == 200:
    result = response.json()
    print(f"   Status: {response.status_code}")
    print(f"   Job ID: {result['job_id']}")
    print(f"   Grid: {result['grid_size']}")
    print(f"   Nodes: {result['statistics']['num_nodes']}")
    print(f"   Edges: {result['statistics']['num_edges']}")
    print(f"   Files available:")
    for key, url in result['files'].items():
        print(f"     - {key}: {url}")
    
    # Test 4: Download Files
    print("\n4. Downloading results...")
    job_id = result['job_id']
    
    # Download benefits
    benefits_url = f"{BASE_URL}{result['files']['benefits_csv']}"
    benefits_response = requests.get(benefits_url)
    with open('benefits.csv', 'wb') as f:
        f.write(benefits_response.content)
    print(f"   ✓ Downloaded benefits.csv ({len(benefits_response.content)} bytes)")
    
    # Download costs
    costs_url = f"{BASE_URL}{result['files']['costs_csv']}"
    costs_response = requests.get(costs_url)
    with open('costs.csv', 'wb') as f:
        f.write(costs_response.content)
    print(f"   ✓ Downloaded costs.csv ({len(costs_response.content)} bytes)")
    
    # Download visualization
    viz_url = f"{BASE_URL}{result['files']['visualization']}"
    viz_response = requests.get(viz_url)
    with open('visualization.png', 'wb') as f:
        f.write(viz_response.content)
    print(f"   ✓ Downloaded visualization.png ({len(viz_response.content)} bytes)")
    
else:
    print(f"   Error: {response.status_code}")
    print(f"   Message: {response.json()}")
```

Run it:
```bash
python test_api.py
```

---

## 📋 Method 4: Using Postman

1. **Open Postman**
2. **Create New Request**

### Test /process endpoint:

1. Set method to `POST`
2. URL: `http://localhost:8000/process`
3. Go to **Body** tab
4. Select **form-data**
5. Add key: `file`, type: `File`, value: browse and select image
6. Add key: `nodes`, type: `Text`, value: `9`
7. Click **Send**

### Test /download endpoint:

1. Set method to `GET`
2. URL: `http://localhost:8000/download/{job_id}/{filename}`
3. Replace `{job_id}` and `{filename}` with actual values
4. Click **Send**
5. Click **Save Response** to download

---

## 📋 Method 5: Using HTTPie (Alternative CLI)

Install HTTPie:
```bash
pip install httpie
```

### Test endpoints:

```bash
# Health check
http GET localhost:8000/health

# Process image
http -f POST localhost:8000/process file@preprocessing/data/map.png nodes=9

# Download file
http GET localhost:8000/results/{job_id}/{filename} > output.csv
```

---

## 🧪 Complete Test Script (Bash)

Save this as `test_endpoints.sh`:

```bash
#!/bin/bash

echo "🌲 Q-FOREST API Testing Script"
echo "=============================="
echo ""

BASE_URL="http://localhost:8000"

# Test 1: Health Check
echo "1️⃣  Testing Health Check..."
HEALTH=$(curl -s $BASE_URL/health)
echo "   Response: $HEALTH"
echo ""

# Test 2: Root endpoint
echo "2️⃣  Testing Root Endpoint..."
ROOT=$(curl -s $BASE_URL/)
echo "   Response: $ROOT"
echo ""

# Test 3: Node Options
echo "3️⃣  Getting Node Options..."
OPTIONS=$(curl -s $BASE_URL/node-options)
echo "   Response: $OPTIONS"
echo ""

# Test 4: Process Image
echo "4️⃣  Processing Image..."
RESULT=$(curl -s -X POST $BASE_URL/process \
  -F "file=@preprocessing/data/map.png" \
  -F "nodes=9")

echo "   Response:"
echo "$RESULT" | python3 -m json.tool
echo ""

# Extract job_id (requires jq)
if command -v jq &> /dev/null; then
    JOB_ID=$(echo "$RESULT" | jq -r '.job_id')
    echo "5️⃣  Job ID: $JOB_ID"
    echo ""
    
    # Test 5: Download Files
    echo "6️⃣  Files are available at:"
    echo "   - $BASE_URL/results/$JOB_ID/"
    ls -lh backend/results/$JOB_ID/
else
    echo "   💡 Tip: Install 'jq' for automatic file downloads"
fi

echo ""
echo "✅ Testing Complete!"
```

Make it executable and run:
```bash
chmod +x test_endpoints.sh
./test_endpoints.sh
```

---

## 📊 Expected Results

### Successful /process response:
```json
{
  "success": true,
  "job_id": "unique-uuid-here",
  "nodes": 9,
  "grid_size": "3x3",
  "files": {
    "visualization": "/results/.../visualization.png",
    "benefits_csv": "/results/.../benefits.csv",
    "costs_csv": "/results/.../costs.csv"
  },
  "statistics": {
    "num_nodes": 9,
    "num_edges": 12,
    "density": 0.3333,
    "avg_benefit": 0.4567,
    "avg_cost": 0.5234
  }
}
```

### Files Created:
After processing, check:
```bash
ls backend/results/{job_id}/
```

You should see:
- `{job_id}_9nodes_benefits.csv`
- `{job_id}_9nodes_costs.csv`
- `{job_id}_9nodes_visualization.png`

---

## ❌ Common Errors and Solutions

### Error: Connection Refused
```
curl: (7) Failed to connect to localhost port 8000
```
**Solution**: Server is not running. Start it with `python main.py`

### Error: Invalid Node Count
```json
{
  "detail": "15 is not a perfect square. Valid values: 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144"
}
```
**Solution**: Use only perfect square numbers

### Error: File Not Found
```json
{
  "detail": "File not found"
}
```
**Solution**: Check the job_id and filename are correct

### Error: Module Not Found
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution**: Activate venv and install dependencies:
```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🎯 Quick Test Commands

Copy and paste these for instant testing:

```bash
# Terminal 1: Start server
cd backend && source .venv/bin/activate && python main.py

# Terminal 2: Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/node-options
curl -X POST http://localhost:8000/process -F "file=@preprocessing/data/map.png" -F "nodes=9"
```

---

## 📚 Additional Resources

- **Swagger UI**: http://localhost:8000/docs (Interactive testing)
- **ReDoc**: http://localhost:8000/redoc (API documentation)
- **OpenAPI JSON**: http://localhost:8000/openapi.json (API schema)

---

**Happy Testing! 🧪🌲**

