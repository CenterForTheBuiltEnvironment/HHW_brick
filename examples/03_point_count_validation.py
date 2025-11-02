"""
Example 3: Count and Validate Points in Brick Models

This example shows how to count points/equipment and validate against ground truth.
You'll learn to generate ground truth and verify your models.

What you'll learn:
- How to generate ground truth from CSV data
- How to validate point counts in Brick models
- How to use batch validation for multiple models
- How to interpret validation results
"""

from pathlib import Path
from hhw_brick.validation import GroundTruthCalculator, BrickModelValidator

def main():
    print("Example 3: Count and Validate Points")
    print("=" * 60)

    # Prepare paths
    fixtures = Path(__file__).parent.parent / "tests" / "fixtures"
    metadata_csv = fixtures / "metadata.csv"
    vars_csv = fixtures / "vars_available_by_building.csv"
    brick_model_dir = fixtures / "Brick_Model_File"

    # Ground truth will be saved in fixtures
    ground_truth_csv = fixtures / "ground_truth.csv"

    # ========================================================================
    # Part 1: Generate Ground Truth (Expected Counts)
    # ========================================================================
    print(f"\n{'='*60}")
    print("Part 1: Generate Ground Truth")
    print(f"{'='*60}")

    print(f"\n✓ Calculating expected counts from CSV data...")

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
        print(f"    Building {row['tag']}: {int(row['point_count'])} points, "
              f"{int(row['boiler_count'])} boilers, {int(row['pump_count'])} pumps")

    # ========================================================================
    # Part 2: Validate Single Building
    # ========================================================================
    print(f"\n{'='*60}")
    print("Part 2: Validate Single Building")
    print(f"{'='*60}")

    # Select a building to validate
    building_tag = "29"
    model_file = brick_model_dir / f"building_{building_tag}_district_hw_z.ttl"

    if not model_file.exists():
        print(f"\n✗ Error: Model file not found: {model_file}")
        print(f"  Please run Example 1 first.")
        return

    print(f"\n✓ Validating building {building_tag}...")

    # Create validator with ground truth
    validator = BrickModelValidator(
        ground_truth_csv_path=str(ground_truth_csv),
    )

    # Validate point counts (validator will auto-extract building_tag from filename)
    result = validator.validate_point_count(str(model_file))

    # Show results
    print(f"\n✓ Validation complete!")

    if result.get('success'):
        print(f"  ✓ Point counts match! Model is correct.")
    else:
        print(f"  ✗ Point count mismatch detected")

    # Display details
    expected = result.get('expected_point_count', 0)
    actual = result.get('actual_point_count', 0)
    accuracy = result.get('accuracy_percentage', 0)

    print(f"\n  Details:")
    print(f"    Expected points: {expected}")
    print(f"    Actual points: {actual}")
    print(f"    Match: {'✓ Yes' if result.get('match') else '✗ No'}")
    print(f"    Accuracy: {accuracy:.1f}%")

    # ========================================================================
    # Part 3: Batch Validate Multiple Buildings (with Parallel Processing)
    # ========================================================================
    print(f"\n{'='*60}")
    print("Part 3: Batch Validate Multiple Buildings")
    print(f"{'='*60}")

    print(f"\n✓ Running batch validation on all models...")
    print(f"  (Using parallel processing for faster validation)")

    # Use batch validation method with parallel processing
    # You can specify max_workers to control parallelism (default: CPU count - 1)
    batch_results = validator.batch_validate_point_count(
        test_data_dir=str(brick_model_dir),
        max_workers=4  # Optional: specify number of parallel workers
    )

    # Show summary
    print(f"\n✓ Batch validation complete!")

    total = batch_results.get('total_files', 0)
    matched = batch_results.get('matched_files', 0)
    mismatched = batch_results.get('mismatched_files', 0)
    accuracy = batch_results.get('overall_accuracy', 0)

    print(f"\nSummary:")
    print(f"  - Total models: {total}")
    print(f"  - Matched (correct): {matched}")
    print(f"  - Mismatched: {mismatched}")
    print(f"  - Overall accuracy: {accuracy:.1f}%")

    # Show details for each model
    if batch_results.get('results'):
        print(f"\nDetails by model:")
        for r in batch_results['results']:
            filename = Path(r['ttl_file_path']).name
            status = "✓" if r.get('success') else "✗"
            expected = r.get('expected_point_count', 0)
            actual = r.get('actual_point_count', 0)

            print(f"  {status} {filename}")
            print(f"      Expected: {expected} points, Actual: {actual} points")

    # ========================================================================
    # Summary
    # ========================================================================
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    print(f"""
  ✓ Generated ground truth from CSV data
  ✓ Validated {total} Brick models using parallel processing
  ✓ Overall accuracy: {accuracy:.1f}%
  ✓ Ground truth saved: {ground_truth_csv}
""")
    print(f"\n✓ Done! Point count validation ensures model completeness.")


if __name__ == "__main__":
    main()
