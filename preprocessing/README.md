# 🔧 **HEATMAP TO GRAPH PREPROCESSING**

## **📁 Folder Structure**

```
preprocessing/
├── image_to_graph.py          # 🎯 Main script 
├── requirements.txt           # 📦 Dependencies
├── USAGE.md                  # 📖 Usage guide
├── data/                     # 📊 Input images & outputs
│   ├── map.png              # Original heatmap images
│   ├── map2.png
│   └── [results]            # Generated matrices & visualizations
└── tests/                    # 🧪 Test & example scripts
    ├── example_usage.py      # Basic usage example
    ├── benefits_costs_example.py  # Benefits vs costs analysis
    └── test_color_diversity.py    # Color detection testing
```

## **🚀 Quick Start**

### **1. Setup Environment**
```bash
cd preprocessing/
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### **2. Run Preprocessing**
```bash
# Basic usage (3x3 grid, 9 nodes)
python image_to_graph.py data/map.png

# Custom grid size
python image_to_graph.py data/map.png --nodes 64  # 8x8 grid
```

### **3. Output Files**
- `data/map_9nodes_benefits_normalized_matrix.csv` - **Benefits matrix**
- `data/map_9nodes_costs_matrix.csv` - **Costs matrix**
- `data/map_9nodes.png` - **Visualization**
- `data/map_9nodes_data/` - **Detailed data**

## **🧪 Test Scripts**

### **Basic Example**
```bash
cd tests/
python example_usage.py
```

### **Benefits vs Costs Analysis**
```bash
cd tests/
python benefits_costs_example.py
```

### **Color Detection Testing**
```bash
cd tests/
python test_color_diversity.py
```

## **📈 Valid Node Counts**
Perfect squares only: **4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144...**

## **⚡ Key Features**
- 🎨 **Smart color detection** - Pink & green heatmap areas
- 💰 **Random cost generation** - For optimization algorithms  
- 📊 **Multiple export formats** - CSV, NPY, NetworkX graphs
- 🗂️ **Clean organization** - Main files separate from detailed data
- ⚡ **Fast default** - 3x3 grid for quick testing
