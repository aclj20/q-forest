# %%
"""
Ejemplo de cómo usar las matrices de BENEFICIOS y COSTOS
"""

import numpy as np
from image_to_graph import HeatmapToGraph

def demonstrate_benefits_and_costs():
    """
    Demostrar cómo acceder y usar tanto beneficios como costos
    """
    print("="*60)
    print("EJEMPLO: BENEFICIOS vs COSTOS")
    print("="*60)
    
    # Crear convertidor
    converter = HeatmapToGraph(grid_size=(5, 5))
    
    # Procesar heatmap
    converter.load_image("data/map.png")
    converter.create_grid_nodes()
    converter.create_edges()
    
    # Obtener matrices
    benefits_matrix, benefits_norm = converter.get_weight_matrix()
    costs_matrix = converter.get_cost_matrix()
    
    print(f"\nMATRICES OBTENIDAS:")
    print(f"Beneficios (5x5): rango [{benefits_norm.min():.3f}, {benefits_norm.max():.3f}]")
    print(f"Costos (5x5): rango [{costs_matrix.min():.3f}, {costs_matrix.max():.3f}]")
    
    # ANÁLISIS: Encontrar mejores nodos considerando beneficio/costo
    print(f"\n" + "="*60)
    print("ANÁLISIS BENEFICIO vs COSTO")
    print("="*60)
    
    # Calcular ratio beneficio/costo para cada nodo
    ratio_matrix = benefits_norm / (costs_matrix + 0.001)  # +0.001 para evitar división por 0
    
    print(f"\nMATRIZ RATIO (Beneficio/Costo):")
    print(ratio_matrix)
    
    # Encontrar los mejores nodos por diferentes criterios
    print(f"\nANÁLISIS POR CRITERIOS:")
    print("-" * 40)
    
    # 1. Mayor beneficio
    max_benefit_pos = np.unravel_index(benefits_norm.argmax(), benefits_norm.shape)
    max_benefit = benefits_norm[max_benefit_pos]
    cost_at_max_benefit = costs_matrix[max_benefit_pos]
    
    print(f"MAYOR BENEFICIO:")
    print(f"  Posición: {max_benefit_pos}")
    print(f"  Beneficio: {max_benefit:.4f}")
    print(f"  Costo: {cost_at_max_benefit:.4f}")
    print(f"  Ratio: {max_benefit/cost_at_max_benefit:.4f}")
    
    # 2. Menor costo
    min_cost_pos = np.unravel_index(costs_matrix.argmin(), costs_matrix.shape)
    min_cost = costs_matrix[min_cost_pos]
    benefit_at_min_cost = benefits_norm[min_cost_pos]
    
    print(f"\nMENOR COSTO:")
    print(f"  Posición: {min_cost_pos}")
    print(f"  Beneficio: {benefit_at_min_cost:.4f}")
    print(f"  Costo: {min_cost:.4f}")
    print(f"  Ratio: {benefit_at_min_cost/min_cost:.4f}")
    
    # 3. Mejor ratio beneficio/costo
    best_ratio_pos = np.unravel_index(ratio_matrix.argmax(), ratio_matrix.shape)
    best_ratio = ratio_matrix[best_ratio_pos]
    benefit_at_best_ratio = benefits_norm[best_ratio_pos]
    cost_at_best_ratio = costs_matrix[best_ratio_pos]
    
    print(f"\nMEJOR RATIO BENEFICIO/COSTO:")
    print(f"  Posición: {best_ratio_pos}")
    print(f"  Beneficio: {benefit_at_best_ratio:.4f}")
    print(f"  Costo: {cost_at_best_ratio:.4f}")
    print(f"  Ratio: {best_ratio:.4f}")
    
    # 4. Nodos con alto beneficio y bajo costo (filtro combinado)
    high_benefit_mask = benefits_norm > np.percentile(benefits_norm, 75)  # Top 25%
    low_cost_mask = costs_matrix < np.percentile(costs_matrix, 25)        # Bottom 25%
    optimal_mask = high_benefit_mask & low_cost_mask
    
    print(f"\nNODOS ÓPTIMOS (Alto beneficio + Bajo costo):")
    optimal_positions = np.where(optimal_mask)
    if len(optimal_positions[0]) > 0:
        for i in range(len(optimal_positions[0])):
            row, col = optimal_positions[0][i], optimal_positions[1][i]
            benefit = benefits_norm[row, col]
            cost = costs_matrix[row, col]
            ratio = benefit / cost
            print(f"  Posición ({row},{col}): Beneficio={benefit:.4f}, Costo={cost:.4f}, Ratio={ratio:.4f}")
    else:
        print("  No hay nodos que cumplan ambos criterios")
    
    # Exportar análisis
    np.savetxt("data/ratio_benefit_cost_matrix.csv", ratio_matrix, delimiter=',', fmt='%.6f')
    
    print(f"\n" + "="*60)
    print("ARCHIVOS DISPONIBLES EN data/:")
    print("• *_benefits_normalized_matrix.csv - Matriz de beneficios (0-1)")
    print("• *_costs_matrix.csv - Matriz de costos aleatorios (0-1)")
    print("• ratio_benefit_cost_matrix.csv - Matriz de ratios beneficio/costo")
    print("="*60)
    
    return benefits_norm, costs_matrix, ratio_matrix

if __name__ == "__main__":
    benefits, costs, ratios = demonstrate_benefits_and_costs()
    
    print(f"\nEJEMPLOS DE USO:")
    print("1. Para optimización: usar matriz de ratios beneficio/costo")
    print("2. Para restricción de presupuesto: filtrar por costos máximos")
    print("3. Para maximizar beneficios: usar matriz de beneficios normalizados")
    print("4. Para análisis multiobjetivo: considerar ambas matrices simultáneamente")
