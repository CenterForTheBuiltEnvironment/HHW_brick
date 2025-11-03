# Understanding Brick Schema

Learn what Brick Schema is and why it matters for portable analytics.

---

## The Problem

Different buildings use different names for the same sensor:

| Building A | Building B | Building C |
|------------|------------|------------|
| `HW_Supply_Temp` | `SupplyTempHotWater` | `HWST_01` |

**Result**: Custom code for EACH building 🔴

---

## The Solution

Brick provides **one standard name**:

```
All buildings → brick:Hot_Water_Supply_Temperature_Sensor
```

**Result**: Code ONCE, works EVERYWHERE ✅

---

## Real Example

From [official Brick documentation](https://brickschema.org/):

![Brick Schema Example](../Figures/understanding-brick/Brick Example.png)

**What you see**:

- 🏢 Buildings & spaces
- ⚙️ Equipment (boilers, pumps)
- 🌡️ Sensors (temperature, flow)
- 🔗 Relationships (connections)

**HHW Brick creates this from your CSV automatically!**

---

## How It Works

**Your CSV**:

```csv
tag,system,hw_supply_temp,hw_return_temp
105,Non-condensing,1,1
```

**Generated Brick**:

```turtle
# Equipment
:Boiler_01 a brick:Boiler .

# Sensors
:Supply_Temp a brick:Hot_Water_Supply_Temperature_Sensor .
:Return_Temp a brick:Hot_Water_Return_Temperature_Sensor .

# Relationships
:Boiler_01 brick:hasPoint :Supply_Temp, :Return_Temp .
```

---

## Why This Matters

**Traditional** ❌:

```python
# Building A
supply = data["HW_Supply_Temp"]

# Building B - different code!
supply = data["SupplyTempHotWater"]
```

**Brick** ✅:

```python
# Works on ALL buildings!
query = """
SELECT ?supply WHERE {
    ?supply a brick:Hot_Water_Supply_Temperature_Sensor .
}
"""
```

---

## Portable Analytics

```python
def analyze_any_building(brick_model):
    """Same code for building 1, 2, 3... 100!"""

    query = """
    SELECT ?supply ?return WHERE {
        ?supply a brick:Hot_Water_Supply_Temperature_Sensor .
        ?return a brick:Hot_Water_Return_Temperature_Sensor .
    }
    """
    # Auto-discovers sensors, calculates ΔT
```

**Time saved**: 90% reduction 🚀

---

## What HHW Brick Does

1. ✅ You provide CSV files
2. ✅ Converts to Brick Schema
3. ✅ Run analytics on ANY building

---

## FAQ

**Q: Do I need to know Brick/RDF/SPARQL?**  
**A**: No! HHW Brick handles everything.

**Q: What if my system isn't supported?**  
**A**: Use "Generic Boiler" or [request it](https://github.com/CenterForTheBuiltEnvironment/HHW_brick/issues).

---

## Learn More

- 🌐 [Brick Website](https://brickschema.org/)
- 🔍 [Browse Classes](https://explore.brickschema.org/)
- 📋 [CSV Format](csv-format.md)
- ⚡ [Quick Start](quick-start.md)

---

!!! success "Key Takeaway"
    Brick = **one language** for ALL buildings  
    → Write once, deploy everywhere 🚀

---

**Next**: [Prepare your CSV](csv-format.md) →
