# -*- coding: utf-8 -*-
"""
Todo List工具页面
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime, timedelta
from common import load_config, load_translations, tr, init_language, save_config, apply_button_styles

# 页面配置
st.set_page_config(
    page_title="Todo List - IT Support Toolkit",
    page_icon="✅",
    layout="wide"
)

# 初始化语言设置
init_language()

# 应用通用按钮样式
apply_button_styles()

# 初始化session state
if 'new_todo' not in st.session_state:
    st.session_state.new_todo = ""
if 'show_done' not in st.session_state:
    st.session_state.show_done = False
if 'editing_todo' not in st.session_state:
    st.session_state.editing_todo = -1  # -1表示没有在编辑任何项目
if 'edit_text' not in st.session_state:
    st.session_state.edit_text = ""

def load_todos():
    """加载Todo数据"""
    config = load_config()
    todo_list_config = config.get('todo_list', {})
    return todo_list_config.get('todo', []), todo_list_config.get('done', [])

def save_todos(todo_list, done_list):
    """保存Todo数据"""
    config = load_config()
    if 'todo_list' not in config:
        config['todo_list'] = {}
    config['todo_list']['todo'] = todo_list
    config['todo_list']['done'] = done_list
    return save_config(config)

def clean_old_done_todos(done_list):
    """清理超过两周的已完成Todo"""
    two_weeks_ago = datetime.now() - timedelta(weeks=2)
    cleaned_done = []
    
    for item in done_list:
        try:
            # 解析完成时间
            done_time_str = item.get('done_time', '')
            if done_time_str:
                done_time = datetime.strptime(done_time_str, '%Y%m%d %H:%M:%S')
                if done_time > two_weeks_ago:
                    cleaned_done.append(item)
        except ValueError:
            # 如果时间格式有问题，保留该项目
            cleaned_done.append(item)
    
    return cleaned_done

def add_todo(display_name, priority="medium"):
    """添加新的Todo"""
    if not display_name.strip():
        return False
    
    todo_list, done_list = load_todos()
    
    new_todo = {
        "display_name": display_name.strip(),
        "priority": priority,
        "creation_time": datetime.now().strftime('%Y%m%d %H:%M:%S')
    }
    
    todo_list.append(new_todo)
    return save_todos(todo_list, done_list)

def complete_todo(index):
    """完成Todo"""
    todo_list, done_list = load_todos()
    
    if 0 <= index < len(todo_list):
        completed_todo = todo_list.pop(index)
        completed_todo['done_time'] = datetime.now().strftime('%Y%m%d %H:%M:%S')
        done_list.append(completed_todo)
        
        # 清理旧的已完成项目
        done_list = clean_old_done_todos(done_list)
        
        return save_todos(todo_list, done_list)
    return False

def delete_todo(index):
    """删除Todo"""
    todo_list, done_list = load_todos()
    
    if 0 <= index < len(todo_list):
        todo_list.pop(index)
        return save_todos(todo_list, done_list)
    return False

def edit_todo(index, new_text):
    """编辑Todo"""
    if not new_text.strip():
        return False
    
    todo_list, done_list = load_todos()
    
    if 0 <= index < len(todo_list):
        todo_list[index]['display_name'] = new_text.strip()
        return save_todos(todo_list, done_list)
    return False

def update_todo_priority(index, priority):
    """更新Todo优先级"""
    todo_list, done_list = load_todos()
    
    if 0 <= index < len(todo_list):
        todo_list[index]['priority'] = priority
        return save_todos(todo_list, done_list)
    return False

def get_priority_style(priority):
    """根据优先级获取样式"""
    styles = {
        "urgent": {"color": "#ff4444", "emoji": "🔥", "weight": "bold"},
        "medium": {"color": "#ff8800", "emoji": "⚡", "weight": "normal"},
        "low": {"color": "#4444ff", "emoji": "💧", "weight": "normal"}
    }
    return styles.get(priority, styles["medium"])

def restore_todo(index):
    """恢复已完成的Todo"""
    todo_list, done_list = load_todos()
    
    if 0 <= index < len(done_list):
        restored_todo = done_list.pop(index)
        # 移除done_time字段
        if 'done_time' in restored_todo:
            del restored_todo['done_time']
        # 更新创建时间为当前时间
        restored_todo['creation_time'] = datetime.now().strftime('%Y%m%d %H:%M:%S')
        todo_list.append(restored_todo)
        return save_todos(todo_list, done_list)
    return False

def delete_done_todo(index):
    """删除已完成的Todo"""
    todo_list, done_list = load_todos()
    
    if 0 <= index < len(done_list):
        done_list.pop(index)
        return save_todos(todo_list, done_list)
    return False

# 页面标题
st.title(f"✅ {tr('todo_list.title')}")

# 添加新Todo
st.subheader(f"➕ {tr('todo_list.add_new')}")

# 使用form来处理Enter键提交
with st.form(key='add_todo_form', clear_on_submit=True):
    col_input, col_priority = st.columns([3, 1])
    
    with col_input:
        new_todo_input = st.text_input(
            "new_todo",
            placeholder=tr('todo_list.input_placeholder'),
            key="new_todo_input",
            label_visibility="collapsed"
        )
    
    with col_priority:
        new_todo_priority = st.selectbox(
            "优先级",
            options=["urgent", "medium", "low"],
            index=1,  # 默认选择medium
            key="new_todo_priority",
            label_visibility="collapsed"
        )
    
    # 提交按钮，用户按Enter时会触发
    submitted = st.form_submit_button("Add", type="primary")
    
    if submitted and new_todo_input.strip():
        if add_todo(new_todo_input, new_todo_priority):
            st.success(f"✅ {tr('todo_list.add_success')}")
            st.rerun()
        else:
            st.error(f"❌ {tr('todo_list.add_failed')}")
    elif submitted and not new_todo_input.strip():
        st.warning(f"⚠️ {tr('todo_list.empty_warning')}")

# 加载Todo数据
todo_list, done_list = load_todos()

# 显示待办事项
st.subheader(f"📋 {tr('todo_list.pending_todos')} ({len(todo_list)})")

if todo_list:
    for i, todo in enumerate(todo_list):
        col1, col2, col3, col4, col5 = st.columns([0.5, 2.5, 1, 0.5, 0.5])
        
        # 获取优先级和样式
        priority = todo.get('priority', 'medium')
        style = get_priority_style(priority)
        
        with col1:
            if st.button("⭕", key=f"complete_{i}", help=tr('todo_list.complete_help')):
                if complete_todo(i):
                    st.success(f"✅ {tr('todo_list.complete_success')}")
                    st.rerun()
                else:
                    st.error(f"❌ {tr('todo_list.complete_failed')}")
        
        with col2:
            # 检查是否正在编辑这个项目
            if st.session_state.editing_todo == i:
                # 编辑模式
                with st.form(key=f'edit_form_{i}'):
                    edited_text = st.text_input(
                        "edit_todo",
                        value=st.session_state.edit_text,
                        key=f"edit_input_{i}",
                        label_visibility="collapsed"
                    )
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.form_submit_button("💾 保存", type="primary"):
                            if edit_todo(i, edited_text):
                                st.session_state.editing_todo = -1
                                st.session_state.edit_text = ""
                                st.success(f"✅ 编辑成功")
                                st.rerun()
                            else:
                                st.error(f"❌ 编辑失败")
                    
                    with col_cancel:
                        if st.form_submit_button("❌ 取消"):
                            st.session_state.editing_todo = -1
                            st.session_state.edit_text = ""
                            st.rerun()
            else:
                # 显示模式 - 带优先级样式
                st.markdown(f"<span style='color: {style['color']}; font-weight: {style['weight']};'>{style['emoji']} **{todo['display_name']}**</span>", unsafe_allow_html=True)
                st.caption(f"{tr('todo_list.created_at')}: {todo['creation_time']}")
        
        with col3:
            # 优先级选择框
            new_priority = st.selectbox(
                "优先级",
                options=["urgent", "medium", "low"],
                index=["urgent", "medium", "low"].index(priority),
                key=f"priority_{i}",
                label_visibility="collapsed"
            )
            if new_priority != priority:
                if update_todo_priority(i, new_priority):
                    st.rerun()
        
        with col4:
            if st.button("✏️", key=f"edit_{i}", help="编辑此项目"):
                st.session_state.editing_todo = i
                st.session_state.edit_text = todo['display_name']
                st.rerun()
        
        with col5:
            if st.button("🗑️", key=f"delete_{i}", help=tr('todo_list.delete_help')):
                if delete_todo(i):
                    st.success(f"✅ {tr('todo_list.delete_success')}")
                    st.rerun()
                else:
                    st.error(f"❌ {tr('todo_list.delete_failed')}")
        
        st.markdown("---")
else:
    st.info(f"💡 {tr('todo_list.no_pending_todos')}")

# 显示已完成事项（可折叠）
if done_list:
    with st.expander(f"✅ {tr('todo_list.completed_todos')} ({len(done_list)})", expanded=st.session_state.show_done):
        # 清理按钮
        if st.button(f"🧹 {tr('todo_list.clean_old_completed')}", help=tr('todo_list.clean_help')):
            cleaned_done = clean_old_done_todos(done_list)
            if save_todos(todo_list, cleaned_done):
                removed_count = len(done_list) - len(cleaned_done)
                if removed_count > 0:
                    st.success(f"✅ {tr('todo_list.clean_success')}: {removed_count}")
                    st.rerun()
                else:
                    st.info(f"💡 {tr('todo_list.no_old_completed')}")
            else:
                st.error(f"❌ {tr('todo_list.clean_failed')}")
        
        st.markdown("---")
        
        for i, todo in enumerate(done_list):
            col1, col2, col3, col4 = st.columns([0.5, 3, 0.5, 0.5])
            
            # 获取优先级和样式
            priority = todo.get('priority', 'medium')
            style = get_priority_style(priority)
            
            with col1:
                st.write("✅")
            
            with col2:
                # 显示带优先级样式的已完成Todo
                st.markdown(f"<span style='color: {style['color']}; font-weight: {style['weight']}; text-decoration: line-through;'>{style['emoji']} {todo['display_name']}</span>", unsafe_allow_html=True)
                # 合并创建时间和完成时间到同一行
                time_info = f"{tr('todo_list.created_at')}: {todo['creation_time']}"
                if 'done_time' in todo:
                    time_info += f" | {tr('todo_list.completed_at')}: {todo['done_time']}"
                st.caption(time_info)
            
            with col3:
                if st.button("↩️", key=f"restore_{i}", help=tr('todo_list.restore_help')):
                    if restore_todo(i):
                        st.success(f"✅ {tr('todo_list.restore_success')}")
                        st.rerun()
                    else:
                        st.error(f"❌ {tr('todo_list.restore_failed')}")
            
            with col4:
                if st.button("🗑️", key=f"delete_done_{i}", help=tr('todo_list.delete_help')):
                    if delete_done_todo(i):
                        st.success(f"✅ {tr('todo_list.delete_success')}")
                        st.rerun()
                    else:
                        st.error(f"❌ {tr('todo_list.delete_failed')}")
            
            st.markdown("---")
else:
    st.info(f"💡 {tr('todo_list.no_completed_todos')}")

# 统计信息
st.subheader(f"📊 {tr('todo_list.statistics')}")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(tr('todo_list.pending_count'), len(todo_list))

with col2:
    st.metric(tr('todo_list.completed_count'), len(done_list))

with col3:
    total = len(todo_list) + len(done_list)
    completion_rate = (len(done_list) / total * 100) if total > 0 else 0
    st.metric(tr('todo_list.completion_rate'), f"{completion_rate:.1f}%")

# 返回主页按钮
st.markdown("---")
if st.button(f"🏠 {tr('todo_list.back_home')}", use_container_width=True):
    st.switch_page("streamlit_app.py")