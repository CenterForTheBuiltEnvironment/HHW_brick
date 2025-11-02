"""
Example 2: Validate Brick Models

This example shows how to validate Brick models for ontology correctness.
You'll learn both single model validation and batch validation.

What you'll learn:
- How to validate a single Brick model
- How to validate multiple Brick models at once
- How to check if models follow Brick schema rules
- How to interpret validation results
"""

from pathlib import Path
from hhw_brick import BrickModelValidator

def main():
    print("Example 2: Brick Model Validation")
    print("=" * 60)

    # Prepare paths
    # Use existing Brick models from Example 1
    fixtures = Path(__file__).parent.parent / "tests" / "fixtures"
    brick_model_dir = fixtures / "Brick_Model_File"

    # ========================================================================
    # Part 1: Validate a Single Brick Model
    # ========================================================================
    print(f"\n{'='*60}")
    print("Part 1: Validate Single Brick Model")
    print(f"{'='*60}")

    # Select one model to validate
    model_file = brick_model_dir / "building_29_district_hw_z.ttl"
    
    if not model_file.exists():
        print(f"\n✗ Error: Model file not found: {model_file}")
        print(f"  Please run Example 1 first to generate Brick models.")
        return

    print(f"\n✓ Validating {model_file.name}...")

    # Create validator with local Brick schema
    validator = BrickModelValidator(use_local_brick=True)
    
    # Validate the model
    result = validator.validate_ontology(str(model_file))

    # Show results
    if result and result.get('valid', result.get('is_valid', False)):
        print(f"✓ Valid! Model follows Brick schema rules.")
    else:
        print(f"✗ Invalid! Model has validation errors.")
        if result and result.get('violations'):
            print(f"  Found {len(result['violations'])} violations")

    # ========================================================================
    # Part 2: Batch Validate Multiple Brick Models (with Parallel Processing)
    # ========================================================================
    print(f"\n{'='*60}")
    print("Part 2: Batch Validate Multiple Models")
    print(f"{'='*60}")

    # Find all TTL files in the directory
    ttl_files = list(brick_model_dir.glob("*.ttl"))
    
    if not ttl_files:
        print(f"\n✗ No TTL files found in {brick_model_dir}")
        return

    print(f"\n✓ Validating {len(ttl_files)} Brick models...")
    print(f"  (Using parallel processing for faster validation)")

    # Use batch validation with parallel processing
    # You can specify max_workers to control parallelism (default: CPU count - 1)
    batch_result = validator.batch_validate_ontology(
        test_data_dir=str(brick_model_dir),
        max_workers=15  # Optional: specify number of parallel workers
    )

    # Show summary
    print(f"\n✓ Validation complete!")
    
    total = batch_result.get('total_files', 0)
    passed = batch_result.get('passed_files', 0)
    failed = batch_result.get('failed_files', 0)
    accuracy = batch_result.get('overall_accuracy', 0)

    print(f"\nResults:")
    print(f"  - Total models: {total}")
    print(f"  - Valid: {passed}")
    print(f"  - Invalid: {failed}")
    print(f"  - Overall accuracy: {accuracy:.1f}%")

    # ========================================================================
    # Summary
    # ========================================================================
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")

Author: Mingchen Li
    print(f"""
  ✓ Validated {total} Brick models using parallel processing
  ✓ All models checked against Brick schema
  ✓ Overall accuracy: {accuracy:.1f}%
""")


if __name__ == "__main__":
    main()
