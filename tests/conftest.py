"""
pytest configuration and shared fixtures for HHWS Brick Application tests.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
import pandas as pd


@pytest.fixture(scope="session")
def fixtures_dir():
    """Return the path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def metadata_csv(fixtures_dir):
    """Return the path to the test metadata.csv file."""
    return str(fixtures_dir / "metadata.csv")


@pytest.fixture(scope="session")
def vars_csv(fixtures_dir):
    """Return the path to the test vars_available_by_building.csv file."""
    return str(fixtures_dir / "vars_available_by_building.csv")


@pytest.fixture(scope="session")
def timeseries_dir(fixtures_dir):
    """Return the path to the TimeSeriesData directory."""
    ts_dir = fixtures_dir / "TimeSeriesData"
    if ts_dir.exists():
        return str(ts_dir)
    return None


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs, cleanup after test."""
    temp_dir = tempfile.mkdtemp(prefix="hhws_test_")
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_building_tag():
    """Return a sample building tag for testing."""
    return "29"  # District HW system from fixtures


@pytest.fixture
def sample_metadata_df(metadata_csv):
    """Load and return sample metadata as DataFrame."""
    return pd.read_csv(metadata_csv)


@pytest.fixture
def sample_vars_df(vars_csv):
    """Load and return sample vars data as DataFrame."""
    return pd.read_csv(vars_csv)


@pytest.fixture
def sample_system_types():
    """Return list of system types to test."""
    return ["District HW", "Condensing", "Non-condensing"]


@pytest.fixture(scope="session")
def ground_truth_csv():
    """Return path to ground truth CSV if it exists."""
    # Look for ground_truth.csv in parent directory structure
    current_dir = Path(__file__).parent.parent
    gt_path = current_dir.parent / "ground_truth.csv"
    if gt_path.exists():
        return str(gt_path)
    return None


@pytest.fixture
def mock_ttl_output(temp_output_dir):
    """Return a path for TTL output in temp directory."""
    return os.path.join(temp_output_dir, "test_output.ttl")

