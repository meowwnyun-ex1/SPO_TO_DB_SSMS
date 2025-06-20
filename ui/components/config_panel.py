from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QLabel,
    QFrame,
    QFileDialog,
    QScrollArea,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QSpinBox,
)
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt6.QtGui import QFont

# ใช้ relative imports
try:
    from ..styles.theme import (
        get_modern_tab_style,
        UltraModernColors,
    )
    from ..widgets.modern_button import ActionButton
    from ..widgets.modern_input import (
        ModernLineEdit,
        ModernSpinBox,
        FormField,
        PasswordField,
    )
    from ..widgets.holographic_combobox import HolographicComboBox
except ImportError:
    # Fallback imports
    import sys
    import os

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from ui.styles.theme import (
        get_modern_tab_style,
        UltraModernColors,
    )
    from ui.widgets.modern_button import ActionButton
    from ui.widgets.modern_input import (
        ModernLineEdit,
        ModernSpinBox,
        FormField,
        PasswordField,
    )
    from ui.widgets.holographic_combobox import HolographicComboBox

from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity
import logging

logger = logging.getLogger(__name__)


class CompactFormField(QWidget):
    """Compact form field สำหรับพื้นที่จำกัด"""

    def __init__(self, label_text, input_widget, parent=None):
        super().__init__(parent)
        self.input_widget = input_widget
        self.setup_ui(label_text)

    def setup_ui(self, label_text):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Compact label
        label = QLabel(label_text)
        label.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        label.setStyleSheet(
            f"color: {UltraModernColors.TEXT_ACCENT}; margin-bottom: 2px;"
        )
        layout.addWidget(label)

        # Input widget
        self.input_widget.setMinimumHeight(28)  # ลดความสูง
        self.input_widget.setMaximumHeight(28)
        layout.addWidget(self.input_widget)

    def get_value(self):
        """Get input value"""
        if isinstance(self.input_widget, (QLineEdit, QTextEdit)):
            return (
                self.input_widget.text()
                if isinstance(self.input_widget, QLineEdit)
                else self.input_widget.toPlainText()
            )
        elif isinstance(self.input_widget, QComboBox):
            return self.input_widget.currentText()
        elif isinstance(self.input_widget, QSpinBox):
            return self.input_widget.value()
        return None

    def set_value(self, value):
        """Set input value"""
        if isinstance(self.input_widget, QLineEdit):
            self.input_widget.setText(str(value))
        elif isinstance(self.input_widget, QTextEdit):
            self.input_widget.setPlainText(str(value))
        elif isinstance(self.input_widget, QComboBox):
            index = self.input_widget.findText(str(value))
            if index >= 0:
                self.input_widget.setCurrentIndex(index)
        elif isinstance(self.input_widget, QSpinBox):
            self.input_widget.setValue(int(value))


class CompactSectionFrame(QFrame):
    """Compact section frame"""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(
            f"""
            QFrame {{
                background: {UltraModernColors.GLASS_BG_DARK};
                border: 1px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 8px;
                margin: 4px;
                padding: 8px;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        # Compact title
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title_label.setStyleSheet(
            f"""
            QLabel {{
                color: {UltraModernColors.TEXT_PRIMARY};
                background: {UltraModernColors.GLASS_BG};
                border: 1px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 6px;
                padding: 4px 8px;
                margin-bottom: 6px;
            }}
            """
        )
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Content area
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(6)
        content_widget = QWidget()
        content_widget.setLayout(self.content_layout)
        layout.addWidget(content_widget)


class ExcelImportSection(QWidget):
    """ส่วน Excel Import ใหม่"""

    excel_file_selected = pyqtSignal(str, str)  # file_path, target_type

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)

        # File selection
        file_layout = QHBoxLayout()

        self.file_path_field = ModernLineEdit("Select Excel file...")
        self.file_path_field.setReadOnly(True)
        self.file_path_field.setMinimumHeight(28)

        self.browse_btn = ActionButton.secondary("📁", size="sm")
        self.browse_btn.setMaximumWidth(35)
        self.browse_btn.setMinimumHeight(28)
        self.browse_btn.clicked.connect(self._browse_file)

        file_layout.addWidget(self.file_path_field)
        file_layout.addWidget(self.browse_btn)
        layout.addLayout(file_layout)

        # Target selection
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Import to:"))

        self.import_to_spo_btn = ActionButton.primary("→ SharePoint", size="sm")
        self.import_to_spo_btn.setMaximumHeight(28)
        self.import_to_spo_btn.clicked.connect(lambda: self._import_excel("spo"))

        self.import_to_sql_btn = ActionButton.primary("→ Database", size="sm")
        self.import_to_sql_btn.setMaximumHeight(28)
        self.import_to_sql_btn.clicked.connect(lambda: self._import_excel("sql"))

        target_layout.addWidget(self.import_to_spo_btn)
        target_layout.addWidget(self.import_to_sql_btn)
        target_layout.addStretch()
        layout.addLayout(target_layout)

    def _browse_file(self):
        """Browse for Excel file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Excel File", "", "Excel Files (*.xlsx *.xls);;All Files (*)"
        )
        if file_path:
            self.file_path_field.setText(file_path)

    def _import_excel(self, target_type):
        """Import Excel file"""
        file_path = self.file_path_field.text()
        if file_path and file_path != "Select Excel file...":
            self.excel_file_selected.emit(file_path, target_type)


class ModernConfigPanel(QWidget):
    """Enhanced Config Panel สำหรับขนาด 900x500"""

    # Signals
    config_changed = pyqtSignal(object)
    test_sharepoint_requested = pyqtSignal()
    test_database_requested = pyqtSignal()
    refresh_sites_requested = pyqtSignal()
    refresh_lists_requested = pyqtSignal()
    refresh_databases_requested = pyqtSignal()
    refresh_tables_requested = pyqtSignal()
    auto_sync_toggled = pyqtSignal(bool)
    excel_import_requested = pyqtSignal(str, str)  # file_path, target_type

    def __init__(self, controller):
        super().__init__(parent=None)
        self.controller = controller
        self.form_fields = {}

        self.setup_compact_ui()
        self._load_config_to_ui()

    def setup_compact_ui(self):
        """Setup compact UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Compact header
        header_frame = QFrame()
        header_frame.setStyleSheet(
            f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {UltraModernColors.NEON_PURPLE},
                    stop:1 {UltraModernColors.NEON_PINK}
                );
                border-radius: 8px;
                padding: 8px;
                margin-bottom: 8px;
            }}
            """
        )

        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(12, 6, 12, 6)

        header_icon = QLabel("⚙️")
        header_icon.setFont(QFont("Segoe UI Emoji", 16))
        header_icon.setStyleSheet("color: white;")

        header_text = QLabel("Configuration")
        header_text.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        header_text.setStyleSheet("color: white;")

        header_layout.addWidget(header_icon)
        header_layout.addWidget(header_text)
        header_layout.addStretch()

        layout.addWidget(header_frame)

        # Compact tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(
            get_modern_tab_style()
            + f"""
            QTabWidget::pane {{
                border: 1px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 8px;
                background: {UltraModernColors.GLASS_BG_DARK};
                margin-top: 8px;
            }}
            QTabBar::tab {{
                background: {UltraModernColors.GLASS_BG};
                border: 1px solid {UltraModernColors.GLASS_BORDER};
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 6px 12px;
                color: {UltraModernColors.TEXT_PRIMARY};
                font-weight: bold;
                font-size: 10px;
                margin-right: 2px;
                min-width: 60px;
            }}
            QTabBar::tab:selected {{
                background: {UltraModernColors.NEON_PURPLE};
                border: 1px solid {UltraModernColors.NEON_PINK};
                color: white;
            }}
            """
        )

        # Create tabs - ให้ tab สั้นลง
        self._create_sharepoint_tab()
        self._create_database_tab()
        self._create_excel_tab()  # Tab ใหม่
        self._create_settings_tab()

        layout.addWidget(self.tab_widget)
        self._connect_signals()

    def _create_sharepoint_tab(self):
        """Compact SharePoint tab"""
        tab = QWidget()

        # Use scroll area for compact space
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Connection section
        conn_section = CompactSectionFrame("🔗 Connection")

        # URL และ Tenant ID - แนวนอน
        url_layout = QHBoxLayout()
        url_layout.setSpacing(8)

        url_field = CompactFormField(
            "SharePoint URL",
            ModernLineEdit("https://company.sharepoint.com/sites/sitename"),
        )
        self.form_fields["sharepoint_url"] = url_field

        tenant_field = CompactFormField(
            "Tenant ID", ModernLineEdit("12345678-1234-1234-1234-123456789012")
        )
        self.form_fields["tenant_id"] = tenant_field

        url_layout.addWidget(url_field)
        url_layout.addWidget(tenant_field)
        conn_section.content_layout.addLayout(url_layout)

        # Client credentials - แนวนอน
        auth_layout = QHBoxLayout()
        auth_layout.setSpacing(8)

        client_id_field = CompactFormField(
            "Client ID", ModernLineEdit("87654321-4321-4321-4321-210987654321")
        )
        self.form_fields["sharepoint_client_id"] = client_id_field

        client_secret_field = CompactFormField(
            "Client Secret", PasswordField("Your-Client-Secret-Here")
        )
        self.form_fields["sharepoint_client_secret"] = client_secret_field

        auth_layout.addWidget(client_id_field)
        auth_layout.addWidget(client_secret_field)
        conn_section.content_layout.addLayout(auth_layout)

        layout.addWidget(conn_section)

        # Site & List section
        site_section = CompactSectionFrame("📋 Site & List")

        # Site selection - แนวนอน
        site_layout = QHBoxLayout()
        site_layout.setSpacing(6)
        site_combo = HolographicComboBox()
        site_combo.setMinimumHeight(28)
        self.form_fields["sharepoint_site"] = CompactFormField("Site", site_combo)
        self.refresh_sites_btn = ActionButton.ghost("🔄", size="sm")
        self.refresh_sites_btn.setMaximumWidth(30)
        self.refresh_sites_btn.setMinimumHeight(28)
        self.refresh_sites_btn.clicked.connect(self.refresh_sites_requested)

        site_layout.addWidget(self.form_fields["sharepoint_site"], 3)
        site_layout.addWidget(self.refresh_sites_btn)
        site_section.content_layout.addLayout(site_layout)

        # List selection - แนวนอน
        list_layout = QHBoxLayout()
        list_layout.setSpacing(6)
        list_combo = HolographicComboBox()
        list_combo.setMinimumHeight(28)
        self.form_fields["sharepoint_list"] = CompactFormField("List", list_combo)
        self.refresh_lists_btn = ActionButton.ghost("🔄", size="sm")
        self.refresh_lists_btn.setMaximumWidth(30)
        self.refresh_lists_btn.setMinimumHeight(28)
        self.refresh_lists_btn.clicked.connect(self.refresh_lists_requested)

        list_layout.addWidget(self.form_fields["sharepoint_list"], 3)
        list_layout.addWidget(self.refresh_lists_btn)
        site_section.content_layout.addLayout(list_layout)

        layout.addWidget(site_section)

        # Test button
        test_btn = ActionButton.primary("🧪 Test Connection", size="sm")
        test_btn.setMinimumHeight(32)
        test_btn.clicked.connect(self.test_sharepoint_requested)
        layout.addWidget(test_btn)

        layout.addStretch()
        scroll.setWidget(scroll_widget)

        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)

        self.tab_widget.addTab(tab, "SharePoint")

    def _create_database_tab(self):
        """Compact Database tab"""
        tab = QWidget()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Database Type section
        type_section = CompactSectionFrame("🗄️ Database Type")

        db_type_field = CompactFormField("Type", HolographicComboBox())
        db_type_field.input_widget.setMinimumHeight(28)
        db_type_field.input_widget.addItems(["SQL Server", "SQLite"])
        self.form_fields["db_type"] = db_type_field
        db_type_field.input_widget.currentTextChanged.connect(self._on_db_type_changed)
        type_section.content_layout.addWidget(db_type_field)

        layout.addWidget(type_section)

        # SQL Server section
        self.sql_section = CompactSectionFrame("💾 SQL Server")

        # Server และ Username - แนวนอน
        server_user_layout = QHBoxLayout()
        server_user_layout.setSpacing(8)

        server_field = CompactFormField(
            "Server", ModernLineEdit("localhost\\SQLEXPRESS")
        )
        self.form_fields["db_host"] = server_field

        username_field = CompactFormField("Username", ModernLineEdit("sa"))
        self.form_fields["db_username"] = username_field

        server_user_layout.addWidget(server_field)
        server_user_layout.addWidget(username_field)
        self.sql_section.content_layout.addLayout(server_user_layout)

        # Password
        password_field = CompactFormField("Password", PasswordField("password"))
        self.form_fields["db_password"] = password_field
        self.sql_section.content_layout.addWidget(password_field)

        # Database และ Table - แนวนอน พร้อมปุ่ม refresh
        db_table_layout = QHBoxLayout()
        db_table_layout.setSpacing(6)

        db_combo = HolographicComboBox()
        db_combo.setEditable(True)
        db_combo.setMinimumHeight(28)
        self.form_fields["db_name"] = CompactFormField("Database", db_combo)
        self.refresh_dbs_btn = ActionButton.ghost("🔄", size="sm")
        self.refresh_dbs_btn.setMaximumWidth(30)
        self.refresh_dbs_btn.setMinimumHeight(28)
        self.refresh_dbs_btn.clicked.connect(self.refresh_databases_requested)

        table_combo = HolographicComboBox()
        table_combo.setEditable(True)
        table_combo.setMinimumHeight(28)
        self.form_fields["db_table"] = CompactFormField("Table", table_combo)
        self.refresh_tables_btn = ActionButton.ghost("🔄", size="sm")
        self.refresh_tables_btn.setMaximumWidth(30)
        self.refresh_tables_btn.setMinimumHeight(28)
        self.refresh_tables_btn.clicked.connect(self.refresh_tables_requested)

        db_table_layout.addWidget(self.form_fields["db_name"], 2)
        db_table_layout.addWidget(self.refresh_dbs_btn)
        db_table_layout.addWidget(self.form_fields["db_table"], 2)
        db_table_layout.addWidget(self.refresh_tables_btn)
        self.sql_section.content_layout.addLayout(db_table_layout)

        layout.addWidget(self.sql_section)

        # SQLite section
        self.sqlite_section = CompactSectionFrame("📄 SQLite")

        sqlite_layout = QHBoxLayout()
        sqlite_layout.setSpacing(8)

        sqlite_file_field = CompactFormField(
            "File Path", ModernLineEdit("data/database.db")
        )
        self.form_fields["sqlite_file"] = sqlite_file_field

        sqlite_table_field = CompactFormField(
            "Table", ModernLineEdit("sharepoint_data")
        )
        self.form_fields["sqlite_table_name"] = sqlite_table_field

        sqlite_layout.addWidget(sqlite_file_field)
        sqlite_layout.addWidget(sqlite_table_field)
        self.sqlite_section.content_layout.addLayout(sqlite_layout)

        layout.addWidget(self.sqlite_section)

        # Test button
        test_btn = ActionButton.primary("🧪 Test Database", size="sm")
        test_btn.setMinimumHeight(32)
        test_btn.clicked.connect(self.test_database_requested)
        layout.addWidget(test_btn)

        layout.addStretch()
        scroll.setWidget(scroll_widget)

        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)

        self.tab_widget.addTab(tab, "Database")

        # Initially show SQL Server
        self._on_db_type_changed("SQL Server")

    def _create_excel_tab(self):
        """Excel Import tab ใหม่"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Excel import section
        excel_section = CompactSectionFrame("📊 Excel Import")

        self.excel_import = ExcelImportSection()
        self.excel_import.excel_file_selected.connect(self.excel_import_requested)
        excel_section.content_layout.addWidget(self.excel_import)

        layout.addWidget(excel_section)

        # Instructions
        info_section = CompactSectionFrame("ℹ️ Instructions")
        info_text = QLabel(
            """
• Select Excel file (.xlsx or .xls)
• Choose import destination (SharePoint or Database)
• First row should contain column headers
• Data will be mapped automatically
        """
        )
        info_text.setFont(QFont("Segoe UI", 9))
        info_text.setStyleSheet(
            f"color: {UltraModernColors.TEXT_SECONDARY}; padding: 8px;"
        )
        info_text.setWordWrap(True)
        info_section.content_layout.addWidget(info_text)

        layout.addWidget(info_section)
        layout.addStretch()

        self.tab_widget.addTab(tab, "Excel")

    def _create_settings_tab(self):
        """Compact Settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Performance section
        perf_section = CompactSectionFrame("⚡ Performance")

        perf_layout = QHBoxLayout()
        perf_layout.setSpacing(8)

        interval_field = CompactFormField(
            "Sync Interval (min)", ModernSpinBox(1, 1440, 60, "min")
        )
        self.form_fields["sync_interval"] = interval_field

        batch_field = CompactFormField(
            "Batch Size", ModernSpinBox(100, 10000, 1000, "")
        )
        self.form_fields["batch_size"] = batch_field

        perf_layout.addWidget(interval_field)
        perf_layout.addWidget(batch_field)
        perf_section.content_layout.addLayout(perf_layout)

        # Log Level
        log_level_field = CompactFormField("Log Level", HolographicComboBox())
        log_level_field.input_widget.setMinimumHeight(28)
        log_level_field.input_widget.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.form_fields["log_level"] = log_level_field
        perf_section.content_layout.addWidget(log_level_field)

        layout.addWidget(perf_section)
        layout.addStretch()

        self.tab_widget.addTab(tab, "Settings")

    def _on_db_type_changed(self, db_type):
        """เปลี่ยน UI ตามประเภทฐานข้อมูล"""
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
        """บันทึก config จาก UI"""
        ui_data = {}
        for field_name, field_widget in self.form_fields.items():
            ui_data[field_name] = field_widget.get_value()

        # Import config manager here to avoid circular import
        from utils.config_manager import ConfigManager

        config_manager = ConfigManager()
        config = config_manager.get_config()

        # Update config with UI data
        for key, value in ui_data.items():
            if hasattr(config, key):
                setattr(config, key, value)

        config_manager.save_config(config)
        self.config_changed.emit(config)
        logger.info("Configuration updated")

    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.LOW)
    def _load_config_to_ui(self):
        """โหลด config มาแสดงใน UI"""
        from utils.config_manager import ConfigManager

        config_manager = ConfigManager()
        config = config_manager.get_config()

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
