"""
Ground Truth Calculator Module

Calculate validation baseline data from source CSV files:
- Point counts from vars_available_by_building.csv
- Boiler counts from metadata.csv and vars data
- Pump counts based on system type and detected pumps
- Weather station counts from oper column


Author: Mingchen Li
"""

import pandas as pd
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class GroundTruthCalculator:
    """
    Calculate ground truth validation data from source CSV files.

    This calculator generates a ground_truth.csv file with expected counts
    for points, boilers, pumps, and weather stations for each building.
    """

    def __init__(self):
        """Initialize the ground truth calculator."""
        self.logger = logging.getLogger(__name__)

    def calculate(
        self, metadata_csv: str, vars_csv: str, output_csv: str = "ground_truth.csv"
    ) -> pd.DataFrame:
        """
        Calculate ground truth data for all buildings.

        Args:
            metadata_csv: Path to metadata.csv file
            vars_csv: Path to vars_available_by_building.csv file
            output_csv: Output path for ground_truth.csv (default: "ground_truth.csv")

        Returns:
            DataFrame with columns: tag, system, point_count, boiler_count,
                                   pump_count, weather_station_count
        """
        self.logger.info("Starting ground truth calculation...")

        # Load data
        metadata_df = pd.read_csv(metadata_csv)
        vars_df = pd.read_csv(vars_csv)

        self.logger.info(f"Loaded {len(metadata_df)} metadata records")
        self.logger.info(f"Loaded {len(vars_df)} vars records")

        # Merge data
        merged_df = pd.merge(metadata_df, vars_df, on="tag", how="inner")
        self.logger.info(f"Merged {len(merged_df)} records")

        # Calculate ground truth for each building
        ground_truth_data = []

        for idx, row in merged_df.iterrows():
            tag = str(int(row["tag"]))
            system = str(row["system"]).strip()

            # 1. Calculate point count
            point_count = self._calculate_point_count(row, vars_df)

            # 2. Calculate boiler count
            boiler_count = self._calculate_boiler_count(row, system)

            # 3. Calculate pump count
            pump_count = self._calculate_pump_count(row, system)

            # 4. Calculate weather station count
            weather_station_count = self._calculate_weather_station_count(row)

            ground_truth_data.append(
                {
                    "tag": tag,
                    "system": system,
                    "point_count": point_count,
                    "boiler_count": boiler_count,
                    "pump_count": pump_count,
                    "weather_station_count": weather_station_count,
                }
            )

        # Create DataFrame
        ground_truth_df = pd.DataFrame(ground_truth_data)

        # Save to file
        ground_truth_df.to_csv(output_csv, index=False)
        self.logger.info(f"Ground truth saved to: {output_csv}")
        self.logger.info(f"Total buildings: {len(ground_truth_df)}")

        return ground_truth_df

    def _calculate_point_count(self, row: pd.Series, vars_df: pd.DataFrame) -> int:
        """
        Calculate point count from vars_available_by_building.csv.
        Counts non-empty values after the 'datetime' column.
        """
        # Get column index for datetime
        datetime_idx = vars_df.columns.get_loc("datetime")
        point_columns = vars_df.columns[datetime_idx + 1 :]

        # Count non-empty values with value > 0
        point_count = 0
        for col in point_columns:
            val = row[col]
            if pd.notna(val) and val != "" and str(val).strip().upper() not in ["NA", "NULL", ""]:
                try:
                    if float(val) > 0:
                        point_count += 1
                except (ValueError, TypeError):
                    pass

        return point_count

    def _calculate_boiler_count(self, row: pd.Series, system: str) -> int:
        """
        Calculate boiler count based on system type and metadata.
        District systems have 0 boilers, others use b_number and fire/sup/ret columns.
        For 'Boiler' system type, at least 1 boiler is guaranteed.
        """
        # Check if district system
        if "district" in system.lower():
            return 0

        # For boiler systems, use b_number and fire/sup/ret columns
        boiler_count = 0
        b_number = row["b_number"]

        try:
            if pd.notna(b_number) and str(b_number).strip().upper() not in ["NA", "NULL", ""]:
                boiler_count = int(float(b_number))
        except (ValueError, TypeError):
            boiler_count = 0

        # Check fire columns (fire1, fire2, fire3, fire4)
        fire_count = 0
        for i in range(1, 5):
            col_name = f"fire{i}"
            if col_name in row.index and pd.notna(row[col_name]):
                try:
                    if float(row[col_name]) > 0:
                        fire_count = max(fire_count, i)
                except (ValueError, TypeError):
                    pass

        # Check sup columns (sup1, sup2, sup3, sup4)
        sup_count = 0
        for i in range(1, 5):
            col_name = f"sup{i}"
            if col_name in row.index and pd.notna(row[col_name]):
                try:
                    if float(row[col_name]) > 0:
                        sup_count = max(sup_count, i)
                except (ValueError, TypeError):
                    pass

        # Check ret columns (ret1, ret2, ret3, ret4)
        ret_count = 0
        for i in range(1, 5):
            col_name = f"ret{i}"
            if col_name in row.index and pd.notna(row[col_name]):
                try:
                    if float(row[col_name]) > 0:
                        ret_count = max(ret_count, i)
                except (ValueError, TypeError):
                    pass

        # Take maximum
        boiler_count = max(boiler_count, fire_count, sup_count, ret_count)

        # For any boiler-based system (Boiler, Condensing, Non-condensing),
        # ensure at least 1 boiler if count is still 0
        # These systems must have at least one boiler by definition
        system_lower = system.lower()
        has_boiler_system = any(
            keyword in system_lower for keyword in ["boiler", "condensing", "non-condensing"]
        )

        if has_boiler_system and boiler_count == 0:
            boiler_count = 1

        return boiler_count

    def _calculate_pump_count(self, row: pd.Series, system: str) -> int:
        """
        Calculate pump count based on system type and detected pumps.

        Logic:
        - District system: 1 loop, default 1 pump. If detected, use detected count.
        - Boiler system: 2 loops, default 1 pump per loop = 2 pumps.
          If detected N pumps, means one loop has N pumps, other has 1 pump.
          Total = N + 1
        """
        # First detect pump count from vars
        vars_pump_count = 0

        # Check pmpN_spd and pmpN_vfd
        for i in range(1, 5):
            spd_col = f"pmp{i}_spd"
            vfd_col = f"pmp{i}_vfd"

            has_spd = spd_col in row.index and pd.notna(row[spd_col])
            has_vfd = vfd_col in row.index and pd.notna(row[vfd_col])

            if has_spd or has_vfd:
                try:
                    if has_spd and float(row[spd_col]) > 0:
                        vars_pump_count = max(vars_pump_count, i)
                    if has_vfd and float(row[vfd_col]) > 0:
                        vars_pump_count = max(vars_pump_count, i)
                except (ValueError, TypeError):
                    pass

        # Check pmp_spd (single pump speed)
        if "pmp_spd" in row.index and pd.notna(row["pmp_spd"]):
            try:
                if float(row["pmp_spd"]) > 0:
                    vars_pump_count = max(vars_pump_count, 1)
            except (ValueError, TypeError):
                pass

        # Determine final pump count based on system type
        if "district" in system.lower():
            # District system: 1 loop, use detected count or default 1
            pump_count = max(1, vars_pump_count)
        else:
            # Boiler system: 2 loops
            if vars_pump_count > 0:
                # One loop has vars_pump_count pumps, other loop has 1 pump
                pump_count = vars_pump_count + 1
            else:
                # Default: 2 loops with 1 pump each
                pump_count = 2

        return pump_count

    def _calculate_weather_station_count(self, row: pd.Series) -> int:
        """
        Calculate weather station count from oper column.
        """
        if "oper" in row.index and pd.notna(row["oper"]):
            try:
                if float(row["oper"]) > 0:
                    return 1
            except (ValueError, TypeError):
                pass
        return 0

    def get_statistics(self, ground_truth_df: pd.DataFrame) -> Dict:
        """
        Get statistics summary from ground truth data.

        Args:
            ground_truth_df: Ground truth DataFrame

        Returns:
            Dict with statistics
        """
        stats = {
            "total_buildings": len(ground_truth_df),
            "point_count": {
                "min": int(ground_truth_df["point_count"].min()),
                "max": int(ground_truth_df["point_count"].max()),
                "mean": float(ground_truth_df["point_count"].mean()),
            },
            "boiler_count": {
                "0": int((ground_truth_df["boiler_count"] == 0).sum()),
                "1": int((ground_truth_df["boiler_count"] == 1).sum()),
                "2": int((ground_truth_df["boiler_count"] == 2).sum()),
                "3+": int((ground_truth_df["boiler_count"] >= 3).sum()),
            },
            "pump_count": {
                "0": int((ground_truth_df["pump_count"] == 0).sum()),
                "1": int((ground_truth_df["pump_count"] == 1).sum()),
                "2": int((ground_truth_df["pump_count"] == 2).sum()),
                "3+": int((ground_truth_df["pump_count"] >= 3).sum()),
            },
            "weather_station": {
                "with": int((ground_truth_df["weather_station_count"] > 0).sum()),
                "without": int((ground_truth_df["weather_station_count"] == 0).sum()),
            },
        }

        return stats
