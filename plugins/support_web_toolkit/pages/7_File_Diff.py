# -*- coding: utf-8 -*-
"""
文件对比工具页面
"""

import streamlit as st
import difflib
from pathlib import Path
from datetime import datetime
from common import load_config, load_translations, tr, init_language, save_config, apply_button_styles

# 页面配置
st.set_page_config(
    page_title="File Diff - IT Support Toolkit",
    page_icon="📄",
    layout="wide"
)

# 初始化语言设置
init_language()

# 应用通用按钮样式
apply_button_styles()

# 初始化会话状态
if 'file1_content' not in st.session_state:
    st.session_state.file1_content = ""
if 'file2_content' not in st.session_state:
    st.session_state.file2_content = ""
if 'file1_name' not in st.session_state:
    st.session_state.file1_name = "File 1"
if 'file2_name' not in st.session_state:
    st.session_state.file2_name = "File 2"
if 'diff_result' not in st.session_state:
    st.session_state.diff_result = None
if 'show_line_numbers' not in st.session_state:
    st.session_state.show_line_numbers = True
if 'ignore_whitespace' not in st.session_state:
    st.session_state.ignore_whitespace = False

# 页面标题
st.title(f"📄 {tr('file_diff.title')}")
st.markdown(f"**{tr('file_diff.description')}**")

# 文件上传区域
st.subheader(f"📁 {tr('file_diff.upload_section')}")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"**{tr('file_diff.file1_label')}**")
    uploaded_file1 = st.file_uploader(
        tr('file_diff.upload_file1'),
        type=['txt', 'py', 'js', 'html', 'css', 'json', 'xml', 'csv', 'md', 'log'],
        key="file1",
        help=tr('file_diff.upload_help')
    )
    
    if uploaded_file1 is not None:
        try:
            # 尝试不同编码读取文件
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            content = None
            
            for encoding in encodings:
                try:
                    uploaded_file1.seek(0)
                    content = uploaded_file1.read().decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is not None:
                st.session_state.file1_content = content
                st.session_state.file1_name = uploaded_file1.name
                st.success(f"✅ {tr('file_diff.file_loaded')}: {uploaded_file1.name}")
            else:
                st.error(f"❌ {tr('file_diff.encoding_error')}")
                
        except Exception as e:
            st.error(f"❌ {tr('file_diff.file_load_error')}: {str(e)}")

with col2:
    st.markdown(f"**{tr('file_diff.file2_label')}**")
    uploaded_file2 = st.file_uploader(
        tr('file_diff.upload_file2'),
        type=['txt', 'py', 'js', 'html', 'css', 'json', 'xml', 'csv', 'md', 'log'],
        key="file2",
        help=tr('file_diff.upload_help')
    )
    
    if uploaded_file2 is not None:
        try:
            # 尝试不同编码读取文件
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            content = None
            
            for encoding in encodings:
                try:
                    uploaded_file2.seek(0)
                    content = uploaded_file2.read().decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is not None:
                st.session_state.file2_content = content
                st.session_state.file2_name = uploaded_file2.name
                st.success(f"✅ {tr('file_diff.file_loaded')}: {uploaded_file2.name}")
            else:
                st.error(f"❌ {tr('file_diff.encoding_error')}")
                
        except Exception as e:
            st.error(f"❌ {tr('file_diff.file_load_error')}: {str(e)}")

# 文件内容编辑区域
if st.session_state.file1_content or st.session_state.file2_content:
    st.subheader(f"✏️ {tr('file_diff.edit_section')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**{tr('file_diff.edit_file1')}: {st.session_state.file1_name}**")
        new_content1 = st.text_area(
            tr('file_diff.content_label'),
            value=st.session_state.file1_content,
            height=300,
            key="edit_file1",
            help=tr('file_diff.edit_help')
        )
        
        if new_content1 != st.session_state.file1_content:
            st.session_state.file1_content = new_content1
            st.session_state.diff_result = None  # 清除之前的对比结果
    
    with col2:
        st.markdown(f"**{tr('file_diff.edit_file2')}: {st.session_state.file2_name}**")
        new_content2 = st.text_area(
            tr('file_diff.content_label'),
            value=st.session_state.file2_content,
            height=300,
            key="edit_file2",
            help=tr('file_diff.edit_help')
        )
        
        if new_content2 != st.session_state.file2_content:
            st.session_state.file2_content = new_content2
            st.session_state.diff_result = None  # 清除之前的对比结果

# 对比选项
if st.session_state.file1_content and st.session_state.file2_content:
    st.subheader(f"⚙️ {tr('file_diff.options_section')}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.session_state.show_line_numbers = st.checkbox(
            tr('file_diff.show_line_numbers'),
            value=st.session_state.show_line_numbers
        )
    
    with col2:
        st.session_state.ignore_whitespace = st.checkbox(
            tr('file_diff.ignore_whitespace'),
            value=st.session_state.ignore_whitespace
        )
    
    with col3:
        if st.button(f"🔍 {tr('file_diff.compare_files')}", use_container_width=True):
            # 执行文件对比
            content1 = st.session_state.file1_content
            content2 = st.session_state.file2_content
            
            if st.session_state.ignore_whitespace:
                # 忽略空白字符
                content1 = '\n'.join(line.strip() for line in content1.splitlines())
                content2 = '\n'.join(line.strip() for line in content2.splitlines())
            
            lines1 = content1.splitlines(keepends=True)
            lines2 = content2.splitlines(keepends=True)
            
            # 生成HTML格式的对比结果
            differ = difflib.HtmlDiff()
            st.session_state.diff_result = differ.make_file(
                lines1, lines2,
                fromdesc=st.session_state.file1_name,
                todesc=st.session_state.file2_name,
                context=True,
                numlines=3
            )

# 显示对比结果
if st.session_state.diff_result:
    st.subheader(f"📊 {tr('file_diff.result_section')}")
    
    # 统计信息
    content1_lines = len(st.session_state.file1_content.splitlines())
    content2_lines = len(st.session_state.file2_content.splitlines())
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"{st.session_state.file1_name} {tr('file_diff.lines')}", content1_lines)
    with col2:
        st.metric(f"{st.session_state.file2_name} {tr('file_diff.lines')}", content2_lines)
    with col3:
        line_diff = abs(content1_lines - content2_lines)
        st.metric(tr('file_diff.line_difference'), line_diff)
    
    # 显示HTML对比结果
    st.components.v1.html(st.session_state.diff_result, height=600, scrolling=True)
    
    # 导出选项
    st.subheader(f"💾 {tr('file_diff.export_section')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 导出HTML格式的对比结果
        st.download_button(
            f"📄 {tr('file_diff.export_html')}",
            st.session_state.diff_result,
            f"file_diff_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            "text/html",
            use_container_width=True
        )
    
    with col2:
        # 生成文本格式的对比结果
        lines1 = st.session_state.file1_content.splitlines(keepends=True)
        lines2 = st.session_state.file2_content.splitlines(keepends=True)
        
        text_diff = '\n'.join(difflib.unified_diff(
            lines1, lines2,
            fromfile=st.session_state.file1_name,
            tofile=st.session_state.file2_name,
            lineterm=''
        ))
        
        st.download_button(
            f"📝 {tr('file_diff.export_text')}",
            text_diff,
            f"file_diff_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "text/plain",
            use_container_width=True
        )

# 提示信息
if not st.session_state.file1_content and not st.session_state.file2_content:
    st.info(f"💡 {tr('file_diff.upload_hint')}")
elif not st.session_state.file1_content or not st.session_state.file2_content:
    st.info(f"💡 {tr('file_diff.upload_both_hint')}")

# 返回主页按钮
st.markdown("---")
if st.button(f"🏠 {tr('file_diff.back_home')}", use_container_width=True):
    st.switch_page("streamlit_app.py")