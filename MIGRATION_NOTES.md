# Classic Solver Migration Notes

## Summary of Changes - October 2025

### 🔄 Reorganization

The classical optimization solver has been moved from `backend/classic/` to a root-level `classic/` module to align with the project structure (preprocessing, postprocessing, quantum-knapsack, etc.).

---

## 📂 Directory Structure Changes

### Before:
```
q-forest/
├── backend/
│   ├── classic/
│   │   └── classicSolve.py  ❌ Old location
│   └── main.py
├── preprocessing/
├── postprocessing/
└── quantum-knapsack/
```

### After:
```
q-forest/
├── backend/
│   └── main.py              ✅ Updated with /optimize/classic endpoint
├── preprocessing/
├── postprocessing/
├── classic/                 ✅ New root-level module
│   ├── classic_solver.py    ✅ Refactored solver
│   ├── __init__.py
│   ├── README.md
│   ├── requirements.txt
│   ├── example_usage.py
│   ├── test_integration.py
│   └── CHANGELOG.md
└── quantum-knapsack/
```

---

## 🔧 Code Changes

### 1. Refactored `classicSolve.py` → `classic_solver.py`

**Old Code (Function-based):**
```python
def solve_optimization():
    alphaMatrix = pd.read_csv("./preprocessing/data/...csv", header=None).values
    weightCostMatrix = pd.read_csv("./preprocessing/data/...csv", header=None).values
    budget = 2
    # ... hardcoded logic
    return normalizedSolutionMatrix
```

**New Code (Class-based):**
```python
class ClassicSolver:
    def solve(self, benefits: np.ndarray, costs: np.ndarray, 
              budget: float, verbose: bool = True) -> Dict:
        # ... flexible, parameterized logic
        return {
            "solution_matrix": ...,
            "objective_value": ...,
            "status": ...,
            # ... comprehensive statistics
        }
```

**Key Improvements:**
- ✅ Class-based design for better organization
- ✅ Accepts numpy arrays or CSV files
- ✅ Parameterized budget (not hardcoded)
- ✅ Returns comprehensive statistics dictionary
- ✅ Input validation and error handling
- ✅ Verbose mode for debugging
- ✅ No hardcoded file paths

---

### 2. Backend API Integration

**Added to `backend/main.py`:**
```python
@app.post("/optimize/classic")
async def optimize_classic(
    benefits_file: UploadFile = File(...),
    costs_file: UploadFile = File(...),
    budget: float = Form(...)
):
    """Run classical optimization using SDP"""
    solver = ClassicSolver()
    result = solver.solve(benefits, costs, budget, verbose=False)
    # ... save results and return JSON
```

**API Endpoint:**
- URL: `POST /optimize/classic`
- Inputs: Benefits CSV, Costs CSV, Budget value
- Output: Solution matrix + statistics (JSON)
- Files: Saves solution.csv and solution_binary.csv

---

## 📊 Usage Comparison

### Before (Direct Script):
```bash
# Had to edit classicSolve.py to change file paths and budget
python backend/classic/classicSolve.py
```

### After (Multiple Options):

**Option 1: Python API**
```python
from classic.classic_solver import ClassicSolver
solver = ClassicSolver()
result = solver.solve(benefits, costs, budget=250.0)
```

**Option 2: REST API**
```bash
curl -X POST http://localhost:8000/optimize/classic \
  -F "benefits_file=@benefits.csv" \
  -F "costs_file=@costs.csv" \
  -F "budget=250.0"
```

**Option 3: Command Line**
```bash
cd classic
python classic_solver.py  # Uses example data
```

---

## 🔗 Integration with Pipeline

### Complete Workflow:

```bash
# 1. Preprocessing: Generate benefits/costs from heatmap
curl -X POST http://localhost:8000/process \
  -F "file=@map.png" -F "nodes=9" > step1.json

# 2. Download matrices
JOB_ID=$(jq -r '.job_id' step1.json)
curl "http://localhost:8000/results/$JOB_ID/${JOB_ID}_9nodes_benefits.csv" -o benefits.csv
curl "http://localhost:8000/results/$JOB_ID/${JOB_ID}_9nodes_costs.csv" -o costs.csv

# 3. Classical Optimization: Find optimal nodes
curl -X POST http://localhost:8000/optimize/classic \
  -F "benefits_file=@benefits.csv" \
  -F "costs_file=@costs.csv" \
  -F "budget=250" > step2.json

# 4. Download solution
OPT_ID=$(jq -r '.job_id' step2.json)
curl "http://localhost:8000/results/$OPT_ID/${OPT_ID}_solution_binary.csv" -o solution.csv

# 5. Postprocessing: Visualize selected nodes
curl -X POST http://localhost:8000/highlight \
  -F "file=@map.png" \
  -F "selection_matrix=@solution.csv" \
  -F "nodes=9" > step3.json

# 6. Download final visualization
VIZ_ID=$(jq -r '.job_id' step3.json)
curl "http://localhost:8000/results/$VIZ_ID/${VIZ_ID}_9nodes_highlighted.png" -o result.png
```

---

## 📦 Dependency Changes

### `backend/requirements.txt` - Added:
```
cvxpy>=1.3.0
pandas>=1.5.0
```

### `classic/requirements.txt` - New file:
```
cvxpy>=1.3.0
numpy>=1.22.0
pandas>=1.5.0
```

---

## 🧪 Testing

### New Test Files:

1. **`classic/example_usage.py`**
   - Example 1: Solve from numpy arrays
   - Example 2: Solve from CSV files
   - Example 3: Test multiple budget values

2. **`classic/test_integration.py`**
   - Complete pipeline test (preprocessing → optimization)
   - Validation of constraints
   - Budget sensitivity analysis

### Run Tests:
```bash
cd classic
python example_usage.py       # Run examples
python test_integration.py    # Run integration tests
```

---

## 📝 Documentation Updates

### Updated Files:
- ✅ `README.md` - Added classic module to project structure
- ✅ `backend/README.md` - Documented `/optimize/classic` endpoint
- ✅ `QUICKSTART.md` - May need updating with workflow examples

### New Files:
- ✅ `classic/README.md` - Complete module documentation
- ✅ `classic/CHANGELOG.md` - Feature history
- ✅ `MIGRATION_NOTES.md` - This file

---

## 🚀 Benefits of New Structure

1. **Consistency**: Aligns with preprocessing/postprocessing structure
2. **Modularity**: Can be imported independently
3. **Flexibility**: Accepts various input formats
4. **API-Ready**: Seamlessly integrated with FastAPI backend
5. **Testable**: Includes test suite and examples
6. **Documented**: Comprehensive README and examples
7. **Reusable**: ClassicSolver can be used in other projects

---

## ⚠️ Breaking Changes

### For Users of Old `classicSolve.py`:

**Old import (won't work):**
```python
from backend.classic.classicSolve import solve_optimization
```

**New import:**
```python
from classic.classic_solver import ClassicSolver
solver = ClassicSolver()
result = solver.solve_from_files(benefits_path, costs_path, budget)
```

**Or use the API:**
```bash
curl -X POST http://localhost:8000/optimize/classic ...
```

---

## ✅ Migration Checklist

- [x] Create new `classic/` module at root level
- [x] Refactor `classicSolve.py` into `classic_solver.py`
- [x] Add class-based API with flexible inputs
- [x] Create `__init__.py` for module
- [x] Write comprehensive `README.md`
- [x] Add `requirements.txt`
- [x] Create example scripts
- [x] Create integration tests
- [x] Integrate with FastAPI backend (`/optimize/classic`)
- [x] Update backend dependencies
- [x] Update main README
- [x] Update backend README
- [x] Remove old `backend/classic/` directory
- [x] Test complete pipeline
- [x] Document migration

---

## 🎯 Next Steps

1. **Test the new endpoint**: Try the `/optimize/classic` API endpoint
2. **Run integration tests**: Execute `classic/test_integration.py`
3. **Update workflows**: If you have scripts using the old solver, update them
4. **Explore examples**: Check `classic/example_usage.py` for usage patterns

---

## 🆘 Need Help?

- **Module Documentation**: See `classic/README.md`
- **API Documentation**: Visit http://localhost:8000/docs (Swagger UI)
- **Examples**: Run `classic/example_usage.py`
- **Tests**: Run `classic/test_integration.py`

---

**Migration completed successfully! 🎉**

The classic solver is now a first-class module in the Q-FOREST ecosystem.

