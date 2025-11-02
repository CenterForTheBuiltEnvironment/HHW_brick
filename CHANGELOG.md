# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2025-11-02

### 🎉 Initial Release

First official release of **HHW Brick**, migrated from `hhws_brick_application`.

---

## 🔴 BREAKING CHANGES

### Package Rename
- **Old**: `hhws_brick_application`
- **New**: `hhw_brick` (PyPI: `hhw-brick`)

**Migration**:
```python
# Before
from hhws_brick_application.conversion import CSVToBrickConverter

# After
from hhw_brick import CSVToBrickConverter
```

### API Changes
- Applications interface: `ApplicationManager` → `apps`
- New CLI command: `hhw-brick`

---

## ✨ Added

### Core Features
- **CSV to Brick Conversion**: Support for 5 hot water system types
- **Validation Framework**: 4-level validation (ontology, point count, equipment count, pattern)
- **Ground Truth Calculator**: Generate expected counts from CSV
- **Batch Processing**: Parallel conversion with multiprocessing
- **Analytics Applications**: Plugin-based apps framework with 2 built-in apps
- **CLI Tool**: `hhw-brick` command with convert, validate, deploy subcommands
- **Utilities**: SPARQL query helpers, data loading, file operations

### Testing
- 110 test cases (95% pass rate)
- Test coverage: 40-45% overall
- pytest framework with fixtures

### Documentation
- README with quick start
- MkDocs structure
- 8 example scripts
- Contributing guide

---

## 🔄 Changed

- Package structure reorganized
- All documentation translated to English
- Improved error messages and type hints
- Simplified public API

---

## 🐛 Fixed

- Package import paths (7 test files)
- Test API mismatches (60+ tests)
- UTF-8 BOM encoding in pyproject.toml
- Missing module exports

---

## 📊 Statistics

- **Code**: ~3,000+ lines
- **Tests**: 110 (53 passed, 3 skipped)
- **Coverage**: 40-45%
- **Supported Systems**: 5 hot water types
- **Tested Buildings**: 216 real buildings

---

## 🚀 Upgrade from hhws_brick_application

```bash
# 1. Uninstall old package
pip uninstall hhws_brick_application

# 2. Install new package
pip install hhw-brick

# 3. Update imports
# Replace hhws_brick_application with hhw_brick in all files

# 4. Update application usage
from hhw_brick import apps  # instead of ApplicationManager
```

---

## 🙏 Acknowledgments

- Original package: hhws_brick_application
- Author: Mingchen Li
- Built with: Brick Schema 1.4, RDF/OWL, SPARQL

---

[0.1.0]: https://github.com/CenterForTheBuiltEnvironment/HHW_brick/releases/tag/v0.1.0
