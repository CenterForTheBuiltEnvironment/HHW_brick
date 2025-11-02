#!/usr/bin/env python3
"""
Subgraph Pattern Validator for Brick Models
Validates Hot Water System patterns using SPARQL queries

Updated to match new pattern diagrams:
- Pattern 1: Boiler System with Dual Loops (Primary + Secondary)
- Pattern 2: District System with Single Loop (Secondary only)
"""

import os
import logging
from typing import Dict
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing

logger = logging.getLogger(__name__)

# Attempt to import brickschema
try:
    from brickschema import Graph
    _BRICKSCHEMA_AVAILABLE = True
except ImportError:  # pragma: no cover
    _BRICKSCHEMA_AVAILABLE = False
    Graph = None


class SubgraphPatternValidator:
    """Validator for matching subgraph patterns in Brick models using SPARQL queries

    Pattern 1 (Boiler System - Dual Loop):
        - Building rec:isLocationOf Hot_Water_System (required)
        - Building rec:isLocationOf Weather_Station (optional)
        - Hot_Water_System brick:hasPart Primary_Loop (required)
        - Hot_Water_System brick:hasPart Secondary_Loop (required)
        - Primary_Loop brick:hasPart Boiler (required)
        - Primary_Loop brick:hasPart Pump (required)
        - Boiler brick:feeds Pump (required)
        - Primary_Loop brick:feeds Secondary_Loop (required)
        - Secondary_Loop brick:hasPart Pump (required)

        Variants:
        - Condensing_Natural_Gas_Boiler
        - Noncondensing_Natural_Gas_Boiler
        - Generic Boiler
        - Any Boiler type

    Pattern 2 (District System - Single Loop):
        - Building rec:isLocationOf Hot_Water_System (required)
        - Building rec:isLocationOf Weather_Station (optional)
        - Hot_Water_System brick:hasPart Hot_Water_Loop (Secondary only) (required)
        - Hot_Water_Loop brick:hasPart Pump (required)
        - NO Boiler (district heating from central plant)
        - NO Primary Loop
    """

    def __init__(self):
        """Initialize subgraph pattern validator"""
        if not _BRICKSCHEMA_AVAILABLE:
            raise ImportError("brickschema is not available. Please install with: pip install brickschema")

    def _parse_ttl_file(self, ttl_file_path: str, max_retries: int = 2):
        """Helper method to parse TTL file with retry logic

        Args:
            ttl_file_path: Path to TTL file
            max_retries: Maximum number of retry attempts

        Returns:
            Tuple of (Graph object, error message or None)
        """
        import time

        for attempt in range(max_retries):
            try:
                # Load Brick ontology to enable class hierarchy reasoning
                g = Graph(load_brick=True)

                try:
                    g.parse(ttl_file_path, format="turtle")
                    # Expand graph to include rdfs:subClassOf inferences
                    try:
                        g.expand(profile='brick')
                    except:
                        # If expand fails, continue without it (basic validation still works)
                        logger.debug(f"Graph expansion failed for {ttl_file_path}, continuing with basic graph")
                    return g, None
                except Exception as parse_error:
                    logger.warning(f"Standard parsing failed for {ttl_file_path}: {parse_error}")
                    try:
                        with open(ttl_file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        g.parse(data=content, format="turtle")
                        try:
                            g.expand(profile='brick')
                        except:
                            logger.debug("Graph expansion failed, continuing with basic graph")
                        return g, None
                    except Exception as alt_error:
                        if attempt < max_retries - 1:
                            logger.warning(f"Retry attempt {attempt + 1}/{max_retries} for {ttl_file_path}")
                            time.sleep(0.05 * (attempt + 1))
                            continue
                        return None, f"Parsing failed: {alt_error}"

            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(0.05 * (attempt + 1))
                    continue
                return None, f"Error: {e}"

        return None, "All retry attempts failed"

    def check_pattern_1_boiler_system(self, ttl_file_path: str) -> Dict:
        """Check if TTL file matches Pattern 1 (Boiler System - Dual Loop)

        Pattern 1: Building has Hot_Water_System (required)
                   Hot_Water_System has Primary_Loop (required)
                   Hot_Water_System has Secondary_Loop (required)
                   Primary_Loop has Boiler (required)
                   Primary_Loop has Pump (required)
                   Boiler feeds Pump (required)
                   Primary_Loop feeds Secondary_Loop (required)
                   Secondary_Loop has Pump (required)
                   Building has Weather_Station (optional)

        Args:
            ttl_file_path: Path to TTL file

        Returns:
            Dict with match results and details
        """
        g, error = self._parse_ttl_file(ttl_file_path)
        if g is None:
            return {
                'pattern': 'Pattern 1 - Boiler System',
                'matched': False,
                'error': error,
                'details': {}
            }

        sparql_query = """
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        PREFIX rec:   <https://w3id.org/rec#>
        PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?building ?hws ?primary_loop ?secondary_loop ?boiler ?boiler_class ?prim_pump ?sec_pump ?weather_station
        WHERE {
          # Required: Building
          ?building rdf:type rec:Building .
          
          # Required: Building has Hot_Water_System
          ?building rec:isLocationOf ?hws .
          ?hws rdf:type brick:Hot_Water_System .
          
          # Required: Hot_Water_System has Primary_Loop
          ?hws brick:hasPart ?primary_loop .
          ?primary_loop rdf:type brick:Hot_Water_Loop .
          
          # Required: Hot_Water_System has Secondary_Loop
          ?hws brick:hasPart ?secondary_loop .
          ?secondary_loop rdf:type brick:Hot_Water_Loop .
          
          # Required: Primary_Loop feeds Secondary_Loop
          ?primary_loop brick:feeds ?secondary_loop .
          
          # Required: Primary_Loop has Boiler (using subClassOf reasoning)
          ?primary_loop brick:hasPart ?boiler .
          ?boiler rdf:type ?boiler_class .
          ?boiler_class rdfs:subClassOf* brick:Boiler .
          
          # Required: Primary_Loop has Pump
          ?primary_loop brick:hasPart ?prim_pump .
          ?prim_pump rdf:type brick:Pump .
          
          # Required: Boiler feeds Pump
          ?boiler brick:feeds ?prim_pump .
          
          # Required: Secondary_Loop has Pump
          ?secondary_loop brick:hasPart ?sec_pump .
          ?sec_pump rdf:type brick:Pump .
          
          # Optional: Weather_Station
          OPTIONAL {
            ?building rec:isLocationOf ?weather_station .
            ?weather_station rdf:type brick:Weather_Station .
          }
        }
        """

        try:
            results = list(g.query(sparql_query))
            matched = len(results) > 0

            details = {
                'has_building': False,
                'has_hot_water_system': False,
                'has_primary_loop': False,
                'has_secondary_loop': False,
                'has_boiler': False,
                'has_primary_pump': False,
                'has_secondary_pump': False,
                'has_boiler_feeds_pump': False,
                'has_primary_feeds_secondary': False,
                'has_weather_station': False,
                'boiler_count': 0,
                'primary_pump_count': 0,
                'secondary_pump_count': 0
            }

            if matched:
                # Extract details from first result
                row = results[0]
                details['has_building'] = row['building'] is not None
                details['has_hot_water_system'] = row['hws'] is not None
                details['has_primary_loop'] = row['primary_loop'] is not None
                details['has_secondary_loop'] = row['secondary_loop'] is not None
                details['has_boiler'] = row['boiler'] is not None
                details['has_primary_pump'] = row['prim_pump'] is not None
                details['has_secondary_pump'] = row['sec_pump'] is not None
                details['has_weather_station'] = row['weather_station'] is not None
                details['has_boiler_feeds_pump'] = True  # Query enforces this
                details['has_primary_feeds_secondary'] = True  # Query enforces this

                # Count unique entities and collect types
                boilers = set()
                boiler_types = set()
                prim_pumps = set()
                sec_pumps = set()
                for row in results:
                    if row['boiler']:
                        boilers.add(str(row['boiler']))
                    if row.get('boiler_class'):
                        # Extract just the class name from URI
                        boiler_class_uri = str(row['boiler_class'])
                        if '#' in boiler_class_uri:
                            boiler_class_name = boiler_class_uri.split('#')[-1]
                            boiler_types.add(boiler_class_name)
                    if row['prim_pump']:
                        prim_pumps.add(str(row['prim_pump']))
                    if row['sec_pump']:
                        sec_pumps.add(str(row['sec_pump']))

                details['boiler_count'] = len(boilers)
                details['primary_pump_count'] = len(prim_pumps)
                details['secondary_pump_count'] = len(sec_pumps)
                details['boiler_types'] = sorted(list(boiler_types))

            return {
                'pattern': 'Pattern 1 - Boiler System',
                'matched': matched,
                'details': details
            }

        except Exception as e:
            logger.error(f"Error checking Pattern 1: {e}")
            return {
                'pattern': 'Pattern 1 - Boiler System',
                'matched': False,
                'error': str(e),
                'details': {}
            }

    def check_pattern_2_district_system(self, ttl_file_path: str) -> Dict:
        """Check if TTL file matches Pattern 2 (District System - Single Loop)

        Pattern 2: Building has Hot_Water_System (required)
                   Hot_Water_System has Hot_Water_Loop (Secondary only) (required)
                   Hot_Water_Loop has Pump (required)
                   Building has Weather_Station (optional)
                   NO Boiler (district heating from central plant)
                   NO Primary Loop

        Args:
            ttl_file_path: Path to TTL file

        Returns:
            Dict with match results and details
        """
        g, error = self._parse_ttl_file(ttl_file_path)
        if g is None:
            return {
                'pattern': 'Pattern 2 - District System',
                'matched': False,
                'error': error,
                'details': {}
            }

        sparql_query = """
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        PREFIX rec:   <https://w3id.org/rec#>
        PREFIX rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?building ?hws ?secondary_loop ?pump ?weather_station
        WHERE {
          # Required: Building
          ?building rdf:type rec:Building .
          
          # Required: Building has Hot_Water_System
          ?building rec:isLocationOf ?hws .
          ?hws rdf:type brick:Hot_Water_System .
          
          # Required: Hot_Water_System has Hot_Water_Loop (Secondary)
          ?hws brick:hasPart ?secondary_loop .
          ?secondary_loop rdf:type brick:Hot_Water_Loop .
          
          # Required: Secondary_Loop has Pump
          ?secondary_loop brick:hasPart ?pump .
          ?pump rdf:type brick:Pump .
          
          # Check NO boiler exists (key for district system)
          FILTER NOT EXISTS {
            ?hws brick:hasPart ?loop .
            ?loop brick:hasPart ?boiler .
            ?boiler rdf:type ?boiler_class .
            ?boiler_class rdfs:subClassOf* brick:Boiler .
          }
          
          # Check NO Primary Loop exists (only Secondary)
          FILTER NOT EXISTS {
            ?hws brick:hasPart ?prim_loop .
            ?prim_loop brick:feeds ?secondary_loop .
          }
          
          # Optional: Weather_Station
          OPTIONAL {
            ?building rec:isLocationOf ?weather_station .
            ?weather_station rdf:type brick:Weather_Station .
          }
        }
        """

        try:
            results = list(g.query(sparql_query))
            matched = len(results) > 0

            details = {
                'has_building': False,
                'has_hot_water_system': False,
                'has_secondary_loop': False,
                'has_pump': False,
                'has_boiler': False,  # Should be False for district system
                'has_primary_loop': False,  # Should be False for district system
                'has_weather_station': False,
                'pump_count': 0
            }

            if matched:
                # Extract details from first result
                row = results[0]
                details['has_building'] = row['building'] is not None
                details['has_hot_water_system'] = row['hws'] is not None
                details['has_secondary_loop'] = row['secondary_loop'] is not None
                details['has_pump'] = row['pump'] is not None
                details['has_weather_station'] = row['weather_station'] is not None

                # Count unique pumps
                pumps = set()
                for row in results:
                    if row['pump']:
                        pumps.add(str(row['pump']))

                details['pump_count'] = len(pumps)

            return {
                'pattern': 'Pattern 2 - District System',
                'matched': matched,
                'details': details
            }

        except Exception as e:
            logger.error(f"Error checking Pattern 2: {e}")
            return {
                'pattern': 'Pattern 2 - District System',
                'matched': False,
                'error': str(e),
                'details': {}
            }

    def validate_building(self, ttl_file_path: str) -> Dict:
        """Validate a single building TTL file against both patterns

        Returns which pattern(s) the building matches, with specific boiler type variants

        Args:
            ttl_file_path: Path to TTL file

        Returns:
            Dict with validation results for all patterns
        """
        if not os.path.exists(ttl_file_path):
            return {
                'ttl_file_path': ttl_file_path,
                'building_tag': 'unknown',
                'error': f'TTL file not found: {ttl_file_path}'
            }

        # Extract building tag from filename
        building_tag = 'unknown'
        filename = os.path.basename(ttl_file_path)
        if filename.startswith('building_'):
            parts = filename.split('_')
            if len(parts) >= 2:
                building_tag = parts[1]

        logger.info(f"Validating building {building_tag}: {ttl_file_path}")

        results = {
            'ttl_file_path': ttl_file_path,
            'building_tag': building_tag,
            'filename': filename,
            'patterns': {}
        }

        # Check Pattern 1: Boiler System (all boiler types)
        pattern_1 = self.check_pattern_1_boiler_system(ttl_file_path)
        results['patterns']['pattern_1_boiler'] = pattern_1

        # Check Pattern 2: District System
        pattern_2 = self.check_pattern_2_district_system(ttl_file_path)
        results['patterns']['pattern_2_district'] = pattern_2

        # Determine which pattern this building matches
        matched_patterns = []
        if pattern_1['matched']:
            # Determine boiler type from details
            boiler_types = pattern_1.get('details', {}).get('boiler_types', [])
            if boiler_types:
                if 'Condensing_Natural_Gas_Boiler' in boiler_types:
                    matched_patterns.append('Pattern 1 - Condensing Boiler')
                elif 'Noncondensing_Natural_Gas_Boiler' in boiler_types:
                    matched_patterns.append('Pattern 1 - Non-Condensing Boiler')
                else:
                    matched_patterns.append(f'Pattern 1 - {", ".join(boiler_types)}')
            else:
                matched_patterns.append('Pattern 1 - Boiler System')

        if pattern_2['matched']:
            matched_patterns.append('Pattern 2 - District System')

        results['matched_patterns'] = matched_patterns
        results['primary_pattern'] = matched_patterns[0] if matched_patterns else 'No Pattern Matched'

        return results

    def batch_validate_all_buildings(self, ttl_directory: str, max_workers: int = None) -> Dict:
        """Validate all building TTL files in a directory with parallel processing

        Args:
            ttl_directory: Directory containing TTL files
            max_workers: Number of parallel workers (default: CPU count - 1)

        Returns:
            Dict with comprehensive validation results and accuracy statistics
        """
        if not os.path.exists(ttl_directory):
            return {
                'error': f'Directory not found: {ttl_directory}',
                'total_files': 0,
                'results': []
            }

        # Find all TTL files
        ttl_files = [f for f in os.listdir(ttl_directory) if f.endswith('.ttl')]

        logger.info(f"Found {len(ttl_files)} TTL files to validate")

        # Determine number of workers
        if max_workers is None:
            max_workers = max(1, multiprocessing.cpu_count() - 1)

        logger.info(f"Using {max_workers} parallel workers for validation")
        print(f"⚙️  Using {max_workers} parallel workers for faster processing")

        all_results = []
        pattern_stats = {
            'pattern_1_any_boiler': {'matched': 0, 'total': 0},
            'pattern_1_condensing': {'matched': 0, 'total': 0},
            'pattern_1_non_condensing': {'matched': 0, 'total': 0},
            'pattern_1_generic_boiler': {'matched': 0, 'total': 0},
            'pattern_2_district': {'matched': 0, 'total': 0}
        }

        # Track pattern matches during processing
        pattern_1_count = 0
        pattern_2_count = 0
        condensing_count = 0
        non_condensing_count = 0

        # Validate each file with parallel processing and progress bar
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(validate_building_worker, os.path.join(ttl_directory, filename)): filename
                for filename in ttl_files
            }

            # Collect results with progress bar
            for future in tqdm(as_completed(future_to_file), total=len(ttl_files), desc="Validating buildings"):
                try:
                    result = future.result()
                    all_results.append(result)

                    # Track and display progress
                    if 'patterns' in result:
                        # Update statistics
                        for pattern_key, pattern_result in result['patterns'].items():
                            if pattern_key in pattern_stats:
                                pattern_stats[pattern_key]['total'] += 1
                                if pattern_result.get('matched', False):
                                    pattern_stats[pattern_key]['matched'] += 1

                        # Track specific patterns for progress display
                        primary = result.get('primary_pattern', '')
                        # Check Non-Condensing FIRST since it contains "Condensing" substring
                        if 'Non-Condensing Boiler' in primary:
                            non_condensing_count += 1
                        elif 'Condensing Boiler' in primary:
                            condensing_count += 1
                        elif 'Pattern 1' in primary:
                            pattern_1_count += 1
                        if 'Pattern 2' in primary:
                            pattern_2_count += 1

                except Exception as e:
                    filename = future_to_file[future]
                    logger.error(f"Error validating {filename}: {e}")
                    all_results.append({
                        'filename': filename,
                        'error': str(e)
                    })

        # Print progress summary after parallel processing
        print(f"\n✅ Validation Complete!")
        print(f"   Processed: {len(all_results)} buildings")
        print(f"   🔥 Boiler Systems Found: {condensing_count + non_condensing_count + pattern_1_count}")
        print(f"      - Condensing: {condensing_count}")
        print(f"      - Non-Condensing: {non_condensing_count}")
        print(f"      - Other Types: {pattern_1_count}")
        print(f"   🏭 District Systems Found: {pattern_2_count}")
        print()

        # Calculate accuracy for each pattern
        accuracies = {}
        for pattern_key, stats in pattern_stats.items():
            if stats['total'] > 0:
                accuracy = (stats['matched'] / stats['total']) * 100
                accuracies[pattern_key] = {
                    'matched': stats['matched'],
                    'total': stats['total'],
                    'accuracy_percentage': accuracy
                }

        # Generate summary
        summary_lines = [
            "=" * 80,
            "SUBGRAPH PATTERN VALIDATION SUMMARY",
            "=" * 80,
            f"Total Buildings Validated: {len(ttl_files)}",
            "",
            "Pattern Matching Accuracies:",
            "-" * 80
        ]

        pattern_names = {
            'pattern_1_any_boiler': 'Pattern 1 - Any Boiler System',
            'pattern_1_condensing': 'Pattern 1 - Condensing Boiler',
            'pattern_1_non_condensing': 'Pattern 1 - Non-Condensing Boiler',
            'pattern_1_generic_boiler': 'Pattern 1 - Generic Boiler',
            'pattern_2_district': 'Pattern 2 - District System'
        }

        for pattern_key, pattern_name in pattern_names.items():
            if pattern_key in accuracies:
                acc = accuracies[pattern_key]
                summary_lines.append(
                    f"{pattern_name}: {acc['matched']}/{acc['total']} "
                    f"({acc['accuracy_percentage']:.2f}%)"
                )

        summary_lines.extend([
            "-" * 80,
            "",
            "Building Pattern Distribution:",
            "-" * 80
        ])

        # Count buildings by primary pattern
        pattern_distribution = {}
        for result in all_results:
            primary = result.get('primary_pattern', 'Unknown')
            pattern_distribution[primary] = pattern_distribution.get(primary, 0) + 1

        for pattern, count in sorted(pattern_distribution.items()):
            percentage = (count / len(ttl_files)) * 100 if ttl_files else 0
            summary_lines.append(f"  {pattern}: {count} ({percentage:.1f}%)")

        summary_lines.append("=" * 80)

        return {
            'total_files': len(ttl_files),
            'results': all_results,
            'accuracies': accuracies,
            'pattern_distribution': pattern_distribution,
            'summary': '\n'.join(summary_lines)
        }


# Worker function for parallel processing (must be at module level for multiprocessing)
def validate_building_worker(ttl_file_path: str) -> Dict:
    """Worker function to validate a single building (for parallel processing)

    This function must be at module level to work with multiprocessing.

    Args:
        ttl_file_path: Path to TTL file

    Returns:
        Dict with validation results
    """
    validator = SubgraphPatternValidator()
    return validator.validate_building(ttl_file_path)

