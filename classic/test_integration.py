"""
Integration test for classic solver with Q-FOREST pipeline
"""

import numpy as np
import sys
from pathlib import Path

# Add preprocessing to path
sys.path.append(str(Path(__file__).parent.parent / "preprocessing"))
from image_to_graph import HeatmapToGraph
from classic_solver import ClassicSolver


def test_complete_pipeline():
    """Test complete pipeline: preprocessing → optimization → solution"""
    
    print("=" * 70)
    print("Q-FOREST Complete Pipeline Test")
    print("=" * 70)
    print()
    
    # Step 1: Preprocessing - Generate benefits and costs
    print("Step 1: Preprocessing (Generating benefits and costs matrices)")
    print("-" * 70)
    
    image_path = "../preprocessing/data/map2.png"
    if not Path(image_path).exists():
        print(f"❌ Test image not found: {image_path}")
        print("Please ensure preprocessing/data/map2.png exists")
        return False
    
    grid_size = (3, 3)  # 9 nodes
    converter = HeatmapToGraph(grid_size=grid_size)
    
    try:
        converter.load_image(image_path)
        converter.create_grid_nodes()
        converter.create_edges(connection_type="adjacent")
        
        # Get matrices
        _, benefits = converter.get_weight_matrix()
        costs = converter.get_cost_matrix()
        
        print(f"✅ Generated {grid_size[0]}×{grid_size[1]} grid ({grid_size[0] * grid_size[1]} nodes)")
        print(f"   Benefits shape: {benefits.shape}, range: [{benefits.min():.3f}, {benefits.max():.3f}]")
        print(f"   Costs shape: {costs.shape}, range: [{costs.min():.2f}, {costs.max():.2f}]")
        print()
        
    except Exception as e:
        print(f"❌ Preprocessing failed: {e}")
        return False
    
    # Step 2: Classical Optimization
    print("Step 2: Classical Optimization")
    print("-" * 70)
    
    budget = 200.0
    solver = ClassicSolver()
    
    try:
        result = solver.solve(
            benefits=benefits,
            costs=costs,
            budget=budget,
            verbose=False
        )
        
        print(f"✅ Optimization completed")
        print(f"   Status: {result['status']}")
        print(f"   Objective value: {result['objective_value']:.4f}")
        print(f"   Selected nodes: {result['selected_count']}/{benefits.size}")
        print(f"   Total benefit: {result['total_benefit']:.4f}")
        print(f"   Total cost: {result['total_cost']:.2f} (budget: {budget})")
        print(f"   Budget utilization: {result['budget_utilization']:.2f}%")
        print()
        
        # Display solution matrix
        print("   Solution matrix:")
        solution = result['solution_matrix']
        binary_solution = (solution > 0.5).astype(int)
        for row in binary_solution:
            print("   ", row)
        print()
        
    except Exception as e:
        print(f"❌ Optimization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Validation
    print("Step 3: Validation")
    print("-" * 70)
    
    # Validate solution
    binary_solution = (result['solution_matrix'] > 0.5).astype(int)
    actual_cost = np.sum(costs * binary_solution)
    actual_benefit = np.sum(benefits * binary_solution)
    
    print(f"   Verifying costs: {actual_cost:.2f} <= {budget} : ", end="")
    if actual_cost <= budget + 1e-6:  # Small tolerance for floating point
        print("✅ PASS")
    else:
        print("❌ FAIL")
        return False
    
    print(f"   Verifying benefits: {actual_benefit:.4f} : ", end="")
    if abs(actual_benefit - result['total_benefit']) < 1e-6:
        print("✅ PASS")
    else:
        print("❌ FAIL")
        return False
    
    print(f"   Verifying matrix shape: {binary_solution.shape} == {grid_size} : ", end="")
    if binary_solution.shape == grid_size:
        print("✅ PASS")
    else:
        print("❌ FAIL")
        return False
    
    print()
    
    # Summary
    print("=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
    print()
    print("Summary:")
    print(f"  - Preprocessed {grid_size[0] * grid_size[1]} nodes from heatmap")
    print(f"  - Optimized with budget constraint: {budget}")
    print(f"  - Selected {result['selected_count']} optimal nodes")
    print(f"  - Achieved benefit: {result['total_benefit']:.4f}")
    print(f"  - Solution can be used for visualization with postprocessing module")
    print()
    
    return True


def test_multiple_budgets():
    """Test optimization with different budget values"""
    
    print("=" * 70)
    print("Budget Sensitivity Analysis")
    print("=" * 70)
    print()
    
    # Use simple test data
    benefits = np.array([
        [0.9, 0.7, 0.8],
        [0.6, 0.95, 0.5],
        [0.75, 0.65, 0.85]
    ])
    
    costs = np.array([
        [50, 45, 48],
        [55, 60, 40],
        [52, 43, 58]
    ])
    
    budgets = [100, 150, 200, 250, 300]
    
    solver = ClassicSolver()
    
    print(f"{'Budget':<12} {'Selected':<12} {'Benefit':<12} {'Cost':<12} {'Utilization':<15}")
    print("-" * 70)
    
    for budget in budgets:
        result = solver.solve(benefits, costs, budget, verbose=False)
        print(f"{budget:<12.0f} {result['selected_count']:<12} "
              f"{result['total_benefit']:<12.4f} {result['total_cost']:<12.2f} "
              f"{result['budget_utilization']:<15.2f}%")
    
    print()


if __name__ == "__main__":
    # Run integration test
    success = test_complete_pipeline()
    
    if success:
        print()
        test_multiple_budgets()
    else:
        print("\n❌ Integration test failed")
        sys.exit(1)

