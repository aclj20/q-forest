"""
Postprocessing module for highlighting selected nodes on Q-FOREST visualizations
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path
from typing import Tuple, Optional
import sys

# Add preprocessing to path to reuse HeatmapToGraph
sys.path.append(str(Path(__file__).parent.parent / "preprocessing"))
from image_to_graph import HeatmapToGraph


class NodeHighlighter:
    """
    Highlights selected nodes on existing Q-FOREST visualizations based on binary matrix
    """
    
    def __init__(self, image_path: str, grid_size: Tuple[int, int]):
        """
        Initialize the highlighter
        
        Args:
            image_path: Path to the original heatmap image
            grid_size: Tuple (rows, cols) for the grid
        """
        self.image_path = image_path
        self.grid_size = grid_size
        self.converter = HeatmapToGraph(grid_size=grid_size)
        self.image = None
        self.nodes = {}
        
    def load_and_process(self):
        """Load image and create node grid"""
        self.converter.load_image(self.image_path)
        self.converter.create_grid_nodes()
        self.converter.create_edges(connection_type="adjacent")
        self.nodes = self.converter.nodes
        self.image = self.converter.image
        
    def highlight_selected_nodes(
        self, 
        selection_matrix: np.ndarray,
        output_path: str,
        highlight_color: Tuple[int, int, int] = (255, 215, 0),  # Gold
        highlight_size: float = 300,
        show_original_weights: bool = False
    ) -> str:
        """
        Create visualization with highlighted nodes
        
        Args:
            selection_matrix: Binary matrix (1 = selected, 0 = not selected)
            output_path: Path to save the output image
            highlight_color: RGB color for highlighted nodes (default: gold)
            highlight_size: Size of highlighted nodes
            show_original_weights: Whether to show original weight-based coloring
            
        Returns:
            Path to saved image
        """
        if self.image is None or not self.nodes:
            raise ValueError("Must call load_and_process() first")
            
        # Validate selection matrix shape
        if selection_matrix.shape != self.grid_size:
            raise ValueError(
                f"Selection matrix shape {selection_matrix.shape} "
                f"must match grid size {self.grid_size}"
            )
        
        # Create figure
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        
        # Show original image
        ax.imshow(self.image)
        ax.set_title("Selected Nodes Highlighted", fontsize=14, fontweight='bold')
        
        # Draw grid lines and highlight selected cells
        rows, cols = self.grid_size
        img_height, img_width = self.converter.heatmap_values.shape
        cell_height = img_height / rows
        cell_width = img_width / cols
        
        # First pass: Draw yellow transparent overlay on selected cells
        from matplotlib.patches import Rectangle
        for (i, j), node_info in self.nodes.items():
            is_selected = selection_matrix[i, j] == 1
            
            if is_selected:
                # Calculate cell boundaries
                x_start = j * cell_width
                y_start = i * cell_height
                
                # Draw transparent yellow rectangle over the entire cell
                rect = Rectangle(
                    (x_start, y_start), 
                    cell_width, 
                    cell_height,
                    facecolor=(1.0, 1.0, 0.0),  # Yellow (RGB normalized)
                    alpha=0.35,  # 35% transparency
                    edgecolor='none'
                )
                ax.add_patch(rect)
        
        # Draw grid lines
        for i in range(rows + 1):
            y = i * cell_height
            ax.axhline(y=y, color='white', linestyle='-', alpha=0.5, linewidth=1)
        
        for j in range(cols + 1):
            x = j * cell_width
            ax.axvline(x=x, color='white', linestyle='-', alpha=0.5, linewidth=1)
        
        # Draw edges (connections between nodes)
        for edge in self.converter.graph.edges():
            node1, node2 = edge
            pos1 = self.nodes[node1]['posicion']
            pos2 = self.nodes[node2]['posicion']
            ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], 
                   'b-', alpha=0.4, linewidth=1)
        
        # Draw nodes
        selected_count = 0
        for (i, j), node_info in self.nodes.items():
            x, y = node_info['posicion']
            is_selected = selection_matrix[i, j] == 1
            
            if is_selected:
                selected_count += 1
                # Highlighted node (selected)
                node_size = highlight_size
                color = tuple(c / 255.0 for c in highlight_color)  # Normalize to 0-1
                edge_color = 'yellow'
                edge_width = 3
                alpha = 0.95
            else:
                # Regular node (not selected)
                if show_original_weights:
                    peso_norm = node_info['peso_normalizado']
                    node_size = 50 + (peso_norm * 150)
                    color = plt.cm.hot(peso_norm)
                else:
                    node_size = 80
                    color = (0.7, 0.7, 0.7)  # Gray
                edge_color = 'white'
                edge_width = 1.5
                alpha = 0.6
            
            # Draw node as circle
            circle = plt.Circle((x, y), radius=np.sqrt(node_size)/3,
                              color=color, alpha=alpha, 
                              ec=edge_color, linewidth=edge_width)
            ax.add_patch(circle)
            
            # Add label for selected nodes
            if is_selected:
                ax.text(x, y, '✓', ha='center', va='center', 
                       fontsize=14, fontweight='bold', color='black')
        
        ax.set_xlim(0, img_width)
        ax.set_ylim(img_height, 0)
        ax.axis('off')
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=tuple(c / 255.0 for c in highlight_color), 
                  edgecolor='yellow', label=f'Selected ({selected_count} nodes)'),
            Patch(facecolor=(0.7, 0.7, 0.7), edgecolor='white', 
                  label=f'Not Selected ({len(self.nodes) - selected_count} nodes)')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Highlighted visualization saved to: {output_path}")
        print(f"Selected nodes: {selected_count}/{len(self.nodes)}")
        
        return output_path


def highlight_from_file(
    image_path: str,
    selection_matrix_path: str,
    output_path: str,
    nodes: int = 9
) -> str:
    """
    Convenience function to highlight nodes from a CSV selection matrix
    
    Args:
        image_path: Path to original heatmap image
        selection_matrix_path: Path to CSV file with binary selection matrix
        output_path: Path to save highlighted visualization
        nodes: Number of nodes (must be perfect square)
        
    Returns:
        Path to saved image
    """
    # Validate nodes is perfect square
    sqrt_nodes = int(np.sqrt(nodes))
    if sqrt_nodes * sqrt_nodes != nodes:
        raise ValueError(f"{nodes} is not a perfect square")
    
    grid_size = (sqrt_nodes, sqrt_nodes)
    
    # Load selection matrix
    selection_matrix = np.loadtxt(selection_matrix_path, delimiter=',')
    
    # Create highlighter and process
    highlighter = NodeHighlighter(image_path, grid_size)
    highlighter.load_and_process()
    
    return highlighter.highlight_selected_nodes(selection_matrix, output_path)


def main():
    """Example usage from command line"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Highlight selected nodes on Q-FOREST visualization"
    )
    parser.add_argument("image_path", help="Path to original heatmap image")
    parser.add_argument("selection_matrix", help="Path to CSV file with binary selection matrix (1=selected, 0=not)")
    parser.add_argument("--nodes", type=int, default=9, 
                       help="Number of nodes (must be perfect square)")
    parser.add_argument("--output", help="Output path for highlighted image")
    parser.add_argument("--color", nargs=3, type=int, default=[255, 215, 0],
                       help="RGB color for highlighted nodes (default: 255 215 0 = gold)")
    parser.add_argument("--size", type=float, default=300,
                       help="Size of highlighted nodes (default: 300)")
    
    args = parser.parse_args()
    
    # Generate output path if not provided
    if args.output is None:
        base_name = Path(args.image_path).stem
        args.output = f"data/{base_name}_{args.nodes}nodes_highlighted.png"
    
    # Validate nodes
    sqrt_nodes = int(np.sqrt(args.nodes))
    if sqrt_nodes * sqrt_nodes != args.nodes:
        print(f"Error: {args.nodes} is not a perfect square.")
        print("Valid values: 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144")
        return
    
    grid_size = (sqrt_nodes, sqrt_nodes)
    
    # Load selection matrix
    try:
        selection_matrix = np.loadtxt(args.selection_matrix, delimiter=',')
        print(f"Loaded selection matrix: {selection_matrix.shape}")
    except Exception as e:
        print(f"Error loading selection matrix: {e}")
        return
    
    # Create highlighter
    highlighter = NodeHighlighter(args.image_path, grid_size)
    
    try:
        print(f"Loading image and creating grid...")
        highlighter.load_and_process()
        
        print(f"Highlighting selected nodes...")
        output_path = highlighter.highlight_selected_nodes(
            selection_matrix,
            args.output,
            highlight_color=tuple(args.color),
            highlight_size=args.size
        )
        
        print(f"\n✅ Success! Highlighted visualization saved to: {output_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()

