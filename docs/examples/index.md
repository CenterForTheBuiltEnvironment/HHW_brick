# Examples

Practical code examples for using HHWS Brick Application.

## Overview

This section contains working code examples demonstrating how to use the HHWS Brick Application package. All examples use test data from `tests/fixtures/` to ensure they work out of the box.

## Available Examples

### Getting Started

- **Installation and Setup** - [Quick Start Guide](../getting-started/quick-start.md)
- **First Conversion** - Convert your first building to Brick format

### Conversion Examples

- **[Single Building Conversion](../user-guide/conversion/single-building.md#examples)** - Convert one building at a time
- **[Batch Conversion](../user-guide/conversion/batch-conversion.md#examples)** - Convert multiple buildings at once
- **[Custom Sensor Mapping](../user-guide/conversion/sensor-mapping.md#examples)** - Customize sensor mappings

### Validation Examples

- **[Ontology Validation](../user-guide/validation/ontology.md#examples)** - Validate Brick schema compliance
- **[Ground Truth Validation](../user-guide/validation/ground-truth.md#examples)** - Check point and equipment counts
- **[Pattern Validation](../user-guide/validation/subgraph-patterns.md#examples)** - Verify system topology

### Application Examples

- **[Apps Manager](../user-guide/applications/apps-manager.md#examples)** - Discover and manage apps
- **[Secondary Loop Analysis](../user-guide/applications/secondary-loop.md#examples)** - Temperature difference analysis
- **[Running Apps](../user-guide/applications/running-apps.md#examples)** - Complete application workflow

## Example Code Repository

The package includes complete example scripts in the `examples/` directory:

```
examples/
├── 01_convert_csv_to_brick.py
├── 02_ontology_validation.py
├── 03_point_count_validation.py
├── 04_equipment_count_validation.py
├── 05_subgraph_pattern_matching.py
├── 06_application_management.py
├── 07_run_application.py
├── 08_batch_run_application.py
└── README.md
```

### Running Examples

All examples can be run directly from the package installation:

```bash
cd path/to/hhw-brick
python examples/01_convert_csv_to_brick.py
```

## Common Workflows

### Complete End-to-End Workflow

```python
"""
Complete workflow: Convert → Validate → Analyze
"""
from hhw_brick import (
    CSVToBrickConverter,
    BrickModelValidator,
    apps
)

# Step 1: Convert
converter = CSVToBrickConverter()
converter.convert_to_brick(
    metadata_csv="metadata.csv",
    vars_csv="vars.csv",
    building_tag="105",
    output_path="building_105.ttl"
)

# Step 2: Validate
validator = BrickModelValidator(use_local_brick=True)
is_valid = validator.validate_ontology("building_105.ttl")['valid']

if is_valid:
    # Step 3: Analyze
    app = apps.load_app("secondary_loop_temp_diff")
    qualified, details = app.qualify("building_105.ttl")
    
    if qualified:
        config = apps.get_default_config("secondary_loop_temp_diff")
        results = app.analyze(
            "building_105.ttl",
            "105_data.csv",
            config
        )
        print(f"Analysis complete: {results['summary']}")
```

## Interactive Tutorials

For step-by-step learning, see:

- [Quick Start Tutorial](../getting-started/quick-start.md)
- [Conversion Guide](../user-guide/conversion/index.md)
- [Validation Guide](../user-guide/validation/index.md)
- [Applications Guide](../user-guide/applications/index.md)

## Need Help?

- Check the [FAQ](../faq.md) for common questions
- Browse the [User Guide](../user-guide/conversion/index.md) for detailed documentation
- Visit the [GitHub repository](https://github.com/yourusername/hhw-brick) for issues and discussions

