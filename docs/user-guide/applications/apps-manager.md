# Apps Manager

Detailed guide to the Apps Manager API for discovering and managing analytics applications.

## Overview

The Apps Manager (`apps`) provides a simple interface to:

- **Discover** available applications
- **Load** applications dynamically
- **Get information** about applications
- **Manage configurations**
- **Batch qualify** buildings

## Importing Apps Manager

```python
from hhw_brick import apps
```

The `apps` object is a singleton instance of `AppsManager` that provides all functionality.

## Core Functions

### list_apps()

List all available analytics applications.

**Signature:**
```python
def list_apps() -> List[Dict[str, str]]
```

**Returns:**
```python
[
    {
        'name': 'secondary_loop_temp_diff',
        'description': 'Analyzes temperature difference in secondary hot water loop',
        'path': '/path/to/app'
    },
    # ... more apps
]
```

**Example:**
```python
from hhw_brick import apps

# List all apps
available = apps.list_apps()

print(f"Found {len(available)} applications:")
for app in available:
    print(f"  • {app['name']}")
    print(f"    {app['description']}")
```

**Output:**
```
Found 2 applications:
  • secondary_loop_temp_diff
    Analyzes temperature difference in secondary hot water loop
  • primary_loop_temp_diff
    Analyzes temperature difference in primary hot water loop
```

### load_app()

Load an application by name.

**Signature:**
```python
def load_app(app_name: str) -> Module
```

**Parameters:**
- `app_name` (str): Name of the application (e.g., "secondary_loop_temp_diff")

**Returns:**
- App module with `qualify()`, `analyze()`, and `load_config()` functions

**Example:**
```python
# Load application
app = apps.load_app("secondary_loop_temp_diff")

# Now you can use app functions
qualified, details = app.qualify("building_105.ttl")
```

**Raises:**
- `ImportError`: If app not found or cannot be loaded

```python
try:
    app = apps.load_app("non_existent_app")
except ImportError as e:
    print(f"Error: {e}")
```

### get_app_info()

Get detailed information about an application.

**Signature:**
```python
def get_app_info(app_name: str) -> Dict[str, Any]
```

**Returns:**
```python
{
    'name': 'secondary_loop_temp_diff',
    'description': 'Analyzes temperature difference in secondary hot water loop',
    'functions': [
        {'name': 'qualify', 'signature': '...'},
        {'name': 'analyze', 'signature': '...'},
        {'name': 'load_config', 'signature': '...'}
    ]
}
```

**Example:**
```python
info = apps.get_app_info("secondary_loop_temp_diff")

print(f"App: {info['name']}")
print(f"Description: {info['description']}")
print(f"Functions:")
for func in info['functions']:
    print(f"  - {func['name']}")
```

### get_default_config()

Get default configuration template for an application.

**Signature:**
```python
def get_default_config(app_name: str) -> Dict[str, Any]
```

**Returns:**
```python
{
    'analysis': {
        'threshold_min_delta': 0.5,
        'threshold_max_delta': 10.0
    },
    'output': {
        'save_results': True,
        'output_dir': './results',
        'generate_plots': True
    }
}
```

**Example:**
```python
# Get default config
config = apps.get_default_config("secondary_loop_temp_diff")

# Customize
config['output']['output_dir'] = './my_results'
config['analysis']['threshold_min_delta'] = 1.0

# Use it
results = app.analyze(model_path, data_path, config)
```

## Batch Operations

### qualify_building()

Qualify a single building against all available applications.

**Signature:**
```python
def qualify_building(model_path: str, verbose: bool = True) -> Dict
```

**Parameters:**
- `model_path` (str): Path to Brick model file
- `verbose` (bool): Print detailed output (default: True)

**Returns:**
```python
{
    'model': 'building_105.ttl',
    'results': [
        {
            'app': 'secondary_loop_temp_diff',
            'qualified': True,
            'details': {...}
        },
        {
            'app': 'primary_loop_temp_diff',
            'qualified': False,
            'details': {...}
        }
    ]
}
```

**Example:**
```python
from hhw_brick import apps

# Qualify one building
result = apps.qualify_building("building_105.ttl")

print(f"Building: {result['model']}")
for r in result['results']:
    status = "✓" if r['qualified'] else "✗"
    print(f"  {status} {r['app']}")
```

**With verbose=False:**
```python
# Silent qualification (no print output)
result = apps.qualify_building("building_105.ttl", verbose=False)

# Process results programmatically
qualified_apps = [
    r['app'] for r in result['results'] if r['qualified']
]
print(f"Qualified for: {', '.join(qualified_apps)}")
```

### qualify_buildings()

Qualify multiple buildings against all applications.

**Signature:**
```python
def qualify_buildings(model_dir: str, verbose: bool = False) -> List[Dict]
```

**Parameters:**
- `model_dir` (str): Directory containing Brick model files
- `verbose` (bool): Print progress (default: False)

**Returns:**
```python
[
    {
        'model': 'building_105.ttl',
        'results': [
            {'app': 'secondary_loop_temp_diff', 'qualified': True, 'details': {...}},
            {'app': 'primary_loop_temp_diff', 'qualified': False, 'details': {...}}
        ]
    },
    # ... more buildings
]
```

**Example:**
```python
from hhw_brick import apps
from pathlib import Path

# Batch qualify
batch_results = apps.qualify_buildings("brick_models/")

# Analyze results
for building in batch_results:
    building_name = Path(building['model']).stem
    qualified_apps = [
        r['app'] for r in building['results'] if r['qualified']
    ]
    
    if qualified_apps:
        print(f"{building_name}: {', '.join(qualified_apps)}")
    else:
        print(f"{building_name}: No apps available")
```

## Advanced Usage

### Building Qualification Matrix

Create a comprehensive view of which buildings qualify for which apps:

```python
"""
Build a qualification matrix
"""
from hhw_brick import apps
from pathlib import Path

def build_qualification_matrix(model_dir):
    """Build matrix of buildings vs applications."""
    
    # Batch qualify
    batch_results = apps.qualify_buildings(model_dir)
    
    # Initialize matrices
    app_to_buildings = {}  # app -> [buildings]
    building_to_apps = {}  # building -> [apps]
    
    # Process results
    for building in batch_results:
        building_name = Path(building['model']).stem
        building_to_apps[building_name] = []
        
        for result in building['results']:
            app_name = result['app']
            
            # Initialize app entry
            if app_name not in app_to_buildings:
                app_to_buildings[app_name] = []
            
            # Record qualification
            if result['qualified']:
                app_to_buildings[app_name].append(building_name)
                building_to_apps[building_name].append(app_name)
    
    return {
        'by_app': app_to_buildings,
        'by_building': building_to_apps,
        'total_buildings': len(batch_results)
    }

# Use it
matrix = build_qualification_matrix("brick_models/")

# Display by application
print("Qualification by Application:")
for app_name, buildings in matrix['by_app'].items():
    pct = len(buildings) / matrix['total_buildings'] * 100
    print(f"  {app_name}:")
    print(f"    {len(buildings)}/{matrix['total_buildings']} ({pct:.1f}%)")

# Display by building
print("\nQualification by Building:")
for building, apps_list in matrix['by_building'].items():
    if apps_list:
        print(f"  {building}: {', '.join(apps_list)}")
```

### Export Qualification Results

Save qualification results to CSV:

```python
"""
Export qualification matrix to CSV
"""
import pandas as pd
from hhw_brick import apps

def export_qualification_matrix(model_dir, output_csv):
    """Export qualification results to CSV."""
    
    batch_results = apps.qualify_buildings(model_dir)
    
    # Flatten results for CSV
    rows = []
    for building in batch_results:
        building_name = Path(building['model']).stem
        
        for result in building['results']:
            rows.append({
                'building': building_name,
                'application': result['app'],
                'qualified': result['qualified']
            })
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    
    # Pivot for matrix view
    matrix = df.pivot(
        index='building',
        columns='application',
        values='qualified'
    )
    
    # Save
    matrix.to_csv(output_csv)
    print(f"Saved qualification matrix to: {output_csv}")
    
    # Summary
    print(f"\nSummary:")
    for app in matrix.columns:
        qualified_count = matrix[app].sum()
        total = len(matrix)
        print(f"  {app}: {qualified_count}/{total} buildings")
    
    return matrix

# Use it
matrix = export_qualification_matrix(
    "brick_models/",
    "qualification_matrix.csv"
)
```

### Dynamic App Loading

Load apps dynamically based on conditions:

```python
"""
Dynamically select and load apps
"""
from hhw_brick import apps

def select_app_for_building(model_path, preferred_apps=None):
    """
    Select best app for a building.
    
    Args:
        model_path: Path to Brick model
        preferred_apps: List of preferred app names (in priority order)
    
    Returns:
        Tuple of (app_module, app_name) or (None, None)
    """
    # Get all available apps
    available = apps.list_apps()
    
    # Set default preference
    if preferred_apps is None:
        preferred_apps = [a['name'] for a in available]
    
    # Try apps in order of preference
    for app_name in preferred_apps:
        try:
            app = apps.load_app(app_name)
            qualified, details = app.qualify(model_path)
            
            if qualified:
                return app, app_name
        except Exception as e:
            print(f"Error loading {app_name}: {e}")
            continue
    
    return None, None

# Use it
model_path = "building_105.ttl"
preferred = ["secondary_loop_temp_diff", "primary_loop_temp_diff"]

app, app_name = select_app_for_building(model_path, preferred)

if app:
    print(f"Selected: {app_name}")
    # Run analysis
    config = apps.get_default_config(app_name)
    results = app.analyze(model_path, data_path, config)
else:
    print("No suitable app found")
```

## Configuration Management

### Load Configuration from File

```python
import yaml

# Create config file
config = apps.get_default_config("secondary_loop_temp_diff")
with open('my_config.yaml', 'w') as f:
    yaml.dump(config, f)

# Load and use
with open('my_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

results = app.analyze(model_path, data_path, config)
```

### Configuration Templates

```python
"""
Create configuration templates for all apps
"""
from hhw_brick import apps
import yaml
from pathlib import Path

def create_config_templates(output_dir):
    """Create config templates for all apps."""
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    available = apps.list_apps()
    
    for app_info in available:
        app_name = app_info['name']
        config = apps.get_default_config(app_name)
        
        config_file = output_path / f"{app_name}_config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print(f"Created: {config_file}")

# Use it
create_config_templates("config_templates/")
```

## Error Handling

### Handle Missing Apps

```python
from hhw_brick import apps

app_name = "my_custom_app"

try:
    app = apps.load_app(app_name)
except ImportError:
    print(f"App '{app_name}' not found")
    print("Available apps:")
    for a in apps.list_apps():
        print(f"  - {a['name']}")
```

### Handle Qualification Failures

```python
app = apps.load_app("secondary_loop_temp_diff")
qualified, details = app.qualify("building_105.ttl")

if not qualified:
    print("Building not qualified")
    
    # Check details for reason
    if 'reason' in details:
        print(f"Reason: {details['reason']}")
    
    if 'missing' in details:
        print(f"Missing: {details['missing']}")
```

## Best Practices

### 1. Check Available Apps First

```python
# Good ✓
available = apps.list_apps()
if available:
    app = apps.load_app(available[0]['name'])

# Bad ✗
app = apps.load_app("some_app")  # Might not exist
```

### 2. Always Qualify Before Analyzing

```python
# Good ✓
qualified, details = app.qualify(model_path)
if qualified:
    results = app.analyze(model_path, data_path, config)

# Bad ✗
results = app.analyze(model_path, data_path, config)  # Might fail
```

### 3. Use Configuration Files

```python
# Good ✓ - Maintainable
config = yaml.safe_load(open('config.yaml'))

# Bad ✗ - Hard-coded
config = {'output': {'output_dir': './results'}}
```

### 4. Handle Errors Gracefully

```python
# Good ✓
try:
    app = apps.load_app(app_name)
    qualified, details = app.qualify(model_path)
    if qualified:
        results = app.analyze(model_path, data_path, config)
except ImportError:
    print(f"App not found: {app_name}")
except FileNotFoundError:
    print(f"File not found")
except Exception as e:
    print(f"Error: {e}")
```

## API Reference Summary

| Function | Purpose | Returns |
|----------|---------|---------|
| `list_apps()` | List all applications | List of app info dicts |
| `load_app(name)` | Load an application | App module |
| `get_app_info(name)` | Get app details | Info dict |
| `get_default_config(name)` | Get default config | Config dict |
| `qualify_building(path)` | Qualify one building | Qualification result |
| `qualify_buildings(dir)` | Qualify multiple buildings | List of results |

## Next Steps

- **[Secondary Loop App](secondary-loop.md)** - Learn about temperature difference analysis
- **[Running Apps](running-apps.md)** - Complete guide to running applications
- **[Developer Guide](../../developer-guide/creating-apps/index.md)** - Create your own apps

---

**Continue to:** [Secondary Loop Temperature Difference](secondary-loop.md) →

