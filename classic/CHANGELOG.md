# Classic Solver - Changelog

## Version 1.0.0 - October 2025

### 🎉 Initial Release

**Module Reorganization:**
- Moved classical optimization from `backend/classic/` to root-level `classic/` module
- Now positioned alongside preprocessing, postprocessing, and quantum-knapsack modules
- Provides consistent project structure

**Features:**
- ✅ **ClassicSolver Class**: Object-oriented API for optimization
- ✅ **SDP Formulation**: Semidefinite programming using CVXPY
- ✅ **Flexible Input**: Accepts numpy arrays or CSV files
- ✅ **Comprehensive Output**: Returns solution matrix with detailed statistics
- ✅ **Budget Constraints**: Knapsack-style optimization with cost limits
- ✅ **Validation**: Input validation and error handling

**API Integration:**
- ✅ **Backend Endpoint**: `POST /optimize/classic` integrated in FastAPI
- ✅ **File Upload**: Accepts benefits and costs CSV files
- ✅ **JSON Response**: Returns solution matrix and statistics
- ✅ **Result Storage**: Saves solution to results directory with job_id

**Documentation:**
- ✅ Complete README with usage examples
- ✅ Mathematical formulation documentation
- ✅ Integration guide with Q-FOREST pipeline
- ✅ Example scripts and test suite

**Testing:**
- ✅ Integration test with preprocessing
- ✅ Budget sensitivity analysis
- ✅ Validation of constraints
- ✅ Example usage scripts

### 📊 Output Format

The solver returns:
```python
{
    "solution_matrix": np.ndarray,      # Binary (0/1) selection matrix
    "selected_vector": np.ndarray,      # Flattened solution vector
    "objective_value": float,           # Optimal objective value
    "status": str,                      # Solver status
    "selected_count": int,              # Number of selected nodes
    "total_benefit": float,             # Sum of benefits
    "total_cost": float,                # Sum of costs
    "budget": float,                    # Budget constraint
    "budget_utilization": float         # Percentage used
}
```

### 🔗 Backend Integration

New API endpoint:
```bash
POST /optimize/classic
Parameters:
  - benefits_file: CSV file with benefits matrix (0-1)
  - costs_file: CSV file with costs matrix (30-100)
  - budget: Budget constraint (float)
```

### 📦 Dependencies

- cvxpy >= 1.3.0
- numpy >= 1.22.0
- pandas >= 1.5.0

### 🚀 Usage Example

```python
from classic.classic_solver import ClassicSolver
import numpy as np

# Create solver
solver = ClassicSolver()

# Run optimization
result = solver.solve(
    benefits=np.array([[0.8, 0.6], [0.7, 0.9]]),
    costs=np.array([[50, 40], [45, 60]]),
    budget=100.0
)

print(f"Selected {result['selected_count']} nodes")
print(result['solution_matrix'])
```

### 🎯 Complete Pipeline

1. **Preprocessing**: Generate benefits/costs from heatmap
2. **Classic Optimization**: Find optimal node selection
3. **Postprocessing**: Visualize selected nodes

```bash
# Generate matrices
curl -X POST http://localhost:8000/process -F "file=@map.png" -F "nodes=9"

# Optimize
curl -X POST http://localhost:8000/optimize/classic \
  -F "benefits_file=@benefits.csv" \
  -F "costs_file=@costs.csv" \
  -F "budget=250"

# Visualize
curl -X POST http://localhost:8000/highlight \
  -F "file=@map.png" \
  -F "selection_matrix=@solution.csv" \
  -F "nodes=9"
```

### 📝 Files

**New Files:**
- `classic/classic_solver.py` - Main solver module
- `classic/__init__.py` - Package initialization
- `classic/README.md` - Documentation
- `classic/requirements.txt` - Dependencies
- `classic/example_usage.py` - Example scripts
- `classic/test_integration.py` - Integration tests
- `classic/CHANGELOG.md` - This file

**Modified Files:**
- `backend/main.py` - Added `/optimize/classic` endpoint
- `backend/requirements.txt` - Added cvxpy, pandas
- `backend/README.md` - Documented new endpoint
- `README.md` - Updated project structure

**Removed Files:**
- `backend/classic/classicSolve.py` - Moved and refactored

---

**Made with 🌲 for better resource management**

