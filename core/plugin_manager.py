# -*- coding: utf-8 -*-
"""
HSBC Little Worker - 插件管理器
"""

import os
import sys
import json
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Any

from PySide6.QtCore import QObject, Signal

from .plugin_base import PluginBase
from utils.logger import logger
from core.i18n import tr, i18n_manager


class PluginManager(QObject):
    """插件管理器类"""
    
    # 信号定义
    plugin_loaded = Signal(str)  # 插件加载信号
    plugin_unloaded = Signal(str)  # 插件卸载信号
    plugin_error = Signal(str, str)  # 插件错误信号 (plugin_name, error_message)
    
    def __init__(self, app=None):
        super().__init__()
        
        self.app = app
        self.plugins: Dict[str, PluginBase] = {}  # 已加载的插件实例
        self.plugin_configs: Dict[str, Dict] = {}  # 插件配置
        
        # 插件目录路径
        self.plugins_dir = Path(__file__).parent.parent / "plugins"
        self.config_file = Path(__file__).parent.parent / "config" / "plugin_config.json"
        
        # 确保目录存在
        self.plugins_dir.mkdir(exist_ok=True)
        self.config_file.parent.mkdir(exist_ok=True)
        
        # 加载插件配置
        self._load_plugin_config()
    
    def _load_plugin_config(self):
        """加载插件配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.plugin_configs = json.load(f)
            else:
                # 创建默认配置
                self.plugin_configs = {
                    "enabled_plugins": [],
                    "plugin_settings": {}
                }
                self._save_plugin_config()
            
            logger.debug(f"📋 Plugin config loaded: {len(self.plugin_configs.get('enabled_plugins', []))} enabled plugins")
            
        except Exception as e:
            logger.error(f"❌ Failed to load plugin config: {e}")
            self.plugin_configs = {
                "enabled_plugins": [],
                "plugin_settings": {}
            }
    
    def _save_plugin_config(self):
        """保存插件配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.plugin_configs, f, indent=2, ensure_ascii=False)
            

            
        except Exception as e:
            logger.error(f"❌ Failed to save plugin config: {e}")
    
    def discover_plugins(self) -> List[Dict[str, Any]]:
        """发现可用插件"""
        available_plugins = []
        
        try:
            # 遍历插件目录
            for plugin_dir in self.plugins_dir.iterdir():
                if not plugin_dir.is_dir() or plugin_dir.name.startswith('_'):
                    continue
                
                # 查找插件主文件
                plugin_file = plugin_dir / "__init__.py"
                if not plugin_file.exists():
                    continue
                
                # 尝试读取插件信息
                plugin_info = self._get_plugin_info(plugin_dir)
                if plugin_info:
                    available_plugins.append(plugin_info)
            
            logger.info(f"🔍 Discovered {len(available_plugins)} available plugins")
            
        except Exception as e:
            logger.error(f"❌ Error discovering plugins: {e}")
        
        return available_plugins
    
    def _get_plugin_info(self, plugin_dir: Path) -> Optional[Dict[str, Any]]:
        """获取插件信息"""
        try:
            plugin_name = plugin_dir.name
            
            # 首先尝试从本地配置文件读取插件信息
            config_file = plugin_dir / "config.json"
            plugin_config = {}
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        plugin_config = json.load(f)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load config for {plugin_name}: {e}")
            
            # 尝试导入插件模块获取元信息
            spec = importlib.util.spec_from_file_location(
                f"plugins.{plugin_name}",
                plugin_dir / "__init__.py"
            )
            
            if spec is None or spec.loader is None:
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 获取插件类
            plugin_class = getattr(module, 'Plugin', None)
            if plugin_class is None or not issubclass(plugin_class, PluginBase):
                logger.warning(f"⚠️ Plugin {plugin_name} has no valid Plugin class")
                return None
            
            # 获取插件元信息，优先使用本地配置
            plugin_info_config = plugin_config.get('plugin_info', {})
            
            plugin_info = {
                'name': plugin_name,
                'display_name': plugin_info_config.get('display_name', getattr(plugin_class, 'DISPLAY_NAME', plugin_name)),
                'description': plugin_info_config.get('description', getattr(plugin_class, 'DESCRIPTION', '')),
                'version': plugin_info_config.get('version', getattr(plugin_class, 'VERSION', '1.0.0')),
                'author': plugin_info_config.get('author', getattr(plugin_class, 'AUTHOR', '')),
                'enabled': plugin_info_config.get('enabled', plugin_name in self.plugin_configs.get('enabled_plugins', [])),
                'path': str(plugin_dir),
                'class': plugin_class,
                'has_local_config': config_file.exists()
            }
            
            return plugin_info
            
        except Exception as e:
            logger.error(f"❌ Failed to get plugin info for {plugin_dir.name}: {e}")
            return None
    
    def load_plugins(self):
        """加载所有启用的插件"""
        enabled_plugins = self.plugin_configs.get('enabled_plugins', [])
        
        if not enabled_plugins:
            logger.info("📦 No enabled plugins found")
            return
        
        logger.info(f"🚀 Loading {len(enabled_plugins)} plugins...")
        
        for plugin_name in enabled_plugins:
            self.load_plugin(plugin_name)
    
    def load_plugin(self, plugin_name: str) -> bool:
        """加载指定插件"""
        if plugin_name in self.plugins:
            logger.warning(f"⚠️ Plugin {plugin_name} already loaded")
            return True
        
        try:
            plugin_dir = self.plugins_dir / plugin_name
            if not plugin_dir.exists():
                logger.error(f"❌ Plugin directory not found: {plugin_dir}")
                return False
            
            # 导入插件模块
            spec = importlib.util.spec_from_file_location(
                f"plugins.{plugin_name}",
                plugin_dir / "__init__.py"
            )
            
            if spec is None or spec.loader is None:
                logger.error(f"❌ Cannot load plugin module: {plugin_name}")
                return False
            
            module = importlib.util.module_from_spec(spec)
            
            # 添加到sys.modules以支持相对导入
            sys.modules[f"plugins.{plugin_name}"] = module
            
            spec.loader.exec_module(module)
            
            # 获取插件类
            plugin_class = getattr(module, 'Plugin', None)
            if plugin_class is None:
                logger.error(f"❌ Plugin {plugin_name} has no Plugin class")
                return False
            
            # 创建插件实例
            plugin_instance = plugin_class(self.app)
            
            # 验证插件实例
            if not isinstance(plugin_instance, PluginBase):
                logger.error(f"❌ Plugin {plugin_name} is not a subclass of PluginBase")
                return False
            
            # 注册插件翻译
            plugin_dir = os.path.join(self.plugins_dir, plugin_name)
            translations_dir = os.path.join(plugin_dir, 'translations')
            if os.path.exists(translations_dir):
                i18n_manager.register_plugin_translations(plugin_name, translations_dir)
                logger.info(f"[插件管理器] 🌐 插件 {plugin_name} 翻译文件已注册")
            
            # 初始化插件
            plugin_instance.initialize()
            
            # 存储插件实例
            self.plugins[plugin_name] = plugin_instance
            
            # 注册插件到主窗口
            if self.app and hasattr(self.app, 'get_main_window'):
                main_window = self.app.get_main_window()
                if main_window:
                    # 添加插件按钮
                    main_window.add_plugin_button(
                        plugin_name,
                        plugin_instance.get_display_name(),
                        plugin_instance.get_description()
                    )
                    
                    # 连接插件界面请求信号（只连接一次）
                    if not hasattr(self, '_signal_connected'):
                        main_window.plugin_widget_requested.connect(
                            self._handle_plugin_widget_request
                        )
                        self._signal_connected = True
            
            logger.info(f"✅ Plugin loaded successfully: {plugin_name}")
            self.plugin_loaded.emit(plugin_name)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load plugin {plugin_name}: {e}")
            self.plugin_error.emit(plugin_name, str(e))
            return False
    
    def _handle_plugin_widget_request(self, plugin_name: str):
        """处理插件界面请求"""
        if plugin_name not in self.plugins:
            logger.warning(f"⚠️ Requested plugin not loaded: {plugin_name}")
            return
        
        try:
            plugin = self.plugins[plugin_name]
            widget = plugin.get_widget()
            
            if widget and self.app and hasattr(self.app, 'get_main_window'):
                main_window = self.app.get_main_window()
                if main_window:
                    main_window.add_plugin_widget(
                        plugin_name,
                        plugin.get_display_name(),
                        widget
                    )
            
        except Exception as e:
            logger.error(f"❌ Failed to get plugin widget for {plugin_name}: {e}")
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """卸载指定插件"""
        if plugin_name not in self.plugins:
            logger.warning(f"⚠️ Plugin {plugin_name} not loaded")
            return True
        
        try:
            plugin = self.plugins[plugin_name]
            
            # 清理插件
            plugin.cleanup()
            
            # 从插件字典中移除
            del self.plugins[plugin_name]
            
            # 从sys.modules中移除
            module_name = f"plugins.{plugin_name}"
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            logger.info(f"🗑️ Plugin unloaded successfully: {plugin_name}")
            self.plugin_unloaded.emit(plugin_name)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """启用插件"""
        enabled_plugins = self.plugin_configs.get('enabled_plugins', [])
        
        if plugin_name not in enabled_plugins:
            enabled_plugins.append(plugin_name)
            self.plugin_configs['enabled_plugins'] = enabled_plugins
            self._save_plugin_config()
            
            # 立即加载插件
            return self.load_plugin(plugin_name)
        
        return True
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """禁用插件"""
        enabled_plugins = self.plugin_configs.get('enabled_plugins', [])
        
        if plugin_name in enabled_plugins:
            enabled_plugins.remove(plugin_name)
            self.plugin_configs['enabled_plugins'] = enabled_plugins
            self._save_plugin_config()
            
            # 卸载插件
            return self.unload_plugin(plugin_name)
        
        return True
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """获取插件实例"""
        return self.plugins.get(plugin_name)
    
    def get_loaded_plugins(self) -> Dict[str, PluginBase]:
        """获取所有已加载的插件"""
        return self.plugins.copy()
    
    def get_plugin_setting(self, plugin_name: str, key: str, default=None):
        """获取插件设置"""
        plugin_settings = self.plugin_configs.get('plugin_settings', {})
        return plugin_settings.get(plugin_name, {}).get(key, default)
    
    def set_plugin_setting(self, plugin_name: str, key: str, value):
        """设置插件设置"""
        if 'plugin_settings' not in self.plugin_configs:
            self.plugin_configs['plugin_settings'] = {}
        
        if plugin_name not in self.plugin_configs['plugin_settings']:
            self.plugin_configs['plugin_settings'][plugin_name] = {}
        
        self.plugin_configs['plugin_settings'][plugin_name][key] = value
        self._save_plugin_config()
    
    def cleanup(self):
        """清理插件管理器"""
        logger.info("🧹 Cleaning up plugin manager...")
        
        # 卸载所有插件
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)
        
        logger.info("✨ Plugin manager cleanup completed")