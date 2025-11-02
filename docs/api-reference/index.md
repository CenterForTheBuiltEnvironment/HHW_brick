# API Reference

Complete API documentation for HHW Brick Application.

## Overview

This section provides detailed documentation for all public APIs in the package.

---

## Modules

### :material-swap-horizontal: Conversion

Transform CSV data to Brick ontology models.

- [CSVToBrickConverter](conversion/csv-to-brick.md) - Main converter class
- [BatchConverter](conversion/batch-converter.md) - Batch processing

---

### :material-check-decagram: Validation

Validate Brick models against schemas and ground truth.

- [BrickModelValidator](validation/validator.md) - Main validator
- [SubgraphPatternValidator](validation/subgraph-matcher.md) - Pattern matching
- [GroundTruthCalculator](validation/ground-truth.md) - Ground truth comparison

---

### :material-application: Applications

Analytics application framework.

- [AppsManager](applications/apps-manager.md) - Application management
- [BaseApp](applications/base-app.md) - Base application interface

---

### :material-console: CLI

Command-line interface.

- [Main CLI](cli/main.md) - Command-line entry points

---

### :material-tools: Utils

Utility functions and helpers.

- [BrickQuery](utils/brick-query.md) - Query Brick models
- [ConfigLoader](utils/config-loader.md) - Load configurations

---

## Quick Reference

### Import Statements

```python
# Main classes
from hhw_brick import (
    CSVToBrickConverter,
    BatchConverter,
    BrickModelValidator,
    GroundTruthCalculator,
    apps
)

# Utilities
from hhw_brick.utils import (
    BrickQuery,
    ConfigLoader
)

# Validation
from hhw_brick.validation import (
    SubgraphPatternValidator
)
```

---

## Common Methods

### Conversion

```python
converter = CSVToBrickConverter()

# Convert single file
converter.convert_csv_to_brick(input_file, output_file)

# Batch convert
batch = BatchConverter()
batch.convert_batch(input_dir, output_dir)
```

### Validation

```python
validator = BrickModelValidator()

# Validate model
is_valid, report = validator.validate_model(model_path)

# Check ontology
is_valid, errors = validator.validate_ontology(model_path)
```

### Applications

```python
# List apps
available = apps.list_apps()

# Load app
app = apps.load_app("app_name")

# Qualify building
qualified, details = app.qualify(brick_model)

# Run analysis
results = app.analyze(brick_model, data, config)
```

---

## Type Hints

All public APIs include type hints for better IDE support:

```python
from typing import Dict, Tuple, Optional
from rdflib import Graph
import pandas as pd

def qualify(brick_model: Graph) -> Tuple[bool, Dict]:
    ...

def analyze(
    brick_model: Graph,
    timeseries_data: pd.DataFrame,
    config: Optional[Dict] = None
) -> Dict:
    ...
```

---

## Return Values

### Success/Failure Pattern

Most methods return success status with details:

```python
# Pattern 1: Boolean + Details
is_valid, report = validator.validate_model(path)
# is_valid: bool
# report: Dict[str, Any]

# Pattern 2: Result Dictionary
result = {
    "success": True,
    "data": {...},
    "errors": []
}
```

### Error Handling

APIs raise specific exceptions:

```python
from hhw_brick.exceptions import (
    ValidationError,
    ConversionError,
    ConfigurationError
)
```

---

## Next Steps

- **Browse** module documentation in the sidebar
- **Check** [Examples](../examples/index.md) for practical usage
- **Read** [User Guide](../user-guide/index.md) for workflows

---

**Need details?** Select a module from the navigation →
