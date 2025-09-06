# -*- coding: utf-8 -*-
"""
HSBC Little Worker - Comparison Variance Report Plugin
"""

import os
import traceback
from pathlib import Path
from typing import Optional
from datetime import datetime

import pandas as pd

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QComboBox, QGroupBox, QFileDialog,
    QSplitter, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

from core.plugin_base import PluginBase
from core.i18n import get_i18n_manager


class Plugin(PluginBase):
    """Comparison Variance Report Plugin"""
    
    # 插件元信息
    NAME = "comparison_variance_report"
    DISPLAY_NAME = "Comparison Variance Report"
    DESCRIPTION = "Comparison Variance Report, Semi-automated solution for monthly related user requests, protecting your eyes starts with you."
    VERSION = "1.0.0"
    AUTHOR = "Tearsyu"
    
    def __init__(self, app=None):
        super().__init__(app)
        self.i18n_manager = get_i18n_manager()
        
        # 文件路径
        self.uk_file_path = ""
        self.hk_file_path = ""
        self.csv_file_path = ""
        
        # 数据存储
        self.uk_data = None
        self.hk_data = None
        self.gcp_csv_data = None
        
        # UI组件
        self.uk_file_input = None
        self.hk_file_input = None
        self.csv_file_input = None
        self.bigquery_text = None
        self.log_text = None

        
        # 连接语言变更信号
        self.i18n_manager.language_changed.connect(self.on_language_changed)
        self.i18n_manager.language_changed.connect(lambda lang: self.set_language(lang))
    
    def initialize(self) -> bool:
        """初始化插件"""
        try:
            self.log_info(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.initialization_start')}")
            
            # 从配置中读取上次使用的文件路径
            self.uk_file_path = self.get_setting('last_uk_excel_path', '')
            self.hk_file_path = self.get_setting('last_hk_excel_path', '')
            self.csv_file_path = self.get_setting('last_csv_path', '')
            
            # 确保reports目录存在
            reports_path = self.get_setting('report_save_path', 'reports')
            if not os.path.isabs(reports_path):
                reports_path = os.path.join(self._plugin_dir, reports_path)
            os.makedirs(reports_path, exist_ok=True)
            
            self._initialized = True
            self.log_info(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.initialization_success')}")
            return True
            
        except Exception as e:
            self.log_error(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.initialization_failed')}: {e} - {traceback.format_exc()}")
            return False
    
    def create_widget(self) -> QWidget:
        """创建插件界面"""
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 创建主容器
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 标题
        title_label = QLabel(self.tr("plugin.comparison_variance_report.name"))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 描述 - 使用配置文件中的description
        config_desc = self.get_description()
        desc_label = QLabel(config_desc)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(
            "QLabel {"
            "    background-color: #f8f9fa;"
            "    border: 1px solid #dee2e6;"
            "    border-radius: 6px;"
            "    padding: 10px;"
            "    color: #495057;"
            "}"
        )
        layout.addWidget(desc_label)
        
        # 创建分割器
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)
        
        # 上半部分：文件选择和SQL生成
        top_widget = self._create_file_selection_widget()
        splitter.addWidget(top_widget)
        
        # 下半部分：日志和报告生成
        bottom_widget = self._create_log_and_report_widget()
        splitter.addWidget(bottom_widget)
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        # 将主容器设置到滚动区域中
        scroll_area.setWidget(widget)
        
        return scroll_area
    
    def _create_file_selection_widget(self) -> QWidget:
        """创建文件选择区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 文件选择区域
        file_group = QGroupBox(self.tr("plugin.comparison_variance_report.file_selection_group"))
        file_layout = QVBoxLayout(file_group)
        
        # UK Excel文件选择
        uk_layout = QHBoxLayout()
        uk_label = QLabel(self.tr("plugin.comparison_variance_report.uk_file_label"))
        uk_label.setMinimumWidth(120)
        self.uk_file_input = QLineEdit()
        self.uk_file_input.setPlaceholderText(self.tr("plugin.comparison_variance_report.uk_file_placeholder"))
        self.uk_file_input.setText(self.uk_file_path)
        uk_browse_btn = QPushButton(self.tr("plugin.comparison_variance_report.choose_file"))
        uk_browse_btn.clicked.connect(self._browse_uk_file)
        
        uk_layout.addWidget(uk_label)
        uk_layout.addWidget(self.uk_file_input)
        uk_layout.addWidget(uk_browse_btn)
        file_layout.addLayout(uk_layout)
        
        # HK Excel文件选择
        hk_layout = QHBoxLayout()
        hk_label = QLabel(self.tr("plugin.comparison_variance_report.hk_file_label"))
        hk_label.setMinimumWidth(120)
        self.hk_file_input = QLineEdit()
        self.hk_file_input.setPlaceholderText(self.tr("plugin.comparison_variance_report.hk_file_placeholder"))
        self.hk_file_input.setText(self.hk_file_path)
        hk_browse_btn = QPushButton(self.tr("plugin.comparison_variance_report.choose_file"))
        hk_browse_btn.clicked.connect(self._browse_hk_file)
        
        hk_layout.addWidget(hk_label)
        hk_layout.addWidget(self.hk_file_input)
        hk_layout.addWidget(hk_browse_btn)
        file_layout.addLayout(hk_layout)
        
        # CSV文件选择
        csv_layout = QHBoxLayout()
        csv_label = QLabel(self.tr("plugin.comparison_variance_report.csv_file_label"))
        csv_label.setMinimumWidth(120)
        self.csv_file_input = QLineEdit()
        self.csv_file_input.setPlaceholderText(self.tr("plugin.comparison_variance_report.csv_file_placeholder"))
        self.csv_file_input.setText(self.csv_file_path)
        csv_browse_btn = QPushButton(self.tr("plugin.comparison_variance_report.choose_file"))
        csv_browse_btn.clicked.connect(self._browse_csv_file)
        
        csv_layout.addWidget(csv_label)
        csv_layout.addWidget(self.csv_file_input)
        csv_layout.addWidget(csv_browse_btn)
        file_layout.addLayout(csv_layout)
        
        layout.addWidget(file_group)
        
        # BigQuery SQL区域
        sql_group = QGroupBox(self.tr("plugin.comparison_variance_report.bigquery_group"))
        sql_layout = QVBoxLayout(sql_group)
        
        # SQL文本区域
        self.bigquery_text = QTextEdit()
        self.bigquery_text.setPlaceholderText(self.tr("plugin.comparison_variance_report.sql_placeholder"))
        self.bigquery_text.setMaximumHeight(200)
        sql_layout.addWidget(self.bigquery_text)
        
        # 生成SQL按钮
        generate_sql_btn = QPushButton(self.tr("plugin.comparison_variance_report.generate_sql"))
        generate_sql_btn.clicked.connect(self._generate_sql)
        generate_sql_btn.setStyleSheet(
            "QPushButton {"
            "    background-color: #28a745;"
            "    color: white;"
            "    border: none;"
            "    padding: 8px 16px;"
            "    border-radius: 4px;"
            "    font-weight: bold;"
            "}"
            "QPushButton:hover {"
            "    background-color: #218838;"
            "}"
        )
        sql_layout.addWidget(generate_sql_btn)
        
        layout.addWidget(sql_group)
        
        return widget
    
    def _create_log_and_report_widget(self) -> QWidget:
        """创建日志和报告生成区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 日志区域
        log_group = QGroupBox(self.tr("plugin.comparison_variance_report.log_group"))
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setPlaceholderText(self.tr("plugin.comparison_variance_report.log_placeholder"))
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        # 清空日志按钮
        clear_log_btn = QPushButton(self.tr("plugin.comparison_variance_report.clear_log"))
        clear_log_btn.clicked.connect(self._clear_log)
        log_layout.addWidget(clear_log_btn)
        
        layout.addWidget(log_group)
        
        # 报告生成区域
        report_group = QGroupBox(self.tr("plugin.comparison_variance_report.report_group"))
        report_layout = QVBoxLayout(report_group)
        
        # 报告格式说明（仅支持HTML）
        format_layout = QHBoxLayout()
        format_label = QLabel(self.tr("plugin.comparison_variance_report.report_format_label") + ": HTML")
        format_layout.addWidget(format_label)
        format_layout.addStretch()
        report_layout.addLayout(format_layout)
        
        # 生成报告按钮
        generate_report_btn = QPushButton(self.tr("plugin.comparison_variance_report.generate_report"))
        generate_report_btn.clicked.connect(self._generate_report)
        generate_report_btn.setStyleSheet(
            "QPushButton {"
            "    background-color: #007bff;"
            "    color: white;"
            "    border: none;"
            "    padding: 10px 20px;"
            "    border-radius: 4px;"
            "    font-weight: bold;"
            "    font-size: 14px;"
            "}"
            "QPushButton:hover {"
            "    background-color: #0056b3;"
            "}"
        )
        report_layout.addWidget(generate_report_btn)
        
        layout.addWidget(report_group)
        
        return widget
    
    def _browse_uk_file(self):
        """浏览UK Excel文件"""
        try:
            # 获取上次使用的目录
            last_dir = os.path.dirname(self.uk_file_path) if self.uk_file_path else os.path.expanduser("~")
            
            file_path, _ = QFileDialog.getOpenFileName(
                None,
                "选择UK Excel文件",
                last_dir,
                "Excel Files (*.xlsx *.xls);;All Files (*)"
            )
            
            if file_path:
                self.uk_file_path = file_path
                self.uk_file_input.setText(file_path)
                self.set_setting('last_uk_excel_path', file_path)
                self._add_log(f"{self.tr('plugin.comparison_variance_report.file_selection_prefix')} ✅ {self.tr('plugin.comparison_variance_report.file_selected', file_path=os.path.basename(file_path))}")
                self.log_info(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.uk_file_selected').format(file_path=file_path)}")
                
        except Exception as e:
            self.log_error(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.uk_file_selection_failed')}: {e} - {traceback.format_exc()}")
            self._add_log(f"{self.tr('plugin.comparison_variance_report.error_prefix')} {self.tr('plugin.comparison_variance_report.uk_file_selection_failed')}: {e}")
    
    def _browse_hk_file(self):
        """浏览HK Excel文件"""
        try:
            # 获取上次使用的目录
            last_dir = os.path.dirname(self.hk_file_path) if self.hk_file_path else os.path.expanduser("~")
            
            file_path, _ = QFileDialog.getOpenFileName(
                None,
                "Choose HK Excel",
                last_dir,
                "Excel Files (*.xlsx *.xls);;All Files (*)"
            )
            
            if file_path:
                self.hk_file_path = file_path
                self.hk_file_input.setText(file_path)
                self.set_setting('last_hk_excel_path', file_path)
                self._add_log(f"{self.tr('plugin.comparison_variance_report.file_selection_prefix')} ✅ {self.tr('plugin.comparison_variance_report.file_selected', file_path=os.path.basename(file_path))}")
                self.log_info(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.hk_file_selected').format(file_path=file_path)}")
                
        except Exception as e:
            self.log_error(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.hk_file_selection_failed')}: {e} - {traceback.format_exc()}")
            self._add_log(f"{self.tr('plugin.comparison_variance_report.error_prefix')} {self.tr('plugin.comparison_variance_report.hk_file_selection_failed')}: {e}")
    
    def _browse_csv_file(self):
        """浏览CSV文件"""
        try:
            # 获取上次使用的目录
            last_dir = os.path.dirname(self.csv_file_path) if self.csv_file_path else os.path.expanduser("~")
            
            file_path, _ = QFileDialog.getOpenFileName(
                None,
                "选择BigQuery结果CSV文件",
                last_dir,
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if file_path:
                self.csv_file_path = file_path
                self.csv_file_input.setText(file_path)
                self.set_setting('last_csv_path', file_path)
                self._add_log(f"{self.tr('plugin.comparison_variance_report.file_selection_prefix')} ✅ {self.tr('plugin.comparison_variance_report.file_selected', file_path=os.path.basename(file_path))}")
                self.log_info(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.csv_file_selected').format(file_path=file_path)}")
                
        except Exception as e:
            self.log_error(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.csv_file_selection_failed')}: {e} - {traceback.format_exc()}")
            self._add_log(f"{self.tr('plugin.comparison_variance_report.error_prefix')} {self.tr('plugin.comparison_variance_report.csv_file_selection_failed')}: {e}")
    
    def _generate_sql(self):
        """生成BigQuery SQL"""
        try:
            # 检查至少有一个文件存在
            uk_exists = self.uk_file_path and os.path.exists(self.uk_file_path)
            hk_exists = self.hk_file_path and os.path.exists(self.hk_file_path)
            
            if not uk_exists and not hk_exists:
                self._add_log(f"[ERROR] ❌ At least one Excel file (UK or HK) must be selected")
                return
            
            # 记录使用的文件
            if uk_exists and hk_exists:
                self._add_log(f"[SQL GENERATION] 📊 Using both UK and HK files to generate SQL")
            elif uk_exists:
                self._add_log(f"[SQL GENERATION] 📊 Using UK file only to generate SQL")
            else:
                self._add_log(f"[SQL GENERATION] 📊 Using HK file only to generate SQL")
            
            self._add_log(f"{self.tr('plugin.comparison_variance_report.sql_generation_prefix')} {self.tr('plugin.comparison_variance_report.sql_generation_start')}")
            self.log_info(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.sql_generation_begin')}")
            
            # 读取并验证Excel数据
            uk_data, hk_data = self._read_and_validate_excel_data(uk_exists, hk_exists)
            if (uk_exists and uk_data is None) or (hk_exists and hk_data is None):
                return
            
            # 提取SQL参数
            sql_params = self._extract_sql_parameters(uk_data, hk_data)
            if not sql_params:
                return
            
            # 生成SQL
            generated_sql = self._build_sql_query(sql_params)
            
            self.bigquery_text.setPlainText(generated_sql)
            self._add_log(f"{self.tr('plugin.comparison_variance_report.sql_generation_prefix')} ✅ {self.tr('plugin.comparison_variance_report.sql_generated')}")
            self.log_info(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.sql_generation_complete')}")
            
        except Exception as e:
            self.log_error(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.sql_generation_failed')}: {e} - {traceback.format_exc()}")
            self._add_log(f"{self.tr('plugin.comparison_variance_report.error_prefix')} {self.tr('plugin.comparison_variance_report.sql_generation_failed')}: {e}")

    def _read_and_validate_excel_data(self, uk_exists=True, hk_exists=True):
        """读取并验证Excel数据"""
        try:
            uk_data = None
            hk_data = None
            
            # 读取UK数据（如果存在）
            if uk_exists:
                self._add_log(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.excel_reading_uk')}")
                uk_data = pd.read_excel(self.uk_file_path)
                self.log_info(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.excel_read_success_uk', rows=len(uk_data))}")
            
            # 读取HK数据（如果存在）
            if hk_exists:
                self._add_log(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.excel_reading_hk')}")
                # 对于HK文件，读取"HK"工作表
                hk_data = pd.read_excel(self.hk_file_path, sheet_name='HK')
                self.log_info(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.excel_read_success_hk', rows=len(hk_data))}")
            
            # 验证必需的列
            required_columns = ['Reporting Date', 'Frequency', 'Record Type', 'Country', 'Variance']
            
            # 验证UK数据列（如果存在）
            if uk_exists and uk_data is not None:
                for col in required_columns:
                    if col not in uk_data.columns:
                        self._add_log(f"{self.tr('plugin.comparison_variance_report.error_prefix')} {self.tr('plugin.comparison_variance_report.missing_column_uk', column=col)}")
                        return None, None
            
            # 验证HK数据列（如果存在）
            if hk_exists and hk_data is not None:
                for col in required_columns:
                    if col not in hk_data.columns:
                        self._add_log(f"{self.tr('plugin.comparison_variance_report.error_prefix')} {self.tr('plugin.comparison_variance_report.missing_column_hk', column=col)}")
                        return None, None
            
            # 按照文档要求过滤数据
            uk_data_filtered = None
            hk_data_filtered = None
            
            # 过滤UK数据（如果存在）
            if uk_exists and uk_data is not None:
                # 1. 过滤Country不是GB或HK的行
                uk_data_filtered = uk_data[uk_data['Country'].isin(['GB', 'HK'])]
                # 2. 过滤Variance为"-", "0", None, ""的行
                variance_exclude = ['-', '0', None, '', 0]
                uk_data_filtered = uk_data_filtered[~uk_data_filtered['Variance'].isin(variance_exclude)]
            
            # 过滤HK数据（如果存在）
            if hk_exists and hk_data is not None:
                # 1. 过滤Country不是GB或HK的行
                hk_data_filtered = hk_data[hk_data['Country'].isin(['GB', 'HK'])]
                # 2. 过滤Variance为"-", "0", None, ""的行
                variance_exclude = ['-', '0', None, '', 0]
                hk_data_filtered = hk_data_filtered[~hk_data_filtered['Variance'].isin(variance_exclude)]
            
            uk_count = len(uk_data_filtered) if uk_data_filtered is not None else 0
            hk_count = len(hk_data_filtered) if hk_data_filtered is not None else 0
            self._add_log(f"{self.tr('plugin.comparison_variance_report.log_prefix')} Data Variance filter done - UK: {uk_count} lines, HK: {hk_count} lines")
            self._add_log(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.column_validation_passed')}")
            return uk_data_filtered, hk_data_filtered
            
        except Exception as e:
            self.log_error(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.excel_read_failed')}: {e} - {traceback.format_exc()}")
            self._add_log(f"{self.tr('plugin.comparison_variance_report.error_prefix')} {self.tr('plugin.comparison_variance_report.excel_read_failed')}: {e}")
            return None, None
    
    def _extract_sql_parameters(self, uk_data, hk_data):
        """从Excel数据中提取SQL参数"""
        try:
            self._add_log(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.extracting_sql_params')}")
            
            # 提取并验证Reporting Date
            all_dates = []
            if uk_data is not None:
                uk_dates = uk_data['Reporting Date'].dropna().unique()
                all_dates.extend(uk_dates)
            if hk_data is not None:
                hk_dates = hk_data['Reporting Date'].dropna().unique()
                all_dates.extend(hk_dates)
            
            # 检查所有日期是否一致
            unique_dates = list(set(all_dates))
            if len(unique_dates) != 1:
                self._add_log(f"{self.tr('plugin.comparison_variance_report.error_prefix')} {self.tr('plugin.comparison_variance_report.reporting_date_not_unique')}")
                return None
            
            reporting_date = unique_dates[0]
            # 确保日期格式为YYYY-MM-DD
            if hasattr(reporting_date, 'strftime'):
                # 如果是datetime对象，直接格式化
                reporting_date = reporting_date.strftime('%Y-%m-%d')
            else:
                # 如果是字符串，尝试解析后格式化
                try:
                    import datetime
                    if isinstance(reporting_date, str):
                        # 尝试多种日期格式解析
                        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y']:
                            try:
                                parsed_date = datetime.datetime.strptime(reporting_date, fmt)
                                reporting_date = parsed_date.strftime('%Y-%m-%d')
                                break
                            except ValueError:
                                continue
                        else:
                            # 如果所有格式都失败，保持原值
                            self._add_log(f"[ERROR] Unable to resolve date: {reporting_date}, please fix, process abort with {e}.")
                            return None
                except Exception as e:
                    self._add_log(f"[ERROR] Unable to resolve date: {reporting_date}, abort with {e}")
                    return None
            
            # 提取并验证freq
            all_freqs = []
            if uk_data is not None:
                uk_freq = uk_data['Frequency'].dropna().unique()
                all_freqs.extend(uk_freq)
            if hk_data is not None:
                hk_freq = hk_data['Frequency'].dropna().unique()
                all_freqs.extend(hk_freq)
            
            # 检查所有频率是否一致
            unique_freqs = list(set(all_freqs))
            if len(unique_freqs) != 1:
                self._add_log(f"{self.tr('plugin.comparison_variance_report.error_prefix')} {self.tr('plugin.comparison_variance_report.freq_not_unique')}")
                return None
            
            if unique_freqs[0].upper() != 'MONTHLY':
                self._add_log(f"{self.tr('plugin.comparison_variance_report.error_prefix')} {self.tr('plugin.comparison_variance_report.freq_not_monthly')}")
                return None
            
            freq = unique_freqs[0]
            
            # 提取Record Type并合并去重
            all_record_types = []
            if uk_data is not None:
                uk_record_types = uk_data['Record Type'].dropna().unique()
                all_record_types.extend(uk_record_types)
            if hk_data is not None:
                hk_record_types = hk_data['Record Type'].dropna().unique()
                all_record_types.extend(hk_record_types)
            
            # 合并并去重，转为大写
            combined_record_types = list(set(all_record_types))
            uniq_record_type_list = [str(rt).upper() for rt in combined_record_types]
            
            # 提取其他可能的字段（如果存在）
            additional_fields = {}
            
            # 提取必需的字段用于WHERE条件
            # 根据文档，需要提取Group Sub System ID, Source Table Name, Output Table Name
            required_fields = {
                'radar_group_sub_sys_id': 'Group Sub System ID',
                'table_name_source': 'Source Table Name', 
                'table_name_output': 'Output Table Name'
            }
            
            for sql_field, excel_col in required_fields.items():
                all_values = []
                col_exists = False
                
                if uk_data is not None and excel_col in uk_data.columns:
                    uk_values = uk_data[excel_col].dropna().unique()
                    all_values.extend(uk_values)
                    col_exists = True
                    
                if hk_data is not None and excel_col in hk_data.columns:
                    hk_values = hk_data[excel_col].dropna().unique()
                    all_values.extend(hk_values)
                    col_exists = True
                
                if col_exists:
                    combined_values = list(set(all_values))
                    additional_fields[sql_field] = [str(v) for v in combined_values]
            
            sql_params = {
                'reporting_date': reporting_date,
                'freq': freq,
                'uniq_record_type_list': uniq_record_type_list,
                'additional_fields': additional_fields
            }
            
            self._add_log(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.sql_params_extracted')}")
            self._add_log(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.reporting_date_info', date=reporting_date)}")
            self._add_log(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.frequency_info', freq=freq)}")
            self._add_log(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.record_types_info', count=len(uniq_record_type_list))}")
            
            return sql_params
            
        except Exception as e:
            self.log_error(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.sql_params_extract_failed')}: {e} - {traceback.format_exc()}")
            self._add_log(f"{self.tr('plugin.comparison_variance_report.error_prefix')} {self.tr('plugin.comparison_variance_report.sql_params_extract_failed')}: {e}")
            return None
    
    def _build_sql_query(self, sql_params):
        """构建SQL查询"""
        try:
            # 格式化Record Type列表 - 按照文档要求使用upper()函数
            record_type_list = "', '".join(sql_params['uniq_record_type_list'])
            record_type_clause = f"upper(('{record_type_list}'))"
            
            # 根据实际上传的文件动态生成国家代码过滤条件
            country_codes = []
            if self.uk_file_path and os.path.exists(self.uk_file_path):
                country_codes.append('GB')
            if self.hk_file_path and os.path.exists(self.hk_file_path):
                country_codes.append('HK')
            
            country_clause = "', '".join(country_codes)
            
            # 构建基础SQL
            sql_query = f"""SELECT
  reporting_date,
  file_freq,
  radar_country_code,
  radar_group_sys_id,
  radar_group_sub_sys_id,
  rule_action,
  table_name_source,
  col_source,
  source_col_rule,
  table_name_output,
  col_output,
  status,
  filter,
  stat, 
  check_type
  
FROM
  `hsbc-xxx-radar-prod.TABLE_NAME_REPORT_V01_00`
WHERE
  reporting_date = '{sql_params['reporting_date']}'  -- For example {sql_params['reporting_date']}
  AND radar_country_code in ('{country_clause}')
  AND file_freq = '{sql_params['freq']}'
  AND upper(record_type) in {record_type_clause}"""
            
            # 添加必需的字段条件
            required_fields = ['radar_group_sub_sys_id', 'table_name_source', 'table_name_output']
            for field_name in required_fields:
                if field_name in sql_params['additional_fields'] and sql_params['additional_fields'][field_name]:
                    field_values = sql_params['additional_fields'][field_name]
                    values_list = "', '".join(field_values)
                    values_clause = f"('{values_list}')"
                    sql_query += f"\n  AND {field_name} in {values_clause}"
            
            sql_query += ";"
            
            return sql_query
            
        except Exception as e:
            self.log_error(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.sql_build_failed')}: {e} - {traceback.format_exc()}")
            self._add_log(f"{self.tr('plugin.comparison_variance_report.error_prefix')} {self.tr('plugin.comparison_variance_report.sql_build_failed')}: {e}")
            return "-- Failed to Generate SQL, Please check log."

    def _generate_report(self):
        """生成报告"""
        try:
            # 验证必要文件
            if not self.csv_file_path or not os.path.exists(self.csv_file_path):
                self._add_log("[ERROR] ❌ GCP CSV file not selected or does not exist")
                return
            
            # 检查至少有一个Excel文件存在
            uk_exists = self.uk_file_path and os.path.exists(self.uk_file_path)
            hk_exists = self.hk_file_path and os.path.exists(self.hk_file_path)
            
            if not uk_exists and not hk_exists:
                self._add_log("[ERROR] ❌ At least one Excel file (UK or HK) must be selected and exist")
                return
            
            # 记录使用的文件
            if uk_exists and hk_exists:
                self._add_log("[INFO] 📁 Using both UK and HK Excel files")
            elif uk_exists:
                self._add_log("[INFO] 📁 Using UK Excel file only")
            else:
                self._add_log("[INFO] 📁 Using HK Excel file only")
            
            self._add_log("[REPORT] 🔄 Starting report generation process...")
            self.log_info(f"{self.tr('plugin.comparison_variance_report.log_prefix')} 📊 Starting report generation")
            
            # Step 1: Read and validate all data
            if not self._read_all_data(uk_exists, hk_exists):
                return
            
            # Step 2: Generate comparison CSV files
            if not self._generate_comparison_csvs():
                return
            
            # Step 3: Generate final HTML report
            if not self._generate_final_report():
                return
            
            self._add_log("[REPORT] ✅ Report generation completed successfully")
            self.log_info(f"{self.tr('plugin.comparison_variance_report.log_prefix')} ✅ Report generation completed")
            
        except Exception as e:
            self.log_error(f"{self.tr('plugin.comparison_variance_report.log_prefix')} ❌ Report generation failed: {e} - {traceback.format_exc()}")
            self._add_log(f"[ERROR] ❌ Report generation failed: {e}")
    
    def _read_all_data(self, uk_exists=True, hk_exists=True):
        """读取所有数据文件"""
        try:
            self._add_log("[DATA] 📖 Reading Excel files...")
            
            # 读取Excel数据
            self.uk_data, self.hk_data = self._read_and_validate_excel_data(uk_exists, hk_exists)
            if (uk_exists and self.uk_data is None) or (hk_exists and self.hk_data is None):
                self._add_log("[ERROR] ❌ Failed to read Excel files")
                return False
            
            # 读取GCP CSV数据
            self._add_log("[DATA] 📖 Reading GCP CSV file...")
            self.gcp_csv_data = self._read_gcp_csv_data()
            if self.gcp_csv_data is None:
                self._add_log("[ERROR] ❌ Failed to read GCP CSV file")
                return False
            
            uk_count = len(self.uk_data) if self.uk_data is not None else 0
            hk_count = len(self.hk_data) if self.hk_data is not None else 0
            self._add_log(f"[DATA] ✅ All data loaded successfully - UK: {uk_count} rows, HK: {hk_count} rows, GCP: {len(self.gcp_csv_data)} rows")
            return True
            
        except Exception as e:
            self.log_error(f"{self.tr('plugin.comparison_variance_report.log_prefix')} ❌ Failed to read data: {e} - {traceback.format_exc()}")
            self._add_log(f"[ERROR] ❌ Failed to read data: {e}")
            return False
    
    def _read_gcp_csv_data(self):
        """读取GCP CSV数据"""
        try:
            # 读取CSV文件，确保所有列都作为字符串读取
            gcp_data = pd.read_csv(self.csv_file_path, dtype=str)
            
            # 验证必需的列
            required_columns = [
                'reporting_date', 'radar_country_code', 'radar_group_sys_id',
                'radar_group_sub_sys_id', 'rule_action', 'table_name_source', 'source_col_rule',
                'table_name_output', 'col_output', 'status'
            ]
            
            missing_columns = [col for col in required_columns if col not in gcp_data.columns]
            if missing_columns:
                self._add_log(f"[ERROR] ❌ Missing required columns in GCP CSV: {missing_columns}")
                return None
            
            # 标准化status字段值 (TRUE/true -> 1, FALSE/false -> 0)
            def normalize_status(value):
                if pd.isna(value) or value is None:
                    return value
                str_val = str(value).strip().upper()
                if str_val in ['TRUE', '1', '1.0']:
                    return '1'
                elif str_val in ['FALSE', '0', '0.0']:
                    return '0'
                else:
                    return str(value)  # 保持原值
            
            gcp_data['status'] = gcp_data['status'].apply(normalize_status)
            self._add_log(f"[CSV] 🔄 Status values normalized: {gcp_data['status'].value_counts().to_dict()}")
            
            # 过滤只保留GB和HK的数据
            gcp_data_filtered = gcp_data[gcp_data['radar_country_code'].isin(['GB', 'HK'])]
            
            self._add_log(f"[DATA] ✅ GCP CSV data loaded - {len(gcp_data_filtered)} rows after filtering")
            return gcp_data_filtered
            
        except Exception as e:
            self.log_error(f"{self.tr('plugin.comparison_variance_report.log_prefix')} ❌ Failed to read GCP CSV: {e} - {traceback.format_exc()}")
            self._add_log(f"[ERROR] ❌ Failed to read GCP CSV: {e}")
            return None
    
    def _generate_comparison_csvs(self):
        """生成比较CSV文件"""
        try:
            self._add_log("[COMPARISON] 🔄 Starting data comparison process...")
            
            # 确保reports目录存在
            reports_dir = os.path.join(self._plugin_dir, 'reports')
            os.makedirs(reports_dir, exist_ok=True)
            
            # 获取当前时间戳
            timestamp = datetime.now().strftime('%Y%m%d%H')
            
            # 获取报告日期
            reporting_date = self._get_reporting_date()
            if not reporting_date:
                self._add_log("[ERROR] ❌ Could not determine reporting date")
                return False
            
            # 处理UK数据（如果存在）
            uk_success = True
            if self.uk_data is not None:
                self._add_log("[COMPARISON] 🔍 Processing UK data...")
                uk_success = self._process_country_data('GB', 'UK', reporting_date, timestamp, reports_dir)
            
            # 处理HK数据（如果存在）
            hk_success = True
            if self.hk_data is not None:
                self._add_log("[COMPARISON] 🔍 Processing HK data...")
                hk_success = self._process_country_data('HK', 'HK', reporting_date, timestamp, reports_dir)
            
            if uk_success and hk_success:
                self._add_log("[COMPARISON] ✅ All comparison CSV files generated successfully")
                return True
            else:
                self._add_log("[ERROR] ❌ Failed to generate some comparison CSV files")
                return False
                
        except Exception as e:
            self.log_error(f"{self.tr('plugin.comparison_variance_report.log_prefix')} ❌ Failed to generate comparison CSVs: {e} - {traceback.format_exc()}")
            self._add_log(f"[ERROR] ❌ Failed to generate comparison CSVs: {e}")
            return False
    
    def _get_reporting_date(self):
        """从数据中获取报告日期"""
        try:
            # 从UK数据中获取报告日期（如果存在）
            if self.uk_data is not None and 'Reporting Date' in self.uk_data.columns:
                uk_dates = self.uk_data['Reporting Date'].dropna().unique()
                if len(uk_dates) > 0:
                    date_val = uk_dates[0]
                    if hasattr(date_val, 'strftime'):
                        return date_val.strftime('%Y-%m-%d')
                    else:
                        # 尝试解析字符串日期
                        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y']:
                            try:
                                parsed_date = datetime.strptime(str(date_val), fmt)
                                return parsed_date.strftime('%Y-%m-%d')
                            except ValueError:
                                continue
            
            # 如果UK数据中没有找到日期，尝试从HK数据中获取
            if self.hk_data is not None and 'Reporting Date' in self.hk_data.columns:
                hk_dates = self.hk_data['Reporting Date'].dropna().unique()
                if len(hk_dates) > 0:
                    date_val = hk_dates[0]
                    if hasattr(date_val, 'strftime'):
                        return date_val.strftime('%Y-%m-%d')
                    else:
                        # 尝试解析字符串日期
                        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y']:
                            try:
                                parsed_date = datetime.strptime(str(date_val), fmt)
                                return parsed_date.strftime('%Y-%m-%d')
                            except ValueError:
                                continue
            
            return None
        except Exception as e:
            self.log_error(f"Failed to get reporting date: {e}")
            return None
    
    def _process_country_data(self, country_code, country_name, reporting_date, timestamp, reports_dir):
        """处理特定国家的数据"""
        try:
            # 选择对应国家的Excel数据
            if country_code == 'GB':
                if self.uk_data is None:
                    self._add_log(f"[WARNING] ⚠️ No UK data available")
                    return True  # 不算错误，只是没有数据
                excel_data = self.uk_data[self.uk_data['Country'] == 'GB'].copy()
            else:
                if self.hk_data is None:
                    self._add_log(f"[WARNING] ⚠️ No HK data available")
                    return True  # 不算错误，只是没有数据
                excel_data = self.hk_data[self.hk_data['Country'] == 'HK'].copy()
            
            if excel_data.empty:
                self._add_log(f"[WARNING] ⚠️ No {country_name} data found in Excel files")
                return True  # 不算错误，只是没有数据
            
            # 处理Status = 0和Status = 1的数据
            success_0 = self._process_status_data(excel_data, country_code, country_name, 0, reporting_date, timestamp, reports_dir)
            success_1 = self._process_status_data(excel_data, country_code, country_name, 1, reporting_date, timestamp, reports_dir)
            
            return success_0 and success_1
            
        except Exception as e:
            self.log_error(f"Failed to process {country_name} data: {e} - {traceback.format_exc()}")
            self._add_log(f"[ERROR] ❌ Failed to process {country_name} data: {e}")
            return False
    
    def _process_status_data(self, excel_data, country_code, country_name, status, reporting_date, timestamp, reports_dir):
        """处理特定状态的数据"""
        try:
            # 过滤Excel数据按状态
            excel_filtered = excel_data[excel_data['Status'].astype(str) == str(status)].copy()
            
            if excel_filtered.empty:
                self._add_log(f"[INFO] ℹ️ No {country_name} data with status = {status}")
                return True
            
            # 过滤GCP数据按国家和状态
            gcp_filtered = self.gcp_csv_data[
                (self.gcp_csv_data['radar_country_code'] == country_code) &
                (self.gcp_csv_data['status'].astype(str) == str(status))
            ].copy()
            
            self._add_log(f"[COMPARISON] 📊 Comparing {country_name} status={status}: Excel={len(excel_filtered)} rows, GCP={len(gcp_filtered)} rows")
            
            # 执行数据比较
            comparison_results = self._compare_data(excel_filtered, gcp_filtered, country_name, status)
            
            # 生成CSV文件
            csv_filename = f"CVR_{country_name}_{status}_{reporting_date}_{timestamp}.csv"
            csv_path = os.path.join(reports_dir, csv_filename)
            
            comparison_results.to_csv(csv_path, index=False)
            self._add_log(f"[CSV] 💾 Generated: {csv_filename} ({len(comparison_results)} rows)")
            
            return True
            
        except Exception as e:
            self.log_error(f"Failed to process {country_name} status {status} data: {e} - {traceback.format_exc()}")
            self._add_log(f"[ERROR] ❌ Failed to process {country_name} status {status} data: {e}")
            return False
    
    def _compare_data(self, excel_data, gcp_data, country_name, status):
        """比较Excel和GCP数据"""
        try:
            comparison_results = []
            
            # 定义匹配字段映射 (Excel列名 -> GCP列名)
            match_fields = {
                'Group System ID': 'radar_group_sys_id',
                'Group Sub System ID': 'radar_group_sub_sys_id', 
                'Record Type': 'record_type',
                'Rule Action': 'rule_action',
                'Source Table Name': 'table_name_source',
                'Source Column Name': 'col_source',
                'Source Column Rule': 'source_col_rule',
                'Output Table Name': 'table_name_output'
            }
            
            # 定义比较字段映射
            compare_fields = {
                'Country': 'radar_country_code',
                'Group System ID': 'radar_group_sys_id',
                'Group Sub System ID': 'radar_group_sub_sys_id',
                'Record Type': 'record_type', 
                'Rule Action': 'rule_action',
                'Source Table Name': 'table_name_source',
                'Source Column Rule': 'source_col_rule',
                'Output Table Name': 'table_name_output',
                'Output Column Rule': 'col_output',
                'Variance': 'variance',
                'Status': 'status'
            }
            
            matched_count = 0
            unmatched_excel_count = 0
            
            # 遍历Excel数据的每一行
            for excel_idx, excel_row in excel_data.iterrows():
                # 构建匹配条件
                match_conditions = []
                for excel_col, gcp_col in match_fields.items():
                    if excel_col in excel_data.columns and gcp_col in gcp_data.columns:
                        excel_val = str(excel_row[excel_col]).strip() if pd.notna(excel_row[excel_col]) else ''
                        match_conditions.append((gcp_col, excel_val))
                
                # 在GCP数据中查找匹配的行
                gcp_match = gcp_data.copy()
                for gcp_col, excel_val in match_conditions:
                    if gcp_col in gcp_match.columns:
                        gcp_match = gcp_match[gcp_match[gcp_col].astype(str).str.strip() == excel_val]
                
                if not gcp_match.empty:
                    # 找到匹配，比较所有字段
                    matched_count += 1
                    gcp_row = gcp_match.iloc[0]  # 取第一个匹配的行
                    
                    # 构建比较结果行
                    result_row = {}
                    
                    for excel_col, gcp_col in compare_fields.items():
                        if excel_col in excel_data.columns:
                            excel_val = str(excel_row[excel_col]).strip() if pd.notna(excel_row[excel_col]) else ''
                            result_row[excel_col] = excel_val
                            
                            if gcp_col in gcp_data.columns:
                                gcp_val = str(gcp_row[gcp_col]).strip() if pd.notna(gcp_row[gcp_col]) else ''
                                result_row[f'GCP_{excel_col}'] = gcp_val
                            else:
                                result_row[f'GCP_{excel_col}'] = 'N/A'
                    
                    comparison_results.append(result_row)
                    
                else:
                    # 未找到匹配
                    unmatched_excel_count += 1
                    
                    # 仍然记录Excel数据，GCP字段标记为未找到
                    result_row = {}
                    for excel_col, gcp_col in compare_fields.items():
                        if excel_col in excel_data.columns:
                            excel_val = str(excel_row[excel_col]).strip() if pd.notna(excel_row[excel_col]) else ''
                            result_row[excel_col] = excel_val
                            result_row[f'GCP_{excel_col}'] = 'NOT_FOUND'
                    
                    comparison_results.append(result_row)
            
            self._add_log(f"[COMPARISON] 📈 {country_name} status={status}: {matched_count} matched, {unmatched_excel_count} unmatched from Excel")
            
            # 转换为DataFrame
            if comparison_results:
                return pd.DataFrame(comparison_results)
            else:
                # 返回空的DataFrame但包含正确的列
                columns = []
                for excel_col in compare_fields.keys():
                    columns.append(excel_col)
                    columns.append(f'GCP_{excel_col}')
                return pd.DataFrame(columns=columns)
                
        except Exception as e:
            self.log_error(f"Failed to compare data for {country_name} status {status}: {e} - {traceback.format_exc()}")
            self._add_log(f"[ERROR] ❌ Failed to compare data for {country_name} status {status}: {e}")
            return pd.DataFrame()  # 返回空DataFrame
    
    def _generate_final_report(self, format_type=None):
        """生成最终报告（仅HTML格式）"""
        try:
            self._add_log("[REPORT] 📝 Generating HTML report...")
            
            # 获取报告日期和时间戳
            reporting_date = self._get_reporting_date()
            timestamp = datetime.now().strftime('%Y%m%d%H')
            
            # 弹出保存对话框 - 默认打开到reports目录
            reports_dir = os.path.join(self._plugin_dir, 'reports')
            os.makedirs(reports_dir, exist_ok=True)  # 确保目录存在
            default_path = os.path.join(reports_dir, f"CVR_{reporting_date}_{timestamp}.html")
            file_path, _ = QFileDialog.getSaveFileName(
                None,
                "Save Comparison Variance Report",
                default_path,
                "HTML Files (*.html)"
            )
            
            if not file_path:
                self._add_log("[INFO] ℹ️ User cancelled report save")
                return True  # 用户取消不算错误
            
            # 读取生成的CSV文件（只包含存在的国家数据）
            csv_files = {}
            if self.uk_data is not None:
                csv_files['UK_0'] = f"CVR_UK_0_{reporting_date}_{timestamp}.csv"
                csv_files['UK_1'] = f"CVR_UK_1_{reporting_date}_{timestamp}.csv"
            if self.hk_data is not None:
                csv_files['HK_0'] = f"CVR_HK_0_{reporting_date}_{timestamp}.csv"
                csv_files['HK_1'] = f"CVR_HK_1_{reporting_date}_{timestamp}.csv"
            
            # 生成HTML报告
            success = self._generate_html_report(file_path, csv_files, reports_dir, reporting_date)
            
            if success:
                self._add_log(f"[REPORT] ✅ Report saved to: {file_path}")
                return True
            else:
                self._add_log("[ERROR] ❌ Failed to generate report")
                return False
                
        except Exception as e:
            self.log_error(f"Failed to generate final report: {e} - {traceback.format_exc()}")
            self._add_log(f"[ERROR] ❌ Failed to generate final report: {e}")
            return False
    
    def _generate_html_report(self, file_path, csv_files, reports_dir, reporting_date):
        """生成HTML格式报告"""
        try:
            # 生成markdown内容
            markdown_content = f"""# Comparison Variance Report

**Report Date:** {reporting_date}  
**Generated At:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Author:** 🐷HSBC Little Worker

---

"""
            
            # 为每个国家和状态组合生成表格（只包含存在的国家数据）
            sections = []
            if self.uk_data is not None:
                sections.extend([
                    ('UK', 0, 'UK_0'),
                    ('UK', 1, 'UK_1')
                ])
            if self.hk_data is not None:
                sections.extend([
                    ('HK', 0, 'HK_0'),
                    ('HK', 1, 'HK_1')
                ])
            
            for country, status, file_key in sections:
                markdown_content += f"\n## {country}, Status = {status}\n\n"
                
                csv_file_path = os.path.join(reports_dir, csv_files[file_key])
                if os.path.exists(csv_file_path):
                    df = pd.read_csv(csv_file_path)
                    if not df.empty:
                        markdown_content += self._dataframe_to_markdown_table(df)
                    else:
                        markdown_content += "No data available for this section.\n\n"
                else:
                    markdown_content += "CSV file not found for this section.\n\n"
            
            # 转换markdown为HTML
            try:
                import markdown
                html_content = markdown.markdown(markdown_content, extensions=['tables'])
                
                # 添加CSS样式
                styled_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Comparison Variance Report - {reporting_date}</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        h1 {{ color: #2c3e50; text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; border-bottom: 2px solid #3498db; padding-bottom: 5px; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        tr:hover {{ background-color: #f5f5f5; }}
        hr {{ border: none; height: 2px; background-color: #3498db; margin: 20px 0; }}
        strong {{ color: #2c3e50; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>
"""
                
                # 写入HTML文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(styled_html)
                
            except ImportError:
                # 如果没有markdown库，记录错误并返回失败
                self._add_log("[ERROR] ❌ Markdown library not found, please install: pip install markdown")
                self.log_error("Markdown library is required for HTML report generation")
                return False
            
            return True
            
        except Exception as e:
            self.log_error(f"Failed to generate HTML report: {e} - {traceback.format_exc()}")
            return False
    
    def _dataframe_to_markdown_table(self, df):
        """将DataFrame转换为Markdown表格"""
        if df.empty:
            return "No data available.\n\n"
        
        # 生成表头
        headers = '| ' + ' | '.join(df.columns) + ' |\n'
        separator = '|' + '|'.join([' --- ' for _ in df.columns]) + '|\n'
        
        # 生成表格内容
        rows = ''
        for _, row in df.iterrows():
            row_data = []
            for col in df.columns:
                value = str(row[col]) if pd.notna(row[col]) else ''
                
                # 为差异数据添加标记
                if col.startswith('GCP_'):
                    original_col = col[4:]  # 移除'GCP_'前缀
                    if original_col in df.columns:
                        original_value = str(row[original_col]) if pd.notna(row[original_col]) else ''
                        if value == 'NOT_FOUND':
                            value = f"🔍 {value}"
                        elif value != original_value:
                            value = f"⚠️ {value}"
                        else:
                            value = f"✅ {value}"
                
                row_data.append(value)
            
            rows += '| ' + ' | '.join(row_data) + ' |\n'
        
        return headers + separator + rows + '\n'
    
    
    def _clear_log(self):
        """清空日志"""
        self.log_text.clear()
        self.log_info(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.log_cleared')}")
    
    def _add_log(self, message: str):
        """添加日志消息"""
        if self.log_text:
            self.log_text.append(message)
    
    def cleanup(self):
        """清理插件资源"""
        try:
            # 保存当前文件路径到配置
            if hasattr(self, 'uk_file_path'):
                self.set_setting('last_uk_excel_path', self.uk_file_path)
            if hasattr(self, 'hk_file_path'):
                self.set_setting('last_hk_excel_path', self.hk_file_path)
            if hasattr(self, 'csv_file_path'):
                self.set_setting('last_csv_path', self.csv_file_path)
            
            self.log_info(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.cleanup_complete')}")
            
        except Exception as e:
            self.log_error(f"{self.tr('plugin.comparison_variance_report.log_prefix')} ❌ Clean up failed: {e} - {traceback.format_exc()}")
    
    def on_language_changed(self):
        """语言变更时更新UI文本"""
        try:
            # 这里可以更新UI组件的文本
            # 由于组件在create_widget中创建，这里主要是为了保持一致性
            pass
        except Exception as e:
            self.log_error(f"{self.tr('plugin.comparison_variance_report.log_prefix')} {self.tr('plugin.comparison_variance_report.language_switch_failed')}: {e} - {traceback.format_exc()}")