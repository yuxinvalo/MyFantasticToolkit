# -*- coding: utf-8 -*-
"""
JSON格式化工具页面
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from common import load_config, load_translations, tr, init_language, save_config

# 页面配置
st.set_page_config(
    page_title="JSON Formatter - IT Support Toolkit",
    page_icon="📄",
    layout="wide"
)

# 初始化语言设置
init_language()

# 初始化暂存状态
if 'stored_jsons' not in st.session_state:
    st.session_state.stored_jsons = {}  # 字典存储多个结果
if 'stored_expanded_states' not in st.session_state:
    st.session_state.stored_expanded_states = {}  # 每个结果的展开状态
if 'editing_quick_links' not in st.session_state:
    st.session_state.editing_quick_links = False
if 'temp_quick_links' not in st.session_state:
    st.session_state.temp_quick_links = {}

# 页面标题
st.title(f"📄 {tr('json_formatter.title')}")

# Quick Links编辑功能
if not st.session_state.editing_quick_links:
    if st.button(f"⚙️ {tr('json_formatter.edit_quick_links')}", use_container_width=True):
        config = load_config()
        st.session_state.temp_quick_links = config.get('quick_links', {}).copy()
        st.session_state.editing_quick_links = True
        st.rerun()
else:
    st.subheader(f"⚙️ {tr('json_formatter.editing_quick_links')}")
    
    # 编辑界面
    categories = list(st.session_state.temp_quick_links.keys())
    
    # 添加新分类
    with st.expander(f"➕ {tr('json_formatter.add_category')}"):
        new_category = st.text_input(tr('json_formatter.category_name'))
        if st.button(tr('json_formatter.add_category_btn')) and new_category:
            if new_category not in st.session_state.temp_quick_links:
                st.session_state.temp_quick_links[new_category] = []
                st.success(f"✅ {tr('json_formatter.category_added')}: {new_category}")
                st.rerun()
            else:
                st.error(f"❌ {tr('json_formatter.category_exists')}")
    
    # 编辑现有分类
    for category in categories:
        with st.expander(f"📂 {category}", expanded=True):
            links = st.session_state.temp_quick_links[category]
            
            # 显示现有链接
            for i, link in enumerate(links):
                col1, col2, col3 = st.columns([2, 3, 1])
                with col1:
                    new_name = st.text_input(f"Name", value=link['name'], key=f"name_{category}_{i}")
                with col2:
                    new_url = st.text_input(f"URL", value=link['url'], key=f"url_{category}_{i}")
                with col3:
                    if st.button("🗑️", key=f"del_{category}_{i}", help="Delete link"):
                        st.session_state.temp_quick_links[category].pop(i)
                        st.rerun()
                
                # 更新链接
                st.session_state.temp_quick_links[category][i] = {'name': new_name, 'url': new_url}
            
            # 添加新链接
            st.markdown("**Add New Link:**")
            col1, col2, col3 = st.columns([2, 3, 1])
            with col1:
                link_name = st.text_input("Link Name", key=f"new_name_{category}")
            with col2:
                link_url = st.text_input("Link URL", key=f"new_url_{category}")
            with col3:
                if st.button("➕", key=f"add_{category}", help="Add link"):
                    if link_name and link_url:
                        st.session_state.temp_quick_links[category].append({'name': link_name, 'url': link_url})
                        st.rerun()
            
            # 删除分类
            if st.button(f"🗑️ {tr('json_formatter.delete_category')}", key=f"del_cat_{category}"):
                del st.session_state.temp_quick_links[category]
                st.rerun()
    
    # 保存和取消按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"💾 {tr('json_formatter.save_changes')}", use_container_width=True):
            config = load_config()
            config['quick_links'] = st.session_state.temp_quick_links
            if save_config(config):
                st.success(f"✅ {tr('json_formatter.changes_saved')}")
                st.session_state.editing_quick_links = False
                st.rerun()
            else:
                st.error(f"❌ {tr('json_formatter.save_failed')}")
    
    with col2:
        if st.button(f"❌ {tr('json_formatter.cancel_changes')}", use_container_width=True):
            st.session_state.editing_quick_links = False
            st.session_state.temp_quick_links = {}
            st.rerun()
    
    st.markdown("---")

# 主要功能区域
col1, col2 = st.columns([1, 1])

with col1:
    
    # 根据语言设置不同的占位符
    placeholder_text = '{\n  "name": "示例",\n  "value": 123,\n  "items": [1, 2, 3]\n}' if st.session_state.language == 'zh_CN' else '{\n  "name": "example",\n  "value": 123,\n  "items": [1, 2, 3]\n}'
    
    json_input = st.text_area(
        tr('json_formatter.input_placeholder'),
        height=400,
        placeholder=placeholder_text,
        help=tr('json_formatter.input_help')
    )
    
    # 格式化选项
    st.subheader(f"⚙️ {tr('json_formatter.options_section')}")
    indent_size = st.slider(tr('json_formatter.indent_size'), min_value=1, max_value=8, value=2)
     # JSON展示选项
    st.subheader(f"🌳 {tr('json_formatter.display_options')}")
    expanded_level = st.slider(tr('json_formatter.expanded_level'), min_value=1, max_value=10, value=2, help=tr('json_formatter.expanded_level_help'))
    sort_keys = st.checkbox(tr('json_formatter.sort_keys'), value=False)
    ensure_ascii = st.checkbox(tr('json_formatter.ensure_ascii'), value=False)
    
with col2:
    st.text(f"✨ {tr('json_formatter.result_section')}")
    
    # 创建可滚动的容器
    with st.container(height=400):
        # 实时处理JSON格式化
        if json_input.strip():
            try:
                # 解析JSON
                parsed_json = json.loads(json_input)
                
                # 应用排序选项
                if sort_keys:
                    # 递归排序所有层级的键
                    def sort_dict_keys(obj):
                        if isinstance(obj, dict):
                            return {k: sort_dict_keys(v) for k, v in sorted(obj.items())}
                        elif isinstance(obj, list):
                            return [sort_dict_keys(item) for item in obj]
                        else:
                            return obj
                    parsed_json = sort_dict_keys(parsed_json)
                
                # 显示可展开/折叠的JSON
                st.json(parsed_json, expanded=expanded_level)
                     
            except json.JSONDecodeError as e:
                st.error(f"❌ {tr('json_formatter.error_format')}: {str(e)}")
                st.info(f"💡 {tr('json_formatter.syntax_help')}")
            except Exception as e:
                st.error(f"❌ {tr('json_formatter.error_processing')}: {str(e)}")
        
        else:
            # 显示示例
            st.info(f"💡 {tr('json_formatter.input_instruction')}")
    
    # 下载按钮和暂存按钮放在容器外面
    if json_input.strip():
        try:
            parsed_json = json.loads(json_input)
            
            # 应用排序选项用于下载
            if sort_keys:
                def sort_dict_keys(obj):
                    if isinstance(obj, dict):
                        return {k: sort_dict_keys(v) for k, v in sorted(obj.items())}
                    elif isinstance(obj, list):
                        return [sort_dict_keys(item) for item in obj]
                    else:
                        return obj
                parsed_json = sort_dict_keys(parsed_json)
            
            # 格式化JSON用于下载
            formatted_json = json.dumps(
                parsed_json,
                indent=indent_size,
                sort_keys=sort_keys,
                ensure_ascii=ensure_ascii
            )
            
            # 按钮行
            col_download, col_store = st.columns(2)
            
            with col_download:
                # 下载按钮
                st.download_button(
                    f"💾 {tr('json_formatter.download_button')}",
                    formatted_json,
                    "formatted.json",
                    "application/json",
                    use_container_width=True
                )
            
            with col_store:
                # 暂存按钮
                if st.button(f"📌 {tr('json_formatter.store_result')}", use_container_width=True):
                    # 生成时间戳命名
                    timestamp = datetime.now().strftime("%Y%m%d %H:%M:%S")
                    key = f"json_{timestamp}"
                    st.session_state.stored_jsons[key] = parsed_json
                    st.session_state.stored_expanded_states[key] = False
                    st.success(f"✅ {tr('json_formatter.stored_success')}: {key}")
                    st.rerun()
        except:
            pass  # 如果JSON无效，不显示按钮
    
    # 显示暂存的JSON结果
    if st.session_state.stored_jsons:
        # st.markdown("---")
        st.subheader(f"📌 {tr('json_formatter.stored_results')}")
        
        # 清除所有暂存按钮
        if st.button(f"🗑️ {tr('json_formatter.clear_all_stored')}", key="clear_all_stored"):
            st.session_state.stored_jsons = {}
            st.session_state.stored_expanded_states = {}
            st.rerun()
        
        # 显示每个暂存的结果
        for key in sorted(st.session_state.stored_jsons.keys(), reverse=True):  # 最新的在前
            stored_json = st.session_state.stored_jsons[key]
            is_expanded = st.session_state.stored_expanded_states.get(key, False)
            
            # 每个暂存结果的标题和控制按钮
            col_title, col_toggle, col_delete = st.columns([2, 1, 1])
            
            with col_title:
                st.write(f"**{key}**")
            
            with col_toggle:
                toggle_text = tr('json_formatter.collapse') if is_expanded else tr('json_formatter.expand')
                if st.button(f"{toggle_text}", key=f"toggle_{key}"):
                    st.session_state.stored_expanded_states[key] = not is_expanded
                    st.rerun()
            
            with col_delete:
                if st.button(f"🗑️", key=f"delete_{key}", help=tr('json_formatter.delete_stored')):
                    del st.session_state.stored_jsons[key]
                    if key in st.session_state.stored_expanded_states:
                        del st.session_state.stored_expanded_states[key]
                    st.rerun()
            
            # 根据展开状态显示暂存的JSON
            if is_expanded:
                with st.container(height=300):
                    st.json(stored_json, expanded=expanded_level)
            
            st.markdown("---")

# 返回主页按钮
# st.markdown("---")
if st.button(f"🏠 {tr('json_formatter.back_home')}", use_container_width=True):
    st.switch_page("streamlit_app.py")