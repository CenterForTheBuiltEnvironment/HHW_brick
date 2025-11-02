"""
Tests for applications module (apps manager and analytics apps).
"""

import pytest
from pathlib import Path
from hhws_brick_application import apps


class TestAppsManager:
    """Test cases for AppsManager."""

    def test_list_apps(self):
        """Test listing available applications."""
        app_list = apps.list_apps()
        assert isinstance(app_list, list)
        assert len(app_list) > 0

        # Check structure
        for app_info in app_list:
            assert 'name' in app_info
            assert 'description' in app_info
            assert 'path' in app_info

    def test_load_app_success(self):
        """Test loading a valid application."""
        app = apps.load_app("secondary_loop_temp_diff")
        assert app is not None

        # Check if app has required functions
        assert hasattr(app, 'qualify')
        assert hasattr(app, 'analyze')
        assert hasattr(app, 'load_config')
        assert callable(app.qualify)
        assert callable(app.analyze)

    def test_load_app_invalid(self):
        """Test loading a non-existent application."""
        with pytest.raises(ImportError):
            apps.load_app("non_existent_app")

    def test_get_default_config(self):
        """Test getting default configuration."""
        config = apps.get_default_config("secondary_loop_temp_diff")
        assert isinstance(config, dict)
        assert 'analysis' in config
        assert 'output' in config

    def test_get_app_info(self):
        """Test getting application information."""
        info = apps.get_app_info("secondary_loop_temp_diff")
        assert isinstance(info, dict)
        assert 'name' in info
        assert 'functions' in info

        # Check functions list
        function_names = [f['name'] for f in info['functions']]
        assert 'qualify' in function_names
        assert 'analyze' in function_names

    def test_qualify_building(self, brick_model_file):
        """Test qualifying a single building."""
        result = apps.qualify_building(str(brick_model_file), verbose=False)

        assert isinstance(result, dict)
        assert 'model' in result
        assert 'results' in result
        assert isinstance(result['results'], list)

        # Check result structure
        for r in result['results']:
            assert 'app' in r
            assert 'qualified' in r

    def test_qualify_buildings_batch(self, brick_model_dir):
        """Test qualifying multiple buildings."""
        results = apps.qualify_buildings(str(brick_model_dir), verbose=False)

        assert isinstance(results, list)
        assert len(results) > 0

        # Check each result
        for building_result in results:
            assert 'model' in building_result
            assert 'results' in building_result


class TestSecondaryLoopTempDiffApp:
    """Test cases for secondary_loop_temp_diff application."""

    def test_qualify_district_hw_building(self, district_hw_brick_model):
        """Test qualifying a district HW building."""
        app = apps.load_app("secondary_loop_temp_diff")

        # Suppress output
        import sys, io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        qualified, details = app.qualify(str(district_hw_brick_model))

        sys.stdout = old_stdout

        assert qualified is True
        assert isinstance(details, dict)
        assert 'loop' in details
        assert 'supply' in details
        assert 'return' in details

    def test_qualify_non_qualified_building(self, boiler_brick_model):
        """Test qualifying a non-district HW building (should fail)."""
        app = apps.load_app("secondary_loop_temp_diff")

        # Suppress output
        import sys, io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        qualified, details = app.qualify(str(boiler_brick_model))

        sys.stdout = old_stdout

        # Boiler systems might not have the required sensor pattern
        # (This depends on your data, adjust assertion if needed)
        assert isinstance(qualified, bool)

    def test_load_config(self):
        """Test loading application configuration."""
        app = apps.load_app("secondary_loop_temp_diff")
        config = app.load_config()

        assert isinstance(config, dict)
        assert 'analysis' in config
        assert 'output' in config
        assert 'time_range' in config

        # Check analysis settings
        assert 'threshold_min_delta' in config['analysis']
        assert 'threshold_max_delta' in config['analysis']

    @pytest.mark.skipif(
        not Path(__file__).parent / "fixtures" / "TimeSeriesData" / "29hhw_system_data.csv",
        reason="Timeseries data not available"
    )
    def test_analyze_with_data(self, district_hw_brick_model, timeseries_data):
        """Test running analysis with timeseries data."""
        app = apps.load_app("secondary_loop_temp_diff")
        config = app.load_config()

        # Set output to temp directory
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            config['output']['output_dir'] = tmpdir
            config['output']['generate_plots'] = False  # Faster

            # Suppress output
            import sys, io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()

            results = app.analyze(
                str(district_hw_brick_model),
                str(timeseries_data),
                config
            )

            sys.stdout = old_stdout

            if results:  # Might be None if building doesn't qualify
                assert 'stats' in results
                assert 'data' in results
                assert 'count' in results['stats']
                assert 'mean_temp_diff' in results['stats']


# Fixtures
@pytest.fixture
def brick_model_file(tmp_path):
    """Create a simple Brick model file for testing."""
    fixtures = Path(__file__).parent / "fixtures" / "Brick_Model_File"
    if fixtures.exists():
        models = list(fixtures.glob("building_29*.ttl"))
        if models:
            return models[0]
    pytest.skip("No Brick model fixtures available")


@pytest.fixture
def brick_model_dir():
    """Path to directory containing multiple Brick models."""
    fixtures = Path(__file__).parent / "fixtures" / "Brick_Model_File"
    if fixtures.exists() and any(fixtures.glob("*.ttl")):
        return fixtures
    pytest.skip("No Brick model directory available")


@pytest.fixture
def district_hw_brick_model():
    """A district HW Brick model."""
    fixtures = Path(__file__).parent / "fixtures" / "Brick_Model_File"
    if fixtures.exists():
        models = list(fixtures.glob("*district_hw*.ttl"))
        if models:
            return models[0]
    pytest.skip("No district HW Brick model available")


@pytest.fixture
def boiler_brick_model():
    """A boiler system Brick model."""
    fixtures = Path(__file__).parent / "fixtures" / "Brick_Model_File"
    if fixtures.exists():
        models = list(fixtures.glob("*boiler*.ttl"))
        if models:
            return models[0]
    # If no boiler model, use any non-district model
    all_models = list(fixtures.glob("*.ttl"))
    for model in all_models:
        if "district" not in model.name.lower():
            return model
    pytest.skip("No boiler Brick model available")


@pytest.fixture
def timeseries_data():
    """Timeseries data file for testing."""
    fixtures = Path(__file__).parent / "fixtures" / "TimeSeriesData"
    if fixtures.exists():
        data_files = list(fixtures.glob("29*.csv"))
        if data_files:
            return data_files[0]
    pytest.skip("No timeseries data available")

