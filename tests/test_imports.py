"""
Basic Import Tests

Verify that all major modules can be imported successfully.
"""

import pytest


def test_import_main_package():
    """Test that the main package can be imported."""
    import hhw_brick

    assert hhw_brick.__version__ is not None


def test_import_conversion_module():
    """Test that conversion module can be imported."""
    from hhw_brick.conversion import CSVToBrickConverter

    assert CSVToBrickConverter is not None


def test_import_validation_module():
    """Test that validation module can be imported."""
    from hhw_brick.validation import BrickModelValidator

    assert BrickModelValidator is not None


def test_import_validation_subgraph_module():
    """Test that subgraph pattern validator can be imported."""
    from hhw_brick.validation import SubgraphPatternValidator

    assert SubgraphPatternValidator is not None


def test_import_applications_module():
    """Test that applications module can be imported."""
    from hhw_brick.applications import apps

    assert apps is not None


def test_import_utils_module():
    """Test that utils module can be imported."""
    from hhw_brick.utils import brick_query

    assert brick_query is not None


def test_package_version_format():
    """Test that package version follows semantic versioning."""
    import hhw_brick
    import re

    # Semantic versioning pattern: MAJOR.MINOR.PATCH
    version_pattern = r"^\d+\.\d+\.\d+$"
    assert re.match(version_pattern, hhw_brick.__version__)


def test_all_core_modules_importable():
    """Test that all core modules are importable in one go."""
    from hhw_brick import (
        CSVToBrickConverter,
        GroundTruthCalculator,
        BrickModelValidator,
        apps,
    )

    assert all(
        [
            CSVToBrickConverter,
            GroundTruthCalculator,
            BrickModelValidator,
            apps,
        ]
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
