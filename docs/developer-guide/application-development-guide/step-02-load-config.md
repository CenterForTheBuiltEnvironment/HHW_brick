# Application Development Tutorial - Step 2: Write load_config Function

In this step, you'll implement the `load_config()` function that loads configuration settings from YAML.

## Goal of This Step

Implement a simple but robust configuration loading function.

---

## Step 2.1: Add Imports to `app.py`

Open `app.py` and add the necessary imports at the top of the file.

**Copy this code to the beginning of `app.py`**:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
My First Application

Detailed description of your application functionality.

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

**Key Points**:
- `Path(__file__).parent` gets the current app directory
- `sys.path.insert(0, ...)` ensures Python can find HHW Brick utilities
- `__all__` defines what functions are exported

---

## Step 2.2: Implement load_config()

Now add the `load_config()` function below the imports.

**Copy this code into `app.py`**:

```python
def load_config(config_file=None):
    """
    Load configuration from YAML file

    Args:
        config_file (str|Path, optional): Path to config file.
            If None, uses config.yaml in application directory.

    Returns:
        dict: Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist

    Example:
        >>> config = load_config()  # Load default config.yaml
        >>> config = load_config("custom_config.yaml")  # Load custom config
    """
    # Use default config.yaml if no file specified
    if config_file is None:
        config_file = app_dir / "config.yaml"

    # Convert to Path object
    config_path = Path(config_file)

    # Check if file exists
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            f"Please ensure config.yaml exists in the application directory."
        )

    # Load YAML file
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Return config or empty dict if file is empty
    return config if config else {}
```

**Understanding the Code**:

1. **Default file handling**:
   ```python
   if config_file is None:
       config_file = app_dir / "config.yaml"
   ```
   If user doesn't specify a file, use the app's `config.yaml`.

2. **Path conversion**:
   ```python
   config_path = Path(config_file)
   ```
   Convert string paths to `Path` objects for better file handling.

3. **Existence check**:
   ```python
   if not config_path.exists():
       raise FileNotFoundError(...)
   ```
   Fail early with a clear error message if file is missing.

4. **YAML parsing**:
   ```python
   with open(config_path, "r", encoding="utf-8") as f:
       config = yaml.safe_load(f)
   ```
   `safe_load()` parses YAML safely without executing code.

5. **Empty file handling**:
   ```python
   return config if config else {}
   ```
   Return empty dict if YAML file is empty or contains only null.

---

## Step 2.3: Test load_config()

Create a simple test to verify your function works.

**Create a test file `test_config.py` in your app directory**:

```python
"""
Test script for load_config function
"""

from pathlib import Path
import sys

# Add parent directory to path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir.parent.parent.parent))

# Import the function
from hhw_brick.applications.my_first_app.app import load_config

def test_load_config():
    """Test loading default config"""
    print("Testing load_config()...")

    try:
        # Test 1: Load default config
        config = load_config()
        print(f"✓ Default config loaded successfully")
        print(f"  Keys: {list(config.keys())}")

        # Test 2: Check required sections
        assert "output" in config, "Missing 'output' section"
        assert "analysis" in config, "Missing 'analysis' section"
        assert "time_range" in config, "Missing 'time_range' section"
        print(f"✓ All required sections present")

        # Test 3: Check output settings
        assert config["output"]["generate_plots"] is not None
        assert config["output"]["generate_plotly_html"] is not None
        print(f"✓ Output settings validated")

        print("\n✅ All tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_load_config()
```

**Run the test**:

```bash
# Navigate to your app directory
cd hhw_brick/applications/my_first_app/

# Run the test
python test_config.py
```

**Expected output**:
```
Testing load_config()...
✓ Default config loaded successfully
  Keys: ['analysis', 'output', 'time_range']
✓ All required sections present
✓ Output settings validated

✅ All tests passed!
```

---

## Step 2.4: Handle Common Errors

Let's test error handling.

**Test with missing file**:

```python
# In test_config.py, add this test
def test_missing_file():
    """Test error handling for missing file"""
    print("\nTesting missing file handling...")

    try:
        config = load_config("nonexistent.yaml")
        print("❌ Should have raised FileNotFoundError")
    except FileNotFoundError as e:
        print(f"✓ Correctly raised FileNotFoundError")
        print(f"  Message: {str(e)[:50]}...")

test_missing_file()
```

**Expected behavior**: Should raise `FileNotFoundError` with helpful message.

---

## Step 2.5: Verify Your Implementation

Your `app.py` should now look like this:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
My First Application

Detailed description of your application functionality.

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


def load_config(config_file=None):
    """Load configuration from YAML file"""
    if config_file is None:
        config_file = app_dir / "config.yaml"

    config_path = Path(config_file)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            f"Please ensure config.yaml exists in the application directory."
        )

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config if config else {}


# qualify() and analyze() will be added in next steps
```

---

## Checkpoint

Before proceeding, verify:

- [x] Imports are at the top of `app.py`
- [x] `load_config()` function is implemented
- [x] Function has proper docstring
- [x] Test script runs successfully
- [x] Error handling works correctly

---

## Next Steps

✅ Configuration loading complete!

👉 Continue to [Step 3: Write qualify Function](./step-03-qualify.md)

---

## Common Issues

**Issue**: `ModuleNotFoundError: No module named 'yaml'`  
**Solution**: Install dependencies: `pip install -r requirements.txt`

**Issue**: `FileNotFoundError` when running test  
**Solution**: Make sure you created `config.yaml` in Step 1

**Issue**: `yaml.safe_load()` returns None  
**Solution**: Check if your `config.yaml` has content and valid YAML syntax

---

## Best Practices

✅ **DO**:
- Use `yaml.safe_load()` instead of `yaml.load()` for security
- Provide clear error messages
- Use `Path` objects for file handling
- Add docstrings to functions

❌ **DON'T**:
- Hardcode file paths
- Use `yaml.load()` (security risk)
- Silently fail on errors
- Forget to handle empty config files
