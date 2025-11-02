# Running Applications

Complete guide to running analytics applications on building data.

## Overview

This guide covers the complete workflow for running applications, including:

- **Preparation** - Setting up data and models
- **Qualification** - Checking building compatibility
- **Configuration** - Customizing analysis parameters
- **Execution** - Running the analysis
- **Results** - Understanding and using outputs

## Complete Workflow

### End-to-End Example

Based on `examples/07_run_application.py`:

```python
"""
Complete workflow: Convert → Validate → Analyze
"""

from pathlib import Path
from hhw_brick import (
    CSVToBrickConverter,
    BrickModelValidator,
    apps
)
import yaml

def complete_workflow(building_id):
    """Complete workflow from CSV to analysis results."""
    
    # ===== Step 1: Convert CSV to Brick =====
    print("Step 1: Convert CSV to Brick")
    print("="*60)
    
    converter = CSVToBrickConverter()
    model_file = f"building_{building_id}.ttl"
    
    converter.convert_to_brick(
        metadata_csv="metadata.csv",
        vars_csv="vars.csv",
        building_tag=building_id,
        output_path=model_file
    )
    print(f"✓ Created Brick model: {model_file}\n")
    
    # ===== Step 2: Validate Model =====
    print("Step 2: Validate Model")
    print("="*60)
    
    validator = BrickModelValidator(use_local_brick=True)
    is_valid = validator.validate_ontology(model_file)['valid']
    
    if not is_valid:
        print("✗ Model validation failed\n")
        return None
    
    print(f"✓ Model is valid\n")
    
    # ===== Step 3: Discover Available Apps =====
    print("Step 3: Discover Available Apps")
    print("="*60)
    
    available_apps = apps.list_apps()
    print(f"Found {len(available_apps)} applications:")
    for app_info in available_apps:
        print(f"  • {app_info['name']}")
    print()
    
    # ===== Step 4: Qualify Building =====
    print("Step 4: Qualify Building")
    print("="*60)
    
    result = apps.qualify_building(model_file, verbose=False)
    
    qualified_apps = [
        r['app'] for r in result['results'] if r['qualified']
    ]
    
    if not qualified_apps:
        print(f"✗ Building {building_id} not qualified for any apps\n")
        return None
    
    print(f"✓ Qualified for: {', '.join(qualified_apps)}\n")
    
    # ===== Step 5: Run Analysis =====
    print("Step 5: Run Analysis")
    print("="*60)
    
    app_name = qualified_apps[0]  # Use first qualified app
    app = apps.load_app(app_name)
    
    # Load config
    config = apps.get_default_config(app_name)
    config['output']['output_dir'] = f"./results/building_{building_id}"
    
    # Run analysis
    data_file = f"{building_id}_data.csv"
    results = app.analyze(model_file, data_file, config)
    
    print(f"✓ Analysis complete: {app_name}")
    print(f"\nSummary:")
    for key, value in results['summary'].items():
        print(f"  {key}: {value}")
    
    print(f"\nOutputs:")
    for output in results['outputs']:
        print(f"  - {output}")
    
    return results

# Run it
if __name__ == "__main__":
    results = complete_workflow("105")
```

## Preparation

### Required Files

Before running an application, prepare:

| File | Description | Example |
|------|-------------|---------|
| **Brick Model** | TTL file with building model | `building_105.ttl` |
| **Timeseries Data** | CSV with sensor data | `105_data.csv` |
| **Configuration** (optional) | YAML with analysis settings | `config.yaml` |

### Data File Requirements

**Timeseries CSV format:**

```csv
datetime,secondary_supply_temp,secondary_return_temp,flow_rate
2024-01-01 00:00:00,70.5,65.3,150.2
2024-01-01 01:00:00,71.2,66.1,155.8
2024-01-01 02:00:00,69.8,64.7,148.3
...
```

**Requirements:**
- ✓ `datetime` column (timestamp)
- ✓ Sensor data columns (names can vary)
- ✓ Numeric values
- ✓ No missing critical timestamps

### Verify Data Quality

```python
import pandas as pd

# Load data
df = pd.read_csv("105_data.csv", parse_dates=['datetime'])

# Check quality
print(f"Data points: {len(df)}")
print(f"Date range: {df['datetime'].min()} to {df['datetime'].max()}")
print(f"Columns: {df.columns.tolist()}")

# Check for missing values
missing = df.isnull().sum()
if missing.any():
    print("\nMissing values:")
    print(missing[missing > 0])
```

## Application Types

### Primary Loop Temperature Difference

Analyzes primary loop (boiler-side) temperature difference.

**Required Sensors:**
- Primary supply temperature
- Primary return temperature

**Use Cases:**
- Boiler efficiency monitoring
- Primary loop performance
- Heat exchanger effectiveness

**Quick Example:**
```python
app = apps.load_app("primary_loop_temp_diff")

# Qualify
qualified, details = app.qualify("building_105.ttl")

if qualified:
    # Get config
    config = apps.get_default_config("primary_loop_temp_diff")
    
    # Run
    results = app.analyze(
        "building_105.ttl",
        "105_data.csv",
        config
    )
    
    print(f"Primary loop temp diff: {results['summary']['mean_temp_diff']:.2f}°C")
```

**Similar to Secondary Loop:**

The primary loop app works identically to the secondary loop app, but:
- Looks for **primary** loop sensors (not secondary)
- Analyzes boiler-side temperatures
- Useful for boiler systems (not district systems)

See [Secondary Loop](secondary-loop.md) for detailed documentation - the workflow is the same.

### Secondary Loop Temperature Difference

See [Secondary Loop App](secondary-loop.md) for complete documentation.

## Batch Processing

### Run on Multiple Buildings

```python
"""
Batch process multiple buildings
"""
from pathlib import Path
from hhw_brick import apps

def batch_run_app(app_name, model_dir, data_dir, output_base):
    """Run app on all qualified buildings."""
    
    # Load app
    app = apps.load_app(app_name)
    base_config = apps.get_default_config(app_name)
    
    # Find models
    model_files = list(Path(model_dir).glob("*.ttl"))
    
    results_summary = []
    
    for model_file in model_files:
        building_id = model_file.stem.split('_')[1]
        
        # Qualify
        qualified, details = app.qualify(str(model_file))
        if not qualified:
            print(f"⊘ Building {building_id}: Not qualified")
            continue
        
        # Find data
        data_file = Path(data_dir) / f"{building_id}_data.csv"
        if not data_file.exists():
            print(f"⊘ Building {building_id}: Data file not found")
            continue
        
        # Configure
        config = base_config.copy()
        config['output']['output_dir'] = f"{output_base}/building_{building_id}"
        
        # Run
        try:
            results = app.analyze(str(model_file), str(data_file), config)
            
            results_summary.append({
                'building_id': building_id,
                'status': 'success',
                'mean_temp_diff': results['summary']['mean_temp_diff'],
                'data_points': results['summary']['data_points']
            })
            
            print(f"✓ Building {building_id}: {results['summary']['mean_temp_diff']:.2f}°C")
            
        except Exception as e:
            results_summary.append({
                'building_id': building_id,
                'status': 'failed',
                'error': str(e)
            })
            print(f"✗ Building {building_id}: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"Batch Analysis Summary - {app_name}")
    print(f"{'='*60}")
    
    successful = [r for r in results_summary if r['status'] == 'success']
    failed = [r for r in results_summary if r['status'] == 'failed']
    
    print(f"Total: {len(model_files)}")
    print(f"Analyzed: {len(successful)}")
    print(f"Failed: {len(failed)}")
    
    if successful:
        avg_temp_diff = sum(r['mean_temp_diff'] for r in successful) / len(successful)
        print(f"\nAverage temp diff: {avg_temp_diff:.2f}°C")
    
    return results_summary

# Use it
results = batch_run_app(
    app_name="secondary_loop_temp_diff",
    model_dir="brick_models/",
    data_dir="timeseries_data/",
    output_base="./results"
)
```

### Parallel Batch Processing

```python
"""
Run apps in parallel for faster processing
"""
from concurrent.futures import ProcessPoolExecutor, as_completed
from hhw_brick import apps

def analyze_one_building(args):
    """Analyze one building (for parallel processing)."""
    model_file, data_file, app_name, config = args
    
    try:
        app = apps.load_app(app_name)
        results = app.analyze(str(model_file), str(data_file), config)
        return {
            'building': model_file.stem,
            'status': 'success',
            'summary': results['summary']
        }
    except Exception as e:
        return {
            'building': model_file.stem,
            'status': 'failed',
            'error': str(e)
        }

def parallel_batch_run(app_name, model_dir, data_dir, max_workers=4):
    """Run app in parallel."""
    
    from pathlib import Path
    
    app = apps.load_app(app_name)
    config = apps.get_default_config(app_name)
    
    # Prepare tasks
    tasks = []
    for model_file in Path(model_dir).glob("*.ttl"):
        building_id = model_file.stem.split('_')[1]
        
        # Qualify
        qualified, _ = app.qualify(str(model_file))
        if not qualified:
            continue
        
        # Find data
        data_file = Path(data_dir) / f"{building_id}_data.csv"
        if not data_file.exists():
            continue
        
        # Configure
        bldg_config = config.copy()
        bldg_config['output']['output_dir'] = f"./results/building_{building_id}"
        
        tasks.append((model_file, data_file, app_name, bldg_config))
    
    # Execute in parallel
    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(analyze_one_building, task): task[0]
            for task in tasks
        }
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            
            status = "✓" if result['status'] == 'success' else "✗"
            print(f"{status} {result['building']}")
    
    return results

# Use it
results = parallel_batch_run(
    "secondary_loop_temp_diff",
    "brick_models/",
    "timeseries_data/",
    max_workers=8
)
```

## Configuration Management

### Configuration File Structure

```yaml
# app_config.yaml

analysis:
  # Analysis-specific parameters
  threshold_min_delta: 0.5
  threshold_max_delta: 10.0
  
output:
  # Output settings
  save_results: true
  output_dir: ./results
  export_format: csv
  generate_plots: true
  plot_format: png
  
time_range:
  # Optional time filtering
  start_time: "2024-01-01 00:00:00"
  end_time: "2024-12-31 23:59:59"
```

### Using Configuration Files

```python
import yaml

# Load config from file
with open('app_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Use it
results = app.analyze(model_path, data_path, config)
```

### Dynamic Configuration

```python
"""
Generate configs for different scenarios
"""

def create_seasonal_configs(base_config, year=2024):
    """Create configs for seasonal analysis."""
    
    seasons = {
        'winter': ('01-01', '03-31'),
        'spring': ('04-01', '06-30'),
        'summer': ('07-01', '09-30'),
        'fall': ('10-01', '12-31')
    }
    
    configs = {}
    for season, (start, end) in seasons.items():
        config = base_config.copy()
        config['time_range']['start_time'] = f"{year}-{start} 00:00:00"
        config['time_range']['end_time'] = f"{year}-{end} 23:59:59"
        config['output']['output_dir'] = f"./results/{season}_{year}"
        configs[season] = config
    
    return configs

# Use it
base = apps.get_default_config("secondary_loop_temp_diff")
seasonal_configs = create_seasonal_configs(base, 2024)

for season, config in seasonal_configs.items():
    results = app.analyze(model_path, data_path, config)
    print(f"{season}: {results['summary']['mean_temp_diff']:.2f}°C")
```

## Results Management

### Saving Results

```python
"""
Save and organize results
"""
import json
from datetime import datetime

def save_analysis_results(results, building_id, app_name, output_dir):
    """Save results with metadata."""
    
    from pathlib import Path
    import pandas as pd
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save summary as JSON
    summary_file = output_path / f"{building_id}_{app_name}_summary.json"
    summary_data = {
        'building_id': building_id,
        'app_name': app_name,
        'analysis_date': datetime.now().isoformat(),
        'summary': results['summary']
    }
    with open(summary_file, 'w') as f:
        json.dump(summary_data, f, indent=2)
    
    # Save detailed data as CSV
    if 'data' in results:
        data_file = output_path / f"{building_id}_{app_name}_data.csv"
        df = pd.DataFrame(results['data'])
        df.to_csv(data_file, index=False)
    
    print(f"Saved results to: {output_dir}")

# Use it
results = app.analyze(model_path, data_path, config)
save_analysis_results(results, "105", "secondary_loop_temp_diff", "./results")
```

### Aggregating Results

```python
"""
Aggregate results from multiple buildings
"""
import pandas as pd

def aggregate_building_results(results_dir):
    """Aggregate results from multiple analyses."""
    
    from pathlib import Path
    import json
    
    summary_files = Path(results_dir).rglob("*_summary.json")
    
    all_results = []
    for file in summary_files:
        with open(file, 'r') as f:
            data = json.load(f)
            all_results.append({
                'building_id': data['building_id'],
                'app': data['app_name'],
                **data['summary']
            })
    
    # Create DataFrame
    df = pd.DataFrame(all_results)
    
    # Calculate statistics
    print("Aggregated Results:")
    print(f"  Total buildings: {len(df)}")
    print(f"  Average temp diff: {df['mean_temp_diff'].mean():.2f}°C")
    print(f"  Min temp diff: {df['mean_temp_diff'].min():.2f}°C")
    print(f"  Max temp diff: {df['mean_temp_diff'].max():.2f}°C")
    
    # Save aggregate
    df.to_csv(Path(results_dir) / "aggregate_results.csv", index=False)
    
    return df

# Use it
aggregate_df = aggregate_building_results("./results")
```

## Error Handling

### Robust Execution

```python
"""
Production-ready application runner
"""
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_run_app(model_path, data_path, app_name, config):
    """Run app with comprehensive error handling."""
    
    from hhw_brick import apps
    
    try:
        # Load app
        app = apps.load_app(app_name)
        logger.info(f"Loaded app: {app_name}")
        
    except ImportError as e:
        logger.error(f"App not found: {app_name}")
        return None
    
    try:
        # Qualify
        qualified, details = app.qualify(model_path)
        
        if not qualified:
            logger.warning(f"Building not qualified for {app_name}")
            return None
        
        logger.info(f"Building qualified")
        
    except FileNotFoundError:
        logger.error(f"Model file not found: {model_path}")
        return None
    except Exception as e:
        logger.error(f"Qualification failed: {e}")
        return None
    
    try:
        # Analyze
        results = app.analyze(model_path, data_path, config)
        logger.info(f"Analysis complete")
        return results
        
    except FileNotFoundError:
        logger.error(f"Data file not found: {data_path}")
        return None
    except KeyError as e:
        logger.error(f"Missing data column: {e}")
        return None
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        return None

# Use it
results = safe_run_app(
    "building_105.ttl",
    "105_data.csv",
    "secondary_loop_temp_diff",
    config
)

if results:
    print("✓ Analysis successful")
else:
    print("✗ Analysis failed - check logs")
```

## Best Practices

### 1. Validate Before Analyzing

```python
# Good ✓
validator = BrickModelValidator(use_local_brick=True)
if validator.validate_ontology(model_path)['valid']:
    results = app.analyze(model_path, data_path, config)

# Bad ✗
results = app.analyze(model_path, data_path, config)  # Might fail
```

### 2. Check Data Quality

```python
# Good ✓
df = pd.read_csv(data_path)
if len(df) < 100:
    print("Warning: Limited data points")
if df.isnull().any().any():
    print("Warning: Missing values detected")

# Then analyze
results = app.analyze(model_path, data_path, config)
```

### 3. Use Configuration Files

```python
# Good ✓ - Reproducible
config = yaml.safe_load(open('config.yaml'))
results = app.analyze(model_path, data_path, config)

# Save config with results
with open('results/config_used.yaml', 'w') as f:
    yaml.dump(config, f)
```

### 4. Handle Failures Gracefully

```python
# Good ✓
for building in buildings:
    try:
        results = app.analyze(building.model, building.data, config)
        save_results(results)
    except Exception as e:
        logger.error(f"Failed: {building.id} - {e}")
        continue  # Continue with next building
```

## Next Steps

- **[Developer Guide](../../developer-guide/creating-apps/index.md)** - Create your own applications
- **[Examples](../../examples/applications/using-apps.md)** - More code samples
- **[API Reference](../../api-reference/applications/apps-manager.md)** - Complete API docs

---

**Applications documentation complete!** 🎉

Ready to analyze your building data! Start with [Apps Manager](apps-manager.md) or [Secondary Loop](secondary-loop.md).

