# CSV Data Format

Prepare your CSV files for Brick model conversion and analytics.

> 📊 **Reference Dataset**: [Hydronic Heating Systems in 216 Commercial Buildings](https://doi.org/10.5061/dryad.t4b8gtj8n)  
> 📄 **Research Paper**: [Raftery et al. (2024), *Energy and Buildings*](https://linkinghub.elsevier.com/retrieve/pii/S0378778824006595)

---

## Required Files

### For Conversion (Brick Model Generation)

1. **`metadata.csv`** - Building characteristics
2. **`vars_available_by_building.csv`** - Sensor availability (which sensors exist)

### For Analytics (Optional)

3. **Timeseries CSV files** - Actual sensor measurements over time (e.g., `105hhw_system_data.csv`)

---

## File 1: metadata.csv

### Minimum Required Columns

| Column | Description | Example |
|--------|-------------|---------|
| `tag` | Unique building ID | `105` |
| `system` | Heating system type | `Non-condensing` |

### System Types (Must Use One)

- `Condensing` - Condensing gas boiler
- `Non-condensing` - Non-condensing gas boiler  
- `Boiler` - Boiler (type unknown)
- `District HW` - District hot water system
- `District Steam` - District steam system

### Optional Metadata Columns

| Column | Description | Type |
|--------|-------------|------|
| `org` | Organization identifier | string |
| `area` | Gross floor area (m²) | float |
| `year` | Year of construction | integer |
| `bldg_type` | Building type | string |
| `climate` | ASHRAE climate zone | string |
| `t_hdd` | Heating design day temp (°C) | float |
| `b_number` | Number of boilers | integer |
| `b_manufacturer` | Boiler manufacturer | string |
| `b_model` | Boiler model | string |
| `b_input` | Boiler input power (W) | float |
| `b_output` | Boiler output power (W) | float |
| `b_efficiency` | Boiler efficiency (fraction) | float |
| `b_min_turndown` | Min turndown (fraction) | float |
| `b_min_flow` | Min flow requirement (l/s) | float |
| `b_redundancy` | Redundancy level (fraction) | float |
| `design_supply` | Design supply temp (°C) | float |
| `design_return` | Design return temp (°C) | float |

### Minimum Example

| tag | system |
|-----|--------|
| 105 | Non-condensing |
| 127 | Condensing |

### Complete Example

| tag | system | org | area | bldg_type | year | b_number | design_supply | design_return |
|-----|--------|-----|------|-----------|------|----------|---------------|---------------|
| 29 | District HW | Z | 13000 | EventSpace | 1960 | NA | NA | NA |
| 53 | Condensing | X | 7700 | Museum | 2020 | 2 | 71.1 | 54.4 |
| 105 | Non-condensing | H | 46000 | Office | 1980 | 3 | 87.8 | NA |
| 127 | Condensing | M | 26000 | Other | 2020 | 2 | 60 | 37.8 |

---

## File 2: vars_available_by_building.csv

### Purpose

**Indicates which sensor types are available** for each building (not the actual data values).

### Required Column Order

⚠️ **IMPORTANT**: The converter **skips the first 3 columns** and treats all remaining columns as sensor availability flags.

**Standard format** (matching test fixtures):

| Column Position | Column Name | Required |
|----------------|-------------|----------|
| 1 | `tag` | ✅ Yes |
| 2 | `org` | Optional (ignored) |
| 3 | `datetime` | Optional (ignored) |
| 4+ | Sensor columns | Sensor availability |

**Minimum format** (if you omit `org` and `datetime`):

You can use any placeholder columns in positions 2-3, or structure your file to have `tag` first, then two dummy columns, then sensors.

### Sensor Availability Columns

**Values**:
- `1` or `1.0` = Sensor exists for this building
- `0`, blank, or missing = Sensor does not exist

**Temperature Sensors**:
- `sup`, `ret` - Primary supply/return temperature
- `sup1`-`sup4`, `ret1`-`ret4` - Individual boiler temperatures
- `supp`, `retp` - Primary circuit temperatures
- `t_out` - Outdoor air temperature
- `sup_stpt` - Supply temperature setpoint

**Flow & Pressure**:
- `flow` - Building flow rate
- `flowp` - Primary circuit flow
- `dp` - Differential pressure
- `dp_stpt` - Differential pressure setpoint

**Heating Power**:
- `hw` - Heating power/load

**Pump Data**:
- `pmp1_pwr`, `pmp2_pwr` - Pump power consumption
- `pmp1_spd`, `pmp2_spd` - Pump speed
- `pmp1_vfd`, `pmp2_vfd` - VFD output frequency
- `pmp_spd` - Generic pump speed

**Boiler Data**:
- `fire1`-`fire4` - Individual boiler firing rates

**System State**:
- `enab` - System enable signal
- `oper` - System operating state (estimated)

**Energy Consumption**:
- `gas` - Natural gas consumption (boiler plant)
- `gas_u` - Natural gas consumption (utility meter)

### Minimum Example

⚠️ **Must have at least 3 columns before sensor columns**:

| tag | org | datetime | ret | sup |
|-----|-----|----------|-----|-----|
| 105 | A | 1 | 1 | 1 |
| 127 | B | 1 | 1 | 1 |

Or use placeholder columns:

| tag | placeholder1 | placeholder2 | ret | sup |
|-----|--------------|--------------|-----|-----|
| 105 | - | - | 1 | 1 |
| 127 | - | - | 1 | 1 |

### Complete Example

| tag | org | datetime | ret | sup | hw | flow | t_out | pmp1_pwr | enab | oper |
|-----|-----|----------|-----|-----|-------|------|-------|----------|------|------|
| 29 | Z | 1 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0 | 0 | 1 |
| 53 | X | 1 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1 |
| 105 | H | 1 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0 | 1 |
| 127 | M | 1 | 1.0 | 1.0 | 1.0 | 0 | 1.0 | 1.0 | 0 | 1 |

---

## File 3: Timeseries Data (For Analytics)

### Purpose

**Actual sensor measurements over time** for running analytics applications.

### File Naming

Format: `{building_tag}hhw_system_data.csv`

Examples:
- `105hhw_system_data.csv` - Data for building 105
- `127hhw_system_data.csv` - Data for building 127

### Required Columns

| Column | Description | Type |
|--------|-------------|------|
| `dt` | Local date | date (YYYY-MM-DD) |
| `datetime_UTC` | UTC timestamp | ISO8601 string |

### Optional Time Features

| Column | Description |
|--------|-------------|
| `yr` | Year |
| `season` | Season (Winter, Spring, Summer, Fall) |
| `mnth` | Month (Jan, Feb, ...) |
| `wd` | Weekday (Mon, Tue, ...) |
| `hr` | Hour of day (0-23) |

### Sensor Data Columns

**Temperature (°C)**:
- `sup` - Supply water temperature
- `ret` - Return water temperature
- `sup_stpt` - Supply temperature setpoint
- `t_out` - Outdoor air temperature

**Flow (l/s)**:
- `flow` - Water flow rate

**Power (W)**:
- `hw` - Heating power/load

**System State**:
- `oper` - Operating state (0-1, fractional values allowed)

### Example

| dt | datetime_UTC | sup | ret | flow | hw | oper | t_out |
|----|--------------|-----|-----|------|-------|------|-------|
| 2020-02-05 | 2020-02-05T13:00:00Z | 85.2 | 72.1 | 12.5 | 685000 | 1 | 7.5 |
| 2020-02-05 | 2020-02-05T14:00:00Z | 84.8 | 71.9 | 12.3 | 678000 | 1 | 7.6 |
| 2020-02-05 | 2020-02-05T15:00:00Z | 85.0 | 72.0 | 12.4 | 680000 | 1 | 8.2 |

**Note**:
- Typically hourly data
- `NA` values indicate missing data
- See [Timeseries Data Guide](https://github.com/CenterForTheBuiltEnvironment/HHW_brick/tree/main/tests/fixtures/TimeSeriesData) for examples

---

## Quick Validation

```python
import pandas as pd

# Check conversion files
meta = pd.read_csv("metadata.csv")
vars_df = pd.read_csv("vars_available_by_building.csv")

assert 'tag' in meta.columns, "Missing 'tag' in metadata.csv"
assert 'system' in meta.columns, "Missing 'system' in metadata.csv"
assert 'tag' in vars_df.columns, "Missing 'tag' in vars_available_by_building.csv"

print(f"✓ Buildings: {len(meta)}")
print(f"✓ Tags match: {set(meta['tag']) == set(vars_df['tag'])}")
print(f"✓ Available sensors: {[c for c in vars_df.columns if c not in ['tag','org','datetime']][:5]}...")

# Check timeseries file (if exists)
try:
    ts = pd.read_csv("105hhw_system_data.csv")
    print(f"✓ Timeseries records: {len(ts)}")
    print(f"✓ Timeseries columns: {list(ts.columns)}")
except FileNotFoundError:
    print("ℹ No timeseries file found (optional for conversion)")
```

---

## Common Issues

### ❌ Missing required column in metadata.csv

| tag |
|-----|
| 105 |

**Fix**: Add `system` column

| tag | system |
|-----|--------|
| 105 | Non-condensing |

### ❌ Invalid system type

| tag | system |
|-----|--------|
| 105 | MyBoiler |

**Fix**: Use valid system type

| tag | system |
|-----|--------|
| 105 | Non-condensing |

### ❌ Tag mismatch between files

```
metadata.csv has: 105, 127
vars.csv has: 105, 128
```

**Fix**: Ensure all tags match exactly

---

## Data Sources

- 📊 **Public Dataset**: [Dryad Repository](https://doi.org/10.5061/dryad.t4b8gtj8n) - 216 buildings
- 📄 **Research Paper**: [Raftery et al. (2024)](https://linkinghub.elsevier.com/retrieve/pii/S0378778824006595)
- 🧪 **Test Files**: [GitHub Fixtures](https://github.com/CenterForTheBuiltEnvironment/HHW_brick/tree/main/tests/fixtures)
- ⏱️ **Timeseries Examples**: [TimeSeriesData/](https://github.com/CenterForTheBuiltEnvironment/HHW_brick/tree/main/tests/fixtures/TimeSeriesData)

---

## Next Steps

- ⚡ [Quick Start](quick-start.md) - Convert your first building
- 📚 [Understanding Brick](understanding-brick.md) - Learn concepts

---

**Ready?** → [Start converting](quick-start.md)
