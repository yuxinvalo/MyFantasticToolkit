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


def apply_button_styles():
    """应用通用按钮样式"""
    st.markdown("""
    <style>
    /* 主要操作按钮样式 - 使用Streamlit主题色 */
    .stButton > button {
        background: linear-gradient(135deg, #ff4b4b, #ff6b6b);
        color: white !important;
        border: 2px solid transparent;
        border-radius: 10px;
        font-weight: 600;
        font-size: 14px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.3);
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #ff2b2b, #ff4b4b);
        box-shadow: 0 6px 20px rgba(255, 75, 75, 0.4);
        transform: translateY(-2px);
        border: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    .stButton > button:active {
        transform: translateY(0px);
        box-shadow: 0 2px 8px rgba(255, 75, 75, 0.3);
    }
    
    /* 编辑快速链接按钮 - 紫色主题 */
    .stButton > button:first-child {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button:first-child:hover {
        background: linear-gradient(135deg, #5a6fd8, #6a4190) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* 下载按钮样式 - 蓝色主题 */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #1f77b4, #4dabf7) !important;
        color: white !important;
        border: 2px solid transparent;
        border-radius: 10px;
        font-weight: 600;
        font-size: 14px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(31, 119, 180, 0.3);
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #1864ab, #339af0) !important;
        box-shadow: 0 6px 20px rgba(31, 119, 180, 0.4);
        transform: translateY(-2px);
        border: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    /* 成功/保存按钮 - 绿色主题 */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #51cf66, #69db7c) !important;
        box-shadow: 0 4px 12px rgba(81, 207, 102, 0.3) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #40c057, #51cf66) !important;
        box-shadow: 0 6px 20px rgba(81, 207, 102, 0.4) !important;
    }
    
    /* Save As按钮样式 - 与下载按钮相同的蓝色主题，使用更高优先级 */
    div[data-testid="column"]:nth-child(3) .stButton > button {
        background: linear-gradient(135deg, #1f77b4, #4dabf7) !important;
        color: white !important;
        border: 2px solid transparent !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(31, 119, 180, 0.3) !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
    }
    
    div[data-testid="column"]:nth-child(3) .stButton > button:hover {
        background: linear-gradient(135deg, #1864ab, #339af0) !important;
        box-shadow: 0 6px 20px rgba(31, 119, 180, 0.4) !important;
        transform: translateY(-2px) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .stButton > button {
            font-size: 12px;
            padding: 0.4rem 0.8rem;
        }
    }
    
    /* 确保按钮文字可见性 */
    .stButton > button span {
        color: white !important;
    }
    
    .stDownloadButton > button span {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)


def render_source_time_card(label: str, time_str: str):
    """渲染源时间卡片样式"""
    return f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        border-left: 4px solid #4CAF50;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    ">
        <div style="
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 5px;
            font-weight: 500;
        ">🕐 {label}</div>
        <div style="
            font-size: 18px;
            font-weight: bold;
            font-family: 'Courier New', monospace;
            letter-spacing: 1px;
        ">{time_str}</div>
    </div>
    """


def init_language():
    """初始化语言设置，从配置文件读取默认语言"""
    if 'language' not in st.session_state:
        config = load_config()
        default_language = config.get('web_language', 'zh_CN')
        st.session_state.language = default_language