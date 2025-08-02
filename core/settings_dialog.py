# -*- coding: utf-8 -*-
"""
HSBC Little Worker - 设置对话框
"""

import traceback
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QWidget, QLabel, QComboBox, QPushButton, QGroupBox,
    QCheckBox, QSlider, QSpinBox, QFormLayout, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from utils.logger import logger
from .i18n import get_i18n_manager, tr


class SettingsDialog(QDialog):
    """设置对话框"""
    
    # 信号定义
    settings_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 获取国际化管理器
        self.i18n_manager = get_i18n_manager()
        
        # 初始化UI
        self._init_ui()
        
        # 加载当前设置
        self._load_settings()
        
        # 连接信号
        self._connect_signals()
        
        logger.debug("[SETTINGS] Settings dialog initialized.")
    
    def _init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle(tr("settings.title"))
        self.setModal(True)
        self.setFixedSize(500, 400)
        self.setObjectName("settings-dialog")
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 创建标签页容器
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("settings-tab-widget")
        main_layout.addWidget(self.tab_widget)
        
        # 创建各个设置页面
        self._create_appearance_tab()
        self._create_language_tab()
        
        # 创建按钮区域
        button_layout = self._create_button_area()
        main_layout.addLayout(button_layout)
    

    
    def _create_appearance_tab(self):
        """创建外观设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # 外观设置组
        appearance_group = QGroupBox(tr("settings.appearance"))
        appearance_layout = QFormLayout(appearance_group)
        
        # 字体大小设置
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(8, 24)
        self.font_size_spinbox.setValue(11)
        appearance_layout.addRow(tr("settings.font_size") + ":", self.font_size_spinbox)
        
        # 窗口透明度设置
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(50, 100)
        self.opacity_slider.setValue(100)
        self.opacity_label = QLabel("100%")
        
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        
        appearance_layout.addRow(tr("settings.opacity") + ":", opacity_layout)
        
        layout.addWidget(appearance_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, tr("settings.appearance"))
    
    def _create_language_tab(self):
        """创建语言设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # 语言设置组
        language_group = QGroupBox(tr("settings.language"))
        language_layout = QFormLayout(language_group)
        
        self.language_combo = QComboBox()
        
        # 获取可用语言
        available_languages = self.i18n_manager.get_available_languages()
        current_language = self.i18n_manager.get_current_language()
        
        for lang_code, lang_name in available_languages.items():
            self.language_combo.addItem(lang_name, lang_code)
            if lang_code == current_language:
                self.language_combo.setCurrentText(lang_name)
        
        language_layout.addRow(tr("settings.language") + ":", self.language_combo)
        
        layout.addWidget(language_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, tr("settings.language"))
    
    def _create_button_area(self):
        """创建按钮区域"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 重置按钮
        self.reset_button = QPushButton(tr("settings.reset"))
        self.reset_button.clicked.connect(self._reset_settings)
        button_layout.addWidget(self.reset_button)
        
        # 应用按钮
        self.apply_button = QPushButton(tr("settings.apply"))
        self.apply_button.clicked.connect(self._apply_settings)
        button_layout.addWidget(self.apply_button)
        
        # 确定按钮
        self.ok_button = QPushButton(tr("settings.ok"))
        self.ok_button.clicked.connect(self._ok_clicked)
        button_layout.addWidget(self.ok_button)
        
        # 取消按钮
        self.cancel_button = QPushButton(tr("settings.cancel"))
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        return button_layout
    
    def _connect_signals(self):
        """连接信号"""
        # 透明度滑块变化时更新标签
        self.opacity_slider.valueChanged.connect(
            lambda value: self.opacity_label.setText(f"{value}%")
        )
        
        # 语言变化时立即应用
        self.language_combo.currentTextChanged.connect(self._on_language_changed)
    
    def _get_config_path(self):
        """获取配置文件路径"""
        import os
        return os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "config", 
            "app_config.json"
        )
    
    def _load_config(self):
        """加载配置文件"""
        import os
        import json
        
        config_path = self._get_config_path()
        
        if not os.path.exists(config_path):
            logger.warning("[SETTINGS] Config file not found, using default settings")
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"[SETTINGS] Failed to load config: {e} - {traceback.format_exc()}")
            return {}
    
    def _save_config(self, config):
        """保存配置文件"""
        import os
        import json
        
        try:
            config_path = self._get_config_path()
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"[SETTINGS] Failed to save config: {e} - {traceback.format_exc()}")
            return False
    
    def _load_settings(self):
        """加载当前设置"""
        try:
            config = self._load_config()
            if not config:
                return
            
            # 获取UI设置
            ui_settings = config.get("ui_settings", {})
            
            # 加载字体大小设置
            font_size = ui_settings.get("font_size", 11)
            self.font_size_spinbox.setValue(font_size)
            
            # 加载窗口透明度设置
            opacity = ui_settings.get("window_opacity", 1.0)
            opacity_percent = int(opacity * 100)
            self.opacity_slider.setValue(opacity_percent)
            
            # 加载语言设置
            language = ui_settings.get("language", "en_US")
            for i in range(self.language_combo.count()):
                if self.language_combo.itemData(i) == language:
                    self.language_combo.setCurrentIndex(i)
                    break
            

            
            logger.debug("[SETTINGS] Settings loaded successfully")
            
        except Exception as e:
            logger.error(f"[SETTINGS] Failed to load settings: {e} - {traceback.format_exc()}")
            self._reset_settings()
    
    def _apply_settings(self):
        """应用设置"""
        try:
            # 读取现有配置
            config = self._load_config()
            
            # 确保ui_settings存在
            if "ui_settings" not in config:
                config["ui_settings"] = {}
            
            # 应用语言设置
            selected_language = self.language_combo.currentData()
            if selected_language:
                self.i18n_manager.set_language(selected_language)
                config["ui_settings"]["language"] = selected_language
                logger.info(f"[SETTINGS] 🌐 Language updated: {selected_language}")
            
            # 应用字体大小设置
            font_size = self.font_size_spinbox.value()
            config["ui_settings"]["font_size"] = font_size
            logger.info(f"[SETTINGS] 🔤 Font size updated: {font_size}")
            
            # 应用透明度设置
            opacity = self.opacity_slider.value()
            config["ui_settings"]["window_opacity"] = opacity / 100.0
            if self.parent():
                self.parent().setWindowOpacity(opacity / 100.0)
            logger.info(f"[SETTINGS] 🔍 Window opacity updated: {opacity}%")
            

            
            # 保存配置到文件
            if self._save_config(config):
                # 发送设置变更信号
                self.settings_changed.emit()
                logger.info("[SETTINGS] ✅ Settings applied and saved")
            else:
                logger.error("[SETTINGS] ❌ Failed to save settings")
            
        except Exception as e:
            logger.error(f"[SETTINGS] ❌ Failed to apply settings: {e} - {traceback.format_exc()}")
    
    def _reset_settings(self):
        """重置设置为默认值"""
        # 重置为默认值
        self.font_size_spinbox.setValue(11)  # 默认字体大小
        self.opacity_slider.setValue(100)    # 默认透明度
        self.language_combo.setCurrentIndex(0)  # 默认语言

        
        logger.info("[SETTINGS] 🔄 Settings reset to default values")
    
    def _ok_clicked(self):
        """确定按钮点击事件"""
        self._apply_settings()
        self.accept()
    
    def _on_language_changed(self):
        """语言变化时的处理"""
        selected_language = self.language_combo.currentData()
        if selected_language and selected_language != self.i18n_manager.get_current_language():
            # 立即切换语言
            self.i18n_manager.set_language(selected_language)
            # 更新对话框界面文本
            self._update_ui_text()
            # 通知父窗口更新
            if self.parent() and hasattr(self.parent(), 'on_language_changed'):
                self.parent().on_language_changed()
    
    def _update_ui_text(self):
        """更新界面文本"""
        self.setWindowTitle(tr("settings.title"))
        
        # 更新标签页标题
        self.tab_widget.setTabText(0, tr("settings.appearance"))
        self.tab_widget.setTabText(1, tr("settings.language"))
        
        # 更新按钮文本
        self.reset_button.setText(tr("settings.reset"))
        self.apply_button.setText(tr("settings.apply"))
        self.ok_button.setText(tr("settings.ok"))
        self.cancel_button.setText(tr("settings.cancel"))