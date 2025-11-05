# Step 2: Write load_config Function

Implement configuration loading from YAML files.

---

## 1. Add Imports to `app.py`

Start your `app.py` with these imports:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
My First Application

Temperature differential analysis for hot water systems.

Author: Your Name
"""

import sys
from pathlib import Path
import yaml

# Setup paths
app_dir = Path(__file__).parent
package_dir = app_dir.parent.parent.parent
sys.path.insert(0, str(package_dir))

# Export core functions
__all__ = ["qualify", "analyze", "load_config"]
```

**Why**:
- `Path(__file__).parent` - Gets current app directory
- `sys.path.insert()` - Allows importing HHW Brick utilities
- `__all__` - Defines public API

---

## 2. Implement load_config()

Add this function to load configuration from YAML:

```python
def load_config(config_file=None):
    """
    Load configuration from YAML file

    Args:
        config_file: Path to config file (default: config.yaml in app dir)

    Returns:
        dict: Configuration dictionary
    """
    if config_file is None:
        config_file = app_dir / "config.yaml"

    config_path = Path(config_file)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            f"Please ensure config.yaml exists."
        )

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config if config else {}
```

**How it works**:
1. Uses default `config.yaml` if no file specified
2. Checks if file exists, raises error if not
3. Loads YAML using `safe_load()` (secure)
4. Returns dictionary or empty dict if file is empty

---

## 3. Test load_config()

Create `test_config.py` in your app directory:

```python
"""Test configuration loading"""
from pathlib import Path
import sys

app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir.parent.parent.parent))

from hhw_brick.applications.my_first_app.app import load_config

# Test 1: Load default config
config = load_config()
assert "output" in config
assert "analysis" in config
print("✓ Config loaded successfully")
print(f"  Keys: {list(config.keys())}")

# Test 2: Check structure
assert config["output"]["generate_plots"] is not None
print("✓ Config structure valid")

print("\n✅ All tests passed!")
```

**Run test**:
```bash
python test_config.py
```

**Expected output**:
```
✓ Config loaded successfully
  Keys: ['analysis', 'output', 'time_range']
✓ Config structure valid

✅ All tests passed!
```

---

## Checkpoint

- [x] Imports added to `app.py`
- [x] `load_config()` function implemented
- [x] Test script runs successfully
- [x] Error handling works (try loading non-existent file)

---

## Common Issues

**`ModuleNotFoundError: No module named 'yaml'`**  
→ Run: `pip install pyyaml`

**`FileNotFoundError` when running test**  
→ Ensure `config.yaml` exists from Step 1

---

## Next Step

👉 [Step 3: SPARQL Query & qualify Function](./step-03-sparql-qualify.md)
