# Step 8: Testing Your Application

Create a comprehensive test suite for your application.

---

## 1. Create Test Script

Create `test_app.py` in your app directory:

```python
"""Comprehensive test suite"""
from pathlib import Path
import sys

app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir.parent.parent.parent))

from hhw_brick.applications.my_first_app.app import load_config, qualify, analyze

def test_load_config():
    """Test config loading"""
    print("\n" + "="*60)
    print("TEST 1: Load Config")
    print("="*60)

    try:
        config = load_config()
        assert "analysis" in config
        assert "output" in config
        print("✅ Config loaded")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_qualify():
    """Test qualification"""
    print("\n" + "="*60)
    print("TEST 2: Qualify")
    print("="*60)

    fixtures = Path(__file__).parent.parent.parent.parent / "tests" / "fixtures"
    brick_dir = fixtures / "Brick_Model_File"

    if not brick_dir.exists():
        print("⚠️  Test data not found")
        return True

    passed = 0
    for model_file in list(brick_dir.glob("*.ttl"))[:3]:  # Test first 3
        try:
            qualified, _ = qualify(str(model_file))
            if qualified:
                passed += 1
                print(f"✅ {model_file.name}")
        except Exception as e:
            print(f"❌ {model_file.name}: {e}")

    print(f"\n{passed} buildings qualified")
    return True

def test_analyze():
    """Test complete analysis"""
    print("\n" + "="*60)
    print("TEST 3: Analyze")
    print("="*60)

    fixtures = Path(__file__).parent.parent.parent.parent / "tests" / "fixtures"
    model = fixtures / "Brick_Model_File" / "building_29.ttl"
    data = fixtures / "TimeSeriesData" / "29hhw_system_data.csv"

    if not model.exists():
        print("⚠️  Test files not found")
        return True

    try:
        config = load_config()
        config["output"]["output_dir"] = "./test_output"

        results = analyze(str(model), str(data), config)

        if results:
            assert "stats" in results
            assert "data" in results
            print(f"\n✅ Analysis complete")
            print(f"  Points: {results['stats']['count']}")
            print(f"  Mean: {results['stats']['mean_temp_diff']:.2f}°C")
            return True
        return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "#"*60)
    print("# RUNNING TESTS")
    print("#"*60)

    results = [
        ("Config", test_load_config()),
        ("Qualify", test_qualify()),
        ("Analyze", test_analyze())
    ]

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")

    total = sum(1 for _, p in results if p)
    print(f"\n{total}/{len(results)} tests passed")

    return total == len(results)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
```

---

## 2. Run Tests

```bash
python test_app.py
```

**Expected output**:
```
============================================================
# RUNNING TESTS
============================================================

============================================================
TEST 1: Load Config
============================================================
✅ Config loaded

============================================================
TEST 2: Qualify
============================================================
✅ building_29.ttl
✅ building_105.ttl

2 buildings qualified

============================================================
TEST 3: Analyze
============================================================
✅ Analysis complete
  Points: 26013
  Mean: 0.60°C

============================================================
SUMMARY
============================================================
✅ PASS: Config
✅ PASS: Qualify
✅ PASS: Analyze

3/3 tests passed
```

---

## 3. Test with AppsManager

Verify integration:

```python
"""Test AppsManager integration"""
from hhw_brick import apps

# List apps
all_apps = apps.list_apps()
assert "my_first_app" in [a["name"] for a in all_apps]
print("✓ App discovered")

# Load app
app = apps.load_app("my_first_app")
print("✓ App loaded")

# Get config
config = apps.get_default_config("my_first_app")
print("✓ Config retrieved")
```

---

## Checkpoint

- [x] Test script created
- [x] All functions tested
- [x] Integration with AppsManager verified
- [x] All tests pass

---

## Next Step

👉 [Step 9: Deployment & Integration](./step-09-deployment.md)


In this step, you'll learn how to test your application to ensure it works correctly.

## Goal of This Step

- Test individual functions
- Test the complete workflow
- Handle errors gracefully
- Verify with multiple buildings

---

## Step 8.1: Create Test Script

Create `test_app.py` in your application directory:

```python
"""
Comprehensive test suite for my_first_app
"""

from pathlib import Path
import sys

# Add parent directory to path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir.parent.parent.parent))

from hhw_brick.applications.my_first_app.app import (
    load_config,
    qualify,
    analyze
)

def test_load_config():
    """Test configuration loading"""
    print("\n" + "="*60)
    print("TEST 1: Load Config")
    print("="*60)

    try:
        config = load_config()
        assert "analysis" in config
        assert "output" in config
        assert "time_range" in config
        print("✅ Config loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False


def test_qualify():
    """Test qualification function"""
    print("\n" + "="*60)
    print("TEST 2: Qualify Buildings")
    print("="*60)

    fixtures = Path(__file__).parent.parent.parent.parent / "tests" / "fixtures"
    brick_dir = fixtures / "Brick_Model_File"

    if not brick_dir.exists():
        print("⚠️  Test data not found, skipping")
        return True

    passed = 0
    failed = 0

    for model_file in brick_dir.glob("*.ttl"):
        try:
            qualified, details = qualify(str(model_file))
            if qualified:
                print(f"✅ {model_file.name}: QUALIFIED")
                passed += 1
            else:
                print(f"⚠️  {model_file.name}: Not qualified")
        except Exception as e:
            print(f"❌ {model_file.name}: ERROR - {e}")
            failed += 1

    print(f"\nResults: {passed} qualified, {failed} errors")
    return failed == 0


def test_analyze():
    """Test complete analysis workflow"""
    print("\n" + "="*60)
    print("TEST 3: Complete Analysis")
    print("="*60)

    fixtures = Path(__file__).parent.parent.parent.parent / "tests" / "fixtures"

    # Use a known good building
    model_file = fixtures / "Brick_Model_File" / "building_29.ttl"
    data_file = fixtures / "TimeSeriesData" / "29hhw_system_data.csv"

    if not model_file.exists() or not data_file.exists():
        print("⚠️  Test files not found, skipping")
        return True

    try:
        config = load_config()
        config["output"]["output_dir"] = "./test_output"
        config["output"]["generate_plots"] = True
        config["output"]["generate_plotly_html"] = True

        results = analyze(str(model_file), str(data_file), config)

        if results:
            assert "stats" in results
            assert "data" in results
            assert results["stats"]["count"] > 0

            print(f"\n✅ Analysis completed successfully")
            print(f"  Data points: {results['stats']['count']}")
            print(f"  Mean temp diff: {results['stats']['mean_temp_diff']:.2f}°C")
            return True
        else:
            print("❌ Analysis returned None")
            return False

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling with invalid inputs"""
    print("\n" + "="*60)
    print("TEST 4: Error Handling")
    print("="*60)

    try:
        # Test with non-existent file
        qualified, details = qualify("nonexistent.ttl")
        print("❌ Should have raised an error")
        return False
    except Exception as e:
        print(f"✅ Correctly handled invalid file: {type(e).__name__}")
        return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "#"*60)
    print("# RUNNING ALL TESTS")
    print("#"*60)

    results = []
    results.append(("Load Config", test_load_config()))
    results.append(("Qualify", test_qualify()))
    results.append(("Analyze", test_analyze()))
    results.append(("Error Handling", test_error_handling()))

    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(f"\n{total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
```

---

## Step 8.2: Run Tests

Run your test suite:

```bash
python test_app.py
```

**Expected Output**:
```
============================================================
# RUNNING ALL TESTS
============================================================

============================================================
TEST 1: Load Config
============================================================
✅ Config loaded successfully

============================================================
TEST 2: Qualify Buildings
============================================================
✅ building_29.ttl: QUALIFIED
✅ building_105.ttl: QUALIFIED
...

============================================================
TEST 3: Complete Analysis
============================================================
✅ Analysis completed successfully
  Data points: 26013
  Mean temp diff: 0.60°C

============================================================
TEST 4: Error Handling
============================================================
✅ Correctly handled invalid file: FileNotFoundError

============================================================
TEST SUMMARY
============================================================
✅ PASS: Load Config
✅ PASS: Qualify
✅ PASS: Analyze
✅ PASS: Error Handling

4/4 tests passed

🎉 ALL TESTS PASSED!
```

---

## Step 8.3: Integration Test with AppsManager

Test that your app works with the apps manager:

```python
def test_with_apps_manager():
    """Test app through AppsManager"""
    print("\n" + "="*60)
    print("TEST: AppsManager Integration")
    print("="*60)

    from hhw_brick import apps

    try:
        # List apps
        all_apps = apps.list_apps()
        app_names = [app["name"] for app in all_apps]

        if "my_first_app" in app_names:
            print("✅ App discovered by AppsManager")
        else:
            print("❌ App not found in app list")
            return False

        # Load app
        app = apps.load_app("my_first_app")
        print("✅ App loaded successfully")

        # Get default config
        config = apps.get_default_config("my_first_app")
        print("✅ Default config retrieved")

        # Get app info
        info = apps.get_app_info("my_first_app")
        print(f"✅ App info: {len(info['functions'])} functions")

        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False
```

---

## Step 8.4: Add Error Handling to Your App

Update your `analyze()` function to handle errors gracefully:

```python
def analyze(brick_model_path, timeseries_data_path, config):
    """Execute analysis workflow"""
    try:
        # Step 1: Qualify
        qualified, qualify_result = qualify(brick_model_path)
        if not qualified:
            print("[INFO] Building does not qualify for this analysis")
            return None

        # ...rest of implementation...

    except FileNotFoundError as e:
        print(f"[ERROR] File not found: {e}")
        return None
    except KeyError as e:
        print(f"[ERROR] Missing configuration key: {e}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return None
```

---

## Step 8.5: Validate Outputs

Add validation to ensure outputs are correct:

```python
def validate_results(results):
    """Validate analysis results"""
    if results is None:
        return False

    # Check structure
    if "stats" not in results or "data" not in results:
        print("❌ Invalid results structure")
        return False

    # Check stats
    stats = results["stats"]
    required_stats = [
        "count", "mean_temp_diff", "std_temp_diff",
        "min_temp_diff", "max_temp_diff"
    ]

    for stat in required_stats:
        if stat not in stats:
            print(f"❌ Missing stat: {stat}")
            return False

    # Check data
    data = results["data"]
    if data.empty:
        print("❌ No data in results")
        return False

    required_columns = ["supply", "return", "temp_diff", "hour", "weekday"]
    for col in required_columns:
        if col not in data.columns:
            print(f"❌ Missing column: {col}")
            return False

    print("✅ Results validation passed")
    return True
```

---

## Checkpoint

Before proceeding, verify:

- [x] Test script created
- [x] All functions tested individually
- [x] Complete workflow tested
- [x] Error handling tested
- [x] Integration with AppsManager tested
- [x] Output validation implemented
- [x] All tests pass

---

## Next Steps

✅ Testing complete!

👉 Continue to [Step 9: Deployment & Integration](./step-09-deployment.md)

---

## Testing Best Practices

### ✅ Do

- Test with multiple buildings
- Test error cases (missing files, bad data)
- Validate outputs
- Use assertions to check conditions
- Print clear success/failure messages

### ❌ Don't

- Skip error handling
- Test only with one building
- Ignore test failures
- Make tests dependent on each other
- Hardcode file paths

---

## Common Test Issues

**Issue**: Tests can't find test data  
**Solution**: Use `Path(__file__).parent` to get relative paths

**Issue**: Import errors  
**Solution**: Check `sys.path.insert(0, ...)` is correct

**Issue**: Tests pass but app fails in production  
**Solution**: Test with diverse buildings and edge cases

**Issue**: Plots not generated during tests  
**Solution**: Check output directory exists and is writable

---

## Summary

You've created a comprehensive test suite:

✅ **Unit Tests**: Test individual functions  
✅ **Integration Tests**: Test complete workflow  
✅ **Error Handling**: Handle failures gracefully  
✅ **Validation**: Ensure outputs are correct  
✅ **AppsManager**: Verify app integration  

Your app is now tested and ready for deployment!
