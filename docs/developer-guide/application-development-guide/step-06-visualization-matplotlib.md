# Step 6: Matplotlib Visualization

Create professional static plots with matplotlib.

---

## 1. Add Imports

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Plot settings
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams["figure.figsize"] = (14, 8)
plt.rcParams["font.size"] = 10
```

---

## 2. Implement generate_plots()

```python
def generate_plots(results, config):
    """Generate matplotlib plots"""
    output_dir = Path(config["output"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    fmt = config["output"]["plot_format"]

    print(f"\n{'='*60}")
    print("PLOTS")
    print(f"{'='*60}\n")

    df = results["data"]
    stats = results["stats"]

    # Generate 4 plots
    plot_timeseries(df, stats, output_dir, fmt)
    plot_distribution(df, stats, output_dir, fmt)
    plot_heatmap(df, output_dir, fmt)
    plot_hourly_pattern(df, output_dir, fmt)

    print("✓ All plots generated")
```

---

## 3. Time-Series Plot

```python
def plot_timeseries(df, stats, output_dir, fmt):
    """Plot temperatures and differential over time"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # Plot 1: Supply and Return
    ax1.plot(df.index, df["supply"], label="Supply", color="#e74c3c", linewidth=1.5)
    ax1.plot(df.index, df["return"], label="Return", color="#3498db", linewidth=1.5)
    ax1.set_ylabel("Temperature (°C)")
    ax1.set_title("Supply and Return Temperatures", fontweight="bold")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Differential
    ax2.plot(df.index, df["temp_diff"], color="#9b59b6", linewidth=1.5)
    ax2.axhline(stats["mean_temp_diff"], color="#27ae60", linestyle="--",
                label=f"Mean: {stats['mean_temp_diff']:.2f}°C")
    ax2.set_xlabel("Time")
    ax2.set_ylabel("Temperature Difference (°C)")
    ax2.set_title("Temperature Differential", fontweight="bold")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / f"timeseries.{fmt}", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✓ timeseries.{fmt}")
```

---

## 4. Distribution Histogram

```python
def plot_distribution(df, stats, output_dir, fmt):
    """Plot distribution histogram"""
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.hist(df["temp_diff"], bins=50, color="#3498db", alpha=0.7, edgecolor="black")
    ax.axvline(stats["mean_temp_diff"], color="#e74c3c", linestyle="--",
               linewidth=2, label=f"Mean: {stats['mean_temp_diff']:.2f}°C")
    ax.axvline(stats["median_temp_diff"], color="#27ae60", linestyle="--",
               linewidth=2, label=f"Median: {stats['median_temp_diff']:.2f}°C")

    ax.set_xlabel("Temperature Difference (°C)")
    ax.set_ylabel("Frequency")
    ax.set_title("Distribution", fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(output_dir / f"distribution.{fmt}", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✓ distribution.{fmt}")
```

---

## 5. Heatmap

```python
def plot_heatmap(df, output_dir, fmt):
    """Plot heatmap by hour and weekday"""
    pivot = df.pivot_table(values="temp_diff", index="hour",
                           columns="weekday", aggfunc="mean")

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="RdYlBu_r",
                center=pivot.values.mean(),
                cbar_kws={"label": "Mean Temp Diff (°C)"}, ax=ax)

    ax.set_xlabel("Day of Week (0=Mon, 6=Sun)")
    ax.set_ylabel("Hour of Day")
    ax.set_title("Average by Hour and Weekday", fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_dir / f"heatmap.{fmt}", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✓ heatmap.{fmt}")
```

---

## 6. Hourly Pattern

```python
def plot_hourly_pattern(df, output_dir, fmt):
    """Plot hourly pattern with error bars"""
    hourly = df.groupby("hour")["temp_diff"].agg(["mean", "std"])

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(hourly.index, hourly["mean"], yerr=hourly["std"],
           color="#3498db", alpha=0.7, error_kw={"elinewidth": 2, "capsize": 5})

    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Mean Temperature Difference (°C)")
    ax.set_title("Hourly Pattern", fontweight="bold")
    ax.set_xticks(range(24))
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(output_dir / f"hourly_pattern.{fmt}", dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✓ hourly_pattern.{fmt}")
```

---

## Checkpoint

- [x] Matplotlib imports added
- [x] 4 plot types implemented
- [x] Plots save in correct format
- [x] Test generates all plots

---

## Next Step

👉 [Step 7: Plotly HTML Visualization](./step-07-visualization-plotly.md)


In this step, you'll create professional static plots using matplotlib and seaborn.

## Goal of This Step

- Generate time-series plots
- Create distribution histograms
- Build heatmaps for pattern analysis
- Save plots in multiple formats (PNG, PDF, SVG)

---

## Step 6.1: Add Matplotlib Imports

At the top of your `app.py`, ensure you have these imports:

```python
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Plot settings
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams["figure.figsize"] = (14, 8)
plt.rcParams["font.size"] = 10
```

**Understanding**:
- `sns.set_style("whitegrid")` - Clean background with grid
- `sns.set_palette("husl")` - Colorful, distinguishable colors
- `plt.rcParams` - Default figure size and font

---

## Step 6.2: Implement generate_plots()

Create the main plotting function:

```python
def generate_plots(results, config):
    """Generate matplotlib visualizations"""
    output_dir = Path(config["output"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_format = config["output"]["plot_format"]

    print(f"\n{'='*60}")
    print(f"PLOTS: Generating matplotlib plots")
    print(f"{'='*60}\n")

    df = results["data"]
    stats = results["stats"]

    # Generate all plots
    plot_timeseries(df, stats, output_dir, plot_format)
    plot_distribution(df, stats, output_dir, plot_format)
    plot_heatmap(df, output_dir, plot_format)
    plot_hourly_pattern(df, output_dir, plot_format)

    print(f"\n[OK] All plots generated")
```

---

## Step 6.3: Time-Series Plot

Create a time-series visualization:

```python
def plot_timeseries(df, stats, output_dir, plot_format):
    """Plot temperature differential over time"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # Plot 1: Supply and Return temperatures
    ax1.plot(df.index, df["supply"], label="Supply Temp", color="#e74c3c", linewidth=1.5)
    ax1.plot(df.index, df["return"], label="Return Temp", color="#3498db", linewidth=1.5)
    ax1.set_ylabel("Temperature (°C)", fontsize=12)
    ax1.set_title("Supply and Return Temperatures", fontsize=14, fontweight="bold")
    ax1.legend(loc="upper right")
    ax1.grid(True, alpha=0.3)

    # Plot 2: Temperature differential
    ax2.plot(df.index, df["temp_diff"], label="Temp Diff", color="#9b59b6", linewidth=1.5)
    ax2.axhline(y=stats["mean_temp_diff"], color="#27ae60", linestyle="--",
                label=f"Mean: {stats['mean_temp_diff']:.2f}°C")
    ax2.set_xlabel("Time", fontsize=12)
    ax2.set_ylabel("Temperature Difference (°C)", fontsize=12)
    ax2.set_title("Temperature Differential", fontsize=14, fontweight="bold")
    ax2.legend(loc="upper right")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    filepath = output_dir / f"timeseries.{plot_format}"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"  [OK] {filepath.name}")
```

**Understanding**:
- `subplots(2, 1)` - Create 2 rows, 1 column of plots
- `sharex=True` - Share x-axis between plots
- `axhline()` - Horizontal line for mean
- `dpi=300` - High resolution for publication
- `bbox_inches="tight"` - Remove extra whitespace

---

## Step 6.4: Distribution Histogram

Create a histogram showing value distribution:

```python
def plot_distribution(df, stats, output_dir, plot_format):
    """Plot distribution of temperature differential"""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Histogram
    ax.hist(df["temp_diff"], bins=50, color="#3498db", alpha=0.7, edgecolor="black")

    # Add vertical lines for statistics
    ax.axvline(stats["mean_temp_diff"], color="#e74c3c", linestyle="--",
               linewidth=2, label=f"Mean: {stats['mean_temp_diff']:.2f}°C")
    ax.axvline(stats["median_temp_diff"], color="#27ae60", linestyle="--",
               linewidth=2, label=f"Median: {stats['median_temp_diff']:.2f}°C")

    # Labels and title
    ax.set_xlabel("Temperature Difference (°C)", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.set_title("Distribution of Temperature Differential", fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    filepath = output_dir / f"distribution.{plot_format}"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"  [OK] {filepath.name}")
```

**Understanding**:
- `bins=50` - Number of histogram bars
- `alpha=0.7` - Transparency
- `edgecolor="black"` - Outline for each bar
- `axvline()` - Vertical line for mean/median

---

## Step 6.5: Heatmap

Create a heatmap showing patterns by hour and day:

```python
def plot_heatmap(df, output_dir, plot_format):
    """Plot heatmap of temperature differential by hour and weekday"""
    # Create pivot table
    pivot = df.pivot_table(
        values="temp_diff",
        index="hour",
        columns="weekday",
        aggfunc="mean"
    )

    # Create heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        pivot,
        annot=True,
        fmt=".1f",
        cmap="RdYlBu_r",
        center=pivot.values.mean(),
        cbar_kws={"label": "Mean Temp Diff (°C)"},
        ax=ax
    )

    # Customize
    ax.set_xlabel("Day of Week (0=Monday, 6=Sunday)", fontsize=12)
    ax.set_ylabel("Hour of Day", fontsize=12)
    ax.set_title("Average Temperature Differential by Hour and Weekday",
                 fontsize=14, fontweight="bold")

    plt.tight_layout()
    filepath = output_dir / f"heatmap.{plot_format}"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"  [OK] {filepath.name}")
```

**Understanding**:
- `pivot_table()` - Reorganize data into matrix
- `sns.heatmap()` - Create colored grid
- `annot=True` - Show values in cells
- `fmt=".1f"` - Format numbers to 1 decimal
- `cmap="RdYlBu_r"` - Color scheme (red-yellow-blue reversed)

---

## Step 6.6: Hourly Pattern Plot

Show how values change by hour:

```python
def plot_hourly_pattern(df, output_dir, plot_format):
    """Plot hourly pattern of temperature differential"""
    hourly_stats = df.groupby("hour")["temp_diff"].agg(["mean", "std", "count"])

    fig, ax = plt.subplots(figsize=(12, 6))

    # Bar plot with error bars
    ax.bar(hourly_stats.index, hourly_stats["mean"],
           yerr=hourly_stats["std"],
           color="#3498db", alpha=0.7,
           error_kw={"elinewidth": 2, "capsize": 5})

    ax.set_xlabel("Hour of Day", fontsize=12)
    ax.set_ylabel("Mean Temperature Difference (°C)", fontsize=12)
    ax.set_title("Hourly Pattern of Temperature Differential",
                 fontsize=14, fontweight="bold")
    ax.set_xticks(range(24))
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    filepath = output_dir / f"hourly_pattern.{plot_format}"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"  [OK] {filepath.name}")
```

**Understanding**:
- `groupby("hour")` - Group data by hour
- `.agg(["mean", "std"])` - Calculate multiple statistics
- `yerr=` - Error bars showing standard deviation
- `set_xticks()` - Set x-axis tick marks

---

## Step 6.7: Update Config for Plot Format

In your `config.yaml`, users can choose output format:

```yaml
output:
  generate_plots: true
  plot_format: "png"  # Options: png, pdf, svg
```

**Formats**:
- **PNG**: Best for web, presentations, reports
- **PDF**: Best for publications, vector graphics
- **SVG**: Best for editing in vector graphics software

---

## Step 6.8: Test the Plots

Update your test script to check plots:

```python
def test_plots():
    """Test plotting functions"""
    from hhw_brick.applications.my_first_app.app import analyze, load_config

    fixtures = Path(__file__).parent.parent.parent.parent / "tests" / "fixtures"
    model_file = fixtures / "Brick_Model_File" / "building_29.ttl"
    data_file = fixtures / "TimeSeriesData" / "29hhw_system_data.csv"

    config = load_config()
    config["output"]["output_dir"] = "./test_plots"
    config["output"]["generate_plots"] = True
    config["output"]["plot_format"] = "png"

    results = analyze(str(model_file), str(data_file), config)

    if results:
        print("\n✅ Plots generated successfully!")
        print(f"Check folder: {config['output']['output_dir']}")
    else:
        print("\n❌ Plot generation failed")

if __name__ == "__main__":
    test_plots()
```

**Run the test**:
```bash
python test_plots.py
```

**Expected output**: 4 plot files in `test_plots/` directory

---

## Step 6.9: Complete generate_plots() Implementation

Your final `app.py` should have all these functions:

```python
def generate_plots(results, config):
    """Generate matplotlib visualizations"""
    # ...implementation from Step 6.2...

def plot_timeseries(df, stats, output_dir, plot_format):
    """Plot temperature differential over time"""
    # ...implementation from Step 6.3...

def plot_distribution(df, stats, output_dir, plot_format):
    """Plot distribution of temperature differential"""
    # ...implementation from Step 6.4...

def plot_heatmap(df, output_dir, plot_format):
    """Plot heatmap of temperature differential by hour and weekday"""
    # ...implementation from Step 6.5...

def plot_hourly_pattern(df, output_dir, plot_format):
    """Plot hourly pattern of temperature differential"""
    # ...implementation from Step 6.6...
```

---

## Checkpoint

Before proceeding, verify:

- [x] All imports added (matplotlib, seaborn)
- [x] generate_plots() function created
- [x] 4 plot types implemented:
  - [x] Time-series plot
  - [x] Distribution histogram
  - [x] Heatmap
  - [x] Hourly pattern
- [x] Plots save in configured format
- [x] Test script generates all plots

---

## Next Steps

✅ Matplotlib visualization complete!

👉 Continue to [Step 7: Plotly HTML Visualization](./step-07-visualization-plotly.md)

---

## Common Issues

**Issue**: `ImportError: No module named 'matplotlib'`  
**Solution**: `pip install matplotlib seaborn`

**Issue**: Plots are blank or don't show  
**Solution**: Make sure to call `plt.close()` after `plt.savefig()`

**Issue**: Labels overlap or are cut off  
**Solution**: Use `plt.tight_layout()` before saving

**Issue**: Low quality images  
**Solution**: Set `dpi=300` in `savefig()`

---

## Customization Tips

### Change Colors

```python
# Use different color palettes
sns.set_palette("Set2")  # Pastel colors
sns.set_palette("dark")  # Dark colors
sns.set_palette(["#FF6B6B", "#4ECDC4", "#45B7D1"])  # Custom colors
```

### Change Figure Size

```python
plt.figure(figsize=(16, 10))  # Larger
plt.figure(figsize=(10, 6))   # Smaller
```

### Add More Statistics

```python
# Add min/max lines
ax.axhline(stats["min_temp_diff"], color="blue", linestyle=":", label="Min")
ax.axhline(stats["max_temp_diff"], color="red", linestyle=":", label="Max")
```

---

## Summary

You've created professional visualizations:

✅ **Time-Series**: Temperature over time  
✅ **Distribution**: Histogram with statistics  
✅ **Heatmap**: Patterns by hour and day  
✅ **Hourly Pattern**: Average by hour with error bars  
✅ **Multiple Formats**: PNG, PDF, SVG support  

Next: Interactive Plotly HTML visualizations!
