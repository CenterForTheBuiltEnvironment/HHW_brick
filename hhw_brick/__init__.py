"""
HHW Brick

A comprehensive Python package for Heating Hot Water System (HHWS) Brick ontology.

Quick Start:
    >>> from hhw_brick import CSVToBrickConverter, apps
    >>>
    >>> # Convert CSV to Brick
    >>> converter = CSVToBrickConverter()
    >>>
    >>> # List available analytics apps
    >>> available_apps = apps.list_apps()
    >>>
    >>> # Load and use an app
    >>> app = apps.load_app("secondary_loop_temp_diff")

Main Components:
    - Conversion: CSV to Brick model conversion
    - Validation: Model validation and verification
    - Analytics: Data analysis applications (via `apps`)


Author: Mingchen Li
"""

__version__ = "0.1.0"
__author__ = "Mingchen Li"
__email__ = "liwei74123@gmail.com"

# =============================================================================
# Core Conversion Tools
# =============================================================================
from .conversion.csv_to_brick import CSVToBrickConverter
from .conversion.batch_converter import BatchConverter

# =============================================================================
# Validation Tools
# =============================================================================
from .validation.validator import BrickModelValidator
from .validation.ground_truth_calculator import GroundTruthCalculator

# =============================================================================
# Applications (Easy Access)
# =============================================================================
# Usage:
#   from hhw_brick import apps
#   apps.list_apps()              # List all available apps
#   app = apps.load_app("name")   # Load an app
#   config = apps.get_default_config("name")  # Get config template
from .applications.apps_manager import apps

# =============================================================================
# Public API
# =============================================================================
__all__ = [
    # Version
    "__version__",
    # Conversion (most common use case)
    "CSVToBrickConverter",
    "BatchConverter",
    # Validation
    "BrickModelValidator",
    "GroundTruthCalculator",
    # Analytics (simplified interface)
    "apps",
]

# =============================================================================
# Advanced imports (for power users)
# =============================================================================
# These are available but not in __all__ (import explicitly if needed):
#   from hhw_brick.validation import SubgraphPatternValidator
#   from hhw_brick import utils, cli
