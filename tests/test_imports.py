"""
Basic Import Tests

Verify that all major modules can be imported successfully.
"""

import pytest


def test_import_main_package():
    """Test that the main package can be imported."""
    import hhws_brick_application
    assert hhws_brick_application.__version__ is not None


def test_import_conversion_module():
    """Test that conversion module can be imported."""
    from hhws_brick_application.conversion import CSVToBrickConverter
    assert CSVToBrickConverter is not None


def test_import_validation_module():
    """Test that validation module can be imported."""
    from hhws_brick_application.validation import BrickModelValidator
    assert BrickModelValidator is not None


def test_import_validation_subgraph_module():
    """Test that subgraph pattern validator can be imported."""
    from hhws_brick_application.validation import SubgraphPatternValidator
    assert SubgraphPatternValidator is not None


def test_import_applications_module():
    """Test that applications module can be imported."""
    from hhws_brick_application.applications import ApplicationManager
    assert ApplicationManager is not None


def test_import_utils_module():
    """Test that utils module can be imported."""
    from hhws_brick_application.utils import get_building
    assert get_building is not None


def test_package_version_format():
    """Test that package version follows semantic versioning."""
    import hhws_brick_application
    import re

    # Semantic versioning pattern: MAJOR.MINOR.PATCH
    version_pattern = r'^\d+\.\d+\.\d+$'
    assert re.match(version_pattern, hhws_brick_application.__version__)


def test_all_core_modules_importable():
    """Test that all core modules are importable in one go."""
    from hhws_brick_application import (
        CSVToBrickConverter,
        GroundTruthCalculator,
        BrickModelValidator,
        SubgraphPatternValidator,
        ApplicationManager,
        get_building,
    )

    assert all([
        CSVToBrickConverter,
        GroundTruthCalculator,
        BrickModelValidator,
        SubgraphPatternValidator,
        ApplicationManager,
        get_building,
    ])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
HHWS Brick Application Test Suite

This package contains unit tests and integration tests for the HHWS Brick Application.
"""

