#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LittleCapturer - 独立启动脚本
专业的截图工具插件，可以独立运行或通过HSBC LittleWorker启动

使用方法:
    python LittleCapturer.py
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from utils.logger import logger
from plugins.little_capturer import Plugin as LittleCapturerPlugin


class LittleCapturerStandalone(QMainWindow):
    """LittleCapturer独立运行窗口"""
    
    def __init__(self):
        super().__init__()
        self.plugin = None
        self.init_ui()
        self.init_plugin()
    
    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle("LittleCapturer - 专业截图工具")
        self.setMinimumSize(600, 500)
        self.resize(700, 600)
        
        # 设置窗口图标（如果存在）
        icon_path = project_root / "resources" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # 创建中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        logger.info("[STANDALONE] 🎨 UI initialized")
    
    def init_plugin(self):
        """初始化插件"""
        try:
            # 创建插件实例
            self.plugin = LittleCapturerPlugin(app=self)
            
            # 初始化插件
            if self.plugin.initialize():
                logger.info("[STANDALONE] ✅ Plugin initialized successfully")
                
                # 获取插件widget并添加到主窗口
                plugin_widget = self.plugin.get_widget()
                if plugin_widget:
                    self.main_layout.addWidget(plugin_widget)
                    logger.info("[STANDALONE] 🎯 Plugin widget added to main window")
                else:
                    logger.error("[STANDALONE] ❌ Failed to get plugin widget")
            else:
                logger.error("[STANDALONE] ❌ Failed to initialize plugin")
                
        except Exception as e:
            import traceback
            logger.error(f"[STANDALONE] ❌ Plugin initialization error: {e} - {traceback.format_exc()}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        try:
            if self.plugin:
                self.plugin.cleanup()
                logger.info("[STANDALONE] 🧹 Plugin cleanup completed")
        except Exception as e:
            logger.error(f"[STANDALONE] ❌ Cleanup error: {e}")
        
        event.accept()
        logger.info("[STANDALONE] 👋 Application closed")


def main():
    """主函数"""
    try:
        # 创建QApplication实例
        app = QApplication(sys.argv)
        app.setApplicationName("LittleCapturer")
        app.setApplicationDisplayName("LittleCapturer - 专业截图工具")
        app.setApplicationVersion("1.0.0")
        
        logger.info("[STANDALONE] 🚀 Starting LittleCapturer standalone application")
        
        # 创建主窗口
        window = LittleCapturerStandalone()
        window.show()
        
        logger.info("[STANDALONE] 🎪 Main window displayed")
        
        # 运行应用程序
        sys.exit(app.exec())
        
    except Exception as e:
        import traceback
        logger.error(f"[STANDALONE] ❌ Application startup error: {e} - {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()