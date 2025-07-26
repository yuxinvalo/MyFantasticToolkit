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
        
        # 插件本地化支持
        self._plugin_dir = None
        self._config = {}
        self._translations = {}
        self._current_language = "zh_CN"
        
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
        # 优先使用本地配置
        if self._config and 'settings' in self._config:
            return self._config['settings'].get(key, default)
        
        # 回退到全局配置
        plugin_manager = self.get_plugin_manager()
        if plugin_manager:
            return plugin_manager.get_plugin_setting(self.get_name(), key, default)
        return default
    
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
            # 通过模块路径确定插件目录
            module_file = sys.modules[self.__class__.__module__].__file__
            if module_file:
                self._plugin_dir = Path(module_file).parent
        except Exception as e:
            logger.error(f"❌ [Plugin] Failed to init plugin paths: {e}")
    
    def _load_plugin_config(self):
        """加载插件本地配置"""
        if not self._plugin_dir:
            return
        
        config_file = self._plugin_dir / "config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                logger.debug(f"📋 [Plugin] Config loaded for {self.get_name()}")
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


class SimplePluginBase(PluginBase):
    """简单插件基类
    
    提供一些常用功能的默认实现，适合简单插件继承
    """
    
    def initialize(self) -> bool:
        """默认初始化实现"""
        try:
            self._initialized = True
            self.log_info("✅ Plugin initialized successfully")
            return True
        except Exception as e:
            self.log_error(f"❌ Plugin initialization failed: {e}")
            return False
    
    def create_widget(self) -> Optional[QWidget]:
        """默认界面创建实现
        
        子类应该重写此方法来创建具体的界面
        """
        from PySide6.QtWidgets import QLabel
        
        widget = QLabel(f"This is the default interface of the {self.get_display_name()} plugin")
        widget.setStyleSheet(
            "QLabel {"
            "    padding: 50px;"
            "    text-align: center;"
            "    font-size: 14px;"
            "    color: #666666;"
            "}"
        )
        
        return widget