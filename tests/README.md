# HHWS Brick Application Tests

This directory contains the test suite for the HHWS Brick Application package.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Shared pytest fixtures
├── fixtures/                # Test data
│   ├── metadata.csv         # Sample metadata
│   ├── vars_available_by_building.csv
│   └── TimeSeriesData/      # Sample time series data
├── test_conversion.py       # Tests for CSV to Brick conversion
├── test_validation.py       # Tests for model validation
├── test_workflow.py         # Tests for workflow orchestration
├── test_utils.py            # Tests for utility modules
└── test_cli.py              # Tests for command-line interface
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_conversion.py
```

### Run specific test class
```bash
pytest tests/test_conversion.py::TestCSVToBrickConverter
```

### Run specific test
```bash
pytest tests/test_conversion.py::TestCSVToBrickConverter::test_converter_initialization
```

### Run with verbose output
```bash
pytest -v
```

### Run with coverage
```bash
pytest --cov=hhws_brick_application --cov-report=html
```

## Test Categories

Tests are organized using markers:

- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Long-running tests
- `@pytest.mark.requires_network` - Tests requiring network access
- `@pytest.mark.requires_data` - Tests requiring external data

### Run tests by marker
```bash
pytest -m unit          # Run only unit tests
pytest -m "not slow"    # Run all except slow tests
```

## Fixtures

Common test fixtures are defined in `conftest.py`:

- `fixtures_dir` - Path to test fixtures directory
- `metadata_csv` - Path to test metadata CSV
- `vars_csv` - Path to test vars CSV
- `temp_output_dir` - Temporary directory for test outputs
- `sample_building_tag` - Sample building tag for testing
- `ground_truth_csv` - Path to ground truth data (if available)

## Writing New Tests

### Basic test structure
```python
import pytest
from hhws_brick_application import SomeClass

class TestSomeClass:
    """Test cases for SomeClass."""
    
    def test_something(self):
        """Test that something works."""
        obj = SomeClass()
        assert obj is not None
    
    def test_with_fixture(self, metadata_csv):
        """Test using a fixture."""
        obj = SomeClass(metadata_csv)
        assert obj.process() is not None
```

### Using markers
```python
@pytest.mark.slow
def test_large_dataset():
    """Test with large dataset - takes time."""
    pass

@pytest.mark.requires_network
def test_download_data():
    """Test that requires internet connection."""
    pass
```

## Test Data

Test fixtures are stored in `tests/fixtures/`:

- **metadata.csv** - Sample building metadata
- **vars_available_by_building.csv** - Sample variables data
- **TimeSeriesData/** - Sample time series data (if available)

The tests use these fixtures to dynamically generate TTL files for validation testing.

## CI/CD Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements-dev.txt
      - run: pytest
```

## Coverage Goals

Target coverage: **≥ 80%**

Current coverage can be checked with:
```bash
pytest --cov=hhws_brick_application --cov-report=term-missing
```

## Troubleshooting

### Tests fail with import errors
Make sure the package is installed:
```bash
pip install -e .
```

### Tests can't find fixtures
Check that you're running pytest from the project root:
```bash
cd /path/to/HHWS_Brick_Application
pytest
```

### Brickschema not available
Install development dependencies:
```bash
pip install -r requirements-dev.txt
```
"""
HHWS Brick Application Test Suite

Tests for conversion, validation, analytics, and workflow modules.
"""

__version__ = "0.2.0"

