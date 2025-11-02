"""
Configuration management utilities for HHW Brick


Author: Mingchen Li
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """
    Simple configuration manager for HHW Brick.

    Supports loading configuration from JSON or YAML files.
    """

    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize configuration.

        Args:
            config_dict: Optional dictionary of configuration values
        """
        self._config = config_dict or {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key (supports dot notation like 'section.key')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split(".")
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Get the full configuration as a dictionary.

        Returns:
            Configuration dictionary
        """
        return self._config.copy()


def load_config(config_file: str) -> Config:
    """
    Load configuration from a JSON or YAML file.

    Args:
        config_file: Path to configuration file (.json or .yaml/.yml)

    Returns:
        Config instance

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If file format is not supported
    """
    config_path = Path(config_file)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    suffix = config_path.suffix.lower()

    if suffix == ".json":
        with open(config_path, "r", encoding="utf-8") as f:
            config_dict = json.load(f)
    elif suffix in [".yaml", ".yml"]:
        try:
            import yaml

            with open(config_path, "r", encoding="utf-8") as f:
                config_dict = yaml.safe_load(f)
        except ImportError:
            raise ImportError(
                "PyYAML is required to load YAML configuration files. "
                "Install it with: pip install pyyaml"
            )
    else:
        raise ValueError(f"Unsupported configuration file format: {suffix}")

    return Config(config_dict)
