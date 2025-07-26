# -*- coding: utf-8 -*-
"""
国际化支持模块
提供多语言支持功能
"""

import os
import json
from typing import Dict, Optional
from PySide6.QtCore import QObject, Signal, QLocale, QTranslator, QCoreApplication
from PySide6.QtWidgets import QApplication


class I18nManager(QObject):
    """国际化管理器"""
    
    # 语言变更信号
    language_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.current_language = "zh_CN"  # 默认中文
        self.translations: Dict[str, Dict[str, str]] = {}
        self.translator = QTranslator()
        self.available_languages = {
            "zh_CN": "简体中文",
            "en_US": "English"
        }
        
        # 翻译文件目录
        self.translations_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "resources", 
            "translations"
        )
        
        # 确保翻译目录存在
        os.makedirs(self.translations_dir, exist_ok=True)
        
        # 加载翻译文件
        self.load_translations()
        
        # 设置默认语言
        self.set_language(self.detect_system_language())
    
    def detect_system_language(self) -> str:
        """检测系统语言"""
        system_locale = QLocale.system().name()
        if system_locale.startswith("zh"):
            return "zh_CN"
        elif system_locale.startswith("en"):
            return "en_US"
        else:
            return "zh_CN"  # 默认中文
    
    def load_translations(self):
        """加载所有翻译文件"""
        for lang_code in self.available_languages.keys():
            translation_file = os.path.join(self.translations_dir, f"{lang_code}.json")
            if os.path.exists(translation_file):
                try:
                    with open(translation_file, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                except Exception as e:
                    print(f"Failed to load translation file {translation_file}: {e}")
                    self.translations[lang_code] = {}
            else:
                self.translations[lang_code] = {}
    
    def set_language(self, language_code: str):
        """设置当前语言"""
        if language_code in self.available_languages:
            self.current_language = language_code
            
            # 安装Qt翻译器
            app = QApplication.instance()
            if app:
                app.removeTranslator(self.translator)
                
                # 加载Qt内置翻译
                qt_translation_file = f"qt_{language_code}"
                if self.translator.load(qt_translation_file, QCoreApplication.applicationDirPath()):
                    app.installTranslator(self.translator)
            
            # 发送语言变更信号
            self.language_changed.emit(language_code)
    
    def get_current_language(self) -> str:
        """获取当前语言"""
        return self.current_language
    
    def get_available_languages(self) -> Dict[str, str]:
        """获取可用语言列表"""
        return self.available_languages.copy()
    
    def tr(self, key: str, default: Optional[str] = None) -> str:
        """翻译文本"""
        if self.current_language in self.translations:
            translation = self.translations[self.current_language].get(key)
            if translation:
                return translation
        
        # 如果当前语言没有翻译，尝试使用英文
        if self.current_language != "en_US" and "en_US" in self.translations:
            translation = self.translations["en_US"].get(key)
            if translation:
                return translation
        
        # 返回默认值或键名
        return default if default is not None else key
    
    def add_translation(self, language_code: str, key: str, value: str):
        """添加翻译"""
        if language_code not in self.translations:
            self.translations[language_code] = {}
        self.translations[language_code][key] = value
    
    def save_translations(self):
        """保存翻译文件"""
        for lang_code, translations in self.translations.items():
            translation_file = os.path.join(self.translations_dir, f"{lang_code}.json")
            try:
                with open(translation_file, 'w', encoding='utf-8') as f:
                    json.dump(translations, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Failed to save translation file {translation_file}: {e}")


# 全局国际化管理器实例
_i18n_manager = None


def get_i18n_manager() -> I18nManager:
    """获取国际化管理器实例"""
    global _i18n_manager
    if _i18n_manager is None:
        _i18n_manager = I18nManager()
    return _i18n_manager


def tr(key: str, default: Optional[str] = None) -> str:
    """翻译文本的便捷函数"""
    return get_i18n_manager().tr(key, default)


def set_language(language_code: str):
    """设置语言的便捷函数"""
    get_i18n_manager().set_language(language_code)


def get_current_language() -> str:
    """获取当前语言的便捷函数"""
    return get_i18n_manager().get_current_language()