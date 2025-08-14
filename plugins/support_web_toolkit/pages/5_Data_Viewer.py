# -*- coding: utf-8 -*-
"""
CSV/Excel数据查看器页面
"""

import streamlit as st
import pandas as pd
import io
from pathlib import Path
from datetime import datetime
from common import load_config, load_translations, tr, init_language, save_config, apply_button_styles

# 页面配置
st.set_page_config(
    page_title="Data Viewer - IT Support Toolkit",
    page_icon="📊",
    layout="wide"
)

# 初始化语言设置
init_language()

# 应用通用按钮样式
apply_button_styles()

# 初始化会话状态
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'selected_columns' not in st.session_state:
    st.session_state.selected_columns = []
if 'available_columns' not in st.session_state:
    st.session_state.available_columns = []

# 页面标题
st.title(f"📊 {tr('data_viewer.title')}")
st.markdown(f"**{tr('data_viewer.description')}**")

# 文件上传区域
st.subheader(f"📁 {tr('data_viewer.upload_section')}")

uploaded_file = st.file_uploader(
    tr('data_viewer.upload_label'),
    type=['csv', 'xlsx', 'xls'],
    help=tr('data_viewer.upload_help')
)

if uploaded_file is not None:
    try:
        # 读取文件
        if uploaded_file.name.endswith('.csv'):
            # CSV文件处理
            # 尝试不同的编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            df = None
            
            for encoding in encodings:
                try:
                    uploaded_file.seek(0)  # 重置文件指针
                    df = pd.read_csv(uploaded_file, encoding=encoding)
                    st.success(f"✅ {tr('data_viewer.file_loaded_success')} (编码: {encoding})")
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    st.error(f"❌ {tr('data_viewer.file_load_error')}: {str(e)}")
                    break
            
            if df is None:
                st.error(f"❌ {tr('data_viewer.encoding_error')}")
                st.stop()
                
        else:
            # Excel文件处理
            df = pd.read_excel(uploaded_file)
            st.success(f"✅ {tr('data_viewer.file_loaded_success')}")
        
        # 存储数据到会话状态
        st.session_state.uploaded_data = df
        st.session_state.available_columns = list(df.columns)
        
        # 如果是新文件，重置选择的列
        if 'last_file_name' not in st.session_state or st.session_state.last_file_name != uploaded_file.name:
            st.session_state.selected_columns = []
            st.session_state.last_file_name = uploaded_file.name
        
        # 显示文件信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(tr('data_viewer.total_rows'), len(df))
        with col2:
            st.metric(tr('data_viewer.total_columns'), len(df.columns))
        with col3:
            st.metric(tr('data_viewer.file_size'), f"{uploaded_file.size / 1024:.1f} KB")
            
    except Exception as e:
        st.error(f"❌ {tr('data_viewer.file_load_error')}: {str(e)}")
        st.stop()

# 列选择器
if st.session_state.uploaded_data is not None:
    st.subheader(f"🔧 {tr('data_viewer.column_selector')}")
    
    # 创建双选择框布局
    col_left, col_middle, col_right = st.columns([2, 1, 2])
    
    with col_left:
        st.markdown(f"**{tr('data_viewer.available_columns')}**")
        
        # 可用列列表
        available_for_selection = [
            col for col in st.session_state.available_columns 
            if col not in st.session_state.selected_columns
        ]
        
        selected_to_add = st.multiselect(
            tr('data_viewer.select_columns_to_add'),
            available_for_selection,
            key="columns_to_add"
        )
    
    with col_middle:
        st.markdown("<br>", unsafe_allow_html=True)  # 添加间距
        
        # 添加按钮
        if st.button("➡️ " + tr('data_viewer.add_columns'), use_container_width=True):
            if selected_to_add:
                st.session_state.selected_columns.extend(selected_to_add)
                st.rerun()
        
        # 移除按钮
        if st.button("⬅️ " + tr('data_viewer.remove_columns'), use_container_width=True):
            if 'columns_to_remove' in st.session_state and st.session_state.columns_to_remove:
                for col in st.session_state.columns_to_remove:
                    if col in st.session_state.selected_columns:
                        st.session_state.selected_columns.remove(col)
                st.rerun()
        
        # 全选按钮
        if st.button("➡️ " + tr('data_viewer.select_all'), use_container_width=True):
            st.session_state.selected_columns = st.session_state.available_columns.copy()
            st.rerun()
        
        # 清空按钮
        if st.button("⬅️ " + tr('data_viewer.clear_all'), use_container_width=True):
            st.session_state.selected_columns = []
            st.rerun()
    
    with col_right:
        st.markdown(f"**{tr('data_viewer.selected_columns')}**")
        
        # 已选择列列表
        selected_to_remove = st.multiselect(
            tr('data_viewer.select_columns_to_remove'),
            st.session_state.selected_columns,
            key="columns_to_remove"
        )
    
    # 显示选择的列数量
    st.info(f"📊 {tr('data_viewer.selected_count')}: {len(st.session_state.selected_columns)} / {len(st.session_state.available_columns)}")

# 数据预览
if st.session_state.uploaded_data is not None and st.session_state.selected_columns:
    st.subheader(f"👀 {tr('data_viewer.data_preview')}")
    
    # 过滤选项
    col1, col2 = st.columns(2)
    with col1:
        show_rows = st.slider(
            tr('data_viewer.preview_rows'),
            min_value=5,
            max_value=min(100, len(st.session_state.uploaded_data)),
            value=min(20, len(st.session_state.uploaded_data))
        )
    
    with col2:
        start_row = st.number_input(
            tr('data_viewer.start_row'),
            min_value=0,
            max_value=max(0, len(st.session_state.uploaded_data) - 1),
            value=0
        )
    
    # 显示选择的数据
    try:
        filtered_df = st.session_state.uploaded_data[st.session_state.selected_columns]
        preview_df = filtered_df.iloc[start_row:start_row + show_rows]
        
        st.dataframe(
            preview_df.astype(str),
            use_container_width=True,
            height=400
        )
        
        # 数据统计信息
        if st.checkbox(tr('data_viewer.show_statistics')):
            st.subheader(f"📈 {tr('data_viewer.statistics')}")
            
            # 数值列统计
            numeric_cols = filtered_df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                st.markdown(f"**{tr('data_viewer.numeric_statistics')}**")
                st.dataframe(filtered_df[numeric_cols].describe(), use_container_width=True)
            
            # 文本列统计
            text_cols = filtered_df.select_dtypes(include=['object']).columns
            if len(text_cols) > 0:
                st.markdown(f"**{tr('data_viewer.text_statistics')}**")
                text_stats = []
                for col in text_cols:
                    stats = {
                        tr('data_viewer.column'): col,
                        tr('data_viewer.unique_values'): filtered_df[col].nunique(),
                        tr('data_viewer.null_values'): filtered_df[col].isnull().sum(),
                        tr('data_viewer.most_common'): filtered_df[col].mode().iloc[0] if not filtered_df[col].mode().empty else 'N/A'
                    }
                    text_stats.append(stats)
                st.dataframe(pd.DataFrame(text_stats), use_container_width=True)
        
        # 导出功能
        st.subheader(f"💾 {tr('data_viewer.export_section')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 导出为CSV
            csv_data = filtered_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                f"📄 {tr('data_viewer.export_csv')}",
                csv_data,
                f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv",
                use_container_width=True
            )
        
        with col2:
            # 导出为Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, index=False, sheet_name='Filtered Data')
            excel_data = output.getvalue()
            
            st.download_button(
                f"📊 {tr('data_viewer.export_excel')}",
                excel_data,
                f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
    except Exception as e:
        st.error(f"❌ {tr('data_viewer.preview_error')}: {str(e)}")

elif st.session_state.uploaded_data is not None:
    st.info(f"💡 {tr('data_viewer.select_columns_hint')}")

else:
    st.info(f"💡 {tr('data_viewer.upload_hint')}")

# 返回主页按钮
st.markdown("---")
if st.button(f"🏠 {tr('data_viewer.back_home')}", use_container_width=True):
    st.switch_page("streamlit_app.py")