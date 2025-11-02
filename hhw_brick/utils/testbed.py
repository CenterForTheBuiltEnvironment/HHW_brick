#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test data management module

Provides unified interface to access Brick models and timeseries data in Final_Test_Output
Allows App developers to conveniently access test data
"""

import os
import random
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union
import pandas as pd
from rdflib import Graph, Namespace

# Project root - testbed.py is under utils/, go up 4 levels to "Hot Water System"
# testbed.py -> utils -> hhw_brick -> HHW_brick -> Hot Water System
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
BRICK_MODELS_DIR = PROJECT_ROOT / "Final_Test_Output"
TIMESERIES_DATA_DIR = PROJECT_ROOT / "Example_Input_Data" / "hhw_system_data"

# Commonly used Brick namespaces (simplifies SPARQL writing)
BRICK = Namespace("https://brickschema.org/schema/Brick#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
REF = Namespace("https://brickschema.org/schema/Brick/ref#")

# Predefined SPARQL PREFIX (simplifies query writing)
SPARQL_PREFIXES = """
PREFIX brick: <https://brickschema.org/schema/Brick#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ref: <https://brickschema.org/schema/Brick/ref#>
PREFIX unit: <http://qudt.org/vocab/unit/>
"""


class TestDataset:
    """Test dataset class"""

    def __init__(self):
        """Initialize test dataset"""
        self.brick_models_dir = BRICK_MODELS_DIR
        self.timeseries_data_dir = TIMESERIES_DATA_DIR
        self._cache = {}

    def list_buildings(self, system_type: Optional[str] = None) -> List[str]:
        """
        List all available buildings

        Args:
            system_type: Filter system type, e.g. 'district_hw', 'condensing', 'district_steam' etc.

        Returns:
            Building ID list
        """
        buildings = []

        if not self.brick_models_dir.exists():
            return buildings

        for file in self.brick_models_dir.glob("building_*.ttl"):
            # Extract building ID and system type
            stem = file.stem  # building_29_district_hw_z
            parts = stem.split('_')

            if len(parts) < 3:
                continue

            building_id = parts[1]
            file_system_type = '_'.join(parts[2:-1]) if len(parts) > 3 else parts[2]

            # Filter system type
            if system_type and not file_system_type.startswith(system_type):
                continue

            buildings.append({
                'id': building_id,
                'system_type': file_system_type,
                'organization': parts[-1] if len(parts) > 3 else 'unknown',
                'brick_model': str(file),
                'timeseries_data': self._get_timeseries_path(building_id)
            })

        return sorted(buildings, key=lambda x: int(x['id']))

    def _get_timeseries_path(self, building_id: str) -> Optional[str]:
        """Get timeseries data path"""
        data_file = self.timeseries_data_dir / f"{building_id}hhw_system_data.csv"
        return str(data_file) if data_file.exists() else None

    def get_building(self, building_id: str) -> Optional[Dict]:
        """
        Get information for a single building

        Args:
            building_id: Building ID, e.g. '29'

        Returns:
            Building information dict containing brick_model and timeseries_data paths
        """
        buildings = self.list_buildings()
        for building in buildings:
            if building['id'] == str(building_id):
                return building
        return None

    def load_brick_model(self, building_id: str) -> Optional[Graph]:
        """
        Load Brick model for building

        Args:
            building_id: Building ID

        Returns:
            RDF Graph object
        """
        cache_key = f"brick_{building_id}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        building = self.get_building(building_id)
        if not building or not building['brick_model']:
            return None

        g = Graph()
        g.parse(building['brick_model'], format='turtle')

        self._cache[cache_key] = g
        return g

    def load_timeseries(self, building_id: str,
                       parse_dates: bool = True,
                       set_index: bool = True) -> Optional[pd.DataFrame]:
        """
        Load timeseries data for building

        Args:
            building_id: Building ID
            parse_dates: Whether to parse date columns
            set_index: Whether to set datetime_UTC as index

        Returns:
            DataFrame
        """
        cache_key = f"timeseries_{building_id}"

        if cache_key in self._cache:
            return self._cache[cache_key].copy()

        building = self.get_building(building_id)
        if not building or not building['timeseries_data']:
            return None

        df = pd.read_csv(building['timeseries_data'])

        if parse_dates and 'datetime_UTC' in df.columns:
            df['datetime_UTC'] = pd.to_datetime(df['datetime_UTC'])

        if set_index and 'datetime_UTC' in df.columns:
            df.set_index('datetime_UTC', inplace=True)

        self._cache[cache_key] = df
        return df.copy()

    def get_sensor_columns(self, building_id: str,
                          sensor_types: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Extract sensor to CSV column mapping from Brick model

        Args:
            building_id: Building ID
            sensor_types: Sensor type list (optional), e.g. ['Temperature_Sensor', 'Flow_Sensor']

        Returns:
            Dict with sensor URI as key and CSV column name as value
        """
        g = self.load_brick_model(building_id)
        if not g:
            return {}

        # SPARQL query to get timeseries ID of sensors
        query = """
        PREFIX ref: <https://brickschema.org/schema/Brick/ref#>
        PREFIX brick: <https://brickschema.org/schema/Brick#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?sensor ?column WHERE {
            ?sensor ref:hasExternalReference ?ref .
            ?ref ref:hasTimeseriesId ?column .
        }
        """

        results = list(g.query(query))
        mapping = {str(row[0]): str(row[1]) for row in results}

        return mapping

    def filter_buildings_by_query(self, sparql_query: str) -> List[Dict]:
        """
        Filter buildings using SPARQL query

        Args:
            sparql_query: SPARQL query string (PREFIX can be omitted, will be added automatically)

        Returns:
            List of qualified buildings
        """
        # Automatically add PREFIX (if not present)
        if 'PREFIX' not in sparql_query.upper():
            sparql_query = SPARQL_PREFIXES + sparql_query

        qualified_buildings = []

        for building in self.list_buildings():
            try:
                g = self.load_brick_model(building['id'])
                if not g:
                    continue

                results = list(g.query(sparql_query))
                if results:
                    building['query_results'] = results
                    qualified_buildings.append(building)
            except Exception as e:
                print(f"Querying building {building['id']} error occurred: {e}")
                continue

        return qualified_buildings

    def query_with_data(self, building_id: str, sparql_query: str) -> Optional[pd.DataFrame]:
        """
        Execute SPARQL query and automatically extract corresponding timeseries data

        Similar to pymortar qualify + fetch pattern

        Args:
            building_id: Building ID
            sparql_query: SPARQL query (returned variables will be mapped to data columns)

        Returns:
            DataFrame containing data corresponding to query results

        Example:
            >>> # Query supply and return temperature sensors
            >>> query = "SELECT ?sup ?ret WHERE { ... }"
            >>> df = query_with_data('29', query)
            >>> # df contains 'sup' and 'ret' columns
        """
        # Automatically add PREFIX
        if 'PREFIX' not in sparql_query.upper():
            sparql_query = SPARQL_PREFIXES + sparql_query

        # Load Brick model
        g = self.load_brick_model(building_id)
        if not g:
            return None

        # Execute query
        results = list(g.query(sparql_query))
        if not results:
            return None

        # Get sensor column mapping
        sensor_columns = self.get_sensor_columns(building_id)

        # Load timeseries data
        df = self.load_timeseries(building_id)
        if df is None:
            return None

        # Extract columns corresponding to sensors in query results
        # First row of results contains all sensor URIs
        sensor_uris = [str(uri) for uri in results[0]]

        # Find corresponding column name
        columns_to_extract = []
        column_mapping = {}

        for sensor_uri in sensor_uris:
            # Find from sensor column mapping
            for uri, col_name in sensor_columns.items():
                if sensor_uri in uri or uri in sensor_uri:
                    columns_to_extract.append(col_name)
                    column_mapping[col_name] = sensor_uri
                    break

        if not columns_to_extract:
            return None

        # Extract data
        df_extracted = df[columns_to_extract].copy()

        return df_extracted

    def sample_buildings(self,
                        n: int = 5,
                        system_type: Optional[str] = None,
                        random_seed: Optional[int] = None) -> List[Dict]:
        """
        Randomly sample n buildings

        Args:
            n: Sample size
            system_type: Filter system type（optional）
            random_seed: Random seed (optional, for reproducible random sampling)

        Returns:
            List of randomly sampled buildings
        """
        buildings = self.list_buildings(system_type)

        if random_seed is not None:
            random.seed(random_seed)

        n = min(n, len(buildings))
        return random.sample(buildings, n)

    def sample_buildings_per_system(self,
                                    n_per_system: int = 2,
                                    random_seed: Optional[int] = None) -> Dict[str, List[Dict]]:
        """
        Randomly sample n buildings for each system type

        Args:
            n_per_system: Sample size for each system type
            random_seed: Random seed (optional)

        Returns:
            Dict with system type as key and building list as value
        """
        if random_seed is not None:
            random.seed(random_seed)

        all_buildings = self.list_buildings()

        # Group by system type
        by_system = {}
        for building in all_buildings:
            system_type = building['system_type']
            if system_type not in by_system:
                by_system[system_type] = []
            by_system[system_type].append(building)

        # Sample for each system type
        sampled = {}
        for system_type, buildings in by_system.items():
            n = min(n_per_system, len(buildings))
            sampled[system_type] = random.sample(buildings, n)

        return sampled

    def get_buildings_with_sensors(self, sensor_types: List[str]) -> List[Dict]:
        """
        Get all buildings containing specified sensor types

        Args:
            sensor_types: Sensor type list (simplified name, e.g. 'Temperature_Sensor'）

        Returns:
            List of qualified buildings
        """
        # Build SPARQL query
        sensor_types_str = ' '.join([f'brick:{st}' for st in sensor_types])

        query = f"""
        SELECT ?sensor WHERE {{
            ?sensor rdf:type/rdfs:subClassOf* ?sensor_type .
            VALUES ?sensor_type {{ {sensor_types_str} }}
        }}
        """

        return self.filter_buildings_by_query(query)


# Global singleton
_dataset = None


def get_dataset() -> TestDataset:
    """Get global test dataset instance"""
    global _dataset
    if _dataset is None:
        _dataset = TestDataset()
    return _dataset


# Convenience functions

def list_buildings(system_type: Optional[str] = None) -> List[str]:
    """List all buildings"""
    return get_dataset().list_buildings(system_type)


def get_building(building_id: str) -> Optional[Dict]:
    """Get building information"""
    return get_dataset().get_building(building_id)


def load_brick_model(building_id: str) -> Optional[Graph]:
    """Load Brick model"""
    return get_dataset().load_brick_model(building_id)


def load_timeseries(building_id: str, **kwargs) -> Optional[pd.DataFrame]:
    """Load timeseries data"""
    return get_dataset().load_timeseries(building_id, **kwargs)


def get_sensor_columns(building_id: str, sensor_types: Optional[List[str]] = None) -> Dict[str, str]:
    """Get sensor column mapping"""
    return get_dataset().get_sensor_columns(building_id, sensor_types)


def find_qualified_buildings(sparql_query: str) -> List[Dict]:
    """Find qualified buildings (SPARQL PREFIX can be omitted)"""
    return get_dataset().filter_buildings_by_query(sparql_query)


def query_with_data(building_id: str, sparql_query: str) -> Optional[pd.DataFrame]:
    """
    Execute SPARQL query and automatically extract corresponding timeseries data

    Similar to pymortar qualify + fetch pattern
    """
    return get_dataset().query_with_data(building_id, sparql_query)


def sample_buildings(n: int = 5,
                    system_type: Optional[str] = None,
                    random_seed: Optional[int] = None) -> List[Dict]:
    """Randomly sample n buildings"""
    return get_dataset().sample_buildings(n, system_type, random_seed)


def sample_per_system(n_per_system: int = 2,
                     random_seed: Optional[int] = None) -> Dict[str, List[Dict]]:
    """Randomly sample n buildings for each system type"""
    return get_dataset().sample_buildings_per_system(n_per_system, random_seed)


def get_buildings_with_sensors(sensor_types: List[str]) -> List[Dict]:
    """Get all buildings containing specified sensor types"""
    return get_dataset().get_buildings_with_sensors(sensor_types)


# Example usage
if __name__ == "__main__":
    print("="*80)
    print("Test data module functionality demonstration")
    print("="*80)

    # 1. List buildings
    print("\n1. List all district_hw system buildings:")
    buildings = list_buildings(system_type='district_hw')
    print(f"   Found {len(buildings)} buildings")

    # 2. Random sampling
    print("\n2. Randomly sample 3 buildings:")
    sampled = sample_buildings(n=3, system_type='district_hw', random_seed=42)
    for b in sampled:
        print(f"   - Building {b['id']}: {b['system_type']}")

    # 3. Sample for each system type
    print("\n3. Sample 1 building for each system type:")
    by_system = sample_per_system(n_per_system=1, random_seed=42)
    for system_type, buildings in list(by_system.items())[:5]:
        print(f"   {system_type}: {[b['id'] for b in buildings]}")

    # 4. Simplified SPARQL query (no need to write PREFIX)
    print("\n4. Use simplified SPARQL query:")
    print("   Query: Find buildings with supply and return temperature sensors")

    query = """
    SELECT ?loop ?sup ?ret WHERE {
        ?loop rdf:type/rdfs:subClassOf* brick:Hot_Water_Loop .
        ?sup rdf:type/rdfs:subClassOf* brick:Leaving_Hot_Water_Temperature_Sensor .
        ?ret rdf:type/rdfs:subClassOf* brick:Entering_Hot_Water_Temperature_Sensor .
        ?loop brick:hasPart ?sup .
        ?loop brick:hasPart ?ret .
    }
    """

    qualified = find_qualified_buildings(query)
    print(f"   to {len(qualified)} qualified buildings")
    for b in qualified[:3]:
        print(f"   - Building {b['id']}")

    # 5. query_with_data functionality (automatically associate data)
    print("\n5. use query_with_data automatically get sensor data:")
    if qualified:
        building_id = qualified[0]['id']
        print(f"   Testing Building {building_id}")

        # This query will automatically extract data from sup and ret columns
        query = """
        SELECT ?sup ?ret WHERE {
            ?loop brick:hasPart ?sup .
            ?loop brick:hasPart ?ret .
            ?sup rdf:type/rdfs:subClassOf* brick:Leaving_Hot_Water_Temperature_Sensor .
            ?ret rdf:type/rdfs:subClassOf* brick:Entering_Hot_Water_Temperature_Sensor .
        }
        """

        df = query_with_data(building_id, query)
        if df is not None:
            print(f"   ✓ Automatically extracted data")
            print(f"     Shape: {df.shape}")
            print(f"     Columns: {list(df.columns)}")
        else:
            print(f"   ✗ Unable to extract data")

    print("\n" + "="*80)
    print("Demonstration complete!")
    print("="*80)

