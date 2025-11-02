"""
Example 7: Run Application

Demonstrates how to run an analytics application on building data.

Quick 4-step workflow:
1. Load application
2. Qualify building
3. Configure settings
4. Run analysis and view results
"""

from pathlib import Path
from hhw_brick import apps
import yaml


def main():
    print("Example 7: Run Application")
    print("=" * 60)

    # Setup paths
    fixtures = Path(__file__).parent.parent / "tests" / "fixtures"

    # Select building number (available: 29, 34, 37, 38, 40)
    building_number = "29"

    # Auto-match Brick model and timeseries data by building number
    model_file = fixtures / "Brick_Model_File" / f"building_{building_number}_district_hw_z.ttl"
    data_file = fixtures / "TimeSeriesData" / f"{building_number}hhw_system_data.csv"

    # ========================================================================
    # Step 1: Load Application
    # ========================================================================
    print(f"\nStep 1: Load Application")
    print("-" * 60)

    app_name = "secondary_loop_temp_diff"
    app = apps.load_app(app_name)
    print(f"✓ {app_name}")

    # ========================================================================
    # Step 2: Qualify Building
    # Check if building has required sensors for this application
    # ========================================================================
    print(f"\nStep 2: Qualify Building")
    print("-" * 60)

    # Use apps.qualify_building with verbose=False for clean output
    result = apps.qualify_building(str(model_file), verbose=False)

    # Check qualification result
    qualified = False
    for r in result["results"]:
        if r["app"] == app_name and r["qualified"]:
            qualified = True
            print(f"✓ Building {building_number} qualified")
            print(f"  Required sensors found:")
            print(f"    Loop: {r['details']['loop'].split('#')[-1]}")
            print(f"    Supply: {r['details']['supply'].split('#')[-1]}")
            print(f"    Return: {r['details']['return'].split('#')[-1]}")
            break

    if not qualified:
        print(f"✗ Not qualified")
        return

    # ========================================================================
    # Step 3: Configure Application
    # Get default config and customize as needed
    # ========================================================================
    print(f"\nStep 3: Configure Application")
    print("-" * 60)

    # Get default configuration template
    config = apps.get_default_config(app_name)

    # Save config template for users to edit
    config_file = fixtures / f"{app_name}_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    print(f"✓ Config template saved: {config_file.name}")

    # Customize configuration (or edit the YAML file directly)
    config["output"]["output_dir"] = str(fixtures / "analysis_output")
    config["output"]["generate_plots"] = True
    print(f"✓ Output directory: {config['output']['output_dir']}")

    # ========================================================================
    # Step 4: Run Analysis
    # Execute analysis with timeseries data
    # ========================================================================
    print(f"\nStep 4: Run Analysis")
    print("-" * 60)

    print(f"Running analysis...")
    print(f"  Building: {building_number}")
    print(f"  Data: {data_file.name}")

    # Run analysis with suppressed verbose output
    import sys, io

    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    results = app.analyze(str(model_file), str(data_file), config)
    sys.stdout = old_stdout

    # Display analysis results
    if results:
        stats = results["stats"]
        print(f"\n✓ Analysis complete!")
        print(f"  Data points: {stats['count']:,}")
        print(f"  Mean ΔT: {stats['mean_temp_diff']:.2f}°C")
        print(f"  Range: [{stats['min_temp_diff']:.2f}, {stats['max_temp_diff']:.2f}]°C")

        # Show generated files
        output_dir = Path(config["output"]["output_dir"])
        files = list(output_dir.glob("*"))
        print(f"\n✓ Generated {len(files)} file(s):")
        for f in sorted(files):
            icon = "📊" if f.suffix == ".png" else "📄"
            print(f"    {icon} {f.name}")

    # ========================================================================
    # Summary
    # ========================================================================
    print(f"\n{'='*60}")
    print(f"Complete!")
    print(f"  Application: {app_name}")
    print(f"  Building: {building_number}")
    print(f"  Config: {config_file.name}")
    print(f"  Results: {config['output']['output_dir']}")
    print(f"\n💡 Tip: Change building_number at line 23 to analyze other buildings")


if __name__ == "__main__":
    main()
