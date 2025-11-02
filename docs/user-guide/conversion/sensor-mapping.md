# Sensor Mapping

Customize how CSV sensor columns map to Brick ontology classes.

## Overview

The sensor mapping file (`sensor_to_brick_mapping.yaml`) defines how CSV column names translate to Brick point classes. This allows you to:

- **Customize mappings** for your specific data
- **Add new sensor types** not in the default mapping
- **Modify Brick classes** for existing sensors
- **Document sensor meanings** with descriptions

## Default Mapping File

The package includes a default mapping at:
```
hhw_brick/conversion/sensor_to_brick_mapping.yaml
```

This is used automatically unless you provide a custom file.

## Mapping File Format

### YAML Structure

Each sensor mapping has four fields:

```yaml
sensor_name:
  brick_class: "brick:ClassName"
  description: "Human-readable description"
  unit: "UNIT_TYPE"
  equipment: "equipment_type"
```

### Example Entry

```yaml
hw_supply_temp:
  brick_class: "brick:Hot_Water_Supply_Temperature_Sensor"
  description: "Hot water supply temperature"
  unit: "DEG_C"
  equipment: "primary_loop"
```

### Fields Explained

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `brick_class` | Yes | Full Brick class name | `brick:Hot_Water_Supply_Temperature_Sensor` |
| `description` | Yes | Sensor description | `"Primary loop supply temperature"` |
| `unit` | No | Unit of measurement | `DEG_C`, `L_PER_MIN`, `KW` |
| `equipment` | No | Associated equipment | `boiler`, `heat_exchanger`, `pump` |

## Default Mappings

### Temperature Sensors

```yaml
# Primary Loop
hw_supply_temp:
  brick_class: "brick:Hot_Water_Supply_Temperature_Sensor"
  description: "Primary hot water supply temperature"
  unit: "DEG_C"
  equipment: "primary_loop"

hw_return_temp:
  brick_class: "brick:Hot_Water_Return_Temperature_Sensor"
  description: "Primary hot water return temperature"
  unit: "DEG_C"
  equipment: "primary_loop"

# Secondary Loop
secondary_supply_temp:
  brick_class: "brick:Hot_Water_Supply_Temperature_Sensor"
  description: "Secondary loop supply temperature"
  unit: "DEG_C"
  equipment: "secondary_loop"

secondary_return_temp:
  brick_class: "brick:Hot_Water_Return_Temperature_Sensor"
  description: "Secondary loop return temperature"
  unit: "DEG_C"
  equipment: "secondary_loop"

# Outdoor
outdoor_temp:
  brick_class: "brick:Outside_Air_Temperature_Sensor"
  description: "Outdoor air temperature"
  unit: "DEG_C"
  equipment: "building"
```

### Flow Sensors

```yaml
hw_flow:
  brick_class: "brick:Water_Flow_Sensor"
  description: "Primary hot water flow rate"
  unit: "L_PER_MIN"
  equipment: "primary_loop"

secondary_flow:
  brick_class: "brick:Water_Flow_Sensor"
  description: "Secondary loop flow rate"
  unit: "L_PER_MIN"
  equipment: "secondary_loop"
```

### Numbered Sensors (Boilers)

```yaml
sup1:
  brick_class: "brick:Leaving_Hot_Water_Temperature_Sensor"
  description: "Supply water temperature leaving boiler 1"
  unit: "DEG_C"
  equipment: "boiler"

ret1:
  brick_class: "brick:Entering_Hot_Water_Temperature_Sensor"
  description: "Return water temperature entering boiler 1"
  unit: "DEG_C"
  equipment: "boiler"

fire1:
  brick_class: "brick:Firing_Rate_Sensor"
  description: "Boiler 1 firing rate"
  unit: "PERCENT"
  equipment: "boiler"
```

### Pump Sensors

```yaml
pmp1_pwr:
  brick_class: "brick:Power_Sensor"
  description: "Pump 1 power consumption"
  unit: "KW"
  equipment: "pump"

pmp1_spd:
  brick_class: "brick:Speed_Sensor"
  description: "Pump 1 speed"
  unit: "PERCENT"
  equipment: "pump"

pmp1_vfd:
  brick_class: "brick:VFD_Enable_Command"
  description: "Pump 1 VFD enable status"
  unit: "BINARY"
  equipment: "pump"
```

### Valves

```yaml
hw_valve:
  brick_class: "brick:Heating_Valve"
  description: "Hot water control valve position"
  unit: "PERCENT"
  equipment: "valve"
```

## Creating Custom Mappings

### Step 1: Copy Default File

Start with the default as a template:

```bash
cp hhw_brick/conversion/sensor_to_brick_mapping.yaml custom_mapping.yaml
```

### Step 2: Edit Mappings

Open `custom_mapping.yaml` and modify:

```yaml
# Add your custom sensors
chilled_water_supply:
  brick_class: "brick:Chilled_Water_Supply_Temperature_Sensor"
  description: "Chilled water supply temperature"
  unit: "DEG_C"
  equipment: "chiller"

chilled_water_return:
  brick_class: "brick:Chilled_Water_Return_Temperature_Sensor"
  description: "Chilled water return temperature"
  unit: "DEG_C"
  equipment: "chiller"

# Modify existing mappings
outdoor_temp:
  brick_class: "brick:Outside_Air_Temperature_Sensor"
  description: "Custom outdoor sensor at roof level"  # Changed
  unit: "DEG_F"  # Changed to Fahrenheit
  equipment: "building"
```

### Step 3: Use Custom Mapping

```python
from hhw_brick import CSVToBrickConverter

converter = CSVToBrickConverter()
result = converter.convert_to_brick(
    metadata_csv="metadata.csv",
    vars_csv="vars.csv",
    sensor_mapping="custom_mapping.yaml",  # Your custom file
    output_path="output.ttl"
)
```

## Common Customizations

### Add Building-Specific Sensors

Your building has unique sensors:

```yaml
# custom_mapping.yaml

# Add solar collector sensors
solar_panel_temp:
  brick_class: "brick:Solar_Panel_Temperature_Sensor"
  description: "Solar thermal panel temperature"
  unit: "DEG_C"
  equipment: "solar_collector"

solar_flow:
  brick_class: "brick:Water_Flow_Sensor"
  description: "Solar collector flow rate"
  unit: "L_PER_MIN"
  equipment: "solar_collector"

# Add thermal storage sensors
storage_tank_top:
  brick_class: "brick:Temperature_Sensor"
  description: "Thermal storage tank top temperature"
  unit: "DEG_C"
  equipment: "thermal_storage"

storage_tank_bottom:
  brick_class: "brick:Temperature_Sensor"
  description: "Thermal storage tank bottom temperature"
  unit: "DEG_C"
  equipment: "thermal_storage"
```

### Change Units

Convert between measurement systems:

```yaml
# Use Fahrenheit instead of Celsius
hw_supply_temp:
  brick_class: "brick:Hot_Water_Supply_Temperature_Sensor"
  description: "Hot water supply temperature"
  unit: "DEG_F"  # Changed from DEG_C
  equipment: "primary_loop"

# Use gallons per minute instead of liters
hw_flow:
  brick_class: "brick:Water_Flow_Sensor"
  description: "Primary hot water flow rate"
  unit: "GAL_PER_MIN"  # Changed from L_PER_MIN
  equipment: "primary_loop"
```

### Use More Specific Classes

Brick has many specialized classes:

```yaml
# Instead of generic Temperature_Sensor
# Use specific class:
supply_temp:
  brick_class: "brick:Leaving_Hot_Water_Temperature_Sensor"  # Specific
  # vs brick:Temperature_Sensor (generic)
  description: "Hot water leaving temperature"
  unit: "DEG_C"
  equipment: "boiler"

# Instead of generic Sensor
# Use specific measurement type:
energy_meter:
  brick_class: "brick:Thermal_Energy_Sensor"  # Specific
  # vs brick:Sensor (generic)
  description: "Thermal energy meter"
  unit: "KWH"
  equipment: "primary_loop"
```

## Brick Class Reference

### Common Brick Classes

#### Temperature

- `brick:Temperature_Sensor` - Generic
- `brick:Hot_Water_Supply_Temperature_Sensor` - HW supply
- `brick:Hot_Water_Return_Temperature_Sensor` - HW return
- `brick:Leaving_Hot_Water_Temperature_Sensor` - Equipment leaving
- `brick:Entering_Hot_Water_Temperature_Sensor` - Equipment entering
- `brick:Outside_Air_Temperature_Sensor` - Outdoor
- `brick:Chilled_Water_Supply_Temperature_Sensor` - CHW supply
- `brick:Chilled_Water_Return_Temperature_Sensor` - CHW return

#### Flow

- `brick:Water_Flow_Sensor` - Water flow rate
- `brick:Air_Flow_Sensor` - Air flow rate
- `brick:Steam_Flow_Sensor` - Steam flow

#### Pressure

- `brick:Water_Pressure_Sensor` - Water pressure
- `brick:Steam_Pressure_Sensor` - Steam pressure
- `brick:Differential_Pressure_Sensor` - Pressure difference

#### Power/Energy

- `brick:Power_Sensor` - Electrical power
- `brick:Energy_Sensor` - Energy consumption
- `brick:Thermal_Power_Sensor` - Thermal power
- `brick:Thermal_Energy_Sensor` - Thermal energy

#### Control

- `brick:Valve_Command` - Valve position
- `brick:Heating_Valve` - Heating valve
- `brick:VFD_Enable_Command` - VFD status
- `brick:Speed_Setpoint` - Speed setpoint

#### Status

- `brick:Run_Status` - Equipment running
- `brick:Enable_Status` - Equipment enabled
- `brick:Alarm_Status` - Alarm condition

### Finding Brick Classes

**Browse online:**
[Brick Schema Explorer](https://explore.brickschema.org/)

**Search in Python:**
```python
from brickschema import Graph

g = Graph(load_brick=True)

# Find all sensor types
query = """
PREFIX brick: <https://brickschema.org/schema/Brick#>
SELECT ?sensor WHERE {
    ?sensor rdfs:subClassOf* brick:Sensor .
}
"""

for row in g.query(query):
    print(row.sensor)
```

## Validation

### Check Your Mapping

Validate mapping file structure:

```python
import yaml

# Load mapping
with open('custom_mapping.yaml', 'r') as f:
    mapping = yaml.safe_load(f)

# Check required fields
for sensor, config in mapping.items():
    if 'brick_class' not in config:
        print(f"❌ {sensor}: missing brick_class")
    if 'description' not in config:
        print(f"⚠️  {sensor}: missing description (optional)")
    
    # Check brick_class format
    if not config['brick_class'].startswith('brick:'):
        print(f"⚠️  {sensor}: brick_class should start with 'brick:'")
```

### Test Custom Mapping

Test with a small dataset:

```python
from hhw_brick import CSVToBrickConverter

converter = CSVToBrickConverter()

try:
    result = converter.convert_to_brick(
        metadata_csv="test_metadata.csv",
        vars_csv="test_vars.csv",
        building_tag="105",
        sensor_mapping="custom_mapping.yaml",
        output_path="test_output.ttl"
    )
    print(f"✓ Custom mapping works! Created {len(result)} triples")
except Exception as e:
    print(f"❌ Error with custom mapping: {e}")
```

## Complete Custom Mapping Example

### Building with Geothermal System

```yaml
# geothermal_mapping.yaml

# Geothermal loop sensors
geo_source_supply:
  brick_class: "brick:Leaving_Water_Temperature_Sensor"
  description: "Geothermal source loop supply temperature"
  unit: "DEG_C"
  equipment: "geothermal_loop"

geo_source_return:
  brick_class: "brick:Entering_Water_Temperature_Sensor"
  description: "Geothermal source loop return temperature"
  unit: "DEG_C"
  equipment: "geothermal_loop"

geo_flow:
  brick_class: "brick:Water_Flow_Sensor"
  description: "Geothermal loop flow rate"
  unit: "L_PER_MIN"
  equipment: "geothermal_loop"

# Heat pump sensors
hp_leaving_temp:
  brick_class: "brick:Leaving_Hot_Water_Temperature_Sensor"
  description: "Heat pump leaving water temperature"
  unit: "DEG_C"
  equipment: "heat_pump"

hp_entering_temp:
  brick_class: "brick:Entering_Hot_Water_Temperature_Sensor"
  description: "Heat pump entering water temperature"
  unit: "DEG_C"
  equipment: "heat_pump"

hp_power:
  brick_class: "brick:Power_Sensor"
  description: "Heat pump electrical power"
  unit: "KW"
  equipment: "heat_pump"

hp_cop:
  brick_class: "brick:Sensor"
  description: "Heat pump coefficient of performance"
  unit: "DIMENSIONLESS"
  equipment: "heat_pump"

# Building loop (same as standard)
hw_supply_temp:
  brick_class: "brick:Hot_Water_Supply_Temperature_Sensor"
  description: "Building hot water supply"
  unit: "DEG_C"
  equipment: "building_loop"

hw_return_temp:
  brick_class: "brick:Hot_Water_Return_Temperature_Sensor"
  description: "Building hot water return"
  unit: "DEG_C"
  equipment: "building_loop"
```

### Usage

```python
from hhw_brick import CSVToBrickConverter

converter = CSVToBrickConverter()
result = converter.convert_to_brick(
    metadata_csv="geothermal_buildings.csv",
    vars_csv="geothermal_sensors.csv",
    building_tag="205",
    sensor_mapping="geothermal_mapping.yaml",
    output_path="geothermal_building_205.ttl"
)
```

## Troubleshooting

### Issue: "Unknown sensor type"

**Cause:** Sensor in CSV not in mapping file

**Solution:** Add it to your custom mapping:
```yaml
new_sensor:
  brick_class: "brick:Sensor"
  description: "New sensor type"
  unit: "UNIT"
  equipment: "equipment_type"
```

### Issue: "Invalid Brick class"

**Cause:** Brick class doesn't exist

**Solution:** Check class name at [Brick Explorer](https://explore.brickschema.org/)

```yaml
# Wrong:
temp_sensor:
  brick_class: "brick:TemperatureSensor"  # No such class

# Right:
temp_sensor:
  brick_class: "brick:Temperature_Sensor"  # Underscores
```

### Issue: Mapping not being used

**Cause:** File path incorrect

**Solution:**
```python
import os

# Check file exists
mapping_file = "custom_mapping.yaml"
if not os.path.exists(mapping_file):
    print(f"❌ File not found: {mapping_file}")
else:
    print(f"✓ File exists: {os.path.abspath(mapping_file)}")

# Use absolute path
result = converter.convert_to_brick(
    metadata_csv="metadata.csv",
    vars_csv="vars.csv",
    sensor_mapping=os.path.abspath("custom_mapping.yaml"),
    output_path="output.ttl"
)
```

## Best Practices

### 1. Start with Default

Don't create from scratch:
```bash
# Copy default as starting point
cp hhw_brick/conversion/sensor_to_brick_mapping.yaml my_mapping.yaml

# Edit only what you need to change
```

### 2. Use Specific Classes

Prefer specific Brick classes over generic:
```yaml
# ✓ Good - Specific
supply_temp:
  brick_class: "brick:Leaving_Hot_Water_Temperature_Sensor"

# ✗ Avoid - Too generic
supply_temp:
  brick_class: "brick:Sensor"
```

### 3. Document Well

Write clear descriptions:
```yaml
# ✓ Good - Clear description
pmp1_vfd:
  brick_class: "brick:VFD_Enable_Command"
  description: "Primary pump 1 variable frequency drive enable status"
  unit: "BINARY"
  equipment: "pump"

# ✗ Avoid - Vague
pmp1_vfd:
  brick_class: "brick:VFD_Enable_Command"
  description: "VFD"  # Too brief
  unit: "BINARY"
  equipment: "pump"
```

### 4. Version Control

Keep mapping files in version control:
```bash
git add custom_mapping.yaml
git commit -m "Add geothermal sensor mappings"
```

### 5. Test Thoroughly

Test with sample data before production use.

## Next Steps

- **[Validation](../validation/index.md)** - Validate converted models
- **[Applications](../applications/index.md)** - Run analytics
- **[Examples](../../examples/conversion/custom-mapping.md)** - More examples

---

**Conversion documentation complete!** 🎉

Continue to [Validation Guide](../validation/index.md) →

