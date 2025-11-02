"""
Tests for CSV to Brick conversion module.
"""

import pytest
import os
from pathlib import Path
from rdflib import Graph, Namespace

from hhws_brick_application.conversion.csv_to_brick import CSVToBrickConverter
from hhws_brick_application.conversion.batch_converter import BatchConverter


class TestCSVToBrickConverter:
    """Test cases for CSVToBrickConverter class."""

    def test_converter_initialization(self):
        """Test that converter initializes correctly."""
        converter = CSVToBrickConverter()
        assert converter is not None
        assert converter.graph is not None
        assert len(converter.graph) == 0  # Empty graph initially

    def test_namespaces_bound(self):
        """Test that all required namespaces are bound."""
        converter = CSVToBrickConverter()
        namespaces = dict(converter.graph.namespaces())

        # Check key namespaces
        assert 'brick' in namespaces
        assert 'hhws' in namespaces
        assert 'rdf' in namespaces
        assert 'rdfs' in namespaces

    def test_safe_float_convert(self):
        """Test safe float conversion utility."""
        converter = CSVToBrickConverter()

        # Valid conversions
        assert converter._safe_float_convert(123.45) == 123.45
        assert converter._safe_float_convert("123.45") == 123.45
        assert converter._safe_float_convert(100) == 100.0

        # Invalid/NA conversions
        assert converter._safe_float_convert(None) is None
        assert converter._safe_float_convert("NA") is None
        assert converter._safe_float_convert("") is None
        assert converter._safe_float_convert("  NA  ") is None

    def test_safe_int_convert(self):
        """Test safe integer conversion utility."""
        converter = CSVToBrickConverter()

        # Valid conversions
        assert converter._safe_int_convert(123) == 123
        assert converter._safe_int_convert("123") == 123
        assert converter._safe_int_convert("123.0") == 123

        # Invalid/NA conversions
        assert converter._safe_int_convert(None) is None
        assert converter._safe_int_convert("NA") is None
        assert converter._safe_int_convert("") is None

    def test_convert_single_building(self, metadata_csv, vars_csv, temp_output_dir, sample_building_tag):
        """Test conversion of a single building to Brick format."""
        converter = CSVToBrickConverter()
        output_path = os.path.join(temp_output_dir, f"building_{sample_building_tag}.ttl")

        # Convert
        graph = converter.convert_to_brick(
            metadata_csv=metadata_csv,
            vars_csv=vars_csv,
            system_type="District HW",
            building_tag=sample_building_tag,
            output_path=output_path
        )

        # Verify output
        assert graph is not None
        assert len(graph) > 0  # Graph should have triples
        assert os.path.exists(output_path)  # File should be created

        # Verify file can be loaded
        loaded_graph = Graph()
        loaded_graph.parse(output_path, format="turtle")
        assert len(loaded_graph) > 0

    def test_convert_system_type(self, metadata_csv, vars_csv, temp_output_dir):
        """Test conversion of specific system type."""
        converter = CSVToBrickConverter()
        output_path = os.path.join(temp_output_dir, "district_hw_system.ttl")

        graph = converter.convert_to_brick(
            metadata_csv=metadata_csv,
            vars_csv=vars_csv,
            system_type="District HW",
            output_path=output_path
        )

        assert graph is not None
        assert len(graph) > 0
        assert os.path.exists(output_path)

    def test_invalid_system_type(self, metadata_csv, vars_csv, temp_output_dir):
        """Test that invalid system type is handled gracefully."""
        converter = CSVToBrickConverter()
        output_path = os.path.join(temp_output_dir, "invalid_system.ttl")

        # Should not raise an error, but might log warnings
        graph = converter.convert_to_brick(
            metadata_csv=metadata_csv,
            vars_csv=vars_csv,
            system_type="NonExistentSystem",
            output_path=output_path
        )

        # Graph might be empty or minimal
        assert graph is not None

    def test_missing_csv_files(self, temp_output_dir):
        """Test that missing CSV files raise appropriate errors."""
        converter = CSVToBrickConverter()

        with pytest.raises(FileNotFoundError):
            converter.convert_to_brick(
                metadata_csv="nonexistent_metadata.csv",
                vars_csv="nonexistent_vars.csv",
                system_type="District HW",
                output_path=os.path.join(temp_output_dir, "output.ttl")
            )


class TestBatchConverter:
    """Test cases for BatchConverter class."""

    def test_batch_converter_initialization(self):
        """Test batch converter initialization."""
        converter = BatchConverter()

        assert converter is not None
        assert converter.converter is not None

    def test_batch_convert_all_buildings(self, metadata_csv, vars_csv, temp_output_dir):
        """Test batch conversion of all buildings."""
        converter = BatchConverter()

        # Convert all District HW buildings
        results = converter.convert_all_buildings(
            metadata_csv=metadata_csv,
            vars_csv=vars_csv,
            output_dir=temp_output_dir,
            system_type="District HW",
            show_progress=False
        )

        assert results is not None
        assert isinstance(results, dict)

    def test_batch_convert_specific_tags(self, metadata_csv, vars_csv, temp_output_dir):
        """Test batch conversion with specific building tags."""
        converter = BatchConverter()

        # Convert only building 29
        results = converter.convert_all_buildings(
            metadata_csv=metadata_csv,
            vars_csv=vars_csv,
            output_dir=temp_output_dir,
            building_tags=["29"],
            show_progress=False
        )

        assert results is not None

