"""
Example 5: Subgraph Pattern Matching

This example shows how to validate Brick models using subgraph pattern matching.
You'll learn to identify system types (Boiler vs District) and verify system structures.

What you'll learn:
- How to check if a model matches Pattern 2 (District System)
- How to validate system structure and components
- How to batch validate multiple models for pattern matching
- How to interpret pattern matching results

Background:
Hot water systems typically follow two main architectural patterns:
- Pattern 1 (Boiler System): Has primary loop with boiler(s) + secondary loop
- Pattern 2 (District System): Has only secondary loop, no boilers (heated by district plant)
"""

from pathlib import Path
from hhw_brick.validation import SubgraphPatternValidator

def main():
    print("Example 5: Subgraph Pattern Matching")
    print("=" * 60)

    # Prepare paths
    # Use existing Brick models from Example 1
    fixtures = Path(__file__).parent.parent / "tests" / "fixtures"
    brick_model_dir = fixtures / "Brick_Model_File"

    # Create pattern validator
    validator = SubgraphPatternValidator()

    # ========================================================================
    # Part 1: Validate a District System (Pattern 2)
    # ========================================================================
    print(f"\n{'='*60}")
    print("Part 1: Validate District System Pattern")
    print(f"{'='*60}")

    # Select a district system model to validate
    building_tag = "29"
    district_model = brick_model_dir / f"building_{building_tag}_district_hw_z.ttl"

    if not district_model.exists():
        print(f"\n✗ Error: Model file not found: {district_model}")
        print(f"  Please run Example 1 first.")
        return

    print(f"\n✓ Validating building {building_tag}...")

    # Check Pattern 2: District System
    pattern_2_result = validator.check_pattern_2_district_system(str(district_model))

    # Show results
    print(f"\n✓ Pattern 2 (District System) Analysis:")

    if pattern_2_result.get('matched'):
        print(f"  ✓ This model matches Pattern 2 - District System!")

        details = pattern_2_result.get('details', {})
        print(f"\n  System Components Found:")
        print(f"    - Building: {'✓' if details.get('has_building') else '✗'}")
        print(f"    - Hot Water System: {'✓' if details.get('has_hot_water_system') else '✗'}")
        print(f"    - Secondary Loop: {'✓' if details.get('has_secondary_loop') else '✗'}")
        print(f"    - Pump: {'✓' if details.get('has_pump') else '✗'}")
        print(f"    - Weather Station: {'✓' if details.get('has_weather_station') else '✗ (optional)'}")
        print(f"    - NO Boiler: {'✓' if not details.get('has_boiler') else '✗ (should be absent)'}")
        print(f"    - NO Primary Loop: {'✓' if not details.get('has_primary_loop') else '✗ (should be absent)'}")

        print(f"\n  Equipment Counts:")
        print(f"    - Pumps: {details.get('pump_count', 0)}")
    else:
        print(f"  ✗ This model does NOT match Pattern 2")
        if pattern_2_result.get('error'):
            print(f"  Error: {pattern_2_result['error']}")

    # ========================================================================
    # Part 2: Batch Validate Multiple Buildings
    # ========================================================================
    print(f"\n{'='*60}")
    print("Part 2: Batch Validate Multiple Buildings")
    print(f"{'='*60}")

    # Find all TTL files in the directory
    ttl_files = list(brick_model_dir.glob("*.ttl"))

    if not ttl_files:
        print(f"\n✗ No TTL files found in {brick_model_dir}")
        return

    print(f"\n✓ Validating {len(ttl_files)} Brick models...")

    # Use batch validation method with parallel processing
    # max_workers is optional (default: CPU count - 1)
    batch_results = validator.batch_validate_all_buildings(
        ttl_directory=str(brick_model_dir),
        max_workers=4  # Optional: specify number of parallel workers
    )

    # Calculate totals
    total = batch_results.get('total_files', 0)
    results = batch_results.get('results', [])

    # Count pattern matches correctly from results
    pattern_1_count = 0
    pattern_2_count = 0
    no_match_count = 0

    for r in results:
        primary_pattern = r.get('primary_pattern', '')
        if 'Pattern 1' in primary_pattern:
            pattern_1_count += 1
        elif 'Pattern 2' in primary_pattern:
            pattern_2_count += 1
        else:
            no_match_count += 1

    print(f"\n✓ Validation complete!")

    # Calculate success rate
    matched_count = pattern_1_count + pattern_2_count
    success_rate = (matched_count / total * 100) if total > 0 else 0.0

    print(f"\nResults:")
    print(f"  - Total models validated: {total}")
    print(f"  - Pattern 1 (Boiler Systems): {pattern_1_count}")
    print(f"  - Pattern 2 (District Systems): {pattern_2_count}")
    if no_match_count > 0:
        print(f"  - No pattern matched: {no_match_count}")
    print(f"\n  - Pattern matching success rate: {success_rate:.1f}% ({matched_count}/{total})")

    # ========================================================================
    # Summary
    # ========================================================================
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")

Author: Mingchen Li
    print(f"""
  Pattern 1 (Boiler System): Primary Loop + Secondary Loop + Boiler(s)
  Pattern 2 (District System): Secondary Loop only, no Boiler
  
  ✓ Successfully validated {total} buildings:
    - {pattern_1_count} Boiler Systems
    - {pattern_2_count} District Systems
    - Pattern matching success rate: {success_rate:.1f}%
""")


if __name__ == "__main__":
    main()

