"""
Analytics module

Contains various hot water system analysis applications

Usage:
    from hhw_brick.analytics import apps

    # List available apps
    app_list = apps.list_apps()

    # Load an app
    app = apps.load_app("secondary_loop_temp_diff")

    # Use the app
    qualified, result = app.qualify(brick_model_path)


Author: Mingchen Li
"""

from .apps_manager import apps, AppsManager

__all__ = ["apps", "AppsManager"]
