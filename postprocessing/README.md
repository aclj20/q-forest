# Postprocessing - Node Highlighting

This module allows you to highlight specific nodes on Q-FOREST visualizations based on a binary selection matrix.

## 🎯 Purpose

After running the preprocessing to generate a node graph, you can use this module to:
- Highlight optimal nodes selected by an optimization algorithm
- Mark specific nodes for analysis
- Visualize solutions from quantum algorithms
- Show selected locations on the heatmap

## 🚀 Usage

### Command Line

```bash
cd postprocessing

# Basic usage
python highlight_nodes.py \
  ../preprocessing/data/map.png \
  example_selection.csv \
  --nodes 9 \
  --output highlighted_result.png

# Custom color (RGB)
python highlight_nodes.py \
  ../preprocessing/data/map.png \
  selection.csv \
  --nodes 9 \
  --color 255 0 0  # Red highlighted nodes

# Custom size
python highlight_nodes.py \
  ../preprocessing/data/map.png \
  selection.csv \
  --nodes 16 \
  --size 400  # Larger highlighted nodes
```

### Python API

```python
from postprocessing.highlight_nodes import NodeHighlighter
import numpy as np

# Define which nodes to highlight (1 = selected, 0 = not selected)
selection_matrix = np.array([
    [1, 0, 1],
    [0, 1, 0],
    [1, 0, 1]
])

# Create highlighter
highlighter = NodeHighlighter(
    image_path='preprocessing/data/map.png',
    grid_size=(3, 3)
)

# Load and process
highlighter.load_and_process()

# Highlight selected nodes
highlighter.highlight_selected_nodes(
    selection_matrix=selection_matrix,
    output_path='highlighted_output.png',
    highlight_color=(255, 215, 0),  # Gold
    highlight_size=300
)
```

### From File

```python
from postprocessing.highlight_nodes import highlight_from_file

# Highlight nodes from CSV selection matrix
highlight_from_file(
    image_path='preprocessing/data/map.png',
    selection_matrix_path='selection.csv',
    output_path='result.png',
    nodes=9
)
```

## 📊 Selection Matrix Format

The selection matrix is a CSV file with binary values:
- `1` = Node is selected (will be highlighted)
- `0` = Node is not selected (will appear dimmed)

**Example for 3×3 grid (9 nodes):**
```csv
1,0,1
0,1,0
1,0,1
```

This selects nodes at corners and center (5 out of 9 nodes).

**Example for 4×4 grid (16 nodes):**
```csv
1,1,0,0
1,1,0,0
0,0,1,1
0,0,1,1
```

## 🎨 Visualization Features

- **Selected Nodes**: Large, golden (or custom color), with checkmark ✓
- **Non-selected Nodes**: Smaller, gray, semi-transparent
- **Grid Lines**: White overlay showing node boundaries
- **Edges**: Blue lines connecting adjacent nodes
- **Legend**: Shows count of selected vs. non-selected nodes

## 🔧 Parameters

### `highlight_color`
RGB tuple for highlighted nodes. Examples:
- `(255, 215, 0)` - Gold (default)
- `(255, 0, 0)` - Red
- `(0, 255, 0)` - Green
- `(0, 191, 255)` - Deep Sky Blue

### `highlight_size`
Size of highlighted nodes (default: 300). Adjust for visibility.

### `show_original_weights`
If `True`, non-selected nodes show original benefit-based coloring from preprocessing.

## 📝 Valid Node Counts

Must be perfect squares:
- 4 (2×2), 9 (3×3), 16 (4×4), 25 (5×5), 36 (6×6), 49 (7×7)
- 64 (8×8), 81 (9×9), 100 (10×10), 121 (11×11), 144 (12×12)

## 🧪 Example Workflow

```bash
# Step 1: Generate node graph from heatmap
cd preprocessing
python image_to_graph.py data/map.png --nodes 9

# Step 2: Run your optimization algorithm
# (creates a selection matrix based on benefits/costs)

# Step 3: Highlight selected nodes
cd ../postprocessing
python highlight_nodes.py \
  ../preprocessing/data/map.png \
  my_selection.csv \
  --nodes 9 \
  --output final_result.png
```

## 📦 Dependencies

Same as preprocessing:
- numpy
- opencv-python
- matplotlib
- Pillow
- networkx

## 🔗 Integration with Backend

The postprocessing module is integrated into the FastAPI backend. See the API endpoint:

```bash
POST /highlight
```

Upload an image and selection matrix to get a highlighted visualization.

## 🎯 Use Cases

1. **Quantum Optimization Results**: Visualize nodes selected by quantum algorithms
2. **Conservation Planning**: Show optimal locations for resource allocation
3. **Comparison**: Highlight different solution sets side-by-side
4. **Presentation**: Create clear visualizations for stakeholders

## 📄 License

MIT License

