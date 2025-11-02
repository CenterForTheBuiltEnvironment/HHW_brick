# Installation

Get HHWS Brick Application installed and ready to use.

## Requirements

### Python Version

- **Python 3.8 or higher** is required
- Python 3.10 is recommended for best performance

Check your Python version:

```bash
python --version
```

### Operating Systems

HHWS Brick Application works on:

- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 20.04+, Debian, CentOS, etc.)

## Installation Methods

### Method 1: Install from PyPI (Recommended)

The easiest way to install:

```bash
pip install hhw-brick
```

This installs the latest stable version.

### Method 2: Install from Source

For the latest development version:

```bash
# Clone the repository
git clone https://github.com/yourusername/hhw-brick.git
cd hhw-brick

# Install in editable mode
pip install -e .
```

### Method 3: Install Specific Version

```bash
# Install specific version
pip install hhw-brick==0.2.0

# Upgrade to latest
pip install --upgrade hhw-brick
```

## Verify Installation

Check that the package is installed correctly:

```python
import hhw_brick
print(hhw_brick.__version__)
```

Expected output:
```
0.2.0
```

Test the main components:

```python
from hhw_brick import CSVToBrickConverter, BatchConverter, apps

print("✓ Conversion module loaded")
print(f"✓ Available apps: {apps.list_apps()}")
```

## Dependencies

HHWS Brick Application automatically installs these dependencies:

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| rdflib | ≥7.2.0 | RDF graph processing |
| pandas | ≥1.3.0 | Data manipulation |
| pyyaml | ≥5.4.0 | Configuration files |
| brickschema | ≥0.7.0 | Brick ontology support |

### Optional Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| click | ≥8.0.0 | Command-line interface |
| matplotlib | ≥3.5.0 | Visualization |
| tqdm | ≥4.0.0 | Progress bars |

## Virtual Environment (Recommended)

It's recommended to use a virtual environment:

### Using venv

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install package
pip install hhw-brick
```

### Using conda

```bash
# Create environment
conda create -n hhws python=3.10

# Activate
conda activate hhws

# Install package
pip install hhw-brick
```

## Troubleshooting

### Issue: "pip: command not found"

**Solution**: Install pip or use `python -m pip` instead:

```bash
python -m pip install hhw-brick
```

### Issue: "Permission denied"

**Solution**: Use `--user` flag:

```bash
pip install --user hhw-brick
```

Or use a virtual environment (recommended).

### Issue: "No matching distribution found"

**Solution**: Upgrade pip:

```bash
python -m pip install --upgrade pip
pip install hhw-brick
```

### Issue: Dependency conflicts

**Solution**: Install in a clean virtual environment:

```bash
python -m venv fresh_env
fresh_env\Scripts\activate  # Windows
pip install hhw-brick
```

## Development Installation

For contributors and developers:

```bash
# Clone repository
git clone https://github.com/yourusername/hhw-brick.git
cd hhw-brick

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install in editable mode
pip install -e .

# Run tests to verify
pytest
```

See [Development Setup](../developer-guide/contributing/setup.md) for more details.

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

