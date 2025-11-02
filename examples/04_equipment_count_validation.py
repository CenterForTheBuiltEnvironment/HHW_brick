"""
Example 4: Validate Equipment Counts in Brick Models

This example shows how to validate equipment counts against ground truth.
You'll learn to verify boilers, pumps, and weather stations in your models.

What you'll learn:
- How to validate equipment counts in Brick models
- How to check boilers, pumps, and weather stations
- How to use batch equipment validation
- How to interpret equipment validation results
"""

from pathlib import Path
from hhw_brick.validation import GroundTruthCalculator, BrickModelValidator

def main():
    print("Example 4: Validate Equipment Counts")
    print("=" * 60)

    # Prepare paths
    fixtures = Path(__file__).parent.parent / "tests" / "fixtures"
    metadata_csv = fixtures / "metadata.csv"
    vars_csv = fixtures / "vars_available_by_building.csv"
    brick_model_dir = fixtures / "Brick_Model_File"

    # Ground truth will be saved in fixtures
    ground_truth_csv = fixtures / "ground_truth.csv"

    # ========================================================================
    # Part 1: Generate Ground Truth
    # ========================================================================
    print(f"\n{'='*60}")
    print("Part 1: Generate Ground Truth")
    print(f"{'='*60}")

    print(f"\n✓ Generating ground truth from CSV data...")

    # Calculate ground truth from source CSV files
    calculator = GroundTruthCalculator()
    ground_truth_df = calculator.calculate(
        metadata_csv=str(metadata_csv),
        vars_csv=str(vars_csv),
        output_csv=str(ground_truth_csv)
    )

    print(f"\n✓ Ground truth generated!")
    print(f"  - Saved to: {ground_truth_csv.name}")
    print(f"  - Total buildings: {len(ground_truth_df)}")

    # Show sample ground truth
    print(f"\n  Sample (first 3 buildings):")
    for idx, row in ground_truth_df.head(3).iterrows():
        print(f"    Building {row['tag']}: {int(row['boiler_count'])} boilers, "
              f"{int(row['pump_count'])} pumps, {int(row['weather_station_count'])} weather stations")

    # ========================================================================
    # Part 2: Validate Equipment in Single Building
    # ========================================================================
    print(f"\n{'='*60}")
    print("Part 2: Validate Single Building Equipment")
    print(f"{'='*60}")

    # Select a building to validate
    building_tag = "29"
    model_file = brick_model_dir / f"building_{building_tag}_district_hw_z.ttl"

    if not model_file.exists():
        print(f"\n✗ Error: Model file not found: {model_file}")
        print(f"  Please run Example 1 first.")
        return

    print(f"\n✓ Validating equipment in building {building_tag}...")

    # Create validator with ground truth
    validator = BrickModelValidator(
        ground_truth_csv_path=str(ground_truth_csv),
        use_local_brick=True
    )

    # Validate equipment counts
    result = validator.validate_equipment_count(str(model_file))

    # Show results
    print(f"\n✓ Validation complete!")

    if result.get('overall_success'):
        print(f"  ✓ All equipment counts match! Model is correct.")
    else:
        print(f"  ✗ Equipment count mismatch detected")

    # Display details for each equipment type
    print(f"\n  Equipment Details:")

    # Boilers
    boiler = result.get('boiler', {})
    boiler_status = "✓" if boiler.get('match') else "✗"
    print(f"    {boiler_status} Boilers: {boiler.get('actual', 0)} / {boiler.get('expected', 0)} (actual/expected)")

    # Pumps
    pump = result.get('pump', {})
    pump_status = "✓" if pump.get('match') else "✗"
    print(f"    {pump_status} Pumps: {pump.get('actual', 0)} / {pump.get('expected', 0)} (actual/expected)")

    # Weather Stations
    weather = result.get('weather_station', {})
    weather_status = "✓" if weather.get('match') else "✗"
    print(f"    {weather_status} Weather Stations: {weather.get('actual', 0)} / {weather.get('expected', 0)} (actual/expected)")

    # ========================================================================
    # Part 3: Batch Validate Multiple Buildings (with Parallel Processing)
    # ========================================================================
    print(f"\n{'='*60}")
    print("Part 3: Batch Validate Equipment Counts")
    print(f"{'='*60}")

    print(f"\n✓ Running batch equipment validation...")
    print(f"  (Using parallel processing for faster validation)")

    # Use batch validation method with parallel processing
    # You can specify max_workers to control parallelism (default: CPU count - 1)
    batch_results = validator.batch_validate_equipment_count(
        test_data_dir=str(brick_model_dir),
        max_workers=4  # Optional: specify number of parallel workers
    )

    # Show summary
    print(f"\n✓ Batch validation complete!")

    total = batch_results.get('total_files', 0)
    passed = batch_results.get('passed_files', 0)
    failed = batch_results.get('failed_files', 0)
    accuracy = batch_results.get('overall_accuracy', 0)

    print(f"\nSummary:")
    print(f"  - Total models: {total}")
    print(f"  - Passed (all match): {passed}")
    print(f"  - Failed (mismatch): {failed}")
    print(f"  - Overall accuracy: {accuracy:.1f}%")

    # Show details for each model
    if batch_results.get('results'):
        print(f"\nDetails by model:")
        for r in batch_results['results']:
            filename = Path(r['ttl_file_path']).name
            status = "✓" if r.get('overall_success') else "✗"

            print(f"  {status} {filename}")

            # Show equipment counts
            boiler = r.get('boiler', {})
            pump = r.get('pump', {})
            weather = r.get('weather_station', {})

            print(f"      Boilers: {boiler.get('actual', 0)}/{boiler.get('expected', 0)}, "
                  f"Pumps: {pump.get('actual', 0)}/{pump.get('expected', 0)}, "
                  f"Weather: {weather.get('actual', 0)}/{weather.get('expected', 0)}")

    # ========================================================================
    # Summary
    # ========================================================================
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    print(f"""
  ✓ Validated equipment in {total} Brick models using parallel processing
  ✓ Checked boilers, pumps, and weather stations
  ✓ Overall accuracy: {accuracy:.1f}%
""")


if __name__ == "__main__":
    main()
