from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QSizePolicy,
    QLabel,
    QFrame,
)
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt6.QtGui import QFont
from ..styles.theme import (
    get_modern_tab_style,
    UltraModernColors,
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


class SectionFrame(QFrame):
    """แก้แล้ว: Frame สำหรับแต่ละ section ที่ดูดีขึ้น"""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_ui()

    def setup_ui(self):
        """Setup frame with title"""
        self.setStyleSheet(
            f"""
            QFrame {{
                background: {UltraModernColors.GLASS_BG_DARK};
                border: 2px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 16px;
                margin: 8px;
                padding: 16px;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Title header
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_label.setStyleSheet(
            f"""
            QLabel {{
                color: {UltraModernColors.TEXT_PRIMARY};
                background: {UltraModernColors.GLASS_BG};
                border: 1px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 8px;
                padding: 8px 16px;
                margin-bottom: 12px;
            }}
            """
        )
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Content area
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(12)
        layout.addWidget(QWidget())  # Spacer
        layout.itemAt(1).widget().setLayout(self.content_layout)


class ModernConfigPanel(QWidget):
    """แก้แล้ว: Config Panel ที่ดูดีขึ้น ไม่เบียดกัน"""

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
        """แก้แล้ว: Setup UI ที่ดูดีขึ้น"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # แก้: Header ที่ดูดีขึ้น
        header_frame = QFrame()
        header_frame.setStyleSheet(
            f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {UltraModernColors.NEON_PURPLE},
                    stop:1 {UltraModernColors.NEON_PINK}
                );
                border-radius: 16px;
                padding: 16px;
                margin-bottom: 16px;
            }}
            """
        )

        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 16, 20, 16)

        header_icon = QLabel("⚙️")
        header_icon.setFont(QFont("Segoe UI Emoji", 24))
        header_icon.setStyleSheet("color: white;")

        header_text = QLabel("System Configuration")
        header_text.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header_text.setStyleSheet("color: white;")

        header_layout.addWidget(header_icon)
        header_layout.addWidget(header_text)
        header_layout.addStretch()

        layout.addWidget(header_frame)

        # แก้: Tab widget ที่ดูดีขึ้น
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(
            get_modern_tab_style()
            + f"""
            QTabWidget::pane {{
                border: 2px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 16px;
                background: {UltraModernColors.GLASS_BG_DARK};
                margin-top: 10px;
            }}
            QTabBar::tab {{
                background: {UltraModernColors.GLASS_BG};
                border: 2px solid {UltraModernColors.GLASS_BORDER};
                border-bottom: none;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                padding: 12px 24px;
                color: {UltraModernColors.TEXT_PRIMARY};
                font-weight: bold;
                font-size: 12px;
                margin-right: 4px;
                min-width: 120px;
            }}
            QTabBar::tab:selected {{
                background: {UltraModernColors.NEON_PURPLE};
                border: 2px solid {UltraModernColors.NEON_PINK};
                color: white;
            }}
            QTabBar::tab:hover:!selected {{
                background: {UltraModernColors.GLASS_BG_LIGHT};
                border: 2px solid {UltraModernColors.NEON_BLUE};
            }}
            """
        )
        self.tab_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Create better tabs
        self._create_better_sharepoint_tab()
        self._create_better_database_tab()
        self._create_better_settings_tab()

        layout.addWidget(self.tab_widget)
        self._connect_signals()

    def _create_better_sharepoint_tab(self):
        """แก้แล้ว: SharePoint tab ที่ดูดีขึ้น"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)

        # Connection section
        conn_section = SectionFrame("🔗 Connection Settings")

        # URL และ Tenant ID
        url_layout = QHBoxLayout()
        url_layout.setSpacing(16)

        url_field = FormField(
            "SharePoint URL",
            ModernLineEdit("https://company.sharepoint.com/sites/sitename"),
        )
        url_field.input_widget.setMinimumHeight(40)
        self.form_fields["sharepoint_url"] = url_field

        tenant_field = FormField(
            "Tenant ID", ModernLineEdit("12345678-1234-1234-1234-123456789012")
        )
        tenant_field.input_widget.setMinimumHeight(40)
        self.form_fields["tenant_id"] = tenant_field

        url_layout.addWidget(url_field)
        url_layout.addWidget(tenant_field)
        conn_section.content_layout.addLayout(url_layout)

        # Client credentials
        auth_layout = QHBoxLayout()
        auth_layout.setSpacing(16)

        client_id_field = FormField(
            "Client ID", ModernLineEdit("87654321-4321-4321-4321-210987654321")
        )
        client_id_field.input_widget.setMinimumHeight(40)
        self.form_fields["sharepoint_client_id"] = client_id_field

        client_secret_field = FormField(
            "Client Secret", PasswordField("Your-Client-Secret-Here")
        )
        client_secret_field.input_widget.setMinimumHeight(40)
        self.form_fields["sharepoint_client_secret"] = client_secret_field

        auth_layout.addWidget(client_id_field)
        auth_layout.addWidget(client_secret_field)
        conn_section.content_layout.addLayout(auth_layout)

        layout.addWidget(conn_section)

        # Site & List section
        site_section = SectionFrame("📋 Site & List Selection")

        # Site selection
        site_layout = QHBoxLayout()
        site_layout.setSpacing(12)
        site_combo = HolographicComboBox()
        site_combo.setMinimumHeight(40)
        self.form_fields["sharepoint_site"] = FormField("Site Name", site_combo)
        self.refresh_sites_btn = ActionButton.ghost("🔄 Refresh", size="md")
        self.refresh_sites_btn.setMinimumWidth(120)
        self.refresh_sites_btn.clicked.connect(self.refresh_sites_requested)

        site_layout.addWidget(self.form_fields["sharepoint_site"], 3)
        site_layout.addWidget(self.refresh_sites_btn, 1)
        site_section.content_layout.addLayout(site_layout)

        # List selection
        list_layout = QHBoxLayout()
        list_layout.setSpacing(12)
        list_combo = HolographicComboBox()
        list_combo.setMinimumHeight(40)
        self.form_fields["sharepoint_list"] = FormField("List Name", list_combo)
        self.refresh_lists_btn = ActionButton.ghost("🔄 Refresh", size="md")
        self.refresh_lists_btn.setMinimumWidth(120)
        self.refresh_lists_btn.clicked.connect(self.refresh_lists_requested)

        list_layout.addWidget(self.form_fields["sharepoint_list"], 3)
        list_layout.addWidget(self.refresh_lists_btn, 1)
        site_section.content_layout.addLayout(list_layout)

        layout.addWidget(site_section)

        # Test button
        test_btn_layout = QHBoxLayout()
        test_btn_layout.addStretch()
        test_btn = ActionButton.primary("🧪 Test SharePoint Connection", size="lg")
        test_btn.setMinimumHeight(50)
        test_btn.clicked.connect(self.test_sharepoint_requested)
        test_btn_layout.addWidget(test_btn)
        test_btn_layout.addStretch()
        layout.addLayout(test_btn_layout)

        layout.addStretch()
        self.tab_widget.addTab(tab, "SharePoint")

    def _create_better_database_tab(self):
        """แก้แล้ว: Database tab ที่ดูดีขึ้น"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)

        # Database Type section
        type_section = SectionFrame("🗄️ Database Type")

        db_type_field = FormField("Database Type", HolographicComboBox())
        db_type_field.input_widget.setMinimumHeight(40)
        db_type_field.input_widget.addItems(["SQL Server", "SQLite"])
        self.form_fields["db_type"] = db_type_field
        db_type_field.input_widget.currentTextChanged.connect(self._on_db_type_changed)
        type_section.content_layout.addWidget(db_type_field)

        layout.addWidget(type_section)

        # SQL Server section
        self.sql_section = SectionFrame("💾 SQL Server Configuration")

        # Server และ Username
        server_user_layout = QHBoxLayout()
        server_user_layout.setSpacing(16)

        server_field = FormField(
            "Server Instance", ModernLineEdit("localhost\\SQLEXPRESS")
        )
        server_field.input_widget.setMinimumHeight(40)
        self.form_fields["db_host"] = server_field

        username_field = FormField("Username", ModernLineEdit("sa"))
        username_field.input_widget.setMinimumHeight(40)
        self.form_fields["db_username"] = username_field

        server_user_layout.addWidget(server_field)
        server_user_layout.addWidget(username_field)
        self.sql_section.content_layout.addLayout(server_user_layout)

        # Password
        password_field = FormField("Password", PasswordField("password"))
        password_field.input_widget.setMinimumHeight(40)
        self.form_fields["db_password"] = password_field
        self.sql_section.content_layout.addWidget(password_field)

        # Database และ Table
        db_table_layout = QHBoxLayout()
        db_table_layout.setSpacing(12)

        db_combo = HolographicComboBox()
        db_combo.setEditable(True)
        db_combo.setMinimumHeight(40)
        self.form_fields["db_name"] = FormField("Database Name", db_combo)
        self.refresh_dbs_btn = ActionButton.ghost("🔄", size="md")
        self.refresh_dbs_btn.setMinimumWidth(80)
        self.refresh_dbs_btn.clicked.connect(self.refresh_databases_requested)

        table_combo = HolographicComboBox()
        table_combo.setEditable(True)
        table_combo.setMinimumHeight(40)
        self.form_fields["db_table"] = FormField("Table Name", table_combo)
        self.refresh_tables_btn = ActionButton.ghost("🔄", size="md")
        self.refresh_tables_btn.setMinimumWidth(80)
        self.refresh_tables_btn.clicked.connect(self.refresh_tables_requested)

        db_table_layout.addWidget(self.form_fields["db_name"], 2)
        db_table_layout.addWidget(self.refresh_dbs_btn)
        db_table_layout.addWidget(self.form_fields["db_table"], 2)
        db_table_layout.addWidget(self.refresh_tables_btn)
        self.sql_section.content_layout.addLayout(db_table_layout)

        layout.addWidget(self.sql_section)

        # SQLite section
        self.sqlite_section = SectionFrame("📄 SQLite Configuration")

        sqlite_layout = QHBoxLayout()
        sqlite_layout.setSpacing(16)

        sqlite_file_field = FormField(
            "Database File Path", ModernLineEdit("data/database.db")
        )
        sqlite_file_field.input_widget.setMinimumHeight(40)
        self.form_fields["sqlite_file"] = sqlite_file_field

        sqlite_table_field = FormField("Table Name", ModernLineEdit("sharepoint_data"))
        sqlite_table_field.input_widget.setMinimumHeight(40)
        self.form_fields["sqlite_table_name"] = sqlite_table_field

        sqlite_layout.addWidget(sqlite_file_field)
        sqlite_layout.addWidget(sqlite_table_field)
        self.sqlite_section.content_layout.addLayout(sqlite_layout)

        layout.addWidget(self.sqlite_section)

        # Test button
        test_btn_layout = QHBoxLayout()
        test_btn_layout.addStretch()
        test_btn = ActionButton.primary("🧪 Test Database Connection", size="lg")
        test_btn.setMinimumHeight(50)
        test_btn.clicked.connect(self.test_database_requested)
        test_btn_layout.addWidget(test_btn)
        test_btn_layout.addStretch()
        layout.addLayout(test_btn_layout)

        layout.addStretch()
        self.tab_widget.addTab(tab, "Database")

        # Initially show SQL Server
        self._on_db_type_changed("SQL Server")

    def _create_better_settings_tab(self):
        """แก้แล้ว: Settings tab ที่ดูดีขึ้น"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(20)

        # Performance section
        perf_section = SectionFrame("⚡ Performance & Sync Settings")

        perf_layout = QHBoxLayout()
        perf_layout.setSpacing(16)

        interval_field = FormField(
            "Sync Interval (minutes)", ModernSpinBox(1, 1440, 60, "min")
        )
        interval_field.input_widget.setMinimumHeight(40)
        self.form_fields["sync_interval"] = interval_field

        batch_field = FormField(
            "Batch Size (records)", ModernSpinBox(100, 10000, 1000, "records")
        )
        batch_field.input_widget.setMinimumHeight(40)
        self.form_fields["batch_size"] = batch_field

        perf_layout.addWidget(interval_field)
        perf_layout.addWidget(batch_field)
        perf_section.content_layout.addLayout(perf_layout)

        # Log Level
        log_level_field = FormField("Logging Level", HolographicComboBox())
        log_level_field.input_widget.setMinimumHeight(40)
        log_level_field.input_widget.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.form_fields["log_level"] = log_level_field
        perf_section.content_layout.addWidget(log_level_field)

        layout.addWidget(perf_section)

        layout.addStretch()
        self.tab_widget.addTab(tab, "Settings")

    def _on_db_type_changed(self, db_type):
        """แก้แล้ว: เปลี่ยน UI ตามประเภทฐานข้อมูล"""
        if db_type == "SQL Server":
            self.sql_section.setVisible(True)
            self.sqlite_section.setVisible(False)
        else:  # SQLite
            self.sql_section.setVisible(False)
            self.sqlite_section.setVisible(True)

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
    def _save_config_from_ui(self, *args):
        """แก้แล้ว: บันทึก config จาก UI รับ args ใดๆ"""
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
