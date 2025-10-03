# Quantum Knapsack - Quick Usage Guide

## 🎯 What It Does

Solves 0-1 knapsack problems using **quantum algorithms (QAOA)** implemented with Qiskit.

**Problem**: Given items with values and weights, select items to maximize value without exceeding weight budget.

---

## 🚀 Three Approaches Available

### 1. **QuadQAOA** ⭐ (Recommended)
- Best accuracy-speed trade-off
- Uses quadratic penalty for constraints
- **Best for most use cases**

### 2. **LinQAOA**
- Faster but less accurate
- Linear penalty for constraints
- **Best for quick testing**

### 3. **QuantumWalkQAOA**
- Guaranteed feasible solutions
- More complex circuit
- **Best when constraints are critical**

---

## 💻 Quick Start

### Basic Example (QuadQAOA)

```python
from knapsack import KnapsackProblem
from circuits import QuadQAOA
from quadqaoa import find_optimal_angles, get_probs_dict

# Define problem
problem = KnapsackProblem(
    values=[10, 20, 30, 40],  # Item benefits
    weights=[5, 10, 15, 20],   # Item costs
    max_weight=25              # Budget
)

# Configure QAOA
p = 2     # Depth (1-3 typical)
a = 40    # Must be ≥ max(values)
b = 100   # Penalty strength

# Run optimization
circuit = QuadQAOA(problem, p)
angles = find_optimal_angles(circuit, problem, a, b)
probs = get_probs_dict(circuit, problem, angles, a, b)

# Get best solution
best = max(probs, key=probs.get)
print(f"Best solution: {best}")
print(f"Probability: {probs[best]:.4f}")
```

### From CSV File

**Create `my_data.csv`:**
```csv
beneficio,costo,max_weight
10,5,25
20,10,
30,15,
40,20,
```

**Run:**
```bash
cd quantum-knapsack
python bridge.py  # Uses datos.csv by default
```

---

## 📊 Integration with Q-FOREST

### Using Preprocessing Outputs

```python
import numpy as np
import pandas as pd
from knapsack import KnapsackProblem
from circuits import QuadQAOA
from quadqaoa import find_optimal_angles, get_probs_dict

# Load Q-FOREST matrices
benefits = pd.read_csv("benefits.csv", header=None).values.flatten()
costs = pd.read_csv("costs.csv", header=None).values.flatten()

# Scale to integers (QAOA works best with integers)
benefits_int = (benefits * 100).astype(int)
costs_int = costs.astype(int)
budget = 200

# Create problem
problem = KnapsackProblem(
    values=benefits_int.tolist(),
    weights=costs_int.tolist(),
    max_weight=budget
)

# Run QuadQAOA
circuit = QuadQAOA(problem, p=3)
angles = find_optimal_angles(circuit, problem, a=100, b=100)
probs = get_probs_dict(circuit, problem, angles, 100, 100)

# Convert to matrix for visualization
best_bitstring = max(probs, key=probs.get)
solution = np.array([int(b) for b in reversed(best_bitstring)])
grid_size = int(np.sqrt(len(solution)))
solution_matrix = solution.reshape(grid_size, grid_size)

# Save for postprocessing
np.savetxt("quantum_solution.csv", solution_matrix, delimiter=',', fmt='%d')
```

---

## ⚙️ Parameter Guide

### QAOA Depth (p)
- **p=1**: Fast, low quality
- **p=2**: Balanced (recommended)
- **p=3**: High quality, slower

### Penalty Parameters

**QuadQAOA:**
- `a`: Value scaling (1-10)
- `b`: Penalty strength (≥ a × max(values), typically 100)

**LinQAOA:**
- `a`: Penalty (≥ max(values), typically 10-100)

**QuantumWalkQAOA:**
- `m`: Walk steps (1-5)

---

## 🔍 Comparing Solutions

### Quantum vs Classical

```python
# Classical solution (from classic module)
from classic.classic_solver import ClassicSolver

classic_solver = ClassicSolver()
classic_result = classic_solver.solve(benefits, costs, budget)

# Quantum solution
# ... (code from above)

print(f"Classical: {classic_result['selected_count']} items")
print(f"Quantum: {sum(solution)} items")
```

---

## 📝 Common Use Cases

### 1. Small Research Problems (< 10 items)
```python
problem = KnapsackProblem([1,2,3,4], [1,2,3,4], 5)
circuit = QuadQAOA(problem, p=2)
# ... optimize
```

### 2. Q-FOREST Grid (9-400 nodes)
```python
# Load from preprocessing, run quantum solver
# See "Integration with Q-FOREST" above
```

### 3. Comparing Approaches
```python
# Run all three: LinQAOA, QuadQAOA, QuantumWalkQAOA
# Compare approximation ratios
```

---

## ⚠️ Important Notes

1. **Integer Values**: Quantum solver works best with integer values/weights
2. **Size Limit**: Practical limit ~10-20 items (qubit constraints)
3. **Simulation**: Uses classical simulation (not real quantum hardware)
4. **Approximate**: Provides approximate solutions, not guaranteed optimal
5. **Speed**: Angle optimization can be slow (minutes for larger problems)

---

## 🐛 Troubleshooting

### Problem: Optimization fails
```python
# Check if angles is None
if angles is None:
    # Try: increase p, adjust a/b, simplify problem
```

### Problem: Poor results
```python
# Solution: Increase depth
p = 3  # Instead of p=1

# Or adjust penalties
a = 100  # Stronger value scaling
b = 200  # Stronger constraint penalty
```

### Problem: Too slow
```python
# Solution: Use LinQAOA or reduce p
circuit = LinQAOA(problem, p=1)  # Faster approach
```

---

## 📚 Learn More

- Full documentation: `quantum-knapsack/README.md`
- Example problems: `knapsack.toy_problems`
- Visualization: See `visualization.py`

---

## 🎯 Quick Command Reference

```bash
# Run example
cd quantum-knapsack
python quadqaoa.py

# Run with CSV data
python bridge.py

# Test different approaches
python linqaoa.py
python quadqaoa.py
python qwqaoa.py
```

---

**🌲 Part of the Q-FOREST ecosystem**
