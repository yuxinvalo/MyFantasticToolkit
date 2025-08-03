# -*- coding: utf-8 -*-
"""
Markdown编辑器页面
"""

import streamlit as st
import json
from pathlib import Path
import markdown
from datetime import datetime
from common import load_config, load_translations, tr, init_language, apply_button_styles

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
    st.session_state.markdown_content = tr('default_markdown_content')

# 页面标题
st.title(f"📝 {tr('markdown_editor')}")
st.markdown(tr('markdown_editor_description'))

# 工具栏
st.subheader(f"🛠️ {tr('toolbar')}")

tool_col1, tool_col2, tool_col3, tool_col4, tool_col5 = st.columns(5)

with tool_col1:
    if st.button(f"📄 {tr('new_document')}", use_container_width=True):
        st.session_state.markdown_content = tr('new_document_template')
        st.rerun()

with tool_col2:
    if st.button(f"📋 {tr('insert_table')}", use_container_width=True):
        table_template = tr('table_template')
        st.session_state.markdown_content += table_template
        st.rerun()

with tool_col3:
    if st.button(f"💻 {tr('insert_code')}", use_container_width=True):
        code_template = tr('code_template')
        st.session_state.markdown_content += code_template
        st.rerun()

with tool_col4:
    if st.button(f"🔗 {tr('insert_link')}", use_container_width=True):
        link_template = tr('link_template')
        st.session_state.markdown_content += link_template
        st.rerun()

with tool_col5:
    if st.button(f"📝 {tr('insert_quote')}", use_container_width=True):
        quote_template = tr('quote_template')
        st.session_state.markdown_content += quote_template
        st.rerun()

# 使用说明
with st.expander(f"📖 {tr('markdown_syntax_help')}"):
    st.markdown(tr('markdown_syntax_content'))

st.markdown("---")

# 主编辑区域
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader(f"✏️ {tr('editor')}")
    
    # 文件上传
    uploaded_file = st.file_uploader(
        tr('upload_markdown_file'),
        type=['md', 'txt'],
        help=tr('upload_file_help')
    )
    
    if uploaded_file is not None:
        content = uploaded_file.read().decode('utf-8')
        st.session_state.markdown_content = content
    
    # 编辑器
    new_content = st.text_area(
        tr('markdown_content'),
        value=st.session_state.markdown_content,
        height=700,
        help=tr('markdown_content_help')
    )
    
    # 实时更新内容
    if new_content != st.session_state.markdown_content:
        st.session_state.markdown_content = new_content

with col2:
    st.subheader(f"👀 {tr('live_preview')}")
    
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
        st.error(f"{tr('preview_error')}: {str(e)}")

# 导出功能
st.markdown("---")
st.subheader(f"💾 {tr('export_document')}")

export_col1, export_col2, export_col3 = st.columns(3)

with export_col1:
    # 导出Markdown
    st.download_button(
        f"📄 {tr('download_markdown')}",
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
            f"🌐 {tr('download_html')}",
            full_html,
            f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            "text/html",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"{tr('html_export_error')}: {str(e)}")

@st.dialog(tr('save_as'))
def save_as_dialog():
    st.markdown(f"**{tr('save_as_help')}**")
    
    filename = st.text_input(
        tr('filename_input'),
        placeholder=tr('filename_placeholder'),
        key="save_as_filename"
    )
    
    if filename:
        # 确保文件名安全
        import re
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        st.markdown("---")
        st.markdown(f"**{tr('export_document')}**")
        
        col_md, col_html = st.columns(2)
        
        with col_md:
            st.download_button(
                f"📄 {tr('download_markdown')}",
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
                    f"🌐 {tr('download_html')}",
                    full_html,
                    f"{safe_filename}.html",
                    "text/html",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"{tr('html_export_error')}: {str(e)}")
    else:
        st.info(tr('filename_placeholder'))

with export_col3:
    # 另存为功能 - 使用download_button样式但触发模态对话框
    if st.download_button(
        f"💾 {tr('save_as')}",
        data="",  # 空数据，实际不下载
        file_name="temp.txt",
        mime="text/plain",
        use_container_width=True,
        on_click=save_as_dialog
    ):
        pass  # download_button的点击已经通过on_click处理

# 返回主页按钮
st.markdown("---")
if st.button(f"🏠 {tr('back_to_home')}", use_container_width=True):
    st.switch_page("streamlit_app.py")