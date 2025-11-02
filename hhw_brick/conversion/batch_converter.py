# -*- coding: utf-8 -*-
"""
Batch Converter for HHWS Brick Models

Provides batch conversion functionality for multiple buildings.
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from tqdm import tqdm

# Import from same module
from .csv_to_brick import CSVToBrickConverter


class BatchConverter:
    """
    Batch converter for multiple buildings.

    Simplifies the process of converting multiple buildings from CSV to Brick format.
    """

    def __init__(self):
        """Initialize the batch converter."""
        self.logger = logging.getLogger(__name__)
        self.converter = CSVToBrickConverter()

    def convert_all_buildings(
        self,
        metadata_csv: str,
        vars_csv: str,
        output_dir: str,
        system_type: Optional[str] = None,
        building_tags: Optional[List[str]] = None,
        show_progress: bool = True,
    ) -> Dict[str, Any]:
        """
        Convert all buildings (or filtered by system type/tags) to Brick models.

        Args:
            metadata_csv: Path to metadata CSV file
            vars_csv: Path to vars CSV file
            output_dir: Output directory for TTL files
            system_type: Optional filter by system type
            building_tags: Optional list of specific building tags to convert
            show_progress: Show progress bar

        Returns:
            Dict with conversion statistics and results
        """
        self.logger.info("Starting batch conversion")

        # Load metadata
        metadata_df = pd.read_csv(metadata_csv)

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Filter by system type if specified
        if system_type:
            metadata_df = metadata_df[
                metadata_df["system"].str.lower().str.contains(system_type.lower(), na=False)
            ]

        # Filter by building tags if specified
        if building_tags:
            metadata_df = metadata_df[
                metadata_df["tag"].astype(str).isin([str(t) for t in building_tags])
            ]

        # Statistics
        stats = {
            "total": len(metadata_df),
            "successful": 0,
            "failed": 0,
            "by_system": {},
            "total_triples": 0,
            "failed_buildings": [],
            "successful_files": [],
        }

        # Process each building
        iterator = metadata_df.iterrows()
        if show_progress:
            iterator = tqdm(iterator, total=len(metadata_df), desc="Converting buildings")

        for idx, (_, building) in enumerate(iterator):
            building_tag = str(int(building["tag"]))
            system = str(building["system"]).strip()
            org = building.get("org", "unknown")

            try:
                # Clear converter graph
                self.converter.clear_graph()

                # Generate output filename
                safe_system = system.replace(" ", "_").replace("/", "_").lower()
                output_file = (
                    output_path / f"building_{building_tag}_{safe_system}_{org.lower()}.ttl"
                )

                # Convert
                graph = self.converter.convert_to_brick(
                    metadata_csv=metadata_csv,
                    vars_csv=vars_csv,
                    system_type=system,
                    building_tag=building_tag,
                    output_path=str(output_file),
                )

                # Update statistics
                stats["successful"] += 1
                stats["total_triples"] += len(graph)
                stats["successful_files"].append(str(output_file))

                if system not in stats["by_system"]:
                    stats["by_system"][system] = 0
                stats["by_system"][system] += 1

            except Exception as e:
                stats["failed"] += 1
                stats["failed_buildings"].append(
                    {"tag": building_tag, "system": system, "error": str(e)}
                )
                self.logger.error(f"Failed to convert building {building_tag}: {e}")

        # Generate summary report
        stats["conversion_date"] = datetime.now().isoformat()
        stats["metadata_csv"] = metadata_csv
        stats["vars_csv"] = vars_csv
        stats["output_dir"] = output_dir

        self.logger.info(
            f"Batch conversion completed: {stats['successful']}/{stats['total']} successful"
        )

        return stats

    def save_summary_report(self, stats: Dict, output_file: str):
        """
        Save conversion summary to a text file.

        Args:
            stats: Statistics dictionary from convert_all_buildings
            output_file: Path to output summary file
        """
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("=" * 70 + "\n")
            f.write("HHWS Brick Batch Conversion Summary Report\n")
            f.write("=" * 70 + "\n\n")

            f.write(f"Conversion Date: {stats.get('conversion_date', 'N/A')}\n")
            f.write(f"Metadata CSV: {stats.get('metadata_csv', 'N/A')}\n")
            f.write(f"Vars CSV: {stats.get('vars_csv', 'N/A')}\n")
            f.write(f"Output Directory: {stats.get('output_dir', 'N/A')}\n\n")

            f.write("-" * 70 + "\n")
            f.write("CONVERSION STATISTICS\n")
            f.write("-" * 70 + "\n")
            f.write(f"Total Buildings: {stats['total']}\n")
            f.write(
                f"Successful: {stats['successful']} ({stats['successful']/stats['total']*100:.1f}%)\n"
            )
            f.write(f"Failed: {stats['failed']}\n")
            f.write(f"Total RDF Triples: {stats['total_triples']:,}\n\n")

            if stats["by_system"]:
                f.write("-" * 70 + "\n")
                f.write("BY SYSTEM TYPE\n")
                f.write("-" * 70 + "\n")
                for system, count in sorted(stats["by_system"].items()):
                    f.write(f"  {system}: {count} buildings\n")
                f.write("\n")

            if stats["failed_buildings"]:
                f.write("-" * 70 + "\n")
                f.write("FAILED BUILDINGS\n")
                f.write("-" * 70 + "\n")
                for failed in stats["failed_buildings"]:
                    f.write(f"  Building {failed['tag']} ({failed['system']})\n")
                    f.write(f"    Error: {failed['error']}\n\n")

        self.logger.info(f"Summary report saved to: {output_file}")
