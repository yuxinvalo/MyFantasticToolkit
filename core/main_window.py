# -*- coding: utf-8 -*-
"""
HSBC Little Worker - 主窗口类
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QSplitter, QFrame, QLabel, QPushButton, QScrollArea,
    QGridLayout, QGroupBox, QSizePolicy, QMenu
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QPalette, QColor, QAction

from utils.logger import logger
from .i18n import get_i18n_manager, tr


class MainWindow(QWidget):
    """主窗口类"""
    
    # 信号定义
    plugin_widget_requested = Signal(str)  # 请求插件界面信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 存储插件界面
        self.plugin_widgets = {}
        # 存储插件按钮
        self.plugin_buttons = {}
        
        # 获取国际化管理器
        self.i18n_manager = get_i18n_manager()
        
        # 初始化UI
        self._init_ui()
        
        # 连接语言变更信号
        self.i18n_manager.language_changed.connect(self.on_language_changed)
    
    def _init_ui(self):
        """初始化用户界面"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 创建欢迎区域
        welcome_widget = self._create_welcome_widget()
        main_layout.addWidget(welcome_widget)
        
        # 创建插件区域
        plugin_widget = self._create_plugin_area()
        main_layout.addWidget(plugin_widget, 1)  # 设置拉伸因子
        
        # 设置样式
        self._apply_styles()
    
    def _create_welcome_widget(self):
        """创建欢迎区域"""
        welcome_frame = QFrame()
        welcome_frame.setFrameStyle(QFrame.Box)
        welcome_frame.setMaximumHeight(120)
        
        layout = QVBoxLayout(welcome_frame)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # 标题
        self.title_label = QLabel(tr("app.title"))
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setObjectName("welcome-title")
        layout.addWidget(self.title_label)
        
        # 副标题
        self.subtitle_label = QLabel(tr("app.subtitle"))
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        self.subtitle_label.setFont(subtitle_font)
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setObjectName("welcome-subtitle")
        layout.addWidget(self.subtitle_label)
        
        return welcome_frame
    
    def _create_plugin_area(self):
        """创建插件区域"""
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：插件列表
        plugin_list_widget = self._create_plugin_list()
        splitter.addWidget(plugin_list_widget)
        
        # 右侧：插件内容区域
        content_widget = self._create_content_area()
        splitter.addWidget(content_widget)
        
        # 设置分割比例
        splitter.setSizes([250, 750])
        splitter.setCollapsible(0, False)  # 左侧不可折叠
        splitter.setCollapsible(1, False)  # 右侧不可折叠
        
        return splitter
    
    def _create_plugin_list(self):
        """创建插件列表"""
        # 创建容器
        container = QFrame()
        container.setFrameStyle(QFrame.StyledPanel)
        container.setMaximumWidth(280)
        container.setMinimumWidth(200)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # 标题
        self.plugin_list_title = QLabel(tr("plugins.available"))
        self.plugin_list_title.setObjectName("plugin-list-title")
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)
        self.plugin_list_title.setFont(title_font)
        layout.addWidget(self.plugin_list_title)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 插件按钮容器
        self.plugin_buttons_widget = QWidget()
        self.plugin_buttons_layout = QVBoxLayout(self.plugin_buttons_widget)
        self.plugin_buttons_layout.setContentsMargins(5, 5, 5, 5)
        self.plugin_buttons_layout.setSpacing(5)
        
        # 添加默认提示
        self.no_plugins_label = QLabel(tr("plugins.none_available"))
        self.no_plugins_label.setAlignment(Qt.AlignCenter)
        self.no_plugins_label.setObjectName("no-plugins-text")
        self.plugin_buttons_layout.addWidget(self.no_plugins_label)
        
        # 添加弹性空间
        self.plugin_buttons_layout.addStretch()
        
        scroll_area.setWidget(self.plugin_buttons_widget)
        layout.addWidget(scroll_area)
        
        return container
    
    def _create_content_area(self):
        """创建内容区域"""
        # 创建标签页容器
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self._close_plugin_tab)
        
        # 添加默认欢迎页
        welcome_tab = self._create_welcome_tab()
        self.welcome_tab_index = self.tab_widget.addTab(welcome_tab, tr("tab.welcome"))
        
        return self.tab_widget
    
    def _create_welcome_tab(self):
        """创建欢迎标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)
        
        # 大标题
        self.welcome_title = QLabel(tr("welcome.title"))
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        self.welcome_title.setFont(title_font)
        self.welcome_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.welcome_title)
        
        # 描述文本
        self.welcome_desc = QLabel(tr("welcome.description"))
        self.welcome_desc.setAlignment(Qt.AlignCenter)
        self.welcome_desc.setWordWrap(True)
        self.welcome_desc.setObjectName("welcome-description")
        layout.addWidget(self.welcome_desc)
        
        # 添加弹性空间
        layout.addStretch()
        
        return widget
    
    def _apply_styles(self):
        """应用样式"""
        # 样式现在由QSS文件统一管理
        pass
    
    def add_plugin_button(self, plugin_name, plugin_display_name, plugin_description=""):
        """添加插件按钮"""
        logger.debug(f"[PLUGIN] 🔌 Adding plugin button: {plugin_display_name}")
        
        # 移除默认提示（如果存在）
        if hasattr(self, 'no_plugins_label') and self.no_plugins_label:
            self.plugin_buttons_layout.removeWidget(self.no_plugins_label)
            self.no_plugins_label.deleteLater()
            self.no_plugins_label = None

        
        # 创建插件按钮
        button = QPushButton(plugin_display_name)
        button.setToolTip(plugin_description or f"打开 {plugin_display_name}")
        button.clicked.connect(lambda: self._open_plugin(plugin_name, plugin_display_name))
        
        # 设置按钮样式
        button.setMinimumHeight(40)
        button.setObjectName("plugin-button")
        
        # 存储插件按钮引用
        self.plugin_buttons[plugin_name] = button
        
        # 插入到弹性空间之前
        self.plugin_buttons_layout.insertWidget(
            self.plugin_buttons_layout.count() - 1, 
            button
        )
    
    def _open_plugin(self, plugin_name, plugin_display_name):
        """打开插件"""
        # 检查是否已经打开
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == plugin_display_name:
                self.tab_widget.setCurrentIndex(i)
                return
        
        # 发送请求插件界面信号
        self.plugin_widget_requested.emit(plugin_name)
        
        logger.debug(f"[PLUGIN] 🚀 Opening plugin: {plugin_name}")
    
    def add_plugin_widget(self, plugin_name, plugin_display_name, widget):
        """添加插件界面"""
        if widget is None:
            logger.warning(f"[PLUGIN] ⚠️ Plugin {plugin_name} returned empty widget")
            return
        
        # 存储插件界面
        self.plugin_widgets[plugin_name] = widget
        
        # 添加到标签页
        index = self.tab_widget.addTab(widget, plugin_display_name)
        self.tab_widget.setCurrentIndex(index)
        
        logger.debug(f"[PLUGIN] 📋 Plugin widget added: {plugin_display_name}")
    
    def _close_plugin_tab(self, index):
        """关闭插件标签页"""
        # if index == 0:
        #     return
        
        tab_text = self.tab_widget.tabText(index)
        self.tab_widget.removeTab(index)
        
        # 从存储中移除
        plugin_name = None
        for name, widget in self.plugin_widgets.items():
            if widget == self.tab_widget.widget(index):
                plugin_name = name
                break
        
        if plugin_name:
            del self.plugin_widgets[plugin_name]
        
        logger.debug(f"[PLUGIN] ❌ Plugin tab closed: {tab_text}")
    
    def remove_plugin_button(self, plugin_name):
        """移除插件按钮"""
        if plugin_name in self.plugin_buttons:
            button = self.plugin_buttons[plugin_name]
            self.plugin_buttons_layout.removeWidget(button)
            button.deleteLater()
            del self.plugin_buttons[plugin_name]
            logger.debug(f"[PLUGIN] 🗑️ Plugin button removed: {plugin_name}")
            
            # 如果没有插件按钮了，显示默认提示
            if not self.plugin_buttons:
                self.no_plugins_label = QLabel(tr("plugins.none_available"))
                self.no_plugins_label.setAlignment(Qt.AlignCenter)
                self.no_plugins_label.setObjectName("no-plugins-text")
                self.plugin_buttons_layout.insertWidget(
                     self.plugin_buttons_layout.count() - 1,
                     self.no_plugins_label
                 )
    
    def enable_plugin_button(self, plugin_name):
        """启用插件按钮"""
        if plugin_name in self.plugin_buttons:
            button = self.plugin_buttons[plugin_name]
            button.setEnabled(True)
            button.setObjectName("plugin-button")
            # 强制刷新样式
            button.style().unpolish(button)
            button.style().polish(button)
            logger.debug(f"[PLUGIN] ✅ Plugin button enabled: {plugin_name}")
    
    def disable_plugin_button(self, plugin_name):
        """禁用插件按钮"""
        if plugin_name in self.plugin_buttons:
            button = self.plugin_buttons[plugin_name]
            button.setEnabled(True)  # 保持按钮可点击
            button.setObjectName("plugin-button-disabled")
            # 强制刷新样式
            button.style().unpolish(button)
            button.style().polish(button)
            logger.debug(f"[PLUGIN] ❌ Plugin button disabled: {plugin_name}")
    
    def on_language_changed(self):
        """语言变更时更新界面文本"""
        # 更新欢迎区域文本
        if hasattr(self, 'title_label') and self.title_label is not None:
            self.title_label.setText(tr("app.title"))
        if hasattr(self, 'subtitle_label') and self.subtitle_label is not None:
            self.subtitle_label.setText(tr("app.subtitle"))
        
        # 更新插件列表标题
        if hasattr(self, 'plugin_list_title') and self.plugin_list_title is not None:
            self.plugin_list_title.setText(tr("plugins.available"))
        
        # 更新无插件提示
        if hasattr(self, 'no_plugins_label') and self.no_plugins_label is not None:
            self.no_plugins_label.setText(tr("plugins.none_available"))
        
        # 更新欢迎标签页
        if hasattr(self, 'welcome_tab_index') and self.welcome_tab_index is not None:
            self.tab_widget.setTabText(self.welcome_tab_index, tr("tab.welcome"))
        
        # 更新欢迎页面内容
        if hasattr(self, 'welcome_title') and self.welcome_title is not None:
            self.welcome_title.setText(tr("welcome.title"))
        if hasattr(self, 'welcome_desc') and self.welcome_desc is not None:
            self.welcome_desc.setText(tr("welcome.description"))
        
        logger.debug("[SETTINGS] 🌐 Main window text updated")
    
    def on_settings_changed(self):
        """设置变更时的处理"""
        # 通知父窗口更新菜单栏
        if self.parent():
            parent = self.parent()
            if hasattr(parent, '_create_menu_bar'):
                parent.menuBar().clear()
                parent._create_menu_bar()
        logger.debug("[SETTINGS] ⚙️ Settings change handled")
    
    def get_plugin_widget(self, plugin_name):
        """获取插件界面"""
        return self.plugin_widgets.get(plugin_name)
    
    def show_plugin_manager(self):
        """显示插件管理器"""
        # 通过父窗口调用插件管理器
        if self.parent() and hasattr(self.parent(), '_show_plugin_manager'):
            self.parent()._show_plugin_manager()
        logger.debug("[PLUGIN] 🔧 Show plugin manager")
    
    def show_settings(self):
        """显示设置对话框"""
        # 通过父窗口调用设置对话框
        if self.parent() and hasattr(self.parent(), '_show_settings'):
            self.parent()._show_settings()
        logger.debug("[SETTINGS] ⚙️ Show settings dialog")
    
    def show_welcome_tab(self):
        """显示欢迎页标签"""
        # 检查欢迎页是否已经存在
        if hasattr(self, 'welcome_tab_index') and self.welcome_tab_index is not None:
            # 如果欢迎页还在，直接切换到它
            for i in range(self.tab_widget.count()):
                if i == self.welcome_tab_index:
                    self.tab_widget.setCurrentIndex(i)
                    logger.debug("[UI] 📋 Switched to existing welcome tab")
                    return
        
        # 如果欢迎页不存在，重新创建
        welcome_tab = self._create_welcome_tab()
        self.welcome_tab_index = self.tab_widget.addTab(welcome_tab, tr("tab.welcome"))
        self.tab_widget.setCurrentIndex(self.welcome_tab_index)
        logger.debug("[UI] 📋 Created and showed new welcome tab")