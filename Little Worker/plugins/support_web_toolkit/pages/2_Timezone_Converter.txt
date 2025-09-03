# -*- coding: utf-8 -*-
"""
时差转换工具页面
"""

import streamlit as st
import json
from datetime import datetime, timezone
from pathlib import Path
import pytz
from common import load_config, load_translations, tr, init_language, apply_button_styles, render_source_time_card

# 页面配置
st.set_page_config(
    page_title="Timezone Converter - IT Support Toolkit",
    page_icon="🌍",
    layout="wide"
)

# 初始化语言设置
init_language()

# 应用通用按钮样式
apply_button_styles()

# 常用时区列表
COMMON_TIMEZONES = {
    'UTC': 'UTC',
    'Asia/Shanghai': 'China Standard Time (CST)',
    'Asia/Hong_Kong': 'Hong Kong Time (HKT)',
    'Asia/Tokyo': 'Japan Standard Time (JST)',
    'Asia/Singapore': 'Singapore Standard Time (SGT)',
    'Europe/London': 'Greenwich Mean Time (GMT)',
    'Europe/Paris': 'Central European Time (CET)',
    'US/Eastern': 'Eastern Standard Time (EST)',
    'US/Central': 'Central Standard Time (CST)',
    'US/Mountain': 'Mountain Standard Time (MST)',
    'US/Pacific': 'Pacific Standard Time (PST)',
    'Australia/Sydney': 'Australian Eastern Standard Time (AEST)',
    'Asia/Kolkata': 'India Standard Time (IST)'
}

# 读取时区转换器配置
def load_timezone_config():
    """加载时区转换器配置"""
    try:
        config = load_config()
        tz_config = config.get('timezone_converter', {})
        return {
            'source_timezone': tz_config.get('source_timezone', 'Asia/Shanghai'),
            'target_timezones': tz_config.get('target_timezones', ['UTC', 'US/Eastern', 'Europe/London'])
        }
    except Exception as e:
        st.error(f"配置加载失败: {str(e)}")
        return {
            'source_timezone': 'Asia/Shanghai',
            'target_timezones': ['UTC', 'US/Eastern', 'Europe/London']
        }

# 保存时区转换器配置
def save_timezone_config(source_timezone, target_timezones):
    """保存时区转换器配置"""
    try:
        import sys
        # 获取插件目录（适配打包环境）
        if getattr(sys, 'frozen', False):
            # 打包后的环境
            plugin_dir = Path(sys.executable).parent / "plugins" / "support_web_toolkit"
        else:
            # 开发环境
            plugin_dir = Path(__file__).parent.parent
        
        config_path = plugin_dir / 'config.json'
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        config['timezone_converter'] = {
            'source_timezone': source_timezone,
            'target_timezones': target_timezones
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        st.error(f"Timezone converter config save failed: {str(e)} - {traceback.format_exc()}")
        return False

# 加载配置
tz_config = load_timezone_config()

# 页面标题和描述
st.title(f"🌍 {tr('timezone_converter.title')}")

# 主要功能区域
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(f"📅 {tr('timezone_converter.input_time_section')}")
    
    # 日期选择器
    current_time = datetime.now()
    date_input = st.date_input(tr("timezone_converter.select_date"), value=current_time.date())
    
    # 初始化session state中的时间值
    if 'default_time' not in st.session_state:
        st.session_state.default_time = current_time.strftime("%H:%M:%S")
    
    # 时间手动输入 - 使用session state保持用户输入
    time_str = st.text_input(
        tr("timezone_converter.enter_time"),
        value=st.session_state.default_time,
        help=tr("timezone_converter.time_format_help"),
        key="time_input"
    )
    
    # 更新session state中的时间值
    st.session_state.default_time = time_str
    
    try:
        time_input = datetime.strptime(time_str, "%H:%M:%S").time()
        input_datetime = datetime.combine(date_input, time_input)
    except ValueError:
        st.error(tr("timezone_converter.time_format_error"))
        input_datetime = current_time
    
    # 源时区选择
    st.subheader(f"🌏 {tr('timezone_converter.source_timezone_section')}")
    
    # 获取配置中的源时区索引
    try:
        source_index = list(COMMON_TIMEZONES.keys()).index(tz_config['source_timezone'])
    except ValueError:
        source_index = 1  # 默认选择 Asia/Shanghai
    
    from_tz_key = st.selectbox(
        tr("timezone_converter.select_source_timezone"),
        options=list(COMMON_TIMEZONES.keys()),
        index=source_index,
        format_func=lambda x: f"{x} - {COMMON_TIMEZONES[x]}",
        key="source_timezone_select"
    )

with col2:
    st.subheader(f"🎯 {tr('timezone_converter.target_timezones_section')}")
    
    # 目标时区选择（支持多选）
    target_timezones = st.multiselect(
        tr("timezone_converter.select_target_timezones"),
        options=list(COMMON_TIMEZONES.keys()),
        default=tz_config['target_timezones'],
        format_func=lambda x: f"{x} - {COMMON_TIMEZONES[x]}",
        key="target_timezones_select"
    )
    
    # 转换按钮
    convert_button = st.button(f"🔄 {tr('timezone_converter.convert_button')}", use_container_width=True)

# 转换结果显示
if convert_button and target_timezones:
    # 保存配置
    save_timezone_config(from_tz_key, target_timezones)
    
    try:
        # 创建源时区的datetime对象
        from_tz = pytz.timezone(from_tz_key)
        localized_dt = from_tz.localize(input_datetime)
        
        st.subheader(f"⏰ {tr('timezone_converter.conversion_results')}")
        
        # 显示源时间
        source_time_html = render_source_time_card(
            tr('timezone_converter.source_time'),
            localized_dt.strftime('%Y-%m-%d %H:%M:%S %Z')
        )
        st.markdown(source_time_html, unsafe_allow_html=True)
        st.markdown("---")
        
        # 转换到各个目标时区
        import pandas as pd
        
        # 添加自定义CSS样式
        st.markdown("""
        <style>
        .stDataFrame {
            border: 2px solid #e1e5e9;
            border-radius: 10px;
            overflow: hidden;
        }
        .stDataFrame > div {
            border-radius: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        table_data = []
        for tz_key in target_timezones:
            target_tz = pytz.timezone(tz_key)
            converted_dt = localized_dt.astimezone(target_tz)
            
            # 计算时差
            time_diff = converted_dt.utcoffset() - localized_dt.utcoffset()
            hours_diff = time_diff.total_seconds() / 3600
            
            # 格式化时差显示
            if hours_diff > 0:
                diff_display = f"🔺 +{hours_diff:.1f}h"
            elif hours_diff < 0:
                diff_display = f"🔻 {hours_diff:.1f}h"
            else:
                diff_display = "⚪ Same"
            
            table_data.append({
                '🌍 时区': tz_key,
                '📍 描述': COMMON_TIMEZONES[tz_key],
                '🕐 转换时间': converted_dt.strftime('%Y-%m-%d %H:%M:%S %Z'),
                '⏰ 时差': diff_display
            })
        
        # 创建并显示表格
        df = pd.DataFrame(table_data)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                '🌍 时区': st.column_config.TextColumn(
                    width="medium",
                    help="Target timezone"
                ),
                '📍 描述': st.column_config.TextColumn(
                    width="large",
                    help="Timezone description"
                ),
                '🕐 转换时间': st.column_config.TextColumn(
                    width="large",
                    help="Converted time"
                ),
                '⏰ 时差': st.column_config.TextColumn(
                    width="small",
                    help="Time difference from source timezone"
                )
            }
        )
        

            
    except Exception as e:
        st.error(f"❌ {tr('timezone_converter.conversion_error')}: {str(e)}")

elif convert_button and not target_timezones:
    st.warning(f"⚠️ {tr('timezone_converter.select_at_least_one')}")


# 返回主页按钮
st.markdown("---")
if st.button(f"🏠 {tr('timezone_converter.back_home')}", use_container_width=True):
    st.switch_page("streamlit_app.py")
