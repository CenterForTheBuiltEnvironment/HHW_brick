# Step 9: Deployment & Integration

Final steps to deploy and share your application.

---

## 1. Verify File Structure

Ensure all required files are present:

```
my_first_app/
├── __init__.py          ✅ Metadata and exports
├── app.py               ✅ Complete implementation
├── config.yaml          ✅ Default configuration
├── requirements.txt     ✅ Dependencies
└── README.md            ✅ Documentation
```

---

## 2. Update README.md

Complete your user documentation:

```markdown
# My First Application

## Overview

Analyzes temperature differential between supply and return water in hot water systems.

## Requirements

Buildings must have:
- Hot Water Loop
- Supply temperature sensor (Leaving_Hot_Water_Temperature_Sensor)
- Return temperature sensor (Entering_Hot_Water_Temperature_Sensor)

## Usage

\`\`\`python
from hhw_brick import apps

app = apps.load_app("my_first_app")

# Check qualification
qualified, details = app.qualify("building.ttl")

# Run analysis
if qualified:
    config = app.load_config()
    config["output"]["output_dir"] = "./results"
    results = app.analyze("building.ttl", "data.csv", config)
\`\`\`

## Output

- `stats.csv` - Statistical summary
- `timeseries.csv` - Processed data
- `timeseries.png` - Temperature plots
- `distribution.png` - Distribution histogram
- `heatmap.png` - Hour/weekday patterns
- `hourly_pattern.png` - Hourly averages
- `dashboard_interactive.html` - Interactive dashboard
- `timeseries_interactive.html` - Interactive timeseries
- `heatmap_interactive.html` - Interactive heatmap
- `boxplot_interactive.html` - Interactive box plot

## Configuration

Edit `config.yaml`:

\`\`\`yaml
analysis:
  threshold_min_delta: 0.5
  threshold_max_delta: 10.0

output:
  output_dir: "./results"
  export_format: "csv"      # csv or json
  plot_format: "png"        # png, pdf, svg
  generate_plots: true
  generate_plotly_html: true
\`\`\`

## Author

Your Name - v1.0.0
```

---

## 3. Test with AppsManager

Verify integration:

```python
"""Integration test"""
from hhw_brick import apps

# List apps
all_apps = apps.list_apps()
print([app["name"] for app in all_apps])

# Load app
app = apps.load_app("my_first_app")
print(f"Loaded: {app.__name__}")

# Get config
config = apps.get_default_config("my_first_app")
print(f"Config: {list(config.keys())}")

# Get info
info = apps.get_app_info("my_first_app")
print(f"Functions: {[f['name'] for f in info['functions']]}")
```

**Expected**:
```
['my_first_app', 'secondary_loop_temp_diff', 'primary_loop_temp_diff']
Loaded: hhw_brick.applications.my_first_app.app
Config: ['analysis', 'output', 'time_range']
Functions: ['qualify', 'analyze', 'load_config']
```

---

## 4. Create Usage Example

Add `example_usage.py`:

```python
"""Example usage of my_first_app"""
from pathlib import Path
from hhw_brick import apps

# Load application
app = apps.load_app("my_first_app")

# Paths
fixtures = Path("tests/fixtures")
model = fixtures / "Brick_Model_File" / "building_29.ttl"
data = fixtures / "TimeSeriesData" / "29hhw_system_data.csv"

# Qualify
qualified, details = app.qualify(str(model))

if not qualified:
    print("Building does not qualify")
    exit(1)

print(f"✓ Building qualified")

# Configure
config = app.load_config()
config["output"]["output_dir"] = "./results/building_29"

# Analyze
results = app.analyze(str(model), str(data), config)

if results:
    print(f"\n✅ Analysis complete!")
    print(f"  Mean: {results['stats']['mean_temp_diff']:.2f}°C")
    print(f"  Output: {config['output']['output_dir']}")
```

---

## 5. Deployment Checklist

Before sharing:

- [x] All 5 files present and complete
- [x] `__init__.py` has correct metadata
- [x] `README.md` has usage examples
- [x] All tests pass
- [x] Works with AppsManager
- [x] Example usage provided
- [x] Error messages are clear

---

## 6. Sharing Your App

### Option 1: Contribute to HHW Brick

```bash
cd HHW_brick
git checkout -b feature/my-first-app
git add hhw_brick/applications/my_first_app/
git commit -m "Add my_first_app application"
git push origin feature/my-first-app
# Then create Pull Request on GitHub
```

### Option 2: Standalone Package

Create `setup.py`:

```python
from setuptools import setup, find_packages

setup(
    name="my-first-app",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "hhw-brick>=0.1.0",
        "pandas>=1.3.0",
        "matplotlib>=3.5.0",
        "plotly>=5.0.0",
    ]
)
```

---

## 🎉 Congratulations!

You've completed the Application Development Guide!

### What You Built

✅ **Complete Application**
- Building qualification
- Data processing
- Statistical analysis
- Matplotlib plots (4 types)
- Plotly HTML (4 interactive)
- Results export

✅ **Professional Package**
- Proper structure
- Comprehensive tests
- Complete documentation
- Framework integration

✅ **Portable & Reusable**
- Works on any qualified building
- Configurable parameters
- Easy to extend

---

## Next Steps

**Enhance**:
- Add more analysis metrics
- Implement advanced SPARQL
- Create custom visualizations

**Learn More**:
- Study: `secondary_loop_temp_diff`, `primary_loop_temp_diff`
- Explore: https://docs.brickschema.org/
- Learn SPARQL: https://www.w3.org/TR/sparql11-query/

**Contribute**:
- Share your app
- Help improve docs
- Report bugs

---

## Resources

- HHW Brick: https://github.com/CenterForTheBuiltEnvironment/HHW_brick
- Brick Schema: https://brickschema.org/
- SPARQL: https://www.w3.org/TR/sparql11-query/
- Plotly: https://plotly.com/python/

---

**Thank you for building with HHW Brick!** 🚀


In this final step, you'll learn how to deploy your application and integrate it with the HHW Brick framework.

## Goal of This Step

- Register your app with AppsManager
- Create proper documentation
- Share your application
- Best practices for maintenance

---

## Step 9.1: Verify App Structure

Ensure your application has all required files:

```
hhw_brick/applications/my_first_app/
├── __init__.py          ✅ Package metadata
├── app.py               ✅ Main application code
├── config.yaml          ✅ Default configuration
├── requirements.txt     ✅ Dependencies
└── README.md            ✅ Documentation
```

---

## Step 9.2: Update __init__.py

Ensure your `__init__.py` is complete:

```python
"""
My First Application

Temperature differential analysis for hot water systems.

Author: Your Name
"""

from .app import qualify, analyze, load_config

__all__ = ["qualify", "analyze", "load_config"]

# Application metadata
__app_name__ = "my_first_app"
__version__ = "1.0.0"
__description__ = "Temperature differential analysis"
__author__ = "Your Name"
__email__ = "your.email@example.com"
```

---

## Step 9.3: Complete README.md

Create comprehensive user documentation:

```markdown
# My First Application

## Overview

Analyzes temperature differential between supply and return water in hot water systems.

## Features

- ✅ Automatic sensor discovery using SPARQL
- ✅ Statistical analysis (mean, std, min, max)
- ✅ Anomaly detection
- ✅ Matplotlib visualizations (PNG/PDF/SVG)
- ✅ Interactive Plotly HTML dashboards

## Requirements

Buildings must have:
- Hot Water Loop (primary or secondary)
- Supply temperature sensor (Leaving_Hot_Water_Temperature_Sensor)
- Return temperature sensor (Entering_Hot_Water_Temperature_Sensor)

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

### Method 1: Through AppsManager

```python
from hhw_brick import apps

# Load application
app = apps.load_app("my_first_app")

# Check if building qualifies
qualified, details = app.qualify("building.ttl")

if qualified:
    # Load and customize config
    config = apps.get_default_config("my_first_app")
    config["output"]["output_dir"] = "./my_results"

    # Run analysis
    results = app.analyze("building.ttl", "data.csv", config)
```

### Method 2: Command Line

```bash
python -m hhw_brick.applications.my_first_app.app \
    building.ttl \
    timeseries.csv \
    --output-dir ./results
```

## Configuration

Edit `config.yaml` or pass custom configuration:

```yaml
analysis:
  threshold_min_delta: 0.5   # Minimum expected differential
  threshold_max_delta: 10.0  # Maximum expected differential

output:
  save_results: true
  output_dir: "./results"
  export_format: "csv"       # csv or json
  generate_plots: true
  plot_format: "png"         # png, pdf, or svg
  generate_plotly_html: true

time_range:
  start_time: null           # YYYY-MM-DD or null
  end_time: null             # YYYY-MM-DD or null
```

## Output

The application generates:

**Data Files**:
- `stats.csv` - Statistical summary
- `timeseries.csv` - Processed time-series data

**Matplotlib Plots** (if enabled):
- `timeseries.png` - Supply, return, and differential
- `distribution.png` - Histogram with statistics
- `heatmap.png` - Hourly/weekday patterns
- `hourly_pattern.png` - Average by hour

**Plotly HTML** (if enabled):
- `dashboard_interactive.html` - 6-panel dashboard
- `timeseries_interactive.html` - Detailed time-series
- `heatmap_interactive.html` - Pattern analysis
- `boxplot_interactive.html` - Distribution

## Examples

See `tests/test_app.py` for example usage.

## Troubleshooting

**Building not qualified**:
- Check if Brick model has required sensors
- Verify sensor types match expected classes
- Ensure sensors are properly linked to loop

**No data after analysis**:
- Check time range in config
- Verify sensor names match data columns
- Check for missing data (NaN values)

**Plots not generated**:
- Ensure output directory is writable
- Check matplotlib/plotly are installed
- Verify `generate_plots` is true in config

## Version History

- **1.0.0** (2025-01-04): Initial release

## Author

Your Name (your.email@example.com)

## License

MIT License
```

---

## Step 9.4: Test with AppsManager

Verify your app works with the framework:

```python
"""Test app integration"""
from hhw_brick import apps

# 1. List all apps
all_apps = apps.list_apps()
print(f"Available apps: {[app['name'] for app in all_apps]}")

# 2. Get app info
info = apps.get_app_info("my_first_app")
print(f"App: {info['name']}")
print(f"Functions: {[f['name'] for f in info['functions']]}")

# 3. Load app
app = apps.load_app("my_first_app")
print(f"Loaded: {app.__name__}")

# 4. Get default config
config = apps.get_default_config("my_first_app")
print(f"Config sections: {list(config.keys())}")
```

**Expected output**:
```
Available apps: ['my_first_app', 'secondary_loop_temp_diff', 'primary_loop_temp_diff']
App: my_first_app
Functions: ['qualify', 'analyze', 'load_config']
Loaded: hhw_brick.applications.my_first_app.app
Config sections: ['analysis', 'output', 'time_range']
```

---

## Step 9.5: Create Usage Examples

Add example scripts to help users:

**Create `examples/run_my_app.py`**:

```python
"""
Example: Run my_first_app on a single building
"""
from pathlib import Path
from hhw_brick import apps

# Configuration
BUILDING_NUMBER = 29
fixtures = Path("tests/fixtures")

# Paths
brick_model = fixtures / "Brick_Model_File" / f"building_{BUILDING_NUMBER}.ttl"
timeseries = fixtures / "TimeSeriesData" / f"{BUILDING_NUMBER}hhw_system_data.csv"

# Load application
print(f"Loading application: my_first_app")
app = apps.load_app("my_first_app")

# Step 1: Qualify
print(f"\nStep 1: Checking if building {BUILDING_NUMBER} qualifies...")
qualified, details = app.qualify(str(brick_model))

if not qualified:
    print(f"❌ Building {BUILDING_NUMBER} does not qualify")
    exit(1)

print(f"✅ Building {BUILDING_NUMBER} qualifies!")

# Step 2: Configure
print(f"\nStep 2: Loading configuration...")
config = apps.get_default_config("my_first_app")
config["output"]["output_dir"] = f"./results/building_{BUILDING_NUMBER}"
print(f"✅ Configuration loaded")

# Step 3: Analyze
print(f"\nStep 3: Running analysis...")
results = app.analyze(str(brick_model), str(timeseries), config)

if results:
    print(f"\n✅ Analysis complete!")
    print(f"  Data points: {results['stats']['count']}")
    print(f"  Mean temp diff: {results['stats']['mean_temp_diff']:.2f}°C")
    print(f"  Output: {config['output']['output_dir']}")
else:
    print(f"\n❌ Analysis failed")
```

---

## Step 9.6: Optional: Add to Git

If contributing to HHW Brick:

```bash
cd HHW_brick
git add hhw_brick/applications/my_first_app/
git commit -m "Add my_first_app application"
git push origin feature/my-first-app
```

---

## Step 9.7: Share Your Application

### Option 1: Contribute to HHW Brick

1. Fork the repository
2. Create a feature branch
3. Add your application
4. Submit a pull request

### Option 2: Standalone Package

Create your own package:

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="my-first-app",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "hhw-brick>=0.1.0",
        "pandas>=1.3.0",
        "matplotlib>=3.5.0",
        "plotly>=5.0.0",
    ],
    entry_points={
        "hhw_brick.applications": [
            "my_first_app = my_first_app:__all__"
        ]
    }
)
```

---

## Step 9.8: Maintenance

### Version Updates

When updating your app:

1. Update version in `__init__.py`
2. Update README.md with changelog
3. Test thoroughly
4. Update documentation if API changes

### Bug Fixes

1. Create issue describing bug
2. Write test that reproduces bug
3. Fix the bug
4. Verify test passes
5. Update version (patch number)

---

## Deployment Checklist

Before releasing your application:

- [ ] All files present (`__init__.py`, `app.py`, `config.yaml`, `requirements.txt`, `README.md`)
- [ ] Metadata complete in `__init__.py`
- [ ] README.md has usage examples
- [ ] All tests pass
- [ ] App works with AppsManager
- [ ] Default config is sensible
- [ ] Example scripts provided
- [ ] Error messages are clear
- [ ] Documentation is accurate

---

## Congratulations! 🎉

You've completed the Application Development Guide!

### What You've Built

✅ **Complete Analytics Application**
- Qualify buildings based on sensors
- Load and process data
- Calculate statistics
- Detect anomalies
- Generate visualizations (matplotlib + Plotly)
- Save results

✅ **Professional Package**
- Proper structure
- Comprehensive tests
- Complete documentation
- Framework integration

✅ **Reusable and Portable**
- Works on any qualified building
- Configurable parameters
- Easy to extend

---

## Next Steps

### Enhance Your Application

- Add more analysis metrics
- Implement advanced SPARQL queries
- Create custom visualizations
- Add machine learning features

### Learn More

- Study existing apps: `secondary_loop_temp_diff`, `primary_loop_temp_diff`
- Explore Brick Schema: https://docs.brickschema.org/
- Learn advanced SPARQL: https://www.w3.org/TR/sparql11-query/

### Contribute

- Share your application with the community
- Help improve documentation
- Report bugs and suggest features

---

## Resources

- **HHW Brick GitHub**: https://github.com/CenterForTheBuiltEnvironment/HHW_brick
- **Brick Schema**: https://brickschema.org/
- **SPARQL Tutorial**: https://www.w3.org/TR/sparql11-query/
- **Plotly Python**: https://plotly.com/python/

---

**Thank you for building with HHW Brick!** 🚀

Have questions? Open an issue on GitHub or start a discussion.

Happy coding! 👨‍💻👩‍💻
