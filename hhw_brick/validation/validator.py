#!/usr/bin/env python3
"""
HHWS Brick Model Validator
For validating the ontology integrity of generated TTL files using brickschema
"""

import os
import logging
import csv
import multiprocessing
import warnings
from typing import Dict
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

logger = logging.getLogger(__name__)

# Attempt to import brickschema
try:
    from brickschema import Graph

    _BRICKSCHEMA_AVAILABLE = True
except ImportError:  # pragma: no cover
    _BRICKSCHEMA_AVAILABLE = False
    Graph = None  # Define Graph in except block


def _validate_ontology_worker(ttl_file_path: str, use_local_brick: bool = True) -> Dict:
    """
    Worker function for parallel ontology validation

    Args:
        ttl_file_path: Path to TTL file to validate
        use_local_brick: Whether to use local Brick schema

    Returns:
        Dict with validation results
    """
    try:
        # Create a temporary validator instance for this worker
        validator = BrickModelValidator(use_local_brick=use_local_brick)
        return validator.validate_ontology(ttl_file_path)
    except Exception as e:
        return {
            'ttl_file_path': ttl_file_path,
            'valid': False,
            'success': False,
            'accuracy_percentage': 0.0,
            'error': str(e),
            'validation_report': f'Error during validation: {str(e)}'
        }


class BrickModelValidator:
    """Brick model validator class using brickschema for ontology validation"""

    def __init__(self, ground_truth_csv_path: str = None, use_local_brick: bool = True):
        """Initialize validator

        Args:
            ground_truth_csv_path: Path to ground_truth.csv file with validation baseline data
                                  (columns: tag, system, point_count, boiler_count, pump_count, weather_station_count)
            use_local_brick: If True, use local Brick_Self.ttl; if False, use GitHub nightly version (default: False)
        """
        if not _BRICKSCHEMA_AVAILABLE:
            raise ImportError("brickschema is not available. Please install with: pip install brickschema")

        self.ground_truth_csv_path = ground_truth_csv_path
        self.use_local_brick = use_local_brick
        self._ground_truth_data = None

        # Set up local Brick path if using local version
        if self.use_local_brick:
            # Brick_Self.ttl is now in the same directory as this validator.py file
            current_dir = os.path.dirname(__file__)
            self.local_brick_path = os.path.join(current_dir, "Brick_Self.ttl")
            
            if not os.path.exists(self.local_brick_path):
                raise FileNotFoundError(f"Local Brick file not found: {self.local_brick_path}")
            logger.info(f"Using local Brick Schema from: {self.local_brick_path}")
        else:
            self.local_brick_path = None
            logger.info("Using GitHub nightly Brick Schema")

    def _create_brick_graph(self) -> Graph:
        """Create a brickschema Graph with appropriate Brick ontology loaded

        Returns:
            Graph: A brickschema Graph object with Brick ontology loaded
        """
        if self.use_local_brick:
            # Use local Brick_Self.ttl file
            g = Graph()
            g.load_file(self.local_brick_path, format="turtle")
            logger.debug(f"Loaded local Brick Schema from {self.local_brick_path}")
        else:
            # Use GitHub nightly version
            g = Graph(load_brick_nightly=True)
            logger.debug("Loaded Brick Schema from GitHub nightly release")
        return g

    def _load_ground_truth_data(self) -> Dict[str, Dict]:
        """Load ground truth data from ground_truth.csv file

        Returns:
            Dict mapping building tags to their expected counts
            Format: {
                'tag': {
                    'point_count': int,
                    'boiler_count': int,
                    'pump_count': int,
                    'weather_station_count': int,
                    'system': str
                }
            }
        """
        if self._ground_truth_data is not None:
            return self._ground_truth_data

        if not self.ground_truth_csv_path or not os.path.exists(self.ground_truth_csv_path):
            logger.warning(f"Ground truth CSV file not found: {self.ground_truth_csv_path}")
            return {}

        try:
            import pandas as pd
            df = pd.read_csv(self.ground_truth_csv_path)

            ground_truth = {}
            for _, row in df.iterrows():
                tag = str(int(row['tag']))  # Convert to string, ensure it's an integer first
                ground_truth[tag] = {
                    'point_count': int(row['point_count']),
                    'boiler_count': int(row['boiler_count']),
                    'pump_count': int(row['pump_count']),
                    'weather_station_count': int(row['weather_station_count']),
                    'system': str(row['system'])
                }

            self._ground_truth_data = ground_truth
            logger.info(f"Loaded ground truth data for {len(ground_truth)} buildings")
            return ground_truth

        except Exception as e:
            logger.error(f"Error loading ground truth data: {e}")
            return {}

    def _load_metadata_data(self) -> Dict[str, Dict]:
        """Load metadata from metadata.csv for equipment validation

        Returns:
            Dict mapping building tags to metadata including b_number (boiler count)
        """
        if self._metadata_data is not None:
            return self._metadata_data

        if not self.metadata_csv_path or not os.path.exists(self.metadata_csv_path):
            logger.warning(f"Metadata CSV file not found: {self.metadata_csv_path}")
            return {}

        try:
            metadata = {}
            with open(self.metadata_csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    tag = row.get('tag', '').strip()
                    if not tag:
                        continue

                    # Extract b_number (boiler number)
                    b_number_str = row.get('b_number', '').strip()
                    b_number = None
                    if b_number_str and b_number_str != 'NA':
                        try:
                            b_number = int(float(b_number_str))
                        except ValueError:
                            logger.warning(f"Invalid b_number for tag {tag}: {b_number_str}")

                    metadata[tag] = {
                        'b_number': b_number,
                        'system': row.get('system', '').strip()
                    }

            self._metadata_data = metadata
            logger.info(f"Loaded metadata for {len(metadata)} buildings")
            return metadata

        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            return {}

    def _load_pump_count_data(self) -> Dict[str, Dict]:
        """Load pump count data from vars_available_by_building.csv

        New logic:
        1. Each loop needs at least 1 pump (structural requirement)
        2. Variables indicate pump count for ONE of the loops
        3. Total pump count = (num_loops - 1) + variable_pump_count
        4. District systems: 1 loop (secondary only)
        5. Boiler/Condensing systems: 2 loops (primary + secondary)

        Returns:
            Dict mapping building tags to pump information
        """
        if not self.ground_truth_csv_path or not os.path.exists(self.ground_truth_csv_path):
            logger.warning(f"Ground truth CSV file not found: {self.ground_truth_csv_path}")
            return {}

        # Load metadata to determine system type and loop count
        metadata = self._load_metadata_data()

        try:
            pump_data = {}
            with open(self.ground_truth_csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    tag = row.get('tag', '').strip()
                    if not tag:
                        continue

                    # Determine number of loops based on system type
                    system_type = metadata.get(tag, {}).get('system', '')
                    if 'District' in system_type:
                        num_loops = 1  # District systems only have secondary loop
                    else:
                        num_loops = 2  # Boiler/Condensing systems have primary + secondary loops

                    # Check pump-related columns
                    pmp_spd = row.get('pmp_spd', '').strip()
                    pmp1_spd = row.get('pmp1_spd', '').strip()
                    pmp2_spd = row.get('pmp2_spd', '').strip()
                    pmp1_vfd = row.get('pmp1_vfd', '').strip()
                    pmp2_vfd = row.get('pmp2_vfd', '').strip()

                    # Determine pump count from variables
                    has_pmp_spd = pmp_spd in ['1', '1.0']
                    has_pmp1_spd = pmp1_spd in ['1', '1.0']
                    has_pmp2_spd = pmp2_spd in ['1', '1.0']
                    has_pmp1_vfd = pmp1_vfd in ['1', '1.0']
                    has_pmp2_vfd = pmp2_vfd in ['1', '1.0']

                    # Count individual pumps from numbered speed signals
                    spd_count = 0
                    if has_pmp1_spd:
                        spd_count += 1
                    if has_pmp2_spd:
                        spd_count += 1
                    if has_pmp_spd and spd_count == 0:  # Only count pmp_spd if no numbered spd
                        spd_count = 1

                    # Count individual pumps from VFD signals
                    vfd_count = 0
                    if has_pmp1_vfd:
                        vfd_count += 1
                    if has_pmp2_vfd:
                        vfd_count += 1

                    # Variable pump count (for one loop) is the maximum of spd_count and vfd_count
                    variable_pump_count = max(spd_count, vfd_count)

                    # NEW LOGIC: Pump variables represent secondary loop pumps
                    # District systems: Only 1 loop (secondary), pump_count = variable_pump_count or 1
                    # Boiler systems: 2 loops (primary + secondary)
                    #   - Primary loop: always 1 pump (structural, no sensor points)
                    #   - Secondary loop: variable_pump_count or 1
                    #   - Total = 1 (primary) + variable_pump_count (secondary)
                    if num_loops == 1:
                        # District systems: only secondary loop
                        pump_count = variable_pump_count if variable_pump_count > 0 else 1
                    else:
                        # Boiler systems: primary (1 pump) + secondary (variable pumps)
                        secondary_pump_count = variable_pump_count if variable_pump_count > 0 else 1
                        pump_count = 1 + secondary_pump_count

                    # Check for potential error: all pump variables present
                    has_all = (has_pmp_spd and has_pmp1_spd and has_pmp2_spd and has_pmp1_vfd and has_pmp2_vfd)

                    pump_data[tag] = {
                        'pump_count': pump_count,
                        'num_loops': num_loops,
                        'variable_pump_count': variable_pump_count,
                        'has_potential_error': has_all,
                        'pmp_spd': has_pmp_spd,
                        'pmp1_spd': has_pmp1_spd,
                        'pmp2_spd': has_pmp2_spd,
                        'pmp1_vfd': has_pmp1_vfd,
                        'pmp2_vfd': has_pmp2_vfd,
                        'spd_count': spd_count,
                        'vfd_count': vfd_count
                    }

            logger.info(f"Loaded pump count data for {len(pump_data)} buildings")
            return pump_data

        except Exception as e:
            logger.error(f"Error loading pump count data: {e}")
            return {}

    def _load_boiler_count_data(self) -> Dict[str, Dict]:
        """Load boiler count data from vars_available_by_building.csv and metadata.csv

        Logic:
        1. District systems (District HW/Steam): 0 boilers (regardless of metadata)
        2. Boiler systems: max(variable_inferred_count, b_number from metadata)

        Returns:
            Dict mapping building tags to boiler information
        """
        if not self.ground_truth_csv_path or not os.path.exists(self.ground_truth_csv_path):
            logger.warning(f"Ground truth CSV file not found: {self.ground_truth_csv_path}")
            return {}

        # Load metadata to get b_number and system type
        metadata = self._load_metadata_data()

        try:
            boiler_data = {}
            with open(self.ground_truth_csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    tag = row.get('tag', '').strip()
                    if not tag:
                        continue

                    # Get system type from metadata
                    system_type = metadata.get(tag, {}).get('system', '')
                    is_district_system = 'District' in system_type

                    # Get b_number from metadata
                    b_number = metadata.get(tag, {}).get('b_number', 0) or 0

                    if is_district_system:
                        # District systems always have 0 boilers
                        boiler_count = 0
                    else:
                        # Boiler systems: infer from variables
                        # Check boiler-related sensors (sup1-9, ret1-9, fire1-9)
                        max_boiler_from_vars = 0
                        for i in range(1, 10):
                            boiler_sensors = [f'sup{i}', f'ret{i}', f'fire{i}']
                            if any(row.get(sensor, '').strip() in ['1', '1.0'] for sensor in boiler_sensors):
                                max_boiler_from_vars = max(max_boiler_from_vars, i)

                        # Check for unnumbered boiler sensors
                        unnumbered_boiler_sensors = ['sup', 'ret', 'fire', 'supp', 'retp']
                        has_unnumbered = any(
                            row.get(sensor, '').strip() in ['1', '1.0'] for sensor in unnumbered_boiler_sensors)

                        if max_boiler_from_vars == 0 and has_unnumbered:
                            max_boiler_from_vars = 1

                        # Take maximum of variable-inferred count and b_number
                        boiler_count = max(max_boiler_from_vars, b_number)

                    boiler_data[tag] = {
                        'boiler_count': boiler_count,
                        'b_number': b_number,
                        'system_type': system_type,
                        'is_district': is_district_system
                    }

            logger.info(f"Loaded boiler count data for {len(boiler_data)} buildings")
            return boiler_data

        except Exception as e:
            logger.error(f"Error loading boiler count data: {e}")
            return {}

    def _count_points_in_ttl(self, ttl_file_path: str, max_retries: int = 2) -> int:
        """Count points in TTL file using SPARQL query

        Args:
            ttl_file_path: Path to TTL file
            max_retries: Maximum number of retry attempts for parsing errors

        Returns:
            Number of points found in the TTL file
        """
        import time

        for attempt in range(max_retries):
            try:
                # Create brickschema Graph with Brick ontology (local or nightly)
                g = self._create_brick_graph()

                # Try to load the TTL file
                try:
                    # Parse with standard turtle parser
                    g.parse(ttl_file_path, format="turtle")
                except Exception as parse_error:
                    # If parsing fails, try alternative approach
                    logger.warning(f"Standard parsing failed for {ttl_file_path}: {parse_error}")
                    try:
                        # Try reading file content and parsing as string
                        with open(ttl_file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        g.parse(data=content, format="turtle")
                    except Exception as alt_error:
                        if attempt < max_retries - 1:
                            logger.warning(f"Retry attempt {attempt + 1}/{max_retries} for {ttl_file_path}")
                            time.sleep(0.05 * (attempt + 1))  # Brief pause before retry
                            continue
                        logger.error(f"Parsing failed for {ttl_file_path}: {alt_error}")
                        return -1  # Return -1 to indicate parsing error

                # SPARQL query to count points
                # Modified to handle owl:sameAs deduplication
                sparql_query = """
                PREFIX brick: <https://brickschema.org/schema/Brick#>
                PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX ref:   <https://brickschema.org/schema/Brick/ref#>
                PREFIX owl:   <http://www.w3.org/2002/07/owl#>

                SELECT (COUNT(DISTINCT ?canonical) AS ?count) WHERE {
                  ?point rdf:type/rdfs:subClassOf* brick:Point .
                  ?point ref:hasExternalReference [
                    a ref:TimeseriesReference ;
                    ref:hasTimeseriesId ?tsid ;
                    ref:storedAt ?store
                  ] .
                  
                  # Handle owl:sameAs - use canonical representation
                  # If ?point has sameAs, use the object as canonical, otherwise use ?point itself
                  OPTIONAL { ?point owl:sameAs ?same }
                  BIND(COALESCE(?same, ?point) AS ?canonical)
                }
                """

                result = g.query(sparql_query)
                for row in result:
                    return int(row[0])

                return 0

            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Error on attempt {attempt + 1}/{max_retries} for {ttl_file_path}: {e}")
                    time.sleep(0.05 * (attempt + 1))
                    continue

                logger.error(f"Error counting points in TTL file {ttl_file_path} after {max_retries} attempts: {e}")
                return -1  # Return -1 to indicate error

        return -1  # Should not reach here, but return -1 if all retries failed

    def _count_equipment_in_ttl(self, ttl_file_path: str, max_retries: int = 2) -> Dict:
        """Count equipment in TTL file using SPARQL query

        Args:
            ttl_file_path: Path to TTL file
            max_retries: Maximum number of retry attempts for parsing errors

        Returns:
            Dict with counts: {'boiler_count': int, 'pump_count': int, 'weather_station_count': int}
        """
        import time

        for attempt in range(max_retries):
            try:
                # Create brickschema Graph with Brick ontology (local or nightly)
                g = self._create_brick_graph()

                # Try to load the TTL file
                try:
                    # Parse with standard turtle parser
                    g.parse(ttl_file_path, format="turtle")
                except Exception as parse_error:
                    # If parsing fails, try alternative approach
                    logger.warning(f"Standard parsing failed for {ttl_file_path}: {parse_error}")
                    try:
                        # Try reading file content and parsing as string
                        with open(ttl_file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        g.parse(data=content, format="turtle")
                    except Exception as alt_error:
                        if attempt < max_retries - 1:
                            logger.warning(f"Retry attempt {attempt + 1}/{max_retries} for {ttl_file_path}")
                            time.sleep(0.05 * (attempt + 1))  # Brief pause before retry
                            continue
                        logger.error(f"Parsing failed for {ttl_file_path}: {alt_error}")
                        return {'boiler_count': -1, 'pump_count': -1, 'weather_station_count': -1}

                # SPARQL query to count all equipment types in one query
                sparql_query = """
                PREFIX brick: <https://brickschema.org/schema/Brick#>
                PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>

                SELECT 
                  (COUNT(DISTINCT ?boiler) AS ?boiler_count)
                  (COUNT(DISTINCT ?pump) AS ?pump_count)
                  (COUNT(DISTINCT ?weather_station) AS ?weather_station_count)
                WHERE {
                  OPTIONAL {
                    ?boiler rdf:type/rdfs:subClassOf* brick:Boiler .
                  }
                  OPTIONAL {
                    ?pump rdf:type/rdfs:subClassOf* brick:Pump .
                  }
                  OPTIONAL {
                    ?weather_station rdf:type/rdfs:subClassOf* brick:Weather_Station .
                  }
                }
                """

                result = g.query(sparql_query)
                for row in result:
                    return {
                        'boiler_count': int(row[0]),
                        'pump_count': int(row[1]),
                        'weather_station_count': int(row[2])
                    }

                return {'boiler_count': 0, 'pump_count': 0, 'weather_station_count': 0}

            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Error on attempt {attempt + 1}/{max_retries} for {ttl_file_path}: {e}")
                    time.sleep(0.05 * (attempt + 1))
                    continue

                logger.error(f"Error counting equipment in TTL file {ttl_file_path} after {max_retries} attempts: {e}")
                return {'boiler_count': -1, 'pump_count': -1, 'weather_station_count': -1}

        return {'boiler_count': -1, 'pump_count': -1, 'weather_station_count': -1}

    def validate_equipment_count(self, ttl_file_path: str, building_tag: str = None) -> Dict:
        """
        Validate equipment count by comparing TTL file against ground truth data

        Args:
            ttl_file_path: Path to the TTL file to validate
            building_tag: Building tag to look up in ground truth data.
                         If None, will try to extract from filename

        Returns:
            Dict: {
                'ttl_file_path': str,
                'building_tag': str,
                'boiler': {
                    'expected': int,
                    'actual': int,
                    'match': bool
                },
                'pump': {
                    'expected': int,
                    'actual': int,
                    'match': bool
                },
                'weather_station': {
                    'expected': int,
                    'actual': int,
                    'match': bool
                },
                'overall_success': bool,
                'validation_report': str,
                'error': str (optional)
            }
        """
        if not _BRICKSCHEMA_AVAILABLE:
            return {
                'ttl_file_path': ttl_file_path,
                'building_tag': building_tag,
                'overall_success': False,
                'error': 'brickschema is not available'
            }

        if not os.path.exists(ttl_file_path):
            return {
                'ttl_file_path': ttl_file_path,
                'building_tag': building_tag,
                'overall_success': False,
                'error': f'TTL file not found: {ttl_file_path}'
            }

        try:
            # Extract building tag from filename if not provided
            if building_tag is None:
                filename = os.path.basename(ttl_file_path)
                # Remove .ttl extension first
                filename_no_ext = filename.replace('.ttl', '')
                # Assuming filename format like "building_105" or "building_105_non-condensing_h"
                if filename_no_ext.startswith('building_'):
                    parts = filename_no_ext.split('_')
                    building_tag = parts[1]  # Extract the number part
                else:
                    return {
                        'ttl_file_path': ttl_file_path,
                        'building_tag': 'unknown',
                        'overall_success': False,
                        'error': 'Could not extract building tag from filename'
                    }

            logger.info(f"Starting equipment count validation for building {building_tag}: {ttl_file_path}")

            # Load ground truth data
            ground_truth = self._load_ground_truth_data()

            if building_tag not in ground_truth:
                return {
                    'ttl_file_path': ttl_file_path,
                    'building_tag': building_tag,
                    'overall_success': False,
                    'error': f'Building tag {building_tag} not found in ground truth data'
                }

            # Get expected counts from ground truth
            gt_data = ground_truth[building_tag]
            expected_boiler = gt_data['boiler_count']
            expected_pump = gt_data['pump_count']
            expected_weather_station = gt_data['weather_station_count']

            # Count actual equipment in TTL file
            actual_counts = self._count_equipment_in_ttl(ttl_file_path)

            # Check if there was a parsing error
            if actual_counts['boiler_count'] == -1:
                return {
                    'ttl_file_path': ttl_file_path,
                    'building_tag': building_tag,
                    'overall_success': False,
                    'error': 'TTL file parsing failed'
                }

            # Compare counts
            boiler_match = (expected_boiler == actual_counts['boiler_count'])
            pump_match = (expected_pump == actual_counts['pump_count'])
            weather_match = (expected_weather_station == actual_counts['weather_station_count'])

            overall_success = boiler_match and pump_match and weather_match

            # Generate validation report
            report_lines = [
                f"Equipment Count Validation for Building {building_tag}:",
                f"",
                f"Boiler:",
                f"  Expected: {expected_boiler}",
                f"  Actual: {actual_counts['boiler_count']}",
                f"  Status: {'✓ PASS' if boiler_match else '✗ FAIL'}",
                f"",
                f"Pump:",
                f"  Expected: {expected_pump}",
                f"  Actual: {actual_counts['pump_count']}",
                f"  Status: {'✓ PASS' if pump_match else '✗ FAIL'}",
                f"",
                f"Weather Station:",
                f"  Expected: {expected_weather_station}",
                f"  Actual: {actual_counts['weather_station_count']}",
                f"  Status: {'✓ PASS' if weather_match else '✗ FAIL'}",
                f"",
                f"Overall: {'✓ ALL CHECKS PASSED' if overall_success else '✗ VALIDATION FAILED'}"
            ]

            result = {
                'ttl_file_path': ttl_file_path,
                'building_tag': building_tag,
                'boiler': {
                    'expected': expected_boiler,
                    'actual': actual_counts['boiler_count'],
                    'match': boiler_match
                },
                'pump': {
                    'expected': expected_pump,
                    'actual': actual_counts['pump_count'],
                    'match': pump_match
                },
                'weather_station': {
                    'expected': expected_weather_station,
                    'actual': actual_counts['weather_station_count'],
                    'match': weather_match
                },
                'overall_success': overall_success,
                'validation_report': '\n'.join(report_lines)
            }

            status = 'PASSED' if overall_success else 'FAILED'
            logger.info(f"Equipment count validation {status} for building {building_tag}")
            return result

        except Exception as e:
            logger.error(f"Equipment count validation failed: {e}")
            return {
                'ttl_file_path': ttl_file_path,
                'building_tag': building_tag or 'unknown',
                'overall_success': False,
                'error': str(e)
            }

    def validate_point_count(self, ttl_file_path: str, building_tag: str = None) -> Dict:
        """
        Validate point count by comparing TTL file against ground truth CSV

        Args:
            ttl_file_path: Path to the TTL file to validate
            building_tag: Building tag to look up in ground truth data.
                         If None, will try to extract from filename

        Returns:
            Dict: Validation results including expected/actual counts and match status
        """
        if not _BRICKSCHEMA_AVAILABLE:
            return {
                'ttl_file_path': ttl_file_path,
                'building_tag': building_tag,
                'expected_point_count': 0,
                'actual_point_count': 0,
                'match': False,
                'accuracy_percentage': 0.0,
                'success': False,
                'validation_report': '',
                'error': 'brickschema is not available'
            }

        if not os.path.exists(ttl_file_path):
            return {
                'ttl_file_path': ttl_file_path,
                'building_tag': building_tag,
                'expected_point_count': 0,
                'actual_point_count': 0,
                'match': False,
                'accuracy_percentage': 0.0,
                'success': False,
                'validation_report': '',
                'error': f'TTL file not found: {ttl_file_path}'
            }

        try:
            # Extract building tag from filename if not provided
            if building_tag is None:
                filename = os.path.basename(ttl_file_path)
                # Remove .ttl extension first
                filename_no_ext = filename.replace('.ttl', '')
                # Assuming filename format like "building_105" or "building_105_non-condensing_h"
                if filename_no_ext.startswith('building_'):
                    parts = filename_no_ext.split('_')
                    building_tag = parts[1]  # Extract the number part
                else:
                    return {
                        'ttl_file_path': ttl_file_path,
                        'building_tag': 'unknown',
                        'expected_point_count': 0,
                        'actual_point_count': 0,
                        'match': False,
                        'accuracy_percentage': 0.0,
                        'success': False,
                        'validation_report': '',
                        'error': 'Could not extract building tag from filename'
                    }

            logger.info(f"Starting point count validation for building {building_tag}: {ttl_file_path}")

            # Load ground truth data
            ground_truth = self._load_ground_truth_data()

            if building_tag not in ground_truth:
                return {
                    'ttl_file_path': ttl_file_path,
                    'building_tag': building_tag,
                    'expected_point_count': 0,
                    'actual_point_count': 0,
                    'match': False,
                    'accuracy_percentage': 0.0,
                    'success': False,
                    'validation_report': '',
                    'error': f'Building tag {building_tag} not found in ground truth data'
                }

            # Get expected point count from ground truth
            expected_count = ground_truth[building_tag]['point_count']

            # Count actual points in TTL file
            actual_count = self._count_points_in_ttl(ttl_file_path)

            # Check if there was a parsing error
            if actual_count == -1:
                return {
                    'ttl_file_path': ttl_file_path,
                    'building_tag': building_tag,
                    'expected_point_count': expected_count,
                    'actual_point_count': 0,
                    'match': False,
                    'accuracy_percentage': 0.0,
                    'success': False,
                    'validation_report': f'Expected points: {expected_count}\nActual points: ERROR (parsing failed)',
                    'error': 'TTL file parsing failed'
                }

            # Check if counts match
            match = (expected_count == actual_count)
            accuracy = 100.0 if match else 0.0

            # Generate validation report
            validation_report = f"Expected points: {expected_count}\nActual points: {actual_count}\n"
            if match:
                validation_report += "✓ Point counts match"
            else:
                validation_report += f"✗ Point counts do not match (difference: {abs(expected_count - actual_count)})"

            result = {
                'ttl_file_path': ttl_file_path,
                'building_tag': building_tag,
                'expected_point_count': expected_count,
                'actual_point_count': actual_count,
                'match': match,
                'accuracy_percentage': accuracy,
                'success': match,
                'validation_report': validation_report
            }

            logger.info(
                f"Point count validation {'PASSED' if match else 'FAILED'} - Expected: {expected_count}, Actual: {actual_count}")
            return result

        except Exception as e:
            logger.error(f"Point count validation failed: {e}")
            return {
                'ttl_file_path': ttl_file_path,
                'building_tag': building_tag or 'unknown',
                'expected_point_count': 0,
                'actual_point_count': 0,
                'match': False,
                'accuracy_percentage': 0.0,
                'success': False,
                'validation_report': '',
                'error': str(e)
            }

    def batch_validate_point_count(self, test_data_dir: str, max_files: int = None, max_workers: int = None) -> Dict:
        """
        Batch point count validation for TTL files in test directory

        Args:
            test_data_dir: Path to directory containing test TTL files
            max_files: Maximum number of files to validate (None for all files)
            max_workers: Number of parallel workers (None = CPU count - 1)

        Returns:
            Dict: {
                'total_files': int,
                'matched_files': int,
                'mismatched_files': int,
                'overall_accuracy': float,
                'results': List[Dict],
                'summary': str
            }
        """
        if not os.path.exists(test_data_dir):
            return {
                'total_files': 0,
                'matched_files': 0,
                'mismatched_files': 0,
                'overall_accuracy': 0.0,
                'results': [],
                'summary': f'Test directory not found: {test_data_dir}',
                'error': f'Directory not found: {test_data_dir}'
            }

        # Find all TTL files in the directory
        ttl_files = []
        for file in os.listdir(test_data_dir):
            if file.endswith('.ttl'):
                ttl_files.append(os.path.join(test_data_dir, file))

        if not ttl_files:
            return {
                'total_files': 0,
                'matched_files': 0,
                'mismatched_files': 0,
                'overall_accuracy': 0.0,
                'results': [],
                'summary': f'No TTL files found in {test_data_dir}'
            }

        # Limit the number of files if max_files is specified
        total_available = len(ttl_files)
        if max_files is not None and max_files > 0:
            ttl_files = ttl_files[:max_files]
            logger.info(f"Limiting validation to {len(ttl_files)} out of {total_available} available TTL files")
        else:
            logger.info(f"Found {len(ttl_files)} TTL files for batch point count validation")

        results = []
        matched_count = 0
        mismatched_count = 0

        # Determine number of workers
        if max_workers is None:
            max_workers = max(1, multiprocessing.cpu_count() - 1)

        logger.info(f"Using {max_workers} parallel workers for validation")
        print(f"⚙️  Using {max_workers} parallel workers for faster processing")

        # Use parallel processing for faster validation
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self.validate_point_count, ttl_file): ttl_file
                for ttl_file in ttl_files
            }

            # Collect results with progress bar
            for future in tqdm(as_completed(future_to_file), total=len(ttl_files), desc="Validating point counts", unit="file"):
                try:
                    result = future.result()
                    results.append(result)

                    if result.get('success', False):
                        matched_count += 1
                    else:
                        mismatched_count += 1

                except Exception as e:
                    ttl_file = future_to_file[future]
                    logger.error(f"Error validating {os.path.basename(ttl_file)}: {e}")
                    # Add error result
                    results.append({
                        'ttl_file_path': ttl_file,
                        'building_tag': 'unknown',
                        'expected_point_count': 0,
                        'actual_point_count': 0,
                        'match': False,
                        'accuracy_percentage': 0.0,
                        'success': False,
                        'validation_report': '',
                        'error': str(e)
                    })
                    mismatched_count += 1

        # Calculate overall accuracy
        total_files = len(ttl_files)
        overall_accuracy = (matched_count / total_files * 100) if total_files > 0 else 0.0

        summary_lines = [
            f"Point Count Validation Summary:",
            f"Total files: {total_files}",
            f"Matched: {matched_count}",
            f"Mismatched: {mismatched_count}",
            f"Overall accuracy: {overall_accuracy:.2f}%"
        ]

        batch_result = {
            'total_files': total_files,
            'matched_files': matched_count,
            'mismatched_files': mismatched_count,
            'overall_accuracy': overall_accuracy,
            'results': results,
            'summary': "\n".join(summary_lines)
        }

        logger.info(
            f"Batch point count validation complete: {matched_count}/{total_files} files matched ({overall_accuracy:.2f}%)")
        return batch_result

    def batch_validate_equipment_count(self, test_data_dir: str, max_files: int = None, max_workers: int = None) -> Dict:
        """
        Batch equipment count validation for TTL files in test directory

        Args:
            test_data_dir: Path to directory containing test TTL files
            max_files: Maximum number of files to validate (None for all files)
            max_workers: Number of parallel workers (None = CPU count - 1)

        Returns:
            Dict: {
                'total_files': int,
                'passed_files': int,
                'failed_files': int,
                'overall_accuracy': float,
                'results': List[Dict],
                'summary': str,
                'potential_errors': List[str]  # Buildings with pump configuration issues
            }
        """
        if not os.path.exists(test_data_dir):
            return {
                'total_files': 0,
                'passed_files': 0,
                'failed_files': 0,
                'overall_accuracy': 0.0,
                'results': [],
                'summary': f'Test directory not found: {test_data_dir}',
                'potential_errors': [],
                'error': f'Directory not found: {test_data_dir}'
            }

        # Find all TTL files in the directory
        ttl_files = []
        for file in os.listdir(test_data_dir):
            if file.endswith('.ttl'):
                ttl_files.append(os.path.join(test_data_dir, file))

        if not ttl_files:
            return {
                'total_files': 0,
                'passed_files': 0,
                'failed_files': 0,
                'overall_accuracy': 0.0,
                'results': [],
                'summary': f'No TTL files found in {test_data_dir}',
                'potential_errors': []
            }

        # Limit the number of files if max_files is specified
        total_available = len(ttl_files)
        if max_files is not None and max_files > 0:
            ttl_files = ttl_files[:max_files]
            logger.info(
                f"Limiting equipment validation to {len(ttl_files)} out of {total_available} available TTL files")
        else:
            logger.info(f"Found {len(ttl_files)} TTL files for batch equipment count validation")

        results = []
        passed_count = 0
        failed_count = 0
        potential_errors = []

        # Separate counters for each equipment type
        boiler_matched = 0
        boiler_total = 0
        pump_matched = 0
        pump_total = 0
        weather_matched = 0
        weather_total = 0

        # Determine number of workers
        if max_workers is None:
            max_workers = max(1, multiprocessing.cpu_count() - 1)

        logger.info(f"Using {max_workers} parallel workers for validation")
        print(f"⚙️  Using {max_workers} parallel workers for faster processing")

        # Use parallel processing for faster validation
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(self.validate_equipment_count, ttl_file): ttl_file
                for ttl_file in ttl_files
            }

            # Collect results with progress bar
            for future in tqdm(as_completed(future_to_file), total=len(ttl_files), desc="Validating equipment counts", unit="file"):
                try:
                    result = future.result()
                    results.append(result)

                    if result.get('overall_success', False):
                        passed_count += 1
                    else:
                        failed_count += 1

                    # Count matches for each equipment type
                    boiler_info = result.get('boiler', {})
                    if boiler_info.get('expected', 0) is not None:
                        boiler_total += 1
                        if boiler_info.get('match', False):
                            boiler_matched += 1

                    pump_info = result.get('pump', {})
                    if pump_info.get('expected', 0) is not None:
                        pump_total += 1
                        if pump_info.get('match', False):
                            pump_matched += 1

                    weather_info = result.get('weather_station', {})
                    if weather_info.get('expected', 0) is not None:
                        weather_total += 1
                        if weather_info.get('match', False):
                            weather_matched += 1

                    # Check for potential pump configuration errors
                    if pump_info.get('has_potential_error', False):
                        building_tag = result.get('building_tag', 'unknown')
                        potential_errors.append(
                            f"Building {building_tag}: All pump variables present (potential configuration error)")

                except Exception as e:
                    ttl_file = future_to_file[future]
                    logger.error(f"Error validating {os.path.basename(ttl_file)}: {e}")
                    # Add error result
                    results.append({
                        'ttl_file_path': ttl_file,
                        'building_tag': 'unknown',
                        'overall_success': False,
                        'error': str(e)
                    })
                    failed_count += 1

        # Calculate overall accuracy
        total_files = len(ttl_files)
        overall_accuracy = (passed_count / total_files * 100) if total_files > 0 else 0.0

        # Calculate accuracy for each equipment type
        boiler_accuracy = (boiler_matched / boiler_total * 100) if boiler_total > 0 else 0.0
        pump_accuracy = (pump_matched / pump_total * 100) if pump_total > 0 else 0.0
        weather_accuracy = (weather_matched / weather_total * 100) if weather_total > 0 else 0.0

        summary_lines = [
            f"Equipment Count Validation Summary:",
            f"Total files: {total_files}",
            f"All checks passed: {passed_count}",
            f"Some checks failed: {failed_count}",
            f"",
            f"Individual Equipment Accuracy:",
            f"  Boiler:          {boiler_matched}/{boiler_total} matched ({boiler_accuracy:.2f}%)",
            f"  Pump:            {pump_matched}/{pump_total} matched ({pump_accuracy:.2f}%)",
            f"  Weather Station: {weather_matched}/{weather_total} matched ({weather_accuracy:.2f}%)",
        ]

        if potential_errors:
            summary_lines.append(f"\n⚠ Potential Configuration Errors: {len(potential_errors)}")
            for error in potential_errors:
                summary_lines.append(f"  - {error}")

        batch_result = {
            'total_files': total_files,
            'passed_files': passed_count,
            'failed_files': failed_count,
            'overall_accuracy': overall_accuracy,
            'boiler_accuracy': boiler_accuracy,
            'boiler_matched': boiler_matched,
            'boiler_total': boiler_total,
            'pump_accuracy': pump_accuracy,
            'pump_matched': pump_matched,
            'pump_total': pump_total,
            'weather_station_accuracy': weather_accuracy,
            'weather_station_matched': weather_matched,
            'weather_station_total': weather_total,
            'results': results,
            'summary': "\n".join(summary_lines),
            'potential_errors': potential_errors
        }

        logger.info(f"Batch equipment count validation complete:")
        logger.info(f"  Boiler: {boiler_matched}/{boiler_total} ({boiler_accuracy:.2f}%)")
        logger.info(f"  Pump: {pump_matched}/{pump_total} ({pump_accuracy:.2f}%)")
        logger.info(f"  Weather Station: {weather_matched}/{weather_total} ({weather_accuracy:.2f}%)")
        return batch_result

    def validate_ontology(self, ttl_file_path: str) -> Dict:
        """
        Ontology validation using brickschema

        This function validates a TTL file against the Brick ontology using brickschema's
        validation capabilities. The accuracy is binary: 100% if the model passes
        all ontology validation checks, 0% otherwise.

        Args:
            ttl_file_path: Path to the TTL file to validate

        Returns:
            Dict: {
                'ttl_file_path': str,
                'valid': bool,           # True if model passes ontology validation
                'accuracy_percentage': float,  # 100.0 if valid, 0.0 if not valid
                'success': bool,         # Same as valid
                'validation_report': str,     # Detailed validation report
                'error': str (optional)  # Error message if validation failed
            }
        """
        if not _BRICKSCHEMA_AVAILABLE:
            return {
                'ttl_file_path': ttl_file_path,
                'valid': False,
                'accuracy_percentage': 0.0,
                'success': False,
                'validation_report': '',
                'error': 'brickschema is not available'
            }

        if not os.path.exists(ttl_file_path):
            return {
                'ttl_file_path': ttl_file_path,
                'valid': False,
                'accuracy_percentage': 0.0,
                'success': False,
                'validation_report': '',
                'error': f'TTL file not found: {ttl_file_path}'
            }

        try:
            logger.info(f"Starting ontology validation for: {ttl_file_path}")

            # Suppress HTML parsing warnings from rdflib during Brick schema loading
            # These warnings are from Brick schema's HTML literals and don't affect validation
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=UserWarning, module='rdflib')
                warnings.filterwarnings('ignore', message='Failed to parse HTML')
                warnings.filterwarnings('ignore', message='Failed to convert Literal')

                # Also suppress logging warnings from rdflib.term
                rdflib_logger = logging.getLogger('rdflib.term')
                original_level = rdflib_logger.level
                rdflib_logger.setLevel(logging.ERROR)

                try:
                    # Create brickschema Graph with Brick ontology (local or nightly)
                    if self.use_local_brick:
                        logger.info(f"Loading local Brick Schema from: {self.local_brick_path}")
                    else:
                        logger.info("Loading latest Brick Schema from GitHub nightly release...")
                    g = self._create_brick_graph()

                    # Load QUDT ontologies (schema, quantity kinds, and units) from online sources
                    try:
                        logger.info("Loading QUDT schema from online source...")
                        g.load_file("http://qudt.org/schema/qudt/")
                        logger.info("✓ QUDT schema loaded successfully")
                    except Exception as e:
                        logger.warning(f"Failed to load QUDT schema from online: {e}")

                    try:
                        logger.info("Loading QUDT quantity kinds from online source...")
                        g.load_file("http://qudt.org/vocab/quantitykind")
                        logger.info("✓ QUDT quantity kinds loaded successfully")
                    except Exception as e:
                        logger.warning(f"Failed to load QUDT quantity kinds from online: {e}")

                    try:
                        logger.info("Loading QUDT units from online source...")
                        g.load_file("http://qudt.org/vocab/unit")
                        logger.info("✓ QUDT units loaded successfully")
                    except Exception as e:
                        logger.warning(f"Failed to load QUDT units from online: {e}")
                        # Fallback to local unit.ttl if online loading fails
                        current_file_dir = os.path.dirname(__file__)
                        unit_file_path = os.path.join(current_file_dir, "unit.ttl")
                        if not os.path.exists(unit_file_path):
                            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                            unit_file_path = os.path.join(project_root, "unit.ttl")
                        if os.path.exists(unit_file_path):
                            logger.info(f"Loading unit definitions from local file: {unit_file_path}")
                            g.load_file(unit_file_path, format="turtle")
                        else:
                            logger.warning("unit.ttl not found locally, validation may fail for QUDT units")

                    # Load the TTL file to be validated
                    g.load_file(ttl_file_path, format="turtle")
                    logger.info(f"Loaded TTL file with {len(g)} triples")

                    # Perform validation
                    valid, _, report = g.validate()
                finally:
                    # Restore original logging level
                    rdflib_logger.setLevel(original_level)

            # Format validation report
            validation_report = ""
            if valid:
                validation_report = "Model passed all ontology validation checks"
            else:
                if report:
                    validation_report = str(report)
                else:
                    validation_report = "Model failed ontology validation (no detailed report available)"

            # Calculate accuracy: 100% if valid, 0% if not
            accuracy = 100.0 if valid else 0.0

            result = {
                'ttl_file_path': ttl_file_path,
                'valid': valid,
                'accuracy_percentage': accuracy,
                'success': valid,
                'validation_report': validation_report,
                'total_triples': len(g)
            }

            logger.info(f"Ontology validation {'PASSED' if valid else 'FAILED'} - Accuracy: {accuracy}%")
            return result

        except Exception as e:
            logger.error(f"Ontology validation failed: {e}")
            return {
                'ttl_file_path': ttl_file_path,
                'valid': False,
                'accuracy_percentage': 0.0,
                'success': False,
                'validation_report': '',
                'error': str(e)
            }

    def batch_validate_ontology(self, test_data_dir: str, max_workers: int = None) -> Dict:
        """
        Batch ontology validation for all TTL files in test directory

        Args:
            test_data_dir: Path to directory containing test TTL files
            max_workers: Number of parallel workers (None = CPU count - 1)

        Returns:
            Dict: {
                'total_files': int,
                'passed_files': int,
                'failed_files': int,
                'overall_accuracy': float,  # Percentage of files that passed
                'results': List[Dict],      # Individual validation results
                'summary': str
            }
        """
        if not os.path.exists(test_data_dir):
            return {
                'total_files': 0,
                'passed_files': 0,
                'failed_files': 0,
                'overall_accuracy': 0.0,
                'results': [],
                'summary': f'Test directory not found: {test_data_dir}',
                'error': f'Directory not found: {test_data_dir}'
            }

        # Find all TTL files in the directory
        ttl_files = []
        for file in os.listdir(test_data_dir):
            if file.endswith('.ttl'):
                ttl_files.append(os.path.join(test_data_dir, file))

        if not ttl_files:
            return {
                'total_files': 0,
                'passed_files': 0,
                'failed_files': 0,
                'overall_accuracy': 0.0,
                'results': [],
                'summary': f'No TTL files found in {test_data_dir}'
            }

        logger.info(f"Found {len(ttl_files)} TTL files for batch validation")

        # Determine number of workers
        if max_workers is None:
            max_workers = max(1, multiprocessing.cpu_count() - 1)
        logger.info(f"Using {max_workers} parallel workers for validation")
        print(f"⚙️  Using {max_workers} parallel workers for faster processing")

        results = []
        passed_count = 0
        failed_count = 0

        # Use parallel processing for faster validation
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(_validate_ontology_worker, ttl_file, self.use_local_brick): ttl_file
                for ttl_file in ttl_files
            }

            # Collect results with progress bar
            for future in tqdm(as_completed(future_to_file), total=len(ttl_files), desc="Validating ontology", unit="file"):
                try:
                    result = future.result()
                    results.append(result)

                    if result.get('success', False):
                        passed_count += 1
                    else:
                        failed_count += 1

                except Exception as e:
                    ttl_file = future_to_file[future]
                    logger.error(f"Error validating {os.path.basename(ttl_file)}: {e}")
                    results.append({
                        'ttl_file_path': ttl_file,
                        'valid': False,
                        'success': False,
                        'accuracy_percentage': 0.0,
                        'error': str(e)
                    })
                    failed_count += 1

        # Calculate overall accuracy
        total_files = len(ttl_files)
        overall_accuracy = (passed_count / total_files * 100) if total_files > 0 else 0.0

        summary_lines = [
            f"Ontology Validation Summary:",
            f"Total files: {total_files}",
            f"Passed: {passed_count}",
            f"Failed: {failed_count}",
            f"Overall accuracy: {overall_accuracy:.2f}%"
        ]

        batch_result = {
            'total_files': total_files,
            'passed_files': passed_count,
            'failed_files': failed_count,
            'overall_accuracy': overall_accuracy,
            'results': results,
            'summary': "\n".join(summary_lines)
        }

        logger.info(f"Batch validation complete: {passed_count}/{total_files} files passed ({overall_accuracy:.2f}%)")
        return batch_result

    def print_ontology_validation_report(self, result: Dict):
        """Print ontology validation report"""
        print(f"\n{'=' * 80}")
        print("ONTOLOGY VALIDATION REPORT")
        print(f"{'=' * 80}")

        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            print(f"File: {result['ttl_file_path']}")
            print(f"Accuracy: {result['accuracy_percentage']}%")
            print(f"{'=' * 80}\n")
            return

        print(f"File: {os.path.basename(result['ttl_file_path'])}")
        print(f"Total triples: {result.get('total_triples', 'N/A')}")
        print(f"Validation result: {'✓ PASSED' if result['valid'] else '✗ FAILED'}")
        print(f"Accuracy: {result['accuracy_percentage']}%")

        if result['validation_report']:
            print(f"\nValidation Report:")
            print("-" * 40)
            # Truncate report if too long
            report = result['validation_report']
            if len(report) > 1000:
                report = report[:1000] + "\n... (report truncated)"
            print(report)

        print(f"\n{'=' * 80}\n")

    def print_batch_validation_report(self, batch_result: Dict):
        """Print batch ontology validation report"""
        print(f"\n{'=' * 80}")
        print("BATCH ONTOLOGY VALIDATION REPORT")
        print(f"{'=' * 80}")

        if 'error' in batch_result:
            print(f"❌ Error: {batch_result['error']}")
            print(f"{'=' * 80}\n")
            return

        print(batch_result['summary'])

        if batch_result['results']:
            print(f"\nIndividual Results:")
            print("-" * 50)

            for result in batch_result['results']:
                filename = os.path.basename(result['ttl_file_path'])
                status = "✓ PASS" if result['success'] else "✗ FAIL"
                accuracy = result['accuracy_percentage']
                print(f"{filename:<30} {status:<8} {accuracy:>6.1f}%")

                if not result['success'] and 'error' in result:
                    print(f"  Error: {result['error']}")

        print(f"\n{'=' * 80}\n")

    def print_point_count_validation_report(self, result: Dict):
        """Print point count validation report"""
        print(f"\n{'=' * 80}")
        print("POINT COUNT VALIDATION REPORT")
        print(f"{'=' * 80}")

        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            print(f"File: {result['ttl_file_path']}")
            print(f"Building: {result['building_tag']}")
            print(f"Accuracy: {result['accuracy_percentage']}%")
            print(f"{'=' * 80}\n")
            return

        print(f"File: {os.path.basename(result['ttl_file_path'])}")
        print(f"Building: {result['building_tag']}")
        print(f"Expected points: {result['expected_point_count']}")
        print(f"Actual points: {result['actual_point_count']}")
        print(f"Match result: {'✓ MATCHED' if result['match'] else '✗ MISMATCHED'}")
        print(f"Accuracy: {result['accuracy_percentage']}%")

        if result['validation_report']:
            print(f"\nValidation Report:")
            print("-" * 40)
            print(result['validation_report'])

        print(f"\n{'=' * 80}\n")

    def print_batch_point_count_report(self, batch_result: Dict):
        """Print batch point count validation report"""
        print(f"\n{'=' * 80}")
        print("BATCH POINT COUNT VALIDATION REPORT")
        print(f"{'=' * 80}")

        if 'error' in batch_result:
            print(f"❌ Error: {batch_result['error']}")
            print(f"{'=' * 80}\n")
            return

        print(batch_result['summary'])

        if batch_result['results']:
            print(f"\nIndividual Results:")
            print("-" * 70)
            print(f"{'Filename':<30} {'Building':<10} {'Expected':<8} {'Actual':<8} {'Status':<8}")
            print("-" * 70)

            for result in batch_result['results']:
                filename = os.path.basename(result['ttl_file_path'])
                building = result['building_tag']
                expected = result['expected_point_count']
                actual = result['actual_point_count']
                status = "✓ MATCH" if result['success'] else "✗ MISMATCH"

                print(f"{filename:<30} {building:<10} {expected:<8} {actual:<8} {status:<8}")

                if not result['success'] and 'error' in result:
                    print(f"  Error: {result['error']}")

        print(f"\n{'=' * 80}\n")

