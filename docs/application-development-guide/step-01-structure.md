# Step 1: Create Application Structure

Set up the basic file structure for your application.

---

## 1. Create Directory

```bash
cd hhw_brick/applications/
mkdir my_first_app
cd my_first_app
```

**Naming**: Use lowercase with underscores (e.g., `temperature_analysis`)

---

## 2. Create Required Files

Every application needs these 5 files:

```
my_first_app/
├── __init__.py          # Package metadata and exports
├── app.py               # Main application code
├── config.yaml          # Default configuration
├── requirements.txt     # Python dependencies
└── README.md            # User documentation
```

**Windows**:
```powershell
New-Item __init__.py, app.py, config.yaml, requirements.txt, README.md
```

**Linux/Mac**:
```bash
touch __init__.py app.py config.yaml requirements.txt README.md
```

---

## 3. File Contents

### `__init__.py`

Exports the three required functions and defines metadata.

```python
"""
My First Application

Temperature differential analysis for hot water systems.

Author: Your Name
"""

from .app import qualify, analyze, load_config

__all__ = ["qualify", "analyze", "load_config"]

__app_name__ = "my_first_app"
__version__ = "1.0.0"
__description__ = "Temperature differential analysis"
__author__ = "Your Name"
```

---

### `requirements.txt`

Lists all Python packages your app needs.

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

### `config.yaml`

Default configuration that users can customize.

```yaml
# Analysis parameters (customize for your app)
analysis:
  threshold_min_delta: 0.5
  threshold_max_delta: 10.0

# Output settings (standard, keep structure)
output:
  save_results: true
  output_dir: "./results"
  export_format: "csv"           # csv or json
  generate_plots: true
  plot_format: "png"             # png, pdf, or svg
  generate_plotly_html: true

# Time filtering (optional)
time_range:
  start_time: null               # YYYY-MM-DD or null
  end_time: null
```

---

### `README.md`

User-facing documentation for your application.

```markdown
# My First Application

## Overview

Analyzes temperature differential in hot water systems.

## Requirements

Buildings must have:
- Hot Water Loop
- Supply temperature sensor (Leaving_Hot_Water_Temperature_Sensor)
- Return temperature sensor (Entering_Hot_Water_Temperature_Sensor)

## Usage

\`\`\`python
from hhw_brick import apps

app = apps.load_app("my_first_app")
qualified, details = app.qualify("building.ttl")

if qualified:
    config = app.load_config()
    results = app.analyze("building.ttl", "data.csv", config)
\`\`\`

## Output

- `stats.csv` - Statistical results
- `timeseries.csv` - Processed data
- `*.png` - Static plots
- `*.html` - Interactive visualizations

## Author

Your Name - v1.0.0
```

---

## Checkpoint

Verify your setup:

- [x] Directory `my_first_app/` created
- [x] All 5 files created
- [x] `__init__.py` has metadata
- [x] `requirements.txt` has dependencies
- [x] `config.yaml` has correct structure
- [x] `README.md` has basic docs

---

## Next Step

👉 [Step 2: Write load_config Function](./step-02-load-config.md)
