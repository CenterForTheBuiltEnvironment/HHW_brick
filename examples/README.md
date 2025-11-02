# Examples

All examples use test data from `tests/fixtures/` to ensure they work out of the box.

## Available Examples

1. **`01_convert_csv_to_brick.py`** — Convert CSV data to Brick models (single + batch)
2. **`02_ontology_validation.py`** — Validate Brick models against Brick Schema 1.4 (SHACL)
3. **`03_point_count_validation.py`** — Verify sensor/point counts match expected values
4. **`04_equipment_count_validation.py`** — Verify equipment counts (boilers, pumps, etc.)
5. **`05_subgraph_pattern_matching.py`** — Validate system topology (boiler vs. district patterns)
6. **`06_application_management.py`** — Discover and manage portable analytics applications
7. **`07_run_application.py`** — Run an application on a single building
8. **`08_batch_run_application.py`** — Run an application across multiple buildings

## Quick Start

```bash
# Install package
pip install hhw-brick
# or development mode
pip install -e .

# Run examples from project root
cd examples
python 01_convert_csv_to_brick.py
python 02_ontology_validation.py
# ... etc
```

## Test Data

Examples use fixtures in `tests/fixtures/`:
- `metadata.csv` — Building metadata and system types
- `vars_available_by_building.csv` — Sensor availability
- `TimeSeriesData/` — Time-series sensor data
- `Brick_Model_File/` — Generated Brick models (created by Example 1)

**Test buildings**: 29, 34, 53, 55, 56, 58, 105, 110, 124, 127

**System types covered**:
- District Hot Water: 29, 34
- District Steam: 56, 58
- Condensing: 53, 55, 127
- Non-condensing: 105, 110
- Boiler (generic): 124

## Usage with Your Own Data

```python
from hhw_brick import CSVToBrickConverter

converter = CSVToBrickConverter()
graph = converter.convert_to_brick(
    metadata_csv="your_metadata.csv",
    vars_csv="your_vars.csv",
    building_tag="105",
    output_path="output.ttl"
)
```

## Troubleshooting

- **Import errors**: Ensure package is installed (`pip install -e .`)
- **File not found**: Run from project root
- **Missing dependencies**: `pip install -r requirements.txt`


