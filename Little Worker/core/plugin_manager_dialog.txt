# -*- coding: utf-8 -*-
"""
HSBC Little Worker - 插件管理器对话框
"""

import os
import traceback

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QScrollArea,
    QPushButton, QLabel, QGroupBox, QTextEdit, QFrame, 
    QMessageBox, QCheckBox, QSizePolicy, QLineEdit, QSpinBox, 
    QComboBox, QFormLayout
)
from PySide6.QtCore import Qt, Signal, QSize, QEvent
from PySide6.QtGui import QFont, QIcon, QPixmap, QKeySequence, QKeyEvent

from utils.logger import logger
from utils.crypto import encrypt_password, decrypt_password, is_password_field
from .i18n import tr


class KeyboardShortcutWidget(QWidget):
    """键盘快捷键输入控件"""
    
    def __init__(self, default_value=None, parent=None):
        super().__init__(parent)
        self.shortcut_text = str(default_value) if default_value else ""
        self.is_recording = False
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # 显示当前快捷键的标签
        self.shortcut_label = QLabel(self.shortcut_text or tr("plugin_manager.keyboard_shortcut_placeholder"))
        self.shortcut_label.setObjectName("keyboard-shortcut-label")
        layout.addWidget(self.shortcut_label, 1)
        
        # 录制按钮
        self.record_button = QPushButton(tr("plugin_manager.keyboard_shortcut_set"))
        self.record_button.setFixedWidth(60)
        self.record_button.clicked.connect(self._toggle_recording)
        layout.addWidget(self.record_button)
        
        # 清除按钮
        self.clear_button = QPushButton(tr("plugin_manager.keyboard_shortcut_clear"))
        self.clear_button.setFixedWidth(60)
        self.clear_button.clicked.connect(self._clear_shortcut)
        layout.addWidget(self.clear_button)
    
    def _toggle_recording(self):
        """切换录制状态"""
        if self.is_recording:
            self._stop_recording()
        else:
            self._start_recording()
    
    def _start_recording(self):
        """开始录制快捷键"""
        self.is_recording = True
        self.record_button.setText(tr("plugin_manager.keyboard_shortcut_stop"))
        self.shortcut_label.setText(tr("plugin_manager.keyboard_shortcut_recording"))
        self.shortcut_label.setObjectName("keyboard-shortcut-label-recording")
        # 设置焦点以接收按键事件
        self.setFocus()
        self.grabKeyboard()
    
    def _stop_recording(self):
        """停止录制快捷键"""
        self.is_recording = False
        self.record_button.setText(tr("plugin_manager.keyboard_shortcut_set"))
        self.releaseKeyboard()
        self._update_display()
    
    def _clear_shortcut(self):
        """清除快捷键"""
        self.shortcut_text = ""
        self._update_display()
    
    def _update_display(self):
        """更新显示"""
        display_text = self.shortcut_text or tr("plugin_manager.keyboard_shortcut_placeholder")
        self.shortcut_label.setText(display_text)
        self.shortcut_label.setObjectName("keyboard-shortcut-label")
    
    def keyPressEvent(self, event):
        """处理按键事件"""
        if not self.is_recording:
            super().keyPressEvent(event)
            return
        
        # 忽略单独的修饰键
        if event.key() in (Qt.Key_Control, Qt.Key_Alt, Qt.Key_Shift, Qt.Key_Meta):
            return
        
        # 构建快捷键字符串
        modifiers = event.modifiers()
        key_parts = []
        
        if modifiers & Qt.ControlModifier:
            key_parts.append("Ctrl")
        if modifiers & Qt.AltModifier:
            key_parts.append("Alt")
        if modifiers & Qt.ShiftModifier:
            key_parts.append("Shift")
        if modifiers & Qt.MetaModifier:
            key_parts.append("Meta")
        
        # 获取按键名称
        key_name = QKeySequence(event.key()).toString()
        if key_name:
            key_parts.append(key_name)
        
        if key_parts:
            self.shortcut_text = "+".join(key_parts)
            self._stop_recording()
    
    def get_shortcut(self):
        """获取当前快捷键"""
        return self.shortcut_text
    
    def set_shortcut(self, shortcut):
        """设置快捷键"""
        self.shortcut_text = str(shortcut) if shortcut else ""
        self._update_display()


class PluginItemWidget(QFrame):
    """插件项显示组件"""
    
    # 信号定义
    plugin_enabled_changed = Signal(str, bool)  # 插件启用状态变化信号
    plugin_config_requested = Signal(str)  # 插件配置请求信号
    
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
        self.setFrameStyle(QFrame.NoFrame)
        self.setContentsMargins(0, 0, 0, 0)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 6, 8, 6)
        main_layout.setSpacing(3)
        
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
        name_font.setPointSize(14)
        name_font.setBold(True)
        self.name_label.setFont(name_font)
        name_status_layout.addWidget(self.name_label)
        
        # 可用状态显示（移到名称右边）
        self.available_label = QLabel()
        self.available_label.setObjectName("plugin-available-label")
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
        self.info_label.setObjectName("plugin-info-label")
        name_version_layout.addWidget(self.info_label)
        
        top_layout.addLayout(name_version_layout, 1)

        # 配置按钮
        self.config_button = QPushButton()
        # self.config_button.setFixedSize(24, 24)
        self.config_button.setToolTip(tr("plugin_manager.config_tooltip"))
        
        # 设置图标路径
        self.config_icon_normal = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "plugin-config.png")
        self.config_icon_hover = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "plugin-config-hovered.png")
        
        # 设置默认图标
        if os.path.exists(self.config_icon_normal):
            self.config_button.setIcon(QIcon(self.config_icon_normal))
            self.config_button.setIconSize(QSize(16, 16))
        
        # 设置样式去掉边框
        self.config_button.setObjectName("plugin-config-button")
        
        self.config_button.clicked.connect(self._on_config_clicked)
        
        # Enabled 复选框和配置按钮的容器布局
        enabled_config_layout = QHBoxLayout()
        enabled_config_layout.setSpacing(0)  # 设置0间距让控件紧密相邻
        enabled_config_layout.setContentsMargins(0, 0, 0, 0)
        
        # Enabled 复选框
        self.enabled_label = QLabel(tr("plugin_manager.enabled"))
        self.enabled_checkbox = QCheckBox()
        self.enabled_checkbox.toggled.connect(self._on_enabled_changed)
        self._update_enabled_switch()
        enabled_config_layout.addWidget(self.enabled_label)
        enabled_config_layout.addWidget(self.enabled_checkbox)
        
        # 重写hover事件
        def on_config_button_enter(event):
            if os.path.exists(self.config_icon_hover):
                self.config_button.setIcon(QIcon(self.config_icon_hover))
            QPushButton.enterEvent(self.config_button, event)
        
        def on_config_button_leave(event):
            if os.path.exists(self.config_icon_normal):
                self.config_button.setIcon(QIcon(self.config_icon_normal))
            QPushButton.leaveEvent(self.config_button, event)
        
        self.config_button.enterEvent = on_config_button_enter
        self.config_button.leaveEvent = on_config_button_leave
        
        enabled_config_layout.addWidget(self.config_button)
        
        # 将enabled和配置按钮的布局添加到主布局
        top_layout.addLayout(enabled_config_layout)
        
        main_layout.addLayout(top_layout)
        
        # 现在所有控件都创建完成，可以安全地更新状态
        self._update_available_display()
        
        # 描述文本
        description = self.plugin_data.get('description', tr("plugin_manager.no_description"))
        self.description_label = QLabel(description)
        self.description_label.setWordWrap(True)
        self.description_label.setObjectName("plugin-description-label")
        self.description_label.setMaximumHeight(40)
        main_layout.addWidget(self.description_label)
        
        # 如果有错误信息，显示错误详情
        if self.plugin_data.get('error_info'):
            self.error_label = QLabel(f"❌ {self.plugin_data['error_info']}")
            self.error_label.setWordWrap(True)
            self.error_label.setObjectName("plugin-error-label")
            main_layout.addWidget(self.error_label)
    

    
    def _update_available_display(self):
        """更新可用状态显示"""
        if self.plugin_data.get('is_available', True):
            self.available_label.setText("✅ Available")
            self.available_label.setObjectName("plugin-available-label-available")
            self.config_button.setEnabled(True)
        else:
            self.available_label.setText("❌ Unavailable")
            self.available_label.setToolTip(self.plugin_data.get('error_info', ''))
            self.available_label.setObjectName("plugin-available-label-unavailable")
            self.config_button.setEnabled(False)
    
    def _update_enabled_switch(self):
        """更新启用开关"""
        # 启用开关现在控制插件的加载/卸载
        is_loaded = self.plugin_data.get('loaded', False)
        is_available = self.plugin_data.get('is_available', True)
        
        self.enabled_checkbox.setChecked(is_loaded)
        self.enabled_checkbox.setEnabled(is_available)  # 只有可用的插件才能操作
    
    def _on_enabled_changed(self, enabled):
        """启用状态变化处理（直接触发启用状态变化信号）"""
        self.plugin_enabled_changed.emit(self.plugin_name, enabled)
    
    def _on_config_clicked(self):
        """配置按钮点击处理"""
        self.plugin_config_requested.emit(self.plugin_name)
        logger.info(f"[PLUGIN] ⚙️ Config requested for plugin: {self.plugin_name}")
    
    def _apply_styles(self):
        """应用样式"""
        self.setObjectName("plugin-item-widget")
    
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
        
        # 更新错误信息
        if hasattr(self, 'error_label'):
            self.error_label.setParent(None)
            delattr(self, 'error_label')
        
        if plugin_data.get('error_info'):
            self.error_label = QLabel(f"❌ {plugin_data['error_info']}")
            self.error_label.setWordWrap(True)
            self.error_label.setObjectName("plugin-error-label")
            self.layout().addWidget(self.error_label)


class PluginConfigDialog(QDialog):
    """插件配置对话框"""
    
    def __init__(self, plugin_name, config_data, available_config, parent=None):
        super().__init__(parent)
        
        self.plugin_name = plugin_name
        self.config_data = config_data.copy() if config_data else {}
        self.available_config = available_config or {}
        self.config_widgets = {}  # 存储配置控件
        
        # 初始化UI
        self._init_ui()
        
        # 加载配置值
        self._load_config_values()
        
        logger.info(f"[PLUGIN_CONFIG] 🔧 Config dialog opened for plugin: {plugin_name}")
    
    def _init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle(f"{tr('plugin_manager.config_title')} - {self.plugin_name}")
        self.setMinimumSize(400, 300)
        self.resize(500, 400)
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icon.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 创建标题
        title_label = QLabel(f"{tr('plugin_manager.config_title')} - {self.plugin_name}")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 创建配置表单
        config_widget = QWidget()
        self.config_layout = QFormLayout(config_widget)
        self.config_layout.setContentsMargins(10, 10, 10, 10)
        self.config_layout.setSpacing(10)
        
        # 根据available_config动态创建控件
        self._create_config_widgets()
        
        scroll_area.setWidget(config_widget)
        main_layout.addWidget(scroll_area, 1)
        
        # 创建按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 取消按钮
        cancel_button = QPushButton(tr("plugin_manager.config_cancel"))
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        # 保存按钮
        save_button = QPushButton(tr("plugin_manager.config_save"))
        save_button.clicked.connect(self._save_config)
        save_button.setDefault(True)
        button_layout.addWidget(save_button)
        
        main_layout.addLayout(button_layout)
        
        # 应用样式
        self._apply_styles()
    
    def _create_config_widgets(self):
        """根据available_config动态创建配置控件"""
        if not self.available_config:
            # 如果没有配置项，显示提示
            no_config_label = QLabel(tr("plugin_manager.no_config_available"))
            no_config_label.setAlignment(Qt.AlignCenter)
            no_config_label.setObjectName("plugin-no-config-label")
            self.config_layout.addRow(no_config_label)
            return
        
        for key, config_info in self.available_config.items():
             widget = self._create_widget_for_config(key, config_info)
             if widget:
                 # 处理标签文本
                 if isinstance(config_info, dict):
                     label_text = config_info.get('label', key)
                     description = config_info.get('description', '')
                     if description:
                         label_text += f" ({description})"
                 else:
                     label_text = key
                 
                 label = QLabel(label_text)
                 self.config_layout.addRow(label, widget)
                 self.config_widgets[key] = widget
    
    def _create_widget_for_config(self, key, config_info):
        """为单个配置项创建控件"""
        default_value = config_info
        config_type = self._infer_config_type(key, default_value)
        
        try:
            if config_type == 'bool':
                if key == 'enabled':  # 特殊处理enabled配置项
                    return
                widget = QCheckBox()
                if default_value is not None:
                        widget.setChecked(bool(default_value))
                return widget
            
            elif config_type == 'int':
                widget = QSpinBox()
                widget.setRange(-999999, 999999)
                if isinstance(config_info, dict):
                    widget.setRange(config_info.get('min', -999999), config_info.get('max', 999999))
                if default_value is not None:
                    widget.setValue(int(default_value))
                return widget
            
            elif config_type == 'list' and len(default_value) > 0:
                widget = QComboBox()
                widget.setEditable(False)  # 禁止编辑，只能从列表中选择
                
                # 存储完整的选项列表（包括最后一个用于存储用户配置的选项）
                full_options = []
                if isinstance(config_info, dict) and 'options' in config_info:
                    # 如果配置中定义了选项，使用这些选项
                    full_options = config_info['options']
                elif config_type == 'list' and isinstance(default_value, list):
                    # 如果没有预定义选项，使用默认值作为选项
                    full_options = default_value.copy()
                
                # 将完整选项列表存储在widget的属性中，用于后续保存
                widget.setProperty('full_options', full_options)
                
                # 只显示除最后一个选项外的所有选项（最后一个选项用于存储用户配置，不显示）
                display_options = full_options[:-1] if len(full_options) > 1 else full_options
                widget.addItems([str(item) for item in display_options])
                
                if default_value is not None:
                    if config_type == 'list' and isinstance(default_value, list) and default_value:
                        # 查找当前选中值（最后一个元素是用户配置）
                        current_value = str(default_value[-1]) if default_value else ''
                        # 在显示的选项中查找
                        index = widget.findText(current_value)
                        if index >= 0:
                            widget.setCurrentIndex(index)
                        else:
                            # 如果在显示选项中找不到，说明是用户自定义的值，选择第一个选项
                            if widget.count() > 0:
                                widget.setCurrentIndex(0)
                    else:
                        # 查找默认值在选项中的索引
                        index = widget.findText(str(default_value))
                        if index >= 0:
                            widget.setCurrentIndex(index)
                        
                return widget
            elif config_type == 'string':
                widget = QLineEdit()
                widget.setMaxLength(100)  # 最大长度为100
                if default_value is not None:
                    widget.setText(str(default_value))
                return widget
            
            elif config_type == 'password':
                widget = QLineEdit()
                widget.setMaxLength(100)  # 最大长度为100
                widget.setEchoMode(QLineEdit.Password)  # 设置为密码输入模式
                widget.setPlaceholderText("请输入密码")
                if default_value is not None:
                    # 解密密码用于显示
                    decrypted_value = decrypt_password(str(default_value))
                    widget.setText(decrypted_value)
                return widget

            elif config_type == 'keyboard':
                widget = KeyboardShortcutWidget(default_value)
                widget.setMaximumWidth(300)
                return widget
                
        except Exception as e:
            logger.error(f"[PLUGIN_CONFIG] ❌ Error creating widget for {key}: {e}")
            # 出错时返回简单的文本框
            widget = QLineEdit()
            if default_value is not None:
                widget.setText(str(default_value))
            return widget
     
    def _infer_config_type(self, key, value):
        """根据键名和值推断配置类型"""
        if isinstance(value, bool):
            return 'bool'
        elif isinstance(value, int):
            return 'int'
        elif isinstance(value, list):
            return 'list'
        elif isinstance(value, str):
            if key.lower().startswith('keyboard'):
                return 'keyboard'
            elif is_password_field(key):
                return 'password'
            return 'string'
        else:
            return 'not support type'
     
    def _load_config_values(self):
        """加载配置值到控件"""
        for key, widget in self.config_widgets.items():
            if key in self.config_data:
                value = self.config_data[key]
                self._set_widget_value(widget, value)
     
    def _set_widget_value(self, widget, value):
        """设置控件值"""
        try:
            if isinstance(widget, KeyboardShortcutWidget):
                widget.set_shortcut(value)
            elif isinstance(widget, QLineEdit):
                if widget.echoMode() == QLineEdit.Password:
                    # 密码字段需要解密后显示
                    decrypted_value = decrypt_password(str(value)) if value is not None else ''
                    widget.setText(decrypted_value)
                else:
                    widget.setText(str(value) if value is not None else '')
            elif isinstance(widget, QSpinBox):
                widget.setValue(int(value) if value is not None else 0)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(bool(value) if value is not None else False)
            elif isinstance(widget, QComboBox):
                if widget.isEditable():
                    # 对于可编辑的下拉菜单，直接设置文本
                    widget.setCurrentText(str(value) if value is not None else '')
                else:
                    # 对于不可编辑的下拉菜单，查找对应的索引
                    index = widget.findData(value)
                    if index >= 0:
                        widget.setCurrentIndex(index)
                    else:
                        # 如果找不到数据，尝试按文本查找
                        index = widget.findText(str(value))
                        if index >= 0:
                            widget.setCurrentIndex(index)
        except Exception as e:
            logger.error(f"[PLUGIN_CONFIG] ❌ Error setting widget value: {e}")
    
    def _get_widget_value(self, widget):
        """获取控件值"""
        try:
            if isinstance(widget, KeyboardShortcutWidget):
                return widget.get_shortcut()
            elif isinstance(widget, QLineEdit):
                text = widget.text().strip()
                
                # 检查是否是密码字段
                if widget.echoMode() == QLineEdit.Password:
                    # 密码字段需要加密后保存
                    return encrypt_password(text) if text else ""
                
                # 检查是否是列表类型（通过占位符文本判断）
                if widget.placeholderText() == "使用逗号分隔多个值":
                    if not text:
                        return []
                    # 将逗号分隔的字符串转换为列表
                    items = [item.strip() for item in text.split(',') if item.strip()]
                    # 尝试转换为数字类型
                    converted_items = []
                    for item in items:
                        try:
                            # 尝试转换为整数
                            if '.' not in item:
                                converted_items.append(int(item))
                            else:
                                # 尝试转换为浮点数
                                converted_items.append(float(item))
                        except ValueError:
                            # 保持为字符串
                            converted_items.append(item)
                    return converted_items
                
                return text if text else None
            elif isinstance(widget, QSpinBox):
                return widget.value()
            elif isinstance(widget, QCheckBox):
                return widget.isChecked()
            elif isinstance(widget, QComboBox):
                # 对于可编辑的下拉菜单，获取当前文本
                if widget.isEditable():
                    return widget.currentText()
                else:
                    # 检查是否是list类型的ComboBox（有full_options属性）
                    full_options = widget.property('full_options')
                    if full_options is not None:
                        # 获取用户当前选择的值
                        current_text = widget.currentText()
                        # 重新构建列表，将用户选择的值放到最后
                        new_list = full_options[:-1].copy()  # 复制除最后一个元素外的所有元素
                        new_list.append(current_text)  # 将用户选择的值添加到最后
                        return new_list
                    else:
                        # 对于普通的不可编辑下拉菜单，获取当前数据
                        return widget.currentData() if widget.currentData() is not None else widget.currentText()
            else:
                return None
        except Exception as e:
            logger.error(f"[PLUGIN_CONFIG] ❌ Error getting widget value: {e}")
            return None
    
    def _save_config(self):
        """保存配置"""
        try:
            # 收集所有配置值
            new_config = {}
            for key, widget in self.config_widgets.items():
                value = self._get_widget_value(widget)
                if value is not None:
                    new_config[key] = value
            
            # 验证配置值
            if self._validate_config(new_config):
                self.config_data = new_config
                self.accept()
                logger.info(f"[PLUGIN_CONFIG] 💾 Config saved for plugin: {self.plugin_name}")
                logger.info(f"[PLUGIN_CONFIG] 🔄 Config saved: {new_config}")
            
        except Exception as e:
            logger.error(f"[PLUGIN_CONFIG] ❌ Error saving config: {e}")
            QMessageBox.warning(self, tr("plugin_manager.error"), str(e))
     
    def _validate_config(self, config):
        """验证配置值"""
        try:
            for key, value in config.items():
                if key in self.available_config:
                    config_info = self.available_config[key]
                    if isinstance(config_info, dict):
                        config_type = config_info.get('type', 'string')
                    else:
                        config_type = self._infer_config_type(key, config_info)
                    
                    # 类型验证
                    if config_type == 'int':
                        try:
                            int_value = int(value)
                            min_val = config_info.get('min') if isinstance(config_info, dict) else None
                            max_val = config_info.get('max') if isinstance(config_info, dict) else None
                            if min_val is not None and int_value < min_val:
                                raise ValueError(f"{key} config value must be greater than or equal to {min_val}")
                            if max_val is not None and int_value > max_val:
                                raise ValueError(f"{key} config value must be less than or equal to {max_val}")
                        except ValueError as e:
                            QMessageBox.warning(self, tr("plugin_manager.validation_error"), str(e))
                            return False
            
            return True
            
        except Exception as e:
            logger.error(f"[PLUGIN_CONFIG] ❌ Error validating config: {e}")
            QMessageBox.warning(self, tr("plugin_manager.error"), str(e))
            return False
    
    def _apply_styles(self):
        """应用样式"""
        self.setObjectName("plugin-config-dialog")
    
    def get_config_data(self):
        """获取配置数据"""
        return self.config_data.copy()


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
        
        logger.debug("[PLUGIN_MANAGER] 🔧 Plugin manager dialog initialized")
    
    def _init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle(tr("plugin_manager.title"))
        self.setMinimumSize(500, 400)
        self.resize(500, 500)
        
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
        self.setObjectName("plugin-manager-dialog")
    
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
                
                # 设置加载状态（用于UI控制）
                plugin_data['loaded'] = plugin_name in loaded_plugins
                
                # 设置状态显示（只基于可用性）
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
            
            try:
                # 创建插件项widget
                plugin_widget = PluginItemWidget(plugin_data)
                
                # 连接信号（检查信号是否存在）
                if hasattr(plugin_widget, 'plugin_enabled_changed'):
                    plugin_widget.plugin_enabled_changed.connect(self._on_plugin_enabled_changed)
                if hasattr(plugin_widget, 'plugin_config_requested'):
                    plugin_widget.plugin_config_requested.connect(self._on_plugin_config_requested)
                
                # 添加到布局中（在弹性空间之前）
                self.plugin_list_layout.insertWidget(self.plugin_list_layout.count() - 1, plugin_widget)
                
                # 存储widget引用
                self.plugin_widgets[plugin_name] = plugin_widget
                
            except Exception as e:
                logger.error(f"[PLUGIN_MANAGER] ❌ Failed to create widget for plugin {plugin_name}: {e} - {traceback.format_exc()}")
                # 创建一个简单的错误显示widget
                error_widget = QLabel(f"❌ 插件 '{plugin_name}' 显示错误: {str(e)}")
                error_widget.setObjectName("plugin-error-widget")
                self.plugin_list_layout.insertWidget(self.plugin_list_layout.count() - 1, error_widget)
                continue
    
    def _connect_signals(self):
        """连接信号"""
        # 连接插件管理器的信号
        if self.plugin_manager:
            self.plugin_manager.plugin_loaded.connect(self._on_plugin_loaded)
            self.plugin_manager.plugin_unloaded.connect(self._on_plugin_unloaded)
            self.plugin_manager.plugin_error.connect(self._on_plugin_error)
        
        # 连接对话框信号到插件管理器
        self.plugin_enabled.connect(self.plugin_manager.enable_plugin)
        self.plugin_disabled.connect(self.plugin_manager.disable_plugin)
        
        # 连接插件加载/卸载信号到主窗口按钮状态更新
        if self.parent() and hasattr(self.parent(), 'main_window'):
            main_window = self.parent().main_window
            if main_window:
                self.plugin_loaded.connect(main_window.enable_plugin_button)
                self.plugin_unloaded.connect(main_window.disable_plugin_button)
    
    def _on_plugin_enabled_changed(self, plugin_name, enabled):
        """插件启用状态变化处理"""
        try:
            if enabled:
                # 启用并加载插件
                self._load_plugin(plugin_name)
            else:
                # 卸载并禁用插件
                self._unload_plugin(plugin_name)
            # 刷新插件列表以更新UI状态
            self._refresh_plugins()
        except Exception as e:
            logger.error(f"[PLUGIN_MANAGER] ❌ Error changing plugin state: {e}")
            self._refresh_plugins()
    
    def _load_plugin(self, plugin_name):
        """加载插件"""
        try:
            # 先启用插件（更新config.json中的enabled状态）
            if self.plugin_manager.enable_plugin(plugin_name):
                # 然后加载插件
                if self.plugin_manager.load_plugin(plugin_name):
                    logger.info(f"[PLUGIN_MANAGER] 🔌 Plugin loaded: {plugin_name}")
                    self.plugin_loaded.emit(plugin_name)  # 发出插件加载信号
                    # 不需要刷新整个插件列表，只更新对应插件项的状态
                else:
                    # 加载失败，回滚启用状态
                    self.plugin_manager.disable_plugin(plugin_name)
                    QMessageBox.warning(self, tr("plugin_manager.error"),
                                      tr("plugin_manager.load_error_msg").format(name=plugin_name))
            else:
                QMessageBox.warning(self, tr("plugin_manager.error"),
                                  tr("plugin_manager.enable_error").format(name=plugin_name))
        except Exception as e:
            logger.error(f"[PLUGIN_MANAGER] ❌ Error loading plugin: {e}")
            QMessageBox.warning(self, tr("plugin_manager.error"), str(e))
    
    def _unload_plugin(self, plugin_name):
        """卸载插件"""
        try:
            # 先卸载插件
            if self.plugin_manager.unload_plugin(plugin_name):
                # 然后禁用插件（更新config.json中的enabled状态）
                if self.plugin_manager.disable_plugin(plugin_name):
                    logger.info(f"[PLUGIN_MANAGER] 🗑️ Plugin unloaded and disabled: {plugin_name}")
                    self.plugin_unloaded.emit(plugin_name)  # 发出插件卸载信号
                    # 不需要刷新整个插件列表，只更新对应插件项的状态
                else:
                    logger.warning(f"[PLUGIN_MANAGER] ⚠️ Plugin unloaded but failed to disable: {plugin_name}")
                    self.plugin_unloaded.emit(plugin_name)  # 仍然发出卸载信号
            else:
                QMessageBox.warning(self, tr("plugin_manager.error"),
                                  tr("plugin_manager.unload_error").format(name=plugin_name))
        except Exception as e:
            logger.error(f"[PLUGIN_MANAGER] ❌ Error unloading plugin: {e}")
            QMessageBox.warning(self, tr("plugin_manager.error"), str(e))
    
    def _on_plugin_config_requested(self, plugin_name):
        """处理插件配置请求"""
        try:
            # 查找插件数据
            plugin_data = None
            for plugin in self.plugins_data:
                if plugin.get('name') == plugin_name:
                    plugin_data = plugin
                    break
            
            if not plugin_data:
                QMessageBox.warning(
                    self,
                    tr("plugin_manager.error"),
                    f"未找到插件 {plugin_name}"
                )
                return
            
            # 获取available_config
            available_config = plugin_data.get('available_config', {})
            current_config = plugin_data.get('config', {})
            
            # 创建配置对话框
            config_dialog = PluginConfigDialog(
                plugin_name=plugin_name,
                config_data=current_config,
                available_config=available_config,
                parent=self
            )
            
            # 显示对话框并处理结果
            if config_dialog.exec() == QDialog.DialogCode.Accepted:
                # 获取新的配置数据
                new_config = config_dialog.get_config_data()
                
                # 更新插件配置
                self._update_plugin_config(plugin_name, new_config)
                
                logger.info(f"[PLUGIN_MANAGER] 💾 Plugin {plugin_name} config updated")
                
                # 刷新插件列表显示
                self._refresh_plugins()
            
        except Exception as e:
            logger.error(f"[PLUGIN_MANAGER] ❌ Error opening config for {plugin_name}: {e} - {traceback.format_exc()}")
            QMessageBox.warning(self, tr("plugin_manager.error"), str(e))
    
    def _refresh_plugins(self):
        """刷新插件列表"""
        try:
            self._load_plugins_data()
            logger.info("[PLUGIN_MANAGER] 🔄 Plugin list refreshed")
        except Exception as e:
            logger.error(f"[PLUGIN_MANAGER] ❌ Error refreshing plugins: {e}")
    
    def _update_single_plugin_status(self, plugin_name):
        """更新单个插件的状态"""
        try:
            # 获取插件的最新状态
            loaded_plugins = self.plugin_manager.get_loaded_plugins()
            
            # 查找对应的插件widget
            if plugin_name in self.plugin_widgets:
                plugin_widget = self.plugin_widgets[plugin_name]
                
                # 更新插件数据中的加载状态
                for plugin_data in self.plugins_data:
                    if plugin_data['name'] == plugin_name:
                        # 更新加载状态（用于UI控制）
                        plugin_data['loaded'] = plugin_name in loaded_plugins
                        
                        # 状态显示只基于可用性，不再区分loaded/unloaded
                        if plugin_data.get('is_available', True):
                            plugin_data['status'] = tr("plugin_manager.status.available")
                        else:
                            plugin_data['status'] = tr("plugin_manager.status.error")
                        
                        # 更新widget显示
                        plugin_widget.update_plugin_data(plugin_data)
                        break
                        
            logger.debug(f"[PLUGIN_MANAGER] 🔄 Updated status for plugin: {plugin_name}")
            
        except Exception as e:
            logger.error(f"[PLUGIN_MANAGER] ❌ Error updating plugin status: {e}")
    
    def _on_plugin_loaded(self, plugin_name):
        """插件加载完成回调"""
        # 插件加载完成后，更新对应插件项的状态
        self._update_single_plugin_status(plugin_name)
    
    def _on_plugin_unloaded(self, plugin_name):
        """插件卸载完成回调"""
        # 插件卸载完成后，更新对应插件项的状态
        self._update_single_plugin_status(plugin_name)
    
    def _on_plugin_error(self, plugin_name, error_message):
        """插件错误回调"""
        QMessageBox.critical(self, tr("plugin_manager.error"),
                           tr("plugin_manager.plugin_error").format(name=plugin_name, error=error_message))
        self._refresh_plugins()
    
    def _update_plugin_config(self, plugin_name, new_config):
        """更新插件配置"""
        try:
            # 通过插件管理器更新配置到文件
            if hasattr(self.plugin_manager, 'update_plugin_config'):
                success = self.plugin_manager.update_plugin_config(plugin_name, new_config)
                if not success:
                    raise Exception(f"Failed to save config to {plugin_name}/config.json")
            else:
                # 如果插件管理器没有此方法，直接更新本地数据（但这不会持久化）
                logger.warning(f"[PLUGIN_MANAGER] ⚠️ Plugin manager missing update_plugin_config method, config may not persist")
                for plugin in self.plugins_data:
                    if plugin.get('name') == plugin_name:
                        plugin['config'] = new_config
                        break
            
            # 同时更新本地数据以保持一致性
            for plugin in self.plugins_data:
                if plugin.get('name') == plugin_name:
                    plugin['config'] = new_config
                    break
            
            logger.info(f"[PLUGIN_MANAGER] 💾 Config updated for plugin: {plugin_name}")
            
        except Exception as e:
            logger.error(f"[PLUGIN_MANAGER] ❌ Error updating plugin config: {e} - {traceback.format_exc()}")
            raise
    
    def refresh_plugin_list(self):
        """刷新插件列表"""
        try:
            # 重新加载插件数据
            self._load_plugins_data()
            
            logger.info("[PLUGIN_MANAGER] 🔄 Plugin list refreshed")
            
        except Exception as e:
            logger.error(f"[PLUGIN_MANAGER] ❌ Error refreshing plugin list: {e}")
            QMessageBox.warning(self, tr("plugin_manager.error"),
                              tr("plugin_manager.refresh_error").format(error=str(e)))
