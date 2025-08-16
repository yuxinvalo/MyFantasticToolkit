# -*- coding: utf-8 -*-
"""
HSBC Little Worker - Configuration Manager
Centralized configuration loading and management utility
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from utils.logger import logger


class ConfigurationManager:
    """Centralized configuration manager for the application"""
    
    @staticmethod
    def _get_resource_path(relative_path: str) -> str:
        """Get absolute path to resource, works for dev and for PyInstaller"""
        if getattr(sys, 'frozen', False):
            # PyInstaller bundle
            base_path = Path(sys.executable).parent
        else:
            # Development
            base_path = Path(__file__).parent.parent
        
        return str(base_path / relative_path)
    
    @staticmethod
    def load_json_config(config_path: str, defaults: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Load JSON configuration with fallback to defaults
        
        Args:
            config_path: Path to the configuration file
            defaults: Default configuration to use if file doesn't exist or is invalid
        
        Returns:
            Configuration dictionary
        """
        if defaults is None:
            defaults = {}
        
        try:
            full_path = ConfigurationManager._get_resource_path(config_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info(f"Loaded configuration from {full_path}")
                    return config
            else:
                logger.warning(f"Configuration file not found: {full_path}, using defaults")
                return defaults
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading configuration from {config_path}: {e}")
            return defaults
    
    @staticmethod
    def save_json_config(config_path: str, data: Dict[str, Any]) -> bool:
        """
        Save configuration to JSON file
        
        Args:
            config_path: Path to save the configuration
            data: Configuration data to save
        
        Returns:
            True if successful, False otherwise
        """
        try:
            full_path = ConfigurationManager._get_resource_path(config_path)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved configuration to {full_path}")
            return True
        except (IOError, TypeError) as e:
            logger.error(f"Error saving configuration to {config_path}: {e}")
            return False
    
    @staticmethod
    def load_app_config() -> Dict[str, Any]:
        """Load main application configuration"""
        defaults = {
            "language": "zh_CN",
            "theme": "light",
            "window": {
                "width": 800,
                "height": 600,
                "maximized": False
            }
        }
        return ConfigurationManager.load_json_config("config/app_config.json", defaults)
    
    @staticmethod
    def load_plugin_config(plugin_name: str) -> Dict[str, Any]:
        """Load plugin-specific configuration"""
        config_path = f"plugins/{plugin_name}/config.json"
        return ConfigurationManager.load_json_config(config_path, {})