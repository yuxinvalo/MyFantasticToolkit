#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HSBC Little Worker - 主程序入口
个人工作小工具集合
"""

import sys
import os
import traceback
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtNetwork import QLocalSocket, QLocalServer

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.application import LittleWorkerApp
from utils.logger import logger, cleanup_old_logs
from utils.config_manager import ConfigurationManager


def get_app_config():
    """获取应用配置"""
    defaults = {
        "name": "HSBC Little Worker",
        "version": "1.0.0",
        "organization": "HSBC Finance IT Support",
        "author": "Tearsyu",
        "description": "HSBC Little Worker 是一个基于 PySide6 开发的插件化工具平台，用于个人工作小工具集合。",
        "license": "MIT"
    }
    
    config = ConfigurationManager.load_json_config("config/app_config.json", {"app_info": defaults})
    return config.get("app_info", defaults)


def main():
    """主程序入口"""
    try:
        app_config = get_app_config()
        
        socket = QLocalSocket()
        socket.connectToServer(app_config["name"])
        if socket.waitForConnected(1000):
            logger.info("[STARTUP] Another instance of HSBC Little Worker is already running. Sending activation signal.")
            # 发送激活信号给已运行的实例
            socket.write(b"ACTIVATE")
            socket.waitForBytesWritten(1000)
            socket.disconnectFromServer()
            sys.exit(0)
        else:
            app = QApplication(sys.argv)
            
            # 创建本地服务器监听新实例连接
            local_server = QLocalServer()
            local_server.listen(app_config["name"])
            
            # 设置应用程序信息
            app.setApplicationName(app_config["name"])
            app.setApplicationVersion(app_config["version"])
            app.setOrganizationName(app_config["organization"])
            
            # 设置应用程序图标
            icon_path = os.path.join(os.path.dirname(__file__), "resources", "icon.svg")
            if os.path.exists(icon_path):
                app.setWindowIcon(QIcon(icon_path))
            
            logger.info("[STARTUP] Starting HSBC Little Worker Application...")
            
            # 清理旧日志文件
            cleanup_old_logs()
            
            # 创建主应用程序实例
            little_worker = LittleWorkerApp()
            
            # 连接本地服务器的新连接信号
            def handle_new_connection():
                """Handle new local connection"""
                logger.info("[STARTUP] New connection from local server.")
                client_socket = local_server.nextPendingConnection()
                if client_socket:
                    client_socket.readyRead.connect(lambda: handle_client_message(client_socket))
            
            def handle_client_message(client_socket):
                """Handle client message"""
                data = client_socket.readAll().data()
                if data == b"ACTIVATE":
                    logger.info("[STARTUP] Received activation signal from new instance.")
                    # 激活主窗口
                    little_worker.show()
                    little_worker.raise_()
                    little_worker.activateWindow()
                    # 如果窗口被最小化，恢复它
                    if little_worker.isMinimized():
                        little_worker.showNormal()
                client_socket.deleteLater()
            
            local_server.newConnection.connect(handle_new_connection)
            
            # 显示主窗口
            little_worker.show()
            
            # 运行应用程序事件循环
            sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"[STARTUP] App start failed with error : {e} - {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()