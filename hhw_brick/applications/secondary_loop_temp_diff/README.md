# Secondary Loop Temperature Differential Analysis App

## Overview

This application analyzes the temperature differential between supply and return water in heating hot water secondary loops. It can:
- Automatically detect required temperature sensors in Brick models
- Load and analyze time-series data
- Generate statistical summaries and visualizations
- Identify anomalous temperature differential conditions

## Features

✅ **Automatic Point Detection**: Checks if Brick model contains required supply and return temperature sensors  
✅ **Flexible Configuration**: Supports custom time ranges, thresholds, and output formats  
✅ **Multiple Sensor Type Support**: Automatically recognizes equivalent sensor types  
✅ **Rich Statistical Analysis**: Calculates mean, standard deviation, percentiles, etc.  
✅ **Visualization Charts**: Auto-generates time series plots, distribution plots, and hourly statistics  
✅ **Anomaly Detection**: Identifies temperature differentials outside normal ranges  

## Installation

```bash
pip install hhw-brick
```

Main dependencies:
- pandas
- numpy
- matplotlib
- seaborn
- rdflib
- brickschema
- pyyaml

## Quick Start

### 1. Check if Building Qualifies

```python
from hhw_brick import apps

# Load the app
app = apps.load_app("secondary_loop_temp_diff")

# Check if building has required sensors
qualified, result = app.qualify("path/to/brick_model.ttl")

if qualified:
    print("✅ Building can run this analysis")
else:
    print("❌ Building missing required sensors")
```

### 2. Run Basic Analysis

```python
from hhw_brick import apps

# Load app
app = apps.load_app("secondary_loop_temp_diff")

# Run analysis
results = app.analyze(
    brick_model_path="path/to/brick_model.ttl",
    timeseries_data_path="path/to/timeseries_data.csv"
)

# Check results
if results['status'] == 'success':
    print("Analysis completed successfully!")
    print(f"Summary: {results['summary']}")
```

### 3. Use Custom Configuration

```python
from hhw_brick import apps

# Create custom configuration
config = {
    'time_range': {
        'start_time': '2018-01-01',
        'end_time': '2018-12-31',
    },
    'analysis': {
        'threshold_min_delta': 1.0,  # Minimum temp diff threshold (°C)
        'threshold_max_delta': 10.0,  # Maximum temp diff threshold (°C)
    },
    'output': {
        'save_results': True,
        'output_dir': './results',
        'export_format': 'csv',  # 'csv' or 'json'
        'generate_plots': True,
        'plot_format': 'png',  # 'png', 'pdf', 'svg'
    }
}

# Load app
app = apps.load_app("secondary_loop_temp_diff")

# Run with custom config
results = app.analyze(
    brick_model_path="path/to/brick_model.ttl",
    timeseries_data_path="path/to/timeseries_data.csv",
    config=config
)
```

## Input Requirements

### Brick Model (.ttl)

Must contain one of the following sensor types:

**Supply Water Temperature Sensor (any one):**
- `Supply_Water_Temperature_Sensor`
- `Leaving_Hot_Water_Temperature_Sensor`
- `Hot_Water_Supply_Temperature_Sensor`

**Return Water Temperature Sensor (any one):**
- `Return_Water_Temperature_Sensor`
- `Entering_Hot_Water_Temperature_Sensor`
- `Hot_Water_Return_Temperature_Sensor`

### Time-Series Data (.csv)

Must include the following columns:
- `datetime_UTC`: Timestamp (ISO format)
- Column names matching sensor references in Brick model

Example:
```csv
datetime_UTC,sup,ret,flow,hw
2018-01-01T08:00:00Z,58.9,57.7,17.9,91854.7
2018-01-01T09:00:00Z,59.2,57.9,17.9,100117.1
```

## Output Results

### Statistical File (CSV/JSON)

Contains the following metrics:
- `count`: Number of valid data points
- `mean_temp_diff`: Average temperature differential
- `std_temp_diff`: Standard deviation of temperature differential
- `min_temp_diff`, `max_temp_diff`: Range of temperature differential
- `median_temp_diff`: Median temperature differential
- `q25_temp_diff`, `q75_temp_diff`: 25th and 75th percentiles
- `mean_supply_temp`: Average supply temperature
- `mean_return_temp`: Average return temperature
- `anomalies_below_threshold`: Count of anomalies below threshold
- `anomalies_above_threshold`: Count of anomalies above threshold
- `anomaly_rate`: Percentage of anomalies (%)

### Time-Series File (CSV/JSON)

Contains all time points with:
- Supply temperature (`sup`)
- Return temperature (`ret`)
- Temperature differential (`temp_diff`)
- Time features (hour, day of week, month, etc.)

### Visualization Charts (PNG/PDF/SVG)

1. **Time Series Plot**: Shows supply temperature, return temperature, and differential over time
2. **Distribution Plot**: Histogram and box plot of temperature differential
3. **Hourly Statistics**: Bar chart of average differential by hour of day

## Configuration File Example (config.yaml)

```yaml
time_range:
  start_time: "2018-01-01"
  end_time: "2018-12-31"

analysis:
  resolution: "1H"
  threshold_min_delta: 1.0
  threshold_max_delta: 10.0

output:
  save_results: true
  output_dir: "./results"
  export_format: "csv"
  generate_plots: true
  plot_format: "png"
```

## API Reference

### qualify(brick_model_path: str) -> Tuple[bool, Dict]

Check if the building qualifies for this analysis.

**Parameters:**
- `brick_model_path`: Path to Brick model TTL file

**Returns:**
- Tuple of (qualified: bool, result: dict)

### analyze(brick_model_path: str, timeseries_data_path: str, config: Optional[Dict] = None) -> Dict

Run the temperature differential analysis.

**Parameters:**
- `brick_model_path`: Path to Brick model TTL file
- `timeseries_data_path`: Path to time-series CSV file
- `config`: Optional configuration dictionary

**Returns:**
- Dictionary with analysis results

### load_config(config_path: str) -> Dict

Load configuration from YAML file.

**Parameters:**
- `config_path`: Path to configuration YAML file

**Returns:**
- Configuration dictionary

## Troubleshooting

### Missing Sensors Error
If you get "Building missing required sensors", verify that your Brick model contains the appropriate temperature sensor types. Use the `qualify()` function to see which sensors are missing.

### Data Column Not Found
Ensure that the column names in your time-series CSV match the `ref:hasExternalReference` values in your Brick model.

### Empty Results
Check that your time range overlaps with available data, and that the data contains valid numeric values.

## License

MIT License - See LICENSE file for details.

## Author

Mingchen Li (liwei74123@gmail.com)
