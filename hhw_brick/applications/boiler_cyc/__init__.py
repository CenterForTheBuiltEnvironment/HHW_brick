"""
Boiler Short Cycling Analysis Application

Analyzes boiler system data to identify short cycling behavior based on supply and return temperature or boiler firing rate.


Author: Aoyu Zou
"""

from .app import qualify, run_hwst_analysis, run_fire_analysis, load_config

__all__ = ["qualify", "run_hwst_analysis", "run_fire_analysis", "load_config"]

# Application metadata
__app_name__ = "boiler_cyc"
__version__ = "1.0.0"
__description__ = "Boiler System Cycle Analysis"
__author__ = "HHW Brick"
