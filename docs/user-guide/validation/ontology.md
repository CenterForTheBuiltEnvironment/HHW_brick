# Ontology Validation

Verify that Brick models follow the Brick Schema 1.4 rules and RDF/OWL standards using SHACL validation.

## Overview

Ontology validation ensures your Brick model:

- ✓ Uses **valid Brick classes** (e.g., `brick:Boiler`, `brick:Temperature_Sensor`)
- ✓ Has **correct relationships** (e.g., `brick:hasPart`, `brick:feeds`, `brick:isPointOf`)
- ✓ Follows **RDF/OWL syntax** rules
- ✓ Uses **proper namespaces** and URIs
- ✓ Conforms to **SHACL constraints** defined in Brick Schema 1.4

---

## Why Ontology Validation?

### 1. Ensure Interoperability
Valid models work seamlessly with all Brick-compatible tools:

```python
# If model is valid, it works with:
# ✓ Other Brick applications
# ✓ SPARQL query engines
# ✓ Visualization tools (e.g., Brick Viewer)
# ✓ Analytics frameworks
# ✓ Integration platforms
```

### 2. Catch Errors Early
Find schema violations before using models in production:

```python
# Invalid models might cause:
# ✗ Analytics application failures
# ✗ SPARQL query errors
# ✗ Integration problems
# ✗ Incorrect inference results

# Always validate first:
validator = BrickModelValidator(use_local_brick=True)
result = validator.validate_ontology("building_105.ttl")

if result['valid']:
    # Safe to use in production
    app.analyze("building_105.ttl", data, config)
else:
    print("Fix violations before proceeding")
```

### 3. Quality Assurance
Ontology validation is the first level of quality assurance in the validation pipeline.

---

## What is SHACL?

**SHACL** (Shapes Constraint Language) is a W3C standard for validating RDF graphs.

### How SHACL Works

```
Brick Model (RDF)  +  SHACL Shapes  →  Validation Report
    (Your data)      (Schema rules)     (Conformance check)
```

**Example SHACL Shape** (from Brick Schema):
```turtle
# A Temperature_Sensor must have a unit
brick:TemperatureSensorShape
    a sh:NodeShape ;
    sh:targetClass brick:Temperature_Sensor ;
    sh:property [
        sh:path brick:hasUnit ;
        sh:minCount 1 ;
        sh:message "Temperature sensor must have a unit" ;
    ] .
```

### SHACL in HHW Brick

HHW Brick uses Brick Schema 1.4's official SHACL shapes to validate models:

- ✓ Class constraints
- ✓ Property constraints
- ✓ Relationship constraints
- ✓ Data type constraints

---

## Basic Usage

### Validate Single Model

Complete example from `examples/02_ontology_validation.py`:

```python
from hhw_brick import BrickModelValidator

# Create validator with local Brick schema
validator = BrickModelValidator(use_local_brick=True)

# Validate a model
result = validator.validate_ontology("building_105.ttl")

# Check result
if result['valid']:
    print("✓ Model is valid!")
    print(f"  Conforms to Brick Schema 1.4")
else:
    print(f"✗ Model has {len(result['violations'])} violations:")
    for i, violation in enumerate(result['violations'], 1):
        print(f"  {i}. {violation}")
```

### Result Structure

```python
{
    'valid': True,              # or False
    'conforms': True,           # SHACL conformance
    'violations': [],           # List of violation messages
    'validation_report': {...}  # Detailed SHACL report (if violations exist)
}
```

### Expected Output

**✓ Valid model:**
```
✓ Model is valid!
  Conforms to Brick Schema 1.4
```

**✗ Invalid model:**
```
✗ Model has 3 violations:
  1. Value does not have class brick:Equipment
  2. Less than 1 values on building105:boiler1->brick:hasPoint
  3. Invalid namespace: http://wrong.namespace.org#sensor1
```

---

## Batch Validation with Parallel Processing

Validate multiple buildings efficiently:

### Basic Batch Validation

```python
from hhw_brick import BrickModelValidator

validator = BrickModelValidator(use_local_brick=True)

# Validate all TTL files in directory
results = validator.batch_validate_ontology(
    test_data_dir="output/",
    max_workers=4  # Parallel workers (default: CPU count - 1)
)

# Display summary
print(f"\n{'='*60}")
print("Batch Validation Results")
print(f"{'='*60}")
print(f"Total models: {results['total_files']}")
print(f"Valid: {results['passed_files']} ✓")
print(f"Invalid: {results['failed_files']} ✗")
print(f"Overall accuracy: {results['overall_accuracy']:.1f}%")
```

### Detailed Results

```python
# Access individual results
for detail in results['details']:
    filename = detail['filename']
    valid = detail['valid']
    status = '✓' if valid else '✗'

    print(f"{status} {filename}")

    if not valid and 'violations' in detail:
        for violation in detail['violations']:
            print(f"    - {violation}")
```

### Results Structure

```python
{
    'total_files': 10,
    'passed_files': 9,
    'failed_files': 1,
    'overall_accuracy': 90.0,
    'details': [
        {
            'filename': 'building_105.ttl',
            'valid': True,
            'conforms': True,
            'violations': []
        },
        {
            'filename': 'building_110.ttl',
            'valid': False,
            'conforms': False,
            'violations': ['Invalid class: brick:WrongBoiler']
        },
        # ... more results
    ]
}
```

### Performance with Parallel Processing

```python
# Single-threaded (slow for many files)
results = validator.batch_validate_ontology(
    test_data_dir="output/",
    max_workers=1  # Sequential
)
# 10 files × 10s each = 100 seconds

# Multi-threaded (faster)
results = validator.batch_validate_ontology(
    test_data_dir="output/",
    max_workers=4  # 4 parallel workers
)
# 10 files / 4 workers × 10s = ~25 seconds
```

!!! tip "Choosing max_workers"
    - Default: `cpu_count() - 1` (leaves one core free)
    - Small datasets: `max_workers=2` or `3`
    - Large datasets: `max_workers=8` or more
    - Don't exceed available CPU cores

---

## Local vs Nightly Brick Schema

### Use Local Brick (Recommended)

```python
validator = BrickModelValidator(use_local_brick=True)
```

**Advantages**:
- ✓ Works offline
- ✓ Faster (no network download)
- ✓ Stable (specific Brick version)
- ✓ Reproducible results

**When to use**:
- Production environments
- CI/CD pipelines
- Offline validation
- Consistent testing

### Use Nightly Brick (Latest)

```python
validator = BrickModelValidator(load_brick_nightly=True)
```

**Advantages**:
- ✓ Latest Brick Schema features
- ✓ Newest SHACL shapes
- ✓ Cutting-edge updates

**Disadvantages**:
- ✗ Requires internet connection
- ✗ Slower (downloads from GitHub)
- ✗ Results may change over time

**When to use**:
- Development/testing
- Exploring new Brick features
- Checking compatibility with latest schema

!!! warning "Don't mix in production"
    Choose one approach and stick with it for consistency. Use `use_local_brick=True`
    for production to ensure reproducible validation results.

---

## Common Violations and Fixes

### 1. Invalid Brick Class

**Violation**:
```
Value does not have class brick:Equipment
```

**Cause**: Using non-existent or misspelled Brick class

**Fix**:
```python
# ✗ Wrong
g.add((building_ns.boiler1, RDF.type, BRICK.InvalidBoiler))

# ✓ Correct
g.add((building_ns.boiler1, RDF.type, BRICK.Boiler))
```

### 2. Missing Required Relationship

**Violation**:
```
Less than 1 values on building105:boiler1->brick:hasPoint
```

**Cause**: Equipment missing required sensors/points

**Fix**:
```python
# ✗ Missing hasPoint relationship
g.add((building_ns.boiler1, RDF.type, BRICK.Boiler))

# ✓ Add required sensor
g.add((building_ns.boiler1, RDF.type, BRICK.Boiler))
g.add((building_ns.boiler1, BRICK.hasPoint, building_ns.boiler1_temp))
g.add((building_ns.boiler1_temp, RDF.type, BRICK.Temperature_Sensor))
```

### 3. Invalid Namespace

**Violation**:
```
Invalid namespace: http://example.org#sensor1
```

**Cause**: Using non-standard namespace without proper declaration

**Fix**:
```python
# ✗ Wrong - undefined namespace
sensor_uri = URIRef("http://example.org#sensor1")

# ✓ Correct - use building-specific namespace
from rdflib import Namespace
BUILDING = Namespace("https://buildings.example.org#")
sensor_uri = BUILDING.building105_sensor1
```

### 4. Incorrect Relationship Direction

**Violation**:
```
Unexpected relationship direction
```

**Cause**: Using inverse relationships incorrectly

**Fix**:
```python
# ✗ Wrong direction
g.add((sensor, BRICK.isPointOf, equipment))

# ✓ Correct direction
g.add((equipment, BRICK.hasPoint, sensor))
# OR use inverse
g.add((sensor, BRICK.isPointOf, equipment))
```

### 5. Missing Type Declaration

**Violation**:
```
Node has no rdf:type
```

**Cause**: Entity missing `rdf:type` declaration

**Fix**:
```python
# ✗ Missing type
g.add((building_ns.loop1, BRICK.hasPart, building_ns.pump1))

# ✓ Add types
g.add((building_ns.loop1, RDF.type, BRICK.Hot_Water_Loop))
g.add((building_ns.pump1, RDF.type, BRICK.Pump))
g.add((building_ns.loop1, BRICK.hasPart, building_ns.pump1))
```

---

## Advanced Usage

### Custom Validation with Additional Shapes

```python
from hhw_brick import BrickModelValidator

# Validate with custom SHACL shapes
validator = BrickModelValidator(use_local_brick=True)

# Load additional shapes
custom_shapes = """
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix brick: <https://brickschema.org/schema/Brick#> .

# Custom shape: All boilers must have a manufacturer
brick:CustomBoilerShape
    a sh:NodeShape ;
    sh:targetClass brick:Boiler ;
    sh:property [
        sh:path brick:hasManufacturer ;
        sh:minCount 1 ;
        sh:message "Boiler must have a manufacturer" ;
    ] .
"""

# Note: HHW Brick currently validates against standard Brick shapes
# Custom shapes require extending the validator
```

### Programmatic Access to Violations

```python
result = validator.validate_ontology("building_105.ttl")

if not result['valid']:
    violations = result['violations']

    # Categorize violations
    class_violations = [v for v in violations if 'class' in v.lower()]
    property_violations = [v for v in violations if 'property' in v.lower()]

    print(f"Class violations: {len(class_violations)}")
    print(f"Property violations: {len(property_violations)}")

    # Log for debugging
    with open('validation_report.txt', 'w') as f:
        for v in violations:
            f.write(f"{v}\n")
```

---

## Integration with Conversion Pipeline

Validate immediately after conversion:

```python
from hhw_brick import CSVToBrickConverter, BrickModelValidator

# Convert
converter = CSVToBrickConverter()
graph = converter.convert_to_brick(
    metadata_csv="metadata.csv",
    vars_csv="vars_available_by_building.csv",
    building_tag="105",
    output_path="building_105.ttl"
)

# Validate immediately
validator = BrickModelValidator(use_local_brick=True)
result = validator.validate_ontology("building_105.ttl")

if result['valid']:
    print(f"✓ Conversion successful: {len(graph)} triples")
    print("✓ Model validated")
else:
    print("✗ Conversion produced invalid model")
    print("Violations:")
    for v in result['violations']:
        print(f"  - {v}")
    # Fix converter logic
```

---

## Troubleshooting

### Validation Takes Too Long

**Problem**: Validation is slow for large models

**Solutions**:
1. Use batch validation with parallel processing
2. Reduce `max_workers` if memory is limited
3. Validate incrementally during development

```python
# Fast batch validation
results = validator.batch_validate_ontology(
    test_data_dir="output/",
    max_workers=8  # Adjust based on CPU
)
```

### "No data to validate" Error

**Problem**: Validator can't read the TTL file

**Solutions**:
1. Check file path is correct
2. Verify TTL file is valid RDF syntax
3. Ensure file has `.ttl` extension

```python
from pathlib import Path

ttl_file = Path("building_105.ttl")
if not ttl_file.exists():
    print(f"File not found: {ttl_file}")
elif not ttl_file.suffix == '.ttl':
    print(f"Wrong extension: {ttl_file.suffix}")
```

### Inconsistent Validation Results

**Problem**: Results differ between runs

**Solution**: Use `use_local_brick=True` for consistent results

```python
# ✗ Inconsistent (downloads latest schema each time)
validator = BrickModelValidator(load_brick_nightly=True)

# ✓ Consistent (uses fixed local schema)
validator = BrickModelValidator(use_local_brick=True)
```

### Violations but Model Looks Correct

**Problem**: SHACL reports violations but model seems valid

**Solutions**:
1. Check Brick Schema version compatibility
2. Verify namespace URIs are exact
3. Review SHACL shape definitions
4. Check relationship directions

```python
# Debug: Inspect model manually
from rdflib import Graph

g = Graph()
g.parse("building_105.ttl", format="turtle")

# Check all types used
types = set()
for s, p, o in g.triples((None, RDF.type, None)):
    types.add(str(o))

print("Classes used:")
for t in sorted(types):
    print(f"  - {t}")
```

---

## Best Practices

!!! tip "Ontology Validation Best Practices"
    1. **Validate early and often** - After each conversion
    2. **Use local Brick** - For consistent results (`use_local_brick=True`)
    3. **Batch validate** - Faster with `max_workers`
    4. **Log violations** - Save reports for debugging
    5. **Fix root causes** - Update converter, not individual models
    6. **Automate** - Include in CI/CD pipeline

### Example CI/CD Integration

```python
def ci_validation_check(output_dir):
    """CI/CD validation check - fails build if invalid models"""
    validator = BrickModelValidator(use_local_brick=True)

    results = validator.batch_validate_ontology(
        test_data_dir=output_dir,
        max_workers=4
    )

    if results['overall_accuracy'] < 100.0:
        print(f"✗ Validation failed: {results['failed_files']} invalid models")
        for detail in results['details']:
            if not detail['valid']:
                print(f"\n{detail['filename']}:")
                for v in detail.get('violations', []):
                    print(f"  - {v}")
        return False  # Fail CI build
    else:
        print(f"✓ All {results['total_files']} models valid")
        return True  # Pass CI build

# In CI pipeline
if not ci_validation_check("output/"):
    exit(1)  # Fail build
```

---

## Next Steps

- [Ground Truth Validation](ground-truth.md) - Validate point and equipment counts
- [Subgraph Pattern Validation](subgraph-patterns.md) - Validate system structure
- [Examples](../../examples/) - Working validation examples
- [Back to Validation Overview](index.md)

---

## References

- [Brick Schema Documentation](https://brickschema.org/)
- [SHACL W3C Specification](https://www.w3.org/TR/shacl/)
- [RDF 1.1 Primer](https://www.w3.org/TR/rdf11-primer/)
- [brickschema Python Package](https://github.com/BrickSchema/py-brickschema)

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
