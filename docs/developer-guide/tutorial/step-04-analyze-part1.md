# Application Development Tutorial - Step 4: analyze Function - Part 1 (Data Loading)

In this step, you'll implement the first part of the `analyze()` function, focusing on loading and preparing data.

## Goal of This Step

- Load Brick model and time-series data
- Map sensors to data columns
- Extract and filter relevant data

---

## Step 4.1: Add Required Imports

Add these imports to the top of your `app.py` (after existing imports):

```python
import pandas as pd
import numpy as np

# Import HHW Brick utilities
from hhw_brick.utils import (
    load_data,
    map_sensors_to_columns,
    extract_data_columns,
    filter_time_range,
)
```

---

## Step 4.2: Start the analyze() Function

Add the basic structure of the `analyze()` function:

```python
def analyze(brick_model_path, timeseries_data_path, config):
    """
    Execute analysis workflow

    Args:
        brick_model_path (str|Path): Path to Brick model file (.ttl)
        timeseries_data_path (str|Path): Path to time-series data (.csv)
        config (dict): Configuration dictionary from load_config()

    Returns:
        dict: Analysis results with 'stats' and 'data' keys, or None if analysis fails

    Example:
        >>> config = load_config()
        >>> results = analyze("model.ttl", "data.csv", config)
        >>> if results:
        ...     print(f"Mean: {results['stats']['mean']}")
        ...     print(f"Data shape: {results['data'].shape}")
    """
    # Step 1: Qualify building
    print(f"\n{'='*60}")
    print(f"STEP 1: Qualification")
    print(f"{'='*60}")

    qualified, qualify_result = qualify(brick_model_path)
    if not qualified:
        print("[FAIL] Building not qualified. Analysis aborted.\n")
        return None

    print("[OK] Building qualified. Proceeding with analysis.\n")

    # Steps 2-5 will be added below...
```

---

## Step 4.3: Load Data

Add data loading logic:

```python
    # Step 2: Load data
    print(f"{'='*60}")
    print(f"STEP 2: Load Data")
    print(f"{'='*60}\n")

    # Load both Brick model and time-series data
    g, df = load_data(brick_model_path, timeseries_data_path)

    print(f"[OK] Loaded {len(df)} data points")
    print(f"[OK] Time range: {df.index.min()} to {df.index.max()}")
    print(f"[OK] Columns: {list(df.columns)}\n")
```

**Understanding load_data()**:
- Loads Brick model as RDF graph (`g`)
- Loads CSV as pandas DataFrame (`df`)
- Automatically sets datetime index
- Returns both objects as tuple

---

## Step 4.4: Map Sensors to Columns

Time-series data has column names, but Brick models have sensor URIs. We need to map them:

```python
    # Step 3: Map sensors to data columns
    print(f"{'='*60}")
    print(f"STEP 3: Map Sensors to Data")
    print(f"{'='*60}\n")

    # Get sensor URIs from qualification result
    supply_uri = qualify_result["supply"]
    return_uri = qualify_result["return"]

    print(f"Looking for sensors:")
    print(f"  Supply: {supply_uri}")
    print(f"  Return: {return_uri}\n")

    # Map sensor URIs to column names in DataFrame
    sensor_mapping = map_sensors_to_columns(
        g,  # Brick model graph
        [supply_uri, return_uri],  # Sensors to find
        df  # DataFrame with column names
    )

    # Verify we found both sensors
    if len(sensor_mapping) != 2:
        print(f"[FAIL] Failed to map sensors to data columns")
        print(f"  Expected 2 sensors, found {len(sensor_mapping)}\n")
        return None

    print(f"[OK] Sensors mapped successfully:")
    for uri, col in sensor_mapping.items():
        print(f"  {uri.split('#')[-1]} -> {col}")
    print()
```

**Understanding map_sensors_to_columns()**:
- Uses Brick model to find `brick:hasLabel` or `brick:timeseries` properties
- Matches sensor URIs to CSV column names
- Returns dictionary: `{sensor_uri: column_name}`

---

## Step 4.5: Extract Relevant Data

Extract only the columns we need and rename them:

```python
    # Step 4: Extract and prepare data
    print(f"{'='*60}")
    print(f"STEP 4: Extract Data")
    print(f"{'='*60}\n")

    # Extract sensor data and rename columns
    df_extracted = extract_data_columns(
        df,
        sensor_mapping,
        rename_map={
            supply_uri: "supply",  # Rename to friendly name
            return_uri: "return"   # Rename to friendly name
        }
    )

    print(f"[OK] Extracted {len(df_extracted)} rows")
    print(f"[OK] Columns: {list(df_extracted.columns)}\n")
```

**Understanding extract_data_columns()**:
- Extracts specific columns from DataFrame
- Renames them to friendly names
- Returns new DataFrame with only relevant data

---

## Step 4.6: Filter Time Range (Optional)

If user specified a time range in config, filter the data:

```python
    # Step 5: Filter time range (optional)
    if config["time_range"]["start_time"] or config["time_range"]["end_time"]:
        print(f"{'='*60}")
        print(f"STEP 5: Filter Time Range")
        print(f"{'='*60}\n")

        start = config["time_range"]["start_time"]
        end = config["time_range"]["end_time"]

        print(f"Filtering to: {start} to {end}")

        df_extracted = filter_time_range(df_extracted, start, end)

        print(f"[OK] Filtered to {len(df_extracted)} rows\n")

    # Return prepared data (analysis logic will be added in next step)
    return {
        "stats": {},  # Will be filled in Step 5
        "data": df_extracted
    }
```

---

## Step 4.7: Complete analyze() So Far

Your `analyze()` function should now look like this:

```python
def analyze(brick_model_path, timeseries_data_path, config):
    """Execute analysis workflow"""

    # Step 1: Qualify
    print(f"\n{'='*60}")
    print(f"STEP 1: Qualification")
    print(f"{'='*60}")
    qualified, qualify_result = qualify(brick_model_path)
    if not qualified:
        return None
    print("[OK] Qualified\n")

    # Step 2: Load data
    print(f"{'='*60}")
    print(f"STEP 2: Load Data")
    print(f"{'='*60}\n")
    g, df = load_data(brick_model_path, timeseries_data_path)
    print(f"[OK] Loaded {len(df)} data points\n")

    # Step 3: Map sensors
    print(f"{'='*60}")
    print(f"STEP 3: Map Sensors")
    print(f"{'='*60}\n")
    supply_uri = qualify_result["supply"]
    return_uri = qualify_result["return"]
    sensor_mapping = map_sensors_to_columns(g, [supply_uri, return_uri], df)

    if len(sensor_mapping) != 2:
        print("[FAIL] Sensor mapping failed\n")
        return None
    print("[OK] Sensors mapped\n")

    # Step 4: Extract data
    print(f"{'='*60}")
    print(f"STEP 4: Extract Data")
    print(f"{'='*60}\n")
    df_extracted = extract_data_columns(
        df, sensor_mapping,
        rename_map={supply_uri: "supply", return_uri: "return"}
    )
    print(f"[OK] Data extracted\n")

    # Step 5: Filter time range (optional)
    if config["time_range"]["start_time"] or config["time_range"]["end_time"]:
        df_extracted = filter_time_range(
            df_extracted,
            config["time_range"]["start_time"],
            config["time_range"]["end_time"]
        )
        print(f"[OK] Time filtered\n")

    # Placeholder return (will be completed in Step 5)
    return {
        "stats": {},
        "data": df_extracted
    }
```

---

## Step 4.8: Test Data Loading

Create a test to verify data loading works:

**Create `test_analyze_part1.py`**:

```python
"""
Test data loading part of analyze function
"""

from pathlib import Path
import sys

app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir.parent.parent.parent))

from hhw_brick.applications.my_first_app.app import analyze, load_config

def test_data_loading():
    """Test data loading steps"""
    print("Testing data loading...\n")

    # Use test fixtures
    fixtures = Path(__file__).parent.parent.parent.parent / "tests" / "fixtures"

    # Find a qualified building
    model_file = fixtures / "Brick_Model_File" / "building_105_non-condensing_h.ttl"
    data_file = fixtures / "TimeSeriesData" / "105hhw_system_data.csv"

    if not model_file.exists() or not data_file.exists():
        print("Test files not found. Skipping test.")
        return

    # Load config
    config = load_config()

    # Run analysis (only data loading part)
    print(f"Testing with: {model_file.name}\n")
    results = analyze(str(model_file), str(data_file), config)

    if results:
        print(f"\n{'='*60}")
        print("✅ Data loading successful!")
        print(f"{'='*60}")
        print(f"Data shape: {results['data'].shape}")
        print(f"Columns: {list(results['data'].columns)}")
        print(f"First 5 rows:")
        print(results['data'].head())
    else:
        print("\n❌ Data loading failed")

if __name__ == "__main__":
    test_data_loading()
```

**Run the test**:
```bash
python test_analyze_part1.py
```

---

## Checkpoint

Before proceeding, verify:

- [x] `analyze()` function exists
- [x] Qualification step works
- [x] Data loading succeeds
- [x] Sensor mapping finds sensors
- [x] Data extraction returns DataFrame
- [x] Optional time filtering works
- [x] Test script runs successfully

---

## Next Steps

✅ Data loading complete!

👉 Continue to [Step 5: analyze Function - Part 2 (Analysis Logic)](./step-05-analyze-part2.md)

---

## Common Issues

**Issue**: `ModuleNotFoundError: No module named 'hhw_brick.utils'`  
**Solution**: Check `sys.path.insert(0, ...)` is at top of file

**Issue**: `KeyError` when accessing sensor URIs  
**Solution**: Verify `qualify()` returns correct keys in details dict

**Issue**: `sensor_mapping` is empty  
**Solution**:
- Check if CSV column names match Brick model labels
- Ensure sensors have `brick:hasLabel` or `brick:timeseries` properties

**Issue**: `df_extracted` has NaN values  
**Solution**: This is normal; we'll handle missing data in Step 5

---

## Understanding the HHW Brick Utilities

### load_data()

```python
g, df = load_data(brick_model, timeseries_csv)
```

**Returns**:
- `g`: RDF graph (rdflib.Graph) with Brick model
- `df`: pandas DataFrame with time-series data (datetime index)

### map_sensors_to_columns()

```python
mapping = map_sensors_to_columns(graph, sensor_uris, dataframe)
```

**Returns**: Dict mapping sensor URIs to column names
```python
{
    "http://example.org#sensor1": "column_name_1",
    "http://example.org#sensor2": "column_name_2"
}
```

### extract_data_columns()

```python
df_new = extract_data_columns(df, sensor_mapping, rename_map)
```

**Returns**: DataFrame with extracted and renamed columns

### filter_time_range()

```python
df_filtered = filter_time_range(df, start_time, end_time)
```

**Parameters**:
- `start_time`: String "YYYY-MM-DD" or None
- `end_time`: String "YYYY-MM-DD" or None

**Returns**: Filtered DataFrame
