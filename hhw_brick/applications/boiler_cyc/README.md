# Boiler Short Cycling Analysis App

## Overview

This application analyzes whether the boiler is short cycling (i.e., turning on and off repeatedly over a short period of time). Frequent cycling increases equipment wear, reduces efficiency, raises fuel consumption, and can greatly shortens the boiler's lifespan. Typically, the method identifies:
- Lower firing rate period.
- Supply water temperature fluctuation under low load conditions.

## Features

✅ **Minimum turndown ratio detection**: Estimates minimum turndown ratio if the boiler firing rate is available.
✅ **Daily operation cycle estimation**: Calculate the number of on-off cycles based on minimum turndown ratio.
✅ **Detect potential short cycling**: Identifies potential short cycling based on available measurements.
✅ **Visualization plots**: generates scatter plots for operating conditions with potential short cycling labeled, histogram summary showing daily operating cycles and firing rates.

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

## Quick start

### 1. Check if building qualifies

To run the analysis, the system needs:
- Preferred: boiler firing rate and knwon mininum turndown ratio
- Alternative: supply and return water temperature, boiler operating status, outdoor temperature
- All measurements should be in sufficiently fine resolution (at least 15-min interval)

```python
from hhw_brick.applications.boiler_cyc.app import qualify

qualified, qualify_result = qualify('path/to/brick_model.ttl')
```

### 2. Run basic analysis
```bash
python app.py brick_model.ttl timeseries_data.csv
```

### 3. Use custom configuration

```bash
python app.py brick_model.ttl timeseries_data.csv --config config.yaml
```

## Configuration options

### Analysis parameters

- `DET_THR`: (default: 3.2), (°C) min supply-return deltaT
- `CYC_THR`: (default: 3), consecutive on-off transitions to count as cycling
- `SPT_THR`: (default: 2), (°C) supply close to setpoint threshold
- `TOUT_MILD`: (default: 12), (°C) mild outdoor criterion
- `N_CYC_THR`: (default: 60), daily cycle threshold (~5/hr * 12hr)

### Output settings

- `save_results`: Whether to save analysis results (default: true)
- `output_dir`: Directory for output files (default: './results')
- `export_format`: 'csv'
- `generate_plots`: Whether to generate visualizations (default: true)
- `plot_format`: 'png', 'pdf', or 'svg' (default: 'png')

### Time range

- `start_time`: Start date in 'YYYY-MM-DD' format (null = use all data)
- `end_time`: End date in 'YYYY-MM-DD' format (null = use all data)

## Output files

### Timeseries file
- `fire_*.csv`: contains flagged potential short cycling at each timestep (if firing rates measurements available).
- `daily_fire_cycles_*.csv`: contains summary of number of cycles estimated for each day.
- `hwst.csv`: contains flagged potential short cycling at each timestep (if firing rates measurements not available, but supply and return water temperature, boiler operating status available).

### Visualization plots
- `daily_cyc_*.png`: histogram showing identified daily operation cycles over the study period. 
- `fire_rate _*.png`: histogram showning firing rate distribution and estimated minimuim turndown ratio.
- `firing_wt_results_*.png` (if firing rate available), `hwst_results.png` (firing rate not available): scatter plots showing hot water plant operating conditions (heating load and outdoor weather conditions)

## Supported sensor types

### Supply temperature sensors
- `Supply_Water_Temperature_Sensor`
- `Leaving_Hot_Water_Temperature_Sensor`
- `Hot_Water_Supply_Temperature_Sensor`

### Return temperature sensors
- `Return_Water_Temperature_Sensor`
- `Entering_Hot_Water_Temperature_Sensor`
- `Hot_Water_Return_Temperature_Sensor`

### Boiler firing rate sensors
- `Firing_Rate_Sensor`

### Boiler operating status
- `Enable_Status`

### Outdoor temperature sensors
- `Outside_Air_Temperature_Sensor`

## Key workflow

```python
from hhw_brick.applications.boiler_cyc.app import qualify, load_config, load_df, run_hwst_analysis, run_fire_analysis

args = parser.parse_args()

# Load config
config = load_config(args.config)

if args.output_dir:
    config["output"]["output_dir"] = args.output_dir

# Run analysis
print(f"\n{'='*60}")
print(f"Boiler Short Cycling Analysis")
print(f"{'='*60}")
print(f"Brick model: {args.brick_model}")
print(f"Timeseries:  {args.timeseries_data}")
print(f"{'='*60}")

print("Running HWST analysis...")

df, app = load_df(args.brick_model, args.timeseries_data, config)

if app == 0:
    return(f"[FAIL] Analysis cannot proceed due to no sensor data.")
elif app == 1:
    run_hwst_analysis(df, config, plot_options=True)
else:
    # Get all fire columns
    fire_columns = [col for col in df.columns if 'fire' in col]
    for fire_col in fire_columns:
        sub_df = df[['datetime_UTC', 'sup', 'ret', 't_out', fire_col]].copy()
        sub_df = sub_df.rename(columns={fire_col: 'value'})
        sub_df['boiler'] = fire_col
        run_fire_analysis(sub_df, config, plot_options=True)

# Process notification
print(f"\n{'='*60}")
print(f"[SUCCESS] Analysis completed successfully!")
print(f"   Results saved to: {config['output']['output_dir']}")
print(f"{'='*60}\n")
```

## Troubleshooting

### Building Not Qualified

**Error**: "Building NOT qualified - Missing: Supply and return temperature sensors or boiler operating status sensors"

### No Data Points Found

**Error**: "Failed to map sensors to data columns"

## License

Part of the HHW Brick package.
