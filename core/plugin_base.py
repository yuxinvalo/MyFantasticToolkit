# -*- coding: utf-8 -*-
"""
HSBC Little Worker - 插件基类
"""

import os
import sys
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject, Signal

from utils.logger import logger
# 移除不存在的导入


class PluginMeta(type(QObject), type(ABC)):
    """解决QObject和ABC元类冲突的元类"""
    pass


class PluginBase(QObject, ABC, metaclass=PluginMeta):
    """插件基类
    
    所有插件都必须继承此类并实现抽象方法
    """
    
    # 插件元信息（子类应该重写这些属性）
    NAME = "Unknown Plugin"
    DISPLAY_NAME = "Unknown Plugin"
    DESCRIPTION = "Unknown Plugin Description"
    VERSION = "1.0.0"
    AUTHOR = "Unknown Author"
    
    # 信号定义
    status_changed = Signal(str)  # 状态变化信号
    error_occurred = Signal(str)  # 错误发生信号
    
    def __init__(self, app=None):
        super().__init__()
        
        self.app = app  # 主应用程序引用
        self._widget = None  # 插件界面组件
        self._initialized = False  # 初始化状态
        self._enabled = True  # 启用状态
        self.is_available = True  # 插件可用状态
        self.error_info = None  # 错误信息
        
        # 插件本地化支持
        self._plugin_dir = None
        self._config = {}
        self._translations = {}
        self._current_language = "zh_CN"
        
        # 插件合规性检查
        self._check_plugin_compliance()
    
        # 初始化插件目录和配置
        self._init_plugin_paths()
        self._load_plugin_config()
        self._load_plugin_translations()
    
    @abstractmethod
    def initialize(self) -> bool:
        """初始化插件
        
        Returns:
            bool: 初始化是否成功
        """
        pass
    
    @abstractmethod
    def create_widget(self) -> Optional[QWidget]:
        """创建插件界面组件
        
        Returns:
            QWidget: 插件的界面组件，如果插件没有界面则返回None
        """
        pass
    
    def cleanup(self):
        """清理插件资源
        
        插件卸载时调用，用于清理资源、保存状态等
        """
        try:
            if self._widget:
                self._widget.close()
                self._widget = None
            
            self._initialized = False
            
        except Exception as e:
            logger.error(f"❌ Plugin {self.get_name()} cleanup error: {e}")
    
    def get_widget(self) -> Optional[QWidget]:
        """获取插件界面组件
        
        Returns:
            QWidget: 插件的界面组件
        """
        if self._widget is None:
            try:
                self._widget = self.create_widget()
                if self._widget:
                    pass
            except Exception as e:
                logger.error(f"❌ Plugin {self.get_name()} widget creation error: {e}")
                self.error_occurred.emit(str(e))
        
        return self._widget
    
    def get_name(self) -> str:
        """获取插件名称
        
        Returns:
            str: 插件名称（通常是类名或模块名）
        """
        return self.__class__.__module__.split('.')[-1] if '.' in self.__class__.__module__ else self.__class__.__name__
    
    def get_display_name(self) -> str:
        """获取插件显示名称
        
        Returns:
            str: 插件的显示名称
        """
        return self.DISPLAY_NAME
    
    def get_description(self) -> str:
        """获取插件描述
        
        Returns:
            str: 插件描述
        """
        return self.DESCRIPTION
    
    def get_version(self) -> str:
        """获取插件版本
        
        Returns:
            str: 插件版本
        """
        return self.VERSION
    
    def get_author(self) -> str:
        """获取插件作者
        
        Returns:
            str: 插件作者
        """
        return self.AUTHOR
    
    def is_initialized(self) -> bool:
        """检查插件是否已初始化
        
        Returns:
            bool: 是否已初始化
        """
        return self._initialized
    
    def is_enabled(self) -> bool:
        """检查插件是否启用
        
        Returns:
            bool: 是否启用
        """
        return self._enabled
    
    def set_enabled(self, enabled: bool):
        """设置插件启用状态
        
        Args:
            enabled: 是否启用
        """
        if self._enabled != enabled:
            self._enabled = enabled
            status = "enabled" if enabled else "disabled"
            logger.info(f"🔄 Plugin {self.get_name()} {status}")
            self.status_changed.emit(status)
    
    def get_app(self):
        """获取主应用程序引用
        
        Returns:
            主应用程序实例
        """
        return self.app
    
    def get_plugin_manager(self):
        """获取插件管理器引用
        
        Returns:
            插件管理器实例
        """
        if self.app and hasattr(self.app, 'get_plugin_manager'):
            return self.app.get_plugin_manager()
        return None
    
    def get_setting(self, key: str, default=None):
        """获取插件设置
        
        Args:
            key: 设置键名
            default: 默认值
            
        Returns:
            设置值
        """
        # 首先尝试从available_config中获取（实时读取）
        if self._config and 'available_config' in self._config:
            # 重新加载配置以获取最新值
            self._load_plugin_config()
            if key in self._config.get('available_config', {}):
                return self._config['available_config'][key]
        
        # 优先使用本地配置
        if self._config and 'settings' in self._config:
            return self._config['settings'].get(key, default)
        
        # 回退到全局配置
        plugin_manager = self.get_plugin_manager()
        if plugin_manager:
            return plugin_manager.get_plugin_setting(self.get_name(), key, default)
        return default

    def get_available_config(self) -> dict:
        """获取插件配置
        
        Returns:
            dict: 插件配置字典
        """
        return self._config.get('available_config', {})
    
    def set_setting(self, key: str, value):
        """设置插件设置
        
        Args:
            key: 设置键名
            value: 设置值
        """
        # 优先使用本地配置
        if self._config:
            if 'settings' not in self._config:
                self._config['settings'] = {}
            self._config['settings'][key] = value
            self._save_plugin_config()
        else:
            # 回退到全局配置
            plugin_manager = self.get_plugin_manager()
            if plugin_manager:
                plugin_manager.set_plugin_setting(self.get_name(), key, value)
    
    def _init_plugin_paths(self):
        """初始化插件路径"""
        try:
            # 使用统一的方法获取插件目录
            self._plugin_dir = self._get_plugin_directory()
            if self._plugin_dir:
                logger.debug(f"[PLUGIN] 🔍 Plugin paths initialized: {self._plugin_dir}")
            else:
                logger.warning(f"[PLUGIN] ⚠️ Could not determine plugin directory for {self.get_name()}")
        except Exception as e:
            import traceback
            logger.error(f"[PLUGIN] ❌ Failed to init plugin paths: {e} - {traceback.format_exc()}")
    
    def _load_plugin_config(self):
        """加载插件本地配置"""
        if not self._plugin_dir:
            return
        
        config_file = self._plugin_dir / "config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                
                # 从配置文件中读取enabled状态
                available_config = self._config.get('available_config', {})
                self._enabled = available_config.get('enabled', True)
                
                logger.debug(f"📋 [Plugin] Config loaded for {self.get_name()}, enabled: {self._enabled}")
            except Exception as e:
                logger.error(f"❌ [Plugin] Failed to load config for {self.get_name()}: {e}")
                self._config = {}
    
    def _save_plugin_config(self):
        """保存插件本地配置"""
        if not self._plugin_dir or not self._config:
            return
        
        config_file = self._plugin_dir / "config.json"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            logger.debug(f"💾 [Plugin] Config saved for {self.get_name()}")
        except Exception as e:
            logger.error(f"❌ [Plugin] Failed to save config for {self.get_name()}: {e}")
    
    def _load_plugin_translations(self):
        """加载插件翻译文件"""
        if not self._plugin_dir:
            return
        
        translations_dir = self._plugin_dir / "translations"
        if not translations_dir.exists():
            return
        
        # 加载所有语言的翻译文件
        for lang_file in translations_dir.glob("*.json"):
            lang_code = lang_file.stem
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self._translations[lang_code] = json.load(f)
                logger.debug(f"🌍 [Plugin] Translation loaded for {self.get_name()}: {lang_code}")
            except Exception as e:
                logger.error(f"❌ [Plugin] Failed to load translation {lang_file}: {e}")
    
    def tr(self, key: str, **kwargs) -> str:
        """
        获取插件本地化文本
        
        Args:
            key: 翻译键
            **kwargs: 格式化参数
            
        Returns:
            str: 翻译后的文本
        """
        # 首先尝试从全局国际化管理器获取插件翻译
        from core.i18n import i18n_manager
        plugin_name = self.__class__.__module__.split('.')[-1]  # 获取插件名称
        text = i18n_manager.get_plugin_translation(plugin_name, key)
        
        if text != key:  # 如果找到了翻译
            if kwargs:
                try:
                    return text.format(**kwargs)
                except (KeyError, ValueError):
                    return text
            return text
        
        # 回退到本地翻译
        if self._translations and self._current_language in self._translations:
            text = self._translations[self._current_language].get(key, key)
            if kwargs:
                try:
                    return text.format(**kwargs)
                except (KeyError, ValueError):
                    return text
            return text
        return key
    
    def set_language(self, language_code: str):
        """设置插件语言
        
        Args:
            language_code: 语言代码
        """
        if language_code in self._translations or language_code in ["zh_CN", "en_US"]:
            self._current_language = language_code
            logger.debug(f"🌍 [Plugin] Language set to {language_code} for {self.get_name()}")
    
    def show_status_message(self, message: str, timeout: int = 3000):
        """在状态栏显示消息
        
        Args:
            message: 要显示的消息
            timeout: 显示时间（毫秒）
        """
        if self.app and hasattr(self.app, 'statusBar'):
            status_bar = self.app.statusBar()
            if status_bar:
                status_bar.showMessage(f"[{self.get_display_name()}] {message}", timeout)
    
    def log_info(self, message: str):
        """记录信息日志
        
        Args:
            message: 日志消息
        """
        logger.info(f"[{self.get_name()}] {message}")
    
    def log_warning(self, message: str):
        """记录警告日志
        
        Args:
            message: 日志消息
        """
        logger.warning(f"[{self.get_name()}] {message}")
    
    def log_error(self, message: str):
        """记录错误日志
        
        Args:
            message: 日志消息
        """
        logger.error(f"[{self.get_name()}] {message}")
    
    def log_debug(self, message: str):
        """记录调试日志
        
        Args:
            message: 日志消息
        """
        logger.debug(f"[{self.get_name()}] {message}")
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"{self.get_display_name()} v{self.get_version()}"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return (
            f"<{self.__class__.__name__}("
            f"name='{self.get_name()}', "
            f"display_name='{self.get_display_name()}', "
            f"version='{self.get_version()}', "
            f"initialized={self._initialized}, "
            f"enabled={self._enabled}"
            f")>"
        )
    
    def _check_plugin_compliance(self):
        """检查插件合规性
        
        根据文档要求检查插件是否符合规范：
        1. 检查必需的类元信息
        2. 如果config.json不存在，自动生成
        3. 验证config.json格式
        """
        try:
            # 检查必需的类元信息
            required_attrs = ['NAME', 'DISPLAY_NAME', 'DESCRIPTION', 'VERSION', 'AUTHOR']
            missing_attrs = []
            
            for attr in required_attrs:
                if not hasattr(self.__class__, attr) or getattr(self.__class__, attr) == f"Unknown {attr.replace('_', ' ').title()}":
                    missing_attrs.append(attr)
            
            if missing_attrs:
                error_msg = f"Missing required attributes: {', '.join(missing_attrs)}"
                logger.warning(f"⚠️ [Plugin Compliance] {self.get_name()} {error_msg}")
                self.is_available = False
                self.error_info = error_msg
                return
            
            # 获取插件目录
            plugin_dir = self._get_plugin_directory()
            if not plugin_dir:
                error_msg = "Cannot determine plugin directory"
                logger.error(f"❌ [Plugin Compliance] {error_msg} for {self.get_name()}")
                self.is_available = False
                self.error_info = error_msg
                return
            
            config_file = plugin_dir / "config.json"
            
            # 如果config.json不存在，自动生成
            if not config_file.exists():
                if not self._generate_config_file(config_file):
                    return  # 生成失败，错误信息已设置
            else:
                # 验证现有config.json格式
                if not self._validate_config_file(config_file):
                    return  # 验证失败，错误信息已设置
                
        except Exception as e:
            import traceback
            error_msg = f"Error checking compliance: {e}"
            logger.error(f"❌ [Plugin Compliance] {error_msg} for {self.get_name()} - {traceback.format_exc()}")
            self.is_available = False
            self.error_info = error_msg
    
    def _get_plugin_directory(self) -> Optional[Path]:
        """获取插件目录路径"""
        try:
            # 尝试从模块文件路径获取
            module_name = self.__class__.__module__
            if module_name in sys.modules:
                module_file = sys.modules[module_name].__file__
                if module_file:
                    plugin_dir = Path(module_file).parent
                    logger.debug(f"[PLUGIN] 🔍 Found plugin directory: {plugin_dir}")
                    return plugin_dir
            
            # 如果上述方法失败，尝试通过插件名称构建路径
            plugin_name = self.get_name()
            if plugin_name:
                # 假设插件位于项目根目录的plugins文件夹下
                current_file = Path(__file__).resolve()
                project_root = current_file.parent.parent  # 从core目录回到项目根目录
                plugin_dir = project_root / "plugins" / plugin_name
                if plugin_dir.exists():
                    logger.debug(f"[PLUGIN] 🔍 Found plugin directory via name: {plugin_dir}")
                    return plugin_dir
                    
        except Exception as e:
            logger.error(f"[PLUGIN] ❌ Failed to get plugin directory: {e} - {traceback.format_exc()}")
        return None
    
    def _generate_config_file(self, config_file: Path) -> bool:
        """自动生成config.json文件"""
        try:
            plugin_name = self.get_name()
            
            # 从类元信息生成配置
            config_data = {
                "plugin_info": {
                    "name": plugin_name,
                    "display_name": getattr(self.__class__, 'DISPLAY_NAME', plugin_name),
                    "description": getattr(self.__class__, 'DESCRIPTION', 'Plugin description'),
                    "version": getattr(self.__class__, 'VERSION', '1.0.0'),
                    "author": getattr(self.__class__, 'AUTHOR', 'Unknown Author')
                },
                "available_config": {
                    "enabled": True
                }
            }
            
            # 创建目录（如果不存在）
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入配置文件
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📋 [Plugin Compliance] Auto-generated config.json for {plugin_name}")
            return True
            
        except Exception as e:
            import traceback
            error_msg = f"Failed to generate config.json: {e}"
            logger.error(f"❌ [Plugin Compliance] {error_msg} for {self.get_name()} - {traceback.format_exc()}")
            self.is_available = False
            self.error_info = error_msg
            return False
    
    def _validate_config_file(self, config_file: Path) -> bool:
        """验证config.json文件格式"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 检查必需的字段
            if 'plugin_info' not in config_data:
                error_msg = "config.json missing 'plugin_info' field"
                logger.error(f"❌ [Plugin Compliance] {self.get_name()} {error_msg}")
                self.is_available = False
                self.error_info = error_msg
                return False
            
            if 'available_config' not in config_data:
                error_msg = "config.json missing 'available_config' field"
                logger.error(f"❌ [Plugin Compliance] {self.get_name()} {error_msg}")
                self.is_available = False
                self.error_info = error_msg
                return False
            
            plugin_info = config_data['plugin_info']
            required_info_fields = ['name', 'display_name', 'description', 'version', 'author']
            
            for field in required_info_fields:
                if field not in plugin_info:
                    error_msg = f"config.json missing required field: plugin_info.{field}"
                    logger.error(f"❌ [Plugin Compliance] {self.get_name()} {error_msg}")
                    self.is_available = False
                    self.error_info = error_msg
                    return False
            
            available_config = config_data['available_config']
            if 'enabled' not in available_config:
                error_msg = "config.json missing required field: available_config.enabled"
                logger.error(f"❌ [Plugin Compliance] {self.get_name()} {error_msg}")
                self.is_available = False
                self.error_info = error_msg
                return False
            
            if not isinstance(available_config['enabled'], bool):
                error_msg = "config.json 'enabled' field must be boolean"
                logger.error(f"❌ [Plugin Compliance] {self.get_name()} {error_msg}")
                self.is_available = False
                self.error_info = error_msg
                return False
            
            logger.debug(f"✅ [Plugin Compliance] {self.get_name()} config.json validation passed")
            return True
            
        except json.JSONDecodeError as e:
            error_msg = f"config.json is not valid JSON: {e}"
            logger.error(f"❌ [Plugin Compliance] {self.get_name()} {error_msg}")
            self.is_available = False
            self.error_info = error_msg
            return False
        except Exception as e:
            import traceback
            error_msg = f"Failed to validate config.json: {e}"
            logger.error(f"❌ [Plugin Compliance] {error_msg} for {self.get_name()} - {traceback.format_exc()}")
            self.is_available = False
            self.error_info = error_msg
            return False
    
    def get_plugin_info(self) -> dict:
        """获取插件信息字典"""
        return {
            'name': self.get_name(),
            'display_name': self.get_display_name(),
            'description': self.get_description(),
            'version': self.get_version(),
            'author': self.get_author(),
            'is_available': self.is_available,
            'error_info': self.error_info,
            'enabled': self.is_enabled(),
            'available_config': self.get_available_config()
        }


