"""
Analytics Apps Manager

Provides a simple interface to discover and load analytics apps.


Author: Mingchen Li
"""

import importlib
from pathlib import Path
from typing import List, Dict, Optional, Any
import yaml


class AppsManager:
    """
    Manager for analytics apps - provides easy discovery and loading.

    Usage:
        from hhw_brick.analytics import apps

        # List available apps
        available = apps.list_apps()

        # Load an app
        app = apps.load_app("secondary_loop_temp_diff")

        # Get app config
        config = apps.get_default_config("secondary_loop_temp_diff")
    """

    def __init__(self):
        """Initialize the apps manager."""
        # Applications are in the same directory as this manager
        self.apps_dir = Path(__file__).parent
        self._app_cache = {}

    def list_apps(self) -> List[Dict[str, str]]:
        """
        List all available analytics apps.

        Returns:
            List of dicts with app info: [{'name': ..., 'description': ...}, ...]
        """
        apps = []

        if not self.apps_dir.exists():
            return apps

        # Scan apps directory
        for app_path in self.apps_dir.iterdir():
            if app_path.is_dir() and not app_path.name.startswith('_'):
                # Check if app.py exists
                app_file = app_path / "app.py"
                if app_file.exists():
                    # Try to get description from __init__.py or app.py
                    description = self._get_app_description(app_path)
                    apps.append({
                        'name': app_path.name,
                        'description': description,
                        'path': str(app_path)
                    })

        return apps

    def load_app(self, app_name: str) -> Any:
        """
        Load an analytics app by name.

        Args:
            app_name: Name of the app (e.g., "secondary_loop_temp_diff")

        Returns:
            The app module with qualify() and analyze() functions

        Example:
            app = apps.load_app("secondary_loop_temp_diff")
            qualified, result = app.qualify(brick_model_path)
            if qualified:
                analysis = app.analyze(brick_model_path, data_path, config)
        """
        # Check cache
        if app_name in self._app_cache:
            return self._app_cache[app_name]

        try:
            # Import the app module
            module_path = f"hhw_brick.applications.{app_name}.app"
            app_module = importlib.import_module(module_path)

            # Cache it
            self._app_cache[app_name] = app_module

            return app_module

        except ImportError as e:
            raise ImportError(f"App '{app_name}' not found or could not be loaded: {e}")

    def get_default_config(self, app_name: str) -> Dict[str, Any]:
        """
        Get default configuration for an app.

        Args:
            app_name: Name of the app

        Returns:
            Default configuration dictionary
        """
        app_path = self.apps_dir / app_name

        # Try to load config from app's load_config function
        try:
            app = self.load_app(app_name)
            if hasattr(app, 'load_config'):
                return app.load_config()
        except:
            pass

        # Return basic default config
        return {
            'analysis': {},
            'output': {
                'save_results': True,
                'output_dir': './results',
                'generate_plots': True
            }
        }

    def get_app_info(self, app_name: str) -> Dict[str, Any]:
        """
        Get detailed information about an app.

        Args:
            app_name: Name of the app

        Returns:
            Dict with app information (functions, description, etc.)
        """
        try:
            app = self.load_app(app_name)

            info = {
                'name': app_name,
                'description': self._get_app_description(self.apps_dir / app_name),
                'functions': []
            }

            # Check if app defines __all__ for core functions
            # Otherwise fallback to common core functions
            if hasattr(app, '__all__'):
                core_functions = app.__all__
            else:
                # Default core functions if app doesn't define __all__
                core_functions = ['qualify', 'analyze', 'load_config']

            # List only core user-facing functions
            for attr_name in core_functions:
                if hasattr(app, attr_name):
                    attr = getattr(app, attr_name)
                    if callable(attr):
                        info['functions'].append({
                            'name': attr_name,
                            'doc': attr.__doc__ or 'No description'
                        })

            return info

        except Exception as e:
            return {'error': str(e)}

    def _get_app_description(self, app_path: Path) -> str:
        """Extract app description from __init__.py or app.py."""
        # Try __init__.py first
        init_file = app_path / "__init__.py"
        if init_file.exists():
            try:
                with open(init_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Look for docstring
                    in_docstring = False
                    for line in lines[:10]:
                        if '"""' in line or "'''" in line:
                            if not in_docstring:
                                in_docstring = True
                                desc = line.strip().replace('"""', '').replace("'''", '').strip()
                                if desc:
                                    return desc
                            else:
                                return line.strip().replace('"""', '').replace("'''", '').strip()
            except:
                pass

        # Try app.py
        app_file = app_path / "app.py"
        if app_file.exists():
            try:
                with open(app_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines[:20]:
                        if line.strip() and not line.strip().startswith('#'):
                            if '"""' in line or "'''" in line:
                                return line.strip().replace('"""', '').replace("'''", '').strip()
            except:
                pass

        return "No description available"

    def qualify_building(self, brick_model_path: str, verbose: bool = False) -> Dict[str, Any]:
        """
        Check if a building qualifies for all available applications.

        Args:
            brick_model_path: Path to Brick model file
            verbose: If False, suppress app's internal output (default: False)

        Returns:
            Dict with qualify results for each app

        Example:
            results = apps.qualify_building("building_29.ttl")
            for r in results['results']:
                if r['qualified']:
                    print(f"{r['app']}: Qualified")
        """
        import sys
        import io

        available_apps = self.list_apps()
        results = []

        for app_info in available_apps:
            app_name = app_info['name']
            try:
                # Load app
                app = self.load_app(app_name)

                # Check if app has qualify function
                if hasattr(app, 'qualify'):
                    # Suppress output if not verbose
                    if not verbose:
                        old_stdout = sys.stdout
                        sys.stdout = io.StringIO()

                    try:
                        qualified, details = app.qualify(brick_model_path)
                    finally:
                        if not verbose:
                            sys.stdout = old_stdout

                    results.append({
                        'app': app_name,
                        'qualified': qualified,
                        'details': details if qualified else None
                    })
                else:
                    results.append({
                        'app': app_name,
                        'qualified': None,
                        'details': None
                    })
            except Exception as e:
                if not verbose and 'old_stdout' in locals():
                    sys.stdout = old_stdout  # Restore in case of error
                results.append({
                    'app': app_name,
                    'qualified': False,
                    'details': None,
                    'error': str(e)
                })

        return {
            'model': brick_model_path,
            'results': results
        }

    def qualify_buildings(self, brick_model_dir: str, verbose: bool = False) -> List[Dict[str, Any]]:
        """
        Check multiple buildings against all available applications.

        Args:
            brick_model_dir: Directory containing Brick model files (.ttl)
            verbose: If False, suppress app's internal output (default: False)

        Returns:
            List of qualify results for each building

        Example:
            results = apps.qualify_buildings("path/to/models/")
            for building in results:
                print(f"Building: {building['model']}")
                for r in building['results']:
                    print(f"  {r['app']}: {r['qualified']}")
        """
        import os

        results = []

        # Find all TTL files
        if os.path.isdir(brick_model_dir):
            for file in os.listdir(brick_model_dir):
                if file.endswith('.ttl'):
                    model_path = os.path.join(brick_model_dir, file)
                    result = self.qualify_building(model_path, verbose=verbose)
                    results.append(result)

        return results
# Create singleton instance
apps = AppsManager()

# Export for easy access
__all__ = ['apps', 'AppsManager']
