"""
Primary Loop Temperature Differential Analysis Application

Analyzes temperature differential between supply and return water in primary loops
of hot water systems with boilers.


Author: Mingchen Li
"""

from .app import qualify, analyze, load_config

__all__ = ['qualify', 'analyze', 'load_config']

# Application metadata
__app_name__ = "primary_loop_temp_diff"
__version__ = "1.0.0"
__description__ = "Primary Loop Temperature Differential Analysis"
__author__ = "HHW Brick"

