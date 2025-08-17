# -*- coding: utf-8 -*-
"""
HSBC Little Worker - 插件管理器
"""

import os
import sys
import json
import importlib.util
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Any

from PySide6.QtCore import QObject, Signal

from .plugin_base import PluginBase
from utils.logger import logger
from utils.crypto import decrypt_password, is_password_field
from core.i18n import tr, i18n_manager


class PluginManager(QObject):
    """插件管理器类"""
    
    # 信号定义
    plugin_loaded = Signal(str)  # 插件加载完成信号
    plugin_unloaded = Signal(str)  # 插件卸载完成信号
    plugin_error = Signal(str, str)  # 插件错误信号 (plugin_name, error_message)
    plugin_enabled = Signal(str)  # 插件启用信号
    plugin_disabled = Signal(str)  # 插件禁用信号
    plugin_config_changed = Signal(str, dict)  # 插件配置变更信号 (plugin_name, new_config)
    
    def __init__(self, app):
        super().__init__()
        
        self.app = app
        self.plugins: Dict[str, PluginBase] = {}  # 已加载的插件实例
        # 插件目录路径
        self.plugins_dir = self._get_plugins_dir()
        
        # 确保目录存在
        self.plugins_dir.mkdir(exist_ok=True)
        
        # 插件配置改为从各个插件的config.json中读取
        self.plugin_configs = {
            'enabled_plugins': [],
            'plugin_settings': {}
        }
        self._load_enabled_plugins_from_configs()
    
    def _get_plugins_dir(self) -> Path:
        """获取插件目录路径，支持打包后的环境"""
        import sys
        
        if getattr(sys, 'frozen', False):
            # 打包后的环境
            base_path = Path(sys.executable).parent
            logger.info(f"[PLUGIN] 📦 Packaged environment detected, base path: {base_path}")
        else:
            # 开发环境
            base_path = Path(__file__).parent.parent
            logger.info(f"[PLUGIN] 🔧 Development environment detected, base path: {base_path}")
        
        plugins_path = base_path / "plugins"
        logger.info(f"[PLUGIN] 📁 Plugin directory path: {plugins_path}")
        logger.info(f"[PLUGIN] 📂 Plugin directory exists: {plugins_path.exists()}")
        
        return plugins_path

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
                else:
                    # 对于无效插件，创建一个错误信息条目
                    error_plugin_info = {
                        'name': plugin_dir.name,
                        'display_name': plugin_dir.name,
                        'version': 'Unknown',
                        'author': 'Unknown',
                        'description': tr('error.plugin_invalid'),
                        'enabled': False,
                        'loaded': False,
                        'is_available': False,
                        'error_info': tr('error.plugin_import_failed'),
                        'path': str(plugin_dir),
                        'has_local_config': (plugin_dir / "config.json").exists(),
                    }
                    available_plugins.append(error_plugin_info)
                    logger.warning(f"[PLUGIN] ⚠️ Added error plugin info for: {plugin_dir.name}")
            
            logger.info(f"🔍 Discovered {len(available_plugins)} available plugins")
            
        except Exception as e:
            logger.error(f"❌ Error discovering plugins: {e} - {traceback.format_exc()}")
        
        return available_plugins
    
    def _get_plugin_info(self, plugin_dir: Path) -> Optional[Dict[str, Any]]:
        """获取插件信息"""
        try:
            plugin_name = plugin_dir.name
            
            # 尝试导入插件模块
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
                logger.error(f"[PLUGIN] ⚠️ Plugin {plugin_name} has no valid Plugin class")
                return None
            
            # 创建临时插件实例，让plugin_base类进行合规性检查和配置处理
            try:
                temp_instance = plugin_class(None)  # 传入None作为app参数
                # 从插件实例获取完整信息（包括合规性检查、配置读取等）
                plugin_info = temp_instance.get_plugin_info()
                
                # 添加管理器相关的额外信息
                plugin_info.update({
                    'path': str(plugin_dir),
                    'class': plugin_class,
                    'has_local_config': (plugin_dir / "config.json").exists(),
                })
                
                logger.info(f"[PLUGIN] 🔍 Plugin {plugin_name} discovered")
                return plugin_info
                
            except Exception as e:
                logger.error(f"[PLUGIN] ❌ Plugin {plugin_name} validation failed: {e} - {traceback.format_exc()}")
                return None
            
        except Exception as e:
            logger.error(f"[PLUGIN] ❌ Failed to get plugin info for {plugin_dir.name}: {e} - {traceback.format_exc()}")
            return None
    
    def load_plugins(self):
        """加载所有启用的插件"""
        # 发现所有可用插件
        available_plugins = self.discover_plugins()
        
        # 筛选出启用的插件
        enabled_plugins = []
        for plugin_info in available_plugins:
            if plugin_info.get('enabled', False):
                enabled_plugins.append(plugin_info['name'])
        
        if not enabled_plugins:
            logger.info("[PLUGIN] 📦 No enabled plugins found")
            return
        
        logger.info(f"[PLUGIN] 🚀 Loading {len(enabled_plugins)} enabled plugins: {', '.join(enabled_plugins)}")
        
        for plugin_name in enabled_plugins:
            self.load_plugin(plugin_name)
    
    def load_plugin(self, plugin_name: str) -> bool:
        """加载指定插件"""
        if plugin_name in self.plugins:
            logger.warning(f"[PLUGIN] ⚠️ Plugin {plugin_name} already loaded")
            return True
        
        try:
            plugin_dir = self.plugins_dir / plugin_name
            if not plugin_dir.exists():
                logger.error(f"[PLUGIN] ❌ Plugin directory not found: {plugin_dir}")
                return False
            
            # 导入插件模块
            spec = importlib.util.spec_from_file_location(
                f"plugins.{plugin_name}",
                plugin_dir / "__init__.py"
            )
            
            if spec is None or spec.loader is None:
                logger.error(f"[PLUGIN] ❌ Cannot load plugin module: {plugin_name}")
                return False
            
            module = importlib.util.module_from_spec(spec)
            
            # 添加到sys.modules以支持相对导入
            sys.modules[f"plugins.{plugin_name}"] = module
            
            spec.loader.exec_module(module)
            
            # 获取插件类
            plugin_class = getattr(module, 'Plugin', None)
            if plugin_class is None:
                logger.error(f"[PLUGIN] ❌ Plugin {plugin_name} has no Plugin class")
                return False
            
            # 创建插件实例
            plugin_instance = plugin_class(self.app)
            
            # 验证插件实例
            if not isinstance(plugin_instance, PluginBase):
                logger.error(f"[PLUGIN] ❌ Plugin {plugin_name} is not a subclass of PluginBase")
                return False
            
            # 获取插件信息（包含display_name、description等）
            plugin_info = plugin_instance.get_plugin_info()
            
            # 注册插件翻译
            plugin_dir_str = str(plugin_dir)
            translations_dir = os.path.join(plugin_dir_str, 'translations')
            if os.path.exists(translations_dir):
                i18n_manager.register_plugin_translations(plugin_name, translations_dir)
                logger.info(f"[PLUGIN] 🌐 The Plugin {plugin_name} translation files have been registered")
            
            # 初始化插件
            plugin_instance.initialize()
            
            # 存储插件实例
            self.plugins[plugin_name] = plugin_instance
            
            # 注册插件到主窗口
            if self.app and hasattr(self.app, 'get_main_window'):
                main_window = self.app.get_main_window()
                if main_window:
                    # 检查按钮是否已存在，如果不存在则添加，否则只启用
                    if hasattr(main_window, 'plugin_buttons') and plugin_name in main_window.plugin_buttons:
                        # 按钮已存在，只需启用
                        if hasattr(main_window, 'enable_plugin_button'):
                            main_window.enable_plugin_button(plugin_name)
                    else:
                        # 按钮不存在，添加新按钮
                        main_window.add_plugin_button(
                            plugin_name,
                            plugin_info.get('display_name', plugin_name),
                            plugin_info.get('description', '')
                        )
                    
                    # 连接插件界面请求信号（只连接一次）
                    if not hasattr(self, '_signal_connected'):
                        main_window.plugin_widget_requested.connect(
                            self._handle_plugin_widget_request
                        )
                        self._signal_connected = True
            
            logger.info(f"[PLUGIN] ✅ Plugin loaded successfully: {plugin_name}")
            self.plugin_loaded.emit(plugin_name)
            
            return True
            
        except Exception as e:
            logger.error(f"[PLUGIN] ❌ Failed to load plugin {plugin_name}: {e} - {traceback.format_exc()}")
            self.plugin_error.emit(plugin_name, str(e))
            return False
    
    def _handle_plugin_widget_request(self, plugin_name: str):
        """处理插件界面请求"""
        if plugin_name not in self.plugins:
            logger.warning(f"[PLUGIN] ⚠️ Requested plugin not loaded: {plugin_name}")
            return
        
        try:
            plugin = self.plugins[plugin_name]
            widget = plugin.get_widget()
            
            if widget and self.app and hasattr(self.app, 'get_main_window'):
                main_window = self.app.get_main_window()
                if main_window:
                    # 获取插件信息
                    plugin_info = plugin.get_plugin_info()
                    main_window.add_plugin_widget(
                        plugin_name,
                        plugin_info.get('display_name', plugin_name),
                        widget
                    )
            
        except Exception as e:
            logger.error(f"[PLUGIN] ❌ Failed to get plugin widget for {plugin_name}: {e} - {traceback.format_exc()}")
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """卸载指定插件"""
        if plugin_name not in self.plugins:
            logger.warning(f"[PLUGIN] ⚠️ Plugin {plugin_name} not loaded")
            return True
        
        try:
            plugin = self.plugins[plugin_name]
            
            # 清理插件
            plugin.cleanup()
            
            # 从插件字典中移除
            del self.plugins[plugin_name]
            
            # 从主窗口移除插件按钮（隐藏按钮）
            if self.app and hasattr(self.app, 'get_main_window'):
                main_window = self.app.get_main_window()
                if main_window and hasattr(main_window, 'remove_plugin_button'):
                    main_window.remove_plugin_button(plugin_name)
            
            # 从sys.modules中移除
            module_name = f"plugins.{plugin_name}"
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            logger.info(f"[PLUGIN] 🗑️ Plugin unloaded successfully: {plugin_name}")
            self.plugin_unloaded.emit(plugin_name)
            
            return True
            
        except Exception as e:
            logger.error(f"[PLUGIN] ❌ Failed to unload plugin {plugin_name}: {e} - {traceback.format_exc()}")
            return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """启用插件"""
        enabled_plugins = self.plugin_configs.get('enabled_plugins', [])
        
        if plugin_name not in enabled_plugins:
            # 更新插件自己的config.json文件中的enabled字段
            success = self.update_plugin_config(plugin_name, {'enabled': True})
            if not success:
                return False
            
            # 更新内存中的启用列表
            enabled_plugins.append(plugin_name)
            self.plugin_configs['enabled_plugins'] = enabled_plugins
            
            # 立即加载插件
            success = self.load_plugin(plugin_name)
            if success:
                self.plugin_enabled.emit(plugin_name)
                logger.info(f"[PLUGIN] ✅ Plugin enabled: {plugin_name}")
            return success
        
        return True
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """禁用插件"""
        enabled_plugins = self.plugin_configs.get('enabled_plugins', [])
        
        if plugin_name in enabled_plugins:
            # 更新插件自己的config.json文件中的enabled字段
            success = self.update_plugin_config(plugin_name, {'enabled': False})
            if not success:
                return False
            
            # 更新内存中的启用列表
            enabled_plugins.remove(plugin_name)
            self.plugin_configs['enabled_plugins'] = enabled_plugins
            
            # 卸载插件
            success = self.unload_plugin(plugin_name)
            if success:
                self.plugin_disabled.emit(plugin_name)
                logger.info(f"[PLUGIN] ❌ Plugin disabled: {plugin_name}")
            return success
        
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
    
    def get_decrypted_plugin_setting(self, plugin_name: str, key: str, default=None):
        """获取解密后的插件设置
        
        对于password开头的配置项，会自动解密后返回明文密码
        对于非密码字段，行为与get_plugin_setting相同
        
        Args:
            plugin_name: 插件名称
            key: 设置键名
            default: 默认值
            
        Returns:
            解密后的设置值（如果是密码字段）或原始设置值
        """
        # 获取原始设置值
        value = self.get_plugin_setting(plugin_name, key, default)
        
        # 如果是密码字段且值不为空，进行解密
        if value and is_password_field(key):
            try:
                decrypted_value = decrypt_password(str(value))
                logger.debug(f"[PLUGIN] 🔓 Password field '{key}' decrypted successfully for plugin {plugin_name}")
                return decrypted_value
            except Exception as e:
                logger.error(f"[PLUGIN] ❌ Failed to decrypt password field '{key}' for plugin {plugin_name}: {e}")
                return value  # 解密失败时返回原值
        
        return value
    
    def set_plugin_setting(self, plugin_name: str, key: str, value):
        """设置插件设置"""
        # 直接更新插件的config.json文件
        success = self.update_plugin_config(plugin_name, {key: value})
        
        if success:
            # 同时更新内存中的设置（用于兼容性）
            if 'plugin_settings' not in self.plugin_configs:
                self.plugin_configs['plugin_settings'] = {}
            
            if plugin_name not in self.plugin_configs['plugin_settings']:
                self.plugin_configs['plugin_settings'][plugin_name] = {}
            
            self.plugin_configs['plugin_settings'][plugin_name][key] = value
            logger.debug(f"[PLUGIN] 💾 Setting {key} updated for plugin {plugin_name}")
        
        return success
    
    def cleanup(self):
        """清理插件管理器"""
        logger.info("[PLUGIN] 🧹 Cleaning up plugin manager...")
        
        # 卸载所有插件
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)
        
        logger.info("✨ Plugin manager cleanup completed")
    
    def _load_enabled_plugins_from_configs(self):
        """从各个插件的config.json文件中加载启用状态"""
        enabled_plugins = []
        
        try:
            # 遍历插件目录
            for plugin_dir in self.plugins_dir.iterdir():
                if not plugin_dir.is_dir() or plugin_dir.name.startswith('_'):
                    continue
                
                config_file = plugin_dir / "config.json"
                if config_file.exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)
                        
                        # 检查插件是否启用
                        available_config = config_data.get('available_config', {})
                        if available_config.get('enabled', False):
                            enabled_plugins.append(plugin_dir.name)
                            logger.debug(f"[PLUGIN] ✅ Plugin {plugin_dir.name} is enabled")
                    
                    except Exception as e:
                        logger.warning(f"[PLUGIN] ⚠️ Failed to read config for {plugin_dir.name}: {e}")
            
            self.plugin_configs['enabled_plugins'] = enabled_plugins
            logger.debug(f"[PLUGIN] 📋 Loaded {len(enabled_plugins)} enabled plugins from individual configs")
            
        except Exception as e:
            logger.error(f"[PLUGIN] ❌ Failed to load enabled plugins from configs: {e} - {traceback.format_exc()}")
    
    def update_plugin_config(self, plugin_name: str, new_config: dict) -> bool:
        """更新插件配置到config.json文件"""
        try:
            plugin_dir = self.plugins_dir / plugin_name
            if not plugin_dir.exists():
                logger.error(f"[PLUGIN] ❌ Plugin directory not found: {plugin_dir}")
                return False
            
            config_file = plugin_dir / "config.json"
            
            # 读取现有配置文件
            existing_config = {}
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        existing_config = json.load(f)
                except Exception as e:
                    logger.warning(f"[PLUGIN] ⚠️ Failed to read existing config for {plugin_name}: {e}")
            
            # 只更新available_config部分
            if 'available_config' not in existing_config:
                existing_config['available_config'] = {}
            
            existing_config['available_config'].update(new_config)
            
            # 保存更新后的配置到插件的config.json文件
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(existing_config, f, indent=2, ensure_ascii=False)
            
            # 发射配置变更信号
            self.plugin_config_changed.emit(plugin_name, new_config)
            
            logger.info(f"[PLUGIN] 💾 Available config updated for plugin {plugin_name}: {new_config}")
            return True
            
        except Exception as e:
            logger.error(f"[PLUGIN] ❌ Failed to update plugin config for {plugin_name}: {e} - {traceback.format_exc()}")
            return False