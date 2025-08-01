# -*- coding: utf-8 -*-
"""
HSBC Little Worker - Support Web Toolkit Plugin
"""

import os
import subprocess
import webbrowser
import requests
import time
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QGroupBox, QGridLayout, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QPixmap

from core.plugin_base import PluginBase
from core.i18n import get_i18n_manager


class StreamlitServerThread(QThread):
    """Streamlit服务器线程"""
    server_started = Signal(str)  # 服务启动信号，传递URL
    server_stopped = Signal()     # 服务停止信号
    server_error = Signal(str)    # 服务错误信号
    
    def __init__(self, port: int, host: str = "localhost"):
        super().__init__()
        self.port = port
        self.host = host
        self.process: Optional[subprocess.Popen] = None
        self.should_stop = False
    
    def run(self):
        """启动Streamlit服务"""
        try:
            # 这里暂时模拟启动过程，实际实现时需要启动真正的Streamlit应用
            # cmd = ["streamlit", "run", "streamlit_app.py", "--server.port", str(self.port), "--server.address", self.host]
            # self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 模拟启动延迟
            time.sleep(2)
            
            if not self.should_stop:
                url = f"http://{self.host}:{self.port}"
                self.server_started.emit(url)
                
                # 保持线程运行
                while not self.should_stop:
                    time.sleep(1)
                    
        except Exception as e:
            self.server_error.emit(str(e))
    
    def stop_server(self):
        """停止服务"""
        self.should_stop = True
        if self.process:
            self.process.terminate()
            self.process = None
        self.server_stopped.emit()
        self.quit()


class Plugin(PluginBase):
    """Support Web Toolkit Plugin"""
    
    # 插件元信息
    NAME = "support_web_toolkit"
    DISPLAY_NAME = "Finance IT Support Web Toolkit"
    DESCRIPTION = "IT Support Web Toolkit with common utilities"
    VERSION = "1.0.0"
    AUTHOR = "Tearsyu"
    
    def __init__(self, app=None):
        super().__init__(app)
        self.i18n_manager = get_i18n_manager()
        self.server_thread: Optional[StreamlitServerThread] = None
        self.server_status = "stopped"  # stopped, starting, running, stopping
        self.server_url = ""
        
        # 连接语言变更信号
        self.i18n_manager.language_changed.connect(self.on_language_changed)
        self.i18n_manager.language_changed.connect(lambda lang: self.set_language(lang))
        
        # 状态检查定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._check_server_status)
        self.status_timer.start(5000)  # 每5秒检查一次
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            self.log_info("[Web Toolkit] 🚀 插件初始化开始")
            
            # 读取配置
            self.port = self.get_setting('port', 8501)
            self.host = self.get_setting('host', 'localhost')
            if isinstance(self.host, list):
                self.host = self.host[-1]  # 取最后一个作为默认值
            
            self._initialized = True
            self.log_info("[Web Toolkit] ✅ 插件初始化完成")
            return True
            
        except Exception as e:
            self.log_error(f"[Web Toolkit] ❌ 插件初始化失败: {e}")
            return False
    
    def create_widget(self) -> QWidget:
        """创建插件界面"""
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 创建主容器
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        self.title_label = QLabel(self.tr("plugin.web_toolkit.name"))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        

        
        # 工具按钮区域
        self.tools_group = QGroupBox(self.tr("plugin.web_toolkit.tools_section"))
        tools_layout = QGridLayout(self.tools_group)
        
        # JSON格式化工具
        self.json_button = self._create_tool_button(
            self.tr("plugin.web_toolkit.json_formatter"),
            self.tr("plugin.web_toolkit.json_formatter_desc"),
            "#28a745",
            lambda: self._open_tool("/json-formatter")
        )
        tools_layout.addWidget(self.json_button, 0, 0)
        
        # 时差转换工具
        self.timezone_button = self._create_tool_button(
            self.tr("plugin.web_toolkit.timezone_converter"),
            self.tr("plugin.web_toolkit.timezone_converter_desc"),
            "#007bff",
            lambda: self._open_tool("/timezone-converter")
        )
        tools_layout.addWidget(self.timezone_button, 0, 1)
        
        # Markdown编辑器
        self.markdown_button = self._create_tool_button(
            self.tr("plugin.web_toolkit.markdown_editor"),
            self.tr("plugin.web_toolkit.markdown_editor_desc"),
            "#6f42c1",
            lambda: self._open_tool("/markdown-editor")
        )
        tools_layout.addWidget(self.markdown_button, 1, 0, 1, 2)
        
        layout.addWidget(self.tools_group)
        
        # 服务状态区域
        self.status_group = QGroupBox(self.tr("plugin.web_toolkit.status_section"))
        status_layout = QVBoxLayout(self.status_group)
        
        # 状态显示
        status_info_layout = QHBoxLayout()
        self.status_label = QLabel(self.tr("plugin.web_toolkit.status_stopped"))
        self.status_label.setStyleSheet("font-weight: bold; color: #dc3545;")
        status_info_layout.addWidget(self.status_label)
        
        status_info_layout.addStretch()
        
        self.url_label = QLabel("")
        self.url_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        status_info_layout.addWidget(self.url_label)
        
        status_layout.addLayout(status_info_layout)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        
        self.start_button = QPushButton(self.tr("plugin.web_toolkit.start_server"))
        self.start_button.clicked.connect(self._start_server)
        self.start_button.setStyleSheet(
            "QPushButton {"
            "    background-color: #28a745;"
            "    color: white;"
            "    border: none;"
            "    padding: 8px 16px;"
            "    border-radius: 4px;"
            "    font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "    background-color: #218838;"
            "}"
            "QPushButton:disabled {"
            "    background-color: #6c757d;"
            "}"
        )
        control_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton(self.tr("plugin.web_toolkit.stop_server"))
        self.stop_button.clicked.connect(self._stop_server)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet(
            "QPushButton {"
            "    background-color: #dc3545;"
            "    color: white;"
            "    border: none;"
            "    padding: 8px 16px;"
            "    border-radius: 4px;"
            "    font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "    background-color: #c82333;"
            "}"
            "QPushButton:disabled {"
            "    background-color: #6c757d;"
            "}"
        )
        control_layout.addWidget(self.stop_button)
        
        self.refresh_button = QPushButton(self.tr("plugin.web_toolkit.refresh_status"))
        self.refresh_button.clicked.connect(self._check_server_status)
        self.refresh_button.setStyleSheet(
            "QPushButton {"
            "    background-color: #6c757d;"
            "    color: white;"
            "    border: none;"
            "    padding: 8px 16px;"
            "    border-radius: 4px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #545b62;"
            "}"
        )
        control_layout.addWidget(self.refresh_button)
        
        control_layout.addStretch()
        
        status_layout.addLayout(control_layout)
        layout.addWidget(self.status_group)
        
        # 日志显示区域
        self.log_group = QGroupBox(self.tr("plugin.web_toolkit.log_section"))
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
        self.log_text.append("[INFO] Web Toolkit Plugin UI Created.")
        self.log_text.append(f"[INFO] Server Configuration - Host: {self.host}, Port: {self.port}")
        
        log_layout.addWidget(self.log_text)
        
        # 清空日志按钮
        self.clear_log_button = QPushButton(self.tr("plugin.web_toolkit.clear_log"))
        self.clear_log_button.clicked.connect(self._clear_log)
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
        
        # 将widget设置为滚动区域的内容
        scroll_area.setWidget(widget)
        
        self.log_info("[Web Toolkit] ✅ UI界面创建完成")
        
        return scroll_area
    
    def _create_tool_button(self, title: str, description: str, color: str, callback) -> QPushButton:
        """创建工具按钮"""
        button = QPushButton(f"{title}\n{description}")
        button.clicked.connect(callback)
        
        button.setStyleSheet(
            f"QPushButton {{"
            f"    background-color: {color};"
            f"    color: white;"
            f"    border: none;"
            f"    border-radius: 8px;"
            f"    min-height: 80px;"
            f"    font-weight: bold;"
            f"    font-size: 12px;"
            f"    text-align: center;"
            f"    padding: 10px;"
            f"}}"
            f"QPushButton:hover {{"
            f"    background-color: {self._darken_color(color)};"
            f"}}"
            f"QPushButton:pressed {{"
            f"    background-color: {self._darken_color(color, 0.8)};"
            f"}}"
        )
        
        return button
    
    def _darken_color(self, color: str, factor: float = 0.9) -> str:
        """使颜色变暗"""
        # 简单的颜色变暗实现
        color_map = {
            "#28a745": "#218838",
            "#007bff": "#0056b3",
            "#6f42c1": "#5a32a3"
        }
        return color_map.get(color, color)
    
    def _start_server(self):
        """启动Streamlit服务"""
        if self.server_status in ["running", "starting"]:
            return
        
        self.server_status = "starting"
        self._update_status_ui()
        
        self.log_info("[Web Toolkit] 🚀 正在启动Streamlit服务...")
        self.log_text.append(f"[INFO] {self.tr('plugin.web_toolkit.server_starting')}")
        
        # 启动服务器线程
        self.server_thread = StreamlitServerThread(self.port, self.host)
        self.server_thread.server_started.connect(self._on_server_started)
        self.server_thread.server_stopped.connect(self._on_server_stopped)
        self.server_thread.server_error.connect(self._on_server_error)
        self.server_thread.start()
    
    def _stop_server(self):
        """停止Streamlit服务"""
        if self.server_status in ["stopped", "stopping"]:
            return
        
        self.server_status = "stopping"
        self._update_status_ui()
        
        self.log_info("[Web Toolkit] 🛑 正在停止Streamlit服务...")
        self.log_text.append(f"[INFO] {self.tr('plugin.web_toolkit.server_stopping')}")
        
        if self.server_thread:
            self.server_thread.stop_server()
    
    def _on_server_started(self, url: str):
        """服务启动成功回调"""
        self.server_status = "running"
        self.server_url = url
        self._update_status_ui()
        
        self.log_info(f"[Web Toolkit] ✅ Streamlit服务启动成功: {url}")
        self.log_text.append(f"[INFO] {self.tr('plugin.web_toolkit.server_started')} - {url}")
        self.show_status_message(self.tr("plugin.web_toolkit.server_started"))
    
    def _on_server_stopped(self):
        """服务停止回调"""
        self.server_status = "stopped"
        self.server_url = ""
        self._update_status_ui()
        
        self.log_info("[Web Toolkit] 🛑 Streamlit服务已停止")
        self.log_text.append(f"[INFO] {self.tr('plugin.web_toolkit.server_stopped')}")
        self.show_status_message(self.tr("plugin.web_toolkit.server_stopped"))
    
    def _on_server_error(self, error: str):
        """服务错误回调"""
        self.server_status = "stopped"
        self.server_url = ""
        self._update_status_ui()
        
        self.log_error(f"[Web Toolkit] ❌ Streamlit服务错误: {error}")
        self.log_text.append(f"[ERROR] Server Error: {error}")
        self.show_status_message(f"Server Error: {error}")
    
    def _update_status_ui(self):
        """更新状态UI"""
        if not hasattr(self, 'status_label'):
            return
        
        status_text = ""
        status_color = ""
        
        if self.server_status == "running":
            status_text = self.tr("plugin.web_toolkit.status_running")
            status_color = "#28a745"
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
        elif self.server_status == "stopped":
            status_text = self.tr("plugin.web_toolkit.status_stopped")
            status_color = "#dc3545"
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
        elif self.server_status == "starting":
            status_text = self.tr("plugin.web_toolkit.status_starting")
            status_color = "#ffc107"
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(False)
        elif self.server_status == "stopping":
            status_text = self.tr("plugin.web_toolkit.status_stopping")
            status_color = "#ffc107"
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(False)
        
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet(f"font-weight: bold; color: {status_color};")
        
        if self.server_url:
            self.url_label.setText(self.tr("plugin.web_toolkit.server_url").format(url=self.server_url))
        else:
            self.url_label.setText("")
    
    def _check_server_status(self):
        """检查服务器状态"""
        if self.server_status == "running" and self.server_url:
            try:
                response = requests.get(self.server_url, timeout=2)
                if response.status_code != 200:
                    # 服务可能已停止
                    self._on_server_stopped()
            except:
                # 连接失败，服务可能已停止
                self._on_server_stopped()
    
    def _open_tool(self, path: str):
        """打开工具"""
        if self.server_status != "running":
            self.log_warning("[Web Toolkit] ⚠️ 服务未运行，正在启动服务...")
            self.log_text.append(f"[WARNING] {self.tr('plugin.web_toolkit.server_not_running')}")
            self._start_server()
            # 这里可以添加等待逻辑，或者提示用户稍后再试
            return
        
        tool_url = f"{self.server_url}{path}"
        try:
            webbrowser.open(tool_url)
            self.log_info(f"[Web Toolkit] 🌐 打开工具: {tool_url}")
            self.log_text.append(f"[INFO] {self.tr('plugin.web_toolkit.tool_opened')}: {path}")
            self.show_status_message(self.tr("plugin.web_toolkit.tool_opened"))
        except Exception as e:
            self.log_error(f"[Web Toolkit] ❌ 打开工具失败: {e}")
            self.log_text.append(f"[ERROR] Failed to open tool: {e}")
    
    def _clear_log(self):
        """清空日志"""
        self.log_text.clear()
        self.log_text.append("[INFO] Log cleared.")
        self.log_info("[Web Toolkit] 🧹 日志已清空")
        self.show_status_message(self.tr("plugin.web_toolkit.log_cleared"))
    
    def on_language_changed(self, language: str):
        """语言变更回调"""
        if hasattr(self, 'title_label'):
            self._update_ui_text()
    
    def _update_ui_text(self):
        """更新UI文本"""
        if hasattr(self, 'title_label'):
            self.title_label.setText(self.tr("plugin.web_toolkit.name"))
        if hasattr(self, 'desc_label'):
            self.desc_label.setText(self.tr("plugin.web_toolkit.description_detail"))
        if hasattr(self, 'tools_group'):
            self.tools_group.setTitle(self.tr("plugin.web_toolkit.tools_section"))
        if hasattr(self, 'status_group'):
            self.status_group.setTitle(self.tr("plugin.web_toolkit.status_section"))
        if hasattr(self, 'log_group'):
            self.log_group.setTitle(self.tr("plugin.web_toolkit.log_section"))
        
        # 更新按钮文本
        if hasattr(self, 'start_button'):
            self.start_button.setText(self.tr("plugin.web_toolkit.start_server"))
        if hasattr(self, 'stop_button'):
            self.stop_button.setText(self.tr("plugin.web_toolkit.stop_server"))
        if hasattr(self, 'refresh_button'):
            self.refresh_button.setText(self.tr("plugin.web_toolkit.refresh_status"))
        if hasattr(self, 'clear_log_button'):
            self.clear_log_button.setText(self.tr("plugin.web_toolkit.clear_log"))
        
        # 更新工具按钮文本
        if hasattr(self, 'json_button'):
            self.json_button.setText(f"{self.tr('plugin.web_toolkit.json_formatter')}\n{self.tr('plugin.web_toolkit.json_formatter_desc')}")
        if hasattr(self, 'timezone_button'):
            self.timezone_button.setText(f"{self.tr('plugin.web_toolkit.timezone_converter')}\n{self.tr('plugin.web_toolkit.timezone_converter_desc')}")
        if hasattr(self, 'markdown_button'):
            self.markdown_button.setText(f"{self.tr('plugin.web_toolkit.markdown_editor')}\n{self.tr('plugin.web_toolkit.markdown_editor_desc')}")
        
        # 更新状态
        self._update_status_ui()
    
    def cleanup(self):
        """清理资源"""
        if self.server_thread and self.server_thread.isRunning():
            self.server_thread.stop_server()
            self.server_thread.wait(3000)  # 等待3秒
        
        if hasattr(self, 'status_timer'):
            self.status_timer.stop()
        
        self.log_info("[Web Toolkit] 🧹 插件资源清理完成")