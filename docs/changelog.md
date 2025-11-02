# Changelog

All notable changes to HHW Brick Application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Web interface for visualization
- Additional analytics applications
- Performance optimizations
- Multi-language documentation

---

## [0.2.0] - 2024-10-29

### Added
- Comprehensive validation module
  - Ontology validation using brickschema
  - Subgraph pattern matching
  - Point and equipment count validation
  - Ground truth calculator
- Unified workflow module (HHWSWorkflow)
- Command-line interface (CLI) with Click
- Batch conversion support
- Configuration management utilities
- Deployment management module
- Application framework with apps_manager
  - Auto-discovery of applications
  - Pluggable analytics system
- Secondary loop temperature difference application
- Primary loop temperature difference application

### Changed
- Migrated to modern pyproject.toml configuration
- Reorganized package structure with clear module separation
- Improved CSV to Brick conversion with better error handling
- Enhanced logging throughout the package
- Updated documentation structure

### Fixed
- CSV conversion edge cases
- Memory leaks in batch processing
- Type hints in core modules

### Deprecated
- Legacy validation methods (replaced with new validation module)

---

## [0.1.8.1] - Previous Release

### Added
- Basic CSV to Brick conversion functionality
- Initial validation features
- Core utilities for Brick query

### Changed
- Various bug fixes and improvements

---

## [0.1.0] - Initial Release

### Added
- Initial release of HHW Brick Application
- CSV to Brick ontology conversion
- Basic Brick model support
- Preliminary validation tools

---

## Version Numbering

We use [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backwards compatible manner
- **PATCH** version for backwards compatible bug fixes

Example: `0.2.1`
- `0` - Major version (pre-1.0 is development)
- `2` - Minor version (new features)
- `1` - Patch version (bug fixes)

---

## Links

- [PyPI Package](https://pypi.org/project/hhw-brick/)
- [GitHub Repository](https://github.com/CenterForTheBuiltEnvironment/HHW_brick)
- [Issue Tracker](https://github.com/CenterForTheBuiltEnvironment/HHW_brick/issues)
- [Documentation](https://yourusername.github.io/hhw-brick/)

---

## How to Contribute

See our [Contributing Guide](developer-guide/contributing/index.md) for:

- Reporting bugs
- Suggesting features
- Submitting pull requests
- Writing documentation

---

**[Back to Home](index.md)**
