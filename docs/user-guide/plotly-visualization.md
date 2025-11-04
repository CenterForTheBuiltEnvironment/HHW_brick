# Plotly Interactive Visualization

## Overview

HHW Brick framework now supports generating **interactive HTML visualizations** using [Plotly](https://plotly.com/python/), in addition to the traditional static matplotlib plots.

Interactive visualizations allow you to:
- **Zoom and pan** through data
- **Hover** over data points for detailed information
- **Toggle traces** on/off by clicking legend items
- **Export** high-quality images
- **Share** results as standalone HTML files that can be viewed in any web browser

## Features

Each application that supports Plotly visualization generates **4 interactive HTML files**:

### 1. Comprehensive Dashboard
A multi-panel dashboard with 6 subplots showing:
- Supply and return temperature timeseries
- Temperature differential timeseries
- Distribution histogram
- Supply vs return scatter plot
- Hourly pattern analysis
- Weekly pattern analysis

**File**: `*_interactive_dashboard.html`

### 2. Detailed Timeseries
Dual y-axis plot showing:
- Supply temperature (left axis)
- Return temperature (left axis)
- Temperature differential (right axis)
- Threshold lines for anomaly detection

**File**: `*_timeseries_interactive.html`

### 3. Heatmap Visualization
Interactive heatmap showing temperature differential patterns:
- Hour of day (y-axis)
- Day of week (x-axis)
- Color intensity represents mean temperature differential

**File**: `*_heatmap_interactive.html`

### 4. Box Plot Distribution
Statistical distribution analysis with:
- Box plot showing quartiles
- Mean and standard deviation indicators
- Interactive hover for detailed statistics

**File**: `*_boxplot_interactive.html`

## Configuration

### Enable/Disable Plotly Visualization

In your application's `config.yaml`:

```yaml
output:
  generate_plotly_html: true  # Set to false to disable
  output_dir: "./results"
```

### Python Code Configuration

```python
from hhw_brick.applications.primary_loop_temp_diff.app import analyze, load_config

config = load_config()
config["output"]["generate_plotly_html"] = True  # Enable Plotly HTML
config["output"]["generate_plots"] = True        # Also generate matplotlib plots
config["output"]["output_dir"] = "./results"

results = analyze(brick_model_path, timeseries_path, config)
```

## Usage Examples

### Example 1: Basic Usage with Default Settings

```python
from hhw_brick.applications.primary_loop_temp_diff.app import analyze, load_config

# Load default configuration (Plotly enabled by default)
config = load_config()

# Run analysis
results = analyze(
    "path/to/brick_model.ttl",
    "path/to/timeseries.csv",
    config
)
```

### Example 2: Plotly Only (No Matplotlib)

```python
config = load_config()
config["output"]["generate_plots"] = False        # Disable matplotlib
config["output"]["generate_plotly_html"] = True   # Keep Plotly enabled

results = analyze(brick_model_path, timeseries_path, config)
```

### Example 3: Command Line Usage

```bash
# Run primary loop analysis (generates both matplotlib and Plotly visualizations)
python -m hhw_brick.applications.primary_loop_temp_diff.app \
    brick_model.ttl \
    timeseries.csv \
    --output-dir ./results

# Run secondary loop analysis
python -m hhw_brick.applications.secondary_loop_temp_diff.app \
    brick_model.ttl \
    timeseries.csv \
    --output-dir ./results
```

### Example 4: Using the Dedicated Example Script

```bash
# Navigate to examples directory
cd examples

# Run the Plotly visualization example
python 09_plotly_visualization.py
```

## Output Files

After running an analysis with Plotly enabled, you'll find these files in your output directory:

```
results/
├── primary_loop_interactive_dashboard.html      # Main dashboard
├── primary_loop_timeseries_interactive.html     # Detailed timeseries
├── primary_loop_heatmap_interactive.html        # Pattern heatmap
├── primary_loop_boxplot_interactive.html        # Distribution analysis
├── primary_loop_temp_diff_stats.csv             # Statistics (CSV)
├── primary_loop_temp_diff_timeseries.csv        # Raw data (CSV)
└── [matplotlib PNG files if enabled]
```

## Viewing Interactive HTML Files

1. **Open in Web Browser**: Double-click any `.html` file to open it in your default web browser

2. **Interactive Controls**:
   - **Pan**: Click and drag on the plot
   - **Zoom**: Use scroll wheel or box zoom (toolbar)
   - **Reset**: Double-click on the plot
   - **Toggle Traces**: Click legend items to show/hide data series
   - **Hover**: Move cursor over data points for details
   - **Download**: Click camera icon to save as PNG

3. **Sharing**: HTML files are standalone and can be:
   - Emailed to colleagues
   - Uploaded to web servers
   - Embedded in reports
   - Viewed offline

## Customization

### Modifying Plotly Visualizations

To customize the Plotly visualizations, edit the `generate_plotly_html()` function in your application's `app.py`:

```python
def generate_plotly_html(results, config):
    # Customize colors
    supply_color = '#e74c3c'  # Red for supply
    return_color = '#3498db'  # Blue for return

    # Customize layout
    fig.update_layout(
        title_text="My Custom Title",
        template='plotly_dark',  # Try: plotly, plotly_white, plotly_dark
        height=1600,             # Adjust height
    )

    # Customize hover templates
    hovertemplate='<b>Custom</b><br>Time: %{x}<br>Value: %{y:.2f}°C<extra></extra>'
```

### Available Plotly Templates

- `plotly` (default)
- `plotly_white`
- `plotly_dark`
- `ggplot2`
- `seaborn`
- `simple_white`

## Benefits of Interactive Visualization

### For Data Exploration
- Quickly zoom into specific time periods
- Identify outliers and anomalies by hovering
- Compare multiple time periods side-by-side

### For Presentations
- Professional, modern visualizations
- No need for PowerPoint - just open in browser
- Real-time interaction during presentations

### For Reports
- Embed in HTML reports
- Self-contained files (no external dependencies)
- Works on any device with a web browser

### For Collaboration
- Easy to share via email or cloud storage
- Anyone can view without installing Python
- Interactive exploration of data

## Performance Considerations

- **Large Datasets**: Plotly handles up to ~100k points well. For larger datasets, consider:
  - Downsampling data
  - Using WebGL rendering: `fig.update_traces(mode='lines+markers', marker=dict(size=2), line=dict(width=1))`

- **File Size**: HTML files range from 500KB to 5MB depending on data size

- **Loading Time**: Initial load takes 1-3 seconds for typical datasets

## Troubleshooting

### Issue: HTML file won't open
**Solution**: Make sure you have a modern web browser (Chrome, Firefox, Edge, Safari)

### Issue: Visualization is slow
**Solution**: Reduce data points or use WebGL rendering

### Issue: Colors don't match matplotlib plots
**Solution**: Customize colors in `generate_plotly_html()` function

### Issue: Missing data in plots
**Solution**: Check that data preprocessing is consistent between matplotlib and Plotly functions

## API Reference

### Configuration Options

```python
config = {
    "output": {
        "generate_plotly_html": bool,  # Enable/disable Plotly HTML generation
        "output_dir": str,              # Output directory path
        "save_results": bool,           # Save CSV/JSON results
        "generate_plots": bool,         # Enable/disable matplotlib plots
    }
}
```

### Generated Functions

Both `primary_loop_temp_diff` and `secondary_loop_temp_diff` applications include:

- `generate_plotly_html(results, config)`: Main function to generate all HTML files
  - **Parameters**:
    - `results`: Dictionary containing `stats` and `data` from analysis
    - `config`: Configuration dictionary
  - **Returns**: None (saves files to disk)

## Examples in Repository

See the following examples for complete working code:

- `examples/09_plotly_visualization.py` - Dedicated Plotly example
- `examples/06_application_management.py` - Application framework usage
- `examples/07_run_application.py` - Running applications programmatically

## Further Reading

- [Plotly Python Documentation](https://plotly.com/python/)
- [Plotly Figure Reference](https://plotly.com/python/reference/)
- [Plotly Subplots](https://plotly.com/python/subplots/)
- [Plotly Styling](https://plotly.com/python/templates/)
