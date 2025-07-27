"""
HSBC Little Worker - LittleCapturer Plugin
专业的截图工具插件
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, 
    QHBoxLayout, QLineEdit, QCheckBox,
    QTextEdit, QFrame, QSpacerItem, QSizePolicy, QScrollArea
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QKeySequence, QPixmap, QIcon

from core.plugin_base import PluginBase
from core.i18n import get_i18n_manager
# from .utils.hotkey_manager import GlobalHotkeyManager
# from .capture_window import CaptureWindow


class Plugin(PluginBase):
    """LittleCapturer Plugin class"""
    
    # 插件元信息
    NAME = "little_capturer"
    DISPLAY_NAME = "LittleCapturer"
    DESCRIPTION = "专业的截图工具插件，超越Windows系统自带截图功能"
    VERSION = "1.0.0"
    AUTHOR = "HSBC IT Support"
    
    def __init__(self, app=None):
        super().__init__(app)
        self.hotkey_manager = None
        self.capture_window = None
        self.i18n_manager = get_i18n_manager()
        
        # 连接语言变更信号
        self.i18n_manager.language_changed.connect(self.on_language_changed)
        self.i18n_manager.language_changed.connect(lambda lang: self.set_language(lang))
        
        # 连接插件管理器的配置变更信号
        if self.app and hasattr(self.app, 'plugin_manager'):
            self.app.plugin_manager.plugin_config_changed.connect(self._on_plugin_config_changed)
        
        # 存储UI组件引用，用于语言切换时更新
        self.title_label = None
        self.desc_label = None
        self.features_label = None
        self.capture_button = None
        
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            self.log_info("[INIT] 🚀 Initialize LittleCapturer Plugin")
            
            # 初始化全局热键管理器
            from .utils.hotkey_manager import GlobalHotkeyManager
            self.hotkey_manager = GlobalHotkeyManager()
            
            # 初始化截图窗口
            from .utils.screenshot import CaptureWindow
            self.capture_window = CaptureWindow()
            self.capture_window.area_selected.connect(self._on_area_selected)
            self.capture_window.capture_cancelled.connect(self._on_capture_cancelled)
            
            # 启动热键管理器
            self.hotkey_manager.start()
            
            # 注册热键
            hotkey = self.get_setting('keyboard_shortcut', 'Alt+Shift+Z')
            self._register_hotkey(hotkey)
            
            self.log_info(f"[INIT] ✅ Initialize LittleCapturer Plugin Success")
            return True
            
        except Exception as e:
            import traceback
            self.log_error(f"[INIT] ❌ Initialize LittleCapturer Plugin Failed: {e} - {traceback.format_exc()}")
            return False
    
    def _register_hotkey(self, hotkey):
        """注册全局热键"""
        try:
            if self.hotkey_manager:
                success = self.hotkey_manager.register_hotkey(hotkey, self._on_hotkey_triggered)
                if success:
                    self.log_info(f"[HOTKEY] ✅ Registered hotkey: {hotkey}")
                else:
                    self.log_error(f"[HOTKEY] ❌ Failed to register hotkey: {hotkey}")
        except Exception as e:
            import traceback
            self.log_error(f"[HOTKEY] ❌ Failed to register hotkey {hotkey}: {e} - {traceback.format_exc()}")
    
    def _on_hotkey_triggered(self):
        """热键触发回调"""
        self._start_capture()
    
    def _on_area_selected(self, rect):
        """区域选择完成回调"""
        try:
            self.log_info(f"[CAPTURE] 📐 Area selected: {rect}")
            
            # 执行区域截图
            from .utils.screenshot import ScreenCapture
            screen_capture = ScreenCapture()
            pixmap = screen_capture.capture_area(rect)
            
            if pixmap and not pixmap.isNull():
                self.log_info(f"[CAPTURE] ✅ Screenshot captured successfully, size: {pixmap.size()}")
                # TODO: 这里可以添加保存、编辑等功能
                # 目前只是演示截图功能已经工作
            else:
                self.log_error("[CAPTURE] ❌ Failed to capture screenshot")
                
        except Exception as e:
            import traceback
            self.log_error(f"[CAPTURE] ❌ Failed to handle area selection: {e} - {traceback.format_exc()}")
    
    def _on_capture_cancelled(self):
        """截图取消回调"""
        try:
            self.log_info("[CAPTURE] ❌ Capture cancelled")
        except Exception as e:
            self.log_error(f"[CAPTURE] ❌ Failed to handle capture cancellation: {e}")
    
    def create_widget(self) -> QWidget:
        """创建插件界面组件"""
        try:
            # 创建主容器
            main_widget = QWidget()
            main_widget.setObjectName("LittleCapturerMainWidget")
            
            # 创建主布局
            main_layout = QVBoxLayout(main_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # 创建滚动区域
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setFrameShape(QFrame.NoFrame)
            
            # 创建内容容器
            content_widget = QWidget()
            content_widget.setObjectName("LittleCapturerWidget")
            
            # 创建内容布局
            content_layout = QVBoxLayout(content_widget)
            content_layout.setContentsMargins(20, 20, 20, 20)
            content_layout.setSpacing(15)
            
            # 标题
            self.title_label = QLabel(self.tr("plugin.capturer.name"))
            title_font = QFont()
            title_font.setPointSize(16)
            title_font.setBold(True)
            self.title_label.setFont(title_font)
            self.title_label.setAlignment(Qt.AlignCenter)
            content_layout.addWidget(self.title_label)
            
            # 描述
            self.desc_label = QLabel(self.tr("plugin.capturer.description_detail"))
            self.desc_label.setWordWrap(True)
            self.desc_label.setAlignment(Qt.AlignCenter)
            self.desc_label.setStyleSheet(
                "QLabel {"
                "    background-color: #f8f9fa;"
                "    border: none;"
                "    border-radius: 6px;"
                "    padding: 15px;"
                "    color: #7f8c8d;"
                "    margin-bottom: 15px;"
                "}"
            )
            content_layout.addWidget(self.desc_label)

            # 截图按钮
            self.capture_button = QPushButton(self._get_capture_button_text())
            self.capture_button.setMinimumHeight(40)
            self.capture_button.setStyleSheet(
                "QPushButton {"
                "    background-color: #3498db;"
                "    color: white;"
                "    border: none;"
                "    border-radius: 8px;"
                "    font-size: 14px;"
                "    font-weight: bold;"
                "    padding: 10px 20px;"
                "}"
                "QPushButton:hover {"
                "    background-color: #2980b9;"
                "}"
                "QPushButton:pressed {"
                "    background-color: #21618c;"
                "}"
            )
            self.capture_button.clicked.connect(self._start_capture)
            content_layout.addWidget(self.capture_button)

            # 功能说明区域 - 使用HTML
            self.features_label = QLabel()
            self.features_label.setText(self.tr("plugin.capturer.features_html"))
            self.features_label.setWordWrap(True)
            self.features_label.setTextFormat(Qt.RichText)
            content_layout.addWidget(self.features_label)
            
            # 添加弹性空间
            content_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
            
            # 将内容容器添加到滚动区域
            scroll_area.setWidget(content_widget)
            
            # 将滚动区域添加到主布局
            main_layout.addWidget(scroll_area)
            
            self.log_info("[UI] ✅ LittleCapturer widget created successfully")
            return main_widget
            
        except Exception as e:
            import traceback
            self.log_error(f"[UI] ❌ Failed to create widget: {e} - {traceback.format_exc()}")
            return None
    
    def _get_capture_button_text(self):
        """获取带有快捷键提示的按钮文本"""
        try:
            # 获取基础按钮文本
            base_text = self.tr("plugin.capturer.capture_button_base")
            
            # 获取当前配置的快捷键
            hotkey = self.get_setting('keyboard_shortcut', 'Alt+Shift+W')
            self.log_info(f"[CONFIG] 📋 Current hotkey from config: {hotkey}")
            
            # 组合文本
            button_text = f"{base_text} ({hotkey})"
            self.log_info(f"[UI] 🔄 Generated button text: {button_text}")
            return button_text
        except Exception as e:
            import traceback
            self.log_error(f"[UI] ❌ Failed to get capture button text: {e} - {traceback.format_exc()}")
            return "🎯 开始截图"
    
    def on_language_changed(self):
        """语言变更时更新界面文本"""
        try:
            if hasattr(self, 'title_label') and self.title_label is not None:
                self.title_label.setText(self.tr("plugin.capturer.name"))
            
            if hasattr(self, 'desc_label') and self.desc_label is not None:
                self.desc_label.setText(self.tr("plugin.capturer.description_detail"))
            
            if hasattr(self, 'features_label') and self.features_label is not None:
                self.features_label.setText(self.tr("plugin.capturer.features_html"))
            
            if hasattr(self, 'capture_button') and self.capture_button is not None:
                self.capture_button.setText(self._get_capture_button_text())
            
            self.log_info("[UI] 🌐 Language changed, UI text updated")
        except Exception as e:
            import traceback
            self.log_error(f"[UI] ❌ Failed to update language: {e} - {traceback.format_exc()}")
    
    def _on_plugin_config_changed(self, plugin_name: str, new_config: dict):
        """插件管理器配置变更信号处理"""
        try:
            # 只处理当前插件的配置变更
            if plugin_name == self.get_name():
                self.log_info(f"[CONFIG] 📡 Received config change signal: {new_config}")
                self.on_config_changed()
        except Exception as e:
            import traceback
            self.log_error(f"[CONFIG] ❌ Failed to handle config change signal: {e} - {traceback.format_exc()}")
    
    def on_config_changed(self):
        """配置变更时更新界面"""
        try:
            # 更新按钮文本以反映新的hotkey
            if hasattr(self, 'capture_button') and self.capture_button is not None:
                self.capture_button.setText(self._get_capture_button_text())
            
            self.log_info("[CONFIG] ⚙️ Config changed, UI updated")
        except Exception as e:
            import traceback
            self.log_error(f"[CONFIG] ❌ Failed to update config: {e} - {traceback.format_exc()}")
    
    def _start_capture(self):
        """开始截图（热键回调）"""
        try:
            self.log_info("[CAPTURE] 🎯 Starting screenshot capture")
            if hasattr(self, 'capture_window') and self.capture_window:
                self.capture_window.show_capture_window()
            else:
                self.log_error("[CAPTURE] ❌ Capture window not initialized")
        except Exception as e:
            import traceback
            self.log_error(f"[CAPTURE] ❌ Failed to start capture: {e} - {traceback.format_exc()}")
    
    def cleanup(self):
        """清理插件资源"""
        try:
            self.log_info("[CLEANUP] 🧹 Cleaning up LittleCapturer plugin")
            
            # 清理热键管理器
            if hasattr(self, 'hotkey_manager') and self.hotkey_manager:
                self.hotkey_manager.cleanup()
                self.hotkey_manager = None
                self.log_info("[CLEANUP] ✅ Hotkey manager cleaned up")
            
            # 清理截图窗口
            if hasattr(self, 'capture_window') and self.capture_window:
                self.capture_window.hide()
                self.capture_window = None
                self.log_info("[CLEANUP] ✅ Capture window cleaned up")
            
            self.log_info("[CLEANUP] ✅ LittleCapturer plugin cleanup completed")
            
        except Exception as e:
            import traceback
            self.log_error(f"[CLEANUP] ❌ Failed to cleanup plugin: {e} - {traceback.format_exc()}")