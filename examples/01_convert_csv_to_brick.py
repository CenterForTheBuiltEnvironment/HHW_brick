"""
Example 1: Convert CSV to Brick Model

This example shows how to convert building data from CSV to Brick format.
You'll learn both single building conversion and batch conversion.

What you'll learn:
- How to convert a single building
- How to batch convert multiple buildings
- How to specify input CSV files
- How to save Brick model outputs
"""

from pathlib import Path
from hhw_brick import CSVToBrickConverter, BatchConverter

def main():
    print("Example 1: CSV to Brick Conversion")
    print("=" * 60)

    # Prepare input data
    # The fixtures directory contains sample CSV data
    fixtures = Path(__file__).parent.parent / "tests" / "fixtures"
    metadata_csv = fixtures / "metadata.csv"          # Building information
    vars_csv = fixtures / "vars_available_by_building.csv"  # Sensor/point data
    output_dir = fixtures / "Brick_Model_File"        # Output directory
    output_dir.mkdir(exist_ok=True)

    # ========================================================================
    # Part 1: Convert a Single Building
    # ========================================================================
    print(f"\n{'='*60}")
    print("Part 1: Convert Single Building")
    print(f"{'='*60}")

    building_id = "29"  # Building ID to convert
    print(f"\n✓ Converting building {building_id}...")

    # Create converter and convert one building
    # Note: system_type is auto-detected from metadata.csv
    converter = CSVToBrickConverter()
    result = converter.convert_to_brick(
        metadata_csv=str(metadata_csv),
        vars_csv=str(vars_csv),
        building_tag=building_id,
        output_path=str(output_dir / f"building_{building_id}_district_hw_z.ttl")
    )

    print(f"✓ Success!")
    print(f"  - Building ID: {building_id}")
    print(f"  - RDF Triples: {len(result)} statements")
    print(f"  - Output: building_{building_id}_district_hw_z.ttl")

    # ========================================================================
    # Part 2: Batch Convert Multiple Buildings
    # ========================================================================
    print(f"\n{'='*60}")
    print("Part 2: Batch Convert Multiple Buildings")
    print(f"{'='*60}")

    print(f"\n✓ Converting all District HW buildings...")

    # Use BatchConverter for multiple buildings at once
    batch_converter = BatchConverter()
    results = batch_converter.convert_all_buildings(
        metadata_csv=str(metadata_csv),
        vars_csv=str(vars_csv),
        output_dir=str(output_dir),   # Only convert this type
        show_progress=True                   # Show progress bar
    )

    print(f"\n✓ Success!")
    print(f"  - Buildings converted: {results['successful']} / {results['total']}")
    print(f"  - Total RDF triples: {results['total_triples']} statements")

    # Show generated files
    if results.get('successful_files'):
        print(f"\n  Generated files:")
        for file_path in results['successful_files']:
            print(f"    - {Path(file_path).name}")

    # ========================================================================
    # Summary
    # ========================================================================
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    print(f"  - All Brick models are saved to: {output_dir}")
    print(f"\n✓ Done! You can now use these Brick models for analysis.")


if __name__ == "__main__":
    main()
