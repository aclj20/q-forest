"""
Classic Optimization Solver for Q-FOREST

This module provides classical optimization using CVXPY for solving
knapsack-style problems with benefits and costs matrices.
"""

import cvxpy as cp
import numpy as np
import pandas as pd
from typing import Dict, List


def lineJump():
    """Print a separator line"""
    print("-" * 50)


def trunc(value, decimals=3):
    """Truncate a value to a specific number of decimals"""
    factor = 10 ** decimals
    return np.trunc(value * factor) / factor


def calculateNonBinaryPositions(matrix, weightCostMatrix, benefitMatrix):
    """
    Calculate positions with non-binary values (values between 0 and 1)
    
    Args:
        matrix: Solution matrix with values between 0 and 1
        weightCostMatrix: Cost matrix
        benefitMatrix: Benefit matrix
    
    Returns:
        List of dictionaries with position info and associated values
    """
    return [
        {
            "value": float(value),
            "pos": (i, j),
            "alpha_value": float(benefitMatrix[i, j]),
            "weight_value": float(weightCostMatrix[i, j])
        }
        for i, row in enumerate(matrix)
        for j, value in enumerate(row)
        if (value > 0.0001 and value < 0.99)
    ]


class ClassicSolver:
    """
    Classical optimization solver using semidefinite programming (SDP)
    to solve knapsack-style optimization problems
    """
    
    def __init__(self):
        """Initialize the classic solver"""
        self.result = None
        self.status = None
        self.selected_vector = None
        self.solution_matrix = None
        
    def solve(
        self,
        benefits: np.ndarray,
        costs: np.ndarray,
        budget: float,
        verbose: bool = True
    ) -> Dict:
        """
        Solve optimization problem using classical SDP approach
        
        Args:
            benefits: Benefits matrix (normalized 0-1), shape (n, n)
            costs: Costs matrix, shape (n, n)
            budget: Budget constraint (total cost allowed)
            verbose: Whether to print detailed output
            
        Returns:
            Dictionary containing:
                - solution_matrix: Matrix with values [0, 1] indicating selection
                - selected_vector: Flattened vector
                - objective_value: Optimal objective function value
                - status: Solver status
                - selected_count: Number of selected nodes
                - total_benefit: Total benefit of selected nodes
                - total_cost: Total cost of selected nodes
                - budget: Budget constraint
                - budget_utilization: Percentage of budget used
                - non_binary_positions: List of fractional (non-binary) positions
        """
        # Validate inputs
        if benefits.shape != costs.shape:
            raise ValueError(
                f"Benefits shape {benefits.shape} must match costs shape {costs.shape}"
            )
        
        if not isinstance(benefits, np.ndarray) or not isinstance(costs, np.ndarray):
            raise TypeError("Benefits and costs must be numpy arrays")
            
        # Flatten matrices to vectors
        alpha_list = benefits.flatten()
        cost_list = costs.flatten()
        
        # Get number of nodes plus 1 for the semidefinite matrix
        n_nodes_plus_1 = len(alpha_list) + 1
        
        # Define optimization variables (semidefinite programming)
        # Create a symmetric matrix variable
        variables = cp.Variable((n_nodes_plus_1, n_nodes_plus_1), symmetric=True)
        
        # Objective: Maximize total benefit
        # Using the formulation: maximize sum of 0.5 * (1 + X_0i) * benefit_i
        objective = cp.Maximize(
            sum(0.5 * (1 + variables[0, i]) * alpha_list[i - 1] 
                for i in range(1, n_nodes_plus_1))
        )
        
        # Constraints
        constraints = []
        
        # Budget constraint: sum of 0.5 * (1 + X_0i) * cost_i <= budget
        constraints.append(
            sum(0.5 * (1 + variables[0, i]) * cost_list[i - 1] 
                for i in range(1, n_nodes_plus_1)) <= budget
        )
        
        # Semidefinite constraint: X >= 0 (positive semidefinite)
        constraints.append(variables >> 0)
        
        # Diagonal elements equal to 1
        for i in range(n_nodes_plus_1):
            constraints.append(variables[i, i] == 1)
        
        # Solve the problem
        problem = cp.Problem(objective, constraints)
        result = problem.solve()
        
        # Extract solution - remove first element (index 0)
        variablesArray = np.delete(np.array(variables.value[0]), 0)
        selected_vector = variablesArray
        
        # Reshape solution to matrix form
        unNormalizedSolutionMatrix = selected_vector.reshape(benefits.shape)
        
        # Normalize solution matrix to [0, 1] range and apply truncation
        # Transform from [-1, 1] to [0, 1] with 3 decimal precision
        normalizedSolutionMatrix = np.array([
            [float(trunc((element + 1) / 2, 3)) for element in line]
            for line in unNormalizedSolutionMatrix
        ])
        
        # Store results
        self.result = result
        self.status = problem.status
        self.selected_vector = selected_vector
        self.solution_matrix = normalizedSolutionMatrix
        
        # Calculate non-binary positions
        not_binary_positions = calculateNonBinaryPositions(
            normalizedSolutionMatrix, costs, benefits
        )
        
        # Calculate statistics
        selected_count = int(np.sum(normalizedSolutionMatrix > 0.5))
        total_benefit = float(np.sum(normalizedSolutionMatrix * benefits))
        total_cost = float(np.sum(normalizedSolutionMatrix * costs))
        
        if verbose:
            lineJump()
            print("CLASSIC SOLVER RESULTS")
            lineJump()
            print(f"Problem status: {problem.status}")
            print(f"Optimal Solution: {result:.2f}")
            lineJump()
            
            if not_binary_positions:
                print("Non-binary positions (fractional values):")
                for item in not_binary_positions:
                    print(f"  Position {item['pos']}: value={item['value']:.3f}, "
                          f"benefit={item['alpha_value']:.3f}, cost={item['weight_value']:.2f}")
                lineJump()
            
            print(f"Variables (vector): {[float(v) for v in selected_vector]}")
            lineJump()
            print("Solution Matrix:")
            print(normalizedSolutionMatrix)
            lineJump()
            print(f"Selected nodes: {selected_count}")
            print(f"Total benefit: {total_benefit:.4f}")
            print(f"Total cost: {total_cost:.2f}")
            print(f"Budget: {budget:.2f}")
            print(f"Budget utilization: {(total_cost/budget)*100:.2f}%")
            lineJump()
        
        return {
            "solution_matrix": normalizedSolutionMatrix,
            "selected_vector": selected_vector,
            "objective_value": float(result) if result is not None else None,
            "status": problem.status,
            "selected_count": selected_count,
            "total_benefit": total_benefit,
            "total_cost": total_cost,
            "budget": budget,
            "budget_utilization": (total_cost / budget) * 100 if budget > 0 else 0,
            "non_binary_positions": not_binary_positions
        }
    
    def solve_from_files(
        self,
        benefits_csv_path: str,
        costs_csv_path: str,
        budget: float,
        verbose: bool = True
    ) -> Dict:
        """
        Solve optimization problem from CSV files
        
        Args:
            benefits_csv_path: Path to benefits CSV file
            costs_csv_path: Path to costs CSV file
            budget: Budget constraint
            verbose: Whether to print detailed output
            
        Returns:
            Dictionary with solution and statistics (same as solve())
        """
        # Load matrices from CSV files
        benefits = pd.read_csv(benefits_csv_path, header=None).values
        costs = pd.read_csv(costs_csv_path, header=None).values
        
        return self.solve(benefits, costs, budget, verbose)


def solve_optimization_from_files(
    benefits_csv_path: str,
    costs_csv_path: str,
    budget: float = 2.0
) -> np.ndarray:
    """
    Convenience function for backward compatibility
    
    Args:
        benefits_csv_path: Path to benefits CSV
        costs_csv_path: Path to costs CSV
        budget: Budget constraint
        
    Returns:
        Solution matrix (normalized 0/1)
    """
    solver = ClassicSolver()
    result = solver.solve_from_files(benefits_csv_path, costs_csv_path, budget)
    return result["solution_matrix"]


if __name__ == "__main__":
    """
    Example usage
    """
    import sys
    from pathlib import Path
    
    # Example with 36 nodes
    benefits_path = "../preprocessing/data/map2_36nodes_benefits_normalized_matrix.csv"
    costs_path = "../preprocessing/data/map2_36nodes_costs_matrix.csv"
    
    lineJump()
    print("Q-FOREST Classic Solver - Example Usage")
    lineJump()
    print()
    
    # Check if files exist
    if not Path(benefits_path).exists():
        print(f"⚠️  Benefits file not found: {benefits_path}")
        print("Please run preprocessing first to generate input files.")
        sys.exit(1)
    
    if not Path(costs_path).exists():
        print(f"⚠️  Costs file not found: {costs_path}")
        print("Please run preprocessing first to generate input files.")
        sys.exit(1)
    
    # Create solver
    solver = ClassicSolver()
    
    # Solve from files
    result = solver.solve_from_files(
        benefits_csv_path=benefits_path,
        costs_csv_path=costs_path,
        budget=400.0,
        verbose=True
    )
    
    lineJump()
    print("Solution Summary:")
    lineJump()
    print(f"Status: {result['status']}")
    print(f"Objective Value: {result['objective_value']:.4f}")
    print(f"Selected Nodes: {result['selected_count']}")
    print(f"Total Benefit: {result['total_benefit']:.4f}")
    print(f"Total Cost: {result['total_cost']:.2f}")
    print(f"Budget: {result['budget']:.2f}")
    print(f"Budget Utilization: {result['budget_utilization']:.2f}%")
    print(f"Non-binary positions: {len(result['non_binary_positions'])}")
    lineJump()
