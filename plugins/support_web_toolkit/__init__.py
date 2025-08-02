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
            import sys
            from pathlib import Path
            
            # 获取当前插件目录
            plugin_dir = Path(__file__).parent
            app_file = plugin_dir / "streamlit_app.py"
            
            # 构建Streamlit启动命令
            cmd = [
                sys.executable, "-m", "streamlit", "run", 
                str(app_file),
                "--server.port", str(self.port),
                "--server.address", self.host,
                "--server.headless", "true",
                "--browser.gatherUsageStats", "false"
            ]
            
            # 启动Streamlit服务
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(plugin_dir)
            )
            
            # 等待服务启动
            time.sleep(3)
            
            if not self.should_stop and self.process and self.process.poll() is None:
                url = f"http://{self.host}:{self.port}"
                self.server_started.emit(url)
                
                # 保持线程运行，监控进程状态
                while not self.should_stop and self.process and self.process.poll() is None:
                    time.sleep(1)
                    
                # 如果进程意外退出
                if self.process and self.process.poll() is not None and not self.should_stop:
                    stderr_output = self.process.stderr.read().decode() if self.process.stderr else ""
                    self.server_error.emit(f"Streamlit process exited unexpectedly: {stderr_output}")
            elif self.process and self.process.poll() is not None:
                stderr_output = self.process.stderr.read().decode() if self.process.stderr else ""
                self.server_error.emit(f"Failed to start Streamlit: {stderr_output}")
                    
        except Exception as e:
            self.server_error.emit(str(e))
    
    def stop_server(self):
        """停止服务"""
        self.should_stop = True
        if self.process:
            try:
                # 首先尝试优雅终止
                self.process.terminate()
                # 等待进程优雅退出
                try:
                    self.process.wait(timeout=10)  # 增加等待时间到10秒
                except subprocess.TimeoutExpired:
                    # 如果优雅退出失败，强制终止
                    self.process.kill()
                    self.process.wait(timeout=5)  # 等待强制终止完成
            except Exception as e:
                # 如果终止过程出错，记录错误但继续清理
                print(f"Error stopping process: {e}")
            finally:
                self.process = None
        
        # 发送停止信号
        self.server_stopped.emit()


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
        self.pending_tool_path = None  # 待打开的工具路径
        
        # 连接语言变更信号
        self.i18n_manager.language_changed.connect(self.on_language_changed)
        self.i18n_manager.language_changed.connect(lambda lang: self.set_language(lang))
        
        # 状态检查定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._check_server_status)
        # 不在初始化时启动定时器，只在服务运行时启动
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            self.log_info("[Web Toolkit] 🚀 Plugin initialization started")
            
            # 读取配置
            self.port = self.get_setting('port', 8501)
            self.host = self.get_setting('host', 'localhost')
            if isinstance(self.host, list):
                self.host = self.host[-1]  # 取最后一个作为默认值
            
            self._initialized = True
            self.log_info("[Web Toolkit] ✅ Plugin initialization completed")
            return True
            
        except Exception as e:
            self.log_error(f"[Web Toolkit] ❌ Plugin initialization failed: {e}")
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
            lambda: self._open_tool("/JSON_Formatter")
        )
        tools_layout.addWidget(self.json_button, 0, 0)
        
        # 时差转换工具
        self.timezone_button = self._create_tool_button(
            self.tr("plugin.web_toolkit.timezone_converter"),
            self.tr("plugin.web_toolkit.timezone_converter_desc"),
            "#007bff",
            lambda: self._open_tool("/Timezone_Converter")
        )
        tools_layout.addWidget(self.timezone_button, 0, 1)
        
        # Markdown编辑器
        self.markdown_button = self._create_tool_button(
            self.tr("plugin.web_toolkit.markdown_editor"),
            self.tr("plugin.web_toolkit.markdown_editor_desc"),
            "#6f42c1",
            lambda: self._open_tool("/Markdown_Editor")
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
        self.url_label.setStyleSheet("color: #6c757d; font-size: 12px; padding: 2px; border-radius: 2px;")
        self.url_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.url_label.setCursor(Qt.PointingHandCursor)
        self.url_label.mouseDoubleClickEvent = self._copy_url_to_clipboard
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
        
        # Refresh button removed as requested
        
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
        
        # 如果正在停止，等待停止完成
        if self.server_status == "stopping":
            self.log_warning("[Web Toolkit] ⚠️ Server is stopping, please try again later")
            self.log_text.append("[WARNING] Server is stopping, please try again later")
            return
        
        # 清理之前的线程实例
        if self.server_thread:
            if self.server_thread.isRunning():
                self.log_warning("[Web Toolkit] ⚠️ Detected running service thread, cleaning up...")
                self.server_thread.stop_server()
                self.server_thread.wait(3000)  # 等待3秒
            self.server_thread.deleteLater()
            self.server_thread = None
        
        self.server_status = "starting"
        self._update_status_ui()
        
        self.log_info("[Web Toolkit] 🚀 Starting Streamlit service...")
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
        
        self.log_info("[Web Toolkit] 🛑 Stopping Streamlit service...")
        self.log_text.append(f"[INFO] {self.tr('plugin.web_toolkit.server_stopping')}")
        
        if self.server_thread:
            # 停止服务器
            self.server_thread.stop_server()
            
            # 异步等待线程结束，避免阻塞UI
            QTimer.singleShot(100, self._wait_for_thread_finish)
    
    def _wait_for_thread_finish(self):
        """等待线程结束"""
        if self.server_thread and self.server_thread.isRunning():
            # 如果线程还在运行，继续等待
            if not self.server_thread.wait(1000):  # 等待1秒
                # 如果1秒后还没结束，继续等待
                QTimer.singleShot(100, self._wait_for_thread_finish)
                return
        
        # 线程已结束，清理资源
        if self.server_thread:
            self.server_thread.deleteLater()
            self.server_thread = None
        
        self.log_info("[Web Toolkit] ✅ Streamlit service completely stopped")
        self.log_text.append("[INFO] Server thread cleaned up successfully")
    
    def _on_server_started(self, url: str):
        """服务启动成功回调"""
        self.server_status = "running"
        self.server_url = url
        self._update_status_ui()
        
        # 启动状态检查定时器
        self.status_timer.start(10000)  # 每10秒检查一次，减少频率
        
        self.log_info(f"[Web Toolkit] ✅ Streamlit service started successfully: {url}")
        self.log_text.append(f"[INFO] {self.tr('plugin.web_toolkit.server_started')} - {url}")
        self.show_status_message(self.tr("plugin.web_toolkit.server_started"))
        
        # 检查是否有待打开的工具路径
        if self.pending_tool_path:
            tool_path = self.pending_tool_path  # 保存到局部变量
            self.log_info(f"[Web Toolkit] 🚀 Auto-opening pending tool: {tool_path}")
            self.pending_tool_path = None  # 先清空待打开路径
            # 延迟1秒后打开工具，确保服务完全启动
            QTimer.singleShot(1000, lambda: self._open_tool(tool_path))
    
    def _on_server_stopped(self):
        """服务停止回调"""
        self.server_status = "stopped"
        self.server_url = ""
        self.pending_tool_path = None  # 清空待打开路径
        self._update_status_ui()
        
        # 停止状态检查定时器
        if self.status_timer:
            self.status_timer.stop()
        
        self.log_info("[Web Toolkit] 🛑 Streamlit service stopped")
        self.log_text.append(f"[INFO] {self.tr('plugin.web_toolkit.server_stopped')}")
        self.show_status_message(self.tr("plugin.web_toolkit.server_stopped"))
    
    def _on_server_error(self, error: str):
        """服务错误回调"""
        self.server_status = "stopped"
        self.server_url = ""
        self._update_status_ui()
        
        self.log_error(f"[Web Toolkit] ❌ Streamlit service error: {error}")
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
            # 将0.0.0.0替换为localhost用于显示
            display_url = self.server_url.replace("0.0.0.0", "localhost")
            self.url_label.setText(self.tr("plugin.web_toolkit.server_url").format(url=display_url))
        else:
            self.url_label.setText("")
    
    def _check_server_status(self):
        """检查服务器状态"""
        if self.server_status == "running" and self.server_url:
            try:
                # 将0.0.0.0替换为localhost进行状态检查
                check_url = self.server_url.replace("0.0.0.0", "localhost")
                response = requests.get(check_url, timeout=2)
                if response.status_code != 200:
                    # 服务可能已停止
                    self.log_warning(f"[Web Toolkit] ⚠️ Service status check failed, status code: {response.status_code}")
                    self._on_server_stopped()
            except Exception as e:
                # 连接失败，服务可能已停止
                self.log_warning(f"[Web Toolkit] ⚠️ Service status check failed: {e}")
                self._on_server_stopped()
    
    def _open_tool(self, path: str):
        """打开工具"""
        if self.server_status != "running":
            self.log_warning("[Web Toolkit] ⚠️ Service not running, starting service...")
            self.log_text.append(f"[WARNING] {self.tr('plugin.web_toolkit.server_not_running')}")
            # 保存要打开的路径，等服务启动后自动打开
            self.pending_tool_path = path
            self._start_server()
            return
        
        # 将0.0.0.0替换为localhost，确保浏览器可以访问
        tool_url = f"{self.server_url}{path}".replace("0.0.0.0", "localhost")
        try:
            webbrowser.open(tool_url)
            self.log_info(f"[Web Toolkit] 🌐 Opening tool: {tool_url}")
            self.log_text.append(f"[INFO] {self.tr('plugin.web_toolkit.tool_opened')}: {path}")
            self.show_status_message(self.tr("plugin.web_toolkit.tool_opened"))
        except Exception as e:
            self.log_error(f"[Web Toolkit] ❌ Failed to open tool: {e}")
            self.log_text.append(f"[ERROR] Failed to open tool: {e}")
    
    def _clear_log(self):
        """清空日志"""
        self.log_text.clear()
        self.log_text.append("[INFO] Log cleared.")
        self.log_info("[Web Toolkit] 🧹 Log cleared")
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
        # Refresh button removed
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
        try:
            self.log_info("[Web Toolkit] 🧹 Starting plugin resource cleanup...")
            
            # 停止状态检查定时器
            if hasattr(self, 'status_timer') and self.status_timer:
                self.status_timer.stop()
                self.status_timer = None
            
            # 停止并清理服务器线程
            if self.server_thread:
                if self.server_thread.isRunning():
                    self.log_info("[Web Toolkit] 🛑 Stopping server thread...")
                    self.server_thread.stop_server()
                    
                    # 等待线程结束
                    if not self.server_thread.wait(5000):  # 等待5秒
                        self.log_warning("[Web Toolkit] ⚠️ Thread did not finish within 5 seconds, force terminating")
                        self.server_thread.terminate()
                        self.server_thread.wait(2000)  # 再等待2秒
                
                # 清理线程对象
                self.server_thread.deleteLater()
                self.server_thread = None
            
            # 重置状态
            self.server_status = "stopped"
            self.server_url = ""
            
            self.log_info("[Web Toolkit] ✅ Plugin resource cleanup completed")
            
        except Exception as e:
            self.log_error(f"[Web Toolkit] ❌ Error occurred during resource cleanup: {e}")
    
    def _copy_url_to_clipboard(self, event):
        """双击复制URL到剪贴板"""
        if self.server_url:
            from PySide6.QtWidgets import QApplication
            # 将0.0.0.0替换为localhost用于复制
            display_url = self.server_url.replace("0.0.0.0", "localhost")
            clipboard = QApplication.clipboard()
            clipboard.setText(display_url)
            self.show_status_message(f"URL copied to clipboard: {display_url}")
        