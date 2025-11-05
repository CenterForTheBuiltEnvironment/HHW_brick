# Step 5: analyze Function - Part 2 (Analysis Logic)

Implement statistical analysis and anomaly detection.

---

## 1. Calculate Temperature Differential

Continue the `analyze()` function from Step 4:

```python
    # Step 6: Analyze
    print(f"{'='*60}")
    print("ANALYZE")
    print(f"{'='*60}\n")

    # Calculate temperature differential
    df_extracted["temp_diff"] = df_extracted["supply"] - df_extracted["return"]
    df_clean = df_extracted.dropna().copy()

    if len(df_clean) == 0:
        print("✗ No valid data after removing NaN\n")
        return None

    print(f"✓ Valid data points: {len(df_clean)}")
```

**Why dropna()**: Removes rows with missing values

---

## 2. Compute Statistics

```python
    # Get thresholds from config
    threshold_min = config["analysis"]["threshold_min_delta"]
    threshold_max = config["analysis"]["threshold_max_delta"]

    # Calculate statistics
    stats = {
        "count": len(df_clean),
        "mean_temp_diff": df_clean["temp_diff"].mean(),
        "std_temp_diff": df_clean["temp_diff"].std(),
        "min_temp_diff": df_clean["temp_diff"].min(),
        "max_temp_diff": df_clean["temp_diff"].max(),
        "median_temp_diff": df_clean["temp_diff"].median(),
        "q25_temp_diff": df_clean["temp_diff"].quantile(0.25),
        "q75_temp_diff": df_clean["temp_diff"].quantile(0.75),
        "mean_supply_temp": df_clean["supply"].mean(),
        "mean_return_temp": df_clean["return"].mean(),
    }
```

**Statistics explained**:
- `mean()` - Average
- `std()` - Standard deviation (spread)
- `quantile(0.25)` - 25th percentile (Q1)
- `median()` - 50th percentile

---

## 3. Detect Anomalies

```python
    # Anomaly detection
    anomalies_low = df_clean[df_clean["temp_diff"] < threshold_min]
    anomalies_high = df_clean[df_clean["temp_diff"] > threshold_max]

    stats["anomalies_below_threshold"] = len(anomalies_low)
    stats["anomalies_above_threshold"] = len(anomalies_high)
    stats["anomaly_rate"] = (
        (stats["anomalies_below_threshold"] + stats["anomalies_above_threshold"])
        / stats["count"] * 100
    )

    # Print summary
    print(f"\nStatistics:")
    print(f"  Mean: {stats['mean_temp_diff']:.2f}°C")
    print(f"  Std:  {stats['std_temp_diff']:.2f}°C")
    print(f"  Range: [{stats['min_temp_diff']:.2f}, {stats['max_temp_diff']:.2f}]°C")
    print(f"  Anomalies: {stats['anomaly_rate']:.2f}%")
```

---

## 4. Add Time Features

```python
    # Add time features for visualization
    df_clean.loc[:, "hour"] = df_clean.index.hour
    df_clean.loc[:, "weekday"] = df_clean.index.dayofweek
    df_clean.loc[:, "month"] = df_clean.index.month
```

**Time features**:
- `hour` - 0-23
- `weekday` - 0=Monday, 6=Sunday
- `month` - 1-12

---

## 5. Save Results

```python
def save_results(results, config):
    """Save statistics and time-series to CSV/JSON"""
    output_dir = Path(config["output"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    fmt = config["output"]["export_format"]

    print(f"\n{'='*60}")
    print(f"SAVE: {output_dir}")
    print(f"{'='*60}\n")

    # Save stats
    stats_file = output_dir / f"stats.{fmt}"
    stats_df = pd.DataFrame([results["stats"]])

    if fmt == "csv":
        stats_df.to_csv(stats_file, index=False)
    else:
        stats_df.to_json(stats_file, orient="records", indent=2)
    print(f"✓ {stats_file.name}")

    # Save timeseries
    ts_file = output_dir / f"timeseries.{fmt}"
    if fmt == "csv":
        results["data"].to_csv(ts_file)
    else:
        results["data"].to_json(ts_file, orient="index", date_format="iso")
    print(f"✓ {ts_file.name}")
```

---

## 6. Complete analyze()

```python
    # Create results
    results = {"stats": stats, "data": df_clean}

    # Save and visualize
    if config["output"]["save_results"]:
        save_results(results, config)

    if config["output"]["generate_plots"]:
        generate_plots(results, config)  # Step 6

    if config["output"]["generate_plotly_html"]:
        generate_plotly_html(results, config)  # Step 7

    return results
```

---

## 7. Test Complete Analysis

Update your test:

```python
"""Test complete analysis"""
from hhw_brick.applications.my_first_app.app import analyze, load_config

config = load_config()
config["output"]["output_dir"] = "./test_output"

results = analyze("building_29.ttl", "29hhw_system_data.csv", config)

if results:
    print("\n✅ Analysis complete!")
    print(f"Mean temp diff: {results['stats']['mean_temp_diff']:.2f}°C")
    print(f"Data points: {len(results['data'])}")
```

---

## Checkpoint

- [x] Temperature differential calculated
- [x] Statistics computed
- [x] Anomaly detection implemented
- [x] Time features added
- [x] `save_results()` function created
- [x] Test runs successfully

---

## Next Step

👉 [Step 6: Matplotlib Visualization](./step-06-visualization-matplotlib.md)


In this step, you'll implement the analysis logic - calculating statistics and processing data.

## Goal of This Step

- Calculate temperature differential
- Compute statistical metrics
- Detect anomalies
- Add time-based features
- Complete the analyze() function

---

## Step 5.1: Add Analysis Section

After Step 4 (data loading and extraction), add the analysis logic to `analyze()` function:

**Add this code to `app.py` after the time filtering section**:

```python
    # Step 6: Analyze data
    print(f"{'='*60}")
    print(f"STEP 6: Analyze Data")
    print(f"{'='*60}\n")

    # Calculate temperature differential
    df_extracted["temp_diff"] = df_extracted["supply"] - df_extracted["return"]

    # Remove rows with missing data
    df_clean = df_extracted.dropna().copy()

    print(f"Valid data points: {len(df_clean)} (after removing NaN values)")

    if len(df_clean) == 0:
        print("[FAIL] No valid data after cleaning\n")
        return None
```

**Understanding**:
- `df["supply"] - df["return"]` calculates the temperature difference
- `dropna()` removes any rows with missing values
- `.copy()` creates a copy to avoid pandas warnings

---

## Step 5.2: Calculate Statistics

Add statistical calculations:

```python
    # Get thresholds from config
    threshold_min = config["analysis"]["threshold_min_delta"]
    threshold_max = config["analysis"]["threshold_max_delta"]

    # Calculate statistics
    stats = {
        "count": len(df_clean),
        "mean_temp_diff": df_clean["temp_diff"].mean(),
        "std_temp_diff": df_clean["temp_diff"].std(),
        "min_temp_diff": df_clean["temp_diff"].min(),
        "max_temp_diff": df_clean["temp_diff"].max(),
        "median_temp_diff": df_clean["temp_diff"].median(),
        "q25_temp_diff": df_clean["temp_diff"].quantile(0.25),
        "q75_temp_diff": df_clean["temp_diff"].quantile(0.75),
        "mean_supply_temp": df_clean["supply"].mean(),
        "mean_return_temp": df_clean["return"].mean(),
    }

    print(f"\nStatistics:")
    print(f"  Mean temp diff:   {stats['mean_temp_diff']:.2f} °C")
    print(f"  Std deviation:    {stats['std_temp_diff']:.2f} °C")
    print(f"  Range:            [{stats['min_temp_diff']:.2f}, {stats['max_temp_diff']:.2f}] °C")
    print(f"  Median:           {stats['median_temp_diff']:.2f} °C")
```

**Understanding Statistics**:
- `mean()` - Average value
- `std()` - Standard deviation (spread)
- `min()/max()` - Minimum and maximum values
- `median()` - Middle value (50th percentile)
- `quantile(0.25)` - 25th percentile (Q1)
- `quantile(0.75)` - 75th percentile (Q3)

---

## Step 5.3: Anomaly Detection

Detect values outside normal range:

```python
    # Detect anomalies
    anomalies_low = df_clean[df_clean["temp_diff"] < threshold_min]
    anomalies_high = df_clean[df_clean["temp_diff"] > threshold_max]

    stats["anomalies_below_threshold"] = len(anomalies_low)
    stats["anomalies_above_threshold"] = len(anomalies_high)
    stats["anomaly_rate"] = (
        (stats["anomalies_below_threshold"] + stats["anomalies_above_threshold"])
        / stats["count"]
        * 100
    )

    print(f"  Anomalies (low):  {stats['anomalies_below_threshold']} "
          f"({stats['anomalies_below_threshold']/stats['count']*100:.1f}%)")
    print(f"  Anomalies (high): {stats['anomalies_above_threshold']} "
          f"({stats['anomalies_above_threshold']/stats['count']*100:.1f}%)")
    print(f"  Total anomalies:  {stats['anomaly_rate']:.2f}%")
```

**Understanding Anomaly Detection**:
- `df[df["column"] < value]` - Filter rows below threshold
- `df[df["column"] > value]` - Filter rows above threshold
- Anomaly rate = (total anomalies / total points) × 100

---

## Step 5.4: Add Time Features

Add time-based columns for analysis:

```python
    # Add time-based features for visualization
    df_clean.loc[:, "hour"] = df_clean.index.hour
    df_clean.loc[:, "weekday"] = df_clean.index.dayofweek
    df_clean.loc[:, "month"] = df_clean.index.month

    print(f"\n[OK] Analysis complete!")
```

**Understanding Time Features**:
- `index.hour` - Hour of day (0-23)
- `index.dayofweek` - Day of week (0=Monday, 6=Sunday)
- `index.month` - Month (1-12)
- These are used for time-pattern analysis in visualizations

---

## Step 5.5: Return Results

Complete the analyze() function by returning results:

```python
    # Create results dictionary
    results = {
        "stats": stats,
        "data": df_clean
    }

    # Step 7: Output (save and visualize)
    if config["output"]["save_results"]:
        save_results(results, config)

    if config["output"]["generate_plots"]:
        generate_plots(results, config)

    if config["output"]["generate_plotly_html"]:
        generate_plotly_html(results, config)

    return results
```

---

## Step 5.6: Implement save_results()

Add the function to save analysis results:

```python
def save_results(results, config):
    """Save analysis results to CSV or JSON"""
    output_dir = Path(config["output"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    export_format = config["output"]["export_format"]

    print(f"\n{'='*60}")
    print(f"SAVE: Saving results to {output_dir}")
    print(f"{'='*60}\n")

    # Save statistics
    stats_file = output_dir / f"stats.{export_format}"
    stats_df = pd.DataFrame([results["stats"]])

    if export_format == "csv":
        stats_df.to_csv(stats_file, index=False)
    else:  # json
        stats_df.to_json(stats_file, orient="records", indent=2)

    print(f"  [OK] {stats_file.name}")

    # Save timeseries data
    ts_file = output_dir / f"timeseries.{export_format}"

    if export_format == "csv":
        results["data"].to_csv(ts_file)
    else:  # json
        results["data"].to_json(ts_file, orient="index", date_format="iso")

    print(f"  [OK] {ts_file.name}")
```

---

## Step 5.7: Complete analyze() Function

Your complete `analyze()` function should look like this:

```python
def analyze(brick_model_path, timeseries_data_path, config):
    """Execute analysis workflow"""

    # Step 1: Qualify
    qualified, qualify_result = qualify(brick_model_path)
    if not qualified:
        return None

    # Step 2: Load data
    g, df = load_data(brick_model_path, timeseries_data_path)

    # Step 3: Map sensors
    supply_uri = qualify_result["supply"]
    return_uri = qualify_result["return"]
    sensor_mapping = map_sensors_to_columns(g, [supply_uri, return_uri], df)

    if len(sensor_mapping) != 2:
        print("[FAIL] Sensor mapping failed\n")
        return None

    # Step 4: Extract data
    df_extracted = extract_data_columns(
        df, sensor_mapping,
        rename_map={supply_uri: "supply", return_uri: "return"}
    )

    # Step 5: Filter time range (optional)
    if config["time_range"]["start_time"] or config["time_range"]["end_time"]:
        df_extracted = filter_time_range(
            df_extracted,
            config["time_range"]["start_time"],
            config["time_range"]["end_time"]
        )

    # Step 6: Analyze
    df_extracted["temp_diff"] = df_extracted["supply"] - df_extracted["return"]
    df_clean = df_extracted.dropna().copy()

    if len(df_clean) == 0:
        return None

    # Calculate statistics
    threshold_min = config["analysis"]["threshold_min_delta"]
    threshold_max = config["analysis"]["threshold_max_delta"]

    stats = {
        "count": len(df_clean),
        "mean_temp_diff": df_clean["temp_diff"].mean(),
        "std_temp_diff": df_clean["temp_diff"].std(),
        "min_temp_diff": df_clean["temp_diff"].min(),
        "max_temp_diff": df_clean["temp_diff"].max(),
        "median_temp_diff": df_clean["temp_diff"].median(),
        "q25_temp_diff": df_clean["temp_diff"].quantile(0.25),
        "q75_temp_diff": df_clean["temp_diff"].quantile(0.75),
        "mean_supply_temp": df_clean["supply"].mean(),
        "mean_return_temp": df_clean["return"].mean(),
        "anomalies_below_threshold": len(df_clean[df_clean["temp_diff"] < threshold_min]),
        "anomalies_above_threshold": len(df_clean[df_clean["temp_diff"] > threshold_max]),
    }
    stats["anomaly_rate"] = (
        (stats["anomalies_below_threshold"] + stats["anomalies_above_threshold"])
        / stats["count"] * 100
    )

    # Add time features
    df_clean.loc[:, "hour"] = df_clean.index.hour
    df_clean.loc[:, "weekday"] = df_clean.index.dayofweek
    df_clean.loc[:, "month"] = df_clean.index.month

    # Create results
    results = {"stats": stats, "data": df_clean}

    # Step 7: Output
    if config["output"]["save_results"]:
        save_results(results, config)

    if config["output"]["generate_plots"]:
        generate_plots(results, config)

    if config["output"]["generate_plotly_html"]:
        generate_plotly_html(results, config)

    return results
```

---

## Step 5.8: Test the Analysis

Create a test script:

```python
"""Test complete analyze function"""
from pathlib import Path
import sys

app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir.parent.parent.parent))

from hhw_brick.applications.my_first_app.app import analyze, load_config

def test_analyze():
    """Test complete analysis"""
    print("Testing complete analyze function...\n")

    fixtures = Path(__file__).parent.parent.parent.parent / "tests" / "fixtures"
    model_file = fixtures / "Brick_Model_File" / "building_29.ttl"
    data_file = fixtures / "TimeSeriesData" / "29hhw_system_data.csv"

    if not model_file.exists() or not data_file.exists():
        print("Test files not found")
        return

    config = load_config()
    config["output"]["output_dir"] = "./test_results"

    results = analyze(str(model_file), str(data_file), config)

    if results:
        print(f"\n{'='*60}")
        print("✅ Analysis complete!")
        print(f"{'='*60}")
        print(f"\nStatistics:")
        for key, value in results["stats"].items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")

        print(f"\nData shape: {results['data'].shape}")
        print(f"Columns: {list(results['data'].columns)}")
    else:
        print("\n❌ Analysis failed")

if __name__ == "__main__":
    test_analyze()
```

---

## Checkpoint

Before proceeding, verify:

- [x] Temperature differential calculated
- [x] Statistics computed (mean, std, min, max, etc.)
- [x] Anomaly detection implemented
- [x] Time features added
- [x] save_results() function created
- [x] analyze() returns results dictionary
- [x] Test script runs successfully

---

## Next Steps

✅ Analysis logic complete!

👉 Continue to [Step 6: Matplotlib Visualization](./step-06-visualization-matplotlib.md)

---

## Common Issues

**Issue**: `KeyError: 'threshold_min_delta'`  
**Solution**: Make sure your `config.yaml` has the `analysis` section with these parameters

**Issue**: All values are NaN after `dropna()`  
**Solution**: Check if your sensors are correctly mapped and have valid data

**Issue**: Division by zero in anomaly rate  
**Solution**: Add check: `if stats['count'] > 0:` before calculating rate

**Issue**: `SettingWithCopyWarning` from pandas  
**Solution**: Use `.copy()` when creating df_clean and `.loc[]` for assignments

---

## Summary

You've now completed the core analysis logic:

✅ **Data Processing**: Calculate temperature differential  
✅ **Statistics**: Mean, std, min, max, quantiles  
✅ **Anomaly Detection**: Find values outside thresholds  
✅ **Time Features**: Add hour, weekday, month columns  
✅ **Save Results**: Export to CSV or JSON  

Next step: Create visualizations!
