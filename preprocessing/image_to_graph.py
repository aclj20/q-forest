# %%

import numpy as np
import cv2
import matplotlib.pyplot as plt
import networkx as nx
from PIL import Image
from typing import Tuple, Dict
import argparse
import os


class HeatmapToGraph:
    """
    Convierte una imagen de mapa de calor en un grafo con nodos ponderados
    (Converts a heatmap image into a weighted graph)
    """

    def __init__(self, grid_size: Tuple[int, int] = (10, 10)):
        """
        Inicializa el convertidor de heatmap a grafo

        Args:
            grid_size: Tupla (filas, columnas) para el tamaño de la grilla
        """
        self.grid_size = grid_size
        self.image = None
        self.heatmap_values = None
        self.nodes = {}
        self.graph = nx.Graph()

    def load_image(self, image_path: str) -> np.ndarray:
        """
        Cargar imagen PNG y convertir a escala de grises para análisis

        Args:
            image_path: Ruta a la imagen PNG

        Returns:
            Array numpy de la imagen en escala de grises
        """
        try:
            # Cargar imagen usando PIL para mejor compatibilidad con PNG
            pil_image = Image.open(image_path)

            # Convertir a RGB si es necesario
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')

            # Convertir a numpy array
            image_array = np.array(pil_image)

            # Convertir a escala de grises para análisis del heatmap
            if len(image_array.shape) == 3:
                # Usar conversión ponderada para mejor representación
                gray_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            else:
                gray_image = image_array

            self.image = image_array
            self.heatmap_values = gray_image

            print(f"Imagen cargada: {image_array.shape}")
            print(f"Rango de valores del heatmap: "
                  f"{gray_image.min()} - {gray_image.max()}")

            return image_array

        except Exception as e:
            raise Exception(f"Error al cargar la imagen: {str(e)}")

    def create_grid_nodes(self) -> Dict[Tuple[int, int], Dict]:
        """
        Crear nodos en una grilla sobre la imagen y calcular pesos basados en
        diversidad de colores del heatmap (más colores = mejor lugar)

        Returns:
            Diccionario con información de los nodos
        """
        if self.heatmap_values is None:
            raise ValueError("Primero debe cargar una imagen")

        rows, cols = self.grid_size
        img_height, img_width = self.heatmap_values.shape

        # Calcular el tamaño de cada celda de la grilla
        cell_height = img_height // rows
        cell_width = img_width // cols

        self.nodes = {}
        self.graph.clear()

        for i in range(rows):
            for j in range(cols):
                # Calcular las coordenadas del centro de cada celda
                center_y = int(i * cell_height + cell_height // 2)
                center_x = int(j * cell_width + cell_width // 2)

                # Extraer la región de la celda para calcular el peso
                y_start = i * cell_height
                y_end = min((i + 1) * cell_height, img_height)
                x_start = j * cell_width
                x_end = min((j + 1) * cell_width, img_width)

                # Extraer región de la imagen original (color) y grayscale
                if len(self.image.shape) == 3:
                    color_region = self.image[y_start:y_end, x_start:x_end]
                else:
                    color_region = self.image[y_start:y_end, x_start:x_end]

                gray_region = self.heatmap_values[y_start:y_end, x_start:x_end]

                # NUEVO ALGORITMO DE PESO BASADO EN DIVERSIDAD DE COLORES
                peso_normalizado = self._calculate_color_diversity_weight(
                    color_region, gray_region)

                # GENERAR COSTO BASADO EN COLUMNA
                # Primera columna (j=0): costo = 30
                # Cada columna a la derecha: costo aumenta en 15
                costo_columna = 30 + (j * 15)  # j=0: 30, j=1: 45, j=2: 60, etc.

                # Información del nodo
                node_info = {
                    'posicion': (center_x, center_y),
                    'peso': peso_normalizado * 255.0,  # Escalar para compatibilidad
                    'peso_normalizado': peso_normalizado,  # BENEFICIO
                    'costo': costo_columna,  # COSTO BASADO EN COLUMNA
                    'region': (x_start, y_start, x_end, y_end),
                    'id': f"node_{i}_{j}"
                }

                self.nodes[(i, j)] = node_info

                # Agregar nodo al grafo NetworkX
                self.graph.add_node((i, j), **node_info)

        print(f"Creados {len(self.nodes)} nodos en grilla {rows}x{cols}")
        print("BENEFICIOS: Basados en colores específicos del heatmap (PINK/MAGENTA y VERDE)")
        print("COSTOS: Generados aleatoriamente entre 30 y 100 para cada nodo")
        return self.nodes

    def _calculate_color_diversity_weight(self, color_region: np.ndarray,
                                        gray_region: np.ndarray) -> float:
        """
        Calcular peso basado en la presencia de colores específicos del heatmap:
        PINK/MAGENTA y VERDE del heatmap (no del bosque)

        Args:
            color_region: Región de la imagen en color
            gray_region: Región de la imagen en escala de grises

        Returns:
            Peso normalizado entre 0 y 1
        """
        if color_region.size == 0:
            return 0.0

        # Convertir a HSV para mejor detección de colores específicos
        if len(color_region.shape) == 3:
            # Normalizar a rango 0-1 para HSV
            color_region_norm = color_region.astype(np.float32) / 255.0
            
            # Convertir RGB a HSV manualmente (OpenCV requiere uint8)
            color_region_uint8 = (color_region_norm * 255).astype(np.uint8)
            hsv_region = cv2.cvtColor(color_region_uint8, cv2.COLOR_RGB2HSV)
            
            # Extraer canales HSV
            hue = hsv_region[:, :, 0].astype(np.float32)
            saturation = hsv_region[:, :, 1].astype(np.float32) / 255.0
            value = hsv_region[:, :, 2].astype(np.float32) / 255.0
            
            # DETECTAR COLORES ESPECÍFICOS DEL HEATMAP
            
            # 1. DETECTAR PINK/MAGENTA (Hue ~ 300-330 o 0-20)
            pink_mask1 = ((hue >= 150) & (hue <= 180)) & (saturation > 0.3) & (value > 0.3)  # Magenta range in OpenCV
            pink_mask2 = ((hue >= 0) & (hue <= 10)) & (saturation > 0.4) & (value > 0.4)     # Pink range
            pink_mask = pink_mask1 | pink_mask2
            pink_coverage = np.sum(pink_mask) / pink_mask.size
            
            # 2. DETECTAR VERDE del heatmap (Hue ~ 60-100, high saturation para distinguir del bosque)
            # Verde del heatmap tiene mayor saturación que el verde natural del bosque
            green_mask = ((hue >= 40) & (hue <= 80)) & (saturation > 0.4) & (value > 0.3)
            green_coverage = np.sum(green_mask) / green_mask.size
            
            # 3. DETECTAR intensidad general (para áreas que podrían tener heatmap)
            high_intensity_mask = value > 0.7  # Áreas brillantes
            intensity_coverage = np.sum(high_intensity_mask) / high_intensity_mask.size
            
            # 4. EVITAR áreas que son principalmente bosque (verde oscuro, baja saturación)
            forest_mask = ((hue >= 35) & (hue <= 85)) & (saturation < 0.4) & (value < 0.6)
            forest_penalty = np.sum(forest_mask) / forest_mask.size
            
        else:
            # Si es escala de grises, usar solo intensidad
            pink_coverage = 0.0
            green_coverage = 0.0
            intensity_coverage = np.sum(gray_region > 180) / gray_region.size
            forest_penalty = 0.0
        
        # CALCULAR PESO BASADO EN PRESENCIA DE COLORES DEL HEATMAP
        
        # Factor 1: Cobertura de PINK/MAGENTA (peso alto)
        pink_score = pink_coverage * 2.0  # Amplificar el impacto del pink
        
        # Factor 2: Cobertura de VERDE del heatmap (peso alto)
        green_score = green_coverage * 1.8  # Amplificar el verde del heatmap
        
        # Factor 3: Intensidad general (soporte)
        intensity_score = intensity_coverage * 0.5
        
        # Factor 4: Penalización por áreas de bosque
        forest_penalty_score = forest_penalty * 0.3
        
        # Combinar factores
        weight = (
            0.5 * pink_score +           # 50% peso al pink/magenta
            0.3 * green_score +          # 30% peso al verde del heatmap  
            0.2 * intensity_score -      # 20% intensidad general
            0.1 * forest_penalty_score   # Penalizar bosque
        )
        
        # Bonus por tener AMBOS colores del heatmap
        if pink_coverage > 0.1 and green_coverage > 0.1:
            weight *= 1.3  # 30% bonus por diversidad de heatmap
        
        # Bonus extra por alta concentración de cualquier color del heatmap
        max_heatmap_coverage = max(pink_coverage, green_coverage)
        if max_heatmap_coverage > 0.3:
            weight *= 1.2  # 20% bonus por alta concentración
        
        # Asegurar que esté en rango [0, 1]
        weight = np.clip(weight, 0.0, 1.0)
        
        return weight

    def create_edges(self, connection_type: str = "adjacent") -> None:
        """
        Crear aristas entre nodos según el tipo de conexión especificado

        Args:
            connection_type: Tipo de conexión ("adjacent", "diagonal", "all")
        """
        rows, cols = self.grid_size

        for i in range(rows):
            for j in range(cols):
                current_node = (i, j)

                # Conexiones adyacentes (arriba, abajo, izquierda, derecha)
                if connection_type in ["adjacent", "all"]:
                    adjacent_positions = [
                        (i-1, j), (i+1, j), (i, j-1), (i, j+1)
                    ]

                    for pos in adjacent_positions:
                        if (0 <= pos[0] < rows and 0 <= pos[1] < cols):
                            # Peso de la arista basado en diferencia de pesos
                            current_weight = self.nodes[current_node][
                                'peso_normalizado']
                            pos_weight = self.nodes[pos]['peso_normalizado']
                            weight_diff = abs(current_weight - pos_weight)
                            # Mayor similitud = menor peso de arista
                            edge_weight = 1.0 - weight_diff

                            self.graph.add_edge(current_node, pos,
                                                weight=edge_weight)

                # Conexiones diagonales
                if connection_type in ["diagonal", "all"]:
                    diagonal_positions = [
                        (i-1, j-1), (i-1, j+1), (i+1, j-1), (i+1, j+1)
                    ]

                    for pos in diagonal_positions:
                        if (0 <= pos[0] < rows and 0 <= pos[1] < cols):
                            current_weight = self.nodes[current_node][
                                'peso_normalizado']
                            pos_weight = self.nodes[pos]['peso_normalizado']
                            weight_diff = abs(current_weight - pos_weight)
                            edge_weight = 1.0 - weight_diff

                            self.graph.add_edge(current_node, pos,
                                                weight=edge_weight)

        print(f"Creadas {self.graph.number_of_edges()} aristas con "
              f"conexión tipo '{connection_type}'")

    def visualize_graph_on_image(self, save_path: str = None,
                                 show_weights: bool = True) -> None:
        """
        Visualizar el grafo superpuesto sobre la imagen original

        Args:
            save_path: Ruta para guardar la imagen (opcional)
            show_weights: Si mostrar los pesos de los nodos
        """
        if self.image is None or not self.nodes:
            raise ValueError("Debe cargar una imagen y crear nodos primero")

        fig, ax = plt.subplots(1, 1, figsize=(12, 10))

        # Mostrar imagen original
        ax.imshow(self.image)
        ax.set_title("Grafo Superpuesto en Heatmap", fontsize=14,
                     fontweight='bold')

        # Dibujar grilla
        rows, cols = self.grid_size
        img_height, img_width = self.heatmap_values.shape
        cell_height = img_height / rows
        cell_width = img_width / cols

        # Líneas de la grilla
        for i in range(rows + 1):
            y = i * cell_height
            ax.axhline(y=y, color='white', linestyle='-',
                       alpha=0.3, linewidth=0.5)

        for j in range(cols + 1):
            x = j * cell_width
            ax.axvline(x=x, color='white', linestyle='-',
                       alpha=0.3, linewidth=0.5)

        # Dibujar aristas
        for edge in self.graph.edges():
            node1, node2 = edge
            pos1 = self.nodes[node1]['posicion']
            pos2 = self.nodes[node2]['posicion']

            ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]],
                    'b-', alpha=0.6, linewidth=1)

        # Dibujar nodos
        for node_pos, node_info in self.nodes.items():
            x, y = node_info['posicion']
            peso_norm = node_info['peso_normalizado']

            # Tamaño del nodo basado en el peso
            node_size = 50 + (peso_norm * 200)  # Tamaño entre 50 y 250

            # Color del nodo basado en el peso (colormap de calor)
            color = plt.cm.hot(peso_norm)

            # Dibujar nodo
            circle = plt.Circle((x, y), radius=np.sqrt(node_size)/3,
                                color=color, alpha=0.8, ec='white',
                                linewidth=2)
            ax.add_patch(circle)

            # Mostrar peso si se solicita
            if show_weights:
                ax.text(x, y, f'{peso_norm:.2f}',
                        ha='center', va='center', fontsize=8,
                        fontweight='bold', color='white')

        ax.set_xlim(0, img_width)
        ax.set_ylim(img_height, 0)  # Invertir eje Y para coincidir
        ax.axis('off')

        # Colorbar removed to keep visualization clean
        # sm = plt.cm.ScalarMappable(cmap='hot',
        #                            norm=plt.Normalize(vmin=0, vmax=1))
        # sm.set_array([])
        # cbar = plt.colorbar(sm, ax=ax, shrink=0.8)
        # cbar.set_label('Peso Normalizado', rotation=270, labelpad=15)

        plt.tight_layout()

        if save_path:
            # Construir la ruta final (ejemplo: frontend/public/graph.png)
            output_path = os.path.join("..", "frontend", "public", "graph.png")
            
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            print(f"Imagen guardada en: {output_path}")

    def get_graph_statistics(self) -> Dict:
        """
        Obtener estadísticas del grafo creado

        Returns:
            Diccionario con estadísticas del grafo
        """
        if not self.graph.nodes():
            return {}

        # Estadísticas básicas
        stats = {
            'num_nodes': self.graph.number_of_nodes(),
            'num_edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph),
            'is_connected': nx.is_connected(self.graph)
        }

        # Estadísticas de pesos
        node_weights = [data['peso_normalizado']
                        for _, data in self.graph.nodes(data=True)]
        edge_weights = [data['weight']
                        for _, _, data in self.graph.edges(data=True)]

        stats.update({
            'peso_promedio_nodos': np.mean(node_weights),
            'peso_std_nodos': np.std(node_weights),
            'peso_min_nodos': np.min(node_weights),
            'peso_max_nodos': np.max(node_weights),
            'peso_promedio_aristas': (np.mean(edge_weights)
                                      if edge_weights else 0),
        })

        return stats

    def save_graph(self, filepath: str, format: str = "gexf") -> None:
        """
        Guardar el grafo en un archivo

        Args:
            filepath: Ruta del archivo
            format: Formato del archivo ("gexf", "graphml", "pickle")
        """
        if format == "gexf":
            nx.write_gexf(self.graph, filepath)
        elif format == "graphml":
            nx.write_graphml(self.graph, filepath)
        elif format == "pickle":
            nx.write_gpickle(self.graph, filepath)
        else:
            raise ValueError("Formato no soportado. "
                             "Use 'gexf', 'graphml', o 'pickle'")

        print(f"Grafo guardado en: {filepath}")

    def get_adjacency_matrix(self) -> np.ndarray:
        """
        Obtener la matriz de adyacencia del grafo
        
        Returns:
            Matriz de adyacencia como numpy array y lista de nodos
        """
        if not self.graph.nodes():
            raise ValueError("El grafo está vacío")
        
        # Crear mapeo de nodos a índices
        nodes = sorted(self.graph.nodes())
        node_to_idx = {node: i for i, node in enumerate(nodes)}
        
        # Crear matriz de adyacencia
        n = len(nodes)
        adj_matrix = np.zeros((n, n))
        
        for edge in self.graph.edges(data=True):
            i = node_to_idx[edge[0]]
            j = node_to_idx[edge[1]]
            weight = edge[2].get('weight', 1.0)
            adj_matrix[i, j] = weight
            adj_matrix[j, i] = weight  # Grafo no dirigido
        
        return adj_matrix, nodes
    
    def get_weight_matrix(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Obtener la matriz de pesos (BENEFICIOS) de los nodos organizados en forma de grilla

        Returns:
            Tupla con (matriz_pesos, matriz_pesos_normalizados)
        """
        if not self.nodes:
            raise ValueError("No hay nodos creados")

        rows, cols = self.grid_size
        weight_matrix = np.zeros((rows, cols))
        weight_matrix_normalized = np.zeros((rows, cols))

        for (i, j), node_info in self.nodes.items():
            weight_matrix[i, j] = node_info['peso']
            weight_matrix_normalized[i, j] = node_info['peso_normalizado']

        return weight_matrix, weight_matrix_normalized

    def get_cost_matrix(self) -> np.ndarray:
        """
        Obtener la matriz de costos de los nodos organizados en forma de grilla

        Returns:
            Matriz de costos (valores entre 0 y 1)
        """
        if not self.nodes:
            raise ValueError("No hay nodos creados")

        rows, cols = self.grid_size
        cost_matrix = np.zeros((rows, cols))

        for (i, j), node_info in self.nodes.items():
            cost_matrix[i, j] = node_info['costo']

        return cost_matrix
    
    def get_node_coordinates_matrix(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Obtener matrices con las coordenadas X e Y de cada nodo
        
        Returns:
            Tupla con (matriz_x, matriz_y) de coordenadas
        """
        if not self.nodes:
            raise ValueError("No hay nodos creados")
        
        rows, cols = self.grid_size
        x_matrix = np.zeros((rows, cols))
        y_matrix = np.zeros((rows, cols))
        
        for (i, j), node_info in self.nodes.items():
            x, y = node_info['posicion']
            x_matrix[i, j] = x
            y_matrix[i, j] = y
        
        return x_matrix, y_matrix
    
    def export_matrices_to_files(self, base_filename: str) -> Dict[str, str]:
        """
        Exportar matrices organizadas: archivos principales en data/ y 
        datos detallados en data/[name]_data/

        Args:
            base_filename: Nombre base para los archivos

        Returns:
            Diccionario con las rutas de los archivos creados
        """
        import os
        
        # Asegurar que el directorio data/ existe
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        # Crear subdirectorio para datos detallados
        detailed_data_dir = f"{data_dir}/{base_filename}_data"
        if not os.path.exists(detailed_data_dir):
            os.makedirs(detailed_data_dir)
            
        files_created = {}

        # === ARCHIVOS PRINCIPALES (en data/) ===
        
        # Matriz de beneficios normalizada (CSV principal)
        weight_matrix, weight_normalized = self.get_weight_matrix()
        benefits_main_csv = f"{data_dir}/{base_filename}_benefits_normalized_matrix.csv"
        np.savetxt(benefits_main_csv, weight_normalized, delimiter=',', fmt='%.6f')
        files_created['benefits_main_csv'] = benefits_main_csv

        # Matriz de costos (CSV principal)
        cost_matrix = self.get_cost_matrix()
        costs_main_csv = f"{data_dir}/{base_filename}_costs_matrix.csv"
        np.savetxt(costs_main_csv, cost_matrix, delimiter=',', fmt='%.6f')
        files_created['costs_main_csv'] = costs_main_csv

        # === ARCHIVOS DETALLADOS (en data/[name]_data/) ===

        # Matriz de adyacencia
        adj_matrix, nodes = self.get_adjacency_matrix()
        adj_file_csv = f"{detailed_data_dir}/adjacency_matrix.csv"
        adj_file_npy = f"{detailed_data_dir}/adjacency_matrix.npy"
        np.savetxt(adj_file_csv, adj_matrix, delimiter=',', fmt='%.6f')
        np.save(adj_file_npy, adj_matrix)
        files_created['adjacency_csv'] = adj_file_csv
        files_created['adjacency_npy'] = adj_file_npy

        # Matrices completas de beneficios
        benefits_csv = f"{detailed_data_dir}/benefits_matrix.csv"
        benefits_norm_npy = f"{detailed_data_dir}/benefits_normalized_matrix.npy"
        benefits_npy = f"{detailed_data_dir}/benefits_matrix.npy"
        
        np.savetxt(benefits_csv, weight_matrix, delimiter=',', fmt='%.6f')
        np.save(benefits_norm_npy, weight_normalized)
        np.save(benefits_npy, weight_matrix)
        
        files_created['benefits_detailed_csv'] = benefits_csv
        files_created['benefits_normalized_npy'] = benefits_norm_npy
        files_created['benefits_npy'] = benefits_npy

        # Matriz completa de costos
        costs_npy = f"{detailed_data_dir}/costs_matrix.npy"
        np.save(costs_npy, cost_matrix)
        files_created['costs_npy'] = costs_npy

        # Coordenadas
        x_matrix, y_matrix = self.get_node_coordinates_matrix()
        x_file_csv = f"{detailed_data_dir}/x_coordinates.csv"
        y_file_csv = f"{detailed_data_dir}/y_coordinates.csv"
        x_file_npy = f"{detailed_data_dir}/x_coordinates.npy"
        y_file_npy = f"{detailed_data_dir}/y_coordinates.npy"

        np.savetxt(x_file_csv, x_matrix, delimiter=',', fmt='%.1f')
        np.savetxt(y_file_csv, y_matrix, delimiter=',', fmt='%.1f')
        np.save(x_file_npy, x_matrix)
        np.save(y_file_npy, y_matrix)

        files_created['x_coords_csv'] = x_file_csv
        files_created['y_coords_csv'] = y_file_csv
        files_created['x_coords_npy'] = x_file_npy
        files_created['y_coords_npy'] = y_file_npy

        # Información de nodos (mapeo)
        nodes_info_file = f"{detailed_data_dir}/nodes_mapping.txt"
        with open(nodes_info_file, 'w') as f:
            f.write("Node Index Mapping:\n")
            f.write("===================\n")
            for idx, node in enumerate(nodes):
                f.write(f"Index {idx}: Node {node} -> "
                        f"Grid position {node}\n")
        files_created['nodes_mapping'] = nodes_info_file

        return files_created
    
    def print_matrices_info(self) -> None:
        """
        Imprimir información sobre las matrices del grafo
        """
        print("\n=== INFORMACIÓN DE MATRICES ===")
        
        # Matriz de adyacencia
        adj_matrix, nodes = self.get_adjacency_matrix()
        print(f"Matriz de Adyacencia: {adj_matrix.shape}")
        print(f"Número de conexiones: {np.count_nonzero(adj_matrix) // 2}")
        density = np.count_nonzero(adj_matrix) / (adj_matrix.shape[0] ** 2)
        print(f"Densidad de conexiones: {density:.4f}")
        
        # Matriz de pesos (BENEFICIOS)
        weight_matrix, weight_normalized = self.get_weight_matrix()
        print(f"\nMatriz de BENEFICIOS: {weight_matrix.shape}")
        print(f"Beneficio mínimo: {weight_matrix.min():.4f}")
        print(f"Beneficio máximo: {weight_matrix.max():.4f}")
        print(f"Beneficio promedio: {weight_matrix.mean():.4f}")

        print(f"\nMatriz de BENEFICIOS Normalizados: {weight_normalized.shape}")
        print(f"Rango: [{weight_normalized.min():.4f}, "
              f"{weight_normalized.max():.4f}]")

        # Matriz de costos
        cost_matrix = self.get_cost_matrix()
        print(f"\nMatriz de COSTOS: {cost_matrix.shape}")
        print(f"Costo mínimo: {cost_matrix.min():.4f}")
        print(f"Costo máximo: {cost_matrix.max():.4f}")
        print(f"Costo promedio: {cost_matrix.mean():.4f}")

        # Mostrar pequeña muestra de la matriz de adyacencia
        print(f"\nMuestra de Matriz de Adyacencia (primeras 5x5):")
        print(adj_matrix[:min(5, adj_matrix.shape[0]),
                         :min(5, adj_matrix.shape[1])])

        print(f"\nMuestra de Matriz de BENEFICIOS Normalizados:")
        print(weight_normalized)

        print(f"\nMuestra de Matriz de COSTOS:")
        print(cost_matrix)


def main():
    """
    Función principal con ejemplo de uso
    """
    parser = argparse.ArgumentParser(
        description="Convertir heatmap a grafo ponderado")
    parser.add_argument("image_path", help="Ruta a la imagen PNG del heatmap")
    parser.add_argument("--nodes", type=int, default=9, 
                       help="Número total de nodos (debe ser cuadrado perfecto: 4, 9, 16, 25, 36, 49, 64, 100, etc.)")
    parser.add_argument("--connection_type",
                        choices=["adjacent", "diagonal", "all"],
                        default="adjacent",
                        help="Tipo de conexiones entre nodos")
    parser.add_argument("--output", help="Ruta para guardar la visualización")
    parser.add_argument("--save_graph",
                        help="Ruta para guardar el grafo (formato GEXF)")

    args = parser.parse_args()
    
    # Validar que el número de nodos es un cuadrado perfecto
    sqrt_nodes = int(np.sqrt(args.nodes))
    if sqrt_nodes * sqrt_nodes != args.nodes:
        print(f"Error: {args.nodes} no es un cuadrado perfecto.")
        print("Valores válidos: 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, etc.")
        return
    
    grid_size = (sqrt_nodes, sqrt_nodes)
    
    # Crear el convertidor
    converter = HeatmapToGraph(grid_size=grid_size)

    try:
        # Cargar imagen
        print(f"Cargando imagen: {args.image_path}")
        converter.load_image(args.image_path)

        # Crear nodos y aristas
        print(f"Creando {args.nodes} nodos en grilla {sqrt_nodes}x{sqrt_nodes}...")
        converter.create_grid_nodes()

        print(f"Creando aristas con conexión tipo '{args.connection_type}'...")
        converter.create_edges(connection_type=args.connection_type)

        # Mostrar estadísticas
        stats = converter.get_graph_statistics()
        print("\n=== ESTADÍSTICAS DEL GRAFO ===")
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"{key}: {value:.4f}")
            else:
                print(f"{key}: {value}")

        # Mostrar información de matrices
        converter.print_matrices_info()
        
        # Obtener matrices
        print("\n=== EXTRAYENDO MATRICES ===")
        
        # Matriz de adyacencia
        adj_matrix, nodes = converter.get_adjacency_matrix()
        print(f"Matriz de adyacencia obtenida: {adj_matrix.shape}")
        
        # Matriz de pesos (BENEFICIOS)
        weight_matrix, weight_normalized = converter.get_weight_matrix()
        print(f"Matriz de beneficios obtenida: {weight_matrix.shape}")

        # Matriz de costos
        cost_matrix = converter.get_cost_matrix()
        print(f"Matriz de costos obtenida: {cost_matrix.shape}")

        # Coordenadas
        x_coords, y_coords = converter.get_node_coordinates_matrix()
        print(f"Matrices de coordenadas obtenidas: {x_coords.shape}")
        
        # Exportar matrices a archivos
        if args.output:
            base_name = args.output
        else:
            # Generar nombre automático basado en la imagen y número de nodos
            import os
            img_name = os.path.basename(args.image_path).split('.')[0]
            base_name = f"{img_name}_{args.nodes}nodes"
            
        files_created = converter.export_matrices_to_files(base_name)
        print(f"\n=== ARCHIVOS EXPORTADOS ===")
        for file_type, filepath in files_created.items():
            if 'main' in file_type:  # Solo mostrar archivos principales
                print(f"📄 {file_type}: {filepath}")
        
        print(f"📂 Datos detallados en: data/{base_name}_data/")

        # Visualizar
        print("\nVisualizando grafo...")
        if args.output:
            output_path = f"data/{args.output}.png"
        else:
            output_path = f"data/{base_name}.png"
        converter.visualize_graph_on_image(save_path=output_path)

        # Guardar grafo si se especifica
        if args.save_graph:
            graph_path = f"data/{args.save_graph}"
            converter.save_graph(graph_path)
        
        print(f"\n=== RESUMEN ===")
        print(f"✅ Grilla: {sqrt_nodes}x{sqrt_nodes} ({args.nodes} nodos)")
        print(f"✅ Beneficios: data/{base_name}_benefits_normalized_matrix.csv")
        print(f"✅ Costos: data/{base_name}_costs_matrix.csv")
        print(f"✅ Visualización: {output_path}")
        
        print(f"\n=== ACCESO PROGRAMÁTICO ===")
        print("Para acceder a las matrices en código Python:")
        print("adj_matrix, nodes = converter.get_adjacency_matrix()")
        print("benefits_matrix, benefits_norm = converter.get_weight_matrix()")
        print("costs_matrix = converter.get_cost_matrix()")
        print("x_coords, y_coords = converter.get_node_coordinates_matrix()")
        print("graph = converter.graph  # Objeto NetworkX completo")

    except Exception as e:
        print(f"Error: {str(e)}")

# %%

if __name__ == "__main__":
    main()