"""
CSV to Brick Converter Module

Core functionality for converting HHWS CSV data to Brick ontology format.


Author: Mingchen Li
"""

import pandas as pd
import logging
import yaml
from typing import Dict, List, Optional, Any
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD
from pathlib import Path


class CSVToBrickConverter:
    """
    Converts CSV data to Brick ontology format for HHWS applications.
    Supports different system types with hierarchical equipment naming.
    """
    def __init__(self):
        """Initialize the CSV to Brick converter."""
        self.logger = logging.getLogger(__name__)
        self.graph = Graph()

        # Initialize validation warnings list
        self.validation_warnings = []

        # Define namespaces - using standard Brick namespace
        self.brick = Namespace("https://brickschema.org/schema/Brick#")
        self.hhws = Namespace("https://hhws.example.org#")  # Use # suffix for consistency
        self.rec = Namespace("https://w3id.org/rec#")  # RealEstateCore namespace for Building
        self.unit = Namespace("http://qudt.org/vocab/unit/")
        self.owl = Namespace("http://www.w3.org/2002/07/owl#")
        self.ref = Namespace("https://brickschema.org/schema/Brick/ref#")  # Add ref namespace

        # Bind namespaces
        self.graph.bind("brick", self.brick, override=True, replace=True)
        self.graph.bind("hhws", self.hhws, override=True, replace=True)  # Add replace=True to ensure correct prefix
        self.graph.bind("rec", self.rec, override=True, replace=True)  # Bind REC namespace
        self.graph.bind("unit", self.unit, override=True, replace=True)
        self.graph.bind("owl", self.owl, override=True, replace=True)
        self.graph.bind("ref", self.ref, override=True, replace=True)  # Bind ref namespace
        self.graph.bind("rdf", RDF, override=True, replace=True)
        self.graph.bind("rdfs", RDFS, override=True, replace=True)
        self.graph.bind("xsd", XSD, override=True, replace=True)  # Add xsd binding

    def _safe_float_convert(self, value) -> Optional[float]:
        """Safely convert value to float, handling NA values with spaces."""
        if pd.isna(value):
            return None

        # Handle string values that might contain spaces or 'NA'
        if isinstance(value, str):
            value = value.strip()
            if value.upper() == 'NA' or value == '' or value.upper() == 'NULL':
                return None

        try:
            return float(value)
        except (ValueError, TypeError):
            self.logger.warning(f"Could not convert '{value}' to float, returning None")
            return None

    def _safe_int_convert(self, value) -> Optional[int]:
        """Safely convert value to int, handling NA values with spaces."""
        if pd.isna(value):
            return None

        # Handle string values that might contain spaces or 'NA'
        if isinstance(value, str):
            value = value.strip()
            if value.upper() == 'NA' or value == '' or value.upper() == 'NULL':
                return None

        try:
            return int(float(value))  # Convert via float first to handle decimal strings
        except (ValueError, TypeError):
            self.logger.warning(f"Could not convert '{value}' to int, returning None")
            return None

    def convert_to_brick(self,
                        metadata_csv: str,
                        vars_csv: str,
                        system_type: Optional[str] = None,
                        building_tag: Optional[str] = None,
                        sensor_mapping: Optional[str] = None,
                        output_path: str = "output.ttl") -> Graph:
        """
        Convert CSV data to Brick format for specified system type.

        Args:
            metadata_csv: Path to metadata.csv file
            vars_csv: Path to vars_available_by_building.csv file
            system_type: System type filter (e.g., 'Boiler', 'Condensing', 'Non-condensing', 'District HW', 'District Steam')
                        If None, auto-detects from metadata (recommended for single building conversion)
            building_tag: Specific building tag to process (optional)
            sensor_mapping: Path to sensor mapping file (uses default if None)
            output_path: Output TTL file path

        Returns:
            RDF Graph with Brick model
        """
        try:
            # Use default sensor mapping if none provided
            if sensor_mapping is None:
                sensor_mapping = self._get_default_sensor_mapping_path()

            # Load sensor mappings
            mappings = self._load_sensor_mappings(sensor_mapping)

            # Load data
            metadata_df = pd.read_csv(metadata_csv)
            vars_df = pd.read_csv(vars_csv)

            # Filter for specific building tag if provided
            if building_tag:
                metadata_df = metadata_df[metadata_df['tag'].astype(str) == str(building_tag)]
                vars_df = vars_df[vars_df['tag'].astype(str) == str(building_tag)]
                self.logger.info(f"Filtering for building tag: {building_tag}")

            if metadata_df.empty:
                raise ValueError(f"No data found for building tag: {building_tag}")

            # Auto-detect system type if not provided (useful for single building)
            if system_type is None and len(metadata_df) == 1:
                system_type = str(metadata_df.iloc[0].get('system', '')).strip()
                self.logger.info(f"Auto-detected system type: {system_type}")
            elif system_type is None:
                # For multiple buildings without system_type, process all
                system_type = ""  # Empty string matches all
                self.logger.info(f"Processing all system types")

            self.logger.info(f"Starting conversion for system type: {system_type}")

            # Add ontology declaration with Brick 1.3 import
            self._add_ontology_declaration()

            # Process buildings
            for _, building_row in metadata_df.iterrows():
                tag = str(int(building_row['tag']))
                building_system_type = str(building_row.get('system', '')).strip()

                # Check if system type matches (empty system_type matches all)
                if not system_type or self._matches_system_type(building_system_type, system_type):
                    self.logger.info(f"Processing building {tag} with system type: {building_system_type}")

                    # Find corresponding vars data
                    building_vars = vars_df[vars_df['tag'] == int(tag)]
                    if not building_vars.empty:
                        # Route to appropriate system creation method
                        if system_type.lower() in ['boiler', 'condensing', 'non-condensing']:
                            self._create_boiler_system(tag, building_row, building_vars.iloc[0], mappings, building_system_type.lower())
                        elif system_type.lower() == 'district hw':
                            self._create_district_hw_system(tag, building_row, building_vars.iloc[0], mappings)
                        elif system_type.lower() == 'district steam':
                            self._create_district_steam_system(tag, building_row, building_vars.iloc[0], mappings)
                    else:
                        self.logger.warning(f"No vars data found for building {tag}")
                else:
                    self.logger.info(f"Skipping building {tag} - system type mismatch")

            # Save to file with custom serialization including ontology declaration
            self._serialize_with_ontology(output_path)
            self.logger.info(f"✅ Conversion completed. Output saved to: {output_path}")
            self.logger.info(f"📊 Generated {len(self.graph)} RDF triples")

            # Output and save validation warnings
            if self.validation_warnings:
                self.logger.warning(f"\n⚠️  Found {len(self.validation_warnings)} issues that need manual verification:")
                for i, warning in enumerate(self.validation_warnings, 1):
                    self.logger.warning(f"  {i}. {warning}")

                # Save warnings to file
                warnings_file = output_path.replace('.ttl', '_validation_warnings.txt')
                self._save_validation_warnings(warnings_file)
                self.logger.info(f"📋 Validation warnings saved to: {warnings_file}")
            else:
                self.logger.info("✓ No issues found that need manual verification")

            return self.graph

        except Exception as e:
            self.logger.error(f"Conversion failed: {e}")
            raise

    def _add_ontology_declaration(self):
        """Add ontology declaration and Brick 1.3 import to the graph."""
        # Add custom Brick class declarations
        self._add_custom_brick_classes()

    def _add_custom_brick_classes(self):
        """Add custom Brick class definitions that don't exist in standard Brick schema."""
        firing_rate_sensor = self.brick.Firing_Rate_Sensor
        self.graph.add((firing_rate_sensor, RDF.type, self.owl.Class))
        self.graph.add((firing_rate_sensor, RDFS.subClassOf, self.brick.Point))
        self.graph.add((firing_rate_sensor, RDFS.label, Literal("Firing Rate Sensor")))
        self.graph.add((firing_rate_sensor, RDFS.comment,
                       Literal("A sensor that measures the firing rate of a boiler or similar combustion equipment, typically expressed as a percentage of maximum capacity.")))

    def _matches_system_type(self, building_system: str, target_type: str) -> bool:
        """Check if building system matches target system type."""
        target = target_type.lower().strip()
        building = building_system.lower().strip()

        if target == 'boiler':
            return building in ['boiler', 'condensing', 'non-condensing']
        elif target == 'condensing':
            return building == 'condensing'
        elif target == 'non-condensing':
            return building == 'non-condensing'
        elif target == 'district hw':
            return building == 'district hw'
        elif target == 'district steam':
            return building == 'district steam'
        else:
            return building == target

    def _analyze_equipment_count(self, vars_data: pd.Series, metadata: pd.Series,
                                 building_tag: str, system_type: str) -> Dict[str, List[int]]:
        """
        Analyze equipment count and numbering based on b_number in metadata and vars availability data

        Args:
            vars_data: Sensor availability data
            metadata: Building metadata (including b_number)
            building_tag: Building tag
            system_type: System type

        Returns:
            Dict containing available number lists for each equipment type
        """
        equipment_count = {
            'boilers': [],
            'pumps': []
        }

        # Get b_number from metadata
        b_number = self._safe_int_convert(metadata.get('b_number'))

        # Infer boiler count from sensor data (through sup1-4, ret1-4, fire1-4, etc. sensors)
        max_boiler_from_sensors = 0
        for i in range(1, 10):  # Check boiler 1-9 (extended range to support more boilers)
            boiler_sensors = [f'sup{i}', f'ret{i}', f'fire{i}']
            # If any boiler-specific sensor is available, update the maximum number
            if any(vars_data.get(sensor, 0) == 1 for sensor in boiler_sensors):
                max_boiler_from_sensors = max(max_boiler_from_sensors, i)

        # Determine if it's a boiler system type
        is_boiler_system = system_type.lower() in ['boiler', 'condensing', 'non-condensing']
        is_district_system = system_type.lower() in ['district hw', 'district steam']

        # Determine final boiler count
        if is_boiler_system:
            # For boiler systems, take the maximum of b_number and sensor-inferred count
            if b_number is not None and b_number > 0:
                final_boiler_count = max(b_number, max_boiler_from_sensors)
                if final_boiler_count > b_number:
                    self.logger.warning(
                        f"Building {building_tag}: b_number={b_number}, but sensor data shows {max_boiler_from_sensors} boilers, "
                        f"using maximum value {final_boiler_count}"
                    )
            elif b_number == 0:
                # b_number is 0 but it's a boiler system - need to log warning
                warning_msg = f"Building {building_tag}: Boiler system type ({system_type}) but b_number=0"
                if max_boiler_from_sensors > 0:
                    warning_msg += f", sensor data shows {max_boiler_from_sensors} boilers, using sensor-inferred value"
                    final_boiler_count = max_boiler_from_sensors
                else:
                    warning_msg += ", sensor data also shows no boilers, needs manual verification"
                    final_boiler_count = 0
                self.logger.warning(warning_msg)
                self.validation_warnings.append(warning_msg)
            else:
                # b_number is None, use sensor inference
                final_boiler_count = max_boiler_from_sensors
                if final_boiler_count == 0:
                    # Check if there are unnumbered boiler sensors
                    boiler_related_sensors = ['sup', 'ret', 'fire', 'supp', 'retp']
                    if any(vars_data.get(sensor, 0) == 1 for sensor in boiler_related_sensors):
                        final_boiler_count = 1
                        self.logger.info(f"Building {building_tag}: Detected unnumbered boiler-related sensors, inferring single boiler exists")

            # Generate boiler number list
            equipment_count['boilers'] = list(range(1, final_boiler_count + 1)) if final_boiler_count > 0 else []

        elif is_district_system:
            # For District systems, there should be no boilers
            if max_boiler_from_sensors > 0 or (b_number is not None and b_number > 0):
                warning_msg = (
                    f"Building {building_tag}: District system ({system_type}) but found boiler-related data - "
                    f"b_number={b_number}, sensors show {max_boiler_from_sensors} boilers, not modeling boilers, needs manual verification"
                )
                self.logger.warning(warning_msg)
                self.validation_warnings.append(warning_msg)
            # District systems don't model boilers
            equipment_count['boilers'] = []

        # Check pump count (inferred through pmp1_pwr, pmp1_spd, pmp1_vfd, etc. sensors)
        max_pump_from_sensors = 0
        for i in range(1, 10):  # Check pump 1-9
            pump_sensors = [f'pmp{i}_pwr', f'pmp{i}_spd', f'pmp{i}_vfd']
            # If any pump-specific sensor is available, update the maximum number
            if any(vars_data.get(sensor, 0) == 1 for sensor in pump_sensors):
                max_pump_from_sensors = max(max_pump_from_sensors, i)

        # Check if there's a generic pump sensor (pmp_spd, without numbering)
        has_generic_pump_sensor = vars_data.get('pmp_spd', 0) == 1

        # Decide final pump count: take the maximum of generic pump sensor implied count (1) and numbered pump sensors
        if max_pump_from_sensors > 0:
            # Has numbered pump sensors, generate all pumps from 1 to max
            equipment_count['pumps'] = list(range(1, max_pump_from_sensors + 1))
            if has_generic_pump_sensor:
                self.logger.info(f"Building {building_tag}: Detected generic pump sensor (pmp_spd) and {max_pump_from_sensors} numbered pump sensors, "
                               f"generating {max_pump_from_sensors} pumps, pmp_spd will be connected to all pumps")
        elif has_generic_pump_sensor:
            # Only generic pump sensor, default to 1 pump
            equipment_count['pumps'] = [1]
            self.logger.info(f"Building {building_tag}: Only detected generic pump sensor (pmp_spd), inferring single pump exists (pump1)")


        self.logger.info(
            f"Building {building_tag} equipment count inference result: "
            f"Boilers {equipment_count['boilers']}, Pumps {equipment_count['pumps']}"
        )
        return equipment_count

    def _create_boiler_system(self, building_tag: str, metadata: pd.Series,
                            vars_data: pd.Series, mappings: Dict, system_type: str) -> None:
        """Create Boiler system with Primary and Secondary loop structure."""

        # Analyze equipment count
        equipment_count = self._analyze_equipment_count(vars_data, metadata, building_tag, system_type)

        # Create building entity with hierarchical naming
        building_uri = self._create_building(building_tag, metadata)

        # Create Hot Water System
        system_uri = self.hhws[f"building{building_tag}.hws"]
        self.graph.add((system_uri, RDF.type, self.brick.Hot_Water_System))
        self.graph.add((system_uri, RDFS.label,
                      Literal(f"Hot Water System - Building {building_tag}")))
        self.graph.add((building_uri, self.rec.isLocationOf, system_uri))

        # Create Primary Loop (Hot_Water_Loop)
        primary_loop_uri = self.hhws[f"building{building_tag}.hws.primary_loop"]
        self.graph.add((primary_loop_uri, RDF.type, self.brick.Hot_Water_Loop))
        self.graph.add((primary_loop_uri, RDFS.label,
                      Literal(f"Primary Hot Water Loop - Building {building_tag}")))
        self.graph.add((system_uri, self.brick.hasPart, primary_loop_uri))

        # Create Secondary Loop (Hot_Water_Loop)
        secondary_loop_uri = self.hhws[f"building{building_tag}.hws.secondary_loop"]
        self.graph.add((secondary_loop_uri, RDF.type, self.brick.Hot_Water_Loop))
        self.graph.add((secondary_loop_uri, RDFS.label,
                      Literal(f"Secondary Hot Water Loop - Building {building_tag}")))
        self.graph.add((system_uri, self.brick.hasPart, secondary_loop_uri))

        # Create multiple boilers in Primary Loop
        boiler_uris = {}
        for boiler_num in equipment_count['boilers']:
            boiler_uri = self.hhws[f"building{building_tag}.boiler{boiler_num}"]
            boiler_uris[boiler_num] = boiler_uri

            # Determine boiler Brick class based on system type
            if system_type == 'condensing':
                boiler_class = self.brick.Condensing_Natural_Gas_Boiler
                boiler_label = f"Condensing Natural Gas Boiler {boiler_num} - Building {building_tag}"
            elif system_type == 'non-condensing':
                boiler_class = self.brick.Noncondensing_Natural_Gas_Boiler
                boiler_label = f"Non-condensing Natural Gas Boiler {boiler_num} - Building {building_tag}"
            else:  # 'boiler' or default
                boiler_class = self.brick.Natural_Gas_Boiler
                boiler_label = f"Natural Gas Boiler {boiler_num} - Building {building_tag}"

            self.graph.add((boiler_uri, RDF.type, boiler_class))
            self.graph.add((boiler_uri, RDFS.label, Literal(boiler_label)))
             # Boiler is part of Primary Loop
            self.graph.add((primary_loop_uri, self.brick.hasPart, boiler_uri))

            # Add boiler properties
            if not pd.isna(metadata.get('b_manufacturer')):
                self.graph.add((boiler_uri, self.hhws.hasManufacturer,
                              Literal(str(metadata['b_manufacturer']))))

            if not pd.isna(metadata.get('b_model')):
                self.graph.add((boiler_uri, self.hhws.hasModel,
                              Literal(str(metadata['b_model']))))

            # Add boiler technical specifications - use safe conversion
            b_input = self._safe_float_convert(metadata.get('b_input'))
            if b_input is not None:
                self.graph.add((boiler_uri, self.hhws.hasNominalInputPower,
                              Literal(b_input, datatype=XSD.float)))

            b_output = self._safe_float_convert(metadata.get('b_output'))
            if b_output is not None:
                self.graph.add((boiler_uri, self.hhws.hasNominalOutputPower,
                              Literal(b_output, datatype=XSD.float)))

            b_efficiency = self._safe_float_convert(metadata.get('b_efficiency'))
            if b_efficiency is not None:
                self.graph.add((boiler_uri, self.hhws.hasNominalEfficiency,
                              Literal(b_efficiency, datatype=XSD.float)))

            b_min_turndown = self._safe_float_convert(metadata.get('b_min_turndown'))
            if b_min_turndown is not None:
                self.graph.add((boiler_uri, self.hhws.hasMinimumTurndown,
                              Literal(b_min_turndown, datatype=XSD.float)))

            b_min_flow = self._safe_float_convert(metadata.get('b_min_flow'))
            if b_min_flow is not None:
                self.graph.add((boiler_uri, self.hhws.hasMinimumFlowRequirement,
                              Literal(b_min_flow, datatype=XSD.float)))

            b_redundancy = self._safe_float_convert(metadata.get('b_redundancy'))
            if b_redundancy is not None:
                self.graph.add((boiler_uri, self.hhws.hasRedundancyLevel,
                              Literal(b_redundancy, datatype=XSD.float)))

        # Add system-level boiler information - use safe conversion
        b_number = self._safe_int_convert(metadata.get('b_number'))
        if b_number is not None:
            self.graph.add((system_uri, self.hhws.hasBoilerCount,
                          Literal(b_number, datatype=XSD.integer)))

        # Create pumps in Primary Loop (always only 1 pump in primary loop)
        # Primary loop pump has no sensor points, it's just structural
        primary_pump_uris = {}
        pump_uri = self.hhws[f"building{building_tag}.primary_pump1"]
        pump_label = f"Primary Circulation Pump 1 - Building {building_tag}"
        primary_pump_uris[1] = pump_uri

        self.graph.add((pump_uri, RDF.type, self.brick.Pump))
        self.graph.add((pump_uri, RDFS.label, Literal(pump_label)))
        # Pump placed in Primary Loop
        self.graph.add((primary_loop_uri, self.brick.hasPart, pump_uri))


        # Create pumps in Secondary Loop
        # Pump variables (pmp1_spd, pmp2_spd, etc.) represent secondary loop pumps
        # If no pump variables, still create at least 1 pump
        secondary_pump_uris = {}
        pump_list = equipment_count['pumps'] if equipment_count['pumps'] else [1]

        for pump_num in pump_list:
            pump_uri = self.hhws[f"building{building_tag}.secondary_pump{pump_num}"]
            pump_label = f"Secondary Circulation Pump {pump_num} - Building {building_tag}"
            secondary_pump_uris[pump_num] = pump_uri

            self.graph.add((pump_uri, RDF.type, self.brick.Pump))
            self.graph.add((pump_uri, RDFS.label, Literal(pump_label)))
            # Pump is part of Secondary Loop
            self.graph.add((secondary_loop_uri, self.brick.hasPart, pump_uri))

        # Add feeds relationships for Primary Loop: Boiler → Pump
        for boiler_uri in boiler_uris.values():
            # Boiler feeds all primary pumps
            for pump_uri in primary_pump_uris.values():
                self.graph.add((boiler_uri, self.brick.feeds, pump_uri))


        # Primary_Loop → Secondary_Loop
        self.graph.add((primary_loop_uri, self.brick.feeds, secondary_loop_uri))

        # Create sensor points
        equipment_uris = {
            'hot_water_system': system_uri,
            'primary_loop': primary_loop_uri,
            'secondary_loop': secondary_loop_uri,
            'boiler_uris': boiler_uris,
            'primary_pump_uris': primary_pump_uris,
            'secondary_pump_uris': secondary_pump_uris,
            'pump_uris': secondary_pump_uris,  # Default pump sensors connect to secondary pumps
            'equipment_count': equipment_count
        }

        self._create_sensor_points(building_tag, vars_data, mappings, equipment_uris)

    def _create_district_hw_system(self, building_tag: str, metadata: pd.Series,
                                  vars_data: pd.Series, mappings: Dict) -> None:
        """Create District Hot Water system with only Secondary loop (no boiler, no primary loop in building)."""

        # District HW systems have no boiler or primary loop in the building, only secondary loop with pumps and heat exchangers
        equipment_count = self._analyze_equipment_count(vars_data, metadata, building_tag, 'district hw')

        # Create building entity
        building_uri = self._create_building(building_tag, metadata)

        # Create Hot Water System (no boiler in building for District HW)
        system_uri = self.hhws[f"building{building_tag}.hws"]
        self.graph.add((system_uri, RDF.type, self.brick.Hot_Water_System))
        self.graph.add((system_uri, RDFS.label,
                      Literal(f"District Hot Water System - Building {building_tag}")))
        self.graph.add((building_uri, self.rec.isLocationOf, system_uri))

        # Create only Secondary Loop (no Primary Loop for District systems)
        secondary_loop_uri = self.hhws[f"building{building_tag}.hws.secondary_loop"]
        self.graph.add((secondary_loop_uri, RDF.type, self.brick.Hot_Water_Loop))
        self.graph.add((secondary_loop_uri, RDFS.label,
                      Literal(f"Hot Water Loop - Building {building_tag}")))
        self.graph.add((system_uri, self.brick.hasPart, secondary_loop_uri))

        # Ensure at least one pump exists
        pump_list = equipment_count['pumps'] if equipment_count['pumps'] else [1]

        # Create pumps in Secondary Loop
        pump_uris = {}
        for pump_num in pump_list:
            pump_uri = self.hhws[f"building{building_tag}.pump{pump_num}"]
            pump_label = f"Circulation Pump {pump_num} - Building {building_tag}"
            pump_uris[pump_num] = pump_uri

            self.graph.add((pump_uri, RDF.type, self.brick.Pump))
            self.graph.add((pump_uri, RDFS.label, Literal(pump_label)))
            self.graph.add((secondary_loop_uri, self.brick.hasPart, pump_uri))

        # Create sensor points
        equipment_uris = {
            'hot_water_system': system_uri,
            'secondary_loop': secondary_loop_uri,
            'boiler_uris': {},  # No boilers in District HW
            'pump_uris': pump_uris,
            'equipment_count': equipment_count
        }

        self._create_sensor_points(building_tag, vars_data, mappings, equipment_uris)

    def _create_district_steam_system(self, building_tag: str, metadata: pd.Series,
                                     vars_data: pd.Series, mappings: Dict) -> None:
        """Create District Steam system with only Secondary loop (no boiler, no primary loop in building, steam to HW heat exchanger)."""

        equipment_count = self._analyze_equipment_count(vars_data, metadata, building_tag, 'district steam')

        # Create building entity
        building_uri = self._create_building(building_tag, metadata)

        # Create Hot Water System (no boiler in building for District Steam)
        system_uri = self.hhws[f"building{building_tag}.hws"]
        self.graph.add((system_uri, RDF.type, self.brick.Hot_Water_System))
        self.graph.add((system_uri, RDFS.label,
                      Literal(f"District Steam to Hot Water System - Building {building_tag}")))
        self.graph.add((building_uri, self.rec.isLocationOf, system_uri))

        # Create only Secondary Loop (no Primary Loop for District systems)
        secondary_loop_uri = self.hhws[f"building{building_tag}.hws.secondary_loop"]
        self.graph.add((secondary_loop_uri, RDF.type, self.brick.Hot_Water_Loop))
        self.graph.add((secondary_loop_uri, RDFS.label,
                      Literal(f"Hot Water Loop - Building {building_tag}")))
        self.graph.add((system_uri, self.brick.hasPart, secondary_loop_uri))

        # Ensure at least one pump exists
        pump_list = equipment_count['pumps'] if equipment_count['pumps'] else [1]

        # Create pumps in Secondary Loop
        pump_uris = {}
        for pump_num in pump_list:
            pump_uri = self.hhws[f"building{building_tag}.pump{pump_num}"]
            pump_label = f"Circulation Pump {pump_num} - Building {building_tag}"
            pump_uris[pump_num] = pump_uri

            self.graph.add((pump_uri, RDF.type, self.brick.Pump))
            self.graph.add((pump_uri, RDFS.label, Literal(pump_label)))
            self.graph.add((secondary_loop_uri, self.brick.hasPart, pump_uri))

        # Create sensor points
        equipment_uris = {
            'hot_water_system': system_uri,
            'secondary_loop': secondary_loop_uri,
            'boiler_uris': {},  # No boilers in District Steam
            'pump_uris': pump_uris,
            'equipment_count': equipment_count
        }

        self._create_sensor_points(building_tag, vars_data, mappings, equipment_uris)

    def _create_sensor_points(self, building_tag: str, vars_data: pd.Series,
                            mappings: Dict, equipment_uris: Dict[str, URIRef]) -> None:
        """Create sensor points based on vars availability data with proper hierarchical naming."""

        # Skip first 3 columns (tag, org, datetime)
        sensor_columns = vars_data.index[3:]

        sensors_created = 0
        for sensor_name in sensor_columns:
            # Check if sensor is available (value = 1)
            if vars_data[sensor_name] == 1:
                sensor_info = mappings.get(sensor_name)
                if sensor_info:
                    self._create_individual_sensor(building_tag, sensor_name,
                                                 sensor_info, equipment_uris)
                    sensors_created += 1
                else:
                    self.logger.warning(f"No mapping found for sensor: {sensor_name}")

        self.logger.info(f"Created {sensors_created} sensor points for building {building_tag}")

    def _create_individual_sensor(self, building_tag: str, sensor_name: str,
                                sensor_info: Dict, equipment_uris: Dict[str, Any]) -> None:
        """Create individual sensor point with proper hierarchical naming based on equipment and device number."""

        # Determine equipment from mapping - mapping file is the source of truth
        equipment_type = sensor_info.get('equipment', 'hot_water_system')

        # Parse sensor number (e.g., sup1, ret1, pmp1_pwr, etc.)
        device_number = None
        base_sensor_name = sensor_name

        # Extract device number
        import re
        if equipment_type == 'boiler':
            # Match boiler-related sensor numbers (sup1, ret1, fire1, etc.)
            match = re.search(r'(sup|ret|fire)(\d+)', sensor_name)
            if match:
                device_number = int(match.group(2))
                base_sensor_name = match.group(1) + match.group(2)
        elif equipment_type == 'pump':
            # Match pump-related sensor numbers (pmp1_pwr, pmp2_spd, etc.)
            match = re.search(r'pmp(\d+)_', sensor_name)
            if match:
                device_number = int(match.group(1))
            else:
                # Generic pump sensor (pmp_spd, etc.) - connect to all pumps
                available_pumps = list(equipment_uris.get('pump_uris', {}).keys())
                if len(available_pumps) > 0:
                    # If there are multiple pumps, connect generic sensor to all pumps
                    device_number = 'all'  # Special marker indicating connection to all pumps
                    self.logger.info(f"Generic pump sensor {sensor_name} will connect to all {len(available_pumps)} pumps")
                else:
                    self.logger.warning(f"No pumps found for sensor {sensor_name}, will assign to secondary loop")
                    equipment_type = 'secondary_loop'

        # Create hierarchical sensor URI based on equipment and device number
        if equipment_type == 'boiler' and device_number is not None:
            # Ensure boiler with this number exists
            if device_number in equipment_uris['boiler_uris']:
                sensor_uri = self.hhws[f"building{building_tag}.boiler{device_number}.{sensor_name}"]
                target_equipment_uri = equipment_uris['boiler_uris'][device_number]
            else:
                self.logger.warning(f"Boiler {device_number} not found for sensor {sensor_name}, assigning to secondary loop")
                sensor_uri = self.hhws[f"building{building_tag}.hws.secondary_loop.{sensor_name}"]
                target_equipment_uri = equipment_uris.get('secondary_loop', equipment_uris['hot_water_system'])

        elif equipment_type == 'pump' and device_number is not None:
            # If generic pump sensor needs to connect to all pumps
            if device_number == 'all':
                # Create sensor instance for each pump
                pump_sensor_uris = []
                for pump_num in equipment_uris.get('pump_uris', {}).keys():
                    pump_sensor_uri = self.hhws[f"building{building_tag}.secondary_pump{pump_num}.{sensor_name}"]
                    pump_sensor_uris.append(pump_sensor_uri)
                    target_pump_uri = equipment_uris['pump_uris'][pump_num]

                    # Get Brick class
                    brick_class_name = sensor_info['brick_class'].replace('brick:', '')
                    brick_class = getattr(self.brick, brick_class_name, self.brick.Point)

                    # Add sensor to graph
                    self.graph.add((pump_sensor_uri, RDF.type, brick_class))
                    self.graph.add((pump_sensor_uri, RDFS.label,
                                  Literal(f"{sensor_info['description']} - Pump {pump_num} - Building {building_tag}")))

                    # Add unit information
                    if sensor_info.get('unit'):
                        unit_uri = self.unit[sensor_info['unit']]
                        self.graph.add((pump_sensor_uri, self.brick.hasUnit, unit_uri))

                    # Add TimeseriesReference
                    self._add_timeseries_reference(pump_sensor_uri, building_tag, sensor_name)

                    # Link to pump with hasPoint
                    self.graph.add((target_pump_uri, self.brick.hasPoint, pump_sensor_uri))

                # Add owl:sameAs relationships between all pump sensor instances
                # This indicates they are the same physical command/sensor
                if len(pump_sensor_uris) > 1:
                    for i in range(len(pump_sensor_uris) - 1):
                        self.graph.add((pump_sensor_uris[i], self.owl.sameAs, pump_sensor_uris[i + 1]))
                    self.logger.info(f"Added owl:sameAs relationships for {len(pump_sensor_uris)} instances of {sensor_name}")

                self.logger.info(f"Created {len(equipment_uris.get('pump_uris', {}))} instances of {sensor_name} for all pumps")
                return  # Processing complete, return directly

            # Ensure pump with this number exists
            if device_number in equipment_uris['pump_uris']:
                sensor_uri = self.hhws[f"building{building_tag}.secondary_pump{device_number}.{sensor_name}"]
                target_equipment_uri = equipment_uris['pump_uris'][device_number]
            else:
                self.logger.warning(f"Pump {device_number} not found for sensor {sensor_name}, assigning to secondary loop")
                sensor_uri = self.hhws[f"building{building_tag}.hws.secondary_loop.{sensor_name}"]
                target_equipment_uri = equipment_uris.get('secondary_loop', equipment_uris['hot_water_system'])


        elif equipment_type == 'primary_loop':
            # Sensor assigned to Primary Loop
            sensor_uri = self.hhws[f"building{building_tag}.hws.primary_loop.{sensor_name}"]
            target_equipment_uri = equipment_uris['primary_loop']

        elif equipment_type == 'secondary_loop':
            # Sensor assigned to Secondary Loop
            sensor_uri = self.hhws[f"building{building_tag}.hws.secondary_loop.{sensor_name}"]
            target_equipment_uri = equipment_uris['secondary_loop']

        elif equipment_type == 'weather_station':
            # Create weather station if it doesn't exist yet
            if 'weather_station' not in equipment_uris:
                # Get building metadata to create weather station
                building_uri = self.hhws[f"building{building_tag}"]
                weather_station_uri = self.hhws[f"building{building_tag}.weather_station"]

                # Add weather station to graph if not already present
                if (weather_station_uri, RDF.type, self.brick.Weather_Station) not in self.graph:
                    self.graph.add((weather_station_uri, RDF.type, self.brick.Weather_Station))
                    self.graph.add((weather_station_uri, RDFS.label,
                                  Literal(f"Weather Station - Building {building_tag}")))
                    # Weather station previously added as hasPart of building; change to isLocationOf
                    # self.graph.add((building_uri, self.brick.hasPart, weather_station_uri))  # old
                    self.graph.add((building_uri, self.rec.isLocationOf, weather_station_uri))

                equipment_uris['weather_station'] = weather_station_uri

            sensor_uri = self.hhws[f"building{building_tag}.weather_station.{sensor_name}"]
            target_equipment_uri = equipment_uris['weather_station']

        elif equipment_type == 'hot_water_system':
            # Sensor assigned to Hot Water System (e.g., system-level commands and status like enab, oper)
            sensor_uri = self.hhws[f"building{building_tag}.hws.{sensor_name}"]
            target_equipment_uri = equipment_uris['hot_water_system']

        else:  # unknown equipment type
            # For unknown types, if secondary_loop exists, default to assigning to secondary_loop
            if equipment_uris.get('secondary_loop'):
                sensor_uri = self.hhws[f"building{building_tag}.hws.secondary_loop.{sensor_name}"]
                target_equipment_uri = equipment_uris['secondary_loop']
            else:
                sensor_uri = self.hhws[f"building{building_tag}.hws.{sensor_name}"]
                target_equipment_uri = equipment_uris['hot_water_system']
                target_equipment_uri = equipment_uris['hot_water_system']

        # Get Brick class
        brick_class_name = sensor_info['brick_class'].replace('brick:', '')
        brick_class = getattr(self.brick, brick_class_name, self.brick.Point)

        # Add sensor to graph
        self.graph.add((sensor_uri, RDF.type, brick_class))
        self.graph.add((sensor_uri, RDFS.label,
                      Literal(f"{sensor_info['description']} - Building {building_tag}")))

        # Add unit information
        if sensor_info.get('unit'):
            unit_uri = self.unit[sensor_info['unit']]
            self.graph.add((sensor_uri, self.brick.hasUnit, unit_uri))

        # Add TimeseriesReference for sensor data
        self._add_timeseries_reference(sensor_uri, building_tag, sensor_name)

        # Link to appropriate equipment with correct relationship
        # Equipment (boiler, pump, weather_station) uses hasPoint for sensors
        # Systems and Loops (hot_water_system, primary_loop, secondary_loop) use hasPart for sensors
        if target_equipment_uri in [equipment_uris['hot_water_system'],
                                     equipment_uris.get('primary_loop'),
                                     equipment_uris.get('secondary_loop')]:
            # System and Loops use hasPart for sensors
            self.graph.add((target_equipment_uri, self.brick.hasPart, sensor_uri))
        else:
            # Equipment (boiler, pump, weather_station) uses hasPoint for sensors
            self.graph.add((target_equipment_uri, self.brick.hasPoint, sensor_uri))


    def get_graph(self) -> Graph:
        """Return the RDF graph."""
        return self.graph

    def clear_graph(self) -> None:
        """Clear the current graph."""
        self.graph = Graph()
        self.validation_warnings = []  # Clear validation warnings
        # Re-bind namespaces with proper override settings
        self.graph.bind("brick", self.brick, override=True, replace=True)
        self.graph.bind("hhws", self.hhws, override=True, replace=True)
        self.graph.bind("unit", self.unit, override=True, replace=True)
        self.graph.bind("owl", self.owl, override=True, replace=True)
        self.graph.bind("ref", self.ref, override=True, replace=True)  # Add ref namespace binding
        self.graph.bind("rdf", RDF, override=True, replace=True)
        self.graph.bind("rdfs", RDFS, override=True, replace=True)

    def _create_building(self, building_tag: str, metadata: pd.Series) -> URIRef:
        """Create building entity with all metadata properties."""
        building_uri = self.hhws[f"building{building_tag}"]

        # Add building to graph - using REC namespace for Building class type
        self.graph.add((building_uri, RDF.type, self.rec.Building))
        self.graph.add((building_uri, RDFS.label, Literal(f"Building {building_tag}")))

        # Add all metadata properties - use safe conversion for numeric fields
        # Basic building properties
        area = self._safe_float_convert(metadata.get('area'))
        if area is not None:
            self.graph.add((building_uri, self.hhws.hasArea,
                          Literal(area, datatype=XSD.float)))

        if not pd.isna(metadata.get('bldg_type')):
            self.graph.add((building_uri, self.hhws.hasBuildingType,
                          Literal(str(metadata['bldg_type']))))

        if not pd.isna(metadata.get('bldg_type_hl')):
            self.graph.add((building_uri, self.hhws.hasHighLevelBuildingType,
                          Literal(str(metadata['bldg_type_hl']))))

        # Construction and time properties - use safe conversion
        year = self._safe_int_convert(metadata.get('year'))
        if year is not None:
            self.graph.add((building_uri, self.hhws.hasConstructionYear,
                          Literal(year, datatype=XSD.integer)))

        decade = self._safe_int_convert(metadata.get('decade'))
        if decade is not None:
            self.graph.add((building_uri, self.hhws.hasConstructionDecade,
                          Literal(decade, datatype=XSD.integer)))

        # Climate and environmental properties
        if not pd.isna(metadata.get('climate')):
            self.graph.add((building_uri, self.hhws.hasClimateZone,
                          Literal(str(metadata['climate']))))

        t_hdd = self._safe_float_convert(metadata.get('t_hdd'))
        if t_hdd is not None:
            self.graph.add((building_uri, self.hhws.hasHeatingDesignTemperature,
                          Literal(t_hdd, datatype=XSD.float)))

        # System properties
        if not pd.isna(metadata.get('system')):
            self.graph.add((building_uri, self.hhws.hasSystemType,
                          Literal(str(metadata['system']))))

        if not pd.isna(metadata.get('system_hl')):
            self.graph.add((building_uri, self.hhws.hasHighLevelSystemType,
                          Literal(str(metadata['system_hl']))))

        # Design parameters - use safe conversion
        design_supply = self._safe_float_convert(metadata.get('design_supply'))
        if design_supply is not None:
            self.graph.add((building_uri, self.hhws.hasDesignSupplyTemperature,
                          Literal(design_supply, datatype=XSD.float)))

        design_return = self._safe_float_convert(metadata.get('design_return'))
        if design_return is not None:
            self.graph.add((building_uri, self.hhws.hasDesignReturnTemperature,
                          Literal(design_return, datatype=XSD.float)))

        # Organization property
        if not pd.isna(metadata.get('org')):
            self.graph.add((building_uri, self.hhws.belongsToOrganization,
                          Literal(str(metadata['org']))))

        # Note: Weather Station will be created dynamically in sensor creation
        # if weather sensors are available (handled in _create_individual_sensor)

        return building_uri

    def _create_weather_station(self, building_tag: str, metadata: pd.Series) -> URIRef:
        """Create Weather Station entity for the building."""
        weather_station_uri = self.hhws[f"building{building_tag}.weather_station"]

        # Add weather station to graph
        self.graph.add((weather_station_uri, RDF.type, self.brick.Weather_Station))
        self.graph.add((weather_station_uri, RDFS.label,
                      Literal(f"Weather Station - Building {building_tag}")))

        # Add climate zone information to weather station
        if not pd.isna(metadata.get('climate')):
            self.graph.add((weather_station_uri, self.hhws.locatedInClimateZone,
                          Literal(str(metadata['climate']))))

        # Add heating design temperature as a property of the weather station - use safe conversion
        t_hdd = self._safe_float_convert(metadata.get('t_hdd'))
        if t_hdd is not None:
            self.graph.add((weather_station_uri, self.hhws.hasHeatingDesignTemperature,
                          Literal(t_hdd, datatype=XSD.float)))

        return weather_station_uri

    def _get_default_sensor_mapping_path(self) -> str:
        """Get the default sensor mapping file path from the package."""
        package_dir = Path(__file__).parent
        return str(package_dir / "sensor_to_brick_mapping.yaml")

    def _load_sensor_mappings(self, mapping_file_path: str) -> Dict:
        """Load sensor to Brick mappings from YAML file."""
        try:
            with open(mapping_file_path, 'r', encoding='utf-8') as f:
                mappings = yaml.safe_load(f)
            self.logger.info(f"Loaded {len(mappings)} sensor mappings from {mapping_file_path}")
            return mappings
        except Exception as e:
            self.logger.error(f"Failed to load sensor mappings: {e}")
            raise

    def _serialize_with_ontology(self, output_path: str):
        """Serialize graph with proper ontology header."""

        # Create a complete graph that includes both ontology and main content
        complete_graph = Graph()

        # Define and bind all prefixes - use # for namespace prefixes (not both / and #)
        prefixes = {
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
            'owl': 'http://www.w3.org/2002/07/owl#',
            'brick': 'https://brickschema.org/schema/Brick#',
            'rec': 'https://w3id.org/rec#',  # RealEstateCore for Building and location relationships
            'unit': 'http://qudt.org/vocab/unit/',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            'ref': 'https://brickschema.org/schema/Brick/ref#',
            'hhws': 'https://hhws.example.org#'  # Use # instead of /#
        }

        for prefix, namespace in prefixes.items():
            complete_graph.bind(prefix, Namespace(namespace), override=True, replace=True)

        # Add ontology declaration triples
        # Ontology URI (without # - this is the document/ontology identifier)
        ontology_uri = URIRef("https://hhws.example.org")
        # Brick ontology URI to import
        brick_ontology_uri = URIRef("https://brickschema.org/schema/1.3/Brick#")

        complete_graph.add((ontology_uri, RDF.type, self.owl.Ontology))
        complete_graph.add((ontology_uri, self.owl.imports, brick_ontology_uri))

        # Add all triples from the main graph to the complete graph
        for triple in self.graph:
            complete_graph.add(triple)

        # Serialize the complete graph
        ttl_content = complete_graph.serialize(format='turtle')

        # Filter out any unwanted auto-generated ontology declarations
        filtered_content = self._filter_unwanted_declarations(ttl_content)

        # Write to file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(filtered_content)
        except IOError as e:
            self.logger.error(f"Failed to write to {output_path}: {e}")
            raise

    def _filter_unwanted_declarations(self, content: str) -> str:
        """Filter out unwanted auto-generated ontology declarations."""
        lines = content.split('\n')
        filtered_lines = []

        for line in lines:
            # Skip unwanted ontology declarations with urn: prefixes
            if (line.strip().startswith('<urn:') or
                (line.strip().startswith('owl:imports') and 'urn:' in line) or
                (line.strip().startswith('a owl:Ontology') and '<urn:' in line)):
                continue
            filtered_lines.append(line)

        return '\n'.join(filtered_lines)

    # Remove the old methods that are no longer needed
    def _get_filtered_graph_content(self) -> str:
        """Deprecated method - functionality moved to _serialize_with_ontology"""
        pass

    def _write_combined_content(self, output_path: str, header: str, content: str):
        """Deprecated method - functionality moved to _serialize_with_ontology"""
        pass

    def _add_timeseries_reference(self, sensor_uri: URIRef, building_tag: str, sensor_name: str) -> None:
        """Add TimeseriesReference to sensor for linking to CSV data."""

        # Use a more direct approach to create blank node
        from rdflib import BNode
        timeseries_ref = BNode()

        # Add the timeseries reference structure
        self.graph.add((sensor_uri, self.ref.hasExternalReference, timeseries_ref))
        self.graph.add((timeseries_ref, RDF.type, self.ref.TimeseriesReference))
        self.graph.add((timeseries_ref, self.ref.hasTimeseriesId, Literal(sensor_name)))

        # CSV filename format: {building_tag}hhw_system_data.csv
        csv_filename = f"{building_tag}hhw_system_data.csv"
        self.graph.add((timeseries_ref, self.ref.storedAt, Literal(csv_filename)))

    def _save_validation_warnings(self, warnings_file: str) -> None:
        """Save validation warnings to a text file for manual review."""
        try:
            from datetime import datetime
            with open(warnings_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("Brick Model Generation - Validation Warnings Report\n")
                f.write(f"Generated time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Total found {len(self.validation_warnings)} issues requiring manual review:\n\n")

                for i, warning in enumerate(self.validation_warnings, 1):
                    f.write(f"{i}. {warning}\n")

                f.write("\n" + "=" * 80 + "\n")
                f.write("Please manually review the above issues to confirm data accuracy\n")
                f.write("=" * 80 + "\n")

            self.logger.info(f"Validation warnings successfully saved to: {warnings_file}")
        except Exception as e:
            self.logger.error(f"Failed to save validation warnings: {e}")

