# Developer Guide

Comprehensive guides for developing with and extending the HHW Brick framework.

## 📚 Documentation Overview

### For Application Developers

**Create analytics applications that run on Brick-modeled buildings:**

| Guide | Description | For |
|-------|-------------|-----|
| [Creating Applications](./creating-applications.md) | Complete reference guide | All developers |
| [Application Development Guide](./application-development-guide/index.md) | Step-by-step tutorial series | Beginners |

### Quick Links

- 🚀 **New to app development?** Start with the [Application Development Guide](./application-development-guide/index.md)
- 📖 **Need a reference?** See [Creating Applications Guide](./creating-applications.md)
- 🔍 **Looking for examples?** Check `hhw_brick/applications/` directory

---

## Creating Applications Guide

**Single comprehensive reference** covering all aspects of application development.

[**📖 Read the Guide →**](./creating-applications.md)

**Contents**:
- Application structure and required files
- Core functions (`load_config`, `qualify`, `analyze`)
- SPARQL queries for Brick models
- Visualization (matplotlib and Plotly)
- Testing and deployment

**Best for**: Developers who want all information in one place

---

## Application Development Guide

**Step-by-step tutorial** that teaches by building a complete application.

[**🎓 Start Tutorial →**](./application-development-guide/index.md)

**Tutorial Steps**:

1. [Create Application Structure](./application-development-guide/step-01-structure.md) - Set up files and folders
2. [Write load_config Function](./application-development-guide/step-02-load-config.md) - Configuration loading
3. [SPARQL Query & qualify Function](./application-development-guide/step-03-sparql-qualify.md) - Sensor discovery
4. [analyze Function - Part 1](./application-development-guide/step-04-analyze-part1.md) - Data loading
5. analyze Function - Part 2 - Analysis logic *(coming soon)*
6. Matplotlib Visualization *(coming soon)*
7. Plotly HTML Visualization *(coming soon)*
8. Testing Your Application *(coming soon)*
9. Deployment & Integration *(coming soon)*

**Best for**: Beginners who prefer learning by doing

**Time**: ~3 hours to complete

---

## Learning Paths

### Path 1: Quick Start

**Goal**: Get a working app as fast as possible

1. Read [Creating Applications Guide](./creating-applications.md) - Overview section
2. Follow [Tutorial Steps 1-4](./tutorial/index.md)
3. Study example: `secondary_loop_temp_diff`

**Time**: 1.5 hours

### Path 2: Deep Understanding

**Goal**: Master application development

1. Complete full [Tutorial](./tutorial/index.md) (Steps 1-9)
2. Read [Creating Applications Guide](./creating-applications.md) for details
3. Study both example applications
4. Build your own custom application

**Time**: 5-6 hours

### Path 3: Advanced Development

**Goal**: Create complex, production-ready applications

1. Complete Path 2
2. Learn advanced SPARQL from [Brick Documentation](https://docs.brickschema.org/)
3. Explore advanced visualization techniques
4. Contribute to the HHW Brick framework

**Time**: Ongoing

---

## Example Applications

Study working applications in `hhw_brick/applications/`:

### 📁 secondary_loop_temp_diff

**What it does**: Analyzes temperature differential in secondary hot water loops

**Complexity**: ⭐⭐ Medium

**Files**:
- `app.py` - Main application logic
- `config.yaml` - Default configuration
- `README.md` - User documentation
- `requirements.txt` - Dependencies

**Learn from it**:
- Simple SPARQL query for sensor discovery
- Basic statistical analysis
- Standard visualization patterns
- Clean code structure

### 📁 primary_loop_temp_diff

**What it does**: Analyzes temperature differential in primary loops with boilers

**Complexity**: ⭐⭐ Medium

**Learn from it**:
- Filtered SPARQL queries
- Anomaly detection logic
- Multiple visualization types
- Advanced data processing

---

## Key Concepts

### Application Structure

Every application follows this structure:

```
my_app/
├── __init__.py          # Package metadata and exports
├── app.py               # Main application logic
├── config.yaml          # Default configuration
├── requirements.txt     # Dependencies
└── README.md            # Documentation
```

### Core Functions

Three required functions:

1. **`load_config()`** - Load configuration from YAML
2. **`qualify()`** - Check if building has required sensors  
3. **`analyze()`** - Execute analysis workflow

### Workflow

```
User Input → qualify() → analyze() → Results
             ↓           ↓
          SPARQL      Load Data
          Query       Compute Stats
                      Generate Viz
```

---

## Development Tools

### Required Software

```bash
# Python 3.8+
python --version

# HHW Brick (install in editable mode for development)
pip install -e /path/to/HHW_brick

# Or install dependencies individually
pip install pandas numpy matplotlib seaborn plotly rdflib brickschema pyyaml
```

### Helpful Tools

- **Brick Studio**: Visual SPARQL query builder - https://brickstudio.io/
- **RDF Visualizer**: Explore Brick models graphically
- **SPARQL Playground**: Test queries interactively

### Testing Tools

```python
# Test your application
from hhw_brick import apps

app = apps.load_app("my_app")
qualified, details = app.qualify("model.ttl")
results = app.analyze("model.ttl", "data.csv", config)
```

---

## Resources

### Brick Schema

- **Official Docs**: https://docs.brickschema.org/
- **Ontology Browser**: https://brickschema.org/ontology/
- **GitHub**: https://github.com/BrickSchema/Brick

### SPARQL

- **W3C SPARQL 1.1**: https://www.w3.org/TR/sparql11-query/
- **Tutorial**: https://www.w3.org/2009/Talks/0615-qbe/
- **Brick Query Examples**: https://docs.brickschema.org/query/

### Python Data Science

- **pandas**: https://pandas.pydata.org/docs/
- **matplotlib**: https://matplotlib.org/stable/tutorials/
- **Plotly**: https://plotly.com/python/

---

## Getting Help

### Issues & Questions

- **GitHub Issues**: https://github.com/CenterForTheBuiltEnvironment/HHW_brick/issues
- **Discussions**: Ask questions in GitHub Discussions

### Contributing

Want to contribute? See:
- Example applications for coding style
- Tutorial for best practices
- Submit pull requests with new applications

---

## Roadmap

### Coming Soon

- [ ] Additional tutorial steps (5-9)
- [ ] Video tutorials
- [ ] Interactive SPARQL builder
- [ ] Application templates
- [ ] Advanced topics guide

### Future Plans

- Community application repository
- Application marketplace
- Automated testing framework
- Performance optimization guide

---

## Quick Reference

### File Template Locations

- `__init__.py`: See [Step 1](./tutorial/step-01-structure.md#step-13-write-__init__py)
- `config.yaml`: See [Step 1](./tutorial/step-01-structure.md#step-15-create-basic-configyaml)
- `load_config()`: See [Step 2](./tutorial/step-02-load-config.md)
- `qualify()`: See [Step 3](./tutorial/step-03-sparql-qualify.md)
- `analyze()`: See [Step 4](./tutorial/step-04-analyze-part1.md)

### Common SPARQL Patterns

```sparql
# Find equipment by type
?equipment rdf:type/rdfs:subClassOf* brick:Equipment_Type .

# Find sensors of equipment
?equipment brick:hasPart ?sensor .

# Filter by sensor type
?sensor rdf:type/rdfs:subClassOf* brick:Sensor_Type .

# Filter by name
FILTER(CONTAINS(LCASE(STR(?equipment)), "keyword"))
```

### Common Code Patterns

```python
# Load config
config = load_config()

# Qualify building
qualified, details = qualify(brick_model_path)

# Load data
g, df = load_data(brick_model_path, timeseries_path)

# Map sensors
sensor_mapping = map_sensors_to_columns(g, sensor_uris, df)

# Extract data
df_clean = extract_data_columns(df, sensor_mapping, rename_map)
```

---

## Feedback

Help us improve these guides:

- Found an error? [Open an issue](https://github.com/CenterForTheBuiltEnvironment/HHW_brick/issues)
- Have a suggestion? Submit a pull request
- Need clarification? Ask in discussions

---

**Ready to start developing?**

👉 [Begin with the Tutorial](./tutorial/index.md) or [Read the Complete Guide](./creating-applications.md)
