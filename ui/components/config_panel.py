from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QSizePolicy,
)
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from ..styles.theme import (
    get_modern_tab_style,
)
from utils.config_validation import quick_validate_sharepoint, quick_validate_database
from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity

from ..widgets.modern_button import ActionButton
from ..widgets.modern_input import (
    ModernLineEdit,
    ModernSpinBox,
    FormField,
    PasswordField,
)
from ..widgets.holographic_combobox import HolographicComboBox
from ..widgets.neon_groupbox import NeonGroupBox
import logging

logger = logging.getLogger(__name__)


class ConfigValidator:
    """แยก validation logic ออกมา"""

    @staticmethod
    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.MEDIUM)
    def validate_sharepoint(config):
        """ตรวจสอบ SharePoint config"""
        return quick_validate_sharepoint(
            config.sharepoint_url,
            config.tenant_id,
            config.sharepoint_client_id,
            config.sharepoint_client_secret,
        )

    @staticmethod
    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.MEDIUM)
    def validate_database(config):
        """ตรวจสอบ Database config"""
        if config.db_type.lower() == "sql server":
            return quick_validate_database(
                "sqlserver",
                server=config.db_host,
                database=config.db_name,
                username=config.db_username,
                password=config.db_password,
            )
        else:
            return quick_validate_database("sqlite", file_path=config.sqlite_file)


class ConfigDataManager:
    """แก้แล้ว: data management"""

    def __init__(self):
        from utils.config_manager import ConfigManager

        self.config_manager = ConfigManager()

    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.LOW)
    def load_config(self):
        """โหลด config จากไฟล์"""
        self.config = self.config_manager.get_config()
        return self.config

    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.MEDIUM)
    def save_config(self, ui_data):
        """บันทึก config จาก UI data"""
        # Map UI data to config
        self.config.sharepoint_url = ui_data.get("sharepoint_url", "")
        self.config.sharepoint_site = ui_data.get("sharepoint_site", "")
        self.config.sharepoint_list = ui_data.get("sharepoint_list", "")
        self.config.sharepoint_client_id = ui_data.get("sharepoint_client_id", "")
        self.config.sharepoint_client_secret = ui_data.get(
            "sharepoint_client_secret", ""
        )
        self.config.tenant_id = ui_data.get("tenant_id", "")
        self.config.use_graph_api = ui_data.get("use_graph_api", False)

        self.config.db_type = ui_data.get("db_type", "SQL Server")
        self.config.db_host = ui_data.get("db_host", "")
        self.config.db_port = ui_data.get("db_port", 1433)
        self.config.db_name = ui_data.get("db_name", "")
        self.config.db_table = ui_data.get("db_table", "")
        self.config.db_username = ui_data.get("db_username", "")
        self.config.db_password = ui_data.get("db_password", "")

        # SQLite settings
        self.config.sqlite_file = ui_data.get("sqlite_file", "data.db")
        self.config.sqlite_table_name = ui_data.get(
            "sqlite_table_name", "sharepoint_data"
        )
        self.config.sqlite_create_table = ui_data.get("sqlite_create_table", True)

        self.config.sync_interval = ui_data.get("sync_interval", 60)
        self.config.batch_size = ui_data.get("batch_size", 1000)
        self.config.log_level = ui_data.get("log_level", "INFO")
        self.config.enable_parallel_processing = ui_data.get(
            "parallel_processing", False
        )
        self.config.enable_success_notifications = ui_data.get(
            "success_notifications", True
        )
        self.config.enable_error_notifications = ui_data.get(
            "error_notifications", True
        )
        self.config.auto_sync_enabled = ui_data.get("auto_sync_enabled", False)

        self.config_manager.save_config(self.config)
        return True


class ModernConfigPanel(QWidget):
    """Modern Configuration Panel with enhanced UI"""

    # Signals
    config_changed = pyqtSignal(object)
    test_sharepoint_requested = pyqtSignal()
    test_database_requested = pyqtSignal()
    refresh_sites_requested = pyqtSignal()
    refresh_lists_requested = pyqtSignal()
    refresh_databases_requested = pyqtSignal()
    refresh_tables_requested = pyqtSignal()
    auto_sync_toggled = pyqtSignal(bool)

    def __init__(self, controller):
        super().__init__(parent=None)
        self.controller = controller
        self.data_manager = ConfigDataManager()
        self.validator = ConfigValidator()
        self.form_fields = {}

        self.setup_modern_ui()
        self._load_config_to_ui()

    def setup_modern_ui(self):
        """Setup modern UI with enhanced styling"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)

        # Modern tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(get_modern_tab_style())
        self.tab_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Create tabs with modern design
        self._create_sharepoint_tab()
        self._create_database_tab()
        self._create_settings_tab()

        layout.addWidget(self.tab_widget)
        self._connect_signals()

    def _create_sharepoint_tab(self):
        """สร้าง SharePoint tab แบบ modern"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(24)

        # Connection Settings Group
        conn_group = NeonGroupBox("🔗 Connection Settings")
        conn_layout = QVBoxLayout(conn_group)
        conn_layout.setSpacing(16)

        # SharePoint URL
        url_field = FormField(
            "SharePoint URL",
            ModernLineEdit("https://company.sharepoint.com/sites/sitename"),
            required=True,
            help_text="Full URL to your SharePoint site",
        )
        self.form_fields["sharepoint_url"] = url_field
        conn_layout.addWidget(url_field)

        # Tenant ID
        tenant_field = FormField(
            "Tenant ID",
            ModernLineEdit("12345678-1234-1234-1234-123456789012"),
            required=True,
            help_text="Azure AD Tenant identifier",
        )
        self.form_fields["tenant_id"] = tenant_field
        conn_layout.addWidget(tenant_field)

        layout.addWidget(conn_group)

        # Authentication Group
        auth_group = NeonGroupBox("🔐 Authentication")
        auth_layout = QVBoxLayout(auth_group)
        auth_layout.setSpacing(16)

        # Client ID
        client_id_field = FormField(
            "Client ID",
            ModernLineEdit("87654321-4321-4321-4321-210987654321"),
            required=True,
            help_text="Application (client) ID from Azure AD",
        )
        self.form_fields["sharepoint_client_id"] = client_id_field
        auth_layout.addWidget(client_id_field)

        # Client Secret
        client_secret_field = FormField(
            "Client Secret",
            PasswordField("Your-Client-Secret-Here"),
            required=True,
            help_text="Client secret from Azure AD app registration",
        )
        self.form_fields["sharepoint_client_secret"] = client_secret_field
        auth_layout.addWidget(client_secret_field)

        layout.addWidget(auth_group)

        # Site & List Selection Group
        selection_group = NeonGroupBox("📋 Site & List Selection")
        selection_layout = QVBoxLayout(selection_group)
        selection_layout.setSpacing(16)

        # Site selection with refresh
        site_layout = QHBoxLayout()
        site_combo = HolographicComboBox()
        self.form_fields["sharepoint_site"] = FormField("Site Name", site_combo)
        self.refresh_sites_btn = ActionButton.ghost("🔄 Refresh", size="sm")
        self.refresh_sites_btn.clicked.connect(self.refresh_sites_requested)

        site_layout.addWidget(self.form_fields["sharepoint_site"], 3)
        site_layout.addWidget(self.refresh_sites_btn, 1)
        selection_layout.addLayout(site_layout)

        # List selection with refresh
        list_layout = QHBoxLayout()
        list_combo = HolographicComboBox()
        self.form_fields["sharepoint_list"] = FormField("List Name", list_combo)
        self.refresh_lists_btn = ActionButton.ghost("🔄 Refresh", size="sm")
        self.refresh_lists_btn.clicked.connect(self.refresh_lists_requested)

        list_layout.addWidget(self.form_fields["sharepoint_list"], 3)
        list_layout.addWidget(self.refresh_lists_btn, 1)
        selection_layout.addLayout(list_layout)

        layout.addWidget(selection_group)

        # Test button
        test_btn = ActionButton.primary("🧪 Test SharePoint Connection", size="md")
        test_btn.clicked.connect(self.test_sharepoint_requested)
        layout.addWidget(test_btn)

        layout.addStretch()
        self.tab_widget.addTab(tab, "SharePoint")

    def _create_database_tab(self):
        """สร้าง Database tab แบบ modern"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(24)

        # Database Type Selection
        type_group = NeonGroupBox("🗄️ Database Type")
        type_layout = QVBoxLayout(type_group)

        db_type_field = FormField(
            "Database Type",
            HolographicComboBox(),
            help_text="Choose your database platform",
        )
        db_type_field.input_widget.addItems(["SQL Server", "SQLite"])
        self.form_fields["db_type"] = db_type_field
        db_type_field.input_widget.currentTextChanged.connect(self._on_db_type_changed)
        type_layout.addWidget(db_type_field)

        layout.addWidget(type_group)

        # SQL Server Configuration
        self.sql_group = NeonGroupBox("💾 SQL Server Configuration")
        sql_layout = QVBoxLayout(self.sql_group)
        sql_layout.setSpacing(16)

        # Server and credentials
        server_field = FormField(
            "Server",
            ModernLineEdit("localhost\\SQLEXPRESS"),
            required=True,
            help_text="SQL Server instance name",
        )
        self.form_fields["db_host"] = server_field
        sql_layout.addWidget(server_field)

        username_field = FormField(
            "Username", ModernLineEdit("username"), required=True
        )
        self.form_fields["db_username"] = username_field
        sql_layout.addWidget(username_field)

        password_field = FormField("Password", PasswordField("password"), required=True)
        self.form_fields["db_password"] = password_field
        sql_layout.addWidget(password_field)

        # Database and table selection
        db_layout = QHBoxLayout()
        db_combo = HolographicComboBox()
        db_combo.setEditable(True)
        self.form_fields["db_name"] = FormField("Database", db_combo)
        self.refresh_dbs_btn = ActionButton.ghost("🔄 Refresh", size="sm")
        self.refresh_dbs_btn.clicked.connect(self.refresh_databases_requested)

        db_layout.addWidget(self.form_fields["db_name"], 3)
        db_layout.addWidget(self.refresh_dbs_btn, 1)
        sql_layout.addLayout(db_layout)

        table_layout = QHBoxLayout()
        table_combo = HolographicComboBox()
        table_combo.setEditable(True)
        self.form_fields["db_table"] = FormField("Table", table_combo)
        self.refresh_tables_btn = ActionButton.ghost("🔄 Refresh", size="sm")
        self.refresh_tables_btn.clicked.connect(self.refresh_tables_requested)

        table_layout.addWidget(self.form_fields["db_table"], 3)
        table_layout.addWidget(self.refresh_tables_btn, 1)
        sql_layout.addLayout(table_layout)

        layout.addWidget(self.sql_group)

        # SQLite Configuration
        self.sqlite_group = NeonGroupBox("📄 SQLite Configuration")
        sqlite_layout = QVBoxLayout(self.sqlite_group)
        sqlite_layout.setSpacing(16)

        sqlite_file_field = FormField(
            "Database File",
            ModernLineEdit("data/database.db"),
            help_text="Path to SQLite database file",
        )
        self.form_fields["sqlite_file"] = sqlite_file_field
        sqlite_layout.addWidget(sqlite_file_field)

        sqlite_table_field = FormField(
            "Table Name",
            ModernLineEdit("sharepoint_data"),
            help_text="Name of the table to store data",
        )
        self.form_fields["sqlite_table_name"] = sqlite_table_field
        sqlite_layout.addWidget(sqlite_table_field)

        layout.addWidget(self.sqlite_group)

        # Test button
        test_btn = ActionButton.primary("🧪 Test Database Connection", size="md")
        test_btn.clicked.connect(self.test_database_requested)
        layout.addWidget(test_btn)

        layout.addStretch()
        self.tab_widget.addTab(tab, "Database")

        # Initially show SQL Server
        self._on_db_type_changed("SQL Server")

    def _create_settings_tab(self):
        """สร้าง Settings tab แบบ modern"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(24)

        # Sync Settings
        sync_group = NeonGroupBox("⏱️ Synchronization Settings")
        sync_layout = QVBoxLayout(sync_group)
        sync_layout.setSpacing(16)

        interval_field = FormField(
            "Sync Interval",
            ModernSpinBox(1, 1440, 60, "minutes"),
            help_text="How often to automatically sync data",
        )
        self.form_fields["sync_interval"] = interval_field
        sync_layout.addWidget(interval_field)

        layout.addWidget(sync_group)

        # Performance Settings
        perf_group = NeonGroupBox("⚡ Performance Settings")
        perf_layout = QVBoxLayout(perf_group)
        perf_layout.setSpacing(16)

        batch_field = FormField(
            "Batch Size",
            ModernSpinBox(100, 10000, 1000, "records"),
            help_text="Number of records to process at once",
        )
        self.form_fields["batch_size"] = batch_field
        perf_layout.addWidget(batch_field)

        log_level_field = FormField(
            "Log Level", HolographicComboBox(), help_text="Level of logging detail"
        )
        log_level_field.input_widget.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.form_fields["log_level"] = log_level_field
        perf_layout.addWidget(log_level_field)

        layout.addWidget(perf_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "Settings")

    def _on_db_type_changed(self, db_type):
        """เปลี่ยน UI ตามประเภทฐานข้อมูล"""
        if db_type == "SQL Server":
            self.sql_group.setVisible(True)
            self.sqlite_group.setVisible(False)
        else:  # SQLite
            self.sql_group.setVisible(False)
            self.sqlite_group.setVisible(True)

    def _connect_signals(self):
        """เชื่อมต่อ signals"""
        # Connect form field changes to save config
        for field_name, field_widget in self.form_fields.items():
            if hasattr(field_widget.input_widget, "textChanged"):
                field_widget.input_widget.textChanged.connect(self._save_config_from_ui)
            elif hasattr(field_widget.input_widget, "valueChanged"):
                field_widget.input_widget.valueChanged.connect(
                    self._save_config_from_ui
                )
            elif hasattr(field_widget.input_widget, "currentTextChanged"):
                field_widget.input_widget.currentTextChanged.connect(
                    self._save_config_from_ui
                )

    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.LOW)
    def _save_config_from_ui(self):
        """บันทึก config จาก UI"""
        ui_data = {}
        for field_name, field_widget in self.form_fields.items():
            ui_data[field_name] = field_widget.get_value()

        success = self.data_manager.save_config(ui_data)
        if success:
            self.config_changed.emit(self.data_manager.config)
            logger.info("Configuration updated")

    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.LOW)
    def _load_config_to_ui(self):
        """โหลด config มาแสดงใน UI"""
        config = self.data_manager.load_config()

        field_mapping = {
            "sharepoint_url": config.sharepoint_url or "",
            "tenant_id": config.tenant_id or "",
            "sharepoint_client_id": config.sharepoint_client_id or "",
            "sharepoint_client_secret": config.sharepoint_client_secret or "",
            "db_type": config.db_type or "SQL Server",
            "db_host": config.db_host or "",
            "db_username": config.db_username or "",
            "db_password": config.db_password or "",
            "db_name": config.db_name or "",
            "db_table": config.db_table or "",
            "sqlite_file": config.sqlite_file or "data.db",
            "sqlite_table_name": config.sqlite_table_name or "sharepoint_data",
            "sync_interval": config.sync_interval,
            "batch_size": config.batch_size,
            "log_level": config.log_level,
        }

        for field_name, value in field_mapping.items():
            if field_name in self.form_fields:
                self.form_fields[field_name].set_value(value)

        # Update UI based on database type
        self._on_db_type_changed(config.db_type or "SQL Server")
        logger.info("Configuration loaded to UI")

    # UI state management
    @pyqtSlot(bool)
    def set_ui_enabled(self, enable: bool):
        """เปิด/ปิด UI elements"""
        self.tab_widget.setEnabled(enable)
        self.refresh_sites_btn.setEnabled(enable)
        self.refresh_lists_btn.setEnabled(enable)
        self.refresh_dbs_btn.setEnabled(enable)
        self.refresh_tables_btn.setEnabled(enable)

    # Data population slots
    @pyqtSlot(list)
    def populate_sharepoint_sites(self, sites):
        if "sharepoint_site" in self.form_fields:
            combo = self.form_fields["sharepoint_site"].input_widget
            combo.clear()
            site_names = [
                site.get("Title", site.get("name", str(site))) for site in sites
            ]
            combo.addItems(site_names)

    @pyqtSlot(list)
    def populate_sharepoint_lists(self, lists):
        if "sharepoint_list" in self.form_fields:
            combo = self.form_fields["sharepoint_list"].input_widget
            combo.clear()
            list_names = [lst.get("Title", lst.get("name", str(lst))) for lst in lists]
            combo.addItems(list_names)

    @pyqtSlot(list)
    def populate_database_names(self, db_names):
        if "db_name" in self.form_fields:
            combo = self.form_fields["db_name"].input_widget
            current_text = combo.currentText()
            combo.clear()
            combo.addItems(db_names)
            if current_text:
                combo.setCurrentText(current_text)

    @pyqtSlot(list)
    def populate_database_tables(self, tables):
        if "db_table" in self.form_fields:
            combo = self.form_fields["db_table"].input_widget
            current_text = combo.currentText()
            combo.clear()
            combo.addItems(tables)
            if current_text:
                combo.setCurrentText(current_text)


# Compatibility alias
UltraModernConfigPanel = ModernConfigPanel
