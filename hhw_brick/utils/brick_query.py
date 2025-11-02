#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Data loading helper functions

Provides unified data loading and mapping functionality to simplify App development
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple
from rdflib import Graph, Namespace

# Brick namespace
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


def load_data(brick_model_path: str, timeseries_data_path: str) -> Tuple[Graph, pd.DataFrame]:
    """
    Load Brick model and timeseries data

    Args:
        brick_model_path: Brick model path
        timeseries_data_path: Timeseries data path

    Returns:
        (Graph, DataFrame) tuple
    """
    # Load Brick model
    g = Graph()
    g.parse(brick_model_path, format="turtle")

    # Load timeseries data
    df = pd.read_csv(timeseries_data_path)

    # Parse time column
    if "datetime_UTC" in df.columns:
        df["datetime_UTC"] = pd.to_datetime(df["datetime_UTC"])
        df.set_index("datetime_UTC", inplace=True)

    return g, df


def query_sensors(
    graph: Graph,
    sensor_types: List[str],
    equipment_type: Optional[str] = None,
    connection_property: str = "hasPart",
    custom_query: Optional[str] = None,
) -> List[Tuple]:
    """
    Generic sensor query function

    Args:
        graph: Brick Graph
        sensor_types: List of sensor types (supports multiple equivalent types)
        equipment_type: Equipment type (optional), e.g. 'Hot_Water_Loop'
        connection_property: Connection property, 'hasPart' or 'isPointOf'
        custom_query: Custom SPARQL query (optional, PREFIX can be omitted)

    Returns:
        Query result list
    """
    # If custom query provided, use it
    if custom_query:
        # Automatically add PREFIX (if not present)
        if "PREFIX" not in custom_query.upper():
            custom_query = SPARQL_PREFIXES + custom_query
        return list(graph.query(custom_query))

    # Build VALUES clause
    sensor_types_values = " ".join([f"brick:{st}" for st in sensor_types])

    # Build query based on connection property
    if connection_property == "hasPart":
        connection_pattern = "?equipment brick:hasPart ?sensor"
    else:
        connection_pattern = "?sensor brick:isPointOf ?equipment"

    # Build query
    if equipment_type:
        query = f"""
        {SPARQL_PREFIXES}
        SELECT ?equipment ?sensor WHERE {{
            ?equipment rdf:type/rdfs:subClassOf* brick:{equipment_type} .
            ?sensor rdf:type/rdfs:subClassOf* ?sensor_type .
            VALUES ?sensor_type {{ {sensor_types_values} }}
            {{ {connection_pattern} }}
        }}
        """
    else:
        query = f"""
        {SPARQL_PREFIXES}
        SELECT ?sensor WHERE {{
            ?sensor rdf:type/rdfs:subClassOf* ?sensor_type .
            VALUES ?sensor_type {{ {sensor_types_values} }}
        }}
        """

    return list(graph.query(query))


def get_sensor_column_name(sensor_uri: str) -> str:
    """
    Extract corresponding CSV column name from sensor URI

    Args:
        sensor_uri: Sensor URI

    Returns:
        CSV column name

    Examples:
        >>> get_sensor_column_name("https://hhws.example.org#building29.hws.sup")
        'sup'
    """
    # Extract last part
    if "#" in sensor_uri:
        local_name = sensor_uri.split("#")[-1]
    else:
        local_name = sensor_uri.split("/")[-1]

    # Extract part after last dot
    if "." in local_name:
        return local_name.split(".")[-1]

    return local_name


def get_sensor_column_from_ref(graph: Graph, sensor_uri: str) -> Optional[str]:
    """
    Get column name from ref:hasTimeseriesId in Brick model

    Args:
        graph: Brick Graph
        sensor_uri: Sensor URI

    Returns:
        CSV column name, returns None if not found
    """
    query = f"""
    {SPARQL_PREFIXES}
    SELECT ?column WHERE {{
        <{sensor_uri}> ref:hasExternalReference ?ref .
        ?ref ref:hasTimeseriesId ?column .
    }}
    """

    results = list(graph.query(query))
    if results:
        return str(results[0][0])

    return None


def map_sensors_to_columns(
    graph: Graph, sensor_uris: List[str], dataframe: pd.DataFrame
) -> Dict[str, str]:
    """
    Map sensor URI to DataFrame column names

    Preferably use ref:hasTimeseriesId, otherwise infer from URI

    Args:
        graph: Brick Graph
        sensor_uris: List of sensor URIs
        dataframe: Timeseries data DataFrame

    Returns:
        Mapping dictionary {sensor_uri: column_name}
    """
    mapping = {}
    df_columns = set(dataframe.columns)

    for sensor_uri in sensor_uris:
        # First try to get from ref
        column = get_sensor_column_from_ref(graph, sensor_uri)

        # If not found, infer from URI
        if not column:
            column = get_sensor_column_name(sensor_uri)

        # Check if column exists
        if column in df_columns:
            mapping[sensor_uri] = column

    return mapping


def extract_data_columns(
    dataframe: pd.DataFrame,
    column_mapping: Dict[str, str],
    rename_map: Optional[Dict[str, str]] = None,
) -> pd.DataFrame:
    """
    Extract specified columns from DataFrame and rename

    Args:
        dataframe: Original DataFrame
        column_mapping: Sensor to column name mapping
        rename_map: Rename mapping (optional), e.g. {sensor_uri: 'new_name'}

    Returns:
        Extracted and renamed DataFrame
    """
    # Extract columns
    columns_to_extract = list(column_mapping.values())
    df_extracted = dataframe[columns_to_extract].copy()

    # Rename
    if rename_map:
        reverse_mapping = {v: rename_map.get(k, v) for k, v in column_mapping.items()}
        df_extracted.rename(columns=reverse_mapping, inplace=True)

    return df_extracted


def filter_time_range(
    dataframe: pd.DataFrame, start_time: Optional[str] = None, end_time: Optional[str] = None
) -> pd.DataFrame:
    """
    Filter time range

    Args:
        dataframe: DataFrame (index must be datetime)
        start_time: Start time (ISO format string)
        end_time: End time (ISO format string)

    Returns:
        Filtered DataFrame
    """
    df = dataframe.copy()

    if start_time:
        start = pd.to_datetime(start_time)
        # Handle timezone
        if hasattr(df.index, "tz") and df.index.tz is not None:
            if start.tz is None:
                start = start.tz_localize(df.index.tz)
        df = df[df.index >= start]

    if end_time:
        end = pd.to_datetime(end_time)
        # Handle timezone
        if hasattr(df.index, "tz") and df.index.tz is not None:
            if end.tz is None:
                end = end.tz_localize(df.index.tz)
        df = df[df.index <= end]

    return df


# NOTE: App-specific sensor queries should be defined in each app,
# not in this universal utility module.
