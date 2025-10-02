# %%
"""
Ejemplo de uso de la clase HeatmapToGraph para obtener matrices y grafo
"""

from image_to_graph import HeatmapToGraph
import numpy as np

# %%
def example_usage():
    """
    Ejemplo de cómo usar la clase para obtener matrices y el grafo
    """
    
    # Crear el convertidor con una grilla de 5x5 (más pequeña para ejemplo)
    converter = HeatmapToGraph(grid_size=(5, 5))
    
    try:
        # Cargar imagen (asegúrate de que data/map.png exista)
        print("Cargando imagen...")
        converter.load_image("data/map.png")
        
        # Crear nodos y aristas
        print("Creando nodos...")
        converter.create_grid_nodes()
        
        print("Creando aristas...")
        converter.create_edges(connection_type="adjacent")
        
        # OBTENER LAS MATRICES
        print("\n" + "="*50)
        print("EXTRAYENDO MATRICES DEL GRAFO")
        print("="*50)
        
        # 1. Matriz de Adyacencia
        adj_matrix, nodes = converter.get_adjacency_matrix()
        print(f"\n1. MATRIZ DE ADYACENCIA:")
        print(f"   Forma: {adj_matrix.shape}")
        print(f"   Tipo: {type(adj_matrix)}")
        print(f"   Primeras 5x5 entradas:")
        print(adj_matrix[:5, :5])
        
        # 2. Matriz de Pesos
        weight_matrix, weight_normalized = converter.get_weight_matrix()
        print(f"\n2. MATRIZ DE PESOS:")
        print(f"   Forma: {weight_matrix.shape}")
        print(f"   Pesos originales:")
        print(weight_matrix)
        print(f"   Pesos normalizados (0-1):")
        print(weight_normalized)
        
        # 3. Matrices de Coordenadas
        x_coords, y_coords = converter.get_node_coordinates_matrix()
        print(f"\n3. COORDENADAS DE NODOS:")
        print(f"   Forma: {x_coords.shape}")
        print(f"   Coordenadas X:")
        print(x_coords.astype(int))
        print(f"   Coordenadas Y:")
        print(y_coords.astype(int))
        
        # 4. Grafo NetworkX
        print(f"\n4. GRAFO NETWORKX:")
        print(f"   Tipo: {type(converter.graph)}")
        print(f"   Número de nodos: {converter.graph.number_of_nodes()}")
        print(f"   Número de aristas: {converter.graph.number_of_edges()}")
        
        # Ejemplo de acceso a datos de nodos
        print(f"\n   Información del primer nodo:")
        first_node = list(converter.graph.nodes())[0]
        node_data = converter.graph.nodes[first_node]
        print(f"   Nodo: {first_node}")
        print(f"   Peso: {node_data['peso']:.2f}")
        print(f"   Peso normalizado: {node_data['peso_normalizado']:.4f}")
        print(f"   Posición: {node_data['posicion']}")
        
        # EXPORTAR MATRICES A ARCHIVOS
        print(f"\n5. EXPORTANDO MATRICES A ARCHIVOS:")
        files_created = converter.export_matrices_to_files("ejemplo")
        for file_type, filepath in files_created.items():
            print(f"   {file_type}: {filepath}")
        
        # EJEMPLOS PRÁCTICOS DE USO
        print(f"\n" + "="*50)
        print("EJEMPLOS PRÁCTICOS DE USO")
        print("="*50)
        
        # Encontrar el nodo con mayor peso
        max_weight_idx = np.unravel_index(weight_normalized.argmax(), 
                                         weight_normalized.shape)
        max_weight_value = weight_normalized[max_weight_idx]
        print(f"\n• Nodo con mayor peso:")
        print(f"  Posición en grilla: {max_weight_idx}")
        print(f"  Peso normalizado: {max_weight_value:.4f}")
        
        # Calcular distancia promedio entre nodos conectados
        edge_weights = [d['weight'] for _, _, d in converter.graph.edges(data=True)]
        avg_edge_weight = np.mean(edge_weights) if edge_weights else 0
        print(f"\n• Peso promedio de aristas: {avg_edge_weight:.4f}")
        
        # Mostrar conexiones del nodo central
        center_node = (2, 2)  # Centro de grilla 5x5
        if center_node in converter.graph:
            neighbors = list(converter.graph.neighbors(center_node))
            print(f"\n• Conexiones del nodo central {center_node}:")
            for neighbor in neighbors:
                edge_weight = converter.graph.edges[center_node, neighbor]['weight']
                print(f"  -> {neighbor} (peso arista: {edge_weight:.4f})")
        
        return {
            'adjacency_matrix': adj_matrix,
            'weight_matrix': weight_matrix,
            'weight_normalized': weight_normalized,
            'x_coordinates': x_coords,
            'y_coordinates': y_coords,
            'graph': converter.graph,
            'nodes': nodes
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# %%
if __name__ == "__main__":
    # Ejecutar ejemplo
    result = example_usage()
    
    if result:
        print(f"\n" + "="*50)
        print("¡ÉXITO! Matrices y grafo extraídos correctamente.")
        print("="*50)
        print("\nPuedes acceder a los datos usando:")
        print("• result['adjacency_matrix'] - Matriz de adyacencia")
        print("• result['weight_matrix'] - Matriz de pesos originales") 
        print("• result['weight_normalized'] - Matriz de pesos normalizados")
        print("• result['x_coordinates'] - Coordenadas X de nodos")
        print("• result['y_coordinates'] - Coordenadas Y de nodos")
        print("• result['graph'] - Objeto NetworkX completo")
        print("• result['nodes'] - Lista de nodos ordenados")
    else:
        print("No se pudieron extraer las matrices. Revisa que la imagen exista.")
