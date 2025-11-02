# Batch Conversion

Efficiently convert multiple buildings from CSV to Brick format in a single operation.

## Overview

Batch conversion is designed for processing multiple buildings at once. It's ideal for:

- **Portfolio-wide conversion** - Convert all buildings in a dataset
- **Production workflows** - Automated, repeatable processes  
- **Large-scale operations** - Hundreds of buildings
- **Progress tracking** - Visual progress bars

## Basic Usage

### Minimal Example

Convert all buildings in your CSV files:

```python
from hhw_brick import BatchConverter

batch = BatchConverter()
results = batch.convert_all_buildings(
    metadata_csv="metadata.csv",
    vars_csv="vars_available_by_building.csv",
    output_dir="brick_models/"
)

print(f"Converted {results['successful']} buildings")
print(f"Failed: {results['failed']}")
```

Output:
```
Converted 150 buildings
Failed: 0
```

### With Progress Bar

Show progress during conversion:

```python
batch = BatchConverter()
results = batch.convert_all_buildings(
    metadata_csv="metadata.csv",
    vars_csv="vars_available_by_building.csv",
    output_dir="brick_models/",
    show_progress=True  # Enable progress bar
)
```

Output:
```
Converting buildings: 100%|████████| 150/150 [01:23<00:00,  1.80it/s]
```

## Parameters

### Required Parameters

#### metadata_csv

Path to building metadata file:

```python
metadata_csv="path/to/metadata.csv"
```

#### vars_csv

Path to sensor availability file:

```python
vars_csv="path/to/vars_available_by_building.csv"
```

#### output_dir

Directory where TTL files will be saved:

```python
output_dir="brick_models/"
```

The directory will be created if it doesn't exist.

### Optional Parameters

#### system_type

Filter by HVAC system type:

```python
system_type="Condensing"  # Only condensing systems
```

- **Type:** String
- **Default:** `None` (convert all systems)
- **Options:** `"Boiler"`, `"Non-condensing"`, `"Condensing"`, `"District HW"`, `"District Steam"`

**Example:**
```python
# Convert only district hot water systems
results = batch.convert_all_buildings(
    metadata_csv="metadata.csv",
    vars_csv="vars.csv",
    output_dir="district_hw_models/",
    system_type="District HW"
)
```

#### building_tags

List of specific buildings to convert:

```python
building_tags=["105", "106", "107"]
```

- **Type:** List of strings
- **Default:** `None` (convert all buildings)

**Example:**
```python
# Convert only selected buildings
target_buildings = ["105", "106", "107", "108", "109"]

results = batch.convert_all_buildings(
    metadata_csv="metadata.csv",
    vars_csv="vars.csv",
    output_dir="selected_buildings/",
    building_tags=target_buildings
)
```

#### show_progress

Show progress bar during conversion:

```python
show_progress=True  # Default: True
```

- **Type:** Boolean
- **Default:** `True`
- Uses `tqdm` for progress visualization

## Return Value

The `convert_all_buildings()` method returns a **dictionary** with statistics:

```python
results = batch.convert_all_buildings(...)

# Results structure
{
    'total': 150,              # Total buildings processed
    'successful': 148,         # Successfully converted
    'failed': 2,               # Failed conversions
    'by_system': {             # Breakdown by system type
        'Condensing': 85,
        'Non-condensing': 45,
        'District HW': 18
    },
    'total_triples': 156789,   # Total RDF statements created
    'failed_buildings': [      # List of failed building IDs
        '127', '304'
    ],
    'successful_files': [      # List of created files
        'brick_models/building_105_non-condensing_h.ttl',
        'brick_models/building_106_condensing_n.ttl',
        # ...
    ]
}
```

### Processing Results

```python
results = batch.convert_all_buildings(...)

print("Conversion Summary:")
print(f"  Total: {results['total']}")
print(f"  Successful: {results['successful']}")
print(f"  Failed: {results['failed']}")
print(f"  Success Rate: {results['successful']/results['total']*100:.1f}%")

print("\nBy System Type:")
for system, count in results['by_system'].items():
    print(f"  {system}: {count}")

if results['failed'] > 0:
    print("\nFailed Buildings:")
    for building_id in results['failed_buildings']:
        print(f"  - Building {building_id}")
```

## Output Files

### File Naming

Files are automatically named using the pattern:

```
building_{tag}_{system_abbreviation}_{variant}.ttl
```

Examples:
- `building_105_non-condensing_h.ttl`
- `building_106_condensing_n.ttl`
- `building_107_district_hw_aa.ttl`

### Output Directory Structure

```
brick_models/
├── building_105_non-condensing_h.ttl
├── building_106_condensing_n.ttl
├── building_107_condensing_an.ttl
├── building_108_district_hw_aa.ttl
└── ...
```

## Common Workflows

### Workflow 1: Convert All Buildings

```python
"""
Simple batch conversion of all buildings
"""
from hhw_brick import BatchConverter
from pathlib import Path

# Create output directory
output_dir = Path("brick_models")
output_dir.mkdir(exist_ok=True)

# Convert
batch = BatchConverter()
results = batch.convert_all_buildings(
    metadata_csv="metadata.csv",
    vars_csv="vars_available_by_building.csv",
    output_dir=str(output_dir),
    show_progress=True
)

# Report
print(f"\n{'='*60}")
print("Conversion Complete!")
print(f"{'='*60}")
print(f"Total Buildings: {results['total']}")
print(f"Successful: {results['successful']}")
print(f"Failed: {results['failed']}")
print(f"Total RDF Triples: {results['total_triples']:,}")

if results['failed'] > 0:
    print(f"\n⚠ Failed buildings: {results['failed_buildings']}")
```

### Workflow 2: Filter by System Type

```python
"""
Convert buildings of specific system types
"""
from hhw_brick import BatchConverter

# Convert condensing systems only
batch = BatchConverter()
condensing_results = batch.convert_all_buildings(
    metadata_csv="metadata.csv",
    vars_csv="vars.csv",
    output_dir="condensing_systems/",
    system_type="Condensing",
    show_progress=True
)

print(f"Converted {condensing_results['successful']} condensing systems")

# Convert district systems separately
district_results = batch.convert_all_buildings(
    metadata_csv="metadata.csv",
    vars_csv="vars.csv",
    output_dir="district_systems/",
    system_type="District HW",
    show_progress=True
)

print(f"Converted {district_results['successful']} district systems")
```

### Workflow 3: Convert by Organization

```python
"""
Batch convert buildings grouped by organization
"""
import pandas as pd
from hhw_brick import BatchConverter

# Load metadata
metadata = pd.read_csv("metadata.csv")

# Get unique organizations
organizations = metadata['org'].unique()

batch = BatchConverter()

for org in organizations:
    print(f"\nConverting buildings for: {org}")
    
    # Get building IDs for this org
    org_buildings = metadata[metadata['org'] == org]['tag'].astype(str).tolist()
    
    # Create org-specific output directory
    output_dir = f"brick_models/{org.replace(' ', '_')}"
    
    # Convert
    results = batch.convert_all_buildings(
        metadata_csv="metadata.csv",
        vars_csv="vars.csv",
        output_dir=output_dir,
        building_tags=org_buildings,
        show_progress=True
    )
    
    print(f"  Converted: {results['successful']}/{results['total']}")
```

### Workflow 4: Production with Logging

```python
"""
Production batch conversion with comprehensive logging
"""
from hhw_brick import BatchConverter
import logging
from datetime import datetime
from pathlib import Path

# Set up logging
log_file = f"conversion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def production_conversion():
    """Production batch conversion with error handling."""
    
    logging.info("Starting batch conversion")
    
    # Set up paths
    output_dir = Path("brick_models_production")
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Convert
        batch = BatchConverter()
        results = batch.convert_all_buildings(
            metadata_csv="metadata.csv",
            vars_csv="vars.csv",
            output_dir=str(output_dir),
            show_progress=True
        )
        
        # Log results
        logging.info(f"Conversion complete: {results['successful']}/{results['total']}")
        logging.info(f"Total triples created: {results['total_triples']:,}")
        
        # Log by system type
        logging.info("Breakdown by system:")
        for system, count in results['by_system'].items():
            logging.info(f"  {system}: {count}")
        
        # Log failures
        if results['failed'] > 0:
            logging.warning(f"{results['failed']} buildings failed:")
            for building_id in results['failed_buildings']:
                logging.warning(f"  - Building {building_id}")
        
        # Save results summary
        summary_file = output_dir / "conversion_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(f"Conversion Date: {datetime.now()}\n")
            f.write(f"Total: {results['total']}\n")
            f.write(f"Successful: {results['successful']}\n")
            f.write(f"Failed: {results['failed']}\n")
            f.write(f"Total Triples: {results['total_triples']:,}\n")
        
        logging.info(f"Summary saved to {summary_file}")
        return results
        
    except FileNotFoundError as e:
        logging.error(f"Input file not found: {e}")
        return None
    except Exception as e:
        logging.error(f"Conversion failed: {e}", exc_info=True)
        return None

if __name__ == "__main__":
    results = production_conversion()
```

## Advanced Usage

### Parallel Processing (Custom Implementation)

For very large datasets, you can implement parallel processing:

```python
"""
Custom parallel batch conversion
"""
from hhw_brick import CSVToBrickConverter
import pandas as pd
from multiprocessing import Pool
from pathlib import Path

def convert_single_building(args):
    """Convert a single building (for use with multiprocessing)."""
    building_tag, metadata_csv, vars_csv, output_dir = args
    
    try:
        converter = CSVToBrickConverter()
        result = converter.convert_to_brick(
            metadata_csv=metadata_csv,
            vars_csv=vars_csv,
            building_tag=building_tag,
            output_path=f"{output_dir}/building_{building_tag}.ttl"
        )
        return building_tag, 'success', len(result)
    except Exception as e:
        return building_tag, 'failed', str(e)

def parallel_batch_conversion(metadata_csv, vars_csv, output_dir, num_workers=4):
    """Batch convert using multiple processes."""
    
    # Get building IDs
    metadata = pd.read_csv(metadata_csv)
    building_ids = metadata['tag'].astype(str).tolist()
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Prepare arguments
    args = [
        (bid, metadata_csv, vars_csv, output_dir)
        for bid in building_ids
    ]
    
    # Process in parallel
    with Pool(num_workers) as pool:
        results = pool.map(convert_single_building, args)
    
    # Summarize
    successful = sum(1 for _, status, _ in results if status == 'success')
    failed = sum(1 for _, status, _ in results if status == 'failed')
    
    print(f"Parallel conversion complete:")
    print(f"  Workers: {num_workers}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    
    return results

# Use it
results = parallel_batch_conversion(
    "metadata.csv",
    "vars.csv",
    "brick_models/",
    num_workers=8
)
```

### Incremental Conversion

Convert only new buildings:

```python
"""
Incremental conversion - skip already converted buildings
"""
from hhw_brick import BatchConverter
import pandas as pd
from pathlib import Path

def incremental_conversion(metadata_csv, vars_csv, output_dir):
    """Convert only buildings not already in output directory."""
    
    # Get all buildings
    metadata = pd.read_csv(metadata_csv)
    all_buildings = set(metadata['tag'].astype(str))
    
    # Get already converted buildings
    output_path = Path(output_dir)
    if output_path.exists():
        existing_files = list(output_path.glob("building_*.ttl"))
        converted = set()
        for file in existing_files:
            # Extract building ID from filename
            parts = file.stem.split('_')
            if len(parts) > 1:
                converted.add(parts[1])  # building_105_... -> 105
    else:
        converted = set()
        output_path.mkdir(exist_ok=True)
    
    # Find new buildings
    new_buildings = all_buildings - converted
    
    print(f"Total buildings: {len(all_buildings)}")
    print(f"Already converted: {len(converted)}")
    print(f"New buildings: {len(new_buildings)}")
    
    if not new_buildings:
        print("No new buildings to convert")
        return
    
    # Convert new buildings
    batch = BatchConverter()
    results = batch.convert_all_buildings(
        metadata_csv=metadata_csv,
        vars_csv=vars_csv,
        output_dir=output_dir,
        building_tags=list(new_buildings),
        show_progress=True
    )
    
    print(f"\nConverted {results['successful']} new buildings")
    return results

# Use it
results = incremental_conversion(
    "metadata.csv",
    "vars.csv",
    "brick_models/"
)
```

## Performance

### Benchmarks

Typical performance on a standard laptop:

| Buildings | Time | Rate |
|-----------|------|------|
| 10 | ~6 seconds | 1.7 builds/sec |
| 50 | ~28 seconds | 1.8 builds/sec |
| 100 | ~55 seconds | 1.8 builds/sec |
| 500 | ~4.5 minutes | 1.9 builds/sec |

### Optimization Tips

1. **Use SSD storage** - Faster file I/O
2. **Disable progress bar** for scripts - Slight speedup
3. **Consider parallel processing** - For very large datasets (>1000 buildings)
4. **Close other applications** - More memory available

## Troubleshooting

### Issue: "No such file or directory"

**Cause:** Output directory path is invalid

**Solution:**
```python
from pathlib import Path

# Create directory first
output_dir = Path("brick_models")
output_dir.mkdir(parents=True, exist_ok=True)

# Then convert
results = batch.convert_all_buildings(
    metadata_csv="metadata.csv",
    vars_csv="vars.csv",
    output_dir=str(output_dir)
)
```

### Issue: Some buildings failed

**Cause:** Data issues in specific buildings

**Solution:**
```python
results = batch.convert_all_buildings(...)

if results['failed'] > 0:
    print(f"Failed buildings: {results['failed_buildings']}")
    
    # Try converting failed buildings individually for debugging
    from hhw_brick import CSVToBrickConverter
    converter = CSVToBrickConverter()
    
    for building_id in results['failed_buildings']:
        try:
            converter.convert_to_brick(
                metadata_csv="metadata.csv",
                vars_csv="vars.csv",
                building_tag=building_id,
                output_path=f"debug_building_{building_id}.ttl"
            )
        except Exception as e:
            print(f"Building {building_id} error: {e}")
```

### Issue: Progress bar not showing

**Cause:** `tqdm` not installed

**Solution:**
```bash
pip install tqdm
```

Or disable progress bar:
```python
results = batch.convert_all_buildings(
    ...,
    show_progress=False
)
```

## Best Practices

### 1. Test First

Test on a small subset before full conversion:

```python
# Test with 10 buildings
test_buildings = ["105", "106", "107", "108", "109"]

results = batch.convert_all_buildings(
    metadata_csv="metadata.csv",
    vars_csv="vars.csv",
    output_dir="test_output/",
    building_tags=test_buildings
)

# If successful, run full conversion
if results['failed'] == 0:
    results = batch.convert_all_buildings(
        metadata_csv="metadata.csv",
        vars_csv="vars.csv",
        output_dir="production_output/"
    )
```

### 2. Separate by System Type

Organize outputs by system type:

```python
system_types = ["Condensing", "Non-condensing", "District HW"]

for system in system_types:
    results = batch.convert_all_buildings(
        metadata_csv="metadata.csv",
        vars_csv="vars.csv",
        output_dir=f"brick_models/{system.lower().replace(' ', '_')}/",
        system_type=system
    )
```

### 3. Keep Conversion Logs

Save detailed logs for auditing:

```python
import json
from datetime import datetime

results = batch.convert_all_buildings(...)

# Save results
log_data = {
    'timestamp': datetime.now().isoformat(),
    'results': results,
    'metadata_file': 'metadata.csv',
    'vars_file': 'vars.csv'
}

with open('conversion_log.json', 'w') as f:
    json.dump(log_data, f, indent=2)
```

## Next Steps

- **[System Types](system-types.md)** - Learn about different HVAC systems
- **[Sensor Mapping](sensor-mapping.md)** - Customize sensor mappings
- **[Validation](../validation/index.md)** - Validate converted models
- **[Examples](../../examples/conversion/batch.md)** - More code examples

---

**Continue to:** [System Types](system-types.md) →

