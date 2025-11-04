# Application Development Tutorial - Step 1: Create Application Structure

This tutorial will guide you through creating your first HHW Brick analytics application step by step.

## Goal of This Step

Create the basic file structure and framework code for your application.

---

## Step 1.1: Create Application Directory

First, create your application folder under `hhw_brick/applications/`.

```bash
# Navigate to applications directory
cd hhw_brick/applications/

# Create new application folder (use your app name)
mkdir my_first_app
cd my_first_app
```

**Naming Rules**:
- Use lowercase letters
- Separate words with underscores
- Use descriptive names
- Examples: `temperature_analysis`, `energy_consumption`, `fault_detection`

---

## Step 1.2: Create Required Files

Create these 5 files in your application folder:

```
my_first_app/
├── __init__.py
├── app.py
├── config.yaml
├── requirements.txt
└── README.md
```

**Create empty files** (Windows PowerShell):
```powershell
New-Item __init__.py
New-Item app.py
New-Item config.yaml
New-Item requirements.txt
New-Item README.md
```

**Create empty files** (Linux/Mac):
```bash
touch __init__.py app.py config.yaml requirements.txt README.md
```

---

## Step 1.3: Write `__init__.py`

This file defines your application's metadata and exports core functions.

**Copy the following code into `__init__.py`**:

```python
"""
My First Application

This is an example application for learning how to create HHW Brick analytics apps.

Author: Your Name
"""

from .app import qualify, analyze, load_config

# Export core functions (required)
__all__ = ["qualify", "analyze", "load_config"]

# Application metadata
__app_name__ = "my_first_app"
__version__ = "1.0.0"
__description__ = "My First HHW Brick Application"
__author__ = "Your Name"
```

**Key Points**:
- ✅ `from .app import ...` - Import three core functions from app.py
- ✅ `__all__` - Define the public API
- ✅ Metadata variables - Provide application information

---

## Step 1.4: Write `requirements.txt`

List the Python packages your application needs.

**Copy the following into `requirements.txt`**:

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

**Notes**:
- These are standard dependencies most apps need
- `>=` specifies minimum version requirements
- Add other packages if your app needs them

---

## Step 1.5: Create Basic `config.yaml`

The configuration file stores your application's default settings.

**Copy the following into `config.yaml`**:

```yaml
# My First Application - Configuration File

# Analysis parameters
analysis:
  # Add your app-specific parameters here
  # For example:
  # threshold: 5.0
  # window_size: 10

# Output settings (required, do not modify key names)
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

  # Whether to generate interactive Plotly HTML
  generate_plotly_html: true

# Time range (optional)
time_range:
  # Start time in YYYY-MM-DD format (null = use all data)
  start_time: null

  # End time in YYYY-MM-DD format (null = use all data)
  end_time: null
```

**Key Points**:
- ✅ `analysis` section: Your custom parameters
- ✅ `output` section: Standard output settings (required)
- ✅ `time_range` section: Optional time filtering

---

## Step 1.6: Create Basic `README.md`

Documentation file describing your application.

**Copy the following template into `README.md`**:

```markdown
# My First Application

## Overview

This application is used for... (describe your app's functionality)

## Features

- ✅ Feature 1
- ✅ Feature 2
- ✅ Feature 3

## Requirements

The building must have the following sensors:
- Sensor Type 1 (e.g., Temperature Sensor)
- Sensor Type 2 (e.g., Flow Sensor)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Method 1: Via AppsManager

```python
from hhw_brick import apps

# Load application
app = apps.load_app("my_first_app")

# Check if building qualifies
qualified, details = app.qualify("path/to/brick_model.ttl")

# If qualified, run analysis
if qualified:
    config = app.load_config()
    results = app.analyze("path/to/brick_model.ttl", "path/to/data.csv", config)
```

### Method 2: Command Line

```bash
python -m hhw_brick.applications.my_first_app.app \
    brick_model.ttl \
    timeseries.csv \
    --output-dir ./my_results
```

## Output

The application generates the following files:
- `stats.csv` - Statistical results
- `timeseries.csv` - Processed time-series data
- `*.png` - Visualization charts
- `*.html` - Interactive visualizations

## Configuration

Customize application behavior by modifying `config.yaml` or passing custom configuration.

## Author

Your Name

## Version

1.0.0
```

---

## Step 1.7: Verify File Structure

Confirm your file structure looks like this:

```
hhw_brick/applications/
└── my_first_app/
    ├── __init__.py          ✅ Created
    ├── app.py               ⏳ Create in next step
    ├── config.yaml          ✅ Created
    ├── requirements.txt     ✅ Created
    └── README.md            ✅ Created
```

---

## Checkpoint

Before proceeding, ensure:

- [x] Created application directory `my_first_app/`
- [x] Created 5 required files
- [x] `__init__.py` contains metadata and import statements
- [x] `requirements.txt` lists dependencies
- [x] `config.yaml` has correct structure
- [x] `README.md` contains basic documentation

---

## Next Steps

✅ File structure complete!

👉 Continue to [Step 2: Write load_config Function](./step-02-load-config.md)

---

## FAQ

**Q: Can I use Chinese characters in the app name?**  
A: Not recommended. App names should be valid Python module names using English and underscores.

**Q: Must I create all 5 files?**  
A: `__init__.py`, `app.py`, `config.yaml`, `requirements.txt` are required. `README.md` is strongly recommended but not mandatory.

**Q: Can I add other files?**  
A: Yes! You can add test files, helper modules, etc. But these 5 are the core files.

**Q: Must the config file be named config.yaml?**  
A: Yes, this is the conventional name. The application will look for `config.yaml` in its own directory.
