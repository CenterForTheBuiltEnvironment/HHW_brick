# Ground Truth Validation

Validate Brick models against expected counts calculated from source CSV data.

## Overview

Ground truth validation compares your Brick model against **expected values** derived from the original CSV data:

- **Point counts** - Number of sensors/points
- **Boiler counts** - Number of boilers
- **Pump counts** - Number of pumps  
- **Weather stations** - Presence of weather data

This ensures your conversion was **complete and accurate**.

## Why Ground Truth Validation?

### Verify Completeness

Ensure no data was lost during conversion:

```python
# Expected: 23 points (from CSV)
# Actual: 18 points (in Brick model)
# ✗ 5 points missing - conversion issue!
```

### Catch Conversion Errors

Find problems early:

```python
# Expected: 2 boilers
# Actual: 1 boiler
# ✗ Check b_number or sensor detection logic
```

### Production Quality

Only use complete models:

```python
if point_validation['match']:
    # Model is complete, safe to use
    app.analyze(model, data, config)
```

## Ground Truth Calculator

### Generate Ground Truth

From `examples/03_point_count_validation.py`:

```python
from hhw_brick.validation import GroundTruthCalculator

# Create calculator
calculator = GroundTruthCalculator()

# Calculate expected counts from CSV
ground_truth_df = calculator.calculate(
    metadata_csv="metadata.csv",
    vars_csv="vars_available_by_building.csv",
    output_csv="ground_truth.csv"
)

print(f"Generated ground truth for {len(ground_truth_df)} buildings")
```

### Ground Truth Format

The generated `ground_truth.csv` contains:

```csv
tag,system,point_count,boiler_count,pump_count,weather_station_count
105,Non-condensing,23,2,3,1
106,Condensing,18,1,2,0
107,District HW,15,0,2,1
```

**Columns:**
- `tag` - Building ID
- `system` - System type
- `point_count` - Expected total points
- `boiler_count` - Expected boilers
- `pump_count` - Expected pumps
- `weather_station_count` - Expected weather stations (0 or 1)

### How Counts Are Calculated

#### Point Count

Counts all sensors marked as available (value=1) in `vars_available_by_building.csv`:

```python
# vars.csv
tag,hw_supply_temp,hw_return_temp,hw_flow,outdoor_temp
105,1,1,1,1  # 4 sensors available

# ground_truth.csv
tag,point_count
105,4  # Calculated from available sensors
```

#### Boiler Count

From `b_number` in metadata.csv or inferred from sensor patterns:

```python
# metadata.csv
tag,b_number
105,2  # Explicitly set

# OR inferred from sensors
# vars.csv: sup1, ret1, fire1, sup2, ret2, fire2
# Infers: 2 boilers

# ground_truth.csv
tag,boiler_count
105,2
```

#### Pump Count

Inferred from pump sensor patterns (`pmp1_*`, `pmp2_*`, etc.):

```python
# vars.csv
tag,pmp1_pwr,pmp1_spd,pmp2_pwr,pmp2_spd,pmp3_pwr
105,1,1,1,1,1  # Pump 1, 2, 3 detected

# ground_truth.csv
tag,pump_count
105,3
```

#### Weather Station

From `oper` column or outdoor sensors:

```python
# Has outdoor_temp sensor or oper != 0
# weather_station_count = 1
```

## Point Count Validation

### Validate Single Building

From `examples/03_point_count_validation.py`:

```python
from hhw_brick import BrickModelValidator

# Create validator with ground truth
validator = BrickModelValidator(
    ground_truth_csv_path="ground_truth.csv"
)

# Validate point count
result = validator.validate_point_count("building_105.ttl")

# Check result
if result['success'] and result['match']:
    print("✓ Point count matches!")
else:
    print(f"✗ Point count mismatch")
    print(f"  Expected: {result['expected_point_count']}")
    print(f"  Actual: {result['actual_point_count']}")
    print(f"  Accuracy: {result['accuracy_percentage']:.1f}%")
```

### validate_point_count()

**Signature:**
```python
def validate_point_count(ttl_file_path: str) -> Dict
```

**Returns:**
```python
{
    'success': bool,                # Overall success
    'match': bool,                  # Counts match exactly
    'expected_point_count': int,    # From ground truth
    'actual_point_count': int,      # From Brick model
    'accuracy_percentage': float,   # Match percentage
    'ttl_file_path': str,          # Model file path
    'building_tag': str             # Extracted building ID
}
```

**Example:**
```python
result = validator.validate_point_count("building_105.ttl")

print(f"Expected: {result['expected_point_count']}")
print(f"Actual: {result['actual_point_count']}")
print(f"Match: {result['match']}")
print(f"Accuracy: {result['accuracy_percentage']:.1f}%")
```

## Equipment Count Validation

### Validate Equipment Counts

From `examples/04_equipment_count_validation.py`:

```python
from hhw_brick import BrickModelValidator

validator = BrickModelValidator(
    ground_truth_csv_path="ground_truth.csv",
    use_local_brick=True
)

# Validate equipment counts
result = validator.validate_equipment_count("building_105.ttl")

# Check overall result
if result['overall_success']:
    print("✓ All equipment counts match!")
else:
    print("✗ Equipment count mismatch detected")

# Check individual equipment
print(f"Boilers: {result['boiler']['actual']}/{result['boiler']['expected']}")
print(f"Pumps: {result['pump']['actual']}/{result['pump']['expected']}")
print(f"Weather: {result['weather_station']['actual']}/{result['weather_station']['expected']}")
```

### validate_equipment_count()

**Signature:**
```python
def validate_equipment_count(ttl_file_path: str) -> Dict
```

**Returns:**
```python
{
    'overall_success': bool,        # All equipment matches
    'boiler': {
        'expected': int,
        'actual': int,
        'match': bool
    },
    'pump': {
        'expected': int,
        'actual': int,
        'match': bool
    },
    'weather_station': {
        'expected': int,
        'actual': int,
        'match': bool
    },
    'ttl_file_path': str,
    'building_tag': str
}
```

**Example:**
```python
result = validator.validate_equipment_count("building_105.ttl")

for equip_type in ['boiler', 'pump', 'weather_station']:
    equip = result[equip_type]
    status = "✓" if equip['match'] else "✗"
    print(f"{status} {equip_type}: {equip['actual']}/{equip['expected']}")
```

## Batch Validation

### Batch Point Count Validation

Validate multiple models:

```python
from hhw_brick import BrickModelValidator

validator = BrickModelValidator(
    ground_truth_csv_path="ground_truth.csv"
)

# Batch validate point counts
results = validator.batch_validate_point_count(
    test_data_dir="brick_models/"
)

print(f"Total files: {results['total_files']}")
print(f"Matched: {results['passed_files']}")
print(f"Mismatched: {results['failed_files']}")
print(f"Accuracy: {results['overall_accuracy']:.1f}%")
```

### Batch Equipment Count Validation

```python
# Batch validate equipment counts
results = validator.batch_validate_equipment_count(
    test_data_dir="brick_models/"
)

print(f"Total files: {results['total_files']}")
print(f"All matched: {results['passed_files']}")
print(f"Accuracy: {results['overall_accuracy']:.1f}%")
```

### batch_validate_point_count()

**Signature:**
```python
def batch_validate_point_count(test_data_dir: str) -> Dict
```

**Returns:**
```python
{
    'total_files': int,
    'passed_files': int,            # Exact matches
    'failed_files': int,            # Mismatches
    'overall_accuracy': float,      # Average accuracy %
    'individual_results': [...]     # List of individual results
}
```

## Complete Validation Workflow

From examples:

```python
"""
Complete ground truth validation workflow
Based on examples/03 and 04
"""

from pathlib import Path
from hhw_brick import BatchConverter, BrickModelValidator
from hhw_brick.validation import GroundTruthCalculator

def complete_ground_truth_workflow():
    # Paths
    metadata_csv = "metadata.csv"
    vars_csv = "vars_available_by_building.csv"
    output_dir = Path("brick_models")
    ground_truth_csv = "ground_truth.csv"

    # ===== Step 1: Convert CSV to Brick =====
    print("Step 1: Converting CSV to Brick...")
    batch = BatchConverter()
    conversion_results = batch.convert_all_buildings(
        metadata_csv=metadata_csv,
        vars_csv=vars_csv,
        output_dir=str(output_dir),
        show_progress=True
    )
    print(f"✓ Converted {conversion_results['successful']} buildings")

    # ===== Step 2: Generate Ground Truth =====
    print("\nStep 2: Generating ground truth...")
    calculator = GroundTruthCalculator()
    ground_truth_df = calculator.calculate(
        metadata_csv=metadata_csv,
        vars_csv=vars_csv,
        output_csv=ground_truth_csv
    )
    print(f"✓ Ground truth for {len(ground_truth_df)} buildings")

    # Show sample
    print("\n  Sample (first 3 buildings):")
    for _, row in ground_truth_df.head(3).iterrows():
        print(f"    Building {row['tag']}: "
              f"{int(row['point_count'])} points, "
              f"{int(row['boiler_count'])} boilers, "
              f"{int(row['pump_count'])} pumps")

    # ===== Step 3: Create Validator =====
    validator = BrickModelValidator(
        ground_truth_csv_path=ground_truth_csv,
        use_local_brick=True
    )

    # ===== Step 4: Validate Point Counts =====
    print("\nStep 3: Validating point counts...")
    point_results = validator.batch_validate_point_count(
        test_data_dir=str(output_dir)
    )

    print(f"✓ Point count validation:")
    print(f"  - Matched: {point_results['passed_files']}/{point_results['total_files']}")
    print(f"  - Accuracy: {point_results['overall_accuracy']:.1f}%")

    # ===== Step 5: Validate Equipment Counts =====
    print("\nStep 4: Validating equipment counts...")
    equipment_results = validator.batch_validate_equipment_count(
        test_data_dir=str(output_dir)
    )

    print(f"✓ Equipment count validation:")
    print(f"  - Matched: {equipment_results['passed_files']}/{equipment_results['total_files']}")
    print(f"  - Accuracy: {equipment_results['overall_accuracy']:.1f}%")

    # ===== Step 6: Detailed Report for Failures =====
    if point_results['failed_files'] > 0:
        print("\nPoint count mismatches:")
        for result in point_results['individual_results']:
            if not result['match']:
                file_name = Path(result['ttl_file_path']).name
                print(f"  ✗ {file_name}")
                print(f"      Expected: {result['expected_point_count']}")
                print(f"      Actual: {result['actual_point_count']}")
                print(f"      Accuracy: {result['accuracy_percentage']:.1f}%")

    # ===== Summary =====
    print("\n" + "="*60)
    print("Ground Truth Validation Summary")
    print("="*60)
    print(f"Total buildings: {conversion_results['successful']}")
    print(f"Point counts matched: {point_results['passed_files']}")
    print(f"Equipment counts matched: {equipment_results['passed_files']}")

    all_valid = (
        point_results['passed_files'] == conversion_results['successful'] and
        equipment_results['passed_files'] == conversion_results['successful']
    )

    if all_valid:
        print("\n✓ All models complete and accurate!")
        print("  Ready for production use.")
    else:
        print("\n⚠ Some models have count mismatches")
        print("  Review conversion or source data.")

    return {
        'conversion': conversion_results,
        'ground_truth': ground_truth_df,
        'points': point_results,
        'equipment': equipment_results
    }

if __name__ == "__main__":
    results = complete_ground_truth_workflow()
```

## Understanding Results

### Point Count Match

```python
# Perfect match
{
    'success': True,
    'match': True,
    'expected_point_count': 23,
    'actual_point_count': 23,
    'accuracy_percentage': 100.0
}

# Partial match
{
    'success': True,
    'match': False,
    'expected_point_count': 23,
    'actual_point_count': 20,
    'accuracy_percentage': 86.96  # 20/23 * 100
}
```

### Equipment Count Results

```python
# All match
{
    'overall_success': True,
    'boiler': {'expected': 2, 'actual': 2, 'match': True},
    'pump': {'expected': 3, 'actual': 3, 'match': True},
    'weather_station': {'expected': 1, 'actual': 1, 'match': True}
}

# Mismatch detected
{
    'overall_success': False,
    'boiler': {'expected': 2, 'actual': 1, 'match': False},  # Missing 1
    'pump': {'expected': 3, 'actual': 3, 'match': True},
    'weather_station': {'expected': 1, 'actual': 1, 'match': True}
}
```

## Common Patterns

### Pattern 1: Validate During Conversion

```python
from hhw_brick import CSVToBrickConverter, BrickModelValidator
from hhw_brick.validation import GroundTruthCalculator

# Generate ground truth once
calculator = GroundTruthCalculator()
calculator.calculate("metadata.csv", "vars.csv", "ground_truth.csv")

# Create validator
validator = BrickModelValidator(ground_truth_csv_path="ground_truth.csv")

# Convert and validate each building
converter = CSVToBrickConverter()
for building_id in ["105", "106", "107"]:
    # Convert
    converter.convert_to_brick(
        metadata_csv="metadata.csv",
        vars_csv="vars.csv",
        building_tag=building_id,
        output_path=f"building_{building_id}.ttl"
    )

    # Validate immediately
    result = validator.validate_point_count(f"building_{building_id}.ttl")

    if result['match']:
        print(f"✓ Building {building_id}: Complete")
    else:
        print(f"✗ Building {building_id}: {result['accuracy_percentage']:.1f}% complete")
```

### Pattern 2: Only Use Complete Models

```python
def get_complete_models(model_dir, ground_truth_path):
    """Return list of models with 100% point count match."""

    validator = BrickModelValidator(
        ground_truth_csv_path=ground_truth_path
    )

    results = validator.batch_validate_point_count(test_data_dir=model_dir)

    complete_models = []
    for result in results['individual_results']:
        if result['match']:  # 100% match
            complete_models.append(result['ttl_file_path'])

    return complete_models

# Use only complete models
complete = get_complete_models("brick_models/", "ground_truth.csv")
print(f"Found {len(complete)} complete models")

for model_path in complete:
    # Safe to use in analytics
    app.analyze(model_path, data, config)
```

### Pattern 3: Threshold-Based Acceptance

Accept models above a certain accuracy threshold:

```python
def get_acceptable_models(model_dir, ground_truth_path, threshold=95.0):
    """Return models with accuracy >= threshold."""

    validator = BrickModelValidator(
        ground_truth_csv_path=ground_truth_path
    )

    results = validator.batch_validate_point_count(test_data_dir=model_dir)

    acceptable = []
    for result in results['individual_results']:
        if result['accuracy_percentage'] >= threshold:
            acceptable.append({
                'path': result['ttl_file_path'],
                'accuracy': result['accuracy_percentage']
            })

    return acceptable

# Use models with 95%+ accuracy
acceptable = get_acceptable_models("brick_models/", "ground_truth.csv", 95.0)
print(f"Found {len(acceptable)} acceptable models (≥95% accurate)")
```

## Troubleshooting

### Issue: "Ground truth file not found"

**Solution:** Generate it first:
```python
calculator = GroundTruthCalculator()
calculator.calculate(
    metadata_csv="metadata.csv",
    vars_csv="vars.csv",
    output_csv="ground_truth.csv"
)
```

### Issue: Point count always 0

**Cause:** Building tag not found in ground truth

**Solution:** Check building ID format:
```python
import pandas as pd

# Check ground truth
gt = pd.read_csv("ground_truth.csv")
print("Buildings in ground truth:")
print(gt['tag'].tolist())

# Ensure building ID matches
# File: building_105.ttl -> tag should be "105" in ground_truth.csv
```

### Issue: All equipment counts mismatch

**Cause:** Ground truth calculation issue

**Solution:** Regenerate ground truth:
```python
# Delete old file
import os
if os.exists("ground_truth.csv"):
    os.remove("ground_truth.csv")

# Regenerate
calculator = GroundTruthCalculator()
calculator.calculate(
    metadata_csv="metadata.csv",
    vars_csv="vars.csv",
    output_csv="ground_truth.csv"
)
```

### Issue: Point count slightly off

**Possible causes:**
1. Sensor mapping differences
2. Optional sensors not counted
3. Generated points (e.g., virtual points)

**Investigation:**
```python
# Check what's in the model
from rdflib import Graph

g = Graph()
g.parse("building_105.ttl", format="turtle")

# Count points manually
query = """
PREFIX brick: <https://brickschema.org/schema/Brick#>
SELECT (COUNT(?point) as ?count) WHERE {
    ?point a ?type .
    ?type rdfs:subClassOf* brick:Point .
}
"""

for row in g.query(query):
    print(f"Actual points in model: {row.count}")
```

## Best Practices

### 1. Generate Ground Truth First

```python
# Good ✓
calculator.calculate("metadata.csv", "vars.csv", "ground_truth.csv")
validator = BrickModelValidator(ground_truth_csv_path="ground_truth.csv")

# Bad ✗
# Try to validate without ground truth
```

### 2. Regenerate After Data Changes

```python
# If CSV data changes, regenerate ground truth
calculator.calculate("updated_metadata.csv", "updated_vars.csv", "ground_truth.csv")
```

### 3. Check Both Points and Equipment

```python
# Good ✓
point_result = validator.validate_point_count(model)
equip_result = validator.validate_equipment_count(model)

# Bad ✗
# Only check one type
```

### 4. Handle Partial Matches

```python
# Good ✓
if result['accuracy_percentage'] >= 95.0:
    # Use model with warning
    logging.warning(f"Model {model} is {result['accuracy_percentage']:.1f}% complete")
    use_model(model)

# Bad ✗
if result['match']:  # Only accept 100% matches
    use_model(model)
# Might reject many usable models
```

## Next Steps

- **[Subgraph Patterns](subgraph-patterns.md)** - Validate system topology
- **[Applications](../applications/index.md)** - Use validated models
- **[Examples](../../examples/validation/ground-truth.md)** - Working code

---

**Continue to:** [Subgraph Patterns](subgraph-patterns.md) →
