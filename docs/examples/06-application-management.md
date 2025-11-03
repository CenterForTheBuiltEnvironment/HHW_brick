# Example 06: Application Management

Discover, load, and inspect available analytics applications.

---

## What You'll Learn

- ✅ Discover available apps
- ✅ Load applications
- ✅ Inspect app requirements
- ✅ View app configuration

---

## Discover Apps

List all available analytics applications:

```python
from hhw_brick import apps

# List all apps
available = apps.list_apps()

for app_info in available:
    print(f"- {app_info['name']}: {app_info.get('description', '')}")
```

**Output**:
```
Available applications:
  - primary_loop_temp_diff
  - secondary_loop_temp_diff
```

---

## Load and Inspect App

```python
# Load an application
app = apps.load_app("secondary_loop_temp_diff")

# Get app info
info = app.get_info()
print(f"Name: {info['name']}")
print(f"Description: {info['description']}")
print(f"Required sensors: {info['required_brick_classes']}")
```

**Output**:
```
Name: secondary_loop_temp_diff
Description: Secondary loop temperature difference analysis
Required sensors:
  - brick:Hot_Water_Supply_Temperature_Sensor
  - brick:Hot_Water_Return_Temperature_Sensor
```

---

## Run Example

```bash
python examples/06_application_management.py
```

---

## Next Steps

- **Run analysis** → [Example 07: Run Application](07-run-application.md)

---

📂 **Source Code**: [`examples/06_application_management.py`](https://github.com/CenterForTheBuiltEnvironment/HHW_brick/blob/main/examples/06_application_management.py)
