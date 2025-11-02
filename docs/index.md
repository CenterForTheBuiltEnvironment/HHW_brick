<div align="center">

<img src="Figures/HHWS LOGO.png" alt="HHWS Brick Application Logo" width="150"/>

<h1 style="margin-top: 1rem;">HHWS Brick Application</h1>

<p style="font-size: 1.2rem; color: #3f51b5; margin: 0.5rem 0; font-weight: 600;">
Semantic Modeling & Analytics Toolkit for Hot Water Systems
</p>

<p style="font-size: 1.05rem; color: #666; margin: 1rem 0;">
Transform building hot water system data into standardized Brick models with automated conversion, validation, and portable analytics
</p>

<p>
  <a href="https://pypi.org/project/hhw-brick/"><img src="https://badge.fury.io/py/hhw-brick.svg" alt="PyPI version"></a>
  <a href="https://pypi.org/project/hhw-brick/"><img src="https://img.shields.io/pypi/pyversions/hhw-brick.svg" alt="Python"></a>
  <a href="https://github.com/yourusername/hhw-brick/blob/main/LICENSE"><img src="https://img.shields.io/github/license/yourusername/hhw-brick.svg" alt="License"></a>
</p>

<p style="margin-top: 1.5rem;">
  <a href="getting-started/quick-start.md" class="md-button md-button--primary">Get Started</a>
  <a href="getting-started/installation.md" class="md-button">Installation</a>
</p>

</div>

---

## Why HHWS Brick Application?

**A complete toolkit for hot water system analytics with portable applications and one-click deployment based on Brick ontology**

HHWS Brick Application provides a specialized portable application framework designed specifically for building heating hot water systems. Built on Brick semantic standards, it enables automated data conversion, quality validation, and seamless deployment of analytics applications across different buildings.

| Component | Description |
|-----------|-------------|
| **Brick-Based Modeling** | Standardized semantic models for 5 hot water system types (Boiler, Non-condensing, Condensing, District HW, District Steam) |
| **Portable App Framework** | Pre-built analytics applications that automatically adapt to different building configurations |
| **One-Click Deployment** | Automated conversion → validation → deployment workflow with built-in quality assurance |
| **Batch Processing** | Process hundreds of buildings in parallel with consistent quality across the portfolio |

---

## Three-Step Workflow

<div style="margin: 1.5rem 0;">

  <div style="padding: 1.2rem; background: var(--md-code-bg-color); border-left: 4px solid #3f51b5; margin-bottom: 1rem; border-radius: 4px;">
    <h3 style="margin-top: 0; color: #3f51b5;">1. Convert - CSV to Brick Models</h3>
    <p style="margin-bottom: 0;">Transform equipment metadata and sensor data into standardized Brick semantic models with automatic system type detection and flexible sensor mapping</p>
  </div>

  <div style="padding: 1.2rem; background: var(--md-code-bg-color); border-left: 4px solid #3f51b5; margin-bottom: 1rem; border-radius: 4px;">
    <h3 style="margin-top: 0; color: #3f51b5;">2. Validate - Triple Quality Assurance</h3>
    <p style="margin-bottom: 0;">Ensure model correctness through Brick Schema compliance, point/equipment count verification, and system topology pattern matching</p>
  </div>

  <div style="padding: 1.2rem; background: var(--md-code-bg-color); border-left: 4px solid #3f51b5; margin-bottom: 1rem; border-radius: 4px;">
    <h3 style="margin-top: 0; color: #3f51b5;">3. Analyze - Deploy Portable Applications</h3>
    <p style="margin-bottom: 0;">Run pre-built analytics applications (temperature difference, performance benchmarking) or deploy custom applications across buildings</p>
  </div>

</div>

---

## Quick Start Example

Get from raw data to validated models in under 5 minutes:

```python
from hhw_brick import CSVToBrickConverter
from hhw_brick.validation import (
    BrickModelValidator, 
    GroundTruthCalculator,
    SubgraphPatternValidator
)
from hhw_brick import apps

# Step 1: Convert your CSV data to Brick
converter = CSVToBrickConverter()
converter.convert_to_brick(
    metadata_csv="metadata.csv",
    vars_csv="vars_available_by_building.csv",
    building_tag="105",
    output_path="building_105.ttl"
)

# Step 2: Validate the generated model

# 2.1 Ontology validation - Brick Schema compliance
validator = BrickModelValidator(use_local_brick=True)
ontology_result = validator.validate_ontology("building_105.ttl")
print(f"Ontology valid: {ontology_result['valid']}")

# 2.2 Generate ground truth for count validation
calculator = GroundTruthCalculator()
ground_truth_df = calculator.calculate(
    metadata_csv="metadata.csv",
    vars_csv="vars_available_by_building.csv",
    output_csv="ground_truth.csv"
)

# 2.3 Validate point and equipment counts
validator_with_gt = BrickModelValidator(
    ground_truth_csv_path="ground_truth.csv",
    use_local_brick=True
)
point_result = validator_with_gt.validate_point_count("building_105.ttl", building_tag="105")
equipment_result = validator_with_gt.validate_equipment_count("building_105.ttl", building_tag="105")
print(f"Point count valid: {point_result['valid']}")
print(f"Equipment count valid: {equipment_result['valid']}")

# 2.4 Validate system topology pattern
pattern_validator = SubgraphPatternValidator()
pattern_result = pattern_validator.validate_building("building_105.ttl")
print(f"Pattern matched: {pattern_result['primary_pattern']}")

# Step 3: Run analytics on validated models
if ontology_result['valid'] and pattern_result['valid']:
    # Load and qualify application
    app = apps.load_app("secondary_loop_temp_diff")
    qualified, details = app.qualify("building_105.ttl")
    
    if qualified:
        # Run analysis
        config = apps.get_default_config("secondary_loop_temp_diff")
        results = app.analyze("building_105.ttl", "105_data.csv", config)
        
        # Results are automatically saved to output directory
        print(f"✓ Analysis complete!")
        print(f"✓ Results saved to: {config['output']['output_dir']}")
```

**That's it!** From CSV to insights in 3 simple steps.

[📖 See Full Tutorial →](getting-started/quick-start.md)

---

## Installation

```bash
pip install hhw-brick
```

**Requirements:** Python 3.8 or higher

[📘 Detailed Installation Guide →](getting-started/installation.md)

---

## Key Features

<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.2rem; margin: 1.5rem 0;">

  <div style="border-left: 4px solid #3f51b5; padding-left: 1.2rem;">
    <h4>Batch Processing at Scale</h4>
    <p>Convert 100+ buildings in minutes with parallel processing. Built-in progress tracking and error handling.</p>
  </div>

  <div style="border-left: 4px solid #5c6bc0; padding-left: 1.2rem;">
    <h4>5 Hot Water System Types</h4>
    <p>Comprehensive support for Boiler, Non-condensing, Condensing, District HW, and District Steam heating systems.</p>
  </div>

  <div style="border-left: 4px solid #3f51b5; padding-left: 1.2rem;">
    <h4>Triple Validation</h4>
    <p>Ontology schema + ground truth comparison + topology pattern matching ensure model quality.</p>
  </div>

  <div style="border-left: 4px solid #5c6bc0; padding-left: 1.2rem;">
    <h4>Portable Applications</h4>
    <p>Pre-built analytics apps with a framework for creating custom applications that work across buildings.</p>
  </div>

  <div style="border-left: 4px solid #3f51b5; padding-left: 1.2rem;">
    <h4>Flexible Sensor Mapping</h4>
    <p>YAML-based configuration with intelligent matching. Customize mappings to fit your data structure.</p>
  </div>

  <div style="border-left: 4px solid #5c6bc0; padding-left: 1.2rem;">
    <h4>Comprehensive Reporting</h4>
    <p>Detailed validation reports with accuracy statistics, violation details, and actionable recommendations.</p>
  </div>

</div>

---


## Documentation

<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; margin: 1.5rem 0;">

  <div style="padding: 1.2rem; background: var(--md-default-bg-color); border: 2px solid var(--md-default-fg-color--lightest); border-radius: 8px;">
    <h3 style="margin-top: 0;">🚀 Getting Started</h3>
    <p>Installation, 5-minute quick start, understanding Brick ontology, and CSV data format requirements.</p>
    <a href="getting-started/index.md" style="color: #3f51b5; font-weight: bold;">Read Guide →</a>
  </div>

  <div style="padding: 1.2rem; background: var(--md-default-bg-color); border: 2px solid var(--md-default-fg-color--lightest); border-radius: 8px;">
    <h3 style="margin-top: 0;">🔄 Conversion Guide</h3>
    <p>Single building conversion, batch processing, system type configuration, and sensor mapping customization.</p>
    <a href="user-guide/conversion/index.md" style="color: #3f51b5; font-weight: bold;">Read Guide →</a>
  </div>

  <div style="padding: 1.2rem; background: var(--md-default-bg-color); border: 2px solid var(--md-default-fg-color--lightest); border-radius: 8px;">
    <h3 style="margin-top: 0;">✅ Validation Guide</h3>
    <p>Ontology validation, ground truth comparison, topology pattern matching, and batch validation workflows.</p>
    <a href="user-guide/validation/index.md" style="color: #3f51b5; font-weight: bold;">Read Guide →</a>
  </div>

  <div style="padding: 1.2rem; background: var(--md-default-bg-color); border: 2px solid var(--md-default-fg-color--lightest); border-radius: 8px;">
    <h3 style="margin-top: 0;">📊 Applications Guide</h3>
    <p>Apps manager, temperature difference analysis, running applications, and custom app development.</p>
    <a href="user-guide/applications/index.md" style="color: #3f51b5; font-weight: bold;">Read Guide →</a>
  </div>

</div>


---

## Resources

<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin: 1.5rem 0; text-align: center;">

  <div style="padding: 1.2rem; background: var(--md-default-fg-color--lightest); border-radius: 8px;">
    <div style="font-size: 2.5rem; margin-bottom: 0.8rem;">📖</div>
    <h4 style="margin-top: 0;">Documentation</h4>
    <p style="margin-top: 0.8rem; font-size: 0.95rem;">
      <a href="getting-started/index.md">Getting Started</a><br/>
      <a href="user-guide/conversion/index.md">User Guide</a><br/>
      <a href="faq.md">FAQ</a>
    </p>
  </div>

  <div style="padding: 1.2rem; background: var(--md-default-fg-color--lightest); border-radius: 8px;">
    <div style="font-size: 2.5rem; margin-bottom: 0.8rem;">📦</div>
    <h4 style="margin-top: 0;">Package Info</h4>
    <p style="margin-top: 0.8rem; font-size: 0.95rem;">
      <a href="https://pypi.org/project/hhw-brick/">PyPI Package</a><br/>
      <a href="changelog.md">Changelog</a><br/>
      <a href="license.md">MIT License</a>
    </p>
  </div>

  <div style="padding: 1.2rem; background: var(--md-default-fg-color--lightest); border-radius: 8px;">
    <div style="font-size: 2.5rem; margin-bottom: 0.8rem;">🔧</div>
    <h4 style="margin-top: 0;">Source Code</h4>
    <p style="margin-top: 0.8rem; font-size: 0.95rem;">
      <a href="https://github.com/yourusername/hhw-brick">GitHub Repository</a><br/>
      <a href="examples/index.md">View Examples</a><br/>
      <a href="https://github.com/yourusername/hhw-brick/issues">Report Issues</a>
    </p>
  </div>

</div>

---

<div align="center" style="padding: 0.8rem 2rem; background: linear-gradient(135deg, #3f51b5 0%, #5c6bc0 100%); border-radius: 8px; color: white; margin: 1.5rem 0;">

<h2 style="color: white; margin-top: 0; margin-bottom: 0.5rem;">Ready to Get Started?</h2>

<p style="font-size: 1.05rem; margin: 0.3rem 0 0.8rem 0; color: white;">
Transform your hot water system data into standardized Brick models
</p>

<p style="margin: 0;">
  <a href="getting-started/quick-start.md" style="display: inline-block; background: white; color: #3f51b5; padding: 0.6rem 2.5rem; font-size: 1.05rem; font-weight: bold; text-decoration: none; border-radius: 6px;">
    Get Started Now →
  </a>
</p>

</div>

---

<div align="center" style="color: #666; font-size: 0.9rem; padding: 1.5rem 0;">

<p style="margin: 0.3rem 0;"><strong>Developed by Mingchen Li</strong></p>

<p style="margin: 0.3rem 0; font-style: italic;">Making building hot water system data standardized and analyzable</p>

</div>

