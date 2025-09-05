from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QFileDialog, QScrollArea, QFrame, QProgressBar
)
from PySide6.QtCore import Qt, QThread, QTimer
from core.plugin_base import PluginBase
import os
import traceback
from datetime import datetime, timedelta
import pandas as pd
from .static_values import PVR_ORIGINAL_SQL, EXTRACT_TABLE_NAME_SQL, GET_BALANCE_SQL, GET_EXCEP_BALANCE_SQL, PVR_COL_MAPPINGS


class ReportGenerationThread(QThread):
    """Report generation worker thread"""
    def __init__(self, plugin_instance, csv_file_path):
        super().__init__()
        self.plugin = plugin_instance
        self.csv_file_path = csv_file_path
    
    def run(self):
        """Execute report generation in background thread"""
        try:
            self.plugin._generate_report_process(self.csv_file_path)
        except Exception as e:
            self.plugin.log_error(f"❌ [Report Generation] Thread execution failed: {e} - {traceback.format_exc()}")


class Plugin(PluginBase):
    # 插件元信息
    NAME = "period_variance_report"
    DISPLAY_NAME = "Period Variance Report"
    DESCRIPTION = "Period Variance Report, Semi-automated solution for monthly related user requests, protecting your eyes starts with you."
    VERSION = "1.0.0"
    AUTHOR = "Tearsyu"

    def __init__(self, app):
        super().__init__(app)
        self.sql_editor = None
        self.csv_file_path = ""
        self.log_viewer = None
        self.generate_button = None
        self.progress_bar = None
        self.worker_thread = None
        
    def initialize(self) -> bool:
        """Initialize plugin"""
        try:
            self.log_info("🚀 [PVR Plugin] Initialization started")
            
            # Load last CSV path from settings
            self.csv_file_path = self.get_setting("last_original_csv_path", "")
            
            self.log_info("✅ [PVR Plugin] Initialization completed")
            return True
        except Exception as e:
            self.log_error(f"❌ [PVR Plugin] Initialization failed: {e} - {traceback.format_exc()}")
            return False
    
    def create_widget(self) -> QWidget:
        """Create plugin UI widget"""
        # Main widget with scroll area
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Content widget inside scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        
        # 1. SQL Editor Section
        sql_section = self._create_sql_section()
        content_layout.addWidget(sql_section)
        
        # 2. File Chooser Section
        file_section = self._create_file_section()
        content_layout.addWidget(file_section)
        
        # 3. Log Viewer Section
        log_section = self._create_log_section()
        content_layout.addWidget(log_section)
        
        # 4. Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        content_layout.addWidget(self.progress_bar)
        
        # 5. Generate Report Button
        button_section = self._create_button_section()
        content_layout.addWidget(button_section)
        
        # Initialize button state based on CSV file selection
        self._update_generate_button_state()
        
        # Set content widget to scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        return main_widget
    
    def _create_sql_section(self) -> QWidget:
        """Create SQL editor section"""
        section = QFrame()
        section.setFrameStyle(QFrame.Box)
        layout = QVBoxLayout(section)
        
        # Title
        title = QLabel(self.tr("plugin.pvr.sql_editor_title"))
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        layout.addWidget(title)
        
        # SQL Editor
        self.sql_editor = QTextEdit()
        self.sql_editor.setMinimumHeight(200)
        self.sql_editor.setPlaceholderText(self.tr("plugin.pvr.sql_placeholder"))
        
        # Load default SQL template
        default_sql = self._get_default_sql_template()
        self.sql_editor.setPlainText(default_sql)
        
        layout.addWidget(self.sql_editor)
        
        return section
    
    def _create_file_section(self) -> QWidget:
        """Create file chooser section"""
        section = QFrame()
        section.setFrameStyle(QFrame.Box)
        layout = QVBoxLayout(section)
        
        # Title
        title = QLabel(self.tr("plugin.pvr.file_chooser_title"))
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        layout.addWidget(title)
        
        # File selection layout
        file_layout = QHBoxLayout()
        
        # File path display
        self.file_path_label = QLabel(self.csv_file_path or self.tr("plugin.pvr.no_file_selected"))
        self.file_path_label.setStyleSheet("padding: 8px; border: 1px solid #bdc3c7; border-radius: 4px; background-color: #ecf0f1;")
        file_layout.addWidget(self.file_path_label, 1)
        
        # Browse button
        browse_button = QPushButton(self.tr("plugin.pvr.browse_button"))
        browse_button.clicked.connect(self._browse_csv_file)
        browse_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        file_layout.addWidget(browse_button)
        
        layout.addLayout(file_layout)
        
        return section
    
    def _create_log_section(self) -> QWidget:
        """Create log viewer section"""
        section = QFrame()
        section.setFrameStyle(QFrame.Box)
        layout = QVBoxLayout(section)
        
        # Title
        title = QLabel(self.tr("plugin.pvr.log_viewer_title"))
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        layout.addWidget(title)
        
        # Log viewer
        self.log_viewer = QTextEdit()
        self.log_viewer.setMinimumHeight(300)
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                border: 1px solid #34495e;
                border-radius: 4px;
            }
        """)
        
        # Add initial message
        self.log_viewer.append(self.tr("plugin.pvr.log_initial_message"))
        
        layout.addWidget(self.log_viewer)
        
        return section
    
    def _create_button_section(self) -> QWidget:
        """Create button section"""
        section = QWidget()
        layout = QHBoxLayout(section)
        layout.addStretch()
        
        # Generate Report Button
        self.generate_button = QPushButton(self.tr("plugin.pvr.generate_button"))
        self.generate_button.clicked.connect(self._on_generate_report)
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                color: #7f8c8d;
            }
        """)
        
        layout.addWidget(self.generate_button)
        layout.addStretch()
        
        return section
    
    def _get_default_sql_template(self) -> str:
        """Get default SQL template with date placeholders"""
        # Calculate last month and prior month dates
        today = datetime.now()
        last_month = today.replace(day=1) - timedelta(days=1)
        prior_month = (last_month.replace(day=1) - timedelta(days=1))
        
        last_month_date = last_month.strftime('%Y-%m-%d')
        prior_month_date = prior_month.strftime('%Y-%m-%d')
        
        # Use SQL template from static_values.py and replace date placeholders
        return PVR_ORIGINAL_SQL.format(
            last_month_date=last_month_date,
            prior_month_date=prior_month_date
        )
    
    def _browse_csv_file(self):
        """Open file dialog to select CSV file"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                None,
                self.tr("plugin.pvr.select_csv_file"),
                self.csv_file_path or os.path.expanduser("~"),
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if file_path:
                self.csv_file_path = file_path
                self.file_path_label.setText(file_path)
                
                # Save to settings
                self.set_setting("last_original_csv_path", file_path)
                
                # Update generate button state
                self._update_generate_button_state()
                
                self._append_log(f"📁 [File Selection] Selected CSV file: {os.path.basename(file_path)}")
                
        except Exception as e:
            self.log_error(f"❌ [File Selection] Failed to select file: {e} - {traceback.format_exc()}")
            self._append_log(f"❌ [File Selection] Error: {str(e)}")
    
    def _update_generate_button_state(self):
        """Update generate button state based on CSV file selection"""
        if self.generate_button:
            has_valid_file = bool(self.csv_file_path and os.path.exists(self.csv_file_path))
            self.generate_button.setEnabled(has_valid_file)
            
            if has_valid_file:
                self._append_log(f"✅ [Button State] Generate button activated - CSV file ready")
            else:
                self._append_log(f"⚠️ [Button State] Generate button deactivated - No valid CSV file selected")
    
    def _on_generate_report(self):
        """Handle generate report button click"""
        try:
            # Validate inputs
            if not self.csv_file_path or not os.path.exists(self.csv_file_path):
                self._append_log("⚠️ [Validation] Please select a valid CSV file first")
                self.show_status_message(self.tr("plugin.pvr.error_no_file"))
                return
            
            sql_content = self.sql_editor.toPlainText().strip()
            if not sql_content:
                self._append_log("⚠️ [Validation] Please enter SQL query")
                self.show_status_message(self.tr("plugin.pvr.error_no_sql"))
                return
            
            # Disable button and show progress
            self.generate_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
            self._append_log("🚀 [Report Generation] Starting report generation process...")
            self._append_log("="*60)
            
            # Start worker thread
            self.worker_thread = ReportGenerationThread(self, self.csv_file_path)
            self.worker_thread.finished.connect(self._on_generation_finished)
            self.worker_thread.start()
            
        except Exception as e:
            self.log_error(f"❌ [Report Generation] Failed to start: {e} - {traceback.format_exc()}")
            self._append_log(f"❌ [Report Generation] Error: {str(e)}")
            self._on_generation_finished()
    
    def _generate_report_process(self, csv_file_path: str):
        """Main report generation process (runs in worker thread)"""
        try:
            # Step 1: Load and validate CSV file
            self._append_log("📊 [Data Loading] Loading CSV file...")
            df = pd.read_csv(csv_file_path)
            self._append_log(f"✅ [Data Loading] Loaded {len(df)} rows from CSV file")
            
            # Step 2: Filter data
            self._append_log("🔍 [Data Filtering] Applying filters...")
            original_count = len(df)
            
            # Convert all data to string type
            df = df.astype(str)
            
            # Apply filters (simulated)
            filtered_df = self._apply_data_filters(df)
            filtered_count = len(filtered_df)
            
            self._append_log(f"📈 [Data Filtering] Filtered from {original_count} to {filtered_count} rows")
            self._append_log("="*60)
            
            # Step 3: Add column_name mapping (Process step 6)
            self._append_log("🏷️ [Column Mapping] Adding column_name based on Col_output mapping...")
            if 'Col_output' in filtered_df.columns:
                filtered_df['column_name'] = filtered_df['Col_output'].apply(self._get_column_name_mapping)
                mapped_count = filtered_df['column_name'].notna().sum()
                self._append_log(f"✅ [Column Mapping] Successfully mapped {mapped_count} column names")
            else:
                self._append_log("⚠️ [Column Mapping] Column 'Col_output' not found, adding default column_name")
                filtered_df['column_name'] = 'UNKNOWN_COLUMN'
            
            # Step 4: Process each row for table_name and balance
            self._append_log(f"⚙️ [Data Processing] Processing {filtered_count} rows for table_name and balance...")
            
            # Initialize new columns
            filtered_df['table_name'] = ''
            filtered_df['balance'] = 0.0
            
            for idx, (index, row) in enumerate(filtered_df.iterrows()):
                table_name, balance = self._process_single_row(idx + 1, row, filtered_count)
                
                # Update the dataframe with results
                filtered_df.at[index, 'table_name'] = table_name
                filtered_df.at[index, 'balance'] = balance
                
                # Add separator between rows
                if idx < len(filtered_df) - 1:
                    self._append_log("-" * 40)
            
            # Step 4: Save report
            self._append_log("="*60)
            self._save_final_report(filtered_df)
            
            self._append_log("🎉 [Report Generation] Process completed successfully!")
            
        except Exception as e:
            self.log_error(f"❌ [Report Generation] Process failed: {e} - {traceback.format_exc()}")
            self._append_log(f"❌ [Report Generation] Process failed: {str(e)}")
    
    def _apply_data_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply data filtering rules according to Process step 5"""
        original_count = len(df)
        self._append_log(f"📊 [FILTER] Starting with {original_count} rows")
        
        # Step 5.1: Remove rows with radar_country_code in ['GB', 'CA', 'HK', 'HS']
        self._append_log("🔸 [FILTER] Removing rows with radar_country_code in ['GB', 'CA', 'HK', 'HS']")
        if 'radar_country_code' in df.columns:
            before_count = len(df)
            df = df[~df['radar_country_code'].isin(['GB', 'CA', 'HK', 'HS'])]
            removed_count = before_count - len(df)
            self._append_log(f"📉 [FILTER] Removed {removed_count} rows with excluded country codes")
        else:
            self._append_log("⚠️ [FILTER] Column 'radar_country_code' not found, skipping country filter")
        
        # Step 5.2: Keep only rows with file_freq = 'Monthly'
        self._append_log("🔸 [FILTER] Keeping only rows with file_freq = 'MONTHLY'")
        if 'file_freq' in df.columns:
            before_count = len(df)
            df = df[df['file_freq'].str.upper() == 'MONTHLY']
            removed_count = before_count - len(df)
            self._append_log(f"📉 [FILTER] Removed {removed_count} rows with non-Monthly frequency")
        else:
            self._append_log("⚠️ [FILTER] Column 'file_freq' not found, skipping frequency filter")
        
        # Step 5.3: Keep only rows with breach_value = 'Breach'
        self._append_log("🔸 [FILTER] Keeping only rows with breach_value = 'Breach'")
        if 'breach_value' in df.columns:
            before_count = len(df)
            df = df[df['breach_value'] == 'Breach']
            removed_count = before_count - len(df)
            self._append_log(f"📉 [FILTER] Removed {removed_count} rows with non-Breach values")
        else:
            self._append_log("⚠️ [FILTER] Column 'breach_value' not found, skipping breach filter")
        
        final_count = len(df)
        self._append_log(f"✅ [FILTER] Filtering completed: {original_count} → {final_count} rows ({original_count - final_count} removed)")
        
        return df
    
    def _process_single_row(self, row_num: int, row: pd.Series, total_rows: int) -> tuple:
        """Process a single row and return table_name and balance"""
        self._append_log(f"🔄 [Row {row_num}/{total_rows}] Processing row...")
        
        # Get column_name from the row (already mapped)
        column_name = row.get('column_name', 'UNKNOWN_COLUMN')
        self._append_log(f"🏷️ [Row {row_num}] Using column_name: {column_name}")
        
        # Extract table name
        radar_country = row.get('radar_country_code', 'unknown')
        radar_group = row.get('radar_group_sys_id', 'unknown')
        reporting_date = row.get('reporting_date', 'unknown')
        
        self._append_log(f"🔍 [Row {row_num}] Extracting table_name for country: {radar_country}, group: {radar_group}, date: {reporting_date}")
        
        # Execute SQL for table name
        table_name = self._execute_table_name_query(radar_country, radar_group, column_name, reporting_date)
        self._append_log(f"🗃️ [Row {row_num}] Found table_name: {table_name}")
        
        # Calculate balance
        balance = self._calculate_balance(table_name, column_name)
        self._append_log(f"💰 [Row {row_num}] Calculated balance: {balance}")
        
        self._append_log(f"✅ [Row {row_num}] Row processing completed")
        
        return table_name, balance
    
    def _get_column_name_mapping(self, col_output: str) -> str:
        """Get column name mapping from static_values"""
        return PVR_COL_MAPPINGS.get(col_output, f'MAPPED_{col_output}')
    
    def _execute_table_name_query(self, country_code: str, group_id: str, column_name: str, reporting_date: str) -> str:
        """Execute table name extraction query (simulated)"""
        # Use SQL template from static_values.py
        column_name_letter = column_name[0].lower() if column_name else 'x'
        
        # Simulate BigQuery execution using the template
        query = EXTRACT_TABLE_NAME_SQL.format(
            radar_country_code=country_code,
            reporting_date=reporting_date,
            radar_group_sys_id=group_id,
            column_name_letter=column_name_letter
        )
        
        self._append_log(f"🔍 [BigQuery] EXTRACT_TABLE_NAME_SQL: {query}")
        
        # Simulate table name result
        table_names = [
            f'mif_{column_name_letter}_table_{country_code.lower()}',
            f'datahub_table_{group_id}_{column_name}',
            f'reporting_table_{country_code}_{column_name[:3]}'
        ]
        table_name = table_names[hash(f'{country_code}{group_id}{column_name}') % len(table_names)]
        self._append_log(f"📊 [BigQuery] Query result: {table_name}")
        
        return table_name
    
    def _calculate_balance(self, table_name: str, column_name: str) -> float:
        """Calculate balance value (simulated)"""
        # Use SQL templates from static_values.py
        balance_query = GET_BALANCE_SQL.format(
            column_name=column_name,
            table_name=table_name
        )
        
        excep_balance_query = GET_EXCEP_BALANCE_SQL.format(
            column_name=column_name,
            table_name=table_name
        )
        
        # Simulate balance calculation
        self._append_log(f"🔍 [BigQuery] GET_BALANCE_SQL: {balance_query}")
        
        # Simulate balance result
        import random
        balance = round(random.uniform(1000, 1000000), 2)
        self._append_log(f"📊 [BigQuery] Balance result: {balance}")
        
        # Also simulate exception balance query
        self._append_log(f"🔍 [BigQuery] GET_EXCEP_BALANCE_SQL: {excep_balance_query}")
        
        return balance
    
    def _save_final_report(self, df: pd.DataFrame):
        """Save final report (simulated)"""
        try:
            # Get report save path
            report_path = self.get_setting("report_save_path", "reports")
            
            # Create reports directory if it doesn't exist
            if not os.path.isabs(report_path):
                # If relative path, make it relative to plugin directory
                plugin_dir = os.path.dirname(os.path.abspath(__file__))
                report_path = os.path.join(plugin_dir, report_path)
            
            os.makedirs(report_path, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"period_variance_report_{timestamp}.csv"
            full_path = os.path.join(report_path, filename)
            
            # Save processed dataframe (already contains column_name, table_name, balance)
            df.to_csv(full_path, index=False)
            
            # Log column summary
            columns_added = ['column_name', 'table_name', 'balance']
            self._append_log(f"📊 [Report Save] Added columns: {', '.join(columns_added)}")
            self._append_log(f"📈 [Report Save] Total columns in report: {len(df.columns)}")
            self._append_log(f"📋 [Report Save] Final report contains {len(df)} rows")
            
            self._append_log(f"💾 [Report Save] Report saved to: {full_path}")
            self._append_log(f"📁 [Report Save] File: {filename}")
            
        except Exception as e:
            self.log_error(f"❌ [Report Save] Failed to save report: {e} - {traceback.format_exc()}")
            self._append_log(f"❌ [Report Save] Error: {str(e)}")
    
    def _on_generation_finished(self):
        """Handle generation completion"""
        # Re-enable button and hide progress
        self.generate_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Clean up worker thread
        if self.worker_thread:
            self.worker_thread.deleteLater()
            self.worker_thread = None
    
    def _append_log(self, message: str):
        """Append message to log viewer"""
        if self.log_viewer:
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            self.log_viewer.append(formatted_message)
            
            # Auto-scroll to bottom
            scrollbar = self.log_viewer.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def cleanup(self) -> None:
        """Clean up plugin resources"""
        try:
            # Stop worker thread if running
            if self.worker_thread and self.worker_thread.isRunning():
                self.worker_thread.quit()
                self.worker_thread.wait(5000)  # Wait up to 5 seconds
            
            self.log_info("🧹 [PVR Plugin] Cleanup completed")
        except Exception as e:
            self.log_error(f"❌ [PVR Plugin] Cleanup failed: {e} - {traceback.format_exc()}")