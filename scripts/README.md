# Utility Scripts

This directory contains utility scripts for visualizing and analyzing Brick models.

---

## 📜 Available Scripts

### 1. `visualize_brick_models.py`

Visualize Brick TTL files as graph diagrams.

**Purpose**:
- Generate visual representations of Brick models
- Show entities (Buildings, Systems, Equipment, Points) as colored nodes
- Display relationships (brick:hasPart, brick:feeds, etc.) as labeled edges
- Support selective visualization by system type or building number

**Features**:
- Automatic color coding by entity type (Point, Equipment, System, Location)
- Type inference using Brick 1.4 ontology
- REC ontology support for Building/Space classification
- High-quality PNG output via Graphviz

**Usage**:
```bash
# Visualize representative files from each system type + special cases
python visualize_brick_models.py

# Customize in script:
# - INPUT_DIR: Directory containing TTL files
# - OUTPUT_DIR: Where to save visualizations
# - special_buildings: List of building IDs to visualize
```

**Output**:
- Directory: `Brick_Visualizations/`
- Format: PNG images
- Naming: `brick_{type}_{building}.png` or `brick_special_case_{id}.png`

**Dependencies**:
- `rdflib` - RDF graph manipulation
- `graphviz` - Graph visualization (requires Graphviz installation)
- `brickschema` - Brick ontology support

**Example Output**:
```
Brick_Visualizations/
├── brick_condensing_building_127.png
├── brick_district_hw_building_235.png
├── brick_special_case_315.png
└── ...
```

---

### 2. `draw_subgraph_patterns.py`

Generate conceptual pattern diagrams for hot water system structures.

**Purpose**:
- Document standard Brick modeling patterns
- Visualize expected subgraph structures
- Support validation and debugging

**Patterns**:
1. **Pattern 1: Boiler System** (with primary and secondary loops)
   - Has boiler equipment
   - Dual-loop configuration
   - Primary loop feeds secondary loop

2. **Pattern 2: District System** (no boiler)
   - No local boiler (uses district heating)
   - Single loop configuration
   - Simpler structure

**Features**:
- Black & white color scheme (suitable for papers/presentations)
- Curved lines for better readability
- Ellipse nodes for professional appearance
- Dashed lines for optional elements (e.g., Weather Station)
- Includes legend diagram

**Usage**:
```bash
# Generate all pattern diagrams
python draw_subgraph_patterns.py
```

**Output**:
- Directory: `Subgraph_Patterns/`
- Format: PNG images
- Files:
  - `pattern_1_boiler_system.png`
  - `pattern_2_district_system.png`
  - `pattern_legend.png`

**Dependencies**:
- `graphviz` - Graph visualization (requires Graphviz installation)

**Example Output**:
```
Subgraph_Patterns/
├── pattern_1_boiler_system.png
├── pattern_2_district_system.png
└── pattern_legend.png
```

---

## 🛠️ Installation

### Prerequisites

Both scripts require **Graphviz** to be installed on your system:

**Windows**:
```bash
# Using Chocolatey
choco install graphviz

# Or download installer from:
# https://graphviz.org/download/
```

**macOS**:
```bash
brew install graphviz
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install graphviz
```

### Python Dependencies

Install required Python packages:
```bash
pip install rdflib graphviz brickschema
```

Or install from the package requirements:
```bash
pip install -r requirements.txt
```

---

## 📊 Usage Examples

### Example 1: Visualize All System Types

```bash
# Run from project root
python scripts/visualize_brick_models.py
```

This will:
1. Scan `Brick_Models_Output/` for TTL files
2. Select one representative file per system type
3. Visualize 5 special case buildings (127, 315, 235, 125, 304)
4. Generate PNG diagrams in `Brick_Visualizations/`

### Example 2: Generate Pattern Documentation

```bash
# Run from project root
python scripts/draw_subgraph_patterns.py
```

This will:
1. Generate 3 pattern diagrams
2. Save to `Subgraph_Patterns/`
3. Display summary of generated files

### Example 3: Customize Visualization

Edit `visualize_brick_models.py` to customize:

```python
# Change input/output directories
INPUT_DIR = Path("my_models")
OUTPUT_DIR = Path("my_visualizations")

# Visualize specific buildings
special_buildings = [29, 34, 53, 55, 56, 58, 105, 110, 124, 127]

# Visualize multiple files per type
selected_files = select_representative_files(INPUT_DIR, max_per_type=2)
```

---

## 🎨 Visualization Details

### Node Colors (visualize_brick_models.py)

- **Gold**: Points (sensors, setpoints, commands)
- **Green (#32BF84)**: Equipment (boilers, pumps, valves)
- **Light Blue (#BFD7FF)**: Systems (hot water systems, loops)
- **Light Coral**: Locations (buildings, spaces)
- **Light Gray**: Other entities

### Pattern Diagram Style (draw_subgraph_patterns.py)

- **Thick border**: Required entities
- **Dashed border**: Optional entities
- **Curved lines**: All relationships
- **Ellipse nodes**: All entities
- **Black & white**: Publication-ready

---

## 🐛 Troubleshooting

### Graphviz Not Found

**Error**: `ExecutableNotFound: failed to execute ['dot', '-Tpng'], make sure the Graphviz executables are on your systems' PATH`

**Solution**:
1. Install Graphviz (see Installation section)
2. Add Graphviz to system PATH
3. Restart terminal/IDE

### RDF Parsing Warnings

**Warning**: `Failed to convert Literal lexical form to value`

**Solution**: These warnings are harmless and automatically suppressed in `visualize_brick_models.py`. They relate to HTML literals in the Brick ontology.

### Large File Performance

**Issue**: Visualization takes long time for large models

**Solution**:
- The script filters to only user-defined nodes (not entire Brick ontology)
- Reduced DPI (300) for faster rendering
- Consider visualizing smaller subsets

---

## 📝 Notes

- **Scripts are standalone utilities** - not imported by the main package
- **Visualizations help with**:
  - Model debugging
  - Documentation
  - Presentations
  - Teaching/learning Brick
- **Pattern diagrams are conceptual** - they show structure, not actual data
- **All scripts output to separate directories** - won't overwrite source data

---

## 🔗 Related

- See `examples/` for usage of the main package
- See `docs/` for full documentation
- Brick Schema: https://brickschema.org/
- REC Ontology: https://w3id.org/rec

