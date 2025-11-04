# Documentation Map

Complete overview of all HHW Brick documentation.

## 📚 Documentation Structure

```
docs/
├── 🏠 Home (index.md)
│
├── 🚀 Getting Started
│   ├── Installation
│   ├── Understanding Brick Schema
│   ├── CSV Data Format
│   └── Quick Start Tutorial
│
├── 📝 Examples (Code Walkthroughs)
│   ├── 01 - Convert CSV to Brick
│   ├── 02 - Ontology Validation
│   ├── 03 - Point Count Validation
│   ├── 04 - Equipment Count Validation
│   ├── 05 - Subgraph Pattern Matching
│   ├── 06 - Application Management
│   ├── 07 - Run Application
│   └── 08 - Batch Run Application
│
├── 📖 User Guide
│   ├── CSV to Brick Conversion
│   │   ├── Single Building Conversion
│   │   ├── Batch Conversion
│   │   ├── System Types
│   │   └── Sensor Mapping
│   ├── Model Validation
│   │   ├── Ontology Validation
│   │   ├── Ground Truth Comparison
│   │   └── Subgraph Patterns
│   ├── Analytics Applications
│   │   ├── Apps Manager
│   │   ├── Secondary Loop App
│   │   └── Running Apps
│   └── Plotly Visualization
│       └── Interactive HTML Visualizations
│
├── 👨‍💻 Developer Guide
│   ├── Overview (README.md)
│   ├── Creating Applications (Complete Reference)
│   └── Tutorial (Step-by-Step)
│       ├── Step 1: Application Structure
│       ├── Step 2: load_config Function
│       ├── Step 3: SPARQL & qualify Function
│       └── Step 4: analyze Function - Data Loading
│
├── ❓ FAQ
├── 📋 Changelog
└── 📄 License

```

---

## Quick Navigation

### For End Users

**I want to...**

- **Convert my CSV data to Brick** → [Quick Start](getting-started/quick-start.md) or [Conversion Guide](user-guide/conversion/)
- **Validate my Brick model** → [Validation Guide](user-guide/validation/)
- **Run analytics on my building** → [Applications Guide](user-guide/applications/)
- **Create interactive visualizations** → [Plotly Visualization](user-guide/plotly-visualization.md)

### For Developers

**I want to...**

- **Create a new application** → [Developer Guide](developer-guide/) → [Tutorial](developer-guide/tutorial/)
- **Understand the framework** → [Creating Applications Reference](developer-guide/creating-applications.md)
- **Learn SPARQL for Brick** → [Tutorial Step 3](developer-guide/tutorial/step-03-sparql-qualify.md)
- **Add visualization** → [Creating Applications - Visualization Section](developer-guide/creating-applications.md#visualization)

### By Skill Level

**Beginner**
1. [Understanding Brick](getting-started/understanding-brick.md)
2. [Quick Start](getting-started/quick-start.md)
3. [Examples](examples/)

**Intermediate**
1. [User Guide](user-guide/)
2. [Batch Processing](user-guide/conversion/batch-conversion.md)
3. [Validation](user-guide/validation/)

**Advanced**
1. [Developer Guide](developer-guide/)
2. [Creating Applications](developer-guide/creating-applications.md)
3. [Tutorial Series](developer-guide/tutorial/)

---

## Documentation by Topic

### 🔄 Data Conversion

| Document | Description | Audience |
|----------|-------------|----------|
| [CSV Data Format](getting-started/csv-format.md) | Required CSV structure | Users |
| [Single Building](user-guide/conversion/single-building.md) | Convert one building | Users |
| [Batch Conversion](user-guide/conversion/batch-conversion.md) | Convert multiple buildings | Users |
| [System Types](user-guide/conversion/system-types.md) | 5 HHW system types | Users |
| [Sensor Mapping](user-guide/conversion/sensor-mapping.md) | Customize sensor mapping | Advanced |

### ✅ Validation

| Document | Description | Audience |
|----------|-------------|----------|
| [Ontology Validation](user-guide/validation/ontology.md) | SHACL validation | Users |
| [Ground Truth](user-guide/validation/ground-truth.md) | Point/equipment counts | Users |
| [Subgraph Patterns](user-guide/validation/subgraph-patterns.md) | Pattern matching | Advanced |

### 📊 Analytics Applications

| Document | Description | Audience |
|----------|-------------|----------|
| [Apps Manager](user-guide/applications/apps-manager.md) | Manage applications | Users |
| [Secondary Loop](user-guide/applications/secondary-loop.md) | Temperature analysis | Users |
| [Running Apps](user-guide/applications/running-apps.md) | Execute applications | Users |
| [Plotly Visualization](user-guide/plotly-visualization.md) | Interactive HTML | Users |

### 👨‍💻 Application Development

| Document | Description | Audience |
|----------|-------------|----------|
| [Developer Guide Overview](developer-guide/README.md) | Start here | Developers |
| [Creating Applications](developer-guide/creating-applications.md) | Complete reference | Developers |
| [Tutorial Overview](developer-guide/tutorial/index.md) | Learning paths | Beginners |
| [Step 1: Structure](developer-guide/tutorial/step-01-structure.md) | File setup | Beginners |
| [Step 2: Config](developer-guide/tutorial/step-02-load-config.md) | Configuration | Beginners |
| [Step 3: SPARQL](developer-guide/tutorial/step-03-sparql-qualify.md) | Queries | Intermediate |
| [Step 4: Analysis](developer-guide/tutorial/step-04-analyze-part1.md) | Data processing | Intermediate |

---

## Learning Paths

### Path 1: Quick Start (30 minutes)

For users who want to get started immediately:

1. [Installation](getting-started/installation.md) - 5 min
2. [Quick Start](getting-started/quick-start.md) - 15 min
3. [Example 01](examples/01-convert-csv-to-brick.md) - 10 min

### Path 2: Complete User Guide (2 hours)

For users who want to master the toolkit:

1. [Understanding Brick](getting-started/understanding-brick.md) - 20 min
2. [CSV Format](getting-started/csv-format.md) - 15 min
3. [Conversion Guide](user-guide/conversion/) - 30 min
4. [Validation Guide](user-guide/validation/) - 30 min
5. [Applications Guide](user-guide/applications/) - 25 min

### Path 3: Developer Path (4-6 hours)

For developers creating applications:

1. Complete Path 2 first
2. [Developer Guide Overview](developer-guide/README.md) - 15 min
3. [Tutorial Series](developer-guide/tutorial/) - 3 hours
4. [Creating Applications Reference](developer-guide/creating-applications.md) - 1 hour
5. Build your own application - varies

---

## Documentation Coverage

### ✅ Complete Documentation

- ✅ Getting Started
- ✅ Examples (8 examples)
- ✅ User Guide (Conversion, Validation, Applications)
- ✅ Developer Guide (Reference + 4 tutorial steps)
- ✅ Plotly Visualization
- ✅ FAQ
- ✅ API Reference

### 🔄 In Progress

- Tutorial Steps 5-9 (Analysis, Visualization, Testing, Deployment)
- Video tutorials
- Advanced topics

---

## Search Tips

Use the search bar (top right) to find content quickly:

- **By task**: "convert csv", "validate model", "run application"
- **By concept**: "SPARQL", "Brick Schema", "temperature sensor"
- **By function**: "load_config", "qualify", "analyze"
- **By file**: "config.yaml", "requirements.txt", "app.py"

---

## Contributing to Documentation

Found an error or want to improve documentation?

1. Click the "Edit" icon on any page
2. Make your changes
3. Submit a pull request

Or [open an issue](https://github.com/CenterForTheBuiltEnvironment/HHW_brick/issues) with suggestions.

---

## External Resources

**Brick Schema**
- [Brick Schema Official Site](https://brickschema.org/)
- [Brick Documentation](https://docs.brickschema.org/)
- [Brick Ontology Browser](https://brickschema.org/ontology/)
- [Brick GitHub](https://github.com/BrickSchema/Brick)

**SPARQL**
- [W3C SPARQL 1.1](https://www.w3.org/TR/sparql11-query/)
- [Brick SPARQL Examples](https://docs.brickschema.org/query/)
- [Brick Studio (Visual Tool)](https://brickstudio.io/)

**Python Libraries**
- [pandas](https://pandas.pydata.org/)
- [rdflib](https://rdflib.readthedocs.io/)
- [matplotlib](https://matplotlib.org/)
- [Plotly](https://plotly.com/python/)

---

**Last Updated**: 2025-01-04

**Total Documentation**: 30+ pages
