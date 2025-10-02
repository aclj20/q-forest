# 🚀 **SIMPLIFIED USAGE GUIDE**

## **Ultra-Simple Usage**

### **Basic Command (just image path)**
```bash
source .venv/bin/activate
python image_to_graph.py data/map.png
```
**Result**: 3x3 grid (9 nodes) with auto-generated name `map_9nodes`

### **Custom Node Count**
```bash
python image_to_graph.py data/map.png --nodes 64
```
**Result**: 8x8 grid (64 nodes) with name `map_64nodes`

### **Valid Node Counts (Perfect Squares Only)**
- **4** → 2x2 grid
- **9** → 3x3 grid  
- **16** → 4x4 grid
- **25** → 5x5 grid
- **36** → 6x6 grid
- **49** → 7x7 grid
- **64** → 8x8 grid
- **81** → 9x9 grid
- **100** → 10x10 grid
- **121** → 11x11 grid
- **144** → 12x12 grid

### **What You Get**
After running, you'll find in `data/`:
- `[imagename]_[nodes]nodes_benefits_normalized_matrix.csv` - **Benefits matrix**
- `[imagename]_[nodes]nodes_costs_matrix.csv` - **Costs matrix**  
- `[imagename]_[nodes]nodes.png` - **Visualization**
- `[imagename]_[nodes]nodes_data/` - **Detailed data folder**

### **Examples**
```bash
# Default: 3x3 grid (9 nodes) - FAST for testing
python image_to_graph.py data/map.png

# Small grid for testing
python image_to_graph.py data/map.png --nodes 16    # 4x4 grid

# Medium grid for analysis  
python image_to_graph.py data/map.png --nodes 64    # 8x8 grid

# Large grid for detailed work
python image_to_graph.py data/map.png --nodes 144   # 12x12 grid

# Custom output name
python image_to_graph.py data/map.png --nodes 25 --output my_analysis
```

### **Error Handling**
```bash
# This will fail (15 is not a perfect square)
python image_to_graph.py data/map.png --nodes 15
# Error: 15 no es un cuadrado perfecto.
# Valores válidos: 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, etc.
```

## **Key Features**
✅ **Only image path required** - everything else has defaults  
✅ **Perfect square validation** - prevents invalid grids  
✅ **Auto-naming** - based on image name and node count  
✅ **Clean file organization** - main files visible, details in subfolder  
✅ **Benefits & Costs** - both matrices generated automatically
