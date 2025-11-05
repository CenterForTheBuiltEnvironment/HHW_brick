<div align="center">

<img src="Figures/HHWS LOGO.png" alt="HHW Brick Logo" width="100"/>

<h1 style="margin-top: 1rem; margin-bottom: 1rem;">HHW Brick: Heating Hot Water System Brick Schema Toolkit</h1>

<p style="font-size: 1.05rem; color: var(--md-default-fg-color--light); margin: 1rem 0 1.5rem 0;">
A Python package for converting heating hot water system data to Brick Schema models with comprehensive validation and portable analytics
</p>

<p>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.8%2B-blue" alt="Python 3.8+"></a>
  <a href="https://brickschema.org/"><img src="https://img.shields.io/badge/Brick-1.4-green" alt="Brick Schema 1.4"></a>
  <a href="https://github.com/CenterForTheBuiltEnvironment/HHW_brick/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"></a>
</p>

<p style="margin-top: 1.5rem;">
  <a href="getting-started/quick-start/" class="md-button md-button--primary">Get Started</a>
  <a href="getting-started/installation/" class="md-button">Installation</a>
</p>

</div>

---

## Overview

HHW Brick provides tools for converting building **heating hot water system** data to Brick Schema models and running portable analytics applications.

**Core Capabilities**:

- **CSV-to-Brick Converter**: Automated conversion from tabular BMS data to Brick Schema 1.4 RDF models
- **Multi-Level Validators**: Ontology, point count, equipment count, and structural pattern validation  
- **Portable Analytics**: Building-agnostic applications that use SPARQL to auto-discover required sensors

**Key Benefits**:

- **Interoperability**: Standardized semantic models work across different BMS platforms
- **Portability**: Write analytics once, run on any qualified building without recoding
- **Quality Assurance**: Comprehensive validation ensures model correctness

The package supports **five heating hot water system types** (condensing boilers, non-condensing boilers, generic boilers, district hot water, district steam) and has been tested on 216 real buildings.

---

## Installation

```bash
# For users (when published to PyPI)
pip install hhw-brick

# For development (current method)
git clone https://github.com/CenterForTheBuiltEnvironment/HHW_brick.git
cd HHW_brick
pip install -e .
```

**Requirements:** Python 3.8 or higher

[📘 Detailed Installation Guide →](getting-started/installation/)

---

## Quick Start Example

Convert, validate, and analyze a building in under 5 minutes:

**Sample Data**: For input data format examples, see [https://doi.org/10.5061/dryad.t4b8gtj8n](https://doi.org/10.5061/dryad.t4b8gtj8n) or use test data in `tests/fixtures/`

### Step 1: Convert CSV to Brick Model

Transform your CSV data into a standardized Brick Schema RDF model with automatic system type detection and sensor mapping.

```python
from pathlib import Path
from hhw_brick import CSVToBrickConverter

# Setup paths
fixtures = Path("tests/fixtures")
metadata_csv = fixtures / "metadata.csv"
vars_csv = fixtures / "vars_available_by_building.csv"

# Convert CSV to Brick model
converter = CSVToBrickConverter()
graph = converter.convert_to_brick(
    metadata_csv=str(metadata_csv),
    vars_csv=str(vars_csv),
    building_tag="105",
    output_path="building_105.ttl"
)
print(f"✓ Converted: {len(graph)} RDF triples")
```

### Step 2: Validate the Model

Ensure your Brick model is correct through multi-level validation: ontology compliance (SHACL), point counts, and equipment counts.

```python
from hhw_brick import BrickModelValidator
from hhw_brick.validation import GroundTruthCalculator

# 2a. Ontology validation (Brick Schema compliance)
validator = BrickModelValidator(use_local_brick=True)
result = validator.validate_ontology("building_105.ttl")
print(f"✓ Ontology valid: {result['valid']}")

# 2b. Generate ground truth from CSV
calculator = GroundTruthCalculator()
calculator.calculate(
    metadata_csv=str(metadata_csv),
    vars_csv=str(vars_csv),
    output_csv="ground_truth.csv"
)

# 2c. Validate point counts
validator = BrickModelValidator(ground_truth_csv_path="ground_truth.csv")
point_result = validator.validate_point_count("building_105.ttl")
print(f"✓ Point count match: {point_result['match']}")

# 2d. Validate equipment counts
equip_result = validator.validate_equipment_count("building_105.ttl")
print(f"✓ Equipment match: {equip_result.get('overall_success', False)}")
```

### Step 3: Run Analytics Application

Deploy portable analytics that automatically discover required sensors using SPARQL queries. Save configuration templates for easy customization.

```python
from hhw_brick import apps
import yaml

# Load application
app = apps.load_app("secondary_loop_temp_diff")

# Check if building qualifies
qualified = app.qualify("building_105.ttl")
if qualified:
    # Get and save default config template
    config = apps.get_default_config("secondary_loop_temp_diff")

    # Save config template for easy editing
    with open("app_config.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    print("✓ Config template saved: app_config.yaml")

    # Customize config (or edit the YAML file directly)
    config["output"]["output_dir"] = "results/"
    config["output"]["generate_plots"] = True

    # Run analysis
    results = app.analyze(
        "building_105.ttl",
        "tests/fixtures/TimeSeriesData/105hhw_system_data.csv",
        config
    )
    print(f"✓ Analysis complete! Results in: results/")
```

**That's it!** From CSV to insights in 3 simple steps.

[📖 Full Tutorial →](getting-started/quick-start/)

---


## Key Features

<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.2rem; margin: 1.5rem 0;">

  <div style="border-left: 4px solid #3f51b5; padding-left: 1.2rem;">
    <h4>🔄 Automated Conversion</h4>
    <p>Convert CSV data to Brick Schema 1.4 models with automatic system type detection and sensor mapping.</p>
  </div>

  <div style="border-left: 4px solid #5c6bc0; padding-left: 1.2rem;">
    <h4>🏭 5 System Types</h4>
    <p>Support for condensing boilers, non-condensing boilers, generic boilers, district hot water, and district steam.</p>
  </div>

  <div style="border-left: 4px solid #3f51b5; padding-left: 1.2rem;">
    <h4>✅ Multi-Level Validation</h4>
    <p>Ontology (SHACL) + point counts + equipment counts + structural patterns ensure model quality.</p>
  </div>

  <div style="border-left: 4px solid #5c6bc0; padding-left: 1.2rem;">
    <h4>📊 Portable Analytics</h4>
    <p>Applications use SPARQL to auto-discover sensors, working across any qualified building.</p>
  </div>

  <div style="border-left: 4px solid #3f51b5; padding-left: 1.2rem;">
    <h4>⚡ Batch Processing</h4>
    <p>Convert and validate 100+ buildings in parallel with progress tracking and error handling.</p>
  </div>

  <div style="border-left: 4px solid #5c6bc0; padding-left: 1.2rem;">
    <h4>🎯 Ground Truth Validation</h4>
    <p>Independent validation using expected counts calculated directly from source CSV data.</p>
  </div>

</div>

---


## Documentation

<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin: 1.5rem 0;">

  <div style="padding: 1.2rem; background: var(--md-default-bg-color); border: 2px solid var(--md-default-fg-color--lightest); border-radius: 8px;">
    <h3 style="margin-top: 0;">🚀 Getting Started</h3>
    <p>Installation guide, 5-minute quick start tutorial, understanding Brick Schema, and CSV data format requirements.</p>
    <a href="getting-started/" style="color: #3f51b5; font-weight: bold;">Read Guide →</a>
  </div>

  <div style="padding: 1.2rem; background: var(--md-default-bg-color); border: 2px solid var(--md-default-fg-color--lightest); border-radius: 8px;">
    <h3 style="margin-top: 0;">🔄 Conversion Guide</h3>
    <p>Single building conversion, batch processing, system type configuration, and sensor mapping customization.</p>
    <a href="user-guide/conversion/" style="color: #3f51b5; font-weight: bold;">Read Guide →</a>
  </div>

  <div style="padding: 1.2rem; background: var(--md-default-bg-color); border: 2px solid var(--md-default-fg-color--lightest); border-radius: 8px;">
    <h3 style="margin-top: 0;">✅ Validation Guide</h3>
    <p>Ontology validation, ground truth comparison, structural pattern matching, and batch validation workflows.</p>
    <a href="user-guide/validation/" style="color: #3f51b5; font-weight: bold;">Read Guide →</a>
  </div>

  <div style="padding: 1.2rem; background: var(--md-default-bg-color); border: 2px solid var(--md-default-fg-color--lightest); border-radius: 8px;">
    <h3 style="margin-top: 0;">📱 Available Apps</h3>
    <p>Browse ready-to-use analytics applications: temperature differential analysis, efficiency monitoring, and more.</p>
    <a href="apps/" style="color: #3f51b5; font-weight: bold;">View Apps →</a>
  </div>

  <div style="padding: 1.2rem; background: var(--md-default-bg-color); border: 2px solid var(--md-default-fg-color--lightest); border-radius: 8px;">
    <h3 style="margin-top: 0;">📊 User Guide</h3>
    <p>Application management, running apps, and detailed usage instructions for all features.</p>
    <a href="user-guide/applications/" style="color: #3f51b5; font-weight: bold;">Read Guide →</a>
  </div>

  <div style="padding: 1.2rem; background: var(--md-default-bg-color); border: 2px solid var(--md-default-fg-color--lightest); border-radius: 8px;">
    <h3 style="margin-top: 0;">👨‍💻 Developer Guide</h3>
    <p>Create your own applications: step-by-step tutorials, SPARQL queries, visualization, and best practices.</p>
    <a href="app-development/" style="color: #3f51b5; font-weight: bold;">Read Guide →</a>
  </div>

</div>


---

## Resources

<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin: 1.5rem 0; text-align: center;">

  <div style="padding: 1.2rem; background: var(--md-default-fg-color--lightest); border-radius: 8px;">
    <div style="font-size: 2.5rem; margin-bottom: 0.8rem;">📖</div>
    <h4 style="margin-top: 0;">Documentation</h4>
    <p style="margin-top: 0.8rem; font-size: 0.95rem;">
      <a href="getting-started/">Getting Started</a><br/>
      <a href="user-guide/conversion/">User Guide</a><br/>
      <a href="apps/">Available Apps</a><br/>
      <a href="app-development/">Developer Guide</a><br/>
      <a href="faq/">FAQ</a>
    </p>
  </div>

  <div style="padding: 1.2rem; background: var(--md-default-fg-color--lightest); border-radius: 8px;">
    <div style="font-size: 2.5rem; margin-bottom: 0.8rem;">📦</div>
    <h4 style="margin-top: 0;">Package Info</h4>
    <p style="margin-top: 0.8rem; font-size: 0.95rem;">
      <a href="https://pypi.org/project/hhw-brick/" target="_blank">PyPI Package</a><br/>
      <a href="changelog/">Changelog</a><br/>
      <a href="license/">MIT License</a>
    </p>
  </div>

  <div style="padding: 1.2rem; background: var(--md-default-fg-color--lightest); border-radius: 8px;">
    <div style="font-size: 2.5rem; margin-bottom: 0.8rem;">🔧</div>
    <h4 style="margin-top: 0;">Source Code</h4>
    <p style="margin-top: 0.8rem; font-size: 0.95rem;">
      <a href="https://github.com/CenterForTheBuiltEnvironment/HHW_brick" target="_blank">GitHub Repository</a><br/>
      <a href="examples/">View Examples</a><br/>
      <a href="https://github.com/CenterForTheBuiltEnvironment/HHW_brick/issues" target="_blank">Report Issues</a>
    </p>
  </div>

</div>

---

<div align="center" style="padding: 0.8rem 2rem; background: linear-gradient(135deg, #3f51b5 0%, #5c6bc0 100%); border-radius: 8px; color: white; margin: 1.5rem 0;">

<h2 style="color: white; margin-top: 0; margin-bottom: 0.5rem;">Ready to Get Started?</h2>

<p style="font-size: 1.05rem; margin: 0.3rem 0 0.8rem 0; color: white;">
Transform your heating hot water system data into standardized Brick models
</p>

<p style="margin: 0;">
  <a href="getting-started/quick-start/" style="display: inline-block; background: white; color: #3f51b5; padding: 0.6rem 2.5rem; font-size: 1.05rem; font-weight: bold; text-decoration: none; border-radius: 6px;">
    Get Started Now →
  </a>
</p>

</div>

---

<div align="center" style="color: var(--md-default-fg-color--light); font-size: 0.9rem; padding: 1.5rem 0;">

<p style="margin: 0.3rem 0;"><strong>Developed by Mingchen Li</strong></p>

<p style="margin: 0.3rem 0; font-style: italic;">Making building heating hot water system data standardized and analyzable</p>

</div>
