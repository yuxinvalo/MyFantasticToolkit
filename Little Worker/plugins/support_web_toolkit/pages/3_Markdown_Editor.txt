# -*- coding: utf-8 -*-
"""
Markdown编辑器页面
"""

import streamlit as st
import json
from pathlib import Path
import markdown
from datetime import datetime
from common import tr, init_language, apply_button_styles

# 页面配置
st.set_page_config(
    page_title="Markdown Editor - IT Support Toolkit",
    page_icon="📝",
    layout="wide"
)

# 初始化语言设置
init_language()

# 应用通用按钮样式
apply_button_styles()

# 初始化session state
if 'markdown_content' not in st.session_state:
    st.session_state.markdown_content = tr('markdown_editor.default_markdown_content')

# 页面标题
st.title(f"📝 {tr('markdown_editor.title')}")
st.markdown(tr('markdown_editor.description'))

# 工具栏
st.subheader(f"🛠️ {tr('markdown_editor.toolbar')}")

tool_col1, tool_col2, tool_col3, tool_col4, tool_col5 = st.columns(5)

with tool_col1:
    if st.button(f"📄 {tr('markdown_editor.new_document')}", use_container_width=True):
        new_content = tr('markdown_editor.new_document_template')
        st.session_state.markdown_content = new_content
        st.session_state.editor_content = new_content

with tool_col2:
    if st.button(f"📋 {tr('markdown_editor.insert_table')}", use_container_width=True):
        table_template = tr('markdown_editor.table_template')
        new_content = st.session_state.markdown_content + table_template
        st.session_state.markdown_content = new_content
        st.session_state.editor_content = new_content

with tool_col3:
    if st.button(f"💻 {tr('markdown_editor.insert_code')}", use_container_width=True):
        code_template = tr('markdown_editor.code_template')
        new_content = st.session_state.markdown_content + code_template
        st.session_state.markdown_content = new_content
        st.session_state.editor_content = new_content

with tool_col4:
    if st.button(f"🔗 {tr('markdown_editor.insert_link')}", use_container_width=True):
        link_template = tr('markdown_editor.link_template')
        new_content = st.session_state.markdown_content + link_template
        st.session_state.markdown_content = new_content
        st.session_state.editor_content = new_content

with tool_col5:
    if st.button(f"📝 {tr('markdown_editor.insert_quote')}", use_container_width=True):
        quote_template = tr('markdown_editor.quote_template')
        new_content = st.session_state.markdown_content + quote_template
        st.session_state.markdown_content = new_content
        st.session_state.editor_content = new_content

# 使用说明
with st.expander(f"📖 {tr('markdown_editor.markdown_syntax_help')}"):
    st.markdown(tr('markdown_editor.markdown_syntax_content'))

st.markdown("---")

# 主编辑区域
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(f"✏️ {tr('markdown_editor.editor')}")
    
    # 文件上传
    uploaded_file = st.file_uploader(
        tr('markdown_editor.upload_markdown_file'),
        type=['md', 'txt'],
        help=tr('markdown_editor.upload_file_help')
    )
    
    if uploaded_file is not None:
        content = uploaded_file.read().decode('utf-8')
        st.session_state.markdown_content = content
        st.session_state.editor_content = content
    
    # 编辑器 - 使用session_state直接管理状态
    if 'editor_content' not in st.session_state:
        st.session_state.editor_content = st.session_state.markdown_content
    
    # 同步编辑器内容到主内容
    st.session_state.markdown_content = st.session_state.editor_content
    
    st.text_area(
        tr('markdown_editor.markdown_content'),
        height=700,
        help=tr('markdown_editor.markdown_content_help'),
        key="editor_content"
    )

with col2:
    st.subheader(f"👀 {tr('markdown_editor.live_preview')}")
    
    # 预览区域 - 添加滚动容器
    try:
        # 转换Markdown为HTML
        html_content = markdown.markdown(
            st.session_state.markdown_content,
            extensions=['tables', 'fenced_code', 'toc']
        )
        
        # 创建滚动容器
        st.markdown(
            f"""
            <div style="height: 820px; overflow-y: auto; border: 1px solid #ddd; padding: 15px; border-radius: 5px; background-color: white;">
                {html_content}
            </div>
            """,
            unsafe_allow_html=True
        )
        
    except Exception as e:
        st.error(f"{tr('markdown_editor.preview_error')}: {str(e)}")

# 导出功能
st.markdown("---")
st.subheader(f"💾 {tr('markdown_editor.export_document')}")

export_col1, export_col2, export_col3 = st.columns(3)

with export_col1:
    # 导出Markdown
    st.download_button(
        f"📄 {tr('markdown_editor.download_markdown')}",
        st.session_state.markdown_content,
        f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        "text/markdown",
        use_container_width=True
    )

with export_col2:
    # 导出HTML
    try:
        html_content = markdown.markdown(
            st.session_state.markdown_content,
            extensions=['tables', 'fenced_code', 'toc']
        )
        
        # 完整的HTML文档
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Markdown Document</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
        pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        blockquote {{ border-left: 4px solid #ddd; margin: 0; padding-left: 20px; color: #666; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
        
        st.download_button(
            f"🌐 {tr('markdown_editor.download_html')}",
            full_html,
            f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            "text/html",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"{tr('markdown_editor.html_export_error')}: {str(e)}")

@st.dialog(tr('markdown_editor.save_as'))
def save_as_dialog():
    st.markdown(f"**{tr('markdown_editor.save_as_help')}**")
    
    filename = st.text_input(
        tr('markdown_editor.filename_input'),
        placeholder=tr('markdown_editor.filename_placeholder'),
        key="save_as_filename"
    )
    
    if filename:
        # 确保文件名安全
        import re
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        st.markdown("---")
        st.markdown(f"**{tr('markdown_editor.export_document')}**")
        
        col_md, col_html = st.columns(2)
        
        with col_md:
            st.download_button(
                f"📄 {tr('markdown_editor.download_markdown')}",
                st.session_state.markdown_content,
                f"{safe_filename}.md",
                "text/markdown",
                use_container_width=True
            )
        
        with col_html:
            try:
                html_content = markdown.markdown(
                    st.session_state.markdown_content,
                    extensions=['tables', 'fenced_code', 'toc']
                )
                
                full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{safe_filename}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
        pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        blockquote {{ border-left: 4px solid #ddd; margin: 0; padding-left: 20px; color: #666; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
                
                st.download_button(
                    f"🌐 {tr('markdown_editor.download_html')}",
                    full_html,
                    f"{safe_filename}.html",
                    "text/html",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"{tr('markdown_editor.html_export_error')}: {str(e)}")
    else:
        st.info(tr('markdown_editor.filename_placeholder'))

with export_col3:
    # 另存为功能 - 使用download_button样式但触发模态对话框
    if st.download_button(
        f"💾 {tr('markdown_editor.save_as')}",
        data="",  # 空数据，实际不下载
        file_name="temp.txt",
        mime="text/plain",
        use_container_width=True,
        on_click=save_as_dialog
    ):
        pass  # download_button的点击已经通过on_click处理

# 返回主页按钮
st.markdown("---")
if st.button(f"🏠 {tr('markdown_editor.back_to_home')}", use_container_width=True):
    st.switch_page("streamlit_app.py")