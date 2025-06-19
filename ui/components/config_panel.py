from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QPushButton,
    QSpinBox,
    QFileDialog,
    QFrame,
    QListWidget,
)
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from ..styles.theme import (
    get_tab_style,
    get_input_style,
    get_combobox_style,
    get_checkbox_style,
    get_gradient_button_style,
    get_groupbox_style,
)
from utils.config_manager import AppConfig
import logging

logger = logging.getLogger(__name__)


class ConfigPanel(QWidget):
    """Configuration Panel with 3 tabs: SharePoint/Database/Advanced"""

    # Signals
    config_changed = pyqtSignal(object)  # AppConfig object
    test_sharepoint_requested = pyqtSignal()
    test_database_requested = pyqtSignal()
    refresh_sites_requested = pyqtSignal()
    refresh_lists_requested = pyqtSignal()
    refresh_databases_requested = pyqtSignal()
    refresh_tables_requested = pyqtSignal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.config = AppConfig()
        self.setup_ui()

    def setup_ui(self):
        """ตั้งค่า UI หลัก"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Tab Widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(get_tab_style())

        # Create tabs
        self.create_sharepoint_tab()
        self.create_database_tab()
        self.create_advanced_tab()

        # Add tabs
        self.tab_widget.addTab(self.sharepoint_tab, "📡 SharePoint")
        self.tab_widget.addTab(self.database_tab, "🗄️ Database")
        self.tab_widget.addTab(self.advanced_tab, "⚙️ Advanced")

        layout.addWidget(self.tab_widget)

        # Action buttons
        self.create_action_buttons(layout)

    def create_sharepoint_tab(self):
        """สร้าง SharePoint Configuration Tab"""
        self.sharepoint_tab = QWidget()
        layout = QVBoxLayout(self.sharepoint_tab)

        # Authentication Group
        auth_group = QGroupBox("Authentication")
        auth_group.setStyleSheet(get_groupbox_style())
        auth_layout = QFormLayout(auth_group)

        # Tenant ID
        self.tenant_id_input = QLineEdit()
        self.tenant_id_input.setStyleSheet(get_input_style())
        self.tenant_id_input.setPlaceholderText("xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        auth_layout.addRow("Tenant ID:", self.tenant_id_input)

        # Client ID
        self.client_id_input = QLineEdit()
        self.client_id_input.setStyleSheet(get_input_style())
        self.client_id_input.setPlaceholderText("Application (client) ID")
        auth_layout.addRow("Client ID:", self.client_id_input)

        # Client Secret
        self.client_secret_input = QLineEdit()
        self.client_secret_input.setStyleSheet(get_input_style())
        self.client_secret_input.setEchoMode(QLineEdit.Password)
        self.client_secret_input.setPlaceholderText("Client secret value")
        auth_layout.addRow("Client Secret:", self.client_secret_input)

        layout.addWidget(auth_group)

        # Site & List Group
        site_group = QGroupBox("Site & List Configuration")
        site_group.setStyleSheet(get_groupbox_style())
        site_layout = QFormLayout(site_group)

        # Site URL
        site_url_layout = QHBoxLayout()
        self.site_url_input = QLineEdit()
        self.site_url_input.setStyleSheet(get_input_style())
        self.site_url_input.setPlaceholderText(
            "https://yourcompany.sharepoint.com/sites/sitename"
        )

        self.refresh_sites_btn = QPushButton("🔄")
        self.refresh_sites_btn.setStyleSheet(
            get_gradient_button_style("#2196F3", "#1976D2", "small")
        )
        self.refresh_sites_btn.setMaximumWidth(40)
        self.refresh_sites_btn.clicked.connect(self.refresh_sites_requested.emit)

        site_url_layout.addWidget(self.site_url_input)
        site_url_layout.addWidget(self.refresh_sites_btn)
        site_layout.addRow("Site URL:", site_url_layout)

        # Available Sites (if any)
        self.sites_list = QListWidget()
        self.sites_list.setMaximumHeight(80)
        self.sites_list.setVisible(False)
        site_layout.addRow("Available Sites:", self.sites_list)

        # List Name
        list_layout = QHBoxLayout()
        self.list_name_combo = QComboBox()
        self.list_name_combo.setStyleSheet(get_combobox_style())
        self.list_name_combo.setEditable(True)
        self.list_name_combo.setPlaceholderText(
            "Enter list name or select from dropdown"
        )

        self.refresh_lists_btn = QPushButton("🔄")
        self.refresh_lists_btn.setStyleSheet(
            get_gradient_button_style("#2196F3", "#1976D2", "small")
        )
        self.refresh_lists_btn.setMaximumWidth(40)
        self.refresh_lists_btn.clicked.connect(self.refresh_lists_requested.emit)

        list_layout.addWidget(self.list_name_combo)
        list_layout.addWidget(self.refresh_lists_btn)
        site_layout.addRow("List Name:", list_layout)

        layout.addWidget(site_group)

        # Options Group
        options_group = QGroupBox("Options")
        options_group.setStyleSheet(get_groupbox_style())
        options_layout = QFormLayout(options_group)

        self.use_graph_api_check = QCheckBox("Use Microsoft Graph API")
        self.use_graph_api_check.setStyleSheet(get_checkbox_style())
        options_layout.addRow("", self.use_graph_api_check)

        layout.addWidget(options_group)

        # Test Connection
        test_layout = QHBoxLayout()
        self.test_sp_btn = QPushButton("🔍 Test SharePoint Connection")
        self.test_sp_btn.setStyleSheet(get_gradient_button_style("#4CAF50", "#388E3C"))
        self.test_sp_btn.clicked.connect(self.test_sharepoint_requested.emit)
        test_layout.addWidget(self.test_sp_btn)
        test_layout.addStretch()

        layout.addLayout(test_layout)
        layout.addStretch()

    def create_database_tab(self):
        """สร้าง Database Configuration Tab"""
        self.database_tab = QWidget()
        layout = QVBoxLayout(self.database_tab)

        # Database Type Selection
        type_group = QGroupBox("Database Type")
        type_group.setStyleSheet(get_groupbox_style())
        type_layout = QVBoxLayout(type_group)

        self.db_type_combo = QComboBox()
        self.db_type_combo.setStyleSheet(get_combobox_style())
        self.db_type_combo.addItems(["sqlserver", "sqlite", "mysql", "postgresql"])
        self.db_type_combo.currentTextChanged.connect(self._on_db_type_changed)
        type_layout.addWidget(self.db_type_combo)

        layout.addWidget(type_group)

        # SQL Server Configuration
        self.sqlserver_group = QGroupBox("SQL Server Configuration")
        self.sqlserver_group.setStyleSheet(get_groupbox_style())
        sqlserver_layout = QFormLayout(self.sqlserver_group)

        # Server
        self.sql_server_input = QLineEdit()
        self.sql_server_input.setStyleSheet(get_input_style())
        self.sql_server_input.setPlaceholderText("server.database.windows.net")
        sqlserver_layout.addRow("Server:", self.sql_server_input)

        # Database
        db_layout = QHBoxLayout()
        self.sql_database_combo = QComboBox()
        self.sql_database_combo.setStyleSheet(get_combobox_style())
        self.sql_database_combo.setEditable(True)

        self.refresh_db_btn = QPushButton("🔄")
        self.refresh_db_btn.setStyleSheet(
            get_gradient_button_style("#2196F3", "#1976D2", "small")
        )
        self.refresh_db_btn.setMaximumWidth(40)
        self.refresh_db_btn.clicked.connect(self.refresh_databases_requested.emit)

        db_layout.addWidget(self.sql_database_combo)
        db_layout.addWidget(self.refresh_db_btn)
        sqlserver_layout.addRow("Database:", db_layout)

        # Username
        self.sql_username_input = QLineEdit()
        self.sql_username_input.setStyleSheet(get_input_style())
        sqlserver_layout.addRow("Username:", self.sql_username_input)

        # Password
        self.sql_password_input = QLineEdit()
        self.sql_password_input.setStyleSheet(get_input_style())
        self.sql_password_input.setEchoMode(QLineEdit.Password)
        sqlserver_layout.addRow("Password:", self.sql_password_input)

        # Table
        table_layout = QHBoxLayout()
        self.sql_table_combo = QComboBox()
        self.sql_table_combo.setStyleSheet(get_combobox_style())
        self.sql_table_combo.setEditable(True)

        self.refresh_tables_btn = QPushButton("🔄")
        self.refresh_tables_btn.setStyleSheet(
            get_gradient_button_style("#2196F3", "#1976D2", "small")
        )
        self.refresh_tables_btn.setMaximumWidth(40)
        self.refresh_tables_btn.clicked.connect(self.refresh_tables_requested.emit)

        table_layout.addWidget(self.sql_table_combo)
        table_layout.addWidget(self.refresh_tables_btn)
        sqlserver_layout.addRow("Table:", table_layout)

        # Options
        self.sql_create_table_check = QCheckBox("Auto-create table if not exists")
        self.sql_create_table_check.setStyleSheet(get_checkbox_style())
        self.sql_create_table_check.setChecked(True)
        sqlserver_layout.addRow("", self.sql_create_table_check)

        self.sql_truncate_check = QCheckBox("Truncate table before insert")
        self.sql_truncate_check.setStyleSheet(get_checkbox_style())
        sqlserver_layout.addRow("", self.sql_truncate_check)

        layout.addWidget(self.sqlserver_group)

        # SQLite Configuration
        self.sqlite_group = QGroupBox("SQLite Configuration")
        self.sqlite_group.setStyleSheet(get_groupbox_style())
        sqlite_layout = QFormLayout(self.sqlite_group)

        # File Path
        file_layout = QHBoxLayout()
        self.sqlite_file_input = QLineEdit()
        self.sqlite_file_input.setStyleSheet(get_input_style())
        self.sqlite_file_input.setPlaceholderText("data.db")

        self.browse_file_btn = QPushButton("📁")
        self.browse_file_btn.setStyleSheet(
            get_gradient_button_style("#FF9800", "#F57C00", "small")
        )
        self.browse_file_btn.setMaximumWidth(40)
        self.browse_file_btn.clicked.connect(self._browse_sqlite_file)

        file_layout.addWidget(self.sqlite_file_input)
        file_layout.addWidget(self.browse_file_btn)
        sqlite_layout.addRow("Database File:", file_layout)

        # Table Name
        self.sqlite_table_input = QLineEdit()
        self.sqlite_table_input.setStyleSheet(get_input_style())
        self.sqlite_table_input.setPlaceholderText("sharepoint_data")
        sqlite_layout.addRow("Table Name:", self.sqlite_table_input)

        # Options
        self.sqlite_create_table_check = QCheckBox("Auto-create table if not exists")
        self.sqlite_create_table_check.setStyleSheet(get_checkbox_style())
        self.sqlite_create_table_check.setChecked(True)
        sqlite_layout.addRow("", self.sqlite_create_table_check)

        layout.addWidget(self.sqlite_group)

        # Test Connection
        test_layout = QHBoxLayout()
        self.test_db_btn = QPushButton("🔍 Test Database Connection")
        self.test_db_btn.setStyleSheet(get_gradient_button_style("#4CAF50", "#388E3C"))
        self.test_db_btn.clicked.connect(self.test_database_requested.emit)
        test_layout.addWidget(self.test_db_btn)
        test_layout.addStretch()

        layout.addLayout(test_layout)
        layout.addStretch()

        # Initially show SQL Server
        self._on_db_type_changed("sqlserver")

    def create_advanced_tab(self):
        """สร้าง Advanced Configuration Tab"""
        self.advanced_tab = QWidget()
        layout = QVBoxLayout(self.advanced_tab)

        # Sync Settings Group
        sync_group = QGroupBox("Sync Settings")
        sync_group.setStyleSheet(get_groupbox_style())
        sync_layout = QFormLayout(sync_group)

        # Sync Interval
        self.sync_interval_spin = QSpinBox()
        self.sync_interval_spin.setMinimum(60)
        self.sync_interval_spin.setMaximum(86400)  # 24 hours
        self.sync_interval_spin.setValue(3600)
        self.sync_interval_spin.setSuffix(" seconds")
        sync_layout.addRow("Auto-sync Interval:", self.sync_interval_spin)

        # Sync Mode
        self.sync_mode_combo = QComboBox()
        self.sync_mode_combo.setStyleSheet(get_combobox_style())
        self.sync_mode_combo.addItems(["full", "incremental"])
        sync_layout.addRow("Sync Mode:", self.sync_mode_combo)

        # Batch Size
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setMinimum(100)
        self.batch_size_spin.setMaximum(10000)
        self.batch_size_spin.setValue(1000)
        self.batch_size_spin.setSuffix(" records")
        sync_layout.addRow("Batch Size:", self.batch_size_spin)

        layout.addWidget(sync_group)

        # Performance Settings Group
        perf_group = QGroupBox("Performance Settings")
        perf_group.setStyleSheet(get_groupbox_style())
        perf_layout = QFormLayout(perf_group)

        # Connection Timeout
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setMinimum(10)
        self.timeout_spin.setMaximum(300)
        self.timeout_spin.setValue(30)
        self.timeout_spin.setSuffix(" seconds")
        perf_layout.addRow("Connection Timeout:", self.timeout_spin)

        # Max Retries
        self.retries_spin = QSpinBox()
        self.retries_spin.setMinimum(1)
        self.retries_spin.setMaximum(10)
        self.retries_spin.setValue(3)
        perf_layout.addRow("Max Retries:", self.retries_spin)

        # Parallel Processing
        self.parallel_check = QCheckBox("Enable parallel processing")
        self.parallel_check.setStyleSheet(get_checkbox_style())
        perf_layout.addRow("", self.parallel_check)

        layout.addWidget(perf_group)

        # Logging Settings Group
        log_group = QGroupBox("Logging Settings")
        log_group.setStyleSheet(get_groupbox_style())
        log_layout = QFormLayout(log_group)

        # Log Level
        self.log_level_combo = QComboBox()
        self.log_level_combo.setStyleSheet(get_combobox_style())
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        log_layout.addRow("Log Level:", self.log_level_combo)

        layout.addWidget(log_group)

        # Notification Settings Group
        notif_group = QGroupBox("Notification Settings")
        notif_group.setStyleSheet(get_groupbox_style())
        notif_layout = QFormLayout(notif_group)

        self.success_notif_check = QCheckBox("Success notifications")
        self.success_notif_check.setStyleSheet(get_checkbox_style())
        self.success_notif_check.setChecked(True)
        notif_layout.addRow("", self.success_notif_check)

        self.error_notif_check = QCheckBox("Error notifications")
        self.error_notif_check.setStyleSheet(get_checkbox_style())
        self.error_notif_check.setChecked(True)
        notif_layout.addRow("", self.error_notif_check)

        layout.addWidget(notif_group)
        layout.addStretch()

    def create_action_buttons(self, layout):
        """สร้างปุ่มสำหรับจัดการ Config"""
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)

        # Save Config Button
        self.save_btn = QPushButton("💾 Save Configuration")
        self.save_btn.setStyleSheet(get_gradient_button_style("#4CAF50", "#388E3C"))
        self.save_btn.clicked.connect(self._save_config)
        button_layout.addWidget(self.save_btn)

        # Load Config Button
        self.load_btn = QPushButton("📂 Load Configuration")
        self.load_btn.setStyleSheet(get_gradient_button_style("#2196F3", "#1976D2"))
        self.load_btn.clicked.connect(self._load_config_file)
        button_layout.addWidget(self.load_btn)

        # Reset Button
        self.reset_btn = QPushButton("🔄 Reset to Defaults")
        self.reset_btn.setStyleSheet(get_gradient_button_style("#FF9800", "#F57C00"))
        self.reset_btn.clicked.connect(self._reset_config)
        button_layout.addWidget(self.reset_btn)

        button_layout.addStretch()
        layout.addWidget(button_frame)

    # Public Methods
    def load_config(self, config: AppConfig):
        """โหลด Configuration ลง UI"""
        self.config = config

        # SharePoint Tab
        self.tenant_id_input.setText(config.tenant_id)
        self.client_id_input.setText(config.client_id)
        self.client_secret_input.setText(config.client_secret)
        self.site_url_input.setText(config.site_url)
        self.list_name_combo.setCurrentText(config.list_name)
        self.use_graph_api_check.setChecked(config.use_graph_api)

        # Database Tab
        self.db_type_combo.setCurrentText(config.database_type)

        # SQL Server
        self.sql_server_input.setText(config.sql_server)
        self.sql_database_combo.setCurrentText(config.sql_database)
        self.sql_username_input.setText(config.sql_username)
        self.sql_password_input.setText(config.sql_password)
        self.sql_table_combo.setCurrentText(config.sql_table_name)
        self.sql_create_table_check.setChecked(config.sql_create_table)
        self.sql_truncate_check.setChecked(config.sql_truncate_before)

        # SQLite
        self.sqlite_file_input.setText(config.sqlite_file)
        self.sqlite_table_input.setText(config.sqlite_table_name)
        self.sqlite_create_table_check.setChecked(config.sqlite_create_table)

        # Advanced Tab
        self.sync_interval_spin.setValue(config.sync_interval)
        self.sync_mode_combo.setCurrentText(config.sync_mode)
        self.batch_size_spin.setValue(config.batch_size)
        self.timeout_spin.setValue(config.connection_timeout)
        self.retries_spin.setValue(config.max_retries)
        self.parallel_check.setChecked(config.parallel_processing)
        self.log_level_combo.setCurrentText(config.log_level)
        self.success_notif_check.setChecked(config.success_notifications)
        self.error_notif_check.setChecked(config.error_notifications)

        # Update database visibility
        self._on_db_type_changed(config.database_type)

    def get_config(self) -> AppConfig:
        """ดึง Configuration จาก UI"""
        config = AppConfig()

        # SharePoint
        config.tenant_id = self.tenant_id_input.text().strip()
        config.client_id = self.client_id_input.text().strip()
        config.client_secret = self.client_secret_input.text().strip()
        config.site_url = self.site_url_input.text().strip()
        config.list_name = self.list_name_combo.currentText().strip()
        config.use_graph_api = self.use_graph_api_check.isChecked()

        # Database
        config.database_type = self.db_type_combo.currentText()

        # SQL Server
        config.sql_server = self.sql_server_input.text().strip()
        config.sql_database = self.sql_database_combo.currentText().strip()
        config.sql_username = self.sql_username_input.text().strip()
        config.sql_password = self.sql_password_input.text().strip()
        config.sql_table_name = self.sql_table_combo.currentText().strip()
        config.sql_create_table = self.sql_create_table_check.isChecked()
        config.sql_truncate_before = self.sql_truncate_check.isChecked()

        # SQLite
        config.sqlite_file = self.sqlite_file_input.text().strip()
        config.sqlite_table_name = self.sqlite_table_input.text().strip()
        config.sqlite_create_table = self.sqlite_create_table_check.isChecked()

        # Advanced
        config.sync_interval = self.sync_interval_spin.value()
        config.sync_mode = self.sync_mode_combo.currentText()
        config.batch_size = self.batch_size_spin.value()
        config.connection_timeout = self.timeout_spin.value()
        config.max_retries = self.retries_spin.value()
        config.parallel_processing = self.parallel_check.isChecked()
        config.log_level = self.log_level_combo.currentText()
        config.success_notifications = self.success_notif_check.isChecked()
        config.error_notifications = self.error_notif_check.isChecked()

        return config

    def update_sharepoint_lists(self, lists):
        """อัพเดทรายการ SharePoint Lists"""
        self.list_name_combo.clear()
        for list_item in lists:
            self.list_name_combo.addItem(list_item.get("Title", ""))

    def update_databases(self, databases):
        """อัพเดทรายการ Databases"""
        current_text = self.sql_database_combo.currentText()
        self.sql_database_combo.clear()
        self.sql_database_combo.addItems(databases)
        self.sql_database_combo.setCurrentText(current_text)

    def update_tables(self, tables):
        """อัพเดทรายการ Tables"""
        current_text = self.sql_table_combo.currentText()
        self.sql_table_combo.clear()
        self.sql_table_combo.addItems(tables)
        self.sql_table_combo.setCurrentText(current_text)

    # Private Methods
    def _on_db_type_changed(self, db_type):
        """จัดการเมื่อเปลี่ยน Database Type"""
        if db_type == "sqlserver":
            self.sqlserver_group.setVisible(True)
            self.sqlite_group.setVisible(False)
        elif db_type == "sqlite":
            self.sqlserver_group.setVisible(False)
            self.sqlite_group.setVisible(True)
        else:
            # For mysql, postgresql - use sqlserver UI
            self.sqlserver_group.setVisible(True)
            self.sqlite_group.setVisible(False)

    def _browse_sqlite_file(self):
        """เลือกไฟล์ SQLite"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Select SQLite Database File",
            self.sqlite_file_input.text() or "data.db",
            "SQLite Files (*.db *.sqlite *.sqlite3);;All Files (*)",
        )

        if file_path:
            self.sqlite_file_input.setText(file_path)

    def _save_config(self):
        """บันทึก Configuration"""
        try:
            config = self.get_config()
            self.config_changed.emit(config)
            logger.info("Configuration saved from UI")
        except Exception as e:
            logger.error(f"Failed to save config from UI: {str(e)}")

    def _load_config_file(self):
        """โหลด Configuration จากไฟล์"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Configuration File", "", "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                import json

                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                config = AppConfig.from_dict(data)
                self.load_config(config)
                self.config_changed.emit(config)
                logger.info(f"Configuration loaded from {file_path}")

            except Exception as e:
                logger.error(f"Failed to load config from {file_path}: {str(e)}")

    def _reset_config(self):
        """รีเซ็ต Configuration เป็นค่าเริ่มต้น"""
        from PyQt5.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            self,
            "Reset Configuration",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            default_config = AppConfig()
            self.load_config(default_config)
            self.config_changed.emit(default_config)
            logger.info("Configuration reset to defaults")

    # Slot Methods
    @pyqtSlot(list)
    def on_sharepoint_lists_received(self, lists):
        """รับรายการ SharePoint Lists"""
        self.update_sharepoint_lists(lists)

    @pyqtSlot(list)
    def on_databases_received(self, databases):
        """รับรายการ Databases"""
        self.update_databases(databases)

    @pyqtSlot(list)
    def on_tables_received(self, tables):
        """รับรายการ Tables"""
        self.update_tables(tables)

    @pyqtSlot(str)
    def on_log_message(self, message):
        """รับข้อความ log จาก controller"""
        logger.info(message)
