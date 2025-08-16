# -*- coding: utf-8 -*-
"""
HSBC Little Worker - Path Manager
Centralized path resolution utility for the application
"""

import os
import sys
from pathlib import Path
from typing import Union, Optional


class PathManager:
    """Centralized path management for the application"""
    
    _base_path: Optional[Path] = None
    
    @classmethod
    def get_base_path(cls) -> Path:
        """Get the base path of the application"""
        if cls._base_path is None:
            if getattr(sys, 'frozen', False):
                # PyInstaller bundle
                cls._base_path = Path(sys.executable).parent
            else:
                # Development environment
                cls._base_path = Path(__file__).parent.parent
        return cls._base_path
    
    @classmethod
    def get_resource_path(cls, relative_path: Union[str, Path]) -> Path:
        """
        Get absolute path to resource, works for dev and PyInstaller
        
        Args:
            relative_path: Path relative to the application base
        
        Returns:
            Absolute Path object
        """
        return cls.get_base_path() / relative_path
    
    @classmethod
    def get_config_path(cls, config_name: str) -> Path:
        """Get path to configuration file"""
        return cls.get_resource_path("config") / config_name
    
    @classmethod
    def get_plugin_path(cls, plugin_name: str) -> Path:
        """Get path to plugin directory"""
        return cls.get_resource_path("plugins") / plugin_name
    
    @classmethod
    def get_plugin_config_path(cls, plugin_name: str) -> Path:
        """Get path to plugin configuration file"""
        return cls.get_plugin_path(plugin_name) / "config.json"
    
    @classmethod
    def get_translations_path(cls, relative_path: str = "") -> Path:
        """Get path to translations directory"""
        return cls.get_resource_path("resources/translations") / relative_path
    
    @classmethod
    def get_plugin_translations_path(cls, plugin_name: str, relative_path: str = "") -> Path:
        """Get path to plugin translations directory"""
        return cls.get_plugin_path(plugin_name) / "translations" / relative_path
    
    @classmethod
    def get_logs_path(cls) -> Path:
        """Get path to logs directory"""
        return cls.get_resource_path("logs")
    
    @classmethod
    def ensure_directory_exists(cls, path: Union[str, Path]) -> Path:
        """
        Ensure a directory exists, creating it if necessary
        
        Args:
            path: Directory path to ensure exists
        
        Returns:
            Path object for the directory
        """
        path_obj = Path(path) if isinstance(path, str) else path
        path_obj.mkdir(parents=True, exist_ok=True)
        return path_obj