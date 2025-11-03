<div align="center">

<table border="0">
  <tr>
    <td><img src="docs/Figures/HHWS LOGO.png" alt="HHW Brick Logo" height="60"/></td>
    <td><h1>HHW Brick: Heating Hot Water System Brick Schema Toolkit</h1></td>
  </tr>
</table>

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Brick Schema](https://img.shields.io/badge/Brick-1.4-green)](https://brickschema.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://centerforthebuiltenvironment.github.io/HHW_brick/)

**A Python package for converting heating hot water system data to Brick Schema models with comprehensive validation and portable analytics.**

[📚 Documentation](https://centerforthebuiltenvironment.github.io/HHW_brick/) | [🚀 Getting Started](#installation) | [💡 Examples](examples/) | [🐛 Issues](https://github.com/CenterForTheBuiltEnvironment/HHW_brick/issues)

</div>

---

## Description

This package provides tools for converting building hot water system data to Brick Schema models and running portable analytics applications.

**Core Contributions**:
- **CSV-to-Brick Converter**: Automated conversion from tabular BMS data to Brick Schema 1.4 RDF models
- **Multi-Level Validators**: Ontology, point count, equipment count, and structural pattern validation
- **Portable Analytics**: Building-agnostic applications that use SPARQL to auto-discover required sensors

**Key Benefits**:
- **Interoperability**: Standardized semantic models work across different BMS platforms
- **Portability**: Write analytics once, run on any qualified building without recoding
- **Quality Assurance**: Comprehensive validation ensures model correctness

The package supports **five hot water system types** (condensing boilers, non-condensing boilers, generic boilers, district hot water, district steam) and has been tested on 216 real buildings.

---

## Usage

### Installation

**For Users (when published to PyPI)**:
```bash
pip install hhw-brick
```

**For Development (current method)**:
```bash
# Clone the repository
git clone https://github.com/CenterForTheBuiltEnvironment/HHW_brick.git
cd HHW_brick

# Install in editable mode
pip install -e .
```

The `-e` flag installs the package in editable mode, so changes to the source code are immediately reflected without reinstalling.

**System Requirements**:
- Python 3.8 or higher
- All dependencies are automatically installed (see `pyproject.toml`)

**Input Data**:
For sample input data format, see: https://doi.org/10.5061/dryad.t4b8gtj8n

---

### 📚 Documentation

**📖 [View Full Documentation →](https://centerforthebuiltenvironment.github.io/HHW_brick/)**

For comprehensive guides, tutorials, and API reference, please visit our documentation site:
- [Getting Started Guide](https://centerforthebuiltenvironment.github.io/HHW_brick/getting-started/quickstart/)
- [User Guide](https://centerforthebuiltenvironment.github.io/HHW_brick/user-guide/conversion/)
- [API Reference](https://centerforthebuiltenvironment.github.io/HHW_brick/api-reference/conversion/)
- [Examples & Tutorials](https://centerforthebuiltenvironment.github.io/HHW_brick/examples/)

---

### Basic Workflow

The typical workflow consists of three steps: **conversion**, **validation**, and **application**.

#### 1. Convert CSV to Brick Model

```python
from hhw_brick import CSVToBrickConverter

converter = CSVToBrickConverter()
graph = converter.convert_to_brick(
    metadata_csv="metadata.csv",
    vars_csv="vars_available_by_building.csv",
    building_tag="105",
    output_path="building_105.ttl"
)
print(f"Generated {len(graph)} RDF triples")
```

#### 2. Validate the Brick Model

```python
from hhw_brick import BrickModelValidator, GroundTruthCalculator

# Generate ground truth from input CSV (expected counts)
calculator = GroundTruthCalculator()
ground_truth = calculator.calculate(
    metadata_csv="metadata.csv",
    vars_csv="vars_available_by_building.csv",
    output_csv="ground_truth.csv"
)

# Validate generated model
validator = BrickModelValidator(ground_truth_csv_path="ground_truth.csv")

# Ontology validation
result = validator.validate_ontology("building_105.ttl")
print(f"Valid: {result['valid']}")

# Point count validation
point_result = validator.validate_point_count("building_105.ttl")

# Equipment count validation
equip_result = validator.validate_equipment_count("building_105.ttl")
```

#### 3. Run Analytics Application

```python
from hhw_brick import apps

# Discover available applications
available_apps = apps.list_apps()

# Load temperature difference analysis
app = apps.load_app("secondary_loop_temp_diff")

# Run on qualified building
results = app.run(
    brick_model="building_105.ttl",
    timeseries_data="building_105_data.csv"
)
```

### Batch Processing

Process multiple buildings in parallel:

```python
from hhw_brick import BatchConverter, BrickModelValidator

# Batch conversion
batch = BatchConverter()
results = batch.convert_all_buildings(
    metadata_csv="metadata.csv",
    vars_csv="vars_available_by_building.csv",
    output_dir="output/",
    show_progress=True  # Show progress bar
)

# Batch validation
validator = BrickModelValidator()
validation_results = validator.batch_validate_ontology(
    test_data_dir="output/",
    max_workers=4
)
```

### Examples

The `examples/` folder contains 8 complete examples:

1. **01_convert_csv_to_brick.py** - Single and batch CSV conversion
2. **02_ontology_validation.py** - SHACL-based ontology validation
3. **03_point_count_validation.py** - Sensor/point count verification
4. **04_equipment_count_validation.py** - Equipment count verification
5. **05_subgraph_pattern_matching.py** - Structural pattern validation
6. **06_application_management.py** - Discover and manage analytics apps
7. **07_run_application.py** - Run analytics on single building
8. **08_batch_run_application.py** - Batch run analytics on multiple buildings

Run any example:
```bash
python examples/01_convert_csv_to_brick.py
```

---

## Input Data Format

Two CSV files are required:

1. **metadata.csv** - Building configuration (system type, equipment counts, building ID)
2. **vars_available_by_building.csv** - Sensor availability matrix (building ID × sensor names)

See example files in `examples/fixtures/` for format details.

---

## Output Format

The converter generates **Brick Schema 1.4 models** in Turtle (.ttl) format with:
- Building and system hierarchy (`rec:Building` → `brick:Hot_Water_System` → `brick:Hot_Water_Loop`)
- Equipment instances (`brick:Boiler`, `brick:Pump`)
- Sensor points (`brick:Temperature_Sensor`, `brick:Flow_Sensor`, etc.)
- Semantic relationships (`brick:hasPart`, `brick:feeds`, `brick:isPointOf`)

**Example**:
```turtle
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix hhws: <https://hhws.example.org#> .

hhws:building105 a rec:Building ;
    rec:isLocationOf hhws:building105.hws .

hhws:building105.hws a brick:Hot_Water_System ;
    brick:hasPart hhws:building105.hws.primary_loop .
```

---

## Key Features

### 1. CSV-to-Brick Conversion
- Automatic system type detection
- Batch processing with parallel execution
- Support for 5 system types (condensing, non-condensing, generic boiler, district hot water, district steam)

### 2. Multi-Level Validation
- **Ontology**: SHACL validation against Brick Schema 1.4
- **Point Count**: Verify sensor counts (with `owl:sameAs` deduplication)
- **Equipment Count**: Validate boilers and pumps (with subclass support)
- **Structural Pattern**: SPARQL-based topology validation

### 3. Portable Analytics
Built-in applications that work across buildings:
- **secondary_loop_temp_diff**: Secondary loop temperature analysis
- **primary_loop_temp_diff**: Primary loop temperature analysis (boiler systems)

Applications use **SPARQL queries** to auto-discover sensors from Brick models, eliminating hardcoded point names.

---

## Methods

The package implements a three-stage validation approach:

1. **Syntactic Validation**: RDF syntax and Brick Schema conformance (SHACL)
2. **Semantic Validation**: Point and equipment counts against ground truth (calculated from input CSV)
3. **Structural Validation**: Subgraph pattern matching for system topology

Ground truth values (expected counts) are computed independently from the **input CSV data**, not from the generated Brick model, ensuring unbiased validation.

---

## Contact

**Author**: Mingchen Li  
**Email**: liwei74123@gmail.com  
**Repository**: https://github.com/CenterForTheBuiltEnvironment/HHW_brick  
**Issues**: https://github.com/CenterForTheBuiltEnvironment/HHW_brick/issues

---

## Version

**Version**: 0.1.0  
**Last Updated**: 2025-01-01
