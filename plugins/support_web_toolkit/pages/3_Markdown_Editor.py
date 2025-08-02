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

# 初始化markdown内容
if 'markdown_content' not in st.session_state:
    if st.session_state.language == 'zh_CN':
        st.session_state.markdown_content = """# 欢迎使用Markdown编辑器

这是一个功能强大的Markdown编辑器，支持实时预览。

## 功能特性

- ✅ **实时预览**: 边写边看效果
- 📄 **语法高亮**: 清晰的代码显示
- 💾 **文件导出**: 支持MD和HTML格式
- 🎨 **丰富格式**: 支持表格、代码块、链接等

## 示例内容

### 代码块
```python
def hello_world():
    print("Hello, World!")
```

### 表格
| 功能 | 状态 | 说明 |
|------|------|------|
| 编辑 | ✅ | 支持实时编辑 |
| 预览 | ✅ | 实时预览效果 |
| 导出 | ✅ | 多格式导出 |

### 链接和图片
[Markdown语法指南](https://markdown.com.cn/)

> 这是一个引用块，用于突出重要信息。

**开始编辑您的文档吧！**
"""
    else:
        st.session_state.markdown_content = """# Welcome to Markdown Editor

This is a powerful Markdown editor with real-time preview.

## Features

- ✅ **Real-time Preview**: See changes as you type
- 📄 **Syntax Highlighting**: Clear code display
- 💾 **File Export**: Support MD and HTML formats
- 🎨 **Rich Formatting**: Support tables, code blocks, links, etc.

## Sample Content

### Code Block
```python
def hello_world():
    print("Hello, World!")
```

### Table
| Feature | Status | Description |
|---------|--------|-------------|
| Edit | ✅ | Real-time editing |
| Preview | ✅ | Live preview |
| Export | ✅ | Multiple formats |

### Links and Images
[Markdown Guide](https://www.markdownguide.org/)

> This is a blockquote for highlighting important information.

**Start editing your document!**
"""

# 页面标题
if st.session_state.language == 'zh_CN':
    st.title("📝 Markdown编辑器")
    st.markdown("实时预览的Markdown文档编辑器")
else:
    st.title("📝 Markdown Editor")
    st.markdown("Real-time preview Markdown document editor")

# 工具栏
if st.session_state.language == 'zh_CN':
    st.subheader("🛠️ 工具栏")
else:
    st.subheader("🛠️ Toolbar")

tool_col1, tool_col2, tool_col3, tool_col4, tool_col5 = st.columns(5)

with tool_col1:
    if st.session_state.language == 'zh_CN':
        if st.button("📄 新建文档", use_container_width=True):
            st.session_state.markdown_content = "# 新文档\n\n开始编写您的内容..."
            st.rerun()
    else:
        if st.button("📄 New Document", use_container_width=True):
            st.session_state.markdown_content = "# New Document\n\nStart writing your content..."
            st.rerun()

with tool_col2:
    if st.session_state.language == 'zh_CN':
        if st.button("📋 插入表格", use_container_width=True):
            table_template = "\n\n| 列1 | 列2 | 列3 |\n|-----|-----|-----|\n| 行1 | 数据 | 数据 |\n| 行2 | 数据 | 数据 |\n\n"
            st.session_state.markdown_content += table_template
            st.rerun()
    else:
        if st.button("📋 Insert Table", use_container_width=True):
            table_template = "\n\n| Column1 | Column2 | Column3 |\n|---------|---------|---------|\n| Row1 | Data | Data |\n| Row2 | Data | Data |\n\n"
            st.session_state.markdown_content += table_template
            st.rerun()

with tool_col3:
    if st.session_state.language == 'zh_CN':
        if st.button("💻 插入代码", use_container_width=True):
            code_template = "\n\n```python\n# 在这里写代码\nprint('Hello, World!')\n```\n\n"
            st.session_state.markdown_content += code_template
            st.rerun()
    else:
        if st.button("💻 Insert Code", use_container_width=True):
            code_template = "\n\n```python\n# Write your code here\nprint('Hello, World!')\n```\n\n"
            st.session_state.markdown_content += code_template
            st.rerun()

with tool_col4:
    if st.session_state.language == 'zh_CN':
        if st.button("🔗 插入链接", use_container_width=True):
            link_template = "[链接文本](https://example.com)"
            st.session_state.markdown_content += link_template
            st.rerun()
    else:
        if st.button("🔗 Insert Link", use_container_width=True):
            link_template = "[Link Text](https://example.com)"
            st.session_state.markdown_content += link_template
            st.rerun()

with tool_col5:
    if st.session_state.language == 'zh_CN':
        if st.button("📝 插入引用", use_container_width=True):
            quote_template = "\n\n> 这是一个引用块\n> 可以用来突出重要信息\n\n"
            st.session_state.markdown_content += quote_template
            st.rerun()
    else:
        if st.button("📝 Insert Quote", use_container_width=True):
            quote_template = "\n\n> This is a blockquote\n> Used to highlight important information\n\n"
            st.session_state.markdown_content += quote_template
            st.rerun()

st.markdown("---")

# 主编辑区域
col1, col2 = st.columns([1, 1])

with col1:
    if st.session_state.language == 'zh_CN':
        st.subheader("✏️ 编辑区")
        
        # 文件上传
        uploaded_file = st.file_uploader(
            "上传Markdown文件",
            type=['md', 'txt'],
            help="支持.md和.txt格式"
        )
        
        if uploaded_file is not None:
            content = uploaded_file.read().decode('utf-8')
            st.session_state.markdown_content = content
            st.success("文件上传成功！")
            st.rerun()
        
        # 编辑器
        new_content = st.text_area(
            "Markdown内容",
            value=st.session_state.markdown_content,
            height=500,
            help="在此处编写您的Markdown内容"
        )
        
        # 实时更新内容
        if new_content != st.session_state.markdown_content:
            st.session_state.markdown_content = new_content
            
    else:
        st.subheader("✏️ Editor")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload Markdown file",
            type=['md', 'txt'],
            help="Support .md and .txt formats"
        )
        
        if uploaded_file is not None:
            content = uploaded_file.read().decode('utf-8')
            st.session_state.markdown_content = content
            st.success("File uploaded successfully!")
            st.rerun()
        
        # Editor
        new_content = st.text_area(
            "Markdown Content",
            value=st.session_state.markdown_content,
            height=500,
            help="Write your Markdown content here"
        )
        
        # Real-time content update
        if new_content != st.session_state.markdown_content:
            st.session_state.markdown_content = new_content

with col2:
    if st.session_state.language == 'zh_CN':
        st.subheader("👀 实时预览")
    else:
        st.subheader("👀 Live Preview")
    
    # 预览区域
    try:
        # 转换Markdown为HTML
        html_content = markdown.markdown(
            st.session_state.markdown_content,
            extensions=['tables', 'fenced_code', 'toc']
        )
        
        # 显示预览
        st.markdown(st.session_state.markdown_content, unsafe_allow_html=True)
        
    except Exception as e:
        if st.session_state.language == 'zh_CN':
            st.error(f"预览错误: {str(e)}")
        else:
            st.error(f"Preview error: {str(e)}")

# 导出功能
st.markdown("---")
if st.session_state.language == 'zh_CN':
    st.subheader("💾 导出文档")
else:
    st.subheader("💾 Export Document")

export_col1, export_col2, export_col3 = st.columns(3)

with export_col1:
    # 导出Markdown
    if st.session_state.language == 'zh_CN':
        st.download_button(
            "📄 下载Markdown文件",
            st.session_state.markdown_content,
            f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            "text/markdown",
            use_container_width=True
        )
    else:
        st.download_button(
            "📄 Download Markdown",
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
        
        if st.session_state.language == 'zh_CN':
            st.download_button(
                "🌐 下载HTML文件",
                full_html,
                f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                "text/html",
                use_container_width=True
            )
        else:
            st.download_button(
                "🌐 Download HTML",
                full_html,
                f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                "text/html",
                use_container_width=True
            )
    except Exception as e:
        if st.session_state.language == 'zh_CN':
            st.error(f"HTML导出错误: {str(e)}")
        else:
            st.error(f"HTML export error: {str(e)}")

with export_col3:
    # 统计信息
    if st.session_state.language == 'zh_CN':
        if st.button("📊 文档统计", use_container_width=True):
            content = st.session_state.markdown_content
            char_count = len(content)
            word_count = len(content.split())
            line_count = len(content.splitlines())
            
            st.info(f"""
            📊 **文档统计信息**
            - 字符数: {char_count:,}
            - 单词数: {word_count:,}
            - 行数: {line_count:,}
            """)
    else:
        if st.button("📊 Document Stats", use_container_width=True):
            content = st.session_state.markdown_content
            char_count = len(content)
            word_count = len(content.split())
            line_count = len(content.splitlines())
            
            st.info(f"""
            📊 **Document Statistics**
            - Characters: {char_count:,}
            - Words: {word_count:,}
            - Lines: {line_count:,}
            """)

# 使用说明
if st.session_state.language == 'zh_CN':
    with st.expander("📖 Markdown语法帮助"):
        st.markdown("""
        ### 基本语法
        
        ```markdown
        # 一级标题
        ## 二级标题
        ### 三级标题
        
        **粗体文本**
        *斜体文本*
        ~~删除线~~
        
        [链接](https://example.com)
        ![图片](image.jpg)
        
        > 引用块
        
        - 无序列表项
        - 另一个列表项
        
        1. 有序列表项
        2. 另一个列表项
        
        `行内代码`
        
        ```python
        # 代码块
        print("Hello, World!")
        ```
        
        | 表格 | 列1 | 列2 |
        |------|-----|-----|
        | 行1  | 数据 | 数据 |
        ```
        """)
else:
    with st.expander("📖 Markdown Syntax Help"):
        st.markdown("""
        ### Basic Syntax
        
        ```markdown
        # Heading 1
        ## Heading 2
        ### Heading 3
        
        **Bold text**
        *Italic text*
        ~~Strikethrough~~
        
        [Link](https://example.com)
        ![Image](image.jpg)
        
        > Blockquote
        
        - Unordered list item
        - Another list item
        
        1. Ordered list item
        2. Another list item
        
        `Inline code`
        
        ```python
        # Code block
        print("Hello, World!")
        ```
        
        | Table | Col1 | Col2 |
        |-------|------|------|
        | Row1  | Data | Data |
        ```
        """)

# 返回主页按钮
st.markdown("---")
if st.session_state.language == 'zh_CN':
    if st.button("🏠 返回主页", use_container_width=True):
        st.switch_page("streamlit_app.py")
else:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("streamlit_app.py")