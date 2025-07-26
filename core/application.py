# -*- coding: utf-8 -*-
"""
HSBC Little Worker - 主应用程序类
"""

import os
import json
from warnings import deprecated
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QToolBar, QStatusBar, QMenuBar, QMenu,
    QSystemTrayIcon, QMessageBox, QSplitter
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QIcon, QPixmap, QAction

from .plugin_manager import PluginManager
from config.settings import APP_NAME
from .main_window import MainWindow
from .i18n import get_i18n_manager, tr
from utils.logger import logger


class LittleWorkerApp(QMainWindow):
    """主应用程序类"""
    
    # 信号定义
    plugin_loaded = Signal(str)  # 插件加载信号
    plugin_unloaded = Signal(str)  # 插件卸载信号
    
    def __init__(self):
        super().__init__()
        
        # 初始化国际化管理器
        self.i18n_manager = get_i18n_manager()
        
        # 加载语言设置
        self.load_language_settings()
        
        # 初始化组件
        self.plugin_manager = None
        self.main_window = None
        self.system_tray = None
        
        # 初始化UI
        self._init_ui()
        
        # 初始化插件管理器
        self._init_plugin_manager()
        
        # 初始化系统托盘
        self._init_system_tray()
        
        logger.info("🚀 Application initialized successfully")
    
    def load_language_settings(self):
        """加载语言设置"""
        try:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                "config", 
                "plugin_config.json"
            )
            
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    language = config.get("ui_settings", {}).get("language", "en_US")
                    self.i18n_manager.set_language(language)
                    logger.info(f"🌐 Language loaded: {language}")
            else:
                logger.warning("⚠️ Config file not found, using default language")
                
        except Exception as e:
            logger.error(f"❌ Failed to load language settings: {e}")
    
    def _load_ui_settings(self):
        """加载并应用UI设置"""
        try:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                "config", 
                "plugin_config.json"
            )
            
            if not os.path.exists(config_path):
                logger.warning("⚠️ Config file not found, using default UI settings")
                return
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                ui_settings = config.get("ui_settings", {})
                
                # 应用窗口透明度设置
                opacity = ui_settings.get("window_opacity", 1.0)
                self.setWindowOpacity(opacity)
                logger.info(f"🔍 Window opacity applied: {int(opacity * 100)}%")
                
                # 应用字体大小设置
                font_size = ui_settings.get("font_size", 11)
                from PySide6.QtGui import QFont
                from PySide6.QtWidgets import QApplication
                font = QApplication.font()
                font.setPointSize(font_size)
                QApplication.setFont(font)
                logger.info(f"🔤 Font size applied: {font_size}")
                
                logger.info("✅ UI settings loaded and applied")
                
        except Exception as e:
            logger.error(f"❌ Failed to load UI settings: {e}")
    
    def _init_ui(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(500, 400)
        self.resize(1000, 700)
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icon.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 加载并应用UI设置
        self._load_ui_settings()
        
        # 创建主窗口组件
        self.main_window = MainWindow(self)
        self.setCentralWidget(self.main_window)
        
        # 创建菜单栏
        self._create_menu_bar()
        
        # # 创建工具栏
        # self._create_tool_bar()
        
        # 创建状态栏
        self._create_status_bar()
        
        logger.info("✅ Main window initialized")
    
    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu(tr("menu.file"))
        
        # 设置按钮
        settings_action = QAction(tr("menu.settings"), self)
        settings_action.setToolTip(tr("menu.settings.tooltip"))
        settings_action.triggered.connect(self._show_settings)
        file_menu.addAction(settings_action)

        # 退出动作
        exit_action = QAction(tr("menu.exit"), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 插件菜单
        plugin_menu = menubar.addMenu(tr("menu.plugins"))
        
        # 插件管理动作
        plugin_manager_action = QAction(tr("menu.plugin_manager"), self)
        plugin_manager_action.triggered.connect(self._show_plugin_manager)
        plugin_menu.addAction(plugin_manager_action)
        
        # 语言菜单
        language_menu = menubar.addMenu(tr("menu.language"))
        self._create_language_menu(language_menu)
        
        # 帮助菜单
        help_menu = menubar.addMenu(tr("menu.help"))
        
        # 欢迎页动作
        welcome_action = QAction(tr("menu.welcome"), self)
        welcome_action.triggered.connect(self._show_welcome)
        help_menu.addAction(welcome_action)
        
        help_menu.addSeparator()
        
        # 关于动作
        about_action = QAction(tr("menu.about"), self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    @deprecated("工具栏已废弃，将在未来版本中移除")
    def _create_tool_bar(self):
        """创建工具栏"""
        toolbar = QToolBar(tr("toolbar.main"), self)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addToolBar(toolbar)
        
        # 插件管理按钮
        plugin_action = QAction(tr("menu.plugin_manager"), self)
        plugin_action.setToolTip(tr("menu.plugin_manager.tooltip"))
        plugin_action.triggered.connect(self._show_plugin_manager)
        toolbar.addAction(plugin_action)
        
        toolbar.addSeparator()
        
        # 设置按钮
        settings_action = QAction(tr("menu.settings"), self)
        settings_action.setToolTip(tr("menu.settings.tooltip"))
        settings_action.triggered.connect(self._show_settings)
        toolbar.addAction(settings_action)
    
    def _create_status_bar(self):
        """创建状态栏"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # 显示就绪状态
        status_bar.showMessage(tr("status.ready"))
        
        # logger.info("状态栏创建完成")
    
    def _create_language_menu(self, language_menu):
        """创建语言菜单"""
        available_languages = self.i18n_manager.get_available_languages()
        current_language = self.i18n_manager.get_current_language()
        
        for lang_code, lang_name in available_languages.items():
            action = QAction(lang_name, self)
            action.setCheckable(True)
            action.setChecked(lang_code == current_language)
            action.triggered.connect(lambda checked, code=lang_code: self.change_language(code))
            language_menu.addAction(action)
    
    def change_language(self, language_code):
        """切换语言"""
        self.i18n_manager.set_language(language_code)
        # 重新创建菜单栏以更新语言
        self.menuBar().clear()
        self._create_menu_bar()
        # 保存语言设置
        self._save_language_settings(language_code)
        logger.info(f"🌐 Language changed to: {language_code}")
    
    def _save_language_settings(self, language_code):
        """保存语言设置"""
        try:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                "config", 
                "plugin_config.json"
            )
            
            config = {}
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            if "ui_settings" not in config:
                config["ui_settings"] = {}
            
            config["ui_settings"]["language"] = language_code
            
            # 确保目录存在
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
            logger.info(f"💾 Language settings saved: {language_code}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save language settings: {e}")
    
    def _init_plugin_manager(self):
        """初始化插件管理器"""
        try:
            self.plugin_manager = PluginManager(self)
            
            # 连接插件信号
            self.plugin_manager.plugin_loaded.connect(self._on_plugin_loaded)
            self.plugin_manager.plugin_unloaded.connect(self._on_plugin_unloaded)
            
            # 加载插件
            self.plugin_manager.load_plugins()
            
            # logger.info("插件管理器初始化完成")
            
        except Exception as e:
            logger.error(f"❌ Plugin manager initialization failed: {e}")
    
    def _init_system_tray(self):
        """初始化系统托盘"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            logger.warning("⚠️ System tray unavailable")
            return
        
        try:
            # 创建系统托盘图标
            self.system_tray = QSystemTrayIcon(self)
            
            # 设置托盘图标
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icon.svg")
            if os.path.exists(icon_path):
                self.system_tray.setIcon(QIcon(icon_path))
            
            # 创建托盘菜单
            tray_menu = QMenu()
            
            # 显示主窗口
            show_action = QAction(tr("tray.show"), self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)
            
            tray_menu.addSeparator()
            
            # 退出应用
            quit_action = QAction(tr("tray.exit"), self)
            quit_action.triggered.connect(self._quit_application)
            tray_menu.addAction(quit_action)
            
            self.system_tray.setContextMenu(tray_menu)
            self.system_tray.show()
            
            # 连接托盘图标双击事件
            self.system_tray.activated.connect(self._on_tray_activated)
            
            logger.info("📱 System tray initialized")
            
        except Exception as e:
            logger.error(f"❌ System tray initialization failed: {e}")
    
    def _on_plugin_loaded(self, plugin_name):
        """插件加载完成回调"""
        self.statusBar().showMessage(tr("status.plugin_loaded").format(name=plugin_name), 3000)
        self.plugin_loaded.emit(plugin_name)
        logger.info(f"🔌 Plugin loaded: {plugin_name}")
    
    def _on_plugin_unloaded(self, plugin_name):
        """插件卸载完成回调"""
        self.statusBar().showMessage(tr("status.plugin_unloaded").format(name=plugin_name), 3000)
        self.plugin_unloaded.emit(plugin_name)
        logger.info(f"🔌 Plugin unloaded: {plugin_name}")
    
    def _on_tray_activated(self, reason):
        """系统托盘激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()
    
    def _show_plugin_manager(self):
        """显示插件管理器"""
        # TODO: 实现插件管理器对话框
        self.statusBar().showMessage(tr("status.plugin_manager_todo"), 3000)
        logger.debug("🔧 Show plugin manager")
    
    def _show_settings(self):
        """显示设置对话框"""
        try:
            from .settings_dialog import SettingsDialog
            from PySide6.QtWidgets import QApplication
            
            dialog = SettingsDialog(self)
            
            # 连接设置变更信号
            dialog.settings_changed.connect(self._on_settings_changed)
            
            # 获取屏幕几何信息
            screen = QApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()
            
            # 计算屏幕中心位置
            screen_center_x = screen_geometry.x() + screen_geometry.width() // 2
            screen_center_y = screen_geometry.y() + screen_geometry.height() // 2
            
            # 获取对话框的大小
            dialog_size = dialog.sizeHint()
            dialog_width = dialog_size.width()
            dialog_height = dialog_size.height()
            
            # 计算对话框的位置，使其显示在屏幕中心
            dialog_x = screen_center_x - dialog_width // 2
            dialog_y = screen_center_y - dialog_height // 2
            
            # 设置对话框位置
            dialog.move(dialog_x, dialog_y)
            
            dialog.exec()
            
        except ImportError:
            # 如果设置对话框不存在，显示简单消息
            QMessageBox.information(self, "设置", "设置功能正在开发中...")
        
        logger.debug("⚙️ Show settings dialog")
    
    def _on_settings_changed(self):
        """设置变更时的处理"""
        # 重新加载并应用UI设置
        self._load_ui_settings()
        
        # 重新创建菜单栏以更新语言
        self.menuBar().clear()
        self._create_menu_bar()
        logger.debug("⚙️ Settings change handled")
    
    def _show_welcome(self):
        """显示欢迎页"""
        if self.main_window:
            self.main_window.show_welcome_tab()
        logger.debug("📋 Show welcome page")
    
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            tr("about.title"),
            tr("about.content")
        )
    
    def _quit_application(self):
        """退出应用程序"""
        from PySide6.QtWidgets import QApplication
        logger.info("👋 User requested app exit")
        if self.system_tray:
            self.system_tray.hide()
        QApplication.quit()
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.system_tray and self.system_tray.isVisible():
            # 如果有系统托盘，最小化到托盘而不是退出
            self.hide()
            event.ignore()
            
            # 显示托盘提示
            if hasattr(self, '_first_hide'):
                return
            
            self.system_tray.showMessage(
                tr("app.name"),
                tr("tray.minimized_message"),
                QSystemTrayIcon.Information,
                2000
            )
            self._first_hide = True
        else:
            # 没有系统托盘，直接退出
            logger.info("👋 Application exiting")
            event.accept()
    
    def get_plugin_manager(self):
        """获取插件管理器实例"""
        return self.plugin_manager
    
    def get_plugin_manager(self):
        """获取插件管理器实例"""
        return self.plugin_manager
    
    def get_main_window(self):
        """获取主窗口实例"""
        return self.main_window