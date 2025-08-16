# -*- coding: utf-8 -*-
"""
Libre CMD - 远程命令执行工具
用于IT SUPPORT日常查询和监控
"""

import streamlit as st
import json
import paramiko
import pandas as pd
import io
from pathlib import Path
import time
import os
import socket
from datetime import datetime

# 导入公共函数
import sys
if getattr(sys, 'frozen', False):
    current_dir = Path(sys.executable).parent / "plugins" / "support_web_toolkit"
else:
    current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir))

from common import tr, apply_button_styles, init_language

# 页面配置
st.set_page_config(
    page_title="Libre CMD - IT Support Toolkit",
    page_icon="💻",
    layout="wide"
)

# 初始化语言设置
init_language()
apply_button_styles()

# 页面主要内容
st.title(tr("libre_cmd.title"))
st.markdown(tr("libre_cmd.description"))

# 标签页
tab1, tab2 = st.tabs([tr("libre_cmd.execute_tab"), tr("libre_cmd.config_tab")])

def load_libre_cmd_config():
    """加载Libre CMD配置文件"""
    try:
        config_file = current_dir / "libre_cmd.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Failed to load libre_cmd config: {e}")
    
    # 返回默认配置
    return {
        "servers": [],
        "libre_cmd": {}
    }


def save_libre_cmd_config(config):
    """保存Libre CMD配置文件"""
    try:
        config_file = current_dir / "libre_cmd.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Failed to save libre_cmd config: {e}")
        return False


def load_main_config():
    """加载主配置文件获取SSO凭据"""
    try:
        config_file = current_dir / "config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Failed to load main config: {e}")
    return {}


def get_plugin_credentials():
    """获取SSO凭据"""
    try:
        # 从环境变量中读取解密后的凭据
        username = os.environ.get('STREAMLIT_SSO_USERNAME', '')
        password = os.environ.get('STREAMLIT_SSO_PASSWORD', '')
        
        if not username or not password:
            st.error(tr("libre_cmd.credentials_missing_error"))
            return "", ""
        
        return username, password
        
    except Exception as e:
        st.error(f"获取凭据失败: {e}")
        return "", ""


def execute_ssh_command(hostname, username, password, command, timeout=60):
    """执行SSH命令"""
    ssh = None
    try:
        # 创建SSH客户端
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # 连接服务器，减少连接超时时间
        ssh.connect(hostname, username=username, password=password, timeout=15)
        
        # 执行命令
        stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
        
        # 设置通道超时
        stdout.channel.settimeout(5)  # 减少通道超时时间
        stderr.channel.settimeout(5)
        
        # 获取输出，使用更严格的超时控制
        output_lines = []
        error_lines = []
        
        start_time = time.time()
        max_idle_time = 10  # 最大空闲时间
        last_activity = start_time
        
        while True:
            current_time = time.time()
            
            # 检查总超时
            if current_time - start_time > timeout:
                try:
                    stdout.channel.close()
                    stderr.channel.close()
                except:
                    pass
                return False, f"Command execution timeout after {timeout} seconds"
            
            # 检查空闲超时
            if current_time - last_activity > max_idle_time:
                try:
                    stdout.channel.close()
                    stderr.channel.close()
                except:
                    pass
                return False, f"Command execution idle timeout after {max_idle_time} seconds of inactivity"
            
            # 检查命令是否完成
            if stdout.channel.exit_status_ready():
                # 读取剩余输出
                try:
                    remaining_output = stdout.read().decode('utf-8', errors='ignore')
                    if remaining_output:
                        output_lines.append(remaining_output)
                        last_activity = current_time
                    remaining_error = stderr.read().decode('utf-8', errors='ignore')
                    if remaining_error:
                        error_lines.append(remaining_error)
                        last_activity = current_time
                except Exception as e:
                    # 如果读取失败，可能是超时或连接问题
                    return False, f"Failed to read command output: {str(e)}"
                break
            
            # 尝试读取部分输出
            activity_detected = False
            try:
                if stdout.channel.recv_ready():
                    chunk = stdout.channel.recv(4096).decode('utf-8', errors='ignore')
                    if chunk:
                        output_lines.append(chunk)
                        activity_detected = True
                
                if stderr.channel.recv_stderr_ready():
                    chunk = stderr.channel.recv_stderr(4096).decode('utf-8', errors='ignore')
                    if chunk:
                        error_lines.append(chunk)
                        activity_detected = True
            except socket.timeout:
                # 通道超时是正常的，继续循环
                pass
            except Exception as e:
                return False, f"Error reading command output: {str(e)}"
            
            if activity_detected:
                last_activity = current_time
            
            # 短暂休眠避免CPU占用过高
            time.sleep(0.1)
        
        # 合并输出
        output = ''.join(output_lines)
        error = ''.join(error_lines)
        
        # 获取退出状态
        try:
            exit_status = stdout.channel.recv_exit_status()
        except:
            exit_status = -1
        
        if error or exit_status != 0:
            return False, error if error else f"Command failed with exit code {exit_status}"
        return True, output
        
    except paramiko.AuthenticationException:
        return False, "Authentication failed. Please check username and password."
    except paramiko.SSHException as e:
        return False, f"SSH connection error: {str(e)}"
    except socket.timeout:
        return False, "Connection timeout. Please check hostname and network connectivity."
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"
    finally:
        if ssh:
            try:
                ssh.close()
            except:
                pass


def format_output(output, output_type, delimiter=None):
    """格式化输出结果"""
    if output_type == "csv" and delimiter:
        try:
            # 将输出转换为CSV格式
            lines = output.strip().split('\n')
            if lines:
                # 使用指定分隔符解析CSV
                csv_data = []
                for line in lines:
                    csv_data.append(line.split(delimiter))
                
                # 创建DataFrame
                if csv_data:
                    df = pd.DataFrame(csv_data[1:], columns=csv_data[0] if len(csv_data) > 1 else None)
                    # 限制显示1000行
                    if len(df) > 1000:
                        st.warning(tr("libre_cmd.csv_truncated"))
                        df = df.head(1000)
                    return df
        except Exception as e:
            st.error(f"CSV parsing error: {e}")
            return output
    
    elif output_type == "json":
        try:
            # 尝试解析JSON
            json_data = json.loads(output)
            # 如果JSON字符串太长，保存到文件
            if len(output) > 10000:
                downloads_dir = Path.home() / "Downloads"
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"libre_cmd_output_{timestamp}.json"
                filepath = downloads_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                
                st.success(tr("libre_cmd.json_saved").format(filename=filename))
                return json_data
            return json_data
        except Exception as e:
            st.error(f"JSON parsing error: {e}")
            return output
    
    else:  # text format
        # 如果文本太长，保存到文件
        if len(output) > 10000:
            downloads_dir = Path.home() / "Downloads"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"libre_cmd_output_{timestamp}.txt"
            filepath = downloads_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(output)
            
            st.success(tr("libre_cmd.text_saved").format(filename=filename))
            return output[:1000] + "\n\n[Output truncated, full content saved to Downloads]"
        
        return output


def show_config_page():
    """显示配置页面"""
    st.subheader(tr("libre_cmd.config_title"))
    
    config = load_libre_cmd_config()
    
    # 服务器管理
    st.markdown("#### " + tr("libre_cmd.servers_section"))
    
    # 添加新服务器
    with st.expander(tr("libre_cmd.add_server")):
        new_server = st.text_input(tr("libre_cmd.server_host"))
        if st.button(tr("libre_cmd.save_server")):
            if new_server and new_server not in config["servers"]:
                config["servers"].append(new_server)
                save_libre_cmd_config(config)
                st.success(tr("libre_cmd.config_saved"))
                st.rerun()
    
    # 显示现有服务器
    if config["servers"]:
        st.markdown("##### " + tr("libre_cmd.current_servers"))
        
        # 初始化编辑状态
        if "editing_server_index" not in st.session_state:
            st.session_state.editing_server_index = -1
        
        for i, server in enumerate(config["servers"]):
            # 检查是否处于编辑模式
            is_editing = st.session_state.editing_server_index == i
            
            if is_editing:
                # 编辑模式
                edit_col1, edit_col2, edit_col3 = st.columns([3, 1, 1])
                with edit_col1:
                    new_server_value = st.text_input(
                        tr("libre_cmd.server_host"),
                        value=server,
                        key=f"edit_input_{i}"
                    )
                with edit_col2:
                    if st.button(tr("libre_cmd.save_server"), key=f"save_edit_{i}"):
                        if new_server_value and new_server_value != server:
                            # 更新服务器列表
                            config["servers"][i] = new_server_value
                            # 同时更新所有使用该服务器的工作流
                            for workflow_name, workflow_config in config["libre_cmd"].items():
                                if workflow_config["server"] == server:
                                    workflow_config["server"] = new_server_value
                            save_libre_cmd_config(config)
                            st.success(tr("libre_cmd.config_saved"))
                        # 退出编辑模式
                        st.session_state.editing_server_index = -1
                        st.rerun()
                with edit_col3:
                    if st.button(tr("libre_cmd.cancel_edit"), key=f"cancel_edit_{i}"):
                        # 退出编辑模式
                        st.session_state.editing_server_index = -1
                        st.rerun()
            else:
                # 显示模式
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.text(server)
                with col2:
                    if st.button(tr("libre_cmd.edit_server"), key=f"edit_server_{i}"):
                        st.session_state.editing_server_index = i
                        st.rerun()
                with col3:
                    if st.button(tr("libre_cmd.delete_server"), key=f"del_server_{i}"):
                        config["servers"].remove(server)
                        save_libre_cmd_config(config)
                        # 如果删除的是正在编辑的服务器，退出编辑模式
                        if st.session_state.editing_server_index == i:
                            st.session_state.editing_server_index = -1
                        elif st.session_state.editing_server_index > i:
                            st.session_state.editing_server_index -= 1
                        st.rerun()
    
    st.divider()
    
    # Workflow管理
    st.markdown("##### " + tr("libre_cmd.workflows_section"))
    
    # 添加新workflow
    with st.expander(tr("libre_cmd.add_workflow")):
        workflow_name = st.text_input(tr("libre_cmd.workflow_name"))
        workflow_desc = st.text_area(tr("libre_cmd.workflow_description"), max_chars=100)
        workflow_server = st.selectbox(
            tr("libre_cmd.select_server"),
            options=config["servers"] + [tr("libre_cmd.custom_server")]
        )
        
        if workflow_server == tr("libre_cmd.custom_server"):
            custom_server = st.text_input(tr("libre_cmd.server_host"))
            if custom_server:
                workflow_server = custom_server
        
        # 步骤配置
        st.markdown("#### " + tr("libre_cmd.steps_config"))
        
        if 'new_workflow_steps' not in st.session_state:
            st.session_state.new_workflow_steps = []
        
        # 添加步骤
        with st.container():
            step_command = st.text_area(tr("libre_cmd.step_command"))
            step_output_type = st.selectbox(
                 tr("libre_cmd.step_output_type"),
                options=["text", "json", "csv"]
            )
            step_delimiter = None
            if step_output_type == "csv":
                step_delimiter = st.text_input(tr("libre_cmd.step_delimiter"), value="|")
            
            step_timeout = st.number_input(tr("libre_cmd.step_timeout"), min_value=10, max_value=300, value=60)
            
            if st.button(tr("libre_cmd.add_step")):
                if step_command:
                    step = {
                        "command": step_command,
                        "output_type": step_output_type,
                        "delimiter": step_delimiter,
                        "timeout": step_timeout
                    }
                    st.session_state.new_workflow_steps.append(step)
                    st.rerun()
        
        # 显示已添加的步骤
        if st.session_state.new_workflow_steps:
            st.markdown("#### " + tr("libre_cmd.added_steps"))
            for i, step in enumerate(st.session_state.new_workflow_steps):
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.text(f"Step {i+1}: {step['command'][:50]}...")
                        st.text(f"Type: {step['output_type']}, Timeout: {step['timeout']}s")
                    with col2:
                        if st.button(tr("libre_cmd.delete_step"), key=f"remove_step_{i}"):
                            st.session_state.new_workflow_steps.pop(i)
                            st.rerun()
        
        # 保存workflow
        if st.button(tr("libre_cmd.save_workflow")):
            if workflow_name and workflow_desc and workflow_server and st.session_state.new_workflow_steps:
                # 如果是自定义服务器且不在列表中，添加到服务器列表
                if workflow_server not in config["servers"]:
                    config["servers"].append(workflow_server)
                
                config["libre_cmd"][workflow_name] = {
                    "description": workflow_desc,
                    "server": workflow_server,
                    "steps": st.session_state.new_workflow_steps
                }
                
                if save_libre_cmd_config(config):
                    st.success(tr("libre_cmd.workflow_saved"))
                    st.session_state.new_workflow_steps = []
                    st.rerun()
            else:
                st.error(tr("libre_cmd.fill_all_fields"))
    
    # 显示现有workflows
    if config["libre_cmd"]:
        st.markdown("##### " + tr("libre_cmd.current_workflows"))
        for workflow_name, workflow_data in config["libre_cmd"].items():
            with st.expander(f"{workflow_name} - {workflow_data['description']}"):
                st.write(f"**{tr('libre_cmd.server')}:** {workflow_data['server']}")
                st.write(f"**{tr('libre_cmd.steps')}:** {len(workflow_data['steps'])}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(tr("libre_cmd.copy_config"), key=f"copy_{workflow_name}"):
                        st.code(json.dumps({workflow_name: workflow_data}, indent=2, ensure_ascii=False))
                
                with col2:
                    if st.button(tr("libre_cmd.delete_workflow"), key=f"del_{workflow_name}"):
                        del config["libre_cmd"][workflow_name]
                        save_libre_cmd_config(config)
                        st.rerun()


with tab2:
    show_config_page()

with tab1:
    # 加载配置
    config = load_libre_cmd_config()
    
    # 获取解密后的SSO凭据
    username, password = get_plugin_credentials()
    
    if not username or not password:
        st.error(tr("libre_cmd.credentials_missing"))
        st.info(tr("libre_cmd.credentials_setup_info"))
        st.markdown("---")
        st.markdown(f"### {tr('libre_cmd.config_instructions_title')}")
        st.markdown(tr("libre_cmd.config_instructions_content"))
        st.stop()

    # Workflow选择
    if not config["libre_cmd"]:
        st.info(tr("libre_cmd.no_workflows"))
        st.markdown("---")
        st.markdown(f"### {tr('libre_cmd.workflow_config_title')}")
        st.markdown(tr("libre_cmd.workflow_config_content"))
        st.stop()
    
    workflow_names = list(config["libre_cmd"].keys())
    selected_workflow = st.selectbox(
        tr("libre_cmd.select_workflow"),
        options=workflow_names,
        key="workflow_selector"
    )
    
    if selected_workflow:
        # 清空之前的结果（当切换workflow时）
        if 'last_workflow' not in st.session_state or st.session_state.last_workflow != selected_workflow:
            st.session_state.last_workflow = selected_workflow
            st.session_state.step_results = []
            st.session_state.execution_in_progress = False
            
        workflow = config["libre_cmd"][selected_workflow]
        
        # 显示workflow信息
        st.markdown(f"### {selected_workflow}")
        
        # 创建信息展示区域
        info_col1, info_col2 = st.columns([3, 1])
        
        with info_col1:
            st.write(f"**{tr('libre_cmd.workflow_description')}:** {workflow['description']}")
            st.write(f"**{tr('libre_cmd.workflow_server')}:** {workflow['server']}")
            st.write(f"**{tr('libre_cmd.steps')}:** {len(workflow['steps'])}")
        
        with info_col2:
            # 复制配置按钮 - 支持展开/隐藏
            config_key = f"show_config_{selected_workflow}"
            if config_key not in st.session_state:
                st.session_state[config_key] = False
            
            button_text = tr("libre_cmd.hide_config") if st.session_state[config_key] else tr("libre_cmd.copy_config")
            if st.button(button_text, key=f"copy_workflow_{selected_workflow}"):
                st.session_state[config_key] = not st.session_state[config_key]
                st.rerun()
        
    # 显示配置内容（如果展开状态为True）
    if config_key in st.session_state and st.session_state[config_key]:
        workflow_json = json.dumps({selected_workflow: workflow}, indent=4, ensure_ascii=False)
        st.code(workflow_json, language="json")
        st.success(tr("libre_cmd.config_displayed_success"))
    
    st.divider()
    
    # 显示步骤和执行按钮
    st.markdown("### " + tr("libre_cmd.workflow_steps"))
    
    # 初始化结果存储
    if 'step_results' not in st.session_state:
        st.session_state.step_results = []
    
    # 步骤预览
    st.subheader(tr("libre_cmd.steps_preview"))
        
    # 步骤概览卡片
    step_cols = st.columns(min(len(workflow['steps']), 3))
    for i, step in enumerate(workflow['steps']):
        col_idx = i % 3
        with step_cols[col_idx]:
            # 获取步骤执行状态
            status_icon = "⏳"
            status_color = "normal"
            
            if hasattr(st.session_state, 'step_results') and i < len(st.session_state.step_results):
                result = st.session_state.step_results[i]
                if result.get('success'):
                    status_icon = "✅"
                    status_color = "normal"
                else:
                    status_icon = "❌"
                    status_color = "normal"
            elif hasattr(st.session_state, 'execution_in_progress') and st.session_state.execution_in_progress:
                if i < len(getattr(st.session_state, 'step_results', [])):
                    status_icon = "🔄"
                    status_color = "normal"
            
            # 显示步骤卡片
            with st.container():
                st.markdown(f"**{tr('libre_cmd.step_number').format(number=i+1)}** {status_icon}")
                st.code(step['command'][:40] + ("..." if len(step['command']) > 40 else ""), language="bash")
                st.caption(f"{tr('libre_cmd.output_type_label')}: {step['output_type']} | {tr('libre_cmd.timeout_label')}: {step.get('timeout', 60)}s")
        
    # 详细步骤信息
    with st.expander(tr("libre_cmd.view_detailed_steps"), expanded=False):
        for i, step in enumerate(workflow['steps']):
            st.markdown(f"**{tr('libre_cmd.step_number').format(number=i+1)}:**")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.code(step['command'], language="bash")
                st.write(f"• **{tr('libre_cmd.output_type')}:** {step['output_type']}")
                if step.get('delimiter'):
                    st.write(f"• **{tr('libre_cmd.delimiter')}:** `{step['delimiter']}`")
                st.write(f"• **{tr('libre_cmd.timeout_seconds')}:** {step.get('timeout', 60)} {tr('libre_cmd.seconds')}")
            
            with col2:
                # 复制命令按钮
                if st.button("📋", key=f"copy_cmd_{selected_workflow}_{i}", help=tr("libre_cmd.copy_command")):
                    st.code(step['command'], language="bash")
            
            if i < len(workflow['steps']) - 1:
                st.divider()
        
    st.divider()
    
    # 执行控制区域
    exec_col1, exec_col2, exec_col3 = st.columns([2, 1, 1])
    
    with exec_col1:
        execute_button = st.button(
            tr("libre_cmd.execute_workflow"), 
            type="primary",
            disabled=getattr(st.session_state, 'execution_in_progress', False)
        )
    
    with exec_col2:
        pass  # 预留位置
    
    with exec_col3:
        pass  # 预留位置
        
    if execute_button:
        st.session_state.step_results = []
        st.session_state.execution_in_progress = True
        
        # 创建执行状态显示区域
        status_container = st.container()
        progress_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        # 执行工作流
        total_steps = len(workflow['steps'])
        failed_steps = []
        
        for i, step in enumerate(workflow['steps']):
            with status_container:
                st.markdown(f"### {tr('libre_cmd.executing_step').format(current=i+1, total=total_steps)}")
                st.code(step['command'], language="bash")
            
            # 显示执行状态和超时信息
            step_timeout = step.get('timeout', 60)
            status_text.text(tr("libre_cmd.executing_command").format(command=step['command'][:50], timeout=step_timeout))
            
            # 创建一个临时的状态显示
            temp_status = st.empty()
            temp_status.info(tr("libre_cmd.connecting_server").format(server=workflow['server']))
            
            # 执行命令
            start_time = time.time()
            try:
                success, output_or_error = execute_ssh_command(
                     hostname=workflow['server'],
                     username=username,
                     password=password,
                     command=step['command'],
                     timeout=step_timeout
                 )
                execution_time = time.time() - start_time
                temp_status.empty()  # 清除临时状态
            except Exception as e:
                execution_time = time.time() - start_time
                success = False
                output_or_error = tr("libre_cmd.execution_exception").format(error=str(e))
                temp_status.empty()  # 清除临时状态
            
            # 保存结果
            step_result = {
                'step': i + 1,
                'command': step['command'],
                'success': success,
                'output': output_or_error if success else '',
                'error': output_or_error if not success else '',
                'output_type': step['output_type'],
                'execution_time': execution_time
            }
            st.session_state.step_results.append(step_result)
            
            # 更新进度
            progress_bar.progress((i + 1) / total_steps)
            
            # 显示步骤结果
            if step_result['success']:
                st.success(tr("libre_cmd.step_success").format(step=i+1, time=f"{execution_time:.2f}"))
                
                # 格式化并显示输出
                formatted_result = format_output(
                    step_result['output'],
                    step['output_type'],
                    step.get('delimiter')
                )
                
                # 根据输出类型显示结果
                if step['output_type'] == 'csv' and isinstance(formatted_result, pd.DataFrame):
                    st.dataframe(formatted_result, height=600)
                elif step['output_type'] == 'json' and isinstance(formatted_result, (dict, list)):
                    st.json(formatted_result)
                else:
                    st.text_area(
                        tr("libre_cmd.step_output").format(step=i+1),
                        value=str(formatted_result),
                        height=200,
                        key=f"output_{i}"
                    )
            else:
                st.error(tr("libre_cmd.step_failed").format(step=i+1, time=f"{execution_time:.2f}", error=step_result.get('error', 'Unknown error')))
                failed_steps.append(i + 1)
                
                # 询问是否继续
                if i < total_steps - 1:  # 不是最后一步
                    continue_execution = st.radio(
                        tr("libre_cmd.step_continue_question").format(step=i+1),
                        [tr("libre_cmd.continue_execution"), tr("libre_cmd.stop_execution")],
                        key=f"continue_radio_{i}"
                    )
                    if continue_execution == tr("libre_cmd.stop_execution"):
                        st.warning(tr("libre_cmd.workflow_stopped_warning"))
                        break
            
            st.divider()
        
        # 工作流执行完成
        st.session_state.execution_in_progress = False
        status_text.text(tr("libre_cmd.workflow_execution_complete"))
        
        # 显示简单的执行摘要
        success_count = sum(1 for r in st.session_state.step_results if r['success'])
        total_executed = len(st.session_state.step_results)
        
        if failed_steps:
            st.warning(tr("libre_cmd.workflow_complete_partial").format(
                success=success_count, 
                total=total_executed, 
                failed=', '.join(map(str, failed_steps))
            ))
        else:
            st.success(tr("libre_cmd.workflow_complete_success").format(count=success_count))
        
        st.info(tr("libre_cmd.detailed_results_info"))
    
    # 显示已有的执行结果（如果存在）
    if hasattr(st.session_state, 'step_results') and st.session_state.step_results and not getattr(st.session_state, 'execution_in_progress', False):
        st.divider()
        
        # 显示执行结果详情
        st.markdown(f"### {tr('libre_cmd.execution_summary')}")
        success_count = sum(1 for r in st.session_state.step_results if r['success'])
        total_executed = len(st.session_state.step_results)
        failed_steps = [r['step'] for r in st.session_state.step_results if not r['success']]
        
        if failed_steps:
            st.warning(tr("libre_cmd.workflow_complete_partial").format(
                success=success_count, 
                total=total_executed, 
                failed=', '.join(map(str, failed_steps))
            ))
        else:
            st.success(tr("libre_cmd.workflow_complete_success").format(count=success_count))
        
        # 显示每个步骤的详细结果
        for i, result in enumerate(st.session_state.step_results):
            command_display = result['command'][:50] + ('...' if len(result['command']) > 50 else '')
            with st.expander(tr("libre_cmd.step_expander_title").format(step=result['step'], command=command_display), expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.code(result['command'], language="bash")
                    if result['success']:
                        st.success(tr("libre_cmd.execution_success").format(time=f"{result['execution_time']:.2f}"))
                        
                        # 格式化并显示输出
                        if result['output']:
                            formatted_result = format_output(
                                result['output'],
                                result['output_type']
                            )
                            
                            if result['output_type'] == 'csv' and isinstance(formatted_result, pd.DataFrame):
                                st.dataframe(formatted_result)
                            elif result['output_type'] == 'json' and isinstance(formatted_result, (dict, list)):
                                st.json(formatted_result)
                            else:
                                st.text_area(
                                    tr("libre_cmd.output_result"),
                                    value=str(formatted_result),
                                    height=200,
                                    key=f"result_output_{i}"
                                )
                    else:
                        st.error(tr("libre_cmd.execution_failed").format(time=f"{result['execution_time']:.2f}"))
                        if result['error']:
                            st.text_area(
                                tr("libre_cmd.error_info"),
                                value=result['error'],
                                height=100,
                                key=f"result_error_{i}"
                            )
                
                with col2:
                    st.write(tr("libre_cmd.output_type_info").format(type=result['output_type']))
                    st.write(tr("libre_cmd.execution_time_info").format(time=f"{result['execution_time']:.2f}"))
                    status = tr("libre_cmd.status_success") if result['success'] else tr("libre_cmd.status_failed")
                    st.write(tr("libre_cmd.status_info").format(status=status))
        
        # 提供重新执行和导出功能
        st.divider()
        result_col1, result_col2, result_col3 = st.columns([2, 1, 1])
        
        with result_col1:
            st.markdown(f"### {tr('libre_cmd.execution_actions')}")
        
        with result_col2:
            if st.button(f"🔄 {tr('libre_cmd.re_execute')}", key="re_execute_from_results"):
                st.session_state.step_results = []
                st.session_state.execution_in_progress = False
                st.rerun()
        
        with result_col3:
            results_json = json.dumps(st.session_state.step_results, indent=2, ensure_ascii=False)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label=f"📋 {tr('libre_cmd.export_results')}",
                data=results_json,
                file_name=f"{selected_workflow}_results_{timestamp}.json",
                mime="application/json",
                key="export_results_from_results"
            )

