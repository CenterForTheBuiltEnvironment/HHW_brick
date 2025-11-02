# License

## MIT License

Copyright (c) 2024 Mingchen Li

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## What This Means

The MIT License is a permissive free software license. In simple terms:

### ✅ You CAN

- **Use** the software for any purpose (commercial or personal)
- **Modify** the source code
- **Distribute** the software
- **Sublicense** the software
- **Use** it in proprietary software

### ⚠️ You MUST

- **Include** the original copyright notice
- **Include** the license text

### ❌ You CANNOT

- **Hold the authors liable** for any damages
- **Use the authors' names** for promotion without permission

---

## Dependencies

This project uses several open-source libraries, each with their own licenses:

| Library | License | Purpose |
|---------|---------|---------|
| [RDFLib](https://github.com/RDFLib/rdflib) | BSD-3-Clause | RDF processing |
| [pandas](https://github.com/pandas-dev/pandas) | BSD-3-Clause | Data manipulation |
| [Click](https://github.com/pallets/click) | BSD-3-Clause | CLI framework |
| [brickschema](https://github.com/BrickSchema/py-brickschema) | BSD-3-Clause | Brick ontology |
| [PyYAML](https://github.com/yaml/pyyaml) | MIT | YAML parsing |

All dependencies are compatible with the MIT License.

---

## Contributing

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

See the [Contributing Guide](developer-guide/contributing/index.md) for more information.

---

## Third-Party Content

### Brick Schema

This package uses [Brick Schema](https://brickschema.org/), which is licensed under BSD-3-Clause.

### Documentation Theme

Documentation is built with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/), licensed under MIT.

---

## Questions?

If you have questions about licensing, please:

1. Check the [FAQ](faq.md)
2. Review the full license text above
3. [Open an issue](https://github.com/CenterForTheBuiltEnvironment/HHW_brick/issues) on GitHub

---

**[Back to Home](index.md)**
# Frequently Asked Questions

Common questions and answers about HHW Brick Application.

## General Questions

### What is HHW Brick Application?

HHW Brick Application is a Python package for working with Brick ontology in heating hot water systems. It provides tools for converting CSV data to Brick models, validating models, and running analytics applications.

### What is Brick?

[Brick](https://brickschema.org/) is a standardized semantic vocabulary for describing building systems and their data. It enables interoperability between different building management systems and analytics tools.

### Do I need to know RDF/ontologies to use this package?

No! The package handles all the RDF and ontology complexity for you. You can work with familiar formats like CSV and Python dictionaries.

### What Python versions are supported?

Python 3.8 and higher are supported.

---

## Installation & Setup

### How do I install the package?

```bash
pip install hhw-brick
```

See the [Installation Guide](getting-started/installation.md) for more details.

### Can I use this package offline?

Yes, once installed, the core functionality works offline. However, some validation features may require internet access to download Brick schema files.

### What are the dependencies?

Main dependencies include:
- `rdflib` - RDF processing
- `pandas` - Data manipulation
- `pyyaml` - Configuration
- `click` - CLI
- `brickschema` - Brick schema support

All dependencies are automatically installed via pip.

---

## Usage Questions

### How do I convert a CSV file to Brick?

```python
from hhw_brick import CSVToBrickConverter

converter = CSVToBrickConverter()
converter.convert_csv_to_brick("input.csv", "output.ttl")
```

See [Basic Usage](user-guide/conversion/basic-usage.md) for more examples.

### What CSV format is required?

The CSV should contain columns for:
- Equipment type
- Equipment name
- Points (sensors/actuators)
- Relationships

See the [Configuration Guide](user-guide/conversion/configuration.md) for details.

### Can I validate a model without ground truth data?

Yes! You can perform ontology validation without ground truth:

```python
validator = BrickModelValidator()
is_valid, report = validator.validate_ontology("model.ttl")
```

### How do I list available applications?

```python
from hhw_brick import apps

available = apps.list_apps()
print(available)
```

---

## Application Development

### How do I create a custom application?

See the [Developer Guide](developer-guide/developing-apps/getting-started.md) for a complete tutorial.

Basic structure:

```python
# my_app/__init__.py
__all__ = ['qualify', 'analyze', 'load_config']

def qualify(brick_model):
    return True, {}

def analyze(brick_model, timeseries_data, config):
    return {"results": "data"}

def load_config(config_path=None):
    return {}
```

### Where do I place my custom application?

Place it in the `hhw_brick/applications/` directory:

```
hhw_brick/
└── applications/
    ├── my_custom_app/
    │   └── __init__.py
    └── apps_manager.py
```

### How does the app discovery work?

The `apps_manager` automatically discovers all packages in the `applications/` directory that have the required interface (`qualify`, `analyze`, `load_config`).

---

## Troubleshooting

### "Module not found" error

Make sure the package is installed:

```bash
pip install hhw-brick
```

### "Command not found: hhw-brick"

The CLI might not be in your PATH. Try:

```bash
python -m hhw_brick.cli.main --help
```

Or reinstall the package:

```bash
pip install --force-reinstall hhw-brick
```

### Validation fails for a valid model

Ensure you have the latest Brick schema:

```python
from brickschema import Graph
g = Graph().load_file("model.ttl")
valid, _, report = g.validate()
print(report)
```

### Performance is slow for large files

For large CSV files, consider:
- Using batch processing with smaller chunks
- Enabling parallel processing (if available)
- Upgrading to a machine with more RAM

---

## Best Practices

### Should I validate every time I convert?

Yes! Validation ensures your Brick model is correct:

```python
# Convert
converter.convert_csv_to_brick("input.csv", "output.ttl")

# Validate
validator = BrickModelValidator()
is_valid, report = validator.validate_model("output.ttl")

if not is_valid:
    print("Validation errors:", report)
```

### How often should I update the package?

Check for updates monthly:

```bash
pip install --upgrade hhw-brick
```

### What's the recommended workflow?

1. Convert CSV to Brick
2. Validate the model
3. Qualify buildings for analysis
4. Run applications
5. Export results

See [User Guide](user-guide/index.md) for detailed workflows.

---

## Contributing

### How can I contribute?

See the [Contributing Guide](developer-guide/contributing/index.md) for:
- Reporting bugs
- Suggesting features
- Submitting pull requests
- Writing documentation

### Where do I report bugs?

[GitHub Issues](https://github.com/CenterForTheBuiltEnvironment/HHW_brick/issues)

### Can I add my application to the package?

Yes! We welcome contributions of new analytics applications. See the [Pull Request Guide](developer-guide/contributing/pull-requests.md).

---

## Still Have Questions?

- **Check the documentation**: Browse the [User Guide](user-guide/index.md) or [Developer Guide](developer-guide/index.md)
- **Search GitHub**: Look for similar [issues](https://github.com/CenterForTheBuiltEnvironment/HHW_brick/issues)
- **Ask the community**: Open a [discussion](https://github.com/CenterForTheBuiltEnvironment/HHW_brick/discussions)

---

**Didn't find your answer?** [Open an issue](https://github.com/CenterForTheBuiltEnvironment/HHW_brick/issues/new) on GitHub.

