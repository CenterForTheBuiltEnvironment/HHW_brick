"""
Example 8: Batch Run Application

Demonstrates how to run an application on multiple buildings at once.

Workflow:
1. Load application
2. Find all qualified buildings
3. Configure application
4. Run analysis on all qualified buildings
5. Generate summary report
"""

from pathlib import Path
from hhw_brick import apps


def main():
    print("Example 8: Batch Run Application")
    print("=" * 60)

    # Setup paths
    fixtures = Path(__file__).parent.parent / "tests" / "fixtures"
    brick_model_dir = fixtures / "Brick_Model_File"
    timeseries_dir = fixtures / "TimeSeriesData"

    # ========================================================================
    # Step 1: Load Application
    # ========================================================================
    print(f"\nStep 1: Load Application")
    print("-" * 60)

    app_name = "primary_loop_temp_diff"
    app = apps.load_app(app_name)
    print(f"✓ {app_name}")

    # ========================================================================
    # Step 2: Find Qualified Buildings
    # Check which buildings qualify for this application
    # ========================================================================
    print(f"\nStep 2: Find Qualified Buildings")
    print("-" * 60)

    # Use apps.qualify_buildings to check all buildings at once
    batch_results = apps.qualify_buildings(str(brick_model_dir), verbose=False)

    # Filter qualified buildings for this specific app
    qualified_buildings = []
    for building in batch_results:
        for r in building['results']:
            if r['app'] == app_name and r['qualified']:
                # Extract building number from filename
                building_name = Path(building['model']).stem
                building_number = building_name.split('_')[1]
                qualified_buildings.append({
                    'number': building_number,
                    'model': building['model'],
                    'details': r['details']
                })
                break

    print(f"✓ Found {len(qualified_buildings)} qualified building(s):")
    for b in qualified_buildings:
        print(f"    Building {b['number']}")

    if not qualified_buildings:
        print(f"✗ No qualified buildings found")
        return

    # ========================================================================
    # Step 3: Configure Application
    # ========================================================================
    print(f"\nStep 3: Configure Application")
    print("-" * 60)

    # Get default configuration
    config = apps.get_default_config(app_name)

    # Customize for batch processing
    config['output']['generate_plots'] = True
    config['output']['save_results'] = True
    print(f"✓ Configuration ready")
    print(f"  Generate plots: {config['output']['generate_plots']}")

    # ========================================================================
    # Step 4: Run Analysis on All Buildings
    # ========================================================================
    print(f"\nStep 4: Run Batch Analysis")
    print("-" * 60)

    analysis_results = []

    for b in qualified_buildings:
        building_number = b['number']
        model_file = b['model']

        # Match timeseries data by building number
        data_file = timeseries_dir / f"{building_number}hhw_system_data.csv"

        if not data_file.exists():
            print(f"  ⚠️  Building {building_number}: No timeseries data, skipping")
            continue

        # Set output directory for this building
        config['output']['output_dir'] = str(fixtures / "analysis_output" / f"building_{building_number}")

        print(f"  Analyzing Building {building_number}...")

        # Run analysis with suppressed output
        import sys, io
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()

        try:
            results = app.analyze(str(model_file), str(data_file), config)
            sys.stdout = old_stdout

            if results:
                analysis_results.append({
                    'building': building_number,
                    'status': 'success',
                    'stats': results['stats']
                })
                print(f"    ✓ Complete - Mean ΔT: {results['stats']['mean_temp_diff']:.2f}°C")
            else:
                analysis_results.append({
                    'building': building_number,
                    'status': 'failed'
                })
                print(f"    ✗ Failed")

        except Exception as e:
            sys.stdout = old_stdout
            analysis_results.append({
                'building': building_number,
                'status': 'error',
                'error': str(e)
            })
            print(f"    ✗ Error: {e}")

    # ========================================================================
    # Step 5: Generate Summary Report
    # ========================================================================
    print(f"\nStep 5: Summary Report")
    print("-" * 60)

    successful = [r for r in analysis_results if r['status'] == 'success']
    failed = [r for r in analysis_results if r['status'] != 'success']

    print(f"\nBatch Analysis Results:")
    print(f"  Total buildings: {len(qualified_buildings)}")
    print(f"  Successful: {len(successful)}")
    print(f"  Failed: {len(failed)}")

    if successful:
        print(f"\nSuccessful analyses:")
        for r in successful:
            stats = r['stats']
            print(f"  Building {r['building']}:")
            print(f"    Data points: {stats['count']:,}")
            print(f"    Mean ΔT: {stats['mean_temp_diff']:.2f}°C")
            print(f"    Range: [{stats['min_temp_diff']:.2f}, {stats['max_temp_diff']:.2f}]°C")

    # ========================================================================
    # Summary
    # ========================================================================
    print(f"\n{'='*60}")
    print(f"Complete!")
    print(f"  Application: {app_name}")
    print(f"  Buildings analyzed: {len(successful)}/{len(qualified_buildings)}")
    print(f"  Results location: {fixtures / 'analysis_output'}")
    print(f"\n💡 Tip: Check analysis_output/building_XX/ for individual results")


if __name__ == "__main__":
    main()

