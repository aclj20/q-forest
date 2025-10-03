"""
Classic Optimization Solver for Q-FOREST

This module provides classical optimization using CVXPY for solving
knapsack-style problems with benefits and costs matrices.
"""

import cvxpy as cp
import numpy as np
from typing import Dict


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
                - solution_matrix: Binary matrix (0/1) indicating selected nodes
                - selected_vector: Flattened binary vector
                - objective_value: Optimal objective function value
                - status: Solver status
                - selected_count: Number of selected nodes
                - total_benefit: Total benefit of selected nodes
                - total_cost: Total cost of selected nodes
        """
        # Validate inputs
        if benefits.shape != costs.shape:
            raise ValueError(
                f"Benefits shape {benefits.shape} must match costs shape {costs.shape}"
            )
        
        if not isinstance(benefits, np.ndarray) or not isinstance(costs, np.ndarray):
            raise TypeError("Benefits and costs must be numpy arrays")
            
        # Flatten matrices to vectors
        alphaList = benefits.flatten()
        weightCostList = costs.flatten()
        
        n_nodes = len(alphaList)
        
        # Create optimization variables (SDP formulation)
        variables = cp.Variable((n_nodes + 1, n_nodes + 1), symmetric=True)
        
        # Objective: Maximize total benefit
        objective = cp.Maximize(
            sum((.5 * (1 + variables[0, i]) * alphaList[i - 1] 
                 for i in range(1, n_nodes + 1)))
        )
        
        # Constraints
        # 1. Budget constraint: total cost <= budget
        constraint = [
            sum((.5 * (1 + variables[0, i]) * weightCostList[i - 1] 
                 for i in range(1, n_nodes + 1))) <= budget
        ]
        
        # 2. Positive semidefinite constraint
        constraint += [variables >> 0]
        
        # 3. Diagonal elements must be 1
        for i in range(n_nodes + 1):
            constraint += [variables[i, i] == 1]
        
        # Solve the problem
        problem = cp.Problem(objective, constraint)
        result = problem.solve()
        
        # Extract solution
        variablesArray = np.delete(np.array(variables.value[0]), 0)
        selected_vector = variablesArray
        
        # Reshape to original matrix shape
        unNormalizedSolutionMatrix = selected_vector.reshape(benefits.shape)
        
        # Normalize to binary 0/1 (rounding)
        normalizedSolutionMatrix = np.array([
            [np.round((element + 1) / 2, 5) for element in line] 
            for line in unNormalizedSolutionMatrix
        ])
        
        # Store results
        self.result = result
        self.status = problem.status
        self.selected_vector = selected_vector
        self.solution_matrix = normalizedSolutionMatrix
        
        # Calculate statistics
        binary_matrix = (normalizedSolutionMatrix > 0.5).astype(int)
        selected_count = int(np.sum(binary_matrix))
        total_benefit = float(np.sum(benefits * binary_matrix))
        total_cost = float(np.sum(costs * binary_matrix))
        
        if verbose:
            print(f"Problem status: {problem.status}")
            print(f"Optimal Solution: {result:.2f}")
            print(f"Variables (vector): {selected_vector}")
            print("Solution Matrix (0/1):")
            print(normalizedSolutionMatrix)
            print("\nStatistics:")
            print(f"  Selected nodes: {selected_count}/{n_nodes}")
            print(f"  Total benefit: {total_benefit:.4f}")
            print(f"  Total cost: {total_cost:.2f} (budget: {budget})")
        
        return {
            "solution_matrix": normalizedSolutionMatrix,
            "selected_vector": selected_vector,
            "objective_value": float(result) if result is not None else None,
            "status": problem.status,
            "selected_count": selected_count,
            "total_benefit": total_benefit,
            "total_cost": total_cost,
            "budget": budget,
            "budget_utilization": (total_cost / budget * 100) if budget > 0 else 0
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
        import pandas as pd
        
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
    
    # Example with default test files
    benefits_path = "../preprocessing/data/map2_9nodes_benefits_normalized_matrix.csv"
    costs_path = "../preprocessing/data/map2_9nodes_costs_matrix.csv"
    
    print("=" * 60)
    print("Q-FOREST Classic Solver - Example Usage")
    print("=" * 60)
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
        budget=2.0,
        verbose=True
    )
    
    print("\n" + "=" * 60)
    print("Solution Summary:")
    print("=" * 60)
    print(f"Status: {result['status']}")
    print(f"Objective Value: {result['objective_value']:.4f}")
    print(f"Selected Nodes: {result['selected_count']}")
    print(f"Total Benefit: {result['total_benefit']:.4f}")
    print(f"Total Cost: {result['total_cost']:.2f}")
    print(f"Budget: {result['budget']:.2f}")
    print(f"Budget Utilization: {result['budget_utilization']:.2f}%")
    print()
    print("Solution Matrix:")
    print(result['solution_matrix'])
