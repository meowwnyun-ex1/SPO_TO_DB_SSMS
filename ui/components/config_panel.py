# ui/components/config_panel.py - Fixed version

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
    QFrame,
)
from PyQt5.QtCore import pyqtSignal
from ..styles.theme import (
    get_modern_tab_style,
    get_modern_input_style,
    get_modern_button_style,
    get_modern_checkbox_style,
    get_modern_groupbox_style,
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
        self.setup_ui()

    def setup_ui(self):
        """Setup modern responsive UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Modern Tab Widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(get_modern_tab_style())

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
        """Create SharePoint configuration tab"""
        self.sharepoint_tab = QWidget()
        layout = QVBoxLayout(self.sharepoint_tab)
        layout.setSpacing(15)

        # Authentication Group
        auth_group = QGroupBox("Authentication")
        auth_group.setStyleSheet(get_modern_groupbox_style())
        auth_layout = QFormLayout(auth_group)

        # Tenant ID
        self.tenant_id_input = QLineEdit()
        self.tenant_id_input.setStyleSheet(get_modern_input_style())
        self.tenant_id_input.setPlaceholderText("xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        auth_layout.addRow("Tenant ID:", self.tenant_id_input)

        # Client ID
        self.client_id_input = QLineEdit()
        self.client_id_input.setStyleSheet(get_modern_input_style())
        self.client_id_input.setPlaceholderText("Application (client) ID")
        auth_layout.addRow("Client ID:", self.client_id_input)

        # Client Secret
        self.client_secret_input = QLineEdit()
        self.client_secret_input.setStyleSheet(get_modern_input_style())
        self.client_secret_input.setEchoMode(QLineEdit.Password)
        self.client_secret_input.setPlaceholderText("Client secret value")
        auth_layout.addRow("Client Secret:", self.client_secret_input)

        layout.addWidget(auth_group)

        # Site & List Group
        site_group = QGroupBox("Site & List Configuration")
        site_group.setStyleSheet(get_modern_groupbox_style())
        site_layout = QFormLayout(site_group)

        # Site URL
        site_url_layout = QHBoxLayout()
        self.site_url_input = QLineEdit()
        self.site_url_input.setStyleSheet(get_modern_input_style())
        self.site_url_input.setPlaceholderText(
            "https://yourcompany.sharepoint.com/sites/sitename"
        )

        self.refresh_sites_btn = QPushButton("🔄")
        self.refresh_sites_btn.setStyleSheet(get_modern_button_style("primary", "sm"))
        self.refresh_sites_btn.setMaximumWidth(40)
        self.refresh_sites_btn.clicked.connect(self.refresh_sites_requested.emit)

        site_url_layout.addWidget(self.site_url_input)
        site_url_layout.addWidget(self.refresh_sites_btn)
        site_layout.addRow("Site URL:", site_url_layout)

        # List Name
        list_layout = QHBoxLayout()
        self.list_name_combo = QComboBox()
        self.list_name_combo.setStyleSheet(get_modern_input_style())
        self.list_name_combo.setEditable(True)
        self.list_name_combo.setPlaceholderText(
            "Enter list name or select from dropdown"
        )

        self.refresh_lists_btn = QPushButton("🔄")
        self.refresh_lists_btn.setStyleSheet(get_modern_button_style("primary", "sm"))
        self.refresh_lists_btn.setMaximumWidth(40)
        self.refresh_lists_btn.clicked.connect(self.refresh_lists_requested.emit)

        list_layout.addWidget(self.list_name_combo)
        list_layout.addWidget(self.refresh_lists_btn)
        site_layout.addRow("List Name:", list_layout)

        layout.addWidget(site_group)

        # Options Group
        options_group = QGroupBox("Options")
        options_group.setStyleSheet(get_modern_groupbox_style())
        options_layout = QFormLayout(options_group)

        self.use_graph_api_check = QCheckBox("Use Microsoft Graph API")
        self.use_graph_api_check.setStyleSheet(get_modern_checkbox_style())
        options_layout.addRow("", self.use_graph_api_check)

        layout.addWidget(options_group)

        # Test Connection
        test_layout = QHBoxLayout()
        self.test_sp_btn = QPushButton("🔍 Test SharePoint Connection")
        self.test_sp_btn.setStyleSheet(get_modern_button_style("success"))
        self.test_sp_btn.clicked.connect(self.test_sharepoint_requested.emit)
        test_layout.addWidget(self.test_sp_btn)
        test_layout.addStretch()

        layout.addLayout(test_layout)
        layout.addStretch()

    def create_database_tab(self):
        """Create database configuration tab"""
        self.database_tab = QWidget()
        layout = QVBoxLayout(self.database_tab)
        layout.setSpacing(15)

        # Database Type Selection
        type_group = QGroupBox("Database Type")
        type_group.setStyleSheet(get_modern_groupbox_style())
        type_layout = QVBoxLayout(type_group)

        self.db_type_combo = QComboBox()
        self.db_type_combo.setStyleSheet(get_modern_input_style())
        self.db_type_combo.addItems(["sqlserver", "sqlite", "mysql", "postgresql"])
        self.db_type_combo.currentTextChanged.connect(self._on_db_type_changed)
        type_layout.addWidget(self.db_type_combo)

        layout.addWidget(type_group)

        # SQL Server Configuration
        self.sqlserver_group = QGroupBox("SQL Server Configuration")
        self.sqlserver_group.setStyleSheet(get_modern_groupbox_style())
        sqlserver_layout = QFormLayout(self.sqlserver_group)

        # Server
        self.sql_server_input = QLineEdit()
        self.sql_server_input.setStyleSheet(get_modern_input_style())
        self.sql_server_input.setPlaceholderText("server.database.windows.net")
        sqlserver_layout.addRow("Server:", self.sql_server_input)

        # Database
        db_layout = QHBoxLayout()
        self.sql_database_combo = QComboBox()
        self.sql_database_combo.setStyleSheet(get_modern_input_style())
        self.sql_database_combo.setEditable(True)

        self.refresh_db_btn = QPushButton("🔄")
        self.refresh_db_btn.setStyleSheet(get_modern_button_style("primary", "sm"))
        self.refresh_db_btn.setMaximumWidth(40)
        self.refresh_db_btn.clicked.connect(self.refresh_databases_requested.emit)

        db_layout.addWidget(self.sql_database_combo)
        db_layout.addWidget(self.refresh_db_btn)
        sqlserver_layout.addRow("Database:", db_layout)

        # Username
        self.sql_username_input = QLineEdit()
        self.sql_username_input.setStyleSheet(get_modern_input_style())
        sqlserver_layout.addRow("Username:", self.sql_username_input)

        # Password
        self.sql_password_input = QLineEdit()
        self.sql_password_input.setStyleSheet(get_modern_input_style())
        self.sql_password_input.setEchoMode(QLineEdit.Password)
        sqlserver_layout.addRow("Password:", self.sql_password_input)

        # Table
        table_layout = QHBoxLayout()
        self.sql_table_combo = QComboBox()
        self.sql_table_combo.setStyleSheet(get_modern_input_style())
        self.sql_table_combo.setEditable(True)

        self.refresh_tables_btn = QPushButton("🔄")
        self.refresh_tables_btn.setStyleSheet(get_modern_button_style("primary", "sm"))
        self.refresh_tables_btn.setMaximumWidth(40)
        self.refresh_tables_btn.clicked.connect(self.refresh_tables_requested.emit)

        table_layout.addWidget(self.sql_table_combo)
        table_layout.addWidget(self.refresh_tables_btn)
        sqlserver_layout.addRow("Table:", table_layout)

        # Options
        self.sql_create_table_check = QCheckBox("Auto-create table if not exists")
        self.sql_create_table_check.setStyleSheet(get_modern_checkbox_style())
        self.sql_create_table_check.setChecked(True)
        sqlserver_layout.addRow("", self.sql_create_table_check)

        self.sql_truncate_check = QCheckBox("Truncate table before insert")
        self.sql_truncate_check.setStyleSheet(get_modern_checkbox_style())
        sqlserver_layout.addRow("", self.sql_truncate_check)

        layout.addWidget(self.sqlserver_group)

        # Test Connection
        test_layout = QHBoxLayout()
        self.test_db_btn = QPushButton("🔍 Test Database Connection")
        self.test_db_btn.setStyleSheet(get_modern_button_style("success"))
        self.test_db_btn.clicked.connect(self.test_database_requested.emit)
        test_layout.addWidget(self.test_db_btn)
        test_layout.addStretch()

        layout.addLayout(test_layout)
        layout.addStretch()

        # Initially show SQL Server
        self._on_db_type_changed("sqlserver")

    def create_advanced_tab(self):
        """Create advanced configuration tab"""
        self.advanced_tab = QWidget()
        layout = QVBoxLayout(self.advanced_tab)
        layout.setSpacing(15)

        # Sync Settings Group
        sync_group = QGroupBox("Sync Settings")
        sync_group.setStyleSheet(get_modern_groupbox_style())
        sync_layout = QFormLayout(sync_group)

        # Sync Interval
        self.sync_interval_spin = QSpinBox()
        self.sync_interval_spin.setMinimum(60)
        self.sync_interval_spin.setMaximum(86400)
        self.sync_interval_spin.setValue(3600)
        self.sync_interval_spin.setSuffix(" seconds")
        sync_layout.addRow("Auto-sync Interval:", self.sync_interval_spin)

        # Sync Mode
        self.sync_mode_combo = QComboBox()
        self.sync_mode_combo.setStyleSheet(get_modern_input_style())
        self.sync_mode_combo.addItems(["full", "incremental"])
        sync_layout.addRow("Sync Mode:", self.sync_mode_combo)

        layout.addWidget(sync_group)
        layout.addStretch()

    def create_action_buttons(self, layout):
        """Create modern action buttons"""
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(15)

        # Save Config Button
        self.save_btn = QPushButton("💾 Save Configuration")
        self.save_btn.setStyleSheet(get_modern_button_style("success"))
        self.save_btn.clicked.connect(self._save_config)
        button_layout.addWidget(self.save_btn)

        # Load Config Button
        self.load_btn = QPushButton("📂 Load Configuration")
        self.load_btn.setStyleSheet(get_modern_button_style("primary"))
        self.load_btn.clicked.connect(self._load_config_file)
        button_layout.addWidget(self.load_btn)

        # Reset Button
        self.reset_btn = QPushButton("🔄 Reset to Defaults")
        self.reset_btn.setStyleSheet(get_modern_button_style("warning"))
        self.reset_btn.clicked.connect(self._reset_config)
        button_layout.addWidget(self.reset_btn)

        button_layout.addStretch()
        layout.addWidget(button_frame)

    # Implementation methods
    def load_config(self, config: AppConfig):
        """Load configuration into UI"""
        self.config = config
        # SharePoint Tab
        self.tenant_id_input.setText(config.tenant_id)
        self.client_id_input.setText(config.client_id)
        self.client_secret_input.setText(config.client_secret)
        self.site_url_input.setText(config.site_url)
        self.list_name_combo.setCurrentText(config.list_name)
        self.use_graph_api_check.setChecked(config.use_graph_api)

    def get_config(self) -> AppConfig:
        """Get configuration from UI"""
        config = AppConfig()
        # SharePoint
        config.tenant_id = self.tenant_id_input.text().strip()
        config.client_id = self.client_id_input.text().strip()
        config.client_secret = self.client_secret_input.text().strip()
        config.site_url = self.site_url_input.text().strip()
        config.list_name = self.list_name_combo.currentText().strip()
        config.use_graph_api = self.use_graph_api_check.isChecked()
        return config

    def update_sharepoint_lists(self, lists):
        """Update SharePoint lists dropdown"""
        self.list_name_combo.clear()
        for list_item in lists:
            self.list_name_combo.addItem(list_item.get("Title", ""))

    def update_databases(self, databases):
        """Update databases dropdown"""
        current_text = self.sql_database_combo.currentText()
        self.sql_database_combo.clear()
        self.sql_database_combo.addItems(databases)
        self.sql_database_combo.setCurrentText(current_text)

    def update_tables(self, tables):
        """Update tables dropdown"""
        current_text = self.sql_table_combo.currentText()
        self.sql_table_combo.clear()
        self.sql_table_combo.addItems(tables)
        self.sql_table_combo.setCurrentText(current_text)

    def _on_db_type_changed(self, db_type):
        """Handle database type change"""
        if db_type == "sqlserver":
            self.sqlserver_group.setVisible(True)
        else:
            self.sqlserver_group.setVisible(False)

    def _save_config(self):
        """Save configuration"""
        try:
            config = self.get_config()
            self.config_changed.emit(config)
            logger.info("Configuration saved from UI")
        except Exception as e:
            logger.error(f"Failed to save config from UI: {str(e)}")

    def _load_config_file(self):
        """Load configuration from file"""
        pass  # Implement if needed

    def _reset_config(self):
        """Reset configuration to defaults"""
        pass  # Implement if needed
