# -*- coding: utf-8 -*-
"""
HSBC Little Worker - 插件管理器对话框
"""

import os
from typing import List, Dict, Any

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QScrollArea,
    QPushButton, QLabel, QGroupBox, QTextEdit, QFrame, 
    QMessageBox, QCheckBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap

from utils.logger import logger
from .i18n import tr


class PluginItemWidget(QFrame):
    """插件项显示组件"""
    
    # 信号定义
    plugin_enabled_changed = Signal(str, bool)  # 插件启用状态变化信号
    plugin_load_requested = Signal(str)  # 插件加载请求信号
    plugin_unload_requested = Signal(str)  # 插件卸载请求信号
    
    def __init__(self, plugin_data, parent=None):
        super().__init__(parent)
        
        self.plugin_data = plugin_data
        self.plugin_name = plugin_data['name']
        
        # 初始化UI
        self._init_ui()
        
        # 应用样式
        self._apply_styles()
    
    def _init_ui(self):
        """初始化用户界面"""
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)
        self.setContentsMargins(0, 0, 0, 0)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 7, 10, 7)
        main_layout.setSpacing(5)
        
        # 顶部信息行
        top_layout = QHBoxLayout()
        top_layout.setSpacing(5)
        
        # 插件名称和版本
        name_version_layout = QVBoxLayout()
        name_version_layout.setSpacing(2)
        
        # 插件名称和可用状态
        name_status_layout = QHBoxLayout()
        name_status_layout.setSpacing(8)
        
        self.name_label = QLabel(self.plugin_data.get('display_name', self.plugin_name))
        name_font = QFont()
        name_font.setPointSize(11)
        name_font.setBold(True)
        self.name_label.setFont(name_font)
        name_status_layout.addWidget(self.name_label)
        
        # 可用状态显示（移到名称右边）
        self.available_label = QLabel()
        self.available_label.setStyleSheet("font-size: 10px; font-weight: bold;")
        self._update_available_display()
        name_status_layout.addWidget(self.available_label)
        name_status_layout.addStretch()
        
        name_version_layout.addLayout(name_status_layout)
        
        # 版本和作者信息
        version = self.plugin_data.get('version', 'Unknown')
        author = self.plugin_data.get('author', 'Unknown')
        self.info_label = QLabel(f"v{version} • {author}")
        info_font = QFont()
        info_font.setPointSize(9)
        self.info_label.setFont(info_font)
        self.info_label.setStyleSheet("color: #666666;")
        name_version_layout.addWidget(self.info_label)
        
        top_layout.addLayout(name_version_layout, 1)
        
        # 状态标签
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFixedSize(80, 24)
        self.status_label.setStyleSheet("""
            QLabel {
                border-radius: 12px;
                padding: 2px 8px;
                font-size: 9px;
                font-weight: bold;
            }
        """)
        self._update_status_label()
        top_layout.addWidget(self.status_label)
        
        # Enabled 复选框
        self.enabled_label = QLabel(tr("plugin_manager.enabled"))
        self.enabled_checkbox = QCheckBox()
        self.enabled_checkbox.toggled.connect(self._on_enabled_changed)
        self._update_enabled_switch()
        top_layout.addWidget(self.enabled_label)
        top_layout.addWidget(self.enabled_checkbox)
        
        main_layout.addLayout(top_layout)
        
        # 描述文本
        description = self.plugin_data.get('description', tr("plugin_manager.no_description"))
        self.description_label = QLabel(description)
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #555555; font-size: 10px; line-height: 1.4;")
        self.description_label.setMaximumHeight(40)
        main_layout.addWidget(self.description_label)
        
        # 如果有错误信息，显示错误详情
        if self.plugin_data.get('error_info'):
            self.error_label = QLabel(f"❌ {self.plugin_data['error_info']}")
            self.error_label.setWordWrap(True)
            self.error_label.setStyleSheet("color: #d32f2f; font-size: 9px; background-color: #ffebee; padding: 4px; border-radius: 4px;")
            main_layout.addWidget(self.error_label)
    
    def _update_status_label(self):
        """更新状态标签"""
        if self.plugin_data.get('loaded', False):
            self.status_label.setText(tr("plugin_manager.status.loaded"))
            self.status_label.setStyleSheet(self.status_label.styleSheet() + "background-color: #4caf50; color: white;")
        elif not self.plugin_data.get('is_available', True):
            self.status_label.setText(tr("plugin_manager.status.error"))
            self.status_label.setStyleSheet(self.status_label.styleSheet() + "background-color: #f44336; color: white;")
        else:
            self.status_label.setText(tr("plugin_manager.status.available"))
            self.status_label.setStyleSheet(self.status_label.styleSheet() + "background-color: #2196f3; color: white;")
    
    def _update_available_display(self):
        """更新可用状态显示"""
        if self.plugin_data.get('is_available', True):
            self.available_label.setText("✅ Available")
            self.available_label.setStyleSheet("font-size: 10px; font-weight: bold; color: #2E7D32;")
        else:
            self.available_label.setText("❌ Unavailable")
            self.available_label.setStyleSheet("font-size: 10px; font-weight: bold; color: #C62828;")
    
    def _update_enabled_switch(self):
        """更新启用开关"""
        # 启用开关现在控制插件的加载/卸载
        is_loaded = self.plugin_data.get('loaded', False)
        is_available = self.plugin_data.get('is_available', True)
        
        self.enabled_checkbox.setChecked(is_loaded)
        self.enabled_checkbox.setEnabled(is_available)  # 只有可用的插件才能操作
    
    def _on_enabled_changed(self, enabled):
        """启用状态变化处理（现在控制加载/卸载）"""
        if enabled:
            self.plugin_load_requested.emit(self.plugin_name)
        else:
            self.plugin_unload_requested.emit(self.plugin_name)
    
    def _apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            PluginItemWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin: 2px;
            }
            
            PluginItemWidget:hover {
                border-color: #2196f3;
                background-color: #f8f9ff;
            }
        """)
    
    def update_plugin_data(self, plugin_data):
        """更新插件数据"""
        self.plugin_data = plugin_data
        
        # 更新名称
        self.name_label.setText(plugin_data.get('display_name', self.plugin_name))
        
        # 更新版本和作者
        version = plugin_data.get('version', 'Unknown')
        author = plugin_data.get('author', 'Unknown')
        self.info_label.setText(f"v{version} • {author}")
        
        # 更新描述
        description = plugin_data.get('description', tr("plugin_manager.no_description"))
        self.description_label.setText(description)
        
        # 更新可用状态和启用开关
        self._update_available_display()
        self._update_enabled_switch()
        
        # 更新状态标签
        self._update_status_label()
        
        # 更新错误信息
        if hasattr(self, 'error_label'):
            self.error_label.setParent(None)
            delattr(self, 'error_label')
        
        if plugin_data.get('error_info'):
            self.error_label = QLabel(f"❌ {plugin_data['error_info']}")
            self.error_label.setWordWrap(True)
            self.error_label.setStyleSheet("color: #d32f2f; font-size: 9px; background-color: #ffebee; padding: 4px; border-radius: 4px;")
            self.layout().addWidget(self.error_label)


class PluginManagerDialog(QDialog):
    """插件管理器对话框"""
    
    # 信号定义
    plugin_enabled = Signal(str)  # 插件启用信号
    plugin_disabled = Signal(str)  # 插件禁用信号
    plugin_loaded = Signal(str)  # 插件加载信号
    plugin_unloaded = Signal(str)  # 插件卸载信号
    
    def __init__(self, plugin_manager, parent=None):
        super().__init__(parent)
        
        self.plugin_manager = plugin_manager
        self.plugins_data = []  # 存储插件数据
        self.plugin_widgets = {}  # 存储插件项widget
        
        # 初始化UI
        self._init_ui()
        
        # 加载插件数据
        self._load_plugins_data()
        
        # 连接信号
        self._connect_signals()
        
        logger.info("[PLUGIN_MANAGER] 🔧 Plugin manager dialog initialized")
    
    def _init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle(tr("plugin_manager.title"))
        self.setMinimumSize(400, 400)
        self.resize(400, 500)
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icon.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # 创建标题区域
        title_widget = self._create_title_widget()
        main_layout.addWidget(title_widget)
        
        # 创建内容区域
        content_widget = self._create_content_widget()
        main_layout.addWidget(content_widget, 1)
        
        # 创建按钮区域
        button_widget = self._create_button_widget()
        main_layout.addWidget(button_widget)
        
        # 应用样式
        self._apply_styles()
    
    def _create_title_widget(self):
        """创建标题区域"""
        title_frame = QFrame()
        title_frame.setFrameStyle(QFrame.NoFrame)  # 移除边框
        title_frame.setMaximumHeight(50)  # 减小高度
        
        layout = QVBoxLayout(title_frame)
        layout.setContentsMargins(10, 5, 10, 5)  # 减小边距
        
        # 主标题
        title_label = QLabel(tr("plugin_manager.title"))
        title_font = QFont()
        title_font.setPointSize(12)  # 缩小字体
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        return title_frame
    
    def _create_content_widget(self):
        """创建内容区域"""
        # 创建主容器
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # 创建插件列表标题
        list_title = QLabel(tr("plugin_manager.available_plugins"))
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)
        list_title.setFont(title_font)
        list_title.setStyleSheet("padding: 10px; background-color: #f5f5f5; border-bottom: 1px solid #e0e0e0;")
        content_layout.addWidget(list_title)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        
        # 创建插件列表容器
        self.plugin_list_widget = QWidget()
        self.plugin_list_layout = QVBoxLayout(self.plugin_list_widget)
        self.plugin_list_layout.setContentsMargins(10, 10, 10, 10)
        self.plugin_list_layout.setSpacing(8)
        self.plugin_list_layout.addStretch()  # 添加弹性空间
        
        scroll_area.setWidget(self.plugin_list_widget)
        content_layout.addWidget(scroll_area)
        
        return content_frame
    
    def _create_button_widget(self):
        """创建按钮区域"""
        button_frame = QFrame()
        layout = QHBoxLayout(button_frame)
        layout.setContentsMargins(0, 10, 0, 0)
        
        # 刷新按钮
        self.refresh_button = QPushButton(tr("plugin_manager.refresh"))
        self.refresh_button.clicked.connect(self._refresh_plugins)
        layout.addWidget(self.refresh_button)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 关闭按钮
        self.close_button = QPushButton(tr("plugin_manager.close"))
        self.close_button.clicked.connect(self.accept)
        layout.addWidget(self.close_button)
        
        return button_frame
    
    def _apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            
            QScrollArea {
                border: none;
                background-color: #ffffff;
            }
            
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 11px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
            }
            
            QPushButton:pressed {
                background-color: #dee2e6;
            }
            
            QCheckBox {
                font-size: 10px;
            }
            
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 1px solid #ccc;
            }
            
            QCheckBox::indicator:checked {
                background-color: #2196f3;
                border-color: #2196f3;
            }
        """)
    
    def _load_plugins_data(self):
        """加载插件数据"""
        try:
            # 获取所有可用插件
            self.plugins_data = self.plugin_manager.discover_plugins()
            
            # 获取已加载的插件
            loaded_plugins = self.plugin_manager.get_loaded_plugins()
            
            # 更新插件状态信息
            for plugin_data in self.plugins_data:
                plugin_name = plugin_data['name']
                
                # 设置加载状态
                if plugin_name in loaded_plugins:
                    plugin_data['loaded'] = True
                    plugin_data['status'] = tr("plugin_manager.status.loaded")
                else:
                    plugin_data['loaded'] = False
                    if plugin_data.get('is_available', True):
                        plugin_data['status'] = tr("plugin_manager.status.available")
                    else:
                        plugin_data['status'] = tr("plugin_manager.status.error")
            
            # 更新插件列表
            self._update_plugin_list()
            
            logger.info(f"[PLUGIN_MANAGER] 📋 Loaded {len(self.plugins_data)} plugins data")
            
        except Exception as e:
            logger.error(f"[PLUGIN_MANAGER] ❌ Failed to load plugins data: {e}")
            QMessageBox.warning(self, tr("plugin_manager.error"), 
                              tr("plugin_manager.load_error").format(error=str(e)))
    
    def _update_plugin_list(self):
        """更新插件列表"""
        # 清除现有的插件项
        for plugin_name, widget in self.plugin_widgets.items():
            widget.setParent(None)
        self.plugin_widgets.clear()
        
        # 创建新的插件项
        for plugin_data in self.plugins_data:
            plugin_name = plugin_data['name']
            
            # 创建插件项widget
            plugin_widget = PluginItemWidget(plugin_data)
            
            # 连接信号
            plugin_widget.plugin_enabled_changed.connect(self._on_plugin_enabled_changed)
            plugin_widget.plugin_load_requested.connect(self._load_plugin)
            plugin_widget.plugin_unload_requested.connect(self._unload_plugin)
            
            # 添加到布局中（在弹性空间之前）
            self.plugin_list_layout.insertWidget(self.plugin_list_layout.count() - 1, plugin_widget)
            
            # 存储widget引用
            self.plugin_widgets[plugin_name] = plugin_widget
    
    def _connect_signals(self):
        """连接信号"""
        # 连接插件管理器的信号
        if self.plugin_manager:
            self.plugin_manager.plugin_loaded.connect(self._on_plugin_loaded)
            self.plugin_manager.plugin_unloaded.connect(self._on_plugin_unloaded)
            self.plugin_manager.plugin_error.connect(self._on_plugin_error)
    
    def _on_plugin_enabled_changed(self, plugin_name, enabled):
        """插件启用状态变化处理"""
        try:
            if enabled:
                # 启用插件
                if self.plugin_manager.enable_plugin(plugin_name):
                    self.plugin_enabled.emit(plugin_name)
                    logger.info(f"[PLUGIN_MANAGER] ✅ Plugin enabled: {plugin_name}")
                else:
                    # 启用失败，恢复复选框状态
                    self._refresh_plugins()
                    QMessageBox.warning(self, tr("plugin_manager.error"),
                                      tr("plugin_manager.enable_error").format(name=plugin_name))
            else:
                # 禁用插件
                if self.plugin_manager.disable_plugin(plugin_name):
                    self.plugin_disabled.emit(plugin_name)
                    logger.info(f"[PLUGIN_MANAGER] ❌ Plugin disabled: {plugin_name}")
                else:
                    # 禁用失败，恢复复选框状态
                    self._refresh_plugins()
                    QMessageBox.warning(self, tr("plugin_manager.error"),
                                      tr("plugin_manager.disable_error").format(name=plugin_name))
        except Exception as e:
            logger.error(f"[PLUGIN_MANAGER] ❌ Error changing plugin state: {e}")
            self._refresh_plugins()
    
    def _load_plugin(self, plugin_name):
        """加载插件"""
        try:
            if self.plugin_manager.load_plugin(plugin_name):
                logger.info(f"[PLUGIN_MANAGER] 🔌 Plugin loaded: {plugin_name}")
                self.plugin_loaded.emit(plugin_name)  # 发出插件加载信号
                self._refresh_plugins()
            else:
                QMessageBox.warning(self, tr("plugin_manager.error"),
                                  tr("plugin_manager.load_error_msg").format(name=plugin_name))
        except Exception as e:
            logger.error(f"[PLUGIN_MANAGER] ❌ Error loading plugin: {e}")
            QMessageBox.warning(self, tr("plugin_manager.error"), str(e))
    
    def _unload_plugin(self, plugin_name):
        """卸载插件"""
        try:
            if self.plugin_manager.unload_plugin(plugin_name):
                logger.info(f"[PLUGIN_MANAGER] 🗑️ Plugin unloaded: {plugin_name}")
                self.plugin_unloaded.emit(plugin_name)  # 发出插件卸载信号
                self._refresh_plugins()
            else:
                QMessageBox.warning(self, tr("plugin_manager.error"),
                                  tr("plugin_manager.unload_error").format(name=plugin_name))
        except Exception as e:
            logger.error(f"[PLUGIN_MANAGER] ❌ Error unloading plugin: {e}")
            QMessageBox.warning(self, tr("plugin_manager.error"), str(e))
    
    def _refresh_plugins(self):
        """刷新插件列表"""
        try:
            self._load_plugins_data()
            logger.info("[PLUGIN_MANAGER] 🔄 Plugin list refreshed")
        except Exception as e:
            logger.error(f"[PLUGIN_MANAGER] ❌ Error refreshing plugins: {e}")
    
    def _on_plugin_loaded(self, plugin_name):
        """插件加载完成回调"""
        self._refresh_plugins()
    
    def _on_plugin_unloaded(self, plugin_name):
        """插件卸载完成回调"""
        self._refresh_plugins()
    
    def _on_plugin_error(self, plugin_name, error_message):
        """插件错误回调"""
        QMessageBox.critical(self, tr("plugin_manager.error"),
                           tr("plugin_manager.plugin_error").format(name=plugin_name, error=error_message))
        self._refresh_plugins()
    
    def refresh_plugin_list(self):
        """刷新插件列表"""
        try:
            # 重新加载插件数据
            self._load_plugins_data()
            
            logger.info("[PLUGIN_MANAGER] 🔄 Plugin list refreshed")
            
        except Exception as e:
            logger.error(f"[PLUGIN_MANAGER] ❌ Error refreshing plugin list: {e}")
            QMessageBox.warning(self, tr("plugin_manager.error"),
                              f"刷新插件列表时出错: {str(e)}")