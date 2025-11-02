"""
Example 6: Application Management

Demonstrates how to discover and manage applications.

What you'll learn:
- List all available applications (secondary_loop_temp_diff, primary_loop_temp_diff)
- View application capabilities
- Batch check which buildings qualify for which apps
- Identify which buildings can use which applications
"""

from pathlib import Path
from hhw_brick import apps


def main():
    print("Example 6: Application Management")
    print("=" * 60)

    # Part 1: Discover Applications
    print(f"\nPart 1: Discover Applications")
    print("-" * 60)

    available_apps = apps.list_apps()
    print(f"Found {len(available_apps)} application(s):\n")
    for app_info in available_apps:
        print(f"  • {app_info['name']}")
        print(f"    {app_info['description']}")

        # Show core functions
        info = apps.get_app_info(app_info["name"])
        if info.get("functions"):
            funcs = ", ".join([f["name"] for f in info["functions"]])
            print(f"    Functions: {funcs}")
        print()

    if not available_apps:
        print("No applications available.")
        return

    # Part 2: Batch Qualification Matrix
    print(f"Part 2: Building Qualification Matrix")
    print("-" * 60)

    # Check all buildings against all applications
    fixtures = Path(__file__).parent.parent / "tests" / "fixtures"
    brick_model_dir = fixtures / "Brick_Model_File"

    if not brick_model_dir.exists():
        print(f"✗ Model directory not found. Run Example 1 first.")
        return

    print(f"Checking which buildings qualify for which applications...\n")
    batch_results = apps.qualify_buildings(str(brick_model_dir))

    # Build qualification matrix
    app_matrix = {}  # app -> list of qualified buildings
    building_matrix = {}  # building -> list of qualified apps

    for building in batch_results:
        building_name = Path(building["model"]).stem
        building_matrix[building_name] = []

        for r in building["results"]:
            app_name = r["app"]

            if app_name not in app_matrix:
                app_matrix[app_name] = []

            if r["qualified"]:
                app_matrix[app_name].append(building_name)
                building_matrix[building_name].append(app_name)

    # Display by application
    print(f"By Application:")
    for app_name, buildings in app_matrix.items():
        print(f"  {app_name}:")
        print(f"    Qualified: {len(buildings)}/{len(batch_results)} buildings")
        if buildings:
            for b in buildings[:3]:
                print(f"      ✓ {b}")
            if len(buildings) > 3:
                print(f"      ... and {len(buildings) - 3} more")

    # Display by building
    print(f"\nBy Building (showing first 3):")
    for i, (building_name, apps_list) in enumerate(list(building_matrix.items())[:3]):
        if apps_list:
            print(f"  {building_name}:")
            print(f"    Can run: {', '.join(apps_list)}")
        else:
            print(f"  {building_name}: No applications available")

    if len(building_matrix) > 3:
        print(f"  ... and {len(building_matrix) - 3} more buildings")

    # Summary
    print(f"\n{'='*60}")
    print("Summary:")
    print(f"  ✓ {len(available_apps)} application(s) available")
    print(f"  ✓ {len(batch_results)} building(s) checked")
    print(f"  ✓ Qualification matrix generated")


if __name__ == "__main__":
    main()
