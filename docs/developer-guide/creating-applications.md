# Creating Analytics Applications

This guide teaches you how to create your own analytics applications for the HHW Brick framework.

## Table of Contents

- [Overview](#overview)
- [Application Structure](#application-structure)
- [Required Files](#required-files)
- [Core Functions](#core-functions)
- [Configuration File](#configuration-file)
- [SPARQL Queries](#sparql-queries)
- [Visualization](#visualization)
- [Testing Your Application](#testing-your-application)
- [Best Practices](#best-practices)

---

## Overview

An **analytics application** in HHW Brick is a self-contained module that:
1. **Qualifies** buildings (checks if required sensors exist)
2. **Analyzes** time-series data from qualified buildings
3. **Generates** visualizations and results

Applications are portable and can run on any building with the required sensors.

---

## Application Structure

Each application is a Python package in the `hhw_brick/applications/` directory:

```
hhw_brick/applications/
└── your_app_name/
    ├── __init__.py          # Package metadata
    ├── app.py               # Main application code
    ├── config.yaml          # Default configuration
    ├── requirements.txt     # App-specific dependencies
    └── README.md            # App documentation
```

### File Purposes

| File | Purpose | Required |
|------|---------|----------|
| `__init__.py` | Exports core functions and metadata | ✅ Yes |
| `app.py` | Main application logic | ✅ Yes |
| `config.yaml` | Default configuration settings | ✅ Yes |
| `requirements.txt` | Python dependencies | ✅ Yes |
| `README.md` | User-facing documentation | ⭐ Recommended |

---

## Required Files

### 1. `__init__.py`

This file exports your application's core functions and provides metadata.

```python
"""
Your Application Name

Brief description of what your app does.

Author: Your Name
"""

from .app import qualify, analyze, load_config

__all__ = ["qualify", "analyze", "load_config"]

# Application metadata
__app_name__ = "your_app_name"
__version__ = "1.0.0"
__description__ = "Brief description"
__author__ = "Your Name"
```

### 2. `app.py`

This is your main application file. It must contain at least three core functions:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Your Application Name

Detailed description of your application.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yaml
import argparse

# Setup paths
app_dir = Path(__file__).parent
package_dir = app_dir.parent.parent.parent
sys.path.insert(0, str(package_dir))

# Import HHW Brick utilities
from hhw_brick.utils import (
    load_data,
    query_sensors,
    map_sensors_to_columns,
    extract_data_columns,
    filter_time_range,
)

# Export core functions
__all__ = ["qualify", "analyze", "load_config"]

# Plot settings
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams["figure.figsize"] = (14, 8)
plt.rcParams["font.size"] = 10


def load_config(config_file=None):
    """Load configuration from YAML file"""
    if config_file is None:
        config_file = app_dir / "config.yaml"

    config_path = Path(config_file)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            f"Please ensure config.yaml exists in the application directory."
        )

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config if config else {}


def find_required_sensors(graph):
    """
    Find required sensors using SPARQL query

    Returns:
        Tuple of sensor URIs or None if not found
    """
    query = """
    SELECT ?equipment ?sensor1 ?sensor2 WHERE {
        # Your SPARQL query here
        # See SPARQL section below for examples
    }
    """

    results = query_sensors(graph, [], custom_query=query)
    return results[0] if results else None


def qualify(brick_model_path):
    """
    Check if building has required sensors

    Args:
        brick_model_path: Path to Brick model file (.ttl)

    Returns:
        Tuple of (qualified: bool, details: dict)
    """
    print(f"\n{'='*60}")
    print(f"QUALIFY: Checking required sensors")
    print(f"{'='*60}\n")

    from rdflib import Graph

    g = Graph()
    g.parse(brick_model_path, format="turtle")

    result = find_required_sensors(g)

    if result:
        equipment, sensor1, sensor2 = result
        print(f"[OK] Building qualified")
        print(f"   Equipment: {equipment}")
        print(f"   Sensor 1: {sensor1}")
        print(f"   Sensor 2: {sensor2}\n")
        return True, {
            "equipment": str(equipment),
            "sensor1": str(sensor1),
            "sensor2": str(sensor2)
        }
    else:
        print(f"[FAIL] Building NOT qualified")
        print(f"   Missing: Required sensors\n")
        return False, {}


def analyze(brick_model_path, timeseries_data_path, config):
    """
    Execute analysis workflow

    Args:
        brick_model_path: Path to Brick model file (.ttl)
        timeseries_data_path: Path to time-series data (.csv)
        config: Configuration dictionary

    Returns:
        Dictionary with 'stats' and 'data' or None if analysis fails
    """
    # Step 1: Qualify
    qualified, qualify_result = qualify(brick_model_path)
    if not qualified:
        return None

    # Step 2: Load data
    print(f"{'='*60}")
    print(f"FETCH: Loading data")
    print(f"{'='*60}\n")

    g, df = load_data(brick_model_path, timeseries_data_path)
    print(f"[OK] Loaded {len(df)} data points")
    print(f"[OK] Time range: {df.index.min()} to {df.index.max()}\n")

    # Map sensors to data columns
    sensor1_uri = qualify_result["sensor1"]
    sensor2_uri = qualify_result["sensor2"]
    sensor_mapping = map_sensors_to_columns(g, [sensor1_uri, sensor2_uri], df)

    if len(sensor_mapping) != 2:
        print("[FAIL] Failed to map sensors to data columns\n")
        return None

    # Extract data
    df_extracted = extract_data_columns(
        df, sensor_mapping,
        rename_map={sensor1_uri: "s1", sensor2_uri: "s2"}
    )

    # Filter time range if specified
    if config["time_range"]["start_time"] or config["time_range"]["end_time"]:
        df_extracted = filter_time_range(
            df_extracted,
            config["time_range"]["start_time"],
            config["time_range"]["end_time"]
        )
        print(f"[OK] Filtered to {len(df_extracted)} data points\n")

    # Step 3: Analyze
    print(f"{'='*60}")
    print(f"ANALYZE: Computing metrics")
    print(f"{'='*60}\n")

    # YOUR ANALYSIS LOGIC HERE
    # Example: calculate difference
    df_extracted["metric"] = df_extracted["s1"] - df_extracted["s2"]
    df_clean = df_extracted.dropna().copy()

    print(f"Valid data points: {len(df_clean)}")

    # Calculate statistics
    stats = {
        "count": len(df_clean),
        "mean_metric": df_clean["metric"].mean(),
        "std_metric": df_clean["metric"].std(),
        "min_metric": df_clean["metric"].min(),
        "max_metric": df_clean["metric"].max(),
    }

    # Add time-based columns for visualization
    df_clean.loc[:, "hour"] = df_clean.index.hour
    df_clean.loc[:, "weekday"] = df_clean.index.dayofweek
    df_clean.loc[:, "month"] = df_clean.index.month

    # Print summary
    print(f"\nStatistics:")
    print(f"  Mean metric: {stats['mean_metric']:.2f}")
    print(f"  Std dev:     {stats['std_metric']:.2f}")
    print(f"  Range:       [{stats['min_metric']:.2f}, {stats['max_metric']:.2f}]")

    results = {"stats": stats, "data": df_clean}

    # Step 4: Output
    if config["output"]["save_results"]:
        save_results(results, config)

    if config["output"]["generate_plots"]:
        generate_plots(results, config)

    if config["output"]["generate_plotly_html"]:
        generate_plotly_html(results, config)

    return results


def save_results(results, config):
    """Save analysis results to CSV/JSON"""
    output_dir = Path(config["output"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    export_format = config["output"]["export_format"]

    print(f"\n{'='*60}")
    print(f"OUTPUT: Saving results to {output_dir}")
    print(f"{'='*60}\n")

    # Save statistics
    stats_file = output_dir / f"stats.{export_format}"
    stats_df = pd.DataFrame([results["stats"]])

    if export_format == "csv":
        stats_df.to_csv(stats_file, index=False)
    else:  # json
        stats_df.to_json(stats_file, orient="records", indent=2)
    print(f"  [OK] {stats_file.name}")

    # Save timeseries
    ts_file = output_dir / f"timeseries.{export_format}"
    if export_format == "csv":
        results["data"].to_csv(ts_file)
    else:  # json
        results["data"].to_json(ts_file, orient="index", date_format="iso")
    print(f"  [OK] {ts_file.name}")


def generate_plots(results, config):
    """Generate matplotlib PNG plots"""
    output_dir = Path(config["output"]["output_dir"])
    plot_format = config["output"]["plot_format"]

    print(f"\n{'='*60}")
    print(f"Generating plots")
    print(f"{'='*60}\n")

    df = results["data"]
    stats = results["stats"]

    # Example: Simple time-series plot
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(df.index, df["metric"], linewidth=1.5)
    ax.axhline(y=stats["mean_metric"], color='r', linestyle='--',
               label=f'Mean: {stats["mean_metric"]:.2f}')
    ax.set_xlabel("Time")
    ax.set_ylabel("Metric")
    ax.set_title("Metric Over Time")
    ax.legend()
    ax.grid(True, alpha=0.3)

    filepath = output_dir / f"timeseries.{plot_format}"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  [OK] {filepath.name}")


def generate_plotly_html(results, config):
    """Generate interactive Plotly HTML visualizations"""
    output_dir = Path(config["output"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Generating interactive Plotly HTML visualizations")
    print(f"{'='*60}\n")

    df = results["data"]
    stats = results["stats"]

    # Example: Interactive time-series
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["metric"],
        mode='lines',
        name='Metric',
        line=dict(color='#3498db', width=2),
        hovertemplate='Time: %{x}<br>Value: %{y:.2f}<extra></extra>'
    ))

    fig.add_hline(
        y=stats["mean_metric"],
        line_dash="dash",
        line_color="#e74c3c",
        annotation_text=f"Mean: {stats['mean_metric']:.2f}"
    )

    fig.update_layout(
        title="Interactive Metric Analysis",
        xaxis_title="Time",
        yaxis_title="Metric Value",
        hovermode='x unified',
        template='plotly_white',
        height=600
    )

    html_file = output_dir / "interactive_dashboard.html"
    fig.write_html(html_file)
    print(f"  [OK] {html_file.name}")


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description="Your Application Name",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("brick_model", help="Path to Brick model (.ttl)")
    parser.add_argument("timeseries_data", help="Path to timeseries data (.csv)")
    parser.add_argument("--config", help="Config file (optional)", default=None)
    parser.add_argument("--output-dir", help="Output directory (optional)", default=None)

    args = parser.parse_args()

    # Load config
    config = load_config(args.config)

    if args.output_dir:
        config["output"]["output_dir"] = args.output_dir

    # Run analysis
    results = analyze(args.brick_model, args.timeseries_data, config)

    if results:
        print(f"\n[SUCCESS] Analysis completed successfully!")
    else:
        print(f"\n[FAILED] Analysis failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### 3. `config.yaml`

Default configuration settings for your application:

```yaml
# Your Application Configuration File

# Analysis parameters
analysis:
  # Your analysis-specific parameters
  threshold_min: 0.5
  threshold_max: 10.0

# Output settings
output:
  # Whether to save results
  save_results: true

  # Output directory
  output_dir: "./results"

  # Export format: csv or json
  export_format: "csv"

  # Whether to generate matplotlib plots
  generate_plots: true

  # Plot format: png, pdf, or svg
  plot_format: "png"

  # Whether to generate interactive HTML visualizations with Plotly
  generate_plotly_html: true

# Time range (optional)
time_range:
  # Start time in YYYY-MM-DD format (null = use all data)
  start_time: null

  # End time in YYYY-MM-DD format (null = use all data)
  end_time: null
```

### 4. `requirements.txt`

List your application's Python dependencies:

```txt
pandas>=1.3.0
numpy>=1.21.0
matplotlib>=3.5.0
seaborn>=0.11.0
plotly>=5.0.0
rdflib>=6.0.0
brickschema>=0.6.0
pyyaml>=5.4.0
```

---

## Core Functions

Every application **must** implement these three core functions:

### 1. `load_config(config_file=None)`

**Purpose**: Load configuration from YAML file

**Parameters**:
- `config_file` (optional): Path to config file. If None, uses `config.yaml` in app directory

**Returns**: Dictionary with configuration settings

**Example**:
```python
def load_config(config_file=None):
    """Load configuration from YAML file"""
    if config_file is None:
        config_file = app_dir / "config.yaml"

    config_path = Path(config_file)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            f"Please ensure config.yaml exists in the application directory."
        )

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config if config else {}
```

### 2. `qualify(brick_model_path)`

**Purpose**: Check if a building has the required sensors for your analysis

**Parameters**:
- `brick_model_path`: Path to Brick model file (.ttl)

**Returns**: Tuple of `(qualified: bool, details: dict)`
- `qualified`: True if building has required sensors
- `details`: Dictionary with sensor URIs and other qualification info

**Example**:
```python
def qualify(brick_model_path):
    """Check if building has required sensors"""
    print(f"\n{'='*60}")
    print(f"QUALIFY: Checking required sensors")
    print(f"{'='*60}\n")

    from rdflib import Graph

    g = Graph()
    g.parse(brick_model_path, format="turtle")

    result = find_required_sensors(g)

    if result:
        equipment, sensor1, sensor2 = result
        print(f"[OK] Building qualified")
        print(f"   Equipment: {equipment}")
        print(f"   Sensor 1: {sensor1}")
        print(f"   Sensor 2: {sensor2}\n")
        return True, {
            "equipment": str(equipment),
            "sensor1": str(sensor1),
            "sensor2": str(sensor2)
        }
    else:
        print(f"[FAIL] Building NOT qualified")
        print(f"   Missing: Required sensors\n")
        return False, {}
```

### 3. `analyze(brick_model_path, timeseries_data_path, config)`

**Purpose**: Execute the main analysis workflow

**Parameters**:
- `brick_model_path`: Path to Brick model file (.ttl)
- `timeseries_data_path`: Path to time-series data (.csv)
- `config`: Configuration dictionary from `load_config()`

**Returns**: Dictionary with analysis results or None if analysis fails
- `{"stats": {...}, "data": DataFrame}` on success
- `None` on failure

**Workflow**:
1. **Qualify** the building
2. **Load** Brick model and time-series data
3. **Map** sensors to data columns
4. **Analyze** the data
5. **Save** results and generate visualizations

**Example**:
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
    sensor_mapping = map_sensors_to_columns(g, [sensor1_uri, sensor2_uri], df)

    # Step 4: Analyze
    # Your analysis logic here

    # Step 5: Output
    if config["output"]["save_results"]:
        save_results(results, config)

    if config["output"]["generate_plots"]:
        generate_plots(results, config)

    if config["output"]["generate_plotly_html"]:
        generate_plotly_html(results, config)

    return results
```

---

## Configuration File

The `config.yaml` file contains all configuration settings for your application.

### Standard Structure

```yaml
# Analysis Parameters
analysis:
  # Your app-specific parameters
  param1: value1
  param2: value2

# Output Settings
output:
  save_results: true
  output_dir: "./results"
  export_format: "csv"
  generate_plots: true
  plot_format: "png"
  generate_plotly_html: true

# Time Range
time_range:
  start_time: null
  end_time: null
```

### Required Sections

1. **`analysis`**: Your application-specific parameters
2. **`output`**: Output configuration (must include all keys shown above)
3. **`time_range`**: Optional time filtering

### Users Can Customize

Users can:
- Copy your `config.yaml` to their project
- Modify values as needed
- Pass custom config to your app:
  ```python
  config = app.load_config("my_custom_config.yaml")
  results = app.analyze(model, data, config)
  ```

---

## SPARQL Queries

SPARQL queries are used to find required sensors in Brick models.

### Writing SPARQL Queries

Brick Schema uses RDF triples. A typical query looks like:

```sparql
SELECT ?equipment ?sensor1 ?sensor2 WHERE {
    # Find equipment (e.g., Hot_Water_Loop)
    ?equipment rdf:type/rdfs:subClassOf* brick:Hot_Water_Loop .

    # Filter by name (e.g., contains "primary")
    FILTER(CONTAINS(LCASE(STR(?equipment)), "primary"))

    # Find sensors associated with equipment
    ?equipment brick:hasPart ?sensor1 .
    ?sensor1 rdf:type/rdfs:subClassOf* brick:Leaving_Hot_Water_Temperature_Sensor .

    ?equipment brick:hasPart ?sensor2 .
    ?sensor2 rdf:type/rdfs:subClassOf* brick:Entering_Hot_Water_Temperature_Sensor .
}
```

### Key SPARQL Patterns

#### 1. Find Equipment by Type
```sparql
?equipment rdf:type/rdfs:subClassOf* brick:Equipment_Type .
```

#### 2. Filter by Name
```sparql
FILTER(CONTAINS(LCASE(STR(?equipment)), "keyword"))
```

#### 3. Find Related Points
```sparql
# Points that are part of equipment
?equipment brick:hasPart ?point .

# Points that belong to equipment
?point brick:isPointOf ?equipment .
```

#### 4. Find Specific Sensor Types
```sparql
?sensor rdf:type/rdfs:subClassOf* brick:Temperature_Sensor .
```

### Learning SPARQL for Brick

**Resources**:
1. **Brick Schema Documentation**: https://brickschema.org/
2. **Brick Schema Ontology**: https://brickschema.org/ontology/
3. **SPARQL Tutorial**: https://www.w3.org/TR/sparql11-query/
4. **Brick Query Examples**: https://docs.brickschema.org/query/index.html

**Interactive Tools**:
- **Brick Studio**: https://brickstudio.io/ - Visual query builder
- **SPARQL Playground**: Test queries on example models

### Using SPARQL in Your App

```python
def find_required_sensors(graph):
    """Find required sensors using SPARQL"""
    query = """
    SELECT ?equipment ?sensor1 ?sensor2 WHERE {
        # Your SPARQL query here
    }
    """

    # Use HHW Brick's query_sensors utility
    results = query_sensors(graph, [], custom_query=query)
    return results[0] if results else None
```

---

## Visualization

Your application should support **two output formats**:

### 1. Matplotlib (PNG/PDF/SVG)

**Static plots** for reports and publications.

```python
def generate_plots(results, config):
    """Generate matplotlib plots"""
    output_dir = Path(config["output"]["output_dir"])
    plot_format = config["output"]["plot_format"]  # png, pdf, or svg

    df = results["data"]
    stats = results["stats"]

    # Create plot
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(df.index, df["metric"])
    ax.set_title("My Analysis")
    ax.grid(True)

    # Save plot
    filepath = output_dir / f"my_plot.{plot_format}"
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"  [OK] {filepath.name}")
```

**Recommended Plots**:
- Time-series plot
- Distribution histogram
- Box plot
- Heatmap (hour vs day of week)

### 2. Plotly (Interactive HTML)

**Interactive plots** for web browsers and exploration.

```python
def generate_plotly_html(results, config):
    """Generate Plotly HTML visualizations"""
    output_dir = Path(config["output"]["output_dir"])
    df = results["data"]
    stats = results["stats"]

    # Create interactive plot
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["metric"],
        mode='lines',
        name='Metric',
        hovertemplate='Time: %{x}<br>Value: %{y:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title="Interactive Analysis",
        xaxis_title="Time",
        yaxis_title="Metric",
        template='plotly_white',
        hovermode='x unified'
    )

    # Save HTML
    html_file = output_dir / "interactive.html"
    fig.write_html(html_file)

    print(f"  [OK] {html_file.name}")
```

**Recommended Interactive Plots**:
- Dashboard with multiple subplots (`make_subplots`)
- Time-series with dual y-axes
- Interactive heatmap
- Box plot with statistics

### Configuration

Users control visualization through `config.yaml`:

```yaml
output:
  generate_plots: true          # Enable/disable matplotlib
  plot_format: "png"            # png, pdf, or svg
  generate_plotly_html: true    # Enable/disable Plotly
```

---

## Testing Your Application

### 1. Manual Testing

Test with example data:

```python
from hhw_brick import apps

# Load your app
app = apps.load_app("your_app_name")

# Test qualification
qualified, details = app.qualify("path/to/model.ttl")
print(f"Qualified: {qualified}")
print(f"Details: {details}")

# Test analysis
config = app.load_config()
results = app.analyze("path/to/model.ttl", "path/to/data.csv", config)

if results:
    print(f"Stats: {results['stats']}")
    print(f"Data shape: {results['data'].shape}")
```

### 2. Test with Examples

Use the framework's example scripts:

```python
# In examples/your_test.py
from pathlib import Path
from hhw_brick import apps

fixtures = Path(__file__).parent.parent / "tests" / "fixtures"

app_name = "your_app_name"
app = apps.load_app(app_name)

# Qualify all test buildings
for model_file in (fixtures / "Brick_Model_File").glob("*.ttl"):
    qualified, details = app.qualify(str(model_file))
    if qualified:
        print(f"✓ {model_file.name}")
```

### 3. Integration with AppsManager

Verify your app is discoverable:

```python
from hhw_brick import apps

# List all apps (should include yours)
all_apps = apps.list_apps()
print([app["name"] for app in all_apps])

# Get app info
info = apps.get_app_info("your_app_name")
print(info)

# Get default config
config = apps.get_default_config("your_app_name")
print(config)
```

---

## Best Practices

### Code Organization

✅ **DO**:
- Keep `app.py` focused on analysis logic
- Use helper functions for complex operations
- Export only core functions in `__all__`
- Add docstrings to all functions
- Use type hints where appropriate

❌ **DON'T**:
- Put configuration in code (use `config.yaml`)
- Hardcode file paths
- Mix analysis logic with visualization
- Create global variables

### Configuration

✅ **DO**:
- Store all settings in `config.yaml`
- Provide sensible defaults
- Document each configuration parameter
- Allow users to override settings

❌ **DON'T**:
- Hardcode thresholds or parameters
- Require users to edit code
- Break backward compatibility

### SPARQL Queries

✅ **DO**:
- Use `rdf:type/rdfs:subClassOf*` for flexible matching
- Filter by meaningful names or properties
- Keep queries simple and readable
- Test queries on multiple buildings

❌ **DON'T**:
- Assume specific URI formats
- Use overly complex queries
- Hardcode URIs in queries

### Visualization

✅ **DO**:
- Generate both PNG and HTML outputs
- Use consistent color schemes
- Add clear labels and titles
- Include hover tooltips in Plotly plots
- Make plots informative and professional

❌ **DON'T**:
- Generate only one format
- Use too many colors or styles
- Create plots without labels
- Make plots too complex

### Error Handling

✅ **DO**:
- Print clear error messages
- Return `None` or `False` on failure
- Validate inputs
- Handle missing data gracefully

❌ **DON'T**:
- Let exceptions crash silently
- Print confusing error messages
- Assume data is always clean

### Documentation

✅ **DO**:
- Write a comprehensive `README.md`
- Document parameters and return values
- Provide usage examples
- List required sensors

❌ **DON'T**:
- Skip documentation
- Use jargon without explanation
- Forget to update docs when changing code

---

## Example: Complete Minimal Application

Here's a minimal but complete application:

```
hhw_brick/applications/
└── example_app/
    ├── __init__.py
    ├── app.py
    ├── config.yaml
    ├── requirements.txt
    └── README.md
```

**File contents available in the repository**: `hhw_brick/applications/primary_loop_temp_diff/` and `hhw_brick/applications/secondary_loop_temp_diff/`

---

## Next Steps

1. **Study existing apps**: Look at `primary_loop_temp_diff` and `secondary_loop_temp_diff`
2. **Learn Brick Schema**: Visit https://brickschema.org/
3. **Practice SPARQL**: Use Brick Studio to build queries
4. **Create your app**: Follow this guide step-by-step
5. **Test thoroughly**: Use example data to verify functionality
6. **Share your app**: Contribute back to the HHW Brick framework!

---

## Getting Help

- **Brick Schema Docs**: https://docs.brickschema.org/
- **SPARQL Tutorial**: https://www.w3.org/TR/sparql11-query/
- **HHW Brick Issues**: https://github.com/CenterForTheBuiltEnvironment/HHW_brick/issues
- **Example Applications**: See `hhw_brick/applications/` directory

---

**Happy Coding! 🚀**
