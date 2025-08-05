from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from core.plugin_base import PluginBase
import traceback

class Plugin(PluginBase):
    """Batch Monitor Plugin - IT Support Batch Monitor Tool"""
    
    NAME = "batch_monitor"
    DISPLAY_NAME = "Batch Monitor"
    DESCRIPTION = "IT Support Batch Monitor, a tool to check the daily and monthly file, hence reducing the toil job."
    VERSION = "1.0.0"
    AUTHOR = "Tearsyu"
    
    def __init__(self, app=None):
        super().__init__(app)
        self.main_widget = None
        self.status_label = None
        self.log_text = None
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            self.log_info("[Batch Monitor] 🚀 插件初始化开始")
            
            # 检查必要的配置项
            host = self.get_setting("host", "")
            username = self.get_setting("username", "")
            port = self.get_setting("port", 22)
            
            if not host or not username:
                self.log_warning("[Batch Monitor] ⚠️ 服务器连接配置不完整，请在设置中配置主机和用户名")
            
            self.log_info(f"[Batch Monitor] 📡 配置的服务器: {username}@{host}:{port}")
            self.log_info("[Batch Monitor] ✅ 插件初始化完成")
            
            return True
            
        except Exception as e:
            self.log_error(f"[Batch Monitor] ❌ 初始化失败: {e} - {traceback.format_exc()}")
            return False
    
    def create_widget(self) -> QWidget:
        """创建插件界面组件"""
        try:
            self.main_widget = QWidget()
            layout = QVBoxLayout(self.main_widget)
            
            # 标题
            title_label = QLabel(self.tr("plugin.batch_monitor.title"))
            title_font = QFont()
            title_font.setPointSize(16)
            title_font.setBold(True)
            title_label.setFont(title_font)
            title_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(title_label)
            
            # 状态显示
            status_layout = QHBoxLayout()
            status_layout.addStretch()
            self.status_label = QLabel(self.tr("plugin.batch_monitor.status.ready"))
            self.status_label.setStyleSheet("font-weight: bold; color: #27ae60;")
            status_layout.addWidget(self.status_label)
            status_layout.addStretch()
            layout.addLayout(status_layout)
            
            # 功能按钮区域
            button_layout = QHBoxLayout()
            
            # 连接测试按钮
            test_connection_btn = QPushButton(self.tr("plugin.batch_monitor.test_connection"))
            test_connection_btn.clicked.connect(self._test_connection)
            test_connection_btn.setStyleSheet(
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
                "QPushButton:disabled {"
                "    background-color: #6c757d;"
                "}"
            )
            button_layout.addWidget(test_connection_btn)
            
            # 开始监控按钮
            start_monitor_btn = QPushButton(self.tr("plugin.batch_monitor.start_monitor"))
            start_monitor_btn.clicked.connect(self._start_monitor)
            start_monitor_btn.setStyleSheet(
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
            button_layout.addWidget(start_monitor_btn)
            
            # 停止监控按钮
            stop_monitor_btn = QPushButton(self.tr("plugin.batch_monitor.stop_monitor"))
            stop_monitor_btn.clicked.connect(self._stop_monitor)
            stop_monitor_btn.setStyleSheet(
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
            button_layout.addWidget(stop_monitor_btn)
            
            button_layout.addStretch()
            layout.addLayout(button_layout)
            
            # 日志显示区域
            log_label = QLabel(self.tr("plugin.batch_monitor.log_title"))
            log_label.setStyleSheet("font-weight: bold;")
            layout.addWidget(log_label)
            
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
            layout.addWidget(self.log_text)
            
            # 添加初始日志
            self._add_log(self.tr("plugin.batch_monitor.log.initialized"))
            
            return self.main_widget
            
        except Exception as e:
            self.log_error(f"[Batch Monitor] ❌ 创建界面失败: {e} - {traceback.format_exc()}")
            # 返回一个简单的错误界面
            error_widget = QWidget()
            error_layout = QVBoxLayout(error_widget)
            error_label = QLabel(f"界面创建失败: {str(e)}")
            error_label.setStyleSheet("color: red;")
            error_layout.addWidget(error_label)
            return error_widget
    
    def _test_connection(self):
        """测试服务器连接"""
        try:
            self.log_info("[Batch Monitor] 🔍 开始测试服务器连接")
            self._update_status(self.tr("plugin.batch_monitor.status.testing"), "#f39c12")
            self._add_log(self.tr("plugin.batch_monitor.log.testing_connection"))
            
            # TODO: 实现实际的连接测试逻辑
            # 这里暂时模拟测试结果
            host = self.get_setting("host", "")
            username = self.get_setting("username", "")
            
            if not host or not username:
                self._update_status(self.tr("plugin.batch_monitor.status.config_error"), "#e74c3c")
                self._add_log(self.tr("plugin.batch_monitor.log.config_incomplete"))
                self.show_status_message(self.tr("plugin.batch_monitor.message.config_required"))
                return
            
            # 模拟连接测试
            self._add_log(f"正在连接到 {username}@{host}...")
            self._update_status(self.tr("plugin.batch_monitor.status.connected"), "#27ae60")
            self._add_log(self.tr("plugin.batch_monitor.log.connection_success"))
            self.show_status_message(self.tr("plugin.batch_monitor.message.connection_success"))
            
        except Exception as e:
            self.log_error(f"[Batch Monitor] ❌ 连接测试失败: {e} - {traceback.format_exc()}")
            self._update_status(self.tr("plugin.batch_monitor.status.error"), "#e74c3c")
            self._add_log(f"连接测试失败: {str(e)}")
    
    def _start_monitor(self):
        """开始监控"""
        try:
            self.log_info("[Batch Monitor] 🚀 开始批处理监控")
            self._update_status(self.tr("plugin.batch_monitor.status.monitoring"), "#27ae60")
            self._add_log(self.tr("plugin.batch_monitor.log.monitor_started"))
            
            # TODO: 实现实际的监控逻辑
            self.show_status_message(self.tr("plugin.batch_monitor.message.monitor_started"))
            
        except Exception as e:
            self.log_error(f"[Batch Monitor] ❌ 启动监控失败: {e} - {traceback.format_exc()}")
            self._update_status(self.tr("plugin.batch_monitor.status.error"), "#e74c3c")
            self._add_log(f"启动监控失败: {str(e)}")
    
    def _stop_monitor(self):
        """停止监控"""
        try:
            self.log_info("[Batch Monitor] 🛑 停止批处理监控")
            self._update_status(self.tr("plugin.batch_monitor.status.stopped"), "#f39c12")
            self._add_log(self.tr("plugin.batch_monitor.log.monitor_stopped"))
            
            # TODO: 实现实际的停止监控逻辑
            self.show_status_message(self.tr("plugin.batch_monitor.message.monitor_stopped"))
            
        except Exception as e:
            self.log_error(f"[Batch Monitor] ❌ 停止监控失败: {e} - {traceback.format_exc()}")
            self._update_status(self.tr("plugin.batch_monitor.status.error"), "#e74c3c")
            self._add_log(f"停止监控失败: {str(e)}")
    
    def _update_status(self, status_text: str, color: str):
        """更新状态显示"""
        if self.status_label:
            self.status_label.setText(status_text)
            self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def _add_log(self, message: str):
        """添加日志到界面"""
        if self.log_text:
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_text.append(f"[{timestamp}] {message}")
    
    def get_config_schema(self):
        """返回插件配置模式"""
        return {
            "host": {
                "type": "string",
                "default": "localhost",
                "description": "SSH主机地址"
            },
            "username": {
                "type": "string",
                "default": "",
                "description": "SSH用户名"
            },
            "password": {
                "type": "string",
                "default": "",
                "description": "SSH密码"
            },
            "port": {
                "type": "int",
                "default": 22,
                "description": "SSH端口"
            },
            "check_frequency": {
                "type": "int",
                "default": 30,
                "description": "检查频率（秒）"
            },
            "timeout": {
                "type": "int",
                "default": 10,
                "description": "连接超时时间（秒）"
            }
        }
    
    def cleanup(self) -> None:
        """清理插件资源"""
        try:
            self.log_info("[Batch Monitor] 🧹 开始清理插件资源")
            
            # TODO: 停止所有监控任务和定时器
            # TODO: 关闭网络连接
            # TODO: 保存配置和状态
            
            self.log_info("[Batch Monitor] ✅ 插件资源清理完成")
            
        except Exception as e:
            self.log_error(f"[Batch Monitor] ❌ 清理失败: {e} - {traceback.format_exc()}")