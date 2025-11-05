# Developer Guide

Comprehensive guide for developing analytics applications with the HHW Brick framework.

## 📚 Application Development Guide

**Step-by-step tutorial** that teaches by building a complete application from scratch.

[**🎓 Start Learning →**](./application-development-guide/index.md)

**What You'll Build**:
- Complete analytics application
- SPARQL queries for sensor discovery
- Data analysis and statistics
- Matplotlib and Plotly visualizations

**Tutorial Steps**:

1. [Create Application Structure](./application-development-guide/step-01-structure.md) - Set up files and folders
2. [Write load_config Function](./application-development-guide/step-02-load-config.md) - Configuration loading
3. [SPARQL Query & qualify Function](./application-development-guide/step-03-sparql-qualify.md) - Sensor discovery
4. [analyze Function - Part 1](./application-development-guide/step-04-analyze-part1.md) - Data loading
5. [analyze Function - Part 2](./application-development-guide/step-05-analyze-part2.md) - Analysis logic
6. [Matplotlib Visualization](./application-development-guide/step-06-visualization-matplotlib.md) - Static plots
7. [Plotly HTML Visualization](./application-development-guide/step-07-visualization-plotly.md) - Interactive plots
8. [Testing Your Application](./application-development-guide/step-08-testing.md) - Test suite
9. [Deployment & Integration](./application-development-guide/step-09-deployment.md) - Share your app

**Time**: ~4-5 hours to complete

---

## Quick Reference

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

## Example Applications

Study working applications in `hhw_brick/applications/`:

### 📁 secondary_loop_temp_diff

Analyzes temperature differential in secondary hot water loops

**Key Features**:
- Simple SPARQL query for sensor discovery
- Basic statistical analysis
- Matplotlib and Plotly visualizations

### 📁 primary_loop_temp_diff

Analyzes temperature differential in primary loops with boilers

**Key Features**:
- Filtered SPARQL queries
- Anomaly detection logic
- Advanced data processing

---

## Development Tools

### Required Software

```bash
# Python 3.8+
python --version

# HHW Brick (install in editable mode for development)
pip install -e /path/to/HHW_brick
```

### Helpful Tools

- **Brick Studio**: Visual SPARQL query builder - https://brickstudio.io/
- **SPARQL Playground**: Test queries interactively

### Testing

```python
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
- **Brick Query Examples**: https://docs.brickschema.org/query/

### Python Libraries

- **pandas**: https://pandas.pydata.org/docs/
- **matplotlib**: https://matplotlib.org/stable/tutorials/
- **Plotly**: https://plotly.com/python/

---

## Getting Help

- **GitHub Issues**: https://github.com/CenterForTheBuiltEnvironment/HHW_brick/issues
- **Discussions**: Ask questions in GitHub Discussions

---

**Ready to start?**

👉 [Start the Application Development Guide](./application-development-guide/index.md)
