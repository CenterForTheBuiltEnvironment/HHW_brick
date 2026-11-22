"""
Pump Differential Pressure Setpoint Tracking Analysis App

Evaluates how well the secondary-loop pumps hold the end-of-line differential pressure at its
setpoint, by flow bin and by pump operating mode, and characterises the DP setpoint reset.


Author: SheltonXiao
"""

from .app import qualify, analyze, load_config

__all__ = ["qualify", "analyze", "load_config"]

# Application metadata
__app_name__ = "pump_flow_spd_vfd"
__version__ = "1.1.0"
__description__ = "Pump Differential Pressure Setpoint Tracking Analysis"
__author__ = "HHW Brick"
