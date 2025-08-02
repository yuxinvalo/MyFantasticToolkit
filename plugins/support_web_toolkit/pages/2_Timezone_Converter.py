# -*- coding: utf-8 -*-
"""
时差转换工具页面
"""

import streamlit as st
import json
from datetime import datetime, timezone
from pathlib import Path
import pytz
from common import load_config, load_translations, tr, init_language, apply_button_styles

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

# 页面标题
if st.session_state.language == 'zh_CN':
    st.title("🌍 时差转换工具")
    st.markdown("在不同时区之间转换时间")
else:
    st.title("🌍 Timezone Converter")
    st.markdown("Convert time between different timezones")

# 主要功能区域
col1, col2 = st.columns([1, 1])

with col1:
    if st.session_state.language == 'zh_CN':
        st.subheader("📅 输入时间")
        
        # 时间输入方式选择
        input_method = st.radio(
            "选择输入方式",
            ["日期时间选择器", "当前时间", "手动输入"]
        )
        
        if input_method == "日期时间选择器":
            date_input = st.date_input("选择日期")
            time_input = st.time_input("选择时间")
            input_datetime = datetime.combine(date_input, time_input)
        elif input_method == "当前时间":
            input_datetime = datetime.now()
            st.info(f"当前时间: {input_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        else:  # 手动输入
            datetime_str = st.text_input(
                "输入日期时间",
                placeholder="2024-01-01 12:00:00",
                help="格式: YYYY-MM-DD HH:MM:SS"
            )
            try:
                input_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                if datetime_str:
                    st.error("日期时间格式错误，请使用 YYYY-MM-DD HH:MM:SS 格式")
                input_datetime = datetime.now()
        
        # 源时区选择
        st.subheader("🌏 源时区")
        from_tz_key = st.selectbox(
            "选择源时区",
            options=list(COMMON_TIMEZONES.keys()),
            index=1,  # 默认选择 Asia/Shanghai
            format_func=lambda x: f"{x} - {COMMON_TIMEZONES[x]}"
        )
        
    else:
        st.subheader("📅 Input Time")
        
        # Time input method selection
        input_method = st.radio(
            "Select input method",
            ["Date Time Picker", "Current Time", "Manual Input"]
        )
        
        if input_method == "Date Time Picker":
            date_input = st.date_input("Select Date")
            time_input = st.time_input("Select Time")
            input_datetime = datetime.combine(date_input, time_input)
        elif input_method == "Current Time":
            input_datetime = datetime.now()
            st.info(f"Current time: {input_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        else:  # Manual Input
            datetime_str = st.text_input(
                "Enter date time",
                placeholder="2024-01-01 12:00:00",
                help="Format: YYYY-MM-DD HH:MM:SS"
            )
            try:
                input_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                if datetime_str:
                    st.error("Invalid date time format, please use YYYY-MM-DD HH:MM:SS")
                input_datetime = datetime.now()
        
        # Source timezone selection
        st.subheader("🌏 Source Timezone")
        from_tz_key = st.selectbox(
            "Select source timezone",
            options=list(COMMON_TIMEZONES.keys()),
            index=1,  # Default to Asia/Shanghai
            format_func=lambda x: f"{x} - {COMMON_TIMEZONES[x]}"
        )

with col2:
    if st.session_state.language == 'zh_CN':
        st.subheader("🎯 目标时区")
        
        # 目标时区选择（支持多选）
        target_timezones = st.multiselect(
            "选择目标时区（可多选）",
            options=list(COMMON_TIMEZONES.keys()),
            default=['UTC', 'US/Eastern', 'Europe/London'],
            format_func=lambda x: f"{x} - {COMMON_TIMEZONES[x]}"
        )
        
        # 转换按钮
        convert_button = st.button("🔄 转换时间", type="primary", use_container_width=True)
        
    else:
        st.subheader("🎯 Target Timezones")
        
        # Target timezone selection (multi-select)
        target_timezones = st.multiselect(
            "Select target timezones (multiple selection)",
            options=list(COMMON_TIMEZONES.keys()),
            default=['UTC', 'US/Eastern', 'Europe/London'],
            format_func=lambda x: f"{x} - {COMMON_TIMEZONES[x]}"
        )
        
        # Convert button
        convert_button = st.button("🔄 Convert Time", type="primary", use_container_width=True)

# 转换结果显示
if convert_button and target_timezones:
    try:
        # 创建源时区的datetime对象
        from_tz = pytz.timezone(from_tz_key)
        localized_dt = from_tz.localize(input_datetime)
        
        if st.session_state.language == 'zh_CN':
            st.subheader("⏰ 转换结果")
            
            # 显示源时间
            st.markdown(f"**源时间**: {localized_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            st.markdown("---")
            
        else:
            st.subheader("⏰ Conversion Results")
            
            # Display source time
            st.markdown(f"**Source Time**: {localized_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            st.markdown("---")
        
        # 转换到各个目标时区
        results = []
        for tz_key in target_timezones:
            target_tz = pytz.timezone(tz_key)
            converted_dt = localized_dt.astimezone(target_tz)
            
            # 计算时差
            time_diff = converted_dt.utcoffset() - localized_dt.utcoffset()
            hours_diff = time_diff.total_seconds() / 3600
            
            results.append({
                'timezone': tz_key,
                'name': COMMON_TIMEZONES[tz_key],
                'time': converted_dt.strftime('%Y-%m-%d %H:%M:%S %Z'),
                'diff': f"{hours_diff:+.1f}h" if hours_diff != 0 else "Same"
            })
            
            # 显示结果
            col_tz, col_time, col_diff = st.columns([2, 2, 1])
            with col_tz:
                st.write(f"**{tz_key}**")
                st.caption(COMMON_TIMEZONES[tz_key])
            with col_time:
                st.write(converted_dt.strftime('%Y-%m-%d %H:%M:%S %Z'))
            with col_diff:
                if hours_diff > 0:
                    st.success(f"+{hours_diff:.1f}h")
                elif hours_diff < 0:
                    st.error(f"{hours_diff:.1f}h")
                else:
                    st.info("Same")
        
        # 导出功能
        st.markdown("---")
        if st.session_state.language == 'zh_CN':
            st.subheader("💾 导出结果")
            
            # 生成导出文本
            export_text = f"时间转换结果\n\n源时间: {localized_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}\n\n"
            for result in results:
                export_text += f"{result['timezone']} ({result['name']}): {result['time']} ({result['diff']})\n"
            
            st.download_button(
                "📄 下载转换结果",
                export_text,
                "timezone_conversion.txt",
                "text/plain",
                use_container_width=True
            )
        else:
            st.subheader("💾 Export Results")
            
            # Generate export text
            export_text = f"Timezone Conversion Results\n\nSource Time: {localized_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}\n\n"
            for result in results:
                export_text += f"{result['timezone']} ({result['name']}): {result['time']} ({result['diff']})\n"
            
            st.download_button(
                "📄 Download Results",
                export_text,
                "timezone_conversion.txt",
                "text/plain",
                use_container_width=True
            )
            
    except Exception as e:
        if st.session_state.language == 'zh_CN':
            st.error(f"❌ 转换错误: {str(e)}")
        else:
            st.error(f"❌ Conversion error: {str(e)}")

elif convert_button and not target_timezones:
    if st.session_state.language == 'zh_CN':
        st.warning("⚠️ 请至少选择一个目标时区")
    else:
        st.warning("⚠️ Please select at least one target timezone")

else:
    # 显示使用说明
    if st.session_state.language == 'zh_CN':
        st.info("💡 选择时间和时区，然后点击转换按钮")
        with st.expander("📖 使用说明"):
            st.markdown("""
            1. 选择时间输入方式：
               - **日期时间选择器**: 使用界面控件选择
               - **当前时间**: 使用系统当前时间
               - **手动输入**: 输入特定的日期时间
            
            2. 选择源时区（时间所在的时区）
            
            3. 选择一个或多个目标时区
            
            4. 点击"转换时间"按钮查看结果
            
            **支持的功能：**
            - 多时区同时转换
            - 时差计算显示
            - 结果导出为文本文件
            - 常用时区快速选择
            """)
    else:
        st.info("💡 Select time and timezones, then click the convert button")
        with st.expander("📖 Usage Instructions"):
            st.markdown("""
            1. Choose time input method:
               - **Date Time Picker**: Use interface controls
               - **Current Time**: Use system current time
               - **Manual Input**: Enter specific date time
            
            2. Select source timezone (where the time is from)
            
            3. Select one or more target timezones
            
            4. Click "Convert Time" button to see results
            
            **Supported features:**
            - Multiple timezone conversion
            - Time difference calculation
            - Export results as text file
            - Quick common timezone selection
            """)

# 返回主页按钮
st.markdown("---")
if st.session_state.language == 'zh_CN':
    if st.button("🏠 返回主页", use_container_width=True):
        st.switch_page("streamlit_app.py")
else:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("streamlit_app.py")