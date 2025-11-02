# Getting Started

Welcome to HHW Brick Application! This guide will help you get up and running with converting heating hot water system data to Brick ontology format.

## What You'll Learn

In this section, you'll learn:

- How to [install](installation.md) the package
- How to perform your [first conversion](quick-start.md)  
- Understanding [Brick ontology](understanding-brick.md)
- [CSV data format](csv-format.md) requirements

## What is HHW Brick Application?

HHW Brick Application is a Python package that converts heating hot water system (HHWS) equipment data from CSV format into standardized Brick ontology models. It supports:

- **Multiple System Types**: Boiler, Condensing, Non-condensing, District HW, District Steam
- **Batch Processing**: Convert hundreds of buildings at once
- **Validation**: Ensure model correctness
- **Analytics**: Run analysis applications on converted models

## Prerequisites

Before you begin, you should have:

- **Python 3.8+** installed on your system
- **Basic Python knowledge** (variables, functions, modules)
- **CSV data files** with building equipment information (we provide test data to get started)

## Quick Example

Here's the simplest possible example:

```python
from hhw_brick import CSVToBrickConverter

# Create converter
converter = CSVToBrickConverter()

# Convert a building
converter.convert_to_brick(
    metadata_csv="metadata.csv",
    vars_csv="vars_available_by_building.csv",
    building_tag="105",
    output_path="building_105.ttl"
)
```

That's it! You now have a Brick ontology model in `building_105.ttl`.

## Package Components

The package consists of three main components:

### 1. Conversion Module

Convert CSV data to Brick models:

```python
from hhw_brick import CSVToBrickConverter, BatchConverter
```

- `CSVToBrickConverter` - Single building conversion
- `BatchConverter` - Multiple buildings at once

### 2. Validation Module

Validate your Brick models:

```python
from hhw_brick import BrickModelValidator, GroundTruthCalculator
```

- `BrickModelValidator` - Check ontology correctness
- `GroundTruthCalculator` - Compare against expected values

### 3. Applications Module

Run analytics on your models:

```python
from hhw_brick import apps

# List available applications
apps.list_apps()

# Load an application
app = apps.load_app("secondary_loop_temp_diff")
```

## Next Steps

Ready to get started? Choose your path:

- 📥 **[Install the Package](installation.md)** - Install HHW Brick Application on your system

- ⚡ **[Quick Start Guide](quick-start.md)** - Convert your first building in 5 minutes

- 📚 **[Understanding Brick](understanding-brick.md)** - Learn what Brick ontology is

- 📋 **[CSV Format Guide](csv-format.md)** - Prepare your data files

## Need Help?

- Check the [FAQ](../faq.md) for common questions
- See [User Guide](../user-guide/conversion/index.md) for detailed documentation

---

**Let's begin!** Head over to [Installation](installation.md) →
