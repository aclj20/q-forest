# Classic Solver Algorithm Details

## Mathematical Formulation

The classic solver uses **Semidefinite Programming (SDP)** to solve the knapsack problem.

### Problem Formulation

**Objective:**
```
Maximize: Σ (0.5 * (1 + X₀ᵢ) * benefitᵢ)
```

**Subject to:**
```
1. Budget Constraint: Σ (0.5 * (1 + X₀ᵢ) * costᵢ) ≤ budget
2. Semidefinite Constraint: X ≽ 0 (positive semidefinite)
3. Diagonal Constraint: Xᵢᵢ = 1 for all i
```

Where:
- `X` is an (n+1) × (n+1) symmetric matrix
- `X₀ᵢ` is the element in position (0, i) of the matrix
- `benefitᵢ` is the benefit value for node i
- `costᵢ` is the cost value for node i
- `n` is the number of nodes

### Algorithm Steps

1. **Input Preprocessing**
   - Flatten benefit and cost matrices to vectors
   - Create (n+1) × (n+1) symmetric variable matrix

2. **Optimization Setup**
   - Define objective function (maximize total benefit)
   - Add budget constraint
   - Add semidefinite constraint (X ≽ 0)
   - Add diagonal constraints (Xᵢᵢ = 1)

3. **Solving**
   - Use CVXPY with SDP solver (CLARABEL, SCS, or MOSEK)
   - Extract solution from X₀ row (remove first element)

4. **Post-processing**
   - Reshape solution vector to original matrix shape
   - Normalize from [-1, 1] to [0, 1] range: `(x + 1) / 2`
   - Apply 3-decimal truncation for precision
   - Identify non-binary positions (0.0001 < value < 0.99)

### Helper Functions

#### `lineJump()`
Prints a separator line for formatted output.

#### `trunc(value, decimals=3)`
Truncates a value to specified decimal places without rounding.

**Formula:**
```python
truncated = floor(value * 10^decimals) / 10^decimals
```

**Example:**
```python
trunc(0.12345, 3) = 0.123
trunc(0.56789, 3) = 0.567
```

#### `calculateNonBinaryPositions(matrix, costs, benefits)`
Identifies positions with fractional values (non-binary).

**Criteria:** 0.0001 < value < 0.99

**Returns:** List of dictionaries with:
- `value`: The fractional solution value
- `pos`: (row, col) position in matrix
- `alpha_value`: Benefit value at that position
- `weight_value`: Cost value at that position

### Non-Binary Positions

Non-binary positions indicate **partial selection** in the relaxed SDP solution. These occur when:
- The budget constraint is tight
- Multiple nodes have similar benefit-to-cost ratios
- The optimal solution requires fractional allocation

**Interpretation:**
- Value close to 1.0: Node should likely be selected
- Value close to 0.0: Node should likely be excluded
- Value near 0.5: Ambiguous, may need problem-specific decision rules

### Rounding to Binary

For actual implementation, convert to binary using threshold:
```python
binary_solution = (solution_matrix > 0.5).astype(int)
```

**Note:** This may slightly violate the budget constraint. For strict budget compliance, use integer programming or custom rounding strategies.

### Complexity

- **Time Complexity**: O(n^3.5) for SDP solver
- **Space Complexity**: O(n^2) for the matrix variable
- **Practical Limits**: Works well for n up to 400 nodes

### Advantages of SDP Approach

1. **Convex Relaxation**: Provides guaranteed polynomial-time solution
2. **Quality Bounds**: Solution quality guaranteed within approximation ratio
3. **Scalability**: Handles moderate problem sizes efficiently
4. **Flexibility**: Can add additional constraints easily

### Limitations

1. **Fractional Solutions**: May require rounding heuristics
2. **Memory Usage**: O(n²) matrix can be large for many nodes
3. **Not Exact**: SDP is a relaxation of the original integer program

## Example

### Input:
```
Benefits: [[0.8, 0.5],
           [0.6, 0.9]]
Costs:    [[50, 40],
           [45, 60]]
Budget: 100
```

### SDP Solution:
```
Solution: [[0.895, 0.756],
           [0.123, 0.001]]
```

### Binary Solution (threshold 0.5):
```
Binary:   [[1, 1],
           [0, 0]]
```

### Non-Binary Positions:
- Position (0,1): value=0.756, benefit=0.5, cost=40
- Position (1,0): value=0.123, benefit=0.6, cost=45

**Interpretation:** First row nodes are selected, second row nodes are not. Position (0,1) has high confidence (0.756), while (1,0) is clearly rejected (0.123).

