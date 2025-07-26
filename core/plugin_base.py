# -*- coding: utf-8 -*-
"""
HSBC Little Worker - 插件基类
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QObject, Signal

from utils.logger import logger


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
        plugin_manager = self.get_plugin_manager()
        if plugin_manager:
            plugin_manager.set_plugin_setting(self.get_name(), key, value)
    
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
        
        widget = QLabel(f"这是 {self.get_display_name()} 插件的默认界面")
        widget.setStyleSheet(
            "QLabel {"
            "    padding: 50px;"
            "    text-align: center;"
            "    font-size: 14px;"
            "    color: #666666;"
            "}"
        )
        
        return widget