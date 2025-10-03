"""
Example usage of the Classic Solver module
"""

import numpy as np
from classic_solver import ClassicSolver


def example_from_arrays():
    """Example: Solve from numpy arrays"""
    print("=" * 60)
    print("Example 1: Solving from NumPy arrays")
    print("=" * 60)
    print()
    
    # Create sample 3x3 grid
    benefits = np.array([
        [0.8, 0.5, 0.7],
        [0.6, 0.9, 0.4],
        [0.7, 0.5, 0.8]
    ])
    
    costs = np.array([
        [50, 40, 45],
        [55, 60, 35],
        [48, 42, 52]
    ])
    
    budget = 150.0
    
    solver = ClassicSolver()
    result = solver.solve(benefits, costs, budget, verbose=True)
    
    print("\n✅ Solution found!")
    print(f"Selected {result['selected_count']} out of 9 nodes")
    print()


def example_from_files():
    """Example: Solve from CSV files"""
    print("=" * 60)
    print("Example 2: Solving from CSV files")
    print("=" * 60)
    print()
    
    benefits_path = "../preprocessing/data/map2_9nodes_benefits_normalized_matrix.csv"
    costs_path = "../preprocessing/data/map2_9nodes_costs_matrix.csv"
    
    from pathlib import Path
    if not Path(benefits_path).exists():
        print("⚠️  Test files not found. Run preprocessing first:")
        print("  cd preprocessing")
        print("  python image_to_graph.py data/map2.png --nodes 9")
        return
    
    solver = ClassicSolver()
    result = solver.solve_from_files(
        benefits_csv_path=benefits_path,
        costs_csv_path=costs_path,
        budget=2.0,
        verbose=True
    )
    
    print("\n✅ Solution found!")
    print(f"Budget utilization: {result['budget_utilization']:.2f}%")
    print()


def example_multiple_budgets():
    """Example: Test multiple budget values"""
    print("=" * 60)
    print("Example 3: Testing multiple budget values")
    print("=" * 60)
    print()
    
    benefits = np.array([
        [0.8, 0.6],
        [0.7, 0.9]
    ])
    
    costs = np.array([
        [50, 40],
        [45, 60]
    ])
    
    budgets = [50, 100, 150, 200]
    
    solver = ClassicSolver()
    
    print(f"{'Budget':<10} {'Selected':<10} {'Benefit':<10} {'Cost':<10} {'Utilization':<15}")
    print("-" * 60)
    
    for budget in budgets:
        result = solver.solve(benefits, costs, budget, verbose=False)
        print(f"{budget:<10.0f} {result['selected_count']:<10} "
              f"{result['total_benefit']:<10.4f} {result['total_cost']:<10.2f} "
              f"{result['budget_utilization']:<15.2f}%")
    print()


if __name__ == "__main__":
    # Run all examples
    example_from_arrays()
    print("\n" + "=" * 60 + "\n")
    
    example_from_files()
    print("\n" + "=" * 60 + "\n")
    
    example_multiple_budgets()
    print("\n" + "=" * 60)
    print("✨ All examples completed!")
    print("=" * 60)

