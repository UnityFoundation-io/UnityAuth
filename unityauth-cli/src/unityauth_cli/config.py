"""Configuration management for UnityAuth CLI.

Handles loading and saving configuration from YAML files.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from unityauth_cli.utils.errors import ConfigurationError


class Configuration:
    """Manages CLI configuration settings.

    Configuration is stored in a YAML file at:
    - Linux/macOS: ~/.config/unityauth-cli/config.yml
    - Windows: %APPDATA%/unityauth-cli/config.yml
    """

    DEFAULT_CONFIG = {
        'api_url': None,
        'api_version': '1.0',
        'default_format': 'table',
        'timeout': 30,
        'batch': {
            'max_size': 1000,
            'continue_on_error': True,
            'delay_ms': 0,
        },
        'output': {
            'show_headers': True,
            'table_style': 'grid',
            'color_enabled': True,
        }
    }

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """Initialize configuration.

        Args:
            config_path: Optional custom config file path. If None, uses default location.
        """
        if config_path is None:
            config_path = self._get_default_config_path()

        self.config_path = config_path
        self.config: Dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self.load()

    @staticmethod
    def _get_default_config_path() -> Path:
        """Get the default configuration file path for the current OS."""
        if os.name == 'nt':  # Windows
            config_dir = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
        else:  # Linux/macOS
            config_dir = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))

        return config_dir / 'unityauth-cli' / 'config.yml'

    def load(self) -> None:
        """Load configuration from file.

        If the file doesn't exist, uses default configuration.
        """
        if not self.config_path.exists():
            return

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f) or {}
                # Merge with defaults (preserve defaults for missing keys)
                self._deep_merge(self.config, loaded_config)
        except (yaml.YAMLError, IOError) as e:
            raise ConfigurationError(f"Failed to load configuration from {self.config_path}: {e}")

    def save(self) -> None:
        """Save current configuration to file.

        Creates the config directory if it doesn't exist.
        """
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(self.config, f, default_flow_style=False, sort_keys=False)
        except IOError as e:
            raise ConfigurationError(f"Failed to save configuration to {self.config_path}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key (supports dot notation, e.g., 'batch.max_size')
            default: Default value if key doesn't exist

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key (supports dot notation, e.g., 'batch.max_size')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config

        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]

        # Set the final value
        config[keys[-1]] = value

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Deep merge override dictionary into base dictionary.

        Args:
            base: Base dictionary to merge into
            override: Dictionary with values to override
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
