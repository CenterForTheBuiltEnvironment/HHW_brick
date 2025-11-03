# Installation

Get **hhw_brick** installed and ready to use.

## Requirements

### Python Version

- **Python 3.8 or higher** is required
- Python 3.10 is recommended for best performance

Check your Python version:

```bash
python --version
```

### Operating Systems

HHW Brick works on:

- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 20.04+, Debian, CentOS, etc.)

## Installation Methods

### Method 1: Install from Source (Recommended)

Currently, the package is not yet published to PyPI. Install from source:

```bash
# Clone the repository
git clone https://github.com/CenterForTheBuiltEnvironment/HHW_brick.git
cd HHW_brick

# Install in editable mode
pip install -e .
```

The `-e` flag installs in editable mode, so changes to the source code are immediately reflected.

### Method 2: Install from PyPI (Coming Soon)

Once published to PyPI, you'll be able to install with:

```bash
pip install hhw-brick
```

This installs the latest stable version.

## Verify Installation

Check that the package is installed correctly:

```python
import hhw_brick
print(hhw_brick.__version__)
```

Expected output:
```
0.1.0
```

Test the main components:

```python
from hhw_brick import CSVToBrickConverter, BatchConverter, apps

print("✓ Conversion module loaded")
print(f"✓ Available apps: {len(apps.list_apps())} applications")
```

## Dependencies

HHW Brick automatically installs these dependencies:

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| rdflib | ≥6.2.0, <7.0.0 | RDF graph processing |
| pandas | ≥1.3.0, <3.0.0 | Data manipulation |
| pyyaml | ≥5.4.0, <7.0.0 | Configuration files |
| brickschema | ≥0.6.0, <0.7.0 | Brick ontology support |

### Analytics & Utilities

| Package | Version | Purpose |
|---------|---------|---------|
| tqdm | ≥4.0.0 | Progress bars |
| jsonschema | ≥4.0.0 | JSON validation |
| requests | ≥2.28.0 | HTTP requests |
| matplotlib | ≥3.5.0 | Visualization |
| seaborn | ≥0.11.0 | Statistical visualization |

All dependencies are automatically installed when you run `pip install -e .`

## Virtual Environment (Recommended)

It's recommended to use a virtual environment to avoid dependency conflicts:

### Using venv

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Clone and install package
git clone https://github.com/CenterForTheBuiltEnvironment/HHW_brick.git
cd HHW_brick
pip install -e .
```

### Using conda

```bash
# Create environment
conda create -n hhw_brick python=3.10

# Activate
conda activate hhw_brick

# Clone and install package
git clone https://github.com/CenterForTheBuiltEnvironment/HHW_brick.git
cd HHW_brick
pip install -e .
```

## Troubleshooting

### Issue: "pip: command not found"

**Solution**: Install pip or use `python -m pip` instead:

```bash
python -m pip install -e .
```

### Issue: "Permission denied"

**Solution**: Use a virtual environment (recommended) or add `--user` flag:

```bash
pip install --user -e .
```

### Issue: Git not installed

**Solution**: Install Git first:
- Windows: Download from [git-scm.com](https://git-scm.com/)
- Mac: `brew install git` or install Xcode Command Line Tools
- Linux: `sudo apt-get install git` (Ubuntu/Debian)

### Issue: Dependency conflicts

**Solution**: Install in a clean virtual environment:

```bash
python -m venv fresh_env
fresh_env\Scripts\activate  # Windows
source fresh_env/bin/activate  # Linux/Mac
cd HHW_brick
pip install -e .
```

### Issue: Import errors after installation

**Solution**: Verify the installation:

```bash
pip list | grep hhw-brick
# Should show: hhw-brick  0.1.0  /path/to/HHW_brick
```

## Development Installation

For contributors and developers who want to modify the code:

```bash
# Clone repository
git clone https://github.com/CenterForTheBuiltEnvironment/HHW_brick.git
cd HHW_brick

# Install development dependencies
pip install -r requirements-dev.txt

# Install in editable mode
pip install -e .

# Run tests to verify
pytest
```

**Development dependencies include**:
- pytest - Testing framework
- pytest-cov - Code coverage
- black - Code formatter
- flake8 - Linter
- mkdocs - Documentation

See [Contributing Guide](../developer-guide/) for more details on contributing to the project.

## Uninstallation

To remove the package:

```bash
pip uninstall hhw-brick
```

## Next Steps

Now that you have the package installed:

- **[Quick Start](quick-start.md)** - Convert your first building
- **[Understanding Brick](understanding-brick.md)** - Learn about Brick ontology
- **[CSV Format](csv-format.md)** - Prepare your data files

---

**Installation complete!** Continue to [Quick Start](quick-start.md) →
