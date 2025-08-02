# -*- coding: utf-8 -*-
"""
通用函数模块
包含配置加载、翻译等共用功能
"""

import json
from pathlib import Path
import streamlit as st


def load_config() -> dict:
    """加载配置文件"""
    try:
        current_dir = Path(__file__).parent
        config_file = current_dir / "config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Failed to load config: {e}")
    return {}


def load_translations(lang_code: str) -> dict:
    """加载翻译文件"""
    try:
        current_dir = Path(__file__).parent
        trans_file = current_dir / "translations" / f"{lang_code}.json"
        if trans_file.exists():
            with open(trans_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Failed to load translations: {e}")
    return {}


def tr(key: str, lang_code: str = None) -> str:
    """翻译函数"""
    if lang_code is None:
        lang_code = st.session_state.get('language', 'zh_CN')
    
    translations = load_translations(lang_code)
    return translations.get(key, key)


def save_config(config: dict):
    """保存配置文件"""
    try:
        current_dir = Path(__file__).parent
        config_file = current_dir / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Failed to save config: {e}")
        return False


def update_language_config(new_language: str):
    """更新配置文件中的语言设置"""
    config = load_config()
    config['web_language'] = new_language
    return save_config(config)


def init_language():
    """初始化语言设置，从配置文件读取默认语言"""
    if 'language' not in st.session_state:
        config = load_config()
        default_language = config.get('web_language', 'zh_CN')
        st.session_state.language = default_language