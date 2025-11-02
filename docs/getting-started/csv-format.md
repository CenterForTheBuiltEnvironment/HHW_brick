# CSV Data Format

Understanding the CSV file format for converting to Brick models.

## Two Required Files

1. **metadata.csv** - Building information
2. **vars_available_by_building.csv** - Sensor availability

## metadata.csv

### Minimum Required

```csv
tag,system,org
105,Non-condensing,Organization A
106,Condensing,Organization B
107,District HW,Organization C
```

### Real-World Example (with optional columns)

```csv
tag,org,area,bldg_type,year,system,b_number,design_supply,design_return
29,Z,13000,Other/EventSpace,1960,District HW,NA,NA,NA
53,X,7700,Other/Museum,2020,Condensing,2,71.1,54.4
105,H,46000,Office,1980,Non-condensing,3,87.8,NA
127,M,26000,Other,2020,Condensing,2,60,37.8
```

### Column Descriptions

**Required:**
- `tag` - Building ID (integer, unique)
- `system` - System type (see below)
- `org` - Organization name

**Optional but useful:**
- `area` - Building area (sq ft)
- `bldg_type` - Building type (Office, Lab, etc.)
- `year` - Year built
- `b_number` - Number of boilers
- `design_supply` - Design supply temperature (°C)
- `design_return` - Design return temperature (°C)

### System Types

Must be one of these 5 types (case-insensitive):

| System Type | Description |
|-------------|-------------|
| `Boiler` | Generic boiler system |
| `Non-condensing` | Standard efficiency boiler |
| `Condensing` | High efficiency boiler |
| `District HW` | Campus hot water |
| `District Steam` | District steam |

---

## vars_available_by_building.csv

### Purpose

Shows which sensors each building has.
- `1` = sensor exists
- `0` or empty = no sensor

### Minimum Example

```csv
tag,ret,sup,hw,flow,t_out
105,1,1,1,1,1
106,1,1,1,0,0
107,1,1,0,0,1
```

### Real-World Example (many sensors)

```csv
tag,ret,sup,sup1,ret1,fire1,sup2,ret2,fire2,hw,flow,pmp1_pwr,pmp2_pwr,t_out,enab
29,1,1,,,,,,,1,1,,,1,
53,1,1,1,,,,,,1,1,,,1,1
105,1,1,1,1,1,1,1,1,1,1,1,1,1,1
```

### Common Sensor Columns

**Temperature:**
```
sup, ret          # Primary supply/return
sup1-4, ret1-4    # Individual boiler temps
```

**Pumps:**
```
pmp1_pwr, pmp1_spd, pmp1_vfd    # Pump 1
pmp2_pwr, pmp2_spd, pmp2_vfd    # Pump 2
```

**Other:**
```
hw          # Hot water sensor
flow        # Flow rate
dp          # Differential pressure
fire1-4     # Boiler firing rates
t_out       # Outdoor temperature
enab        # Enable signal
```

**You can have 5 columns or 50 columns** - the converter automatically handles all available sensors!

---

## Quick Validation

```python
import pandas as pd

# Load files
meta = pd.read_csv("metadata.csv")
vars_df = pd.read_csv("vars_available_by_building.csv")

# Check basics
print("Buildings in metadata:", len(meta))
print("Buildings in vars:", len(vars_df))
print("Tags match:", set(meta['tag']) == set(vars_df['tag']))
print("Sensor types:", len(vars_df.columns) - 1)
```

---

## Common Issues & Solutions

### ❌ Issue: Missing required column

```csv
tag,system
105,Non-condensing
# Missing 'org' column!
```

✅ **Fix**: Add the `org` column
```csv
tag,system,org
105,Non-condensing,Organization A
```

### ❌ Issue: Invalid system type

```csv
tag,system,org
105,InvalidType,Org A
```

✅ **Fix**: Use one of the 5 supported types
```csv
tag,system,org
105,Non-condensing,Org A
```

### ❌ Issue: Tags don't match

```csv
# metadata.csv: has building 105
# vars.csv: has building 106
```

✅ **Fix**: Ensure tags match exactly in both files

---

## Next Steps

Ready to convert? See:

- [Quick Start](quick-start.md) - Convert your first building
- [Conversion Guide](../user-guide/conversion/single-building.md) - Detailed guide
- [Sensor Mapping](../user-guide/conversion/sensor-mapping.md) - Customize mappings
