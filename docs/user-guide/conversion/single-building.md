# Single Building Conversion

Detailed guide to converting individual buildings from CSV to Brick format.

## Overview

Single building conversion gives you precise control over the conversion process. It's ideal for:

- **Development and testing** - Work with one building at a time
- **Custom workflows** - Integrate into your own scripts
- **Detailed inspection** - Examine the output carefully
- **Targeted conversion** - Convert specific buildings

## Basic Usage

### Minimal Example

The simplest possible conversion:

```python
from hhw_brick import CSVToBrickConverter

converter = CSVToBrickConverter()
result = converter.convert_to_brick(
    metadata_csv="metadata.csv",
    vars_csv="vars_available_by_building.csv",
    building_tag="105",
    output_path="building_105.ttl"
)

print(f"✓ Created {len(result)} RDF triples")
```

This will:
1. Read building #105 from the CSV files
2. Auto-detect the system type
3. Create appropriate Brick entities
4. Save to `building_105.ttl`

### Complete Example

With all parameters:

```python
from hhw_brick import CSVToBrickConverter

converter = CSVToBrickConverter()

result = converter.convert_to_brick(
    metadata_csv="metadata.csv",
    vars_csv="vars_available_by_building.csv",
    building_tag="105",
    system_type="Non-condensing",  # Optional: specify type
    sensor_mapping="custom_mapping.yaml",  # Optional: custom mapping
    output_path="output/building_105_non-condensing.ttl"
)

# Check for warnings
if converter.validation_warnings:
    print("Warnings during conversion:")
    for warning in converter.validation_warnings:
        print(f"  ⚠ {warning}")

print(f"✓ Conversion complete: {len(result)} triples")
```

## Parameters Explained

### Required Parameters

#### metadata_csv

Path to the building metadata file.

```python
metadata_csv="path/to/metadata.csv"
```

**Format:**
```csv
tag,system,org
105,Non-condensing,Organization A
106,Condensing,Organization B
```

#### vars_csv

Path to the sensor availability file.

```python
vars_csv="path/to/vars_available_by_building.csv"
```

**Format:**
```csv
tag,hw_supply_temp,hw_return_temp,hw_flow
105,1,1,1
106,1,1,0
```

### Optional Parameters

#### building_tag

Specific building ID to convert.

```python
building_tag="105"  # Convert only building 105
```

- **Type:** String or Integer
- **Default:** `None` (converts all matching buildings)
- **When to use:** Convert a single specific building

**Example:**
```python
# Convert building 105 only
result = converter.convert_to_brick(
    metadata_csv="metadata.csv",
    vars_csv="vars.csv",
    building_tag="105",  # Specific building
    output_path="building_105.ttl"
)
```

#### system_type

Filter by HVAC system type.

```python
system_type="Condensing"  # Only condensing systems
```

- **Type:** String
- **Default:** `None` (auto-detect from metadata)
- **Options:** `"Boiler"`, `"Non-condensing"`, `"Condensing"`, `"District HW"`, `"District Steam"`
- **Case insensitive**

**When to use:**
- Converting multiple buildings of the same type
- Filtering a large dataset
- Validation (ensure building matches expected type)

**Example:**
```python
# Convert all condensing systems
result = converter.convert_to_brick(
    metadata_csv="metadata.csv",
    vars_csv="vars.csv",
    system_type="Condensing",
    output_path="all_condensing.ttl"
)
```

#### sensor_mapping

Custom sensor mapping file.

```python
sensor_mapping="my_custom_mapping.yaml"
```

- **Type:** String (file path)
- **Default:** Uses built-in mapping
- **Format:** YAML file

See [Sensor Mapping](sensor-mapping.md) for details.

#### output_path

Where to save the generated Brick model.

```python
output_path="output/building_105.ttl"
```

- **Type:** String (file path)
- **Default:** `"output.ttl"`
- **Format:** Creates TTL (Turtle) format file

## Return Value

The `convert_to_brick()` method returns an **RDFLib Graph** object.

```python
result = converter.convert_to_brick(...)

# Result is an rdflib.Graph
print(type(result))  # <class 'rdflib.graph.Graph'>
print(len(result))   # Number of RDF triples

# Query the graph
for s, p, o in result:
    print(f"{s} {p} {o}")
```

### Working with the Graph

```python
from rdflib import Namespace

result = converter.convert_to_brick(
    metadata_csv="metadata.csv",
    vars_csv="vars.csv",
    building_tag="105",
    output_path="building_105.ttl"
)

# Define namespaces
BRICK = Namespace("https://brickschema.org/schema/Brick#")

# Query for equipment
query = """
PREFIX brick: <https://brickschema.org/schema/Brick#>

SELECT ?equip ?type WHERE {
    ?equip a ?type .
    FILTER(STRSTARTS(STR(?type), STR(brick:)))
}
"""

print("Equipment in model:")
for row in result.query(query):
    equip_name = str(row.equip).split('#')[-1]
    type_name = str(row.type).split('#')[-1]
    print(f"  - {equip_name}: {type_name}")

# Serialize in different formats
result.serialize("output.xml", format="xml")
result.serialize("output.json", format="json-ld")
result.serialize("output.nt", format="nt")  # N-Triples
```

## Step-by-Step Workflow

### Step 1: Prepare Data

Ensure your CSV files are ready:

```python
import pandas as pd

# Check metadata
metadata = pd.read_csv("metadata.csv")
print("Buildings in metadata:")
print(metadata[['tag', 'system', 'org']])

# Check vars
vars_df = pd.read_csv("vars_available_by_building.csv")
print("\nSensors available:")
print(vars_df.head())
```

### Step 2: Initialize Converter

```python
from hhw_brick import CSVToBrickConverter

converter = CSVToBrickConverter()
```

The converter initializes with:
- Default namespaces (Brick, REC, etc.)
- Empty RDF graph
- Built-in sensor mapping

### Step 3: Convert

```python
result = converter.convert_to_brick(
    metadata_csv="metadata.csv",
    vars_csv="vars_available_by_building.csv",
    building_tag="105",
    output_path="building_105.ttl"
)
```

During conversion:
1. ✓ Reads CSV files
2. ✓ Finds building #105
3. ✓ Identifies system type
4. ✓ Creates building entity
5. ✓ Creates equipment entities
6. ✓ Creates sensor/point entities
7. ✓ Adds relationships
8. ✓ Writes to file

### Step 4: Validate Output

```python
from hhw_brick import BrickModelValidator

validator = BrickModelValidator()
is_valid, report = validator.validate_model("building_105.ttl")

if is_valid:
    print("✓ Model is valid!")
else:
    print("Validation report:")
    print(report)
```

### Step 5: Inspect Results

```python
from rdflib import Graph

# Load the model
g = Graph()
g.parse("building_105.ttl", format="turtle")

# Count entities
print(f"Total triples: {len(g)}")

# List all equipment
query = """
PREFIX brick: <https://brickschema.org/schema/Brick#>

SELECT DISTINCT ?type WHERE {
    ?equip a ?type .
    FILTER(STRSTARTS(STR(?type), STR(brick:)))
}
"""

print("\nEquipment types:")
for row in g.query(query):
    print(f"  - {str(row.type).split('#')[-1]}")
```

## Common Patterns

### Pattern 1: Convert Multiple Buildings Sequentially

```python
"""
Convert multiple specific buildings one by one
"""
from hhw_brick import CSVToBrickConverter

converter = CSVToBrickConverter()
building_ids = ["105", "106", "107", "108"]

for building_id in building_ids:
    print(f"Converting building {building_id}...")
    
    try:
        result = converter.convert_to_brick(
            metadata_csv="metadata.csv",
            vars_csv="vars.csv",
            building_tag=building_id,
            output_path=f"output/building_{building_id}.ttl"
        )
        
        print(f"  ✓ Success: {len(result)} triples")
        
    except Exception as e:
        print(f"  ✗ Failed: {e}")
    
    # Clear graph for next building
    converter.graph = converter.graph.__class__()
```

### Pattern 2: Conditional Conversion

```python
"""
Convert only if building meets criteria
"""
import pandas as pd
from hhw_brick import CSVToBrickConverter

metadata = pd.read_csv("metadata.csv")
converter = CSVToBrickConverter()

for _, building in metadata.iterrows():
    building_id = str(int(building['tag']))
    system = building['system']
    
    # Only convert condensing systems
    if 'condensing' in system.lower():
        print(f"Converting {building_id} ({system})...")
        
        result = converter.convert_to_brick(
            metadata_csv="metadata.csv",
            vars_csv="vars.csv",
            building_tag=building_id,
            output_path=f"condensing/building_{building_id}.ttl"
        )
        
        print(f"  ✓ {len(result)} triples")
```

### Pattern 3: Conversion with Validation

```python
"""
Convert and validate in one workflow
"""
from hhw_brick import CSVToBrickConverter, BrickModelValidator

def convert_and_validate(building_id):
    """Convert a building and validate the result."""
    
    # Convert
    converter = CSVToBrickConverter()
    output_file = f"building_{building_id}.ttl"
    
    result = converter.convert_to_brick(
        metadata_csv="metadata.csv",
        vars_csv="vars.csv",
        building_tag=building_id,
        output_path=output_file
    )
    
    print(f"Converted: {len(result)} triples")
    
    # Validate
    validator = BrickModelValidator()
    is_valid, report = validator.validate_model(output_file)
    
    if is_valid:
        print("✓ Validation passed")
        return True, output_file
    else:
        print("⚠ Validation warnings:")
        for warning in report.get('warnings', []):
            print(f"  - {warning}")
        return False, output_file

# Use it
success, file = convert_and_validate("105")
```

## Advanced Usage

### Custom Output Processing

```python
"""
Process the graph before saving
"""
from hhw_brick import CSVToBrickConverter
from rdflib import Namespace, Literal

converter = CSVToBrickConverter()
result = converter.convert_to_brick(
    metadata_csv="metadata.csv",
    vars_csv="vars.csv",
    building_tag="105",
    output_path="temp.ttl"
)

# Add custom metadata
HHWS = Namespace("https://hhws.example.org#")
building_uri = HHWS.Building_105

result.add((
    building_uri,
    HHWS.conversionDate,
    Literal("2025-10-30")
))

result.add((
    building_uri,
    HHWS.conversionTool,
    Literal("HHW Brick Application v0.2.0")
))

# Save with custom metadata
result.serialize("building_105_annotated.ttl", format="turtle")
```

### Merging Multiple Buildings

```python
"""
Combine multiple buildings into one graph
"""
from hhw_brick import CSVToBrickConverter
from rdflib import Graph

converter = CSVToBrickConverter()
combined = Graph()

# Bind namespaces
for prefix, namespace in converter.graph.namespace_manager.namespaces():
    combined.bind(prefix, namespace)

# Convert and merge multiple buildings
for building_id in ["105", "106", "107"]:
    result = converter.convert_to_brick(
        metadata_csv="metadata.csv",
        vars_csv="vars.csv",
        building_tag=building_id,
        output_path=f"temp_{building_id}.ttl"
    )
    
    # Add to combined graph
    combined += result
    
    print(f"Added building {building_id}: {len(result)} triples")

# Save combined graph
combined.serialize("campus_model.ttl", format="turtle")
print(f"\nCombined model: {len(combined)} total triples")
```

## Troubleshooting

### Issue: "No data found for building tag"

**Cause:** Building ID doesn't exist in CSV files

**Solution:**
```python
import pandas as pd

# Check which buildings exist
metadata = pd.read_csv("metadata.csv")
print("Available building IDs:")
print(metadata['tag'].tolist())

# Then use a valid ID
result = converter.convert_to_brick(
    metadata_csv="metadata.csv",
    vars_csv="vars.csv",
    building_tag="105",  # Must be in the list above
    output_path="output.ttl"
)
```

### Issue: Conversion warnings

**Cause:** Some data issues (usually minor)

**Solution:**
```python
converter = CSVToBrickConverter()
result = converter.convert_to_brick(...)

# Check warnings
if converter.validation_warnings:
    print("Conversion completed with warnings:")
    for w in converter.validation_warnings:
        print(f"  {w}")
    print("\nThese are usually safe to ignore.")
```

### Issue: Empty output file

**Cause:** No matching data or wrong filters

**Solution:**
```python
# Don't use system_type filter unless needed
result = converter.convert_to_brick(
    metadata_csv="metadata.csv",
    vars_csv="vars.csv",
    building_tag="105",
    # system_type="Condensing",  # Remove this if not needed
    output_path="output.ttl"
)
```

## Performance Tips

### Memory Management

Clear the graph between conversions:

```python
converter = CSVToBrickConverter()

for building_id in range(105, 200):
    result = converter.convert_to_brick(...)
    
    # Clear for next iteration
    converter.graph = converter.graph.__class__()
```

### Batch vs Sequential

For many buildings, use BatchConverter instead:

```python
# Instead of this:
for building_id in all_buildings:
    converter.convert_to_brick(building_tag=building_id, ...)

# Use this:
from hhw_brick import BatchConverter
batch = BatchConverter()
batch.convert_all_buildings(...)
```

See [Batch Conversion](batch-conversion.md) for details.

## Next Steps

- **[Batch Conversion](batch-conversion.md)** - Convert multiple buildings efficiently
- **[System Types](system-types.md)** - Understand different HVAC systems
- **[Sensor Mapping](sensor-mapping.md)** - Customize sensor mappings
- **[Examples](../../examples/conversion/single-building.md)** - More code examples

---

**Continue to:** [Batch Conversion](batch-conversion.md) →

