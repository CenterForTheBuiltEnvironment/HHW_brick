# Primary Loop Temperature Differential Analysis App

## Overview

This application analyzes the temperature differential between supply and return water in **primary loops** of hot water systems with boilers. It is specifically designed for boiler systems where:
- Primary loop connects boilers to heat exchangers
- Temperature differentials are typically larger than secondary loops
- Analysis helps identify boiler efficiency and loop performance

## Features

✅ **Automatic Point Detection**: Checks if Brick model contains required supply and return temperature sensors on primary loop  
✅ **Boiler System Validation**: Ensures the loop has boilers (characteristic of primary loops)  
✅ **Flexible Configuration**: Supports custom time ranges, thresholds, and output formats  
✅ **Multiple Sensor Type Support**: Automatically recognizes equivalent sensor types  
✅ **Rich Statistical Analysis**: Computes mean, standard deviation, quantiles, etc.  
✅ **Visualization Plots**: Auto-generates timeseries, distribution, and hourly statistics plots  
✅ **Anomaly Detection**: Identifies temperature differentials outside normal range  

## Key Differences from Secondary Loop App

| Feature | Primary Loop | Secondary Loop |
|---------|-------------|----------------|
| **Loop Type** | Primary loop with boilers | Secondary loop |
| **Typical ΔT** | 2-20°C (larger) | 0.5-10°C (smaller) |
| **Equipment** | Must have boilers | No boilers |
| **Use Case** | Boiler efficiency analysis | Distribution system analysis |

## Installation

```bash
pip install -r requirements.txt
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

The building must have:
- A primary loop with boilers
- Supply temperature sensor on primary loop
- Return temperature sensor on primary loop

```python
from hhw_brick.applications.primary_loop_temp_diff.app import qualify

qualified, result = qualify('path/to/brick_model.ttl')
if qualified:
    print(f"✓ Building qualified for primary loop analysis")
    print(f"  Loop: {result['loop']}")
    print(f"  Supply: {result['supply']}")
    print(f"  Return: {result['return']}")
```

### 2. Run Basic Analysis

```bash
python app.py brick_model.ttl timeseries_data.csv
```

### 3. Use Custom Configuration

```bash
python app.py brick_model.ttl timeseries_data.csv --config config.yaml
```

## Python API Usage

### Simple Usage

```python
from hhw_brick.applications.primary_loop_temp_diff.app import analyze, load_config

# Load configuration
config = load_config('config.yaml')

# Run analysis
results = analyze(
    brick_model_path='path/to/brick_model.ttl',
    timeseries_data_path='path/to/timeseries_data.csv',
    config=config
)

if results:
    print(f"✓ Analysis completed!")
    print(f"  Mean temp differential: {results['stats']['mean_temp_diff']:.2f}°C")
    print(f"  Anomaly rate: {results['stats']['anomaly_rate']:.2f}%")
```

### Custom Configuration in Code

```python
from hhw_brick.applications.primary_loop_temp_diff.app import analyze

config = {
    'time_range': {
        'start_time': '2018-01-01',
        'end_time': '2018-12-31',
    },
    'analysis': {
        'threshold_min_delta': 2.0,   # Minimum temp diff threshold (°C)
        'threshold_max_delta': 20.0,  # Maximum temp diff threshold (°C)
    },
    'output': {
        'save_results': True,
        'output_dir': './results',
        'export_format': 'csv',  # 'csv' or 'json'
        'generate_plots': True,
        'plot_format': 'png',    # 'png', 'pdf', 'svg'
    }
}

results = analyze('model.ttl', 'data.csv', config)
```

## Configuration Options

### Analysis Parameters

- `threshold_min_delta`: Minimum temperature differential (default: 2.0°C)
  - Below this value is considered anomalous
  - Primary loops typically need higher thresholds than secondary loops
  
- `threshold_max_delta`: Maximum temperature differential (default: 20.0°C)
  - Above this value is considered anomalous

### Output Settings

- `save_results`: Whether to save analysis results (default: true)
- `output_dir`: Directory for output files (default: './results')
- `export_format`: 'csv' or 'json' (default: 'csv')
- `generate_plots`: Whether to generate visualizations (default: true)
- `plot_format`: 'png', 'pdf', or 'svg' (default: 'png')

### Time Range

- `start_time`: Start date in 'YYYY-MM-DD' format (null = use all data)
- `end_time`: End date in 'YYYY-MM-DD' format (null = use all data)

## Output Files

### Statistics File
`primary_loop_temp_diff_stats.csv` or `.json`

Contains:
- Mean, median, std deviation of temperature differential
- Min/max values
- Quartiles (Q25, Q75)
- Mean supply and return temperatures
- Anomaly counts and rates

### Timeseries File
`primary_loop_temp_diff_timeseries.csv` or `.json`

Contains:
- Timestamp
- Supply temperature
- Return temperature
- Temperature differential
- Hour, weekday, month (for analysis)

### Visualization Plots

1. **primary_loop_timeseries.png**
   - Supply and return temperatures over time
   - Temperature differential over time with mean/median lines

2. **primary_loop_distribution.png**
   - Histogram of temperature differentials
   - Box plot
   - Cumulative distribution function

3. **primary_loop_time_analysis.png**
   - Temperature differential by hour of day
   - Temperature differential by day of week
   - Temperature differential by month
   - Scatter plot: supply vs return temperature

4. **primary_loop_heatmap.png**
   - Heatmap of temperature differential by hour and day of week

## Supported Sensor Types

### Supply Temperature Sensors
- `Supply_Water_Temperature_Sensor`
- `Leaving_Hot_Water_Temperature_Sensor`
- `Hot_Water_Supply_Temperature_Sensor`

### Return Temperature Sensors
- `Return_Water_Temperature_Sensor`
- `Entering_Hot_Water_Temperature_Sensor`
- `Hot_Water_Return_Temperature_Sensor`

## Example Workflow

```python
from hhw_brick.applications.primary_loop_temp_diff.app import qualify, analyze, load_config

# Step 1: Check qualification
brick_model = 'building_105_non-condensing_h.ttl'
timeseries = 'building_105_timeseries.csv'

qualified, qualify_result = qualify(brick_model)

if not qualified:
    print("✗ Building does not have required sensors on primary loop")
    exit(1)

# Step 2: Load configuration
config = load_config('config.yaml')

# Optional: customize config
config['time_range']['start_time'] = '2018-06-01'
config['time_range']['end_time'] = '2018-08-31'
config['output']['output_dir'] = './summer_analysis'

# Step 3: Run analysis
results = analyze(brick_model, timeseries, config)

# Step 4: Review results
if results:
    stats = results['stats']
    print(f"\n=== Primary Loop Analysis Results ===")
    print(f"Mean Temperature Differential: {stats['mean_temp_diff']:.2f}°C")
    print(f"Standard Deviation: {stats['std_temp_diff']:.2f}°C")
    print(f"Mean Supply Temperature: {stats['mean_supply_temp']:.2f}°C")
    print(f"Mean Return Temperature: {stats['mean_return_temp']:.2f}°C")
    print(f"Anomaly Rate: {stats['anomaly_rate']:.2f}%")
    print(f"\nResults saved to: {config['output']['output_dir']}")
```

## Interpretation Guidelines

### Normal Operation
- **ΔT Range**: 2-15°C is typical for primary loops
- **Higher ΔT**: Indicates good heat transfer from boiler to secondary loop
- **Stable ΔT**: Suggests consistent boiler operation

### Potential Issues
- **ΔT < 2°C**: Possible issues:
  - Low load on the system
  - Boiler not operating efficiently
  - Excessive flow rate
  
- **ΔT > 20°C**: Possible issues:
  - Very high load
  - Flow rate too low
  - Sensor calibration issues

- **High Variability**: May indicate:
  - Cycling boiler operation
  - Variable load patterns
  - Control system issues

## Troubleshooting

### Building Not Qualified

**Error**: "Building NOT qualified - Missing: Supply and return temperature sensors on primary loop with boiler"

**Solutions**:
1. Verify the Brick model has a primary loop defined
2. Check that the primary loop has `brick:hasPart` relationships to temperature sensors
3. Ensure the primary loop contains boilers
4. Verify sensor types match the supported list

### No Data Points Found

**Error**: "Failed to map sensors to data columns"

**Solutions**:
1. Check that sensor URIs in Brick model match column names in timeseries data
2. Verify timeseries CSV file has correct format
3. Ensure data columns exist for the identified sensors

### All Data Filtered Out

**Issue**: Analysis shows 0 valid data points

**Solutions**:
1. Check time range in configuration
2. Verify data quality (remove NaN/null values)
3. Check data types in CSV file

## License

Part of the HHW Brick package.

