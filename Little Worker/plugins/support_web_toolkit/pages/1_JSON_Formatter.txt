# -*- coding: utf-8 -*-
"""
JSON格式化工具页面
"""

import streamlit as st
import json
import ast
from pathlib import Path
from datetime import datetime
from common import load_config, load_translations, tr, init_language, save_config, apply_button_styles

# 页面配置
st.set_page_config(
    page_title="JSON Formatter - IT Support Toolkit",
    page_icon="📄",
    layout="wide"
)

# 初始化语言设置
init_language()

# 应用通用按钮样式
apply_button_styles()

# 初始化暂存状态
if 'stored_jsons' not in st.session_state:
    st.session_state.stored_jsons = {}  # 字典存储多个结果
if 'stored_expanded_states' not in st.session_state:
    st.session_state.stored_expanded_states = {}  # 每个结果的展开状态
if 'editing_quick_links' not in st.session_state:
    st.session_state.editing_quick_links = False
if 'temp_quick_links' not in st.session_state:
    st.session_state.temp_quick_links = {}
if 'last_input' not in st.session_state:
    st.session_state.last_input = ""
if 'formatted_input' not in st.session_state:
    st.session_state.formatted_input = ""

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
    st.subheader(f"⚙️ {tr('json_formatter.edit_quick_links')}")
    
    # Quick Links 编辑功能
    with st.expander(f"🆕 {tr('json_formatter.add_new_category')}", expanded=False):
        new_category = st.text_input(tr('json_formatter.category_name'), placeholder=tr('json_formatter.category_placeholder'))
        if st.button(tr('json_formatter.add_category_button')) and new_category:
            if new_category not in st.session_state.temp_quick_links:
                st.session_state.temp_quick_links[new_category] = []
                st.success(f"✅ {tr('json_formatter.category_added_success')}: {new_category}")
                st.rerun()
            else:
                st.error(f"❌ {tr('json_formatter.category_already_exists')}: {new_category}")
    
    # 编辑现有分类
    categories = list(st.session_state.temp_quick_links.keys())
    for category in categories:
        with st.expander(f"📂 {category}", expanded=True):
            links = st.session_state.temp_quick_links[category]
            
            # 显示现有链接
            for i, link in enumerate(links):
                col1, col2, col3 = st.columns([2, 3, 1])
                with col1:
                    new_name = st.text_input(tr('json_formatter.link_name'), value=link['name'], key=f"name_{category}_{i}")
                with col2:
                    new_url = st.text_input(tr('json_formatter.link_url'), value=link['url'], key=f"url_{category}_{i}")
                with col3:
                    if st.button("🗑️", key=f"del_{category}_{i}", help=tr('json_formatter.delete_link')):
                        st.session_state.temp_quick_links[category].pop(i)
                        st.rerun()
                
                # 更新链接
                st.session_state.temp_quick_links[category][i] = {'name': new_name, 'url': new_url}
            
            # 添加新链接
            st.markdown(f"**{tr('json_formatter.add_new_link')}:**")
            col1, col2, col3 = st.columns([2, 3, 1])
            with col1:
                link_name = st.text_input(tr('json_formatter.link_name_placeholder'), key=f"new_name_{category}")
            with col2:
                link_url = st.text_input(tr('json_formatter.link_url_placeholder'), key=f"new_url_{category}")
            with col3:
                if st.button("➕", key=f"add_{category}", help=tr('json_formatter.add_link_button')):
                    if link_name and link_url:
                        st.session_state.temp_quick_links[category].append({'name': link_name, 'url': link_url})
                        st.rerun()
                    
            # 删除分类
            if st.button(f"🗑️ {tr('json_formatter.delete_category_button')} {category}", key=f"del_cat_{category}", type="secondary"):
                del st.session_state.temp_quick_links[category]
                st.rerun()
            
            st.markdown("---")
    
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

# 主要功能区域 - 改为竖向布局以提供更宽的JSON显示空间

# JSON输入区域
placeholder_text = tr('json_formatter.json_example_placeholder')
help_text = tr('json_formatter.input_help_text')

# 使用当前格式化的输入作为默认值
current_value = st.session_state.formatted_input if st.session_state.formatted_input else ""

json_input = st.text_area(
    tr('json_formatter.input_placeholder'),
    value=current_value,
    height=400,
    placeholder=placeholder_text,
    help=help_text,
    key="json_input_area"
)

# 选项设置
st.subheader(f"⚙️ Options")

# 将indent size和expanded level放在同一行
col1, col2 = st.columns(2)
with col1:
    indent_size = st.slider(tr('json_formatter.indent_size'), min_value=1, max_value=8, value=2)
with col2:
    expanded_level = st.slider(tr('json_formatter.expanded_level'), min_value=1, max_value=10, value=2, help=tr('json_formatter.expanded_level_help'))

# 其他选项
sort_keys = st.checkbox(tr('json_formatter.sort_keys'), value=False)
ensure_ascii = st.checkbox(tr('json_formatter.ensure_ascii'), value=False)

# 检测输入变化或indent_size变化并自动格式化
if 'current_indent_size' not in st.session_state:
    st.session_state.current_indent_size = 2

# 检查是否需要重新格式化
indent_changed = indent_size != st.session_state.current_indent_size
input_changed = json_input != st.session_state.last_input

# 如果输入变化或缩进大小变化，重新格式化
if (input_changed or indent_changed) and json_input.strip():
    try:
        # 自动检测格式：先尝试JSON，失败后尝试Python字典
        try:
            parsed_json = json.loads(json_input)
        except json.JSONDecodeError:
            # JSON解析失败，尝试Python字典格式
            parsed_json = ast.literal_eval(json_input)
        
        # 格式化JSON，使用用户设置的缩进大小
        formatted_json = json.dumps(
            parsed_json,
            indent=indent_size,
            ensure_ascii=False,
            sort_keys=False
        )
        
        # 更新状态
        st.session_state.last_input = json_input
        st.session_state.formatted_input = formatted_json
        st.session_state.current_indent_size = indent_size
        
        # 如果是indent_size变化导致的重新格式化，需要重新运行页面来更新text_area
        if indent_changed:
            st.rerun()
        
    except (ValueError, SyntaxError, json.JSONDecodeError):
        # 如果解析失败，保持原始输入
        st.session_state.last_input = json_input
        st.session_state.formatted_input = json_input
        st.session_state.current_indent_size = indent_size
elif not json_input.strip():
    # 如果输入为空，清空状态
    st.session_state.last_input = ""
    st.session_state.formatted_input = ""
    st.session_state.current_indent_size = indent_size

# JSON结果显示区域
st.text(f"✨ {tr('json_formatter.result_section')}")

# 创建可滚动的容器
with st.container(height=400):
    # 实时处理JSON格式化
    if json_input.strip():
        try:
            # 自动检测格式：先尝试JSON，失败后尝试Python字典
            try:
                parsed_json = json.loads(json_input)
            except json.JSONDecodeError:
                # JSON解析失败，尝试Python字典格式
                parsed_json = ast.literal_eval(json_input)
            
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
                 
        except (ValueError, SyntaxError) as e:
            st.error(f"❌ {tr('json_formatter.format_error_message')}: {str(e)}")
            st.info(f"💡 {tr('json_formatter.syntax_check_message')}")
        except Exception as e:
            st.error(f"❌ {tr('json_formatter.error_processing')}: {str(e)}")
    
    else:
        # 显示示例
        st.info(f"💡 {tr('json_formatter.input_instruction')}")

# 下载按钮和暂存按钮放在容器外面
if json_input.strip():
    try:
        # 自动检测格式：先尝试JSON，失败后尝试Python字典
        try:
            parsed_json = json.loads(json_input)
        except json.JSONDecodeError:
            # JSON解析失败，尝试Python字典格式
            parsed_json = ast.literal_eval(json_input)
        
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
        
        # 按钮行 - 三个按钮并排显示
        col_download, col_copy, col_store = st.columns(3)
        
        with col_download:
            st.download_button(
                f"💾 {tr('json_formatter.download_button')}",
                formatted_json,
                f"formatted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "application/json",
                use_container_width=True
            )
        
        with col_copy:
            # 复制到剪贴板按钮
            if st.button(f"📋 {tr('json_formatter.copy_to_clipboard')}", use_container_width=True):
                # 使用JavaScript复制到剪贴板
                st.write(f"<script>navigator.clipboard.writeText(`{formatted_json.replace('`', '\\`')}`).then(() => console.log('Copied to clipboard'));</script>", unsafe_allow_html=True)
                st.success(f"✅ {tr('json_formatter.copied_success')}")
        
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
        
        # 根据展开状态显示暂存的JSON - 占满全宽
        if is_expanded:
            with st.container(height=300):
                st.json(stored_json, expanded=expanded_level)
        
        st.markdown("---")

# 返回主页按钮
# st.markdown("---")
if st.button(f"🏠 {tr('json_formatter.back_home')}", use_container_width=True):
    st.switch_page("streamlit_app.py")