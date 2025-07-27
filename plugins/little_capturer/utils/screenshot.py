# -*- coding: utf-8 -*-
"""
LittleCapturer - 截图功能模块
提供屏幕截图的核心功能
"""

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import QObject, Signal, QRect, Qt, QPoint
from PySide6.QtGui import QPixmap, QScreen, QPainter, QPen, QBrush, QColor, QCursor, QKeyEvent, QMouseEvent, QPaintEvent
from typing import Optional, Callable

from utils.logger import logger


class ScreenCapture(QObject):
    """屏幕截图类"""
    
    # 信号定义
    capture_started = Signal()  # 截图开始信号
    capture_completed = Signal(QPixmap, QRect)  # 截图完成信号 (图片, 区域)
    capture_cancelled = Signal()  # 截图取消信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_capturing = False
        self._capture_window = None
        
        logger.debug("[SCREENSHOT] 📸 ScreenCapture initialized")
    
    def start_capture(self) -> bool:
        """开始截图
        
        Returns:
            bool: 是否成功开始截图
        """
        try:
            if self._is_capturing:
                logger.warning("[SCREENSHOT] ⚠️ Capture already in progress")
                return False
            
            self._is_capturing = True
            logger.info("[SCREENSHOT] 🎯 Starting screen capture")
            
            # TODO: 实现截图逻辑
            # 1. 创建全屏覆盖窗口
            # 2. 捕获屏幕内容
            # 3. 显示选择区域界面
            
            self.capture_started.emit()
            return True
            
        except Exception as e:
            import traceback
            logger.error(f"[SCREENSHOT] ❌ Failed to start capture: {e} - {traceback.format_exc()}")
            self._is_capturing = False
            return False
    
    def cancel_capture(self):
        """取消截图"""
        try:
            if not self._is_capturing:
                return
            
            logger.info("[SCREENSHOT] 🚫 Cancelling screen capture")
            self._is_capturing = False
            
            # TODO: 清理截图相关资源
            
            self.capture_cancelled.emit()
            
        except Exception as e:
            import traceback
            logger.error(f"[SCREENSHOT] ❌ Failed to cancel capture: {e} - {traceback.format_exc()}")
    
    def capture_area(self, rect: QRect) -> Optional[QPixmap]:
        """截取指定区域
        
        Args:
            rect: 截图区域
            
        Returns:
            QPixmap: 截图结果，失败返回None
        """
        try:
            logger.info(f"[SCREENSHOT] 📷 Capturing area: {rect}")
            
            # 获取主屏幕
            screen = QApplication.primaryScreen()
            if not screen:
                logger.error("[SCREENSHOT] ❌ No primary screen found")
                return None
            
            # 截取全屏
            full_pixmap = screen.grabWindow(0)
            if full_pixmap.isNull():
                logger.error("[SCREENSHOT] ❌ Failed to capture full screen")
                return None
            
            # 裁剪指定区域
            area_pixmap = full_pixmap.copy(rect)
            
            if not area_pixmap.isNull():
                self.capture_completed.emit(area_pixmap, rect)
                logger.info("[SCREENSHOT] ✅ Area capture completed")
            
            return area_pixmap
            
        except Exception as e:
            import traceback
            logger.error(f"[SCREENSHOT] ❌ Failed to capture area: {e} - {traceback.format_exc()}")
            return None
        finally:
            self._is_capturing = False
    
    def capture_full_screen(self) -> Optional[QPixmap]:
        """全屏截图
        
        Returns:
            QPixmap: 截图结果，失败返回None
        """
        try:
            logger.info("[SCREENSHOT] 🖥️ Capturing full screen")
            
            # 获取主屏幕
            screen = QApplication.primaryScreen()
            if not screen:
                logger.error("[SCREENSHOT] ❌ No primary screen found")
                return None
            
            # 截取全屏
            pixmap = screen.grabWindow(0)
            
            if not pixmap.isNull():
                logger.info("[SCREENSHOT] ✅ Full screen capture completed")
            
            return pixmap
            
        except Exception as e:
            import traceback
            logger.error(f"[SCREENSHOT] ❌ Failed to capture full screen: {e} - {traceback.format_exc()}")
            return None
    
    def is_capturing(self) -> bool:
        """检查是否正在截图
        
        Returns:
            bool: 是否正在截图
        """
        return self._is_capturing
    
    def get_screen_geometry(self) -> QRect:
        """获取屏幕几何信息
        
        Returns:
            QRect: 屏幕区域
        """
        try:
            # 获取主屏幕
            screen = QApplication.primaryScreen()
            if not screen:
                logger.error("[SCREENSHOT] ❌ No primary screen found")
                return QRect()
            
            # 获取屏幕几何信息
            geometry = screen.geometry()
            logger.debug(f"[SCREENSHOT] 📐 Screen geometry: {geometry}")
            
            return geometry
            
        except Exception as e:
            import traceback
            logger.error(f"[SCREENSHOT] ❌ Failed to get screen geometry: {e} - {traceback.format_exc()}")
            return QRect()


class CaptureWindow(QWidget):
    """截图选择窗口"""
    
    # 信号定义
    area_selected = Signal(QRect)  # 区域选择完成信号
    capture_cancelled = Signal()  # 取消截图信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 选择状态
        self._selecting = False
        self._start_point = QPoint()
        self._end_point = QPoint()
        self._selection_rect = QRect()
        
        # 背景截图
        self._background_pixmap = QPixmap()
        
        self._setup_ui()
        self._setup_events()
        
        logger.debug("[SCREENSHOT] 🪟 CaptureWindow initialized")
    
    def _setup_ui(self):
        """设置UI界面"""
        try:
            # 设置窗口属性
            self.setWindowTitle("LittleCapturer - 选择截图区域")
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.BypassWindowManagerHint
            )
            
            # 设置窗口属性
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
            self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
            
            # 设置全屏
            screen = QApplication.primaryScreen()
            if screen:
                self.setGeometry(screen.geometry())
            
            # 设置鼠标样式
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            
            # 设置焦点策略
            self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            
            logger.debug("[SCREENSHOT] 🎨 CaptureWindow UI setup completed")
            
        except Exception as e:
            import traceback
            logger.error(f"[SCREENSHOT] ❌ Failed to setup UI: {e} - {traceback.format_exc()}")
    
    def _setup_events(self):
        """设置事件处理"""
        try:
            # 启用鼠标跟踪
            self.setMouseTracking(True)
            
            logger.debug("[SCREENSHOT] ⚡ CaptureWindow events setup completed")
            
        except Exception as e:
            import traceback
            logger.error(f"[SCREENSHOT] ❌ Failed to setup events: {e} - {traceback.format_exc()}")
    
    def show_capture_window(self):
        """显示截图选择窗口"""
        try:
            logger.info("[SCREENSHOT] 👁️ Showing capture window")
            
            # 获取屏幕截图作为背景
            screen = QApplication.primaryScreen()
            if screen:
                self._background_pixmap = screen.grabWindow(0)
                logger.debug("[SCREENSHOT] 📸 Background screenshot captured")
            
            # 重置选择区域
            self._selection_rect = QRect()
            self._start_point = QPoint()
            
            # 显示窗口
            self.show()
            self.showFullScreen()
            self.raise_()
            self.activateWindow()
            self.setFocus()
            
            # 确保窗口在最顶层
            self.setWindowState(Qt.WindowState.WindowFullScreen)
            
        except Exception as e:
            import traceback
            logger.error(f"[SCREENSHOT] ❌ Failed to show capture window: {e} - {traceback.format_exc()}")
    
    def hide_capture_window(self):
        """隐藏截图选择窗口"""
        try:
            logger.info("[SCREENSHOT] 🙈 Hiding capture window")
            self.hide()
            
        except Exception as e:
            import traceback
            logger.error(f"[SCREENSHOT] ❌ Failed to hide capture window: {e} - {traceback.format_exc()}")
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                self._selecting = True
                self._start_point = event.pos()
                self._end_point = event.pos()
                self._selection_rect = QRect()
                logger.debug(f"[SCREENSHOT] 🖱️ Mouse press at: {self._start_point}")
                self.update()
            
        except Exception as e:
            import traceback
            logger.error(f"[SCREENSHOT] ❌ Mouse press event error: {e} - {traceback.format_exc()}")
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件"""
        try:
            if self._selecting:
                self._end_point = event.pos()
                # 计算选择矩形
                self._selection_rect = QRect(
                    min(self._start_point.x(), self._end_point.x()),
                    min(self._start_point.y(), self._end_point.y()),
                    abs(self._end_point.x() - self._start_point.x()),
                    abs(self._end_point.y() - self._start_point.y())
                )
                self.update()
            
        except Exception as e:
            import traceback
            logger.error(f"[SCREENSHOT] ❌ Mouse move event error: {e} - {traceback.format_exc()}")
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        try:
            if event.button() == Qt.MouseButton.LeftButton and self._selecting:
                self._selecting = False
                self._end_point = event.pos()
                
                # 计算最终选择矩形
                self._selection_rect = QRect(
                    min(self._start_point.x(), self._end_point.x()),
                    min(self._start_point.y(), self._end_point.y()),
                    abs(self._end_point.x() - self._start_point.x()),
                    abs(self._end_point.y() - self._start_point.y())
                )
                
                logger.info(f"[SCREENSHOT] ✅ Area selected: {self._selection_rect}")
                
                # 如果选择区域有效，发射信号
                if self._selection_rect.width() > 5 and self._selection_rect.height() > 5:
                    self.area_selected.emit(self._selection_rect)
                    self.hide_capture_window()
                else:
                    logger.warning("[SCREENSHOT] ⚠️ Selected area too small, ignoring")
                    self._selection_rect = QRect()
                    self.update()
            
        except Exception as e:
            import traceback
            logger.error(f"[SCREENSHOT] ❌ Mouse release event error: {e} - {traceback.format_exc()}")
    
    def keyPressEvent(self, event: QKeyEvent):
        """键盘按下事件"""
        try:
            if event.key() == Qt.Key.Key_Escape:
                logger.info("[SCREENSHOT] 🚫 Capture cancelled by user (ESC)")
                self.capture_cancelled.emit()
                self.hide_capture_window()
            else:
                super().keyPressEvent(event)
            
        except Exception as e:
            import traceback
            logger.error(f"[SCREENSHOT] ❌ Key press event error: {e} - {traceback.format_exc()}")
    
    def paintEvent(self, event: QPaintEvent):
        """绘制事件"""
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # 绘制背景截图
            if not self._background_pixmap.isNull():
                painter.drawPixmap(0, 0, self._background_pixmap)
            
            # 绘制半透明遮罩，但排除选择区域
            mask_color = QColor(0, 0, 0, 100)
            
            if not self._selection_rect.isEmpty():
                # 分别绘制四个遮罩区域，避开选择区域
                screen_rect = self.rect()
                
                # 上方遮罩
                if self._selection_rect.top() > 0:
                    top_rect = QRect(0, 0, screen_rect.width(), self._selection_rect.top())
                    painter.fillRect(top_rect, mask_color)
                
                # 下方遮罩
                if self._selection_rect.bottom() < screen_rect.bottom():
                    bottom_rect = QRect(0, self._selection_rect.bottom() + 1, 
                                      screen_rect.width(), 
                                      screen_rect.bottom() - self._selection_rect.bottom())
                    painter.fillRect(bottom_rect, mask_color)
                
                # 左侧遮罩
                if self._selection_rect.left() > 0:
                    left_rect = QRect(0, self._selection_rect.top(), 
                                    self._selection_rect.left(), 
                                    self._selection_rect.height())
                    painter.fillRect(left_rect, mask_color)
                
                # 右侧遮罩
                if self._selection_rect.right() < screen_rect.right():
                    right_rect = QRect(self._selection_rect.right() + 1, self._selection_rect.top(),
                                     screen_rect.right() - self._selection_rect.right(),
                                     self._selection_rect.height())
                    painter.fillRect(right_rect, mask_color)
                
                # 绘制选择框边框
                pen = QPen(QColor(0, 120, 215), 2)  # 蓝色边框
                painter.setPen(pen)
                painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
                painter.drawRect(self._selection_rect)
            else:
                # 没有选择区域时，绘制全屏遮罩
                painter.fillRect(self.rect(), mask_color)
                
                # 绘制尺寸信息
                if self._selection_rect.width() > 50 and self._selection_rect.height() > 30:
                    size_text = f"{self._selection_rect.width()} × {self._selection_rect.height()}"
                    text_rect = painter.fontMetrics().boundingRect(size_text)
                    text_pos = QPoint(
                        self._selection_rect.x() + 5,
                        self._selection_rect.y() - 5
                    )
                    
                    # 确保文本在屏幕内
                    if text_pos.y() < text_rect.height():
                        text_pos.setY(self._selection_rect.y() + text_rect.height() + 5)
                    
                    # 绘制文本背景
                    text_bg_rect = QRect(
                        text_pos.x() - 3,
                        text_pos.y() - text_rect.height() - 3,
                        text_rect.width() + 6,
                        text_rect.height() + 6
                    )
                    painter.fillRect(text_bg_rect, QColor(0, 0, 0, 150))
                    
                    # 绘制文本
                    painter.setPen(QPen(QColor(255, 255, 255)))
                    painter.drawText(text_pos, size_text)
            
        except Exception as e:
            import traceback
            logger.error(f"[SCREENSHOT] ❌ Paint event error: {e} - {traceback.format_exc()}")