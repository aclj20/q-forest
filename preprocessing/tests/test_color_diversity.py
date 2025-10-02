# %%
"""
Script para probar el nuevo sistema de pesos basado en diversidad de colores
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import os

def create_test_heatmap():
    """
    Crear una imagen de prueba con diferentes niveles de diversidad de colores
    """
    # Crear imagen de 400x400 píxeles
    img = Image.new('RGB', (400, 400), (0, 0, 0))  # Fondo negro
    draw = ImageDraw.Draw(img)
    
    # Región 1: Área con muchos colores (esquina superior izquierda)
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), 
              (255, 0, 255), (0, 255, 255), (255, 128, 0), (128, 0, 255)]
    for i, color in enumerate(colors):
        x = (i % 4) * 25
        y = (i // 4) * 25
        draw.rectangle([x, y, x+25, y+25], fill=color)
    
    # Región 2: Área con pocos colores pero alta intensidad (esquina superior derecha)
    draw.rectangle([200, 0, 400, 100], fill=(255, 255, 255))  # Blanco uniforme
    
    # Región 3: Área con gradiente (esquina inferior izquierda)
    for y in range(200, 400):
        intensity = int((y - 200) / 200 * 255)
        draw.rectangle([0, y, 200, y+1], fill=(intensity, intensity//2, intensity//3))
    
    # Región 4: Área casi vacía (esquina inferior derecha)
    draw.rectangle([200, 200, 400, 400], fill=(10, 10, 10))  # Casi negro
    
    # Agregar algunas formas coloridas dispersas
    draw.ellipse([250, 50, 300, 100], fill=(255, 100, 150))
    draw.ellipse([320, 250, 370, 300], fill=(100, 255, 150))
    
    return img

def test_color_diversity_weights():
    """
    Probar el nuevo sistema de pesos
    """
    # Crear imagen de prueba
    test_img = create_test_heatmap()
    
    # Guardar en data/
    os.makedirs('data', exist_ok=True)
    test_img.save('data/test_heatmap.png')
    print("Imagen de prueba creada: data/test_heatmap.png")
    
    # Importar y usar nuestro script
    from image_to_graph import HeatmapToGraph
    
    # Crear convertidor con grilla pequeña para ver diferencias
    converter = HeatmapToGraph(grid_size=(4, 4))
    
    # Cargar imagen de prueba
    converter.load_image('data/test_heatmap.png')
    
    # Crear nodos con el nuevo algoritmo
    converter.create_grid_nodes()
    converter.create_edges(connection_type="adjacent")
    
    # Mostrar resultados
    print("\n" + "="*60)
    print("RESULTADOS DEL NUEVO ALGORITMO DE PESOS")
    print("="*60)
    
    weight_matrix, weight_norm = converter.get_weight_matrix()
    
    print("\nMatriz de Pesos Normalizados (0-1):")
    print("Región de la imagen -> Peso calculado")
    print("-" * 40)
    
    regions = [
        "Muchos colores (sup-izq)",
        "Uniforme blanco (sup-der)", 
        "Gradiente colorido (inf-izq)",
        "Casi vacío (inf-der)"
    ]
    
    for i in range(4):
        for j in range(4):
            region_idx = i * 2 + j // 2
            if region_idx < len(regions):
                region_name = regions[region_idx]
            else:
                region_name = f"Región ({i},{j})"
            
            weight = weight_norm[i, j]
            print(f"{region_name:25} -> {weight:.4f}")
    
    print(f"\nRango de pesos: [{weight_norm.min():.4f}, {weight_norm.max():.4f}]")
    print(f"Peso promedio: {weight_norm.mean():.4f}")
    
    # Exportar matrices
    files = converter.export_matrices_to_files("test_color_diversity")
    print(f"\nArchivos exportados:")
    for file_type, path in files.items():
        print(f"  {file_type}: {path}")
    
    # Crear visualización
    converter.visualize_graph_on_image(save_path="data/test_visualization.png")
    print(f"\nVisualización guardada: data/test_visualization.png")
    
    return converter, weight_norm

if __name__ == "__main__":
    print("Probando el nuevo algoritmo de pesos basado en diversidad de colores...")
    print("="*70)
    
    converter, weights = test_color_diversity_weights()
    
    print(f"\n" + "="*70)
    print("INTERPRETACIÓN DE RESULTADOS:")
    print("• Pesos MÁS ALTOS = Áreas con más diversidad de colores (mejores lugares)")
    print("• Pesos MÁS BAJOS = Áreas uniformes o vacías (peores lugares)")
    print("• El algoritmo combina:")
    print("  - Intensidad básica (20%)")
    print("  - Varianza de colores (40%)")  
    print("  - Riqueza de colores únicos (30%)")
    print("  - Contraste local (10%)")
    print("="*70)
