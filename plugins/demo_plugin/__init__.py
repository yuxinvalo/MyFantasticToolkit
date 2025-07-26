# -*- coding: utf-8 -*-
"""
HSBC Little Worker - 演示插件
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, 
    QTextEdit, QHBoxLayout, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from core.plugin_base import SimplePluginBase
from core.i18n import tr, get_i18n_manager


class Plugin(SimplePluginBase):
    """Demo Plugin class"""
    
    # 插件元信息
    DISPLAY_NAME = "Demo Plugin"
    DESCRIPTION = "This is a demo plugin to show basic plugin system features"
    VERSION = "1.0.0"
    AUTHOR = "HSBC IT Support"
    
    def __init__(self, app=None):
        super().__init__(app)
        self.click_count = 0
        self.i18n_manager = get_i18n_manager()
        
        # 连接语言变更信号
        self.i18n_manager.language_changed.connect(self.on_language_changed)
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            self.log_info("Demo Plugin Init ...")
            
            # 从配置中读取点击次数
            self.click_count = self.get_setting('click_count', 0)
            
            self._initialized = True
            self.log_info("Demo Plugin Init Done.")
            return True
            
        except Exception as e:
            self.log_error(f"Demo Plugin Init Failed: {e}")
            return False
    
    def create_widget(self) -> QWidget:
        """创建插件界面"""
        # 创建主容器
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        self.title_label = QLabel(tr("plugin.demo.name"))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # 描述
        self.desc_label = QLabel(tr("plugin.demo.description_detail"))
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet(
            "QLabel {"
            "    background-color: #f8f9fa;"
            "    border: 1px solid #dee2e6;"
            "    border-radius: 6px;"
            "    padding: 15px;"
            "    color: #495057;"
            "}"
        )
        layout.addWidget(self.desc_label)
        
        # 功能区域
        self.function_group = QGroupBox(tr("plugin.demo.function_demo"))
        function_layout = QVBoxLayout(self.function_group)
        
        # 点击计数器
        counter_layout = QHBoxLayout()
        
        self.counter_label = QLabel(tr("plugin.demo.click_count").format(count=self.click_count))
        self.counter_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        counter_layout.addWidget(self.counter_label)
        
        counter_layout.addStretch()
        
        self.click_button = QPushButton(tr("plugin.demo.click_button"))
        self.click_button.clicked.connect(self._on_click_button)
        self.click_button.setStyleSheet(
            "QPushButton {"
            "    background-color: #007bff;"
            "    color: white;"
            "    border: none;"
            "    padding: 8px 16px;"
            "    border-radius: 4px;"
            "    font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "    background-color: #0056b3;"
            "}"
            "QPushButton:pressed {"
            "    background-color: #004085;"
            "}"
        )
        counter_layout.addWidget(self.click_button)
        
        function_layout.addLayout(counter_layout)
        
        # 重置按钮
        self.reset_button = QPushButton(tr("plugin.demo.reset_button"))
        self.reset_button.clicked.connect(self._on_reset_button)
        self.reset_button.setStyleSheet(
            "QPushButton {"
            "    background-color: #6c757d;"
            "    color: white;"
            "    border: none;"
            "    padding: 6px 12px;"
            "    border-radius: 4px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #545b62;"
            "}"
        )
        function_layout.addWidget(self.reset_button)
        
        layout.addWidget(self.function_group)
        
        # 日志显示区域
        self.log_group = QGroupBox(tr("plugin.demo.log_title"))
        log_layout = QVBoxLayout(self.log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(
            "QTextEdit {"
            "    background-color: #f8f9fa;"
            "    border: 1px solid #dee2e6;"
            "    border-radius: 4px;"
            "    font-family: 'Consolas', 'Monaco', monospace;"
            "    font-size: 10px;"
            "}"
        )
        
        # 添加初始日志
        self.log_text.append("[INFO] Demo Plugin UI Created.")
        self.log_text.append(f"[INFO] Current Click Count: {self.click_count}")
        
        log_layout.addWidget(self.log_text)
        
        # 清空日志按钮
        self.clear_log_button = QPushButton(tr("plugin.demo.clear_log"))
        self.clear_log_button.clicked.connect(self._on_clear_log)
        self.clear_log_button.setStyleSheet(
            "QPushButton {"
            "    background-color: #dc3545;"
            "    color: white;"
            "    border: none;"
            "    padding: 4px 8px;"
            "    border-radius: 4px;"
            "    font-size: 10px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #c82333;"
            "}"
        )
        log_layout.addWidget(self.clear_log_button)
        
        layout.addWidget(self.log_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        self.log_info("Demo Plugin UI Created.")
        
        return widget
    
    def _on_click_button(self):
        """点击按钮事件处理"""
        self.click_count += 1
        
        # 更新界面
        self.counter_label.setText(tr("plugin.demo.click_count").format(count=self.click_count))
        
        # 保存设置
        self.set_setting('click_count', self.click_count)
        
        # 添加日志
        message = tr("plugin.demo.clicked_message").format(count=self.click_count)
        self.log_text.append(f"[INFO] {message}")
        
        # 显示状态消息
        self.show_status_message(message)
        
        # 记录日志
        self.log_info(f"Button is triggered, count: {self.click_count}")
    
    def _on_reset_button(self):
        """重置按钮事件处理"""
        old_count = self.click_count
        self.click_count = 0
        
        # 更新界面
        self.counter_label.setText(tr("plugin.demo.click_count").format(count=self.click_count))
        
        # 保存设置
        self.set_setting('click_count', self.click_count)
        
        # 添加日志
        message = tr("plugin.demo.reset_message").format(old_count=old_count)
        self.log_text.append(f"[INFO] {message}")
        
        # 显示状态消息
        self.show_status_message(tr("plugin.demo.reset_status"))
        
        # 记录日志
        self.log_info(f"Counter reset: {old_count} to 0")
    
    def _on_clear_log(self):
        """清空日志事件处理"""
        self.log_text.clear()
        message = tr("plugin.demo.log_cleared")
        self.log_text.append(f"[INFO] {message}")
        
        # 显示状态消息
        self.show_status_message(message)
        
        # 记录日志
        self.log_info("Log cleared.")
    
    def cleanup(self):
        """清理插件资源"""
        # 保存当前状态
        self.set_setting('click_count', self.click_count)
        
        self.log_info("Demo Plugin is cleaning up resources...")
        
        # 调用父类清理方法
        super().cleanup()
        
        self.log_info("Demo Plugin cleaned up.")
    
    def on_language_changed(self):
        """语言变更时更新界面文本"""
        if hasattr(self, 'title_label'):
            self.title_label.setText(tr("plugin.demo.name"))
        if hasattr(self, 'desc_label'):
            self.desc_label.setText(tr("plugin.demo.description_detail"))
        if hasattr(self, 'function_group'):
            self.function_group.setTitle(tr("plugin.demo.function_demo"))
        if hasattr(self, 'counter_label'):
            self.counter_label.setText(tr("plugin.demo.click_count").format(count=self.click_count))
        if hasattr(self, 'click_button'):
            self.click_button.setText(tr("plugin.demo.click_button"))
        if hasattr(self, 'reset_button'):
            self.reset_button.setText(tr("plugin.demo.reset_button"))
        if hasattr(self, 'log_group'):
            self.log_group.setTitle(tr("plugin.demo.log_title"))
        if hasattr(self, 'clear_log_button'):
            self.clear_log_button.setText(tr("plugin.demo.clear_log"))