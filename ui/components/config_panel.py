from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QFormLayout,
    QLineEdit,
    QCheckBox,
    QSpinBox,
    QFrame,
    QFileDialog,
    QMessageBox,
)
from PyQt6.QtCore import pyqtSignal, QTimer
from ..styles.theme import (
    get_holographic_tab_style,
    get_ultra_modern_input_style,
    get_neon_checkbox_style,
    get_ultra_modern_card_style,
)
from utils.config_manager import AppConfig
import logging

logger = logging.getLogger(__name__)


class ConfigPanel(QWidget):
    """Modern Configuration Panel with responsive design"""

    # Signals
    config_changed = pyqtSignal(object)
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
        self.setup_ultra_modern_ui()
        self.setup_background_effects()

    def setup_ultra_modern_ui(self):
        """ตั้งค่า UI แบบ ultra modern"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Ultra modern tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(get_holographic_tab_style())

        # สร้าง tabs
        self.create_neural_sharepoint_tab()
        self.create_quantum_database_tab()
        self.create_matrix_advanced_tab()

        # เพิ่ม tabs พร้อม cyber icons
        self.tab_widget.addTab(self.sharepoint_tab, "◈ Neural SharePoint")
        self.tab_widget.addTab(self.database_tab, "◎ Quantum Database")
        self.tab_widget.addTab(self.advanced_tab, "⬢ Matrix Advanced")

        layout.addWidget(self.tab_widget)

        # Action buttons แบบ cyberpunk
        self.create_cyber_action_buttons(layout)

    def create_sharepoint_tab(self):
        """Create SharePoint configuration tab"""
        self.sharepoint_tab = QWidget()
        layout = QVBoxLayout(self.sharepoint_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(24)

        # Neural Authentication Group
        auth_group = NeonGroupBox("◈ Neural Authentication Matrix")
        auth_layout = QFormLayout(auth_group)
        auth_layout.setSpacing(16)

        # Tenant ID
        self.tenant_id_input = CyberInput("xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        auth_layout.addRow(
            self.create_neon_label("Tenant Neural ID:"), self.tenant_id_input
        )

        # Client ID
        self.client_id_input = CyberInput("Application (client) neural identifier")
        auth_layout.addRow(
            self.create_neon_label("Client Neural ID:"), self.client_id_input
        )

        # Client Secret
        self.client_secret_input = QLineEdit()
        self.client_secret_input.setStyleSheet(get_modern_input_style())
        self.client_secret_input.setEchoMode(QLineEdit.Password)
        self.client_secret_input.setPlaceholderText("Client secret value")
        auth_layout.addRow("Client Secret:", self.client_secret_input)

        content_layout.addWidget(auth_group)

        # Matrix Connection Group
        connection_group = NeonGroupBox("◎ Matrix Connection Protocol")
        connection_layout = QFormLayout(connection_group)
        connection_layout.setSpacing(16)

        # Site URL with refresh
        site_url_layout = QHBoxLayout()
        self.site_url_input = CyberInput(
            "https://yourcompany.sharepoint.com/sites/matrix"
        )

        self.refresh_sites_btn = CyberButton("◉", "primary", "sm")
        self.refresh_sites_btn.setMaximumWidth(44)
        self.refresh_sites_btn.clicked.connect(self.refresh_sites_requested.emit)

        site_url_layout.addWidget(self.site_url_input)
        site_url_layout.addWidget(self.refresh_sites_btn)
        connection_layout.addRow(
            self.create_neon_label("Matrix Site URL:"), site_url_layout
        )

        # List Name with refresh
        list_layout = QHBoxLayout()
        self.list_name_combo = HolographicComboBox()
        self.list_name_combo.setEditable(True)

        self.refresh_lists_btn = CyberButton("◈", "primary", "sm")
        self.refresh_lists_btn.setMaximumWidth(44)
        self.refresh_lists_btn.clicked.connect(self.refresh_lists_requested.emit)

        list_layout.addWidget(self.list_name_combo)
        list_layout.addWidget(self.refresh_lists_btn)
        connection_layout.addRow(
            self.create_neon_label("Data Stream List:"), list_layout
        )

        content_layout.addWidget(connection_group)

        # Protocol Options Group
        options_group = NeonGroupBox("⬢ Neural Protocol Options")
        options_layout = QFormLayout(options_group)

        self.use_graph_api_check = QCheckBox("◦ Enable Microsoft Graph Neural API")
        self.use_graph_api_check.setStyleSheet(get_neon_checkbox_style())
        options_layout.addRow("", self.use_graph_api_check)

        content_layout.addWidget(options_group)

        # Test Neural Connection
        test_layout = QHBoxLayout()
        self.test_sp_btn = CyberButton("◉ Initiate Neural Probe", "success", "lg")
        self.test_sp_btn.clicked.connect(self.test_sharepoint_requested.emit)
        test_layout.addWidget(self.test_sp_btn)
        test_layout.addStretch()

        content_layout.addLayout(test_layout)
        content_layout.addStretch()

    def create_database_tab(self):
        """Create database configuration tab"""
        self.database_tab = QWidget()
        layout = QVBoxLayout(self.database_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(24)

        # Quantum Engine Selection
        type_group = NeonGroupBox("◎ Quantum Storage Engine")
        type_layout = QVBoxLayout(type_group)

        self.db_type_combo = HolographicComboBox()
        self.db_type_combo.addItems(["sqlserver", "sqlite", "mysql", "postgresql"])
        self.db_type_combo.currentTextChanged.connect(self._on_db_type_changed)
        type_layout.addWidget(self.db_type_combo)

        content_layout.addWidget(type_group)

        # SQL Server Quantum Configuration
        self.sqlserver_group = NeonGroupBox("◈ SQL Server Quantum Matrix")
        sqlserver_layout = QFormLayout(self.sqlserver_group)
        sqlserver_layout.setSpacing(16)

        # Server
        self.sql_server_input = CyberInput("quantum-server.database.matrix.net")
        sqlserver_layout.addRow(
            self.create_neon_label("Quantum Server:"), self.sql_server_input
        )

        # Database with refresh
        db_layout = QHBoxLayout()
        self.sql_database_combo = HolographicComboBox()
        self.sql_database_combo.setEditable(True)

        self.refresh_db_btn = CyberButton("◎", "primary", "sm")
        self.refresh_db_btn.setMaximumWidth(44)
        self.refresh_db_btn.clicked.connect(self.refresh_databases_requested.emit)

        db_layout.addWidget(self.sql_database_combo)
        db_layout.addWidget(self.refresh_db_btn)
        sqlserver_layout.addRow(self.create_neon_label("Quantum Database:"), db_layout)

        # Username
        self.sql_username_input = QLineEdit()
        self.sql_username_input.setStyleSheet(get_modern_input_style())
        sqlserver_layout.addRow("Username:", self.sql_username_input)

        # Password
        self.sql_password_input = QLineEdit()
        self.sql_password_input.setStyleSheet(get_modern_input_style())
        self.sql_password_input.setEchoMode(QLineEdit.Password)
        sqlserver_layout.addRow("Password:", self.sql_password_input)

        # Table with refresh
        table_layout = QHBoxLayout()
        self.sql_table_combo = HolographicComboBox()
        self.sql_table_combo.setEditable(True)

        self.refresh_tables_btn = CyberButton("⬢", "primary", "sm")
        self.refresh_tables_btn.setMaximumWidth(44)
        self.refresh_tables_btn.clicked.connect(self.refresh_tables_requested.emit)

        table_layout.addWidget(self.sql_table_combo)
        table_layout.addWidget(self.refresh_tables_btn)
        sqlserver_layout.addRow(
            self.create_neon_label("Data Matrix Table:"), table_layout
        )

        # Quantum Options
        self.sql_create_table_check = QCheckBox(
            "◦ Auto-generate quantum table structure"
        )
        self.sql_create_table_check.setStyleSheet(get_neon_checkbox_style())
        self.sql_create_table_check.setChecked(True)
        sqlserver_layout.addRow("", self.sql_create_table_check)

        self.sql_truncate_check = QCheckBox("◦ Purge existing quantum data before sync")
        self.sql_truncate_check.setStyleSheet(get_neon_checkbox_style())
        sqlserver_layout.addRow("", self.sql_truncate_check)

        content_layout.addWidget(self.sqlserver_group)

        # Test Quantum Connection
        test_layout = QHBoxLayout()
        self.test_db_btn = CyberButton("◎ Quantum Connection Probe", "success", "lg")
        self.test_db_btn.clicked.connect(self.test_database_requested.emit)
        test_layout.addWidget(self.test_db_btn)
        test_layout.addStretch()

        content_layout.addLayout(test_layout)
        content_layout.addStretch()

        # Initially show SQL Server
        self._on_db_type_changed("sqlserver")

    def create_advanced_tab(self):
        """Create advanced configuration tab"""
        self.advanced_tab = QWidget()
        layout = QVBoxLayout(self.advanced_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(24)

        # Neural Sync Settings
        sync_group = NeonGroupBox("◈ Neural Synchronization Protocol")
        sync_layout = QFormLayout(sync_group)
        sync_layout.setSpacing(16)

        # Sync Interval
        self.sync_interval_spin = QSpinBox()
        self.sync_interval_spin.setMinimum(60)
        self.sync_interval_spin.setMaximum(86400)
        self.sync_interval_spin.setValue(3600)
        self.sync_interval_spin.setSuffix(" neural cycles")
        self.sync_interval_spin.setStyleSheet(get_ultra_modern_input_style())
        sync_layout.addRow(
            self.create_neon_label("Sync Frequency:"), self.sync_interval_spin
        )

        # Sync Mode
        self.sync_mode_combo = HolographicComboBox()
        self.sync_mode_combo.addItems(["full", "incremental", "quantum"])
        sync_layout.addRow(
            self.create_neon_label("Sync Protocol:"), self.sync_mode_combo
        )

        # Batch Size
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setMinimum(100)
        self.batch_size_spin.setMaximum(10000)
        self.batch_size_spin.setValue(1000)
        self.batch_size_spin.setSuffix(" data packets")
        self.batch_size_spin.setStyleSheet(get_ultra_modern_input_style())
        sync_layout.addRow(
            self.create_neon_label("Neural Batch Size:"), self.batch_size_spin
        )

        content_layout.addWidget(sync_group)

        # Quantum Performance Settings
        perf_group = NeonGroupBox("⬢ Quantum Performance Matrix")
        perf_layout = QFormLayout(perf_group)
        perf_layout.setSpacing(16)

        # Connection Timeout
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setMinimum(10)
        self.timeout_spin.setMaximum(300)
        self.timeout_spin.setValue(30)
        self.timeout_spin.setSuffix(" quantum seconds")
        self.timeout_spin.setStyleSheet(get_ultra_modern_input_style())
        perf_layout.addRow(self.create_neon_label("Neural Timeout:"), self.timeout_spin)

        # Max Retries
        self.retries_spin = QSpinBox()
        self.retries_spin.setMinimum(1)
        self.retries_spin.setMaximum(10)
        self.retries_spin.setValue(3)
        self.retries_spin.setStyleSheet(get_ultra_modern_input_style())
        perf_layout.addRow(self.create_neon_label("Retry Attempts:"), self.retries_spin)

        # Parallel Processing
        self.parallel_check = QCheckBox("◦ Enable parallel quantum processing")
        self.parallel_check.setStyleSheet(get_neon_checkbox_style())
        perf_layout.addRow("", self.parallel_check)

        content_layout.addWidget(perf_group)

        # Matrix Monitoring Settings
        log_group = NeonGroupBox("◎ Neural Activity Monitoring")
        log_layout = QFormLayout(log_group)
        log_layout.setSpacing(16)

        # Log Level
        self.log_level_combo = HolographicComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level_combo.setCurrentText("INFO")
        log_layout.addRow(
            self.create_neon_label("Monitor Level:"), self.log_level_combo
        )

        content_layout.addWidget(log_group)

        # Notification Matrix
        notif_group = NeonGroupBox("◈ Alert Transmission Protocol")
        notif_layout = QFormLayout(notif_group)

        self.success_notif_check = QCheckBox("◦ Success neural transmissions")
        self.success_notif_check.setStyleSheet(get_neon_checkbox_style())
        self.success_notif_check.setChecked(True)
        notif_layout.addRow("", self.success_notif_check)

        self.error_notif_check = QCheckBox("◦ Error neural alerts")
        self.error_notif_check.setStyleSheet(get_neon_checkbox_style())
        self.error_notif_check.setChecked(True)
        notif_layout.addRow("", self.error_notif_check)

        content_layout.addWidget(notif_group)
        content_layout.addStretch()

    def create_cyber_action_buttons(self, layout):
        """สร้าง action buttons แบบ cyberpunk"""
        button_frame = QFrame()
        button_frame.setStyleSheet(get_ultra_modern_card_style())

        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(24, 16, 24, 16)
        button_layout.setSpacing(16)

        # Save Config Button
        self.save_btn = CyberButton("◉ Save Neural Configuration", "success", "lg")
        self.save_btn.clicked.connect(self._save_config)
        button_layout.addWidget(self.save_btn)

        # Load Config Button
        self.load_btn = CyberButton("◎ Load Configuration Matrix", "primary", "lg")
        self.load_btn.clicked.connect(self._load_config_file)
        button_layout.addWidget(self.load_btn)

        # Reset Button
        self.reset_btn = CyberButton("⬢ Reset to Quantum Defaults", "warning", "lg")
        self.reset_btn.clicked.connect(self._reset_config)
        button_layout.addWidget(self.reset_btn)

        button_layout.addStretch()
        layout.addWidget(button_frame)

    # Implementation methods
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
            title = list_item.get("Title", "")
            if title:
                self.list_name_combo.addItem(f"◦ {title}")

    def update_databases(self, databases):
        """อัพเดทรายการ Databases"""
        current_text = self.sql_database_combo.currentText()
        self.sql_database_combo.clear()
        for db in databases:
            self.sql_database_combo.addItem(f"◎ {db}")
        self.sql_database_combo.setCurrentText(current_text)

    def update_tables(self, tables):
        """อัพเดทรายการ Tables"""
        current_text = self.sql_table_combo.currentText()
        self.sql_table_combo.clear()
        for table in tables:
            self.sql_table_combo.addItem(f"⬢ {table}")
        self.sql_table_combo.setCurrentText(current_text)

    # Private Methods
    def _on_db_type_changed(self, db_type):
        """จัดการเมื่อเปลี่ยน Database Type"""
        if db_type == "sqlserver":
            self.sqlserver_group.setVisible(True)
        else:
            # For other types, could add more groups
            self.sqlserver_group.setVisible(True)  # Keep visible for now

    def _save_config(self):
        """บันทึก Configuration พร้อม cyber effects"""
        try:
            config = self.get_config()
            self.config_changed.emit(config)

            # Visual feedback
            self.save_btn.setText("◉ Neural Config Saved!")
            QTimer.singleShot(
                2000, lambda: self.save_btn.setText("◉ Save Neural Configuration")
            )

            logger.info("Configuration saved from cyber UI")
        except Exception as e:
            logger.error(f"Failed to save config from cyber UI: {str(e)}")

    def _load_config_file(self):
        """โหลด Configuration จากไฟล์"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Neural Configuration Matrix",
            "",
            "JSON Files (*.json);;All Files (*)",
        )

        if file_path:
            try:
                import json

                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                config = AppConfig.from_dict(data)
                self.load_config(config)
                self.config_changed.emit(config)

                # Visual feedback
                self.load_btn.setText("◎ Matrix Loaded!")
                QTimer.singleShot(
                    2000, lambda: self.load_btn.setText("◎ Load Configuration Matrix")
                )

                logger.info(f"Configuration loaded from neural matrix: {file_path}")

            except Exception as e:
                logger.error(f"Failed to load config from {file_path}: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Neural Matrix Error",
                    f"Failed to load configuration matrix:\n{str(e)}",
                )

    def _reset_config(self):
        """Reset configuration to defaults"""
        pass  # Implement if needed



# UltraModernConfigPanel สำหรับ UI แบบ ultra modern
class UltraModernConfigPanel(ConfigPanel):
    def __init__(self, controller):
        super().__init__(controller)
