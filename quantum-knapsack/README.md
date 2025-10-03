# Quantum Knapsack Solver

**Quantum Approximate Optimization Algorithm (QAOA) implementations for solving the 0-1 Knapsack Problem**

This module provides three different QAOA approaches for solving knapsack optimization problems using quantum circuits implemented with Qiskit.

---

## 🎯 Overview

The quantum-knapsack module implements three variants of QAOA for the knapsack problem:

1. **LinQAOA** - Linear soft constraints approach
2. **QuadQAOA** - Quadratic soft constraints approach  
3. **QuantumWalkQAOA** - Hard constraints with quantum walk mixer

Each approach provides a different trade-off between circuit complexity, accuracy, and constraint handling.

---

## 📁 Module Structure

```
quantum-knapsack/
├── knapsack.py         # Knapsack problem definitions
├── circuits.py         # QAOA circuit implementations
├── optimization.py     # Angle optimization helpers
├── linqaoa.py         # Linear penalty QAOA
├── quadqaoa.py        # Quadratic penalty QAOA
├── qwqaoa.py          # Quantum walk QAOA
├── bridge.py          # CSV data bridge
├── simulation.py      # Qiskit simulation backend
├── visualization.py   # Result visualization
└── datos.csv          # Example data file
```

---

## 🔧 Problem Definition

### KnapsackProblem Class

The core class represents a 0-1 integer knapsack problem:

```python
from knapsack import KnapsackProblem

problem = KnapsackProblem(
    values=[2, 5, 8, 4],      # Benefits/values of items
    weights=[1, 3, 5, 2],     # Costs/weights of items
    max_weight=6              # Budget/capacity constraint
)
```

**Attributes:**
- `values` (list): Benefits of each item (integers recommended)
- `weights` (list): Costs/weights of each item (integers recommended)
- `max_weight` (int): Maximum total weight allowed (budget constraint)
- `N` (int): Number of items (auto-computed)
- `total_weight` (int): Sum of all weights (auto-computed)

**Helper Functions:**
```python
import numpy as np
from knapsack import value, weight, is_choice_feasible

choice = np.array([1, 0, 1, 0])  # Select items 0 and 2
total_value = value(choice, problem)      # Get total benefit
total_weight = weight(choice, problem)    # Get total cost
is_valid = is_choice_feasible(choice, problem)  # Check constraint
```

---

## 🌟 QAOA Approaches

### 1. LinQAOA - Linear Soft Constraints

**Best for:** Small problems, fast execution

**Circuit:** Uses linear penalty to discourage infeasible solutions

**Key Features:**
- Soft constraint handling via penalty parameter `a`
- Default X-mixer for state transitions
- Feasibility oracle checks weight constraints
- Requires parameter `a ≥ max(values)` for correct behavior

**Usage:**
```python
from circuits import LinQAOA
from linqaoa import find_optimal_angles, get_probs_dict
import knapsack

# Define problem
problem = knapsack.KnapsackProblem(
    values=[1, 2, 3],
    weights=[1, 2, 3],
    max_weight=4
)

# Parameters
p = 2       # QAOA depth (number of layers)
a = 10      # Penalty scaling factor (a ≥ max(values))

# Build circuit
circuit = LinQAOA(problem, p)

# Optimize angles
angles = find_optimal_angles(circuit, problem, a)

# Get probability distribution
probs = get_probs_dict(circuit, problem, angles, a)
print(f"Probabilities: {probs}")
```

**Parameter Guide:**
- `p`: QAOA depth (1-3 typical, higher = better approximation but slower)
- `a`: Penalty parameter (must be ≥ max(values), typically 10-100)

---

### 2. QuadQAOA - Quadratic Soft Constraints ⭐

**Best for:** Medium problems, good accuracy-speed trade-off

**Circuit:** Uses quadratic penalty for more accurate constraint enforcement

**Key Features:**
- Quadratic penalty term for better constraint handling
- Two penalty parameters `a` (value scaling) and `b` (penalty scaling)
- More qubits required (N + max_weight)
- Better approximation ratios than LinQAOA

**Usage:**
```python
from circuits import QuadQAOA
from quadqaoa import find_optimal_angles, get_probs_dict
import knapsack

# Define problem
problem = knapsack.KnapsackProblem(
    values=[2, 5, 8, 4],
    weights=[1, 3, 5, 2],
    max_weight=6
)

# Parameters
p = 3       # QAOA depth
a = 10      # Value scaling factor
b = 10      # Penalty scaling factor (b ≥ a * max(values))

# Build circuit
circuit = QuadQAOA(problem, p)

# Optimize angles
angles = find_optimal_angles(circuit, problem, a, b)

# Get probability distribution
probs = get_probs_dict(circuit, problem, angles, a, b)
print(f"Probabilities: {probs}")

# Get best solution
best_solution = max(probs, key=probs.get)
print(f"Best solution: {best_solution}")
```

**Parameter Guide:**
- `p`: QAOA depth (2-4 typical)
- `a`: Value scaling (1-10)
- `b`: Penalty scaling (b ≥ a * max(values), typically 10-100)

---

### 3. QuantumWalkQAOA - Hard Constraints

**Best for:** Guaranteed feasible solutions

**Circuit:** Uses quantum walk mixer to only explore feasible states

**Key Features:**
- Hard constraint enforcement (only feasible states)
- Quantum walk mixer parameter `m`
- More complex circuit but guaranteed constraint satisfaction
- No penalty parameters needed

**Usage:**
```python
from circuits import QuantumWalkQAOA
from qwqaoa import find_optimal_angles, get_probs_dict
import knapsack

# Define problem
problem = knapsack.KnapsackProblem(
    values=[1, 2, 4],
    weights=[1, 2, 3],
    max_weight=3
)

# Parameters
p = 2       # QAOA depth
m = 3       # Quantum walk steps per layer

# Build circuit
circuit = QuantumWalkQAOA(problem, p, m)

# Optimize angles
angles = find_optimal_angles(circuit, problem)

# Get probability distribution
probs = get_probs_dict(circuit, problem, angles)
print(f"Probabilities: {probs}")
```

**Parameter Guide:**
- `p`: QAOA depth (1-3 typical)
- `m`: Quantum walk steps (1-5, higher = more thorough mixing)

---

## 📊 Using CSV Data

### CSV Format

The `bridge.py` module provides CSV integration:

**Example `datos.csv`:**
```csv
beneficio,costo,max_weight
2,1,6
5,3,
8,5,
4,2,
```

**Usage:**
```python
from bridge import read_knapsack_csv, main
import knapsack
from circuits import QuadQAOA
from quadqaoa import find_optimal_angles, get_probs_dict

# Load from CSV
values, weights, max_weight = read_knapsack_csv("datos.csv")

# Create problem
problem = knapsack.KnapsackProblem(values, weights, int(max_weight))

# Run QuadQAOA
a = 10
b = 10
p = 3

circuit = QuadQAOA(problem, p)
angles = find_optimal_angles(circuit, problem, a, b)
probs = get_probs_dict(circuit, problem, angles, a, b)

print(f"Best solution probabilities: {probs}")
```

**Or use the bridge directly:**
```bash
cd quantum-knapsack
python bridge.py
```

---

## 🔬 Circuit Components

### Core Building Blocks

1. **QFT (Quantum Fourier Transform)**: Used for weight calculation
2. **Add**: Circuit for adding integers in QFT basis
3. **WeightCalculator**: Computes total weight of selected items
4. **FeasibilityOracle**: Checks if a choice satisfies weight constraint
5. **DephaseValue**: Applies phase based on item values
6. **Mixers**: 
   - `DefaultMixer`: Standard X-rotations
   - `QuantumWalkMixer`: Feasibility-preserving quantum walk

### Quantum Registers

**LinQAOA:**
- `choice_reg`: N qubits for item selection
- `weight_reg`: log₂(total_weight) + 1 qubits for weight calculation
- `flag_reg`: 1 qubit for feasibility checking

**QuadQAOA:**
- `choice_reg`: N qubits for item selection
- `weight_reg`: max_weight qubits for weight representation

**QuantumWalkQAOA:**
- `choice_reg`: N qubits for item selection
- `weight_reg`: log₂(total_weight) + 1 qubits
- `flag_x`, `flag_neighbor`, `flag_both`: Auxiliary qubits for quantum walk

---

## 📈 Performance & Approximation Ratios

### Comparing Approaches

```python
from linqaoa import approximation_ratio as lin_ratio
from quadqaoa import approximation_ratio as quad_ratio
import knapsack

problem = knapsack.toy_problems[0]  # Example problem

# Compare approximation ratios
lin_approx = lin_ratio(problem, p=2, a=10)
quad_approx = quad_ratio(problem, p=2, a=10, b=10)

print(f"LinQAOA approximation ratio: {lin_approx:.4f}")
print(f"QuadQAOA approximation ratio: {quad_approx:.4f}")
```

### Toy Problems

Pre-defined test problems are available:

```python
from knapsack import toy_problems, problem_names, best_known_solutions

for name, problem in zip(problem_names, toy_problems):
    print(f"Problem {name}: {problem}")
    best_sols = best_known_solutions(problem)
    print(f"Best solutions: {best_sols}")
```

---

## 🎨 Visualization

```python
from visualization import hist
import matplotlib.pyplot as plt

# After getting probabilities
fig, ax = plt.subplots()
hist(ax, probs)
plt.title("QAOA Solution Distribution")
plt.show()
```

---

## 🔧 Integration with Q-FOREST

### Using Q-FOREST Matrices

The quantum solver can work with Q-FOREST preprocessing outputs:

```python
import numpy as np
import pandas as pd
from knapsack import KnapsackProblem
from circuits import QuadQAOA
from quadqaoa import find_optimal_angles, get_probs_dict

# Load Q-FOREST outputs
benefits = pd.read_csv("benefits.csv", header=None).values.flatten()
costs = pd.read_csv("costs.csv", header=None).values.flatten()

# Scale and convert to integers (QAOA works best with integers)
benefits_int = (benefits * 100).astype(int)  # Scale 0-1 to 0-100
costs_int = costs.astype(int)                # Already 30-100

# Set budget (same as classic solver)
budget = 200

# Create knapsack problem
problem = KnapsackProblem(
    values=benefits_int.tolist(),
    weights=costs_int.tolist(),
    max_weight=budget
)

# Run QuadQAOA
a = 100  # Should be ≥ max(benefits_int)
b = 100
p = 3

circuit = QuadQAOA(problem, p)
angles = find_optimal_angles(circuit, problem, a, b)
probs = get_probs_dict(circuit, problem, angles, a, b, choices_only=True)

# Get best solution
best_bitstring = max(probs, key=probs.get)
solution_array = np.array(list(map(int, reversed(best_bitstring))))

# Reshape to grid format for Q-FOREST postprocessing
grid_size = int(np.sqrt(len(solution_array)))
solution_matrix = solution_array.reshape(grid_size, grid_size)

# Save for postprocessing
np.savetxt("quantum_solution.csv", solution_matrix, delimiter=',', fmt='%d')
```

---

## 📦 Dependencies

```python
qiskit >= 0.34.2
numpy >= 1.22.0
scipy >= 1.7.3
matplotlib >= 3.5.0
```

Install with:
```bash
pip install qiskit numpy scipy matplotlib
```

---

## 🚀 Quick Start Examples

### Example 1: Simple 3-Item Problem

```python
import knapsack
from circuits import QuadQAOA
from quadqaoa import find_optimal_angles, get_probs_dict

# Define problem
problem = knapsack.KnapsackProblem(
    values=[10, 20, 30],
    weights=[5, 10, 15],
    max_weight=20
)

# Run QuadQAOA
circuit = QuadQAOA(problem, p=2)
angles = find_optimal_angles(circuit, problem, a=30, b=100)
probs = get_probs_dict(circuit, problem, angles, 30, 100)

print("Solution probabilities:")
for bitstring, prob in sorted(probs.items(), key=lambda x: -x[1])[:5]:
    print(f"  {bitstring}: {prob:.4f}")
```

### Example 2: From CSV File

```python
from bridge import main

# Edit datos.csv with your data, then run:
main()
```

### Example 3: Compare All Three Approaches

```python
import knapsack
from circuits import LinQAOA, QuadQAOA, QuantumWalkQAOA
from linqaoa import find_optimal_angles as lin_optimize
from quadqaoa import find_optimal_angles as quad_optimize
from qwqaoa import find_optimal_angles as qw_optimize

problem = knapsack.toy_problems[4]  # Problem E

# LinQAOA
lin_circuit = LinQAOA(problem, p=2)
lin_angles = lin_optimize(lin_circuit, problem, a=10)

# QuadQAOA
quad_circuit = QuadQAOA(problem, p=2)
quad_angles = quad_optimize(quad_circuit, problem, a=10, b=100)

# QuantumWalkQAOA
qw_circuit = QuantumWalkQAOA(problem, p=2, m=3)
qw_angles = qw_optimize(qw_circuit, problem)

print("All approaches optimized!")
```

---

## 📝 Parameter Selection Guide

### QAOA Depth (p)

| p | Quality | Speed | Recommendation |
|---|---------|-------|----------------|
| 1 | Low | Fast | Quick testing |
| 2 | Medium | Moderate | Good balance |
| 3 | High | Slow | Better accuracy |
| 4+ | Higher | Very slow | Research only |

### Penalty Parameters

**LinQAOA:**
- `a ≥ max(values)` (required)
- Start with `a = 10 * max(values)`

**QuadQAOA:**
- `a`: 1-10 typical
- `b ≥ a * max(values)` (required)
- Start with `a=10, b=100`

**QuantumWalkQAOA:**
- `m`: 1-5 (quantum walk steps)
- Higher m = better mixing, but slower

---

## ⚠️ Limitations & Considerations

1. **Integer Values**: Works best with integer values and weights
2. **Problem Size**: Limited by available qubits (practical limit ~10-20 items)
3. **Simulation**: Uses classical simulation (not real quantum hardware)
4. **Optimization Time**: Angle optimization can be slow for large p
5. **Approximation**: QAOA provides approximate solutions, not guaranteed optimal

---

## 🔍 Troubleshooting

### No optimal angles found
```python
# Issue: Optimization failed
# Solution: Check parameter bounds, increase optimization iterations
angles = find_optimal_angles(circuit, problem, a, b)
if angles is None:
    print("Try adjusting a, b, or p parameters")
```

### Circuit too large
```python
# Issue: Too many qubits required
# Solution: Reduce problem size or use LinQAOA
# LinQAOA requires fewer qubits than QuadQAOA
```

### Poor approximation ratio
```python
# Issue: Solution quality too low
# Solution: Increase p, adjust penalty parameters
p = 3  # Instead of p=1
a = 100  # Increase penalty strength
```

---

## 📚 References

This implementation is based on QAOA approaches for the knapsack problem as described in quantum optimization literature.

**Key Concepts:**
- QAOA (Quantum Approximate Optimization Algorithm)
- Soft constraints (linear and quadratic penalties)
- Hard constraints (quantum walk mixers)
- QFT-based arithmetic circuits

---

## 🎓 Academic Use

This module is suitable for:
- Research on quantum optimization algorithms
- Comparing classical vs quantum approaches
- Educational demonstrations of QAOA
- Benchmarking different QAOA variants

---

## 🔜 Future Enhancements

- [ ] Real quantum hardware support
- [ ] Adaptive penalty parameter selection
- [ ] Warm-start angle initialization
- [ ] Parallel circuit execution
- [ ] Backend API integration
- [ ] Comparison with classical solver

---

**Made with 🌲 for quantum optimization research**

