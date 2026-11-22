# Pump Differential Pressure Setpoint Tracking App

## Overview

Variable-speed pumps on a secondary hot water loop are usually controlled to hold the end-of-line
differential pressure (DP) at a setpoint. This application checks how well the loop holds that
setpoint over the operating range and how the setpoint itself is operated. It identifies:

- where and when the DP stays within, falls below or rises above the setpoint;
- how tracking differs between flow rates and pump operating modes;
- whether the DP setpoint is fixed, changed in steps or reset dynamically.

DP, DP setpoint and flow are loop-level points shared by all pumps on the loop, so tracking is a
property of the loop. Pump speed, where available, is used only to separate the operating modes
(pump 1 alone, pump 2 alone, both pumps).

## Features

✅ **Signed DP error**: each operating point is classified as under-pressurised, within tolerance or
over-pressurised using e = (Δp − Δp_set) / Δp_set and a two-sided tolerance band.
✅ **Flow-bin and operating-mode breakdown**: shares of the three classes for the whole record, per
flow bin and per pump operating mode.
✅ **Setpoint characterisation**: stable setpoint values, their coverage, the setpoint class
(single / multiple stable / dynamic) and, for non-stable values, the Spearman correlation with outdoor
air temperature and loop load.
✅ **Visualization plots**: signed-error grid by operating mode, per-pump dashboard, DP and setpoint
time series, setpoint correlation plots.

## Installation

```bash
pip install -r requirements.txt
```

Main dependencies: pandas, numpy, matplotlib, scipy, rdflib, pyyaml.

## Quick start

### 1. Check if the building qualifies

Required points (on the secondary hot water loop):
- Differential pressure sensor
- Differential pressure setpoint
- Loop flow sensor

Optional points:
- Pump speed commands of the pumps on the loop (operating-mode split, speed plots)
- System operating status (only operating periods are analysed when available)
- Supply and return water temperature (loop load for the setpoint correlation)
- Outdoor air temperature (setpoint correlation)

```python
from hhw_brick.applications.pump_flow_spd_vfd.app import qualify

qualified, qualify_result = qualify("path/to/brick_model.ttl")
```

### 2. Run the analysis

```bash
python app.py brick_model.ttl timeseries_data.csv
```

### 3. Use a custom configuration

```bash
python app.py brick_model.ttl timeseries_data.csv --config config.yaml --output-dir ./results
```

```python
from hhw_brick.applications.pump_flow_spd_vfd.app import analyze, load_config

config = load_config()
config["analysis"]["sept_threshold"] = 0.05
results = analyze("brick_model.ttl", "timeseries_data.csv", config)
print(results["summary"])
```

## Method

1. **Row selection.** When the operating status is available, only operating periods (status > 0)
   are kept. Rows are selected on DP, DP setpoint and flow only; missing optional values (pump speed,
   temperatures) never remove a row.
2. **Cleaning.** DP outliers are removed with an IQR rule on the values (k = `dp_outlier_iqr_k`) and
   on their second differences (k = `dp_spike_iqr_k`); only points with positive DP, DP setpoint and
   flow are kept.
3. **Tracking class.** With tolerance τ = `sept_threshold`, a point is within tolerance if
   |Δp − Δp_set| ≤ τ·Δp_set, under-pressurised if Δp < (1 − τ)·Δp_set and over-pressurised if
   Δp > (1 + τ)·Δp_set. The compliance ratio is the share of points within tolerance.
4. **Operating mode.** A pump runs when its speed command is > 0. With two speed points the modes
   are "P1 only", "P2 only", "both" and "none" (no pump speed > 0); with one speed point "single" and
   "none"; without speed points all points are analysed together ("all").
5. **Flow bins.** `flow_bins` equal-width bins between the minimum and maximum flow.
6. **Setpoint.** A setpoint value is stable if it holds at least `stable_setpoint_ratio_threshold`
   of the points. The setpoint is dynamic if the stable values cover less than
   `dynamic_setpoint_coverage_threshold` of the points, otherwise single (one stable value) or
   multiple stable (step).

## Configuration options

### Analysis parameters

- `sept_threshold` (default 0.10): two-sided tolerance as a fraction of the setpoint
- `flow_bins` (default 10): number of equal-width flow bins
- `min_bin_points` (default 30): minimum points in a bin for the bin median / IQR in the signed-error plot
- `high_speed_threshold` (default 0.95): pump speed counted as high-speed operation
- `stable_setpoint_ratio_threshold` (default 0.05): minimum share of points for a stable setpoint value
- `dynamic_setpoint_coverage_threshold` (default 0.95): stable-value coverage below which the setpoint is dynamic
- `min_correlation_points` (default 30): minimum complete pairs for a Spearman correlation
- `dp_outlier_iqr_k` (default 2.0), `dp_spike_iqr_k` (default 1.5): DP outlier removal

### Output settings

- `save_results`: whether to save the result tables (default: true)
- `output_dir`: directory for output files (default: './results')
- `export_format`: 'csv' or 'json'
- `generate_plots`: whether to generate plots (default: true)
- `plot_format`: 'png', 'pdf' or 'svg' (default: 'png')

### Time range

- `start_time`, `end_time`: 'YYYY-MM-DD' (null = use all data)

## Output files

### Tables
- `pump_dp_tracking_summary.*`: point count, under / within / over shares and median signed error for
  all points and per operating mode.
- `pump_dp_flow_bin.*`: the same per flow bin, plus, for each pump speed point, the points with that
  pump running, their compliance ratio (`{pump}_meet_setpoint`) and speed statistics.
- `pump_dp_setpoint_bin.*`: the same per DP setpoint value.
- `pump_dp_setpoint_characteristics.*`: stable setpoints, coverage, setpoint class and Spearman
  correlations.

### Plots
- `dp_signed_error_grid.*`: by operating mode (columns), (a) point count per flow bin by class,
  (b) pump speed vs flow, (c) signed DP error vs flow with the tolerance band and bin medians.
- `flow_bin.*` (with pump speed data): per-pump dashboard, using the points where each pump runs.
- `sp_setpoint_change.*`: DP and DP setpoint time series and the setpoint histogram.
- `sp_setpoint_corr.*` (when enough non-stable setpoint points exist): non-stable setpoint values vs
  outdoor air temperature and loop load.

## Supported sensor types

- DP: `Differential_Pressure_Sensor`; setpoint: `Differential_Pressure_Setpoint`; flow: `Flow_Sensor`
  (all as `brick:hasPart` of a secondary `Hot_Water_Loop`)
- Pump speed: `Speed_Command` (`brick:hasPoint` of a `Pump` that is part of the loop)
- Operating status: `Enable_Status` (part of the `Hot_Water_System`)
- Supply / return temperature: `Leaving_Hot_Water_Temperature_Sensor` /
  `Entering_Hot_Water_Temperature_Sensor` (part of the loop)
- Outdoor air temperature: `Outside_Air_Temperature_Sensor` (point of a `Weather_Station`)

## Limitations

- The configured minimum pump speed is not part of the data model; the signed-error plot marks the
  lowest observed speed (1st percentile) instead.
- Without pump curves or valve positions, the results show where and when the setpoint is not
  tracked, not why.
- Pump VFD frequency points are not used.

## Troubleshooting

**"Building NOT qualified"**: the secondary loop lacks a DP sensor, DP setpoint or flow sensor.

**"No data column found for: …"**: the timeseries file has no column for a required point
(check `ref:hasTimeseriesId` in the Brick model).

## License

Part of the HHW Brick package.
