# -*- coding: utf-8 -*-
"""
LittleCapturer - 全局热键管理模块
提供全局热键注册和管理功能
"""

from PySide6.QtCore import QObject, Signal
from typing import Callable, Dict, Optional

from utils.logger import logger


class GlobalHotkeyManager(QObject):
    """全局热键管理器"""
    
    # 信号定义
    hotkey_triggered = Signal(str)  # 热键触发信号
    hotkey_registered = Signal(str)  # 热键注册成功信号
    hotkey_unregistered = Signal(str)  # 热键注销成功信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._registered_hotkeys: Dict[str, Callable] = {}
        self._is_enabled = True
        
        logger.debug("[HOTKEY] ⌨️ GlobalHotkeyManager initialized")
    
    def register_hotkey(self, hotkey: str, callback: Callable) -> bool:
        """注册全局热键
        
        Args:
            hotkey: 热键组合字符串 (例如: "Alt+Shift+A")
            callback: 热键触发时的回调函数
            
        Returns:
            bool: 注册是否成功
        """
        try:
            if not hotkey or not callback:
                logger.warning("[HOTKEY] ⚠️ Invalid hotkey or callback")
                return False
            
            if hotkey in self._registered_hotkeys:
                logger.warning(f"[HOTKEY] ⚠️ Hotkey already registered: {hotkey}")
                return False
            
            logger.info(f"[HOTKEY] 📝 Registering hotkey: {hotkey}")
            
            # TODO: 实现系统级热键注册
            # Windows: 使用 RegisterHotKey API
            # Linux: 使用 X11 或其他方式
            # macOS: 使用 Carbon 或其他方式
            
            # 解析热键字符串
            parsed_hotkey = self._parse_hotkey(hotkey)
            if not parsed_hotkey:
                logger.error(f"[HOTKEY] ❌ Failed to parse hotkey: {hotkey}")
                return False
            
            # 注册到系统
            success = self._register_system_hotkey(parsed_hotkey)
            if success:
                self._registered_hotkeys[hotkey] = callback
                self.hotkey_registered.emit(hotkey)
                logger.info(f"[HOTKEY] ✅ Hotkey registered successfully: {hotkey}")
                return True
            else:
                logger.error(f"[HOTKEY] ❌ Failed to register system hotkey: {hotkey}")
                return False
            
        except Exception as e:
            import traceback
            logger.error(f"[HOTKEY] ❌ Failed to register hotkey {hotkey}: {e} - {traceback.format_exc()}")
            return False
    
    def unregister_hotkey(self, hotkey: str) -> bool:
        """注销全局热键
        
        Args:
            hotkey: 要注销的热键组合字符串
            
        Returns:
            bool: 注销是否成功
        """
        try:
            if hotkey not in self._registered_hotkeys:
                logger.warning(f"[HOTKEY] ⚠️ Hotkey not registered: {hotkey}")
                return False
            
            logger.info(f"[HOTKEY] 🗑️ Unregistering hotkey: {hotkey}")
            
            # TODO: 实现系统级热键注销
            
            # 解析热键字符串
            parsed_hotkey = self._parse_hotkey(hotkey)
            if not parsed_hotkey:
                logger.error(f"[HOTKEY] ❌ Failed to parse hotkey for unregistration: {hotkey}")
                return False
            
            # 从系统注销
            success = self._unregister_system_hotkey(parsed_hotkey)
            if success:
                del self._registered_hotkeys[hotkey]
                self.hotkey_unregistered.emit(hotkey)
                logger.info(f"[HOTKEY] ✅ Hotkey unregistered successfully: {hotkey}")
                return True
            else:
                logger.error(f"[HOTKEY] ❌ Failed to unregister system hotkey: {hotkey}")
                return False
            
        except Exception as e:
            import traceback
            logger.error(f"[HOTKEY] ❌ Failed to unregister hotkey {hotkey}: {e} - {traceback.format_exc()}")
            return False
    
    def unregister_all_hotkeys(self):
        """注销所有已注册的热键"""
        try:
            logger.info("[HOTKEY] 🧹 Unregistering all hotkeys")
            
            hotkeys_to_remove = list(self._registered_hotkeys.keys())
            for hotkey in hotkeys_to_remove:
                self.unregister_hotkey(hotkey)
            
            logger.info("[HOTKEY] ✅ All hotkeys unregistered")
            
        except Exception as e:
            import traceback
            logger.error(f"[HOTKEY] ❌ Failed to unregister all hotkeys: {e} - {traceback.format_exc()}")
    
    def set_enabled(self, enabled: bool):
        """设置热键管理器启用状态
        
        Args:
            enabled: 是否启用
        """
        try:
            if self._is_enabled == enabled:
                return
            
            self._is_enabled = enabled
            status = "enabled" if enabled else "disabled"
            logger.info(f"[HOTKEY] 🔄 Hotkey manager {status}")
            
            # TODO: 实现启用/禁用逻辑
            
        except Exception as e:
            import traceback
            logger.error(f"[HOTKEY] ❌ Failed to set enabled state: {e} - {traceback.format_exc()}")
    
    def is_enabled(self) -> bool:
        """检查热键管理器是否启用
        
        Returns:
            bool: 是否启用
        """
        return self._is_enabled
    
    def get_registered_hotkeys(self) -> list:
        """获取已注册的热键列表
        
        Returns:
            list: 已注册的热键列表
        """
        return list(self._registered_hotkeys.keys())
    
    def _parse_hotkey(self, hotkey: str) -> Optional[dict]:
        """解析热键字符串
        
        Args:
            hotkey: 热键字符串 (例如: "Alt+Shift+A")
            
        Returns:
            dict: 解析后的热键信息，失败返回None
        """
        try:
            if not hotkey:
                return None
            
            # TODO: 实现热键字符串解析
            # 1. 分割修饰键和主键
            # 2. 转换为系统识别的键码
            # 3. 返回解析结果
            
            parts = hotkey.split('+')
            if not parts:
                return None
            
            modifiers = []
            key = None
            
            for part in parts:
                part = part.strip()
                if part.lower() in ['ctrl', 'control']:
                    modifiers.append('ctrl')
                elif part.lower() in ['alt']:
                    modifiers.append('alt')
                elif part.lower() in ['shift']:
                    modifiers.append('shift')
                elif part.lower() in ['win', 'windows', 'cmd', 'meta']:
                    modifiers.append('win')
                else:
                    key = part.upper()
            
            if not key:
                return None
            
            return {
                'modifiers': modifiers,
                'key': key,
                'original': hotkey
            }
            
        except Exception as e:
            import traceback
            logger.error(f"[HOTKEY] ❌ Failed to parse hotkey {hotkey}: {e} - {traceback.format_exc()}")
            return None
    
    def _register_system_hotkey(self, parsed_hotkey: dict) -> bool:
        """注册系统级热键
        
        Args:
            parsed_hotkey: 解析后的热键信息
            
        Returns:
            bool: 注册是否成功
        """
        try:
            # TODO: 实现平台特定的热键注册
            # Windows: 使用 ctypes 调用 RegisterHotKey
            # Linux: 使用 python-xlib 或其他库
            # macOS: 使用 PyObjC 或其他库
            
            logger.debug(f"[HOTKEY] 🔧 Registering system hotkey: {parsed_hotkey}")
            
            # 临时返回True，实际实现时需要调用系统API
            return True
            
        except Exception as e:
            import traceback
            logger.error(f"[HOTKEY] ❌ Failed to register system hotkey: {e} - {traceback.format_exc()}")
            return False
    
    def _unregister_system_hotkey(self, parsed_hotkey: dict) -> bool:
        """注销系统级热键
        
        Args:
            parsed_hotkey: 解析后的热键信息
            
        Returns:
            bool: 注销是否成功
        """
        try:
            # TODO: 实现平台特定的热键注销
            
            logger.debug(f"[HOTKEY] 🔧 Unregistering system hotkey: {parsed_hotkey}")
            
            # 临时返回True，实际实现时需要调用系统API
            return True
            
        except Exception as e:
            import traceback
            logger.error(f"[HOTKEY] ❌ Failed to unregister system hotkey: {e} - {traceback.format_exc()}")
            return False
    
    def _on_hotkey_triggered(self, hotkey: str):
        """热键触发回调
        
        Args:
            hotkey: 触发的热键字符串
        """
        try:
            if not self._is_enabled:
                return
            
            if hotkey in self._registered_hotkeys:
                callback = self._registered_hotkeys[hotkey]
                logger.info(f"[HOTKEY] 🎯 Hotkey triggered: {hotkey}")
                
                # 发射信号
                self.hotkey_triggered.emit(hotkey)
                
                # 调用回调函数
                if callback:
                    callback()
            else:
                logger.warning(f"[HOTKEY] ⚠️ Unknown hotkey triggered: {hotkey}")
                
        except Exception as e:
            import traceback
            logger.error(f"[HOTKEY] ❌ Error handling hotkey trigger: {e} - {traceback.format_exc()}")
    
    def cleanup(self):
        """清理资源"""
        try:
            logger.info("[HOTKEY] 🧹 Cleaning up hotkey manager")
            self.unregister_all_hotkeys()
            
        except Exception as e:
            import traceback
            logger.error(f"[HOTKEY] ❌ Failed to cleanup: {e} - {traceback.format_exc()}")