# -*- coding: utf-8 -*-
"""
HSBC Little Worker - Ollama Vision 插件
"""

import os
import json
import requests
import base64
import traceback
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFileDialog, QGroupBox, QMessageBox, QProgressBar, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QPixmap

from core.plugin_base import PluginBase
from core.i18n import get_i18n_manager


class OllamaVisionWorker(QThread):
    """Ollama Vision API 调用工作线程"""
    
    finished = Signal(str)  # 完成信号
    error = Signal(str)     # 错误信号
    
    def __init__(self, host: str, port: int, model: str, image_path: str, prompt: str):
        super().__init__()
        self.host = host
        self.port = port
        self.model = model
        self.image_path = image_path
        self.prompt = prompt
    
    def run(self):
        """执行 Ollama Vision API 调用"""
        try:
            # 读取图片并转换为 base64
            with open(self.image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 构建请求数据
            url = f"{self.host}:{self.port}/api/generate"
            data = {
                "model": self.model,
                "prompt": self.prompt,
                "images": [image_data],
                "stream": False
            }
            
            # 发送请求
            response = requests.post(url, json=data, timeout=60)
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            if 'response' in result:
                self.finished.emit(result['response'])
            else:
                self.error.emit("API 响应格式错误")
                
        except FileNotFoundError:
            self.error.emit("图片文件不存在")
        except requests.exceptions.RequestException as e:
            self.error.emit(f"网络请求失败: {str(e)}")
        except Exception as e:
            self.error.emit(f"处理失败: {str(e)}")


class Plugin(PluginBase):
    """Ollama Vision Plugin class"""
    
    # 插件元信息
    NAME = "ollama_vision"
    DISPLAY_NAME = "Ollama Vision"
    DESCRIPTION = "使用 Ollama Vision 模型分析图片内容"
    VERSION = "1.0.0"
    AUTHOR = "Tearsyu"
    
    def __init__(self, app=None):
        super().__init__(app)
        self.i18n_manager = get_i18n_manager()
        self.selected_image_path: Optional[str] = None
        self.worker_thread: Optional[OllamaVisionWorker] = None
        
        # 连接语言变更信号
        self.i18n_manager.language_changed.connect(self.on_language_changed)
        self.i18n_manager.language_changed.connect(lambda lang: self.set_language(lang))
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            self.log_info("[Ollama Vision] 🚀 插件初始化中...")
            
            # 验证配置
            host = self.get_setting('host', 'http://127.0.0.1')
            port = self.get_setting('port', 11434)
            model = self.get_setting('model', 'gemma3:4b')
            
            # self.log_info(f"[Ollama Vision] ⚙️ 配置信息 - Host: {host}:{port}, Model: {model}")
            
            self._initialized = True
            self.log_info("[Ollama Vision] ✅ 插件初始化完成")
            return True
            
        except Exception as e:
            self.log_error(f"[Ollama Vision] ❌ 插件初始化失败: {e} - {traceback.format_exc()}")
            return False
    
    def create_widget(self) -> QWidget:
        """创建插件界面"""
        # 创建主容器
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 创建内容widget
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        self.title_label = QLabel(self.tr("plugin.ollama_vision.title"))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # 描述
        self.desc_label = QLabel(self.tr("plugin.ollama_vision.description"))
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
        
        # 文件选择区域
        self.file_group = QGroupBox(self.tr("plugin.ollama_vision.file_selection"))
        file_layout = QVBoxLayout(self.file_group)
        
        # 文件选择按钮和路径显示
        file_button_layout = QHBoxLayout()
        
        self.select_file_button = QPushButton(self.tr("plugin.ollama_vision.select_image"))
        self.select_file_button.clicked.connect(self._on_select_file)
        self.select_file_button.setStyleSheet(
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
        )
        file_button_layout.addWidget(self.select_file_button)
        
        self.file_path_label = QLabel(self.tr("plugin.ollama_vision.no_file_selected"))
        self.file_path_label.setStyleSheet(
            "QLabel {"
            "    background-color: #f8f9fa;"
            "    border: 1px solid #dee2e6;"
            "    border-radius: 4px;"
            "    padding: 8px;"
            "    color: #6c757d;"
            "}"
        )
        file_button_layout.addWidget(self.file_path_label, 1)
        
        file_layout.addLayout(file_button_layout)
        layout.addWidget(self.file_group)
        
        # Prompt 编写区域
        self.prompt_group = QGroupBox(self.tr("plugin.ollama_vision.prompt_input"))
        prompt_layout = QVBoxLayout(self.prompt_group)
        
        self.prompt_text = QTextEdit()
        self.prompt_text.setMaximumHeight(120)
        self.prompt_text.setPlainText(self._get_config_field('prompt', 'Please extract the text from the image, return in json format.'))
        
        # 加载上次的响应
        last_response = self._get_config_field('last_response', '')
        if last_response:
            self.response_text.setPlainText(last_response)
        self.prompt_text.setStyleSheet(
            "QTextEdit {"
            "    background-color: #ffffff;"
            "    border: 1px solid #dee2e6;"
            "    border-radius: 4px;"
            "    padding: 8px;"
            "    font-family: 'Consolas', 'Monaco', monospace;"
            "    font-size: 12px;"
            "}"
        )
        prompt_layout.addWidget(self.prompt_text)
        
        # 分析按钮
        self.analyze_button = QPushButton(self.tr("plugin.ollama_vision.analyze_image"))
        self.analyze_button.clicked.connect(self._on_analyze_image)
        self.analyze_button.setEnabled(False)
        self.analyze_button.setStyleSheet(
            "QPushButton {"
            "    background-color: #28a745;"
            "    color: white;"
            "    border: none;"
            "    padding: 10px 20px;"
            "    border-radius: 4px;"
            "    font-weight: bold;"
            "    font-size: 14px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #218838;"
            "}"
            "QPushButton:disabled {"
            "    background-color: #6c757d;"
            "}"
        )
        prompt_layout.addWidget(self.analyze_button)
        
        layout.addWidget(self.prompt_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(
            "QProgressBar {"
            "    border: 1px solid #dee2e6;"
            "    border-radius: 4px;"
            "    text-align: center;"
            "}"
            "QProgressBar::chunk {"
            "    background-color: #007bff;"
            "    border-radius: 3px;"
            "}"
        )
        layout.addWidget(self.progress_bar)
        
        # AI 回复显示区域
        self.response_group = QGroupBox(self.tr("plugin.ollama_vision.ai_response"))
        response_layout = QVBoxLayout(self.response_group)
        
        self.response_text = QTextEdit()
        self.response_text.setReadOnly(True)
        self.response_text.setStyleSheet(
            "QTextEdit {"
            "    background-color: #f8f9fa;"
            "    border: 1px solid #dee2e6;"
            "    border-radius: 4px;"
            "    padding: 10px;"
            "    font-family: 'Consolas', 'Monaco', monospace;"
            "    font-size: 11px;"
            "}"
        )
        response_layout.addWidget(self.response_text)
        
        # 清空回复按钮
        self.clear_response_button = QPushButton(self.tr("plugin.ollama_vision.clear_response"))
        self.clear_response_button.clicked.connect(self._on_clear_response)
        self.clear_response_button.setStyleSheet(
            "QPushButton {"
            "    background-color: #dc3545;"
            "    color: white;"
            "    border: none;"
            "    padding: 6px 12px;"
            "    border-radius: 4px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #c82333;"
            "}"
        )
        response_layout.addWidget(self.clear_response_button)
        
        layout.addWidget(self.response_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 将内容widget设置到滚动区域
        scroll_area.setWidget(content_widget)
        
        # 将滚动区域添加到主布局
        main_layout.addWidget(scroll_area)
        
        self.log_info("[Ollama Vision] 🎨 UI界面创建完成")
        
        return widget
    
    def _on_select_file(self):
        """选择图片文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            self.tr("plugin.ollama_vision.select_image_dialog"),
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff);;All Files (*)"
        )
        
        if file_path:
            self.selected_image_path = file_path
            self.file_path_label.setText(os.path.basename(file_path))
            self.file_path_label.setToolTip(file_path)
            self.analyze_button.setEnabled(True)
            
            self.log_info(f"[Ollama Vision] 📁 已选择图片: {file_path}")
            self.show_status_message(self.tr("plugin.ollama_vision.file_selected"))
    
    def _on_analyze_image(self):
        """分析图片"""
        if not self.selected_image_path:
            QMessageBox.warning(None, "警告", self.tr("plugin.ollama_vision.no_image_warning"))
            return
        
        prompt = self.prompt_text.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(None, "警告", self.tr("plugin.ollama_vision.no_prompt_warning"))
            return
        
        # 保存当前提示词到配置文件
        self._save_config_field('prompt', prompt)
        
        # 开始分析
        self._start_analysis()
    
    def _start_analysis(self):
        """开始图片分析"""
        try:
            # 获取配置
            host = self.get_setting('host', 'http://127.0.0.1')
            port = self.get_setting('port', 11434)
            model = self.get_setting('model', 'gemma3:4b')
            prompt = self.prompt_text.toPlainText().strip()
            
            # 更新UI状态
            self.analyze_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # 无限进度条
            
            # 创建工作线程
            self.worker_thread = OllamaVisionWorker(
                host, port, model, self.selected_image_path, prompt
            )
            self.worker_thread.finished.connect(self._on_analysis_finished)
            self.worker_thread.error.connect(self._on_analysis_error)
            self.worker_thread.start()
            
            self.log_info(f"[Ollama Vision] 🔍 开始分析图片: {os.path.basename(self.selected_image_path)}")
            self.show_status_message(self.tr("plugin.ollama_vision.analyzing"))
            
        except Exception as e:
            self.log_error(f"[Ollama Vision] ❌ 启动分析失败: {e} - {traceback.format_exc()}")
            self._reset_ui_state()
    
    def _on_analysis_finished(self, response: str):
        """分析完成处理"""
        self.response_text.setPlainText(response)
        
        # 保存响应到配置文件
        self._save_config_field('last_response', response)
        
        self._reset_ui_state()
        
        self.log_info("[Ollama Vision] ✅ 图片分析完成")
        self.show_status_message(self.tr("plugin.ollama_vision.analysis_complete"))
    
    def _on_analysis_error(self, error_msg: str):
        """分析错误处理"""
        self.response_text.setPlainText(f"错误: {error_msg}")
        self._reset_ui_state()
        
        self.log_error(f"[Ollama Vision] ❌ 分析失败: {error_msg}")
        self.show_status_message(self.tr("plugin.ollama_vision.analysis_failed"))
        
        QMessageBox.critical(None, "错误", f"分析失败:\n{error_msg}")
    
    def _reset_ui_state(self):
        """重置UI状态"""
        self.analyze_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread = None
    
    def _on_clear_response(self):
        """清空回复"""
        self.response_text.clear()
        self.log_info("[Ollama Vision] 🧹 已清空回复内容")
        self.show_status_message(self.tr("plugin.ollama_vision.response_cleared"))
    
    def get_plugin_dir(self):
        """获取插件目录路径"""
        return str(self._plugin_dir) if self._plugin_dir else ''
    
    def _save_config_field(self, key: str, value):
        """保存字段到config.json的根级别"""
        try:
            config_path = os.path.join(self.get_plugin_dir(), 'config.json')
            config = {}
            
            # 读取现有配置
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            # 更新字段
            config[key] = value
            
            # 保存配置
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.log_error(f"[Ollama Vision] ❌ 保存配置字段失败: {e}")
    
    def _get_config_field(self, key: str, default_value=None):
        """从config.json的根级别读取字段"""
        try:
            config_path = os.path.join(self.get_plugin_dir(), 'config.json')
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get(key, default_value)
            
            return default_value
            
        except Exception as e:
            self.log_error(f"[Ollama Vision] ❌ 读取配置字段失败: {e}")
            return default_value
    
    def cleanup(self):
        """清理插件资源"""
        try:
            # 停止工作线程
            if self.worker_thread and self.worker_thread.isRunning():
                self.worker_thread.quit()
                self.worker_thread.wait()
                self.worker_thread = None
            
            # 保存当前 prompt
            if hasattr(self, 'prompt_text'):
                current_prompt = self.prompt_text.toPlainText().strip()
                if current_prompt:
                    self._save_config_field('prompt', current_prompt)
            
            self.log_info("[Ollama Vision] 🧹 插件资源清理完成")
            
        except Exception as e:
            self.log_error(f"[Ollama Vision] ❌ 清理失败: {e} - {traceback.format_exc()}")
        
        # 调用父类清理方法
        super().cleanup()
    
    def on_language_changed(self):
        """语言变更时更新界面文本"""
        if hasattr(self, 'title_label'):
            self.title_label.setText(self.tr("plugin.ollama_vision.title"))
        if hasattr(self, 'desc_label'):
            self.desc_label.setText(self.tr("plugin.ollama_vision.description"))
        if hasattr(self, 'file_group'):
            self.file_group.setTitle(self.tr("plugin.ollama_vision.file_selection"))
        if hasattr(self, 'select_file_button'):
            self.select_file_button.setText(self.tr("plugin.ollama_vision.select_image"))
        if hasattr(self, 'prompt_group'):
            self.prompt_group.setTitle(self.tr("plugin.ollama_vision.prompt_input"))
        if hasattr(self, 'analyze_button'):
            self.analyze_button.setText(self.tr("plugin.ollama_vision.analyze_image"))
        if hasattr(self, 'response_group'):
            self.response_group.setTitle(self.tr("plugin.ollama_vision.ai_response"))
        if hasattr(self, 'clear_response_button'):
            self.clear_response_button.setText(self.tr("plugin.ollama_vision.clear_response"))
        if hasattr(self, 'file_path_label') and not self.selected_image_path:
            self.file_path_label.setText(self.tr("plugin.ollama_vision.no_file_selected"))