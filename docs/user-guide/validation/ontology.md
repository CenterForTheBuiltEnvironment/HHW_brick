# Ontology Validation

Verify that Brick models follow the Brick schema rules and RDF/OWL standards.

## Overview

Ontology validation checks if your Brick model:

- Uses **valid Brick classes** (e.g., `brick:Boiler`, `brick:Temperature_Sensor`)
- Has **correct relationships** (e.g., `brick:hasPoint`, `brick:feeds`)
- Follows **RDF/OWL syntax** rules
- Uses **proper namespaces**

## Why Ontology Validation?

### Ensure Interoperability

Valid models work with all Brick-compatible tools:

```python
# If model is valid, it works with:
# - Other Brick applications
# - SPARQL queries
# - Visualization tools
# - Analytics frameworks
```

### Catch Errors Early

Find issues before using models in production:

```python
# Invalid model might cause:
# - Analytics failures
# - Query errors
# - Integration problems

# Validate first:
if validator.validate_ontology(model)['valid']:
    # Safe to use
    app.analyze(model, data, config)
```

## Basic Usage

### Validate Single Model

Based on `examples/02_ontology_validation.py`:

```python
from hhw_brick import BrickModelValidator

# Create validator with local Brick schema
validator = BrickModelValidator(use_local_brick=True)

# Validate a model
result = validator.validate_ontology("building_105.ttl")

# Check result
if result['valid']:
    print("✓ Model is valid!")
else:
    print(f"✗ Model has {len(result['violations'])} violations")
    for violation in result['violations']:
        print(f"  - {violation}")
```

### Expected Output

**Valid model:**
```
✓ Model is valid!
```

**Invalid model:**
```
✗ Model has 3 violations
  - Invalid class: brick:InvalidBoiler
  - Missing required property: brick:hasPoint
  - Invalid namespace: http://wrong.namespace.org#
```

## Validation Methods

### validate_ontology()

Main ontology validation method.

**Signature:**
```python
def validate_ontology(ttl_file_path: str) -> Dict
```

**Parameters:**
- `ttl_file_path` (str): Path to TTL file to validate

**Returns:**
```python
{
    'valid': bool,              # True if valid
    'violations': list,         # List of violation messages
    'ttl_file_path': str,       # Path to validated file
    'success': bool,            # Same as 'valid'
    'is_valid': bool,           # Same as 'valid'
    'validation_report': str    # Text report
}
```

**Example:**
```python
result = validator.validate_ontology("building_105.ttl")

print(f"Valid: {result['valid']}")
print(f"File: {result['ttl_file_path']}")

if not result['valid']:
    print("Violations:")
    for v in result['violations']:
        print(f"  - {v}")
```

## Batch Validation

### Validate Multiple Models (Parallel)

From `examples/02_ontology_validation.py`:

```python
from hhw_brick import BrickModelValidator

validator = BrickModelValidator(use_local_brick=True)

# Batch validate with parallel processing
results = validator.batch_validate_ontology(
    test_data_dir="brick_models/",
    max_workers=8  # Number of parallel workers
)

# Results
print(f"Total files: {results['total_files']}")
print(f"Valid: {results['passed_files']}")
print(f"Invalid: {results['failed_files']}")
print(f"Accuracy: {results['overall_accuracy']:.1f}%")
```

### batch_validate_ontology()

**Signature:**
```python
def batch_validate_ontology(
    test_data_dir: str,
    max_workers: int = None
) -> Dict
```

**Parameters:**
- `test_data_dir` (str): Directory containing TTL files
- `max_workers` (int, optional): Number of parallel workers (default: CPU count - 1)

**Returns:**
```python
{
    'total_files': int,           # Total TTL files found
    'passed_files': int,          # Valid models
    'failed_files': int,          # Invalid models
    'overall_accuracy': float,    # Percentage valid
    'individual_results': [...]   # List of individual results
}
```

**Example:**
```python
# Auto-detect worker count
results = validator.batch_validate_ontology(
    test_data_dir="brick_models/"
)

# Custom worker count for better performance
results = validator.batch_validate_ontology(
    test_data_dir="brick_models/",
    max_workers=16  # Use 16 workers
)

# Show detailed results
for result in results['individual_results']:
    file_name = result['ttl_file_path'].split('/')[-1]
    status = "✓" if result['valid'] else "✗"
    print(f"{status} {file_name}")
```

## Local vs Remote Brick Schema

### Using Local Brick Schema (Recommended)

Faster and works offline:

```python
validator = BrickModelValidator(use_local_brick=True)
result = validator.validate_ontology("building_105.ttl")
```

**Advantages:**
- ✓ Faster validation
- ✓ Works offline
- ✓ Consistent results
- ✓ No network dependency

**Uses:** `hhw_brick/validation/Brick_Self.ttl`

### Using Remote Brick Schema

Latest Brick schema from GitHub:

```python
validator = BrickModelValidator(use_local_brick=False)
result = validator.validate_ontology("building_105.ttl")
```

**Advantages:**
- ✓ Always latest Brick version
- ✓ Latest class definitions

**Disadvantages:**
- ✗ Requires internet
- ✗ Slower validation
- ✗ May change over time

## Common Validation Patterns

### Pattern 1: Validate After Conversion

```python
from hhw_brick import CSVToBrickConverter, BrickModelValidator

# Convert
converter = CSVToBrickConverter()
result = converter.convert_to_brick(
    metadata_csv="metadata.csv",
    vars_csv="vars.csv",
    building_tag="105",
    output_path="building_105.ttl"
)

# Validate immediately
validator = BrickModelValidator(use_local_brick=True)
validation = validator.validate_ontology("building_105.ttl")

if validation['valid']:
    print("✓ Conversion successful and valid")
else:
    print("✗ Conversion produced invalid model")
    print("Review these issues:")
    for v in validation['violations']:
        print(f"  - {v}")
```

### Pattern 2: Production Batch Validation

```python
"""
Production validation workflow
"""
from pathlib import Path
from hhw_brick import BatchConverter, BrickModelValidator

def production_validation():
    """Convert and validate all buildings."""
    
    # Step 1: Batch convert
    print("Converting buildings...")
    batch = BatchConverter()
    conversion_results = batch.convert_all_buildings(
        metadata_csv="metadata.csv",
        vars_csv="vars.csv",
        output_dir="brick_models/",
        show_progress=True
    )
    
    print(f"Converted {conversion_results['successful']} buildings")
    
    # Step 2: Batch validate
    print("\nValidating models...")
    validator = BrickModelValidator(use_local_brick=True)
    validation_results = validator.batch_validate_ontology(
        test_data_dir="brick_models/",
        max_workers=8
    )
    
    # Step 3: Report
    print(f"\nValidation Results:")
    print(f"  Total: {validation_results['total_files']}")
    print(f"  Valid: {validation_results['passed_files']}")
    print(f"  Invalid: {validation_results['failed_files']}")
    print(f"  Accuracy: {validation_results['overall_accuracy']:.1f}%")
    
    # Step 4: Handle failures
    if validation_results['failed_files'] > 0:
        print("\nFailed models:")
        for result in validation_results['individual_results']:
            if not result['valid']:
                print(f"  ✗ {Path(result['ttl_file_path']).name}")
                for v in result.get('violations', [])[:3]:  # First 3
                    print(f"      - {v}")
    
    return validation_results

if __name__ == "__main__":
    results = production_validation()
```

### Pattern 3: Selective Validation

Only validate new or changed models:

```python
import os
from pathlib import Path

def validate_new_models(model_dir, cache_file=".validation_cache"):
    """Validate only new/changed models."""
    
    # Load validation cache
    validated = set()
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            validated = set(line.strip() for line in f)
    
    # Find new models
    all_models = set(str(p) for p in Path(model_dir).glob("*.ttl"))
    new_models = all_models - validated
    
    if not new_models:
        print("No new models to validate")
        return
    
    print(f"Validating {len(new_models)} new models...")
    
    validator = BrickModelValidator(use_local_brick=True)
    
    # Validate new models
    newly_validated = []
    for model_path in new_models:
        result = validator.validate_ontology(model_path)
        
        if result['valid']:
            newly_validated.append(model_path)
            print(f"✓ {Path(model_path).name}")
        else:
            print(f"✗ {Path(model_path).name}")
    
    # Update cache
    with open(cache_file, 'a') as f:
        for model in newly_validated:
            f.write(f"{model}\n")
    
    print(f"\nValidated {len(newly_validated)}/{len(new_models)} new models")

# Use it
validate_new_models("brick_models/")
```

## What Gets Validated

### Brick Class Names

Checks if classes exist in Brick schema:

```python
# Valid ✓
brick:Boiler
brick:Hot_Water_Supply_Temperature_Sensor
brick:Heat_Exchanger

# Invalid ✗
brick:InvalidBoiler  # No such class
brick:TemperatureSensor  # Wrong name (should be Temperature_Sensor)
myprefix:CustomClass  # Not in Brick namespace
```

### Relationship Types

Checks if relationships are valid:

```python
# Valid ✓
brick:hasPoint
brick:feeds
brick:isPartOf

# Invalid ✗
brick:hasInvalidRelation  # No such relation
custom:feeds  # Wrong namespace
```

### RDF Syntax

Checks RDF/Turtle syntax:

```turtle
# Valid ✓
:Boiler_01 a brick:Boiler .
:Boiler_01 brick:hasPoint :Temp_Sensor .

# Invalid ✗
:Boiler_01 a brick:Boiler  # Missing period
:Boiler_01 brick:hasPoint  # Incomplete triple
```

### Namespace Declarations

Checks proper namespace usage:

```turtle
# Valid ✓
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix hhws: <https://hhws.example.org#> .

# Invalid ✗
@prefix brick: <http://wrong.url.org#> .  # Wrong URL
# Missing namespace declarations
```

## Understanding Validation Results

### Valid Result

```python
{
    'valid': True,
    'violations': [],
    'ttl_file_path': 'building_105.ttl',
    'success': True,
    'is_valid': True,
    'validation_report': 'Model is valid'
}
```

### Invalid Result

```python
{
    'valid': False,
    'violations': [
        'sh:Violation on brick:hasPoint',
        'Invalid class: brick:WrongClass',
        'Missing required property'
    ],
    'ttl_file_path': 'building_105.ttl',
    'success': False,
    'is_valid': False,
    'validation_report': 'Model has 3 violations'
}
```

## Performance

### Single Model

Typical validation time:
- **Local Brick**: 0.5-2 seconds per model
- **Remote Brick**: 3-5 seconds per model (first time)

### Batch Validation

Parallel processing dramatically improves speed:

```python
# Serial (slow)
for file in ttl_files:
    validator.validate_ontology(file)  # ~2 sec each
# 100 files = ~200 seconds

# Parallel (fast)
results = validator.batch_validate_ontology(
    test_data_dir="models/",
    max_workers=8
)
# 100 files = ~30 seconds (8x speedup)
```

**Performance table:**

| Models | Serial | Parallel (8 workers) | Speedup |
|--------|--------|---------------------|---------|
| 10 | ~20s | ~5s | 4x |
| 50 | ~100s | ~15s | 6.7x |
| 100 | ~200s | ~30s | 6.7x |
| 500 | ~1000s | ~150s | 6.7x |

### Optimization Tips

1. **Use local Brick** for faster validation
2. **Increase workers** for more parallelism (up to CPU count)
3. **Validate in batches** rather than one-by-one
4. **Cache results** for unchanged models

## Troubleshooting

### Issue: "brickschema not available"

**Cause:** Missing dependency

**Solution:**
```bash
pip install brickschema
```

### Issue: "Local Brick file not found"

**Cause:** Package not properly installed

**Solution:**
```bash
# Reinstall package
pip install --force-reinstall hhw-brick
```

Or use remote Brick:
```python
validator = BrickModelValidator(use_local_brick=False)
```

### Issue: All models failing validation

**Possible causes:**
1. Conversion issues
2. Wrong Brick version
3. Corrupted TTL files

**Solution:**
```python
# Check single model manually
from rdflib import Graph

g = Graph()
try:
    g.parse("building_105.ttl", format="turtle")
    print(f"✓ File parses correctly: {len(g)} triples")
except Exception as e:
    print(f"✗ Parse error: {e}")
```

### Issue: Validation too slow

**Solution 1:** Use local Brick
```python
validator = BrickModelValidator(use_local_brick=True)
```

**Solution 2:** Increase workers
```python
results = validator.batch_validate_ontology(
    test_data_dir="models/",
    max_workers=16  # More workers
)
```

**Solution 3:** Validate only changed files
```python
# See "Pattern 3: Selective Validation" above
```

## Best Practices

### 1. Always Validate After Conversion

```python
# Good ✓
result = converter.convert_to_brick(...)
validation = validator.validate_ontology(output_file)

# Bad ✗
result = converter.convert_to_brick(...)
# Skip validation - might have invalid models
```

### 2. Use Local Brick for Production

```python
# Production ✓
validator = BrickModelValidator(use_local_brick=True)

# Development (occasional use)
validator = BrickModelValidator(use_local_brick=False)
```

### 3. Handle Validation Failures

```python
# Good ✓
result = validator.validate_ontology("model.ttl")
if not result['valid']:
    log_error(result['violations'])
    notify_admin()
    skip_model()

# Bad ✗
result = validator.validate_ontology("model.ttl")
# Ignore failures - use invalid model anyway
```

### 4. Log Validation Results

```python
import logging

logging.basicConfig(level=logging.INFO)

result = validator.validate_ontology("model.ttl")
if result['valid']:
    logging.info(f"✓ Valid: {result['ttl_file_path']}")
else:
    logging.error(f"✗ Invalid: {result['ttl_file_path']}")
    for v in result['violations']:
        logging.error(f"  - {v}")
```

## Next Steps

- **[Ground Truth Validation](ground-truth.md)** - Validate counts and completeness
- **[Subgraph Patterns](subgraph-patterns.md)** - Validate system topology
- **[Examples](../../examples/validation/basic.md)** - Working code samples

---

**Continue to:** [Ground Truth Validation](ground-truth.md) →

