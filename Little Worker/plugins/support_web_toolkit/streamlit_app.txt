# -*- coding: utf-8 -*-
"""
HSBC Little Worker - Support Web Toolkit Streamlit App
IT支持Web工具包主页
"""

import streamlit as st
from common import load_config, load_translations, tr, init_language, update_language_config, apply_button_styles

# 配置页面
st.set_page_config(
    page_title="IT Support Web Toolkit",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 多语言支持
init_language()

# 应用通用按钮样式
apply_button_styles()

# 语言切换
with st.sidebar:
    st.title(f"🛠️ {tr('app.sidebar.title')}")
    
    # 语言选择
    language_options = {
        "中文": "zh_CN",
        "English": "en_US"
    }
    
    selected_lang = st.selectbox(
        tr("app.sidebar.language"),
        options=list(language_options.keys()),
        index=0 if st.session_state.language == 'zh_CN' else 1
    )
    
    if language_options[selected_lang] != st.session_state.language:
        new_language = language_options[selected_lang]
        st.session_state.language = new_language
        # 保存语言设置到配置文件
        update_language_config(new_language)
        st.rerun()
    
    st.divider()
    
    # 工具导航
    st.markdown(f"### 🔧 {tr('app.sidebar.tools')}")
    st.page_link("pages/1_JSON_Formatter.py", label=f"📄 {tr('plugin.web_toolkit.json_formatter')}")
    st.page_link("pages/2_Timezone_Converter.py", label=f"⏰ {tr('plugin.web_toolkit.timezone_converter')}")
    st.page_link("pages/3_Markdown_Editor.py", label=f"📝 {tr('plugin.web_toolkit.markdown_editor')}")
    st.page_link("pages/4_Todo_List.py", label=f"📋 {tr('plugin.web_toolkit.todo_list')}")
    st.page_link("pages/5_Data_Viewer.py", label=f"📊 {tr('plugin.web_toolkit.data_viewer')}")
    st.page_link("pages/6_Libre_CMD.py", label=f"💻 {tr('plugin.web_toolkit.libre_cmd')}")

# 主页内容
st.title(f"🛠️ {tr('app.title')}")

# Quick Links
st.markdown("---")

st.subheader(f"🔗 {tr('app.quick_links')}")

# 加载配置文件
config = load_config()
quick_links = config.get('quick_links', {})
if quick_links:
    # 将quick_links按每行最多3列显示
    link_categories = list(quick_links.items())
    
    # 每3个分类为一行
    for i in range(0, len(link_categories), 3):
        cols = st.columns(3)
        
        for j, (category, links) in enumerate(link_categories[i:i+3]):
            with cols[j]:
                with st.container(border=True):
                    st.markdown(f"**📂 {category}**")
                    st.markdown("---")
                    for link in links:
                        st.markdown(f"🔗 [{link['name']}]({link['url']})")
else:
    st.info("No quick links configured.")

# 技术支持
st.markdown("---")
st.subheader(f"📞 {tr('app.technical_support')}")
st.markdown(tr('app.technical_support_content'))

# 页脚
st.markdown("---")
st.caption(f"🏦 {tr('app.footer')}")