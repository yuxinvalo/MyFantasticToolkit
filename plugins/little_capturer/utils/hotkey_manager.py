# -*- coding: utf-8 -*-
"""
LittleCapturer - 全局热键管理模块
基于pynput库提供更可靠的全局热键注册和管理功能
"""

import threading
from typing import Callable, Dict, Optional, Set
from pynput import keyboard
from PySide6.QtCore import QObject, Signal

from utils.logger import logger


class GlobalHotkeyManager(QObject):
    """基于pynput的全局热键管理器"""
    
    # 定义信号
    hotkey_triggered = Signal(str)  # 热键触发信号
    
    def __init__(self):
        super().__init__()
        self._hotkeys: Dict[str, Callable] = {}  # 热键字符串到回调函数的映射
        self._listener: Optional[keyboard.GlobalHotKeys] = None
        self._running = False
        self._lock = threading.Lock()
        
    def start(self):
        """启动热键监听"""
        try:
            with self._lock:
                if self._running:
                    logger.warning("[HOTKEY] ⚠️ Hotkey manager is already running")
                    return True
                    
                # 如果有已注册的热键，创建监听器
                if self._hotkeys:
                    self._create_listener()
                    
                self._running = True
                logger.info("[HOTKEY] 🚀 Hotkey manager started")
                return True
                
        except Exception as e:
            import traceback
            logger.error(f"[HOTKEY] ❌ Failed to start hotkey manager: {e} - {traceback.format_exc()}")
            return False
    
    def stop(self):
        """停止热键监听"""
        try:
            with self._lock:
                if not self._running:
                    return
                    
                self._running = False
                
                # 停止监听器
                if self._listener:
                    self._listener.stop()
                    self._listener = None
                    
                logger.info("[HOTKEY] 🛑 Hotkey manager stopped")
                
        except Exception as e:
            import traceback
            logger.error(f"[HOTKEY] ❌ Failed to stop hotkey manager: {e} - {traceback.format_exc()}")
    
    def register_hotkey(self, hotkey: str, callback: Callable) -> bool:
        """注册热键
        
        Args:
            hotkey: 热键字符串，如 'alt+shift+z', 'ctrl+c' 等
            callback: 热键触发时的回调函数
            
        Returns:
            bool: 注册是否成功
        """
        try:
            # 标准化热键字符串
            normalized_hotkey = self._normalize_hotkey(hotkey)
            if not normalized_hotkey:
                logger.error(f"[HOTKEY] ❌ Invalid hotkey format: {hotkey}")
                return False
            
            with self._lock:
                # 检查是否已经注册
                if normalized_hotkey in self._hotkeys:
                    logger.warning(f"[HOTKEY] ⚠️ Hotkey already registered: {normalized_hotkey}")
                    return False
                
                # 添加到热键映射
                self._hotkeys[normalized_hotkey] = callback
                
                # 如果管理器正在运行，重新创建监听器
                if self._running:
                    self._recreate_listener()
                
                logger.info(f"[HOTKEY] ✅ Hotkey registered: {normalized_hotkey}")
                return True
                
        except Exception as e:
            import traceback
            logger.error(f"[HOTKEY] ❌ Failed to register hotkey {hotkey}: {e} - {traceback.format_exc()}")
            return False
    
    def unregister_hotkey(self, hotkey: str) -> bool:
        """注销热键
        
        Args:
            hotkey: 要注销的热键字符串
            
        Returns:
            bool: 注销是否成功
        """
        try:
            normalized_hotkey = self._normalize_hotkey(hotkey)
            if not normalized_hotkey:
                logger.error(f"[HOTKEY] ❌ Invalid hotkey format: {hotkey}")
                return False
            
            with self._lock:
                if normalized_hotkey not in self._hotkeys:
                    logger.warning(f"[HOTKEY] ⚠️ Hotkey not found: {normalized_hotkey}")
                    return False
                
                # 从热键映射中移除
                del self._hotkeys[normalized_hotkey]
                
                # 如果管理器正在运行，重新创建监听器
                if self._running:
                    self._recreate_listener()
                
                logger.info(f"[HOTKEY] ✅ Hotkey unregistered: {normalized_hotkey}")
                return True
                
        except Exception as e:
            import traceback
            logger.error(f"[HOTKEY] ❌ Failed to unregister hotkey {hotkey}: {e} - {traceback.format_exc()}")
            return False
    
    def _normalize_hotkey(self, hotkey: str) -> Optional[str]:
        """标准化热键字符串
        
        将用户输入的热键字符串转换为pynput可识别的格式
        例如: 'Alt+Shift+Z' -> '<alt>+<shift>+z'
        """
        try:
            if not hotkey or not isinstance(hotkey, str):
                return None
            
            # 分割并清理各部分
            parts = [part.strip().lower() for part in hotkey.split('+')]
            if len(parts) < 2:
                return None
            
            # 修饰键映射
            modifier_map = {
                'ctrl': '<ctrl>',
                'control': '<ctrl>',
                'alt': '<alt>',
                'shift': '<shift>',
                'win': '<cmd>',
                'cmd': '<cmd>',
                'super': '<cmd>'
            }
            
            # 特殊键映射
            special_key_map = {
                'space': '<space>',
                'enter': '<enter>',
                'return': '<enter>',
                'tab': '<tab>',
                'esc': '<esc>',
                'escape': '<esc>',
                'backspace': '<backspace>',
                'delete': '<delete>',
                'del': '<delete>',
                'insert': '<insert>',
                'home': '<home>',
                'end': '<end>',
                'pageup': '<page_up>',
                'pagedown': '<page_down>',
                'up': '<up>',
                'down': '<down>',
                'left': '<left>',
                'right': '<right>'
            }
            
            # 处理功能键
            for i in range(1, 13):
                special_key_map[f'f{i}'] = f'<f{i}>'
            
            normalized_parts = []
            
            for part in parts:
                if part in modifier_map:
                    normalized_parts.append(modifier_map[part])
                elif part in special_key_map:
                    normalized_parts.append(special_key_map[part])
                elif len(part) == 1 and part.isalnum():
                    # 单个字母或数字
                    normalized_parts.append(part.lower())
                else:
                    logger.warning(f"[HOTKEY] ⚠️ Unknown key part: {part}")
                    return None
            
            return '+'.join(normalized_parts)
            
        except Exception as e:
            import traceback
            logger.error(f"[HOTKEY] ❌ Failed to normalize hotkey {hotkey}: {e} - {traceback.format_exc()}")
            return None
    
    def _create_listener(self):
        """创建热键监听器"""
        try:
            if not self._hotkeys:
                return
            
            # 创建热键映射，将回调包装为触发信号的函数
            hotkey_map = {}
            for hotkey_str, callback in self._hotkeys.items():
                hotkey_map[hotkey_str] = lambda h=hotkey_str, c=callback: self._on_hotkey_triggered(h, c)
            
            # 创建全局热键监听器
            self._listener = keyboard.GlobalHotKeys(hotkey_map)
            self._listener.start()
            
            logger.info(f"[HOTKEY] 🎧 Listener created with {len(hotkey_map)} hotkeys")
            
        except Exception as e:
            import traceback
            logger.error(f"[HOTKEY] ❌ Failed to create listener: {e} - {traceback.format_exc()}")
    
    def _recreate_listener(self):
        """重新创建监听器"""
        try:
            # 停止现有监听器
            if self._listener:
                self._listener.stop()
                self._listener = None
            
            # 创建新监听器
            self._create_listener()
            
        except Exception as e:
            import traceback
            logger.error(f"[HOTKEY] ❌ Failed to recreate listener: {e} - {traceback.format_exc()}")
    
    def _on_hotkey_triggered(self, hotkey_str: str, callback: Callable):
        """热键触发处理"""
        try:
            logger.info(f"[HOTKEY] 🎯 Hotkey triggered: {hotkey_str}")
            
            # 发射信号
            self.hotkey_triggered.emit(hotkey_str)
            
            # 执行回调
            if callable(callback):
                callback()
            else:
                logger.warning(f"[HOTKEY] ⚠️ Invalid callback for hotkey: {hotkey_str}")
                
        except Exception as e:
            import traceback
            logger.error(f"[HOTKEY] ❌ Error handling hotkey trigger: {e} - {traceback.format_exc()}")
    
    def get_registered_hotkeys(self) -> Dict[str, Callable]:
        """获取已注册的热键列表"""
        with self._lock:
            return self._hotkeys.copy()
    
    def is_running(self) -> bool:
        """检查管理器是否正在运行"""
        return self._running
    
    def cleanup(self):
        """清理资源"""
        self.stop()
        with self._lock:
            self._hotkeys.clear()