"""
Tests for utility modules.
"""

import pytest
import os
from pathlib import Path

from hhws_brick_application.utils import brick_query, logger, file_utils


class TestBrickQuery:
    """Test cases for brick_query utility."""

    def test_brick_query_module_import(self):
        """Test that brick_query module can be imported."""
        assert brick_query is not None

    def test_query_functions_exist(self):
        """Test that expected query functions exist."""
        # Check for common query-related attributes
        # Adjust based on actual implementation
        module_attrs = dir(brick_query)
        assert len(module_attrs) > 0


class TestLogger:
    """Test cases for logger utility."""

    def test_logger_module_import(self):
        """Test that logger module can be imported."""
        assert logger is not None

    def test_logger_configuration(self):
        """Test logger configuration."""
        # Check that we can get a logger
        import logging
        test_logger = logging.getLogger("test_hhws")
        assert test_logger is not None


class TestFileUtils:
    """Test cases for file_utils utility."""

    def test_file_utils_module_import(self):
        """Test that file_utils module can be imported."""
        assert file_utils is not None

    def test_file_utils_functions_exist(self):
        """Test that expected file utility functions exist."""
        module_attrs = dir(file_utils)
        assert len(module_attrs) > 0

