# HHWS Brick Application - Examples

This directory contains practical examples demonstrating how to use the HHWS Brick Application package.

## 📚 Examples Overview

All examples use test data from `tests/fixtures/` to ensure they work out of the box.

### 1️⃣ Single Building Conversion
**File**: `01_single_building_conversion.py`

Convert a single building from CSV to Brick format.

```bash
python examples/01_single_building_conversion.py
```

**What it demonstrates**:
- Basic CSV to Brick conversion
- Using CSVToBrickConverter
- Working with test fixtures
- Checking conversion warnings

---

### 2️⃣ Batch Conversion
**File**: `02_batch_conversion.py`

Convert multiple buildings at once.

```bash
python examples/02_batch_conversion.py
```

**What it demonstrates**:
- Batch conversion by system type
- Converting specific buildings
- Using BatchConverter
- Progress tracking

---

### 3️⃣ Ontology Validation
**File**: `03_ontology_validation.py`

Validate Brick models for ontology correctness.

```bash
python examples/03_ontology_validation.py
```

**What it demonstrates**:
- Creating and validating Brick models
- Using BrickModelValidator
- GitHub nightly vs local Brick schema
- Interpreting validation results

---

### 4️⃣ Point Count Validation
**File**: `04_point_count_validation.py`

Validate point counts against ground truth.

```bash
python examples/04_point_count_validation.py
```

**What it demonstrates**:
- Point/equipment count validation
- Using ground truth data
- Comparing expected vs actual counts

---

### 5️⃣ Subgraph Pattern Matching
**File**: `05_subgraph_pattern_matching.py`

Validate system architecture using SPARQL-based subgraph pattern matching.

```bash
python examples/05_subgraph_pattern_matching.py
```

**What it demonstrates**:
- Pattern 1: Boiler System validation (dual loops: primary + secondary)
- Pattern 2: District System validation (single loop: secondary only)
- SPARQL queries with rdfs:subClassOf* reasoning
- Identifying specific boiler types (Condensing vs Non-condensing)
- Batch pattern validation
- System topology verification

**Key Concepts**:
- Boiler systems have primary loop (with boiler) feeding secondary loop
- District systems have only secondary loop (heated by central plant)
- Uses Brick ontology reasoning to match equipment types

---

### 6️⃣ Application Management
**File**: `06_application_management.py`

Run analytics on Brick models (example structure).

```bash
python examples/06_analytics_app.py
```

**What it demonstrates**:
- Analytics app structure
- Using Brick models with timeseries data
- Expected analytics outputs

**Note**: Analytics module is being refactored. This shows the expected structure.

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install the package in development mode
pip install -e .

# Or install required dependencies
pip install -r requirements.txt
```

### Run All Examples

```bash
# From project root
python examples/01_single_building_conversion.py
python examples/02_batch_conversion.py
python examples/03_ontology_validation.py
python examples/04_point_count_validation.py
python examples/05_complete_workflow.py
python examples/06_analytics_app.py
```

### Output

All examples create output in `example_output/` directory:
- `*.ttl` files - Brick models
- Validation results
- Analytics results (when available)

---

## 📊 Example Data

All examples use test data from `tests/fixtures/`:

```
tests/fixtures/
├── metadata.csv                    # Building metadata
├── vars_available_by_building.csv  # Available variables
└── TimeSeriesData/                 # Timeseries data (if available)
```

This data includes:
- Building 29, 34, 37, 38, 40 (District HW systems)
- Complete metadata and variable information
- Ready-to-use test data

---

## 💡 Tips

### Customize for Your Data

Replace test data paths with your own:

```python
# Instead of:
fixtures_dir = Path(__file__).parent.parent / "tests" / "fixtures"
metadata_csv = fixtures_dir / "metadata.csv"

# Use:
metadata_csv = "path/to/your/metadata.csv"
vars_csv = "path/to/your/vars.csv"
```

### Run in Your Own Scripts

```python
from hhw_brick import CSVToBrickConverter

converter = CSVToBrickConverter()
graph = converter.convert_to_brick(
    metadata_csv="your_data.csv",
    vars_csv="your_vars.csv",
    system_type="District HW",
    output_path="output.ttl"
)
```

### Error Handling

```python
try:
    result = workflow.run(...)
    if result['success']:
        print("Success!")
    else:
        print(f"Warning: {result}")
except Exception as e:
    print(f"Error: {e}")
```

---

## 🔗 Related Documentation

- **User Guide**: `../USER_GUIDE.md`
- **Testing Guide**: `../tests/README.md`
- **App Developer Guide**: `../docs/APP_DEVELOPER_GUIDE.md`
- **API Documentation**: Package docstrings

---

## 🐛 Troubleshooting

### Import Errors

```bash
# Make sure package is installed
pip install -e .

# Or add to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/HHW_brick"
```

### File Not Found

Make sure you're running from the project root:

```bash
cd /path/to/HHW_brick
python examples/01_single_building_conversion.py
```

### Missing Test Data

```bash
# Check if test fixtures exist
ls tests/fixtures/

# If missing, they should be there from the test setup
```

---

## 📝 Contributing Examples

Want to add a new example? Follow this structure:

```python
"""
Example N: Your Example Title

Brief description of what this example demonstrates.
"""

from hhw_brick import SomeClass

def main():
    """Main function."""
    print("=" * 70)
    print("Example N: Your Title")
    print("=" * 70)
    
    # Your example code here
    
if __name__ == "__main__":
    main()
```

---

## 📞 Need Help?

- Check the main README: `../README.md`
- Read the user guide: `../USER_GUIDE.md`
- See test cases: `../tests/`
- Open an issue on GitHub

---

**Happy Converting! 🎉**
"""
Example 1: CSV to Brick Conversion - Single Building

This example demonstrates how to convert a single building's CSV data to Brick format.
Uses test data from tests/fixtures/
"""

import os
from pathlib import Path
from hhw_brick import CSVToBrickConverter

def main():
    """Convert a single building to Brick format."""
    
    print("=" * 70)
    print("Example 1: CSV to Brick Conversion - Single Building")
    print("=" * 70)
    
    # Setup paths - using test fixtures
    fixtures_dir = Path(__file__).parent.parent / "tests" / "fixtures"
    metadata_csv = fixtures_dir / "metadata.csv"
    vars_csv = fixtures_dir / "vars_available_by_building.csv"
    
    # Output directory
    output_dir = Path("example_output")
    output_dir.mkdir(exist_ok=True)
    
    # Building to convert
    building_tag = "29"  # District HW system
    
    print(f"\n📂 Input files:")
    print(f"   - Metadata: {metadata_csv}")
    print(f"   - Variables: {vars_csv}")
    print(f"\n🏢 Converting building: {building_tag}")
    
    # Create converter
    converter = CSVToBrickConverter()
    
    # Convert single building
    output_file = output_dir / f"building_{building_tag}.ttl"
    
    print(f"\n🔄 Converting...")
    graph = converter.convert_to_brick(
        metadata_csv=str(metadata_csv),
        vars_csv=str(vars_csv),
        system_type="District HW",
        building_tag=building_tag,
        output_path=str(output_file)
    )
    
    print(f"\n✅ Conversion complete!")
    print(f"   - Output file: {output_file}")
    print(f"   - Triples: {len(graph)}")
    
    # Display some warnings if any
    if converter.validation_warnings:
        print(f"\n⚠️  Validation warnings: {len(converter.validation_warnings)}")
        for warning in converter.validation_warnings[:5]:  # Show first 5
            print(f"      - {warning}")
    
    print(f"\n💡 You can now:")
    print(f"   - View the TTL file: {output_file}")
    print(f"   - Load it into a Brick viewer")
    print(f"   - Query it with SPARQL")
    

if __name__ == "__main__":
    main()

