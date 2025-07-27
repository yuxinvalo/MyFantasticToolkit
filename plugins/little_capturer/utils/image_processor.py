# -*- coding: utf-8 -*-
"""
LittleCapturer - 图片处理模块
提供图片编辑、OCR识别、保存等功能
"""

from PySide6.QtCore import QObject, Signal, QRect, QPoint
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QFont
from typing import Optional, List, Tuple
from pathlib import Path

from utils.logger import logger


class ImageProcessor(QObject):
    """图片处理器"""
    
    # 信号定义
    image_saved = Signal(str)  # 图片保存完成信号
    ocr_completed = Signal(str)  # OCR识别完成信号
    edit_applied = Signal()  # 编辑应用完成信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_image: Optional[QPixmap] = None
        self._edit_history: List[QPixmap] = []
        self._edit_index = -1
        
        logger.debug("[IMAGE] 🖼️ ImageProcessor initialized")
    
    def set_image(self, pixmap: QPixmap) -> bool:
        """设置当前处理的图片
        
        Args:
            pixmap: 要处理的图片
            
        Returns:
            bool: 设置是否成功
        """
        try:
            if pixmap.isNull():
                logger.warning("[IMAGE] ⚠️ Cannot set null pixmap")
                return False
            
            self._current_image = pixmap.copy()
            
            # 清空编辑历史并添加原始图片
            self._edit_history.clear()
            self._edit_history.append(self._current_image.copy())
            self._edit_index = 0
            
            logger.info(f"[IMAGE] ✅ Image set successfully, size: {pixmap.size()}")
            return True
            
        except Exception as e:
            import traceback
            logger.error(f"[IMAGE] ❌ Failed to set image: {e} - {traceback.format_exc()}")
            return False
    
    def get_current_image(self) -> Optional[QPixmap]:
        """获取当前图片
        
        Returns:
            QPixmap: 当前图片，如果没有则返回None
        """
        return self._current_image
    
    def save_image(self, file_path: str, format: str = "PNG", quality: int = 100) -> bool:
        """保存图片到文件
        
        Args:
            file_path: 保存路径
            format: 图片格式 (PNG, JPG, BMP等)
            quality: 图片质量 (1-100)
            
        Returns:
            bool: 保存是否成功
        """
        try:
            if not self._current_image or self._current_image.isNull():
                logger.warning("[IMAGE] ⚠️ No image to save")
                return False
            
            # 确保目录存在
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"[IMAGE] 💾 Saving image to: {file_path}")
            
            # 保存图片
            success = self._current_image.save(str(file_path), format, quality)
            
            if success:
                self.image_saved.emit(str(file_path))
                logger.info(f"[IMAGE] ✅ Image saved successfully: {file_path}")
            else:
                logger.error(f"[IMAGE] ❌ Failed to save image: {file_path}")
            
            return success
            
        except Exception as e:
            import traceback
            logger.error(f"[IMAGE] ❌ Failed to save image: {e} - {traceback.format_exc()}")
            return False
    
    def perform_ocr(self) -> str:
        """对当前图片执行OCR文字识别
        
        Returns:
            str: 识别出的文字内容
        """
        try:
            if not self._current_image or self._current_image.isNull():
                logger.warning("[IMAGE] ⚠️ No image for OCR")
                return ""
            
            logger.info("[IMAGE] 🔍 Starting OCR recognition")
            
            # TODO: 实现OCR识别逻辑
            # 可以使用以下库之一：
            # 1. pytesseract (Tesseract OCR)
            # 2. easyocr
            # 3. paddleocr
            # 4. 百度/腾讯等云服务API
            
            # 临时返回示例文本
            recognized_text = "这是OCR识别的示例文本\nThis is sample OCR text"
            
            self.ocr_completed.emit(recognized_text)
            logger.info("[IMAGE] ✅ OCR recognition completed")
            
            return recognized_text
            
        except Exception as e:
            import traceback
            logger.error(f"[IMAGE] ❌ OCR recognition failed: {e} - {traceback.format_exc()}")
            return ""
    
    def add_text_annotation(self, text: str, position: QPoint, font_size: int = 12, color: QColor = QColor(255, 0, 0)) -> bool:
        """添加文字标注
        
        Args:
            text: 标注文字
            position: 标注位置
            font_size: 字体大小
            color: 文字颜色
            
        Returns:
            bool: 添加是否成功
        """
        try:
            if not self._current_image or self._current_image.isNull():
                logger.warning("[IMAGE] ⚠️ No image for text annotation")
                return False
            
            logger.info(f"[IMAGE] ✏️ Adding text annotation: {text} at {position}")
            
            # 创建新的图片副本
            new_image = self._current_image.copy()
            
            # 在图片上绘制文字
            painter = QPainter(new_image)
            painter.setRenderHint(QPainter.Antialiasing)
            
            font = QFont()
            font.setPointSize(font_size)
            painter.setFont(font)
            painter.setPen(QPen(color))
            
            painter.drawText(position, text)
            painter.end()
            
            # 更新当前图片并添加到历史记录
            self._add_to_history(new_image)
            
            self.edit_applied.emit()
            logger.info("[IMAGE] ✅ Text annotation added successfully")
            
            return True
            
        except Exception as e:
            import traceback
            logger.error(f"[IMAGE] ❌ Failed to add text annotation: {e} - {traceback.format_exc()}")
            return False
    
    def add_rectangle(self, rect: QRect, pen_color: QColor = QColor(255, 0, 0), pen_width: int = 2) -> bool:
        """添加矩形标注
        
        Args:
            rect: 矩形区域
            pen_color: 边框颜色
            pen_width: 边框宽度
            
        Returns:
            bool: 添加是否成功
        """
        try:
            if not self._current_image or self._current_image.isNull():
                logger.warning("[IMAGE] ⚠️ No image for rectangle annotation")
                return False
            
            logger.info(f"[IMAGE] 📐 Adding rectangle annotation: {rect}")
            
            # 创建新的图片副本
            new_image = self._current_image.copy()
            
            # 在图片上绘制矩形
            painter = QPainter(new_image)
            painter.setRenderHint(QPainter.Antialiasing)
            
            pen = QPen(pen_color)
            pen.setWidth(pen_width)
            painter.setPen(pen)
            
            painter.drawRect(rect)
            painter.end()
            
            # 更新当前图片并添加到历史记录
            self._add_to_history(new_image)
            
            self.edit_applied.emit()
            logger.info("[IMAGE] ✅ Rectangle annotation added successfully")
            
            return True
            
        except Exception as e:
            import traceback
            logger.error(f"[IMAGE] ❌ Failed to add rectangle annotation: {e} - {traceback.format_exc()}")
            return False
    
    def add_arrow(self, start_point: QPoint, end_point: QPoint, pen_color: QColor = QColor(255, 0, 0), pen_width: int = 2) -> bool:
        """添加箭头标注
        
        Args:
            start_point: 起始点
            end_point: 结束点
            pen_color: 箭头颜色
            pen_width: 箭头宽度
            
        Returns:
            bool: 添加是否成功
        """
        try:
            if not self._current_image or self._current_image.isNull():
                logger.warning("[IMAGE] ⚠️ No image for arrow annotation")
                return False
            
            logger.info(f"[IMAGE] ➡️ Adding arrow annotation: {start_point} -> {end_point}")
            
            # 创建新的图片副本
            new_image = self._current_image.copy()
            
            # 在图片上绘制箭头
            painter = QPainter(new_image)
            painter.setRenderHint(QPainter.Antialiasing)
            
            pen = QPen(pen_color)
            pen.setWidth(pen_width)
            painter.setPen(pen)
            
            # TODO: 实现箭头绘制逻辑
            # 1. 绘制主线
            # 2. 计算箭头头部的两个点
            # 3. 绘制箭头头部
            
            painter.drawLine(start_point, end_point)
            painter.end()
            
            # 更新当前图片并添加到历史记录
            self._add_to_history(new_image)
            
            self.edit_applied.emit()
            logger.info("[IMAGE] ✅ Arrow annotation added successfully")
            
            return True
            
        except Exception as e:
            import traceback
            logger.error(f"[IMAGE] ❌ Failed to add arrow annotation: {e} - {traceback.format_exc()}")
            return False
    
    def undo(self) -> bool:
        """撤销上一步操作
        
        Returns:
            bool: 撤销是否成功
        """
        try:
            if self._edit_index <= 0:
                logger.warning("[IMAGE] ⚠️ No operation to undo")
                return False
            
            self._edit_index -= 1
            self._current_image = self._edit_history[self._edit_index].copy()
            
            logger.info("[IMAGE] ↶ Undo operation completed")
            self.edit_applied.emit()
            
            return True
            
        except Exception as e:
            import traceback
            logger.error(f"[IMAGE] ❌ Failed to undo: {e} - {traceback.format_exc()}")
            return False
    
    def redo(self) -> bool:
        """重做下一步操作
        
        Returns:
            bool: 重做是否成功
        """
        try:
            if self._edit_index >= len(self._edit_history) - 1:
                logger.warning("[IMAGE] ⚠️ No operation to redo")
                return False
            
            self._edit_index += 1
            self._current_image = self._edit_history[self._edit_index].copy()
            
            logger.info("[IMAGE] ↷ Redo operation completed")
            self.edit_applied.emit()
            
            return True
            
        except Exception as e:
            import traceback
            logger.error(f"[IMAGE] ❌ Failed to redo: {e} - {traceback.format_exc()}")
            return False
    
    def can_undo(self) -> bool:
        """检查是否可以撤销
        
        Returns:
            bool: 是否可以撤销
        """
        return self._edit_index > 0
    
    def can_redo(self) -> bool:
        """检查是否可以重做
        
        Returns:
            bool: 是否可以重做
        """
        return self._edit_index < len(self._edit_history) - 1
    
    def _add_to_history(self, pixmap: QPixmap):
        """添加图片到编辑历史
        
        Args:
            pixmap: 要添加的图片
        """
        try:
            # 如果当前不在历史记录的末尾，删除后续的记录
            if self._edit_index < len(self._edit_history) - 1:
                self._edit_history = self._edit_history[:self._edit_index + 1]
            
            # 添加新的图片到历史记录
            self._edit_history.append(pixmap.copy())
            self._edit_index = len(self._edit_history) - 1
            
            # 更新当前图片
            self._current_image = pixmap.copy()
            
            # 限制历史记录数量（避免内存过多占用）
            max_history = 20
            if len(self._edit_history) > max_history:
                self._edit_history = self._edit_history[-max_history:]
                self._edit_index = len(self._edit_history) - 1
            
            logger.debug(f"[IMAGE] 📝 Added to edit history, index: {self._edit_index}")
            
        except Exception as e:
            import traceback
            logger.error(f"[IMAGE] ❌ Failed to add to history: {e} - {traceback.format_exc()}")
    
    def clear_history(self):
        """清空编辑历史"""
        try:
            self._edit_history.clear()
            self._edit_index = -1
            logger.info("[IMAGE] 🧹 Edit history cleared")
            
        except Exception as e:
            import traceback
            logger.error(f"[IMAGE] ❌ Failed to clear history: {e} - {traceback.format_exc()}")
    
    def get_image_info(self) -> dict:
        """获取当前图片信息
        
        Returns:
            dict: 图片信息字典
        """
        try:
            if not self._current_image or self._current_image.isNull():
                return {}
            
            return {
                'width': self._current_image.width(),
                'height': self._current_image.height(),
                'depth': self._current_image.depth(),
                'format': self._current_image.format(),
                'has_alpha': self._current_image.hasAlpha(),
                'size_bytes': self._current_image.sizeInBytes()
            }
            
        except Exception as e:
            import traceback
            logger.error(f"[IMAGE] ❌ Failed to get image info: {e} - {traceback.format_exc()}")
            return {}