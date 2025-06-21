# ui/components/config_panel.py - Modern 2025 Config Panel
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import sys
from pathlib import Path

current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from ui.styles.theme import ModernColors, Typography, BorderRadius, Spacing
    from ui.widgets.modern_button import ActionButton, IconButton
    from ui.widgets.modern_input import *
    from utils.config_manager import get_config_manager
except ImportError as e:
    print(f"Config panel import error: {e}")


class ConfigSection(QWidget):
    """Collapsible configuration section"""

    def __init__(self, title, icon="", parent=None):
        super().__init__(parent)
        self.title = title
        self.icon = icon
        self.is_expanded = False
        self.content_widget = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header button
        self.header_btn = QPushButton(f"{self.icon} {self.title}")
        self.header_btn.setCheckable(True)
        self.header_btn.clicked.connect(self._toggle_section)
        self.header_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {ModernColors.SURFACE_TERTIARY};
                border: 1px solid {ModernColors.GLASS_BORDER};
                border-radius: {BorderRadius.BASE}px;
                padding: 12px 16px;
                text-align: left;
                font-size: {Typography.TEXT_BASE}px;
                font-weight: {Typography.WEIGHT_MEDIUM};
                color: {ModernColors.TEXT_PRIMARY};
            }}
            QPushButton:hover {{
                background: {ModernColors.SURFACE_ELEVATED};
                border-color: {ModernColors.PRIMARY};
            }}
            QPushButton:checked {{
                background: {ModernColors.PRIMARY};
                color: white;
            }}
        """
        )
        layout.addWidget(self.header_btn)

        # Content container
        self.content_container = QWidget()
        self.content_container.hide()
        self.content_container.setStyleSheet(
            f"""
            QWidget {{
                background: {ModernColors.SURFACE_SECONDARY};
                border: 1px solid {ModernColors.GLASS_BORDER};
                border-top: none;
                border-radius: 0 0 {BorderRadius.BASE}px {BorderRadius.BASE}px;
                padding: 16px;
            }}
        """
        )
        layout.addWidget(self.content_container)

        # Content layout
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(12)

    def add_content(self, widget):
        """Add widget to section content"""
        self.content_layout.addWidget(widget)

    def _toggle_section(self, checked):
        """Toggle section visibility"""
        self.is_expanded = checked
        if checked:
            self.content_container.show()
            self.header_btn.setText(f"{self.icon} {self.title} ▼")
        else:
            self.content_container.hide()
            self.header_btn.setText(f"{self.icon} {self.title} ▶")

    def set_expanded(self, expanded):
        """Programmatically expand/collapse section"""
        self.header_btn.setChecked(expanded)
        self._toggle_section(expanded)


class SharePointConfigSection(ConfigSection):
    """SharePoint configuration section"""

    def __init__(self, parent=None):
        super().__init__("SharePoint Configuration", "🔗", parent)
        self._setup_content()

    def _setup_content(self):
        # Site URL
        self.site_field = create_text_field(
            "https://company.sharepoint.com/sites/site", "Site URL", True
        )
        self.add_content(self.site_field)

        # List Name
        self.list_field = create_text_field("List name", "List Name", True)
        self.add_content(self.list_field)

        # Authentication section
        auth_group = QGroupBox("Authentication")
        auth_group.setStyleSheet(
            f"""
            QGroupBox {{
                font-weight: {Typography.WEIGHT_MEDIUM};
                color: {ModernColors.TEXT_PRIMARY};
                border: 1px solid {ModernColors.GLASS_BORDER};
                border-radius: {BorderRadius.SM}px;
                margin-top: 8px;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px;
            }}
        """
        )

        auth_layout = QVBoxLayout(auth_group)
        auth_layout.setSpacing(12)

        self.client_id_field = create_text_field("Client ID (GUID)", "Client ID", True)
        auth_layout.addWidget(self.client_id_field)

        self.client_secret_field = create_password_field("Client Secret", True)
        auth_layout.addWidget(self.client_secret_field)

        self.tenant_id_field = create_text_field("Tenant ID (GUID)", "Tenant ID", True)
        auth_layout.addWidget(self.tenant_id_field)

        self.add_content(auth_group)

        # Test button
        test_btn = ActionButton.secondary("🔍 Test Connection", size="sm")
        test_btn.clicked.connect(self._test_sharepoint)
        self.add_content(test_btn)

    def _test_sharepoint(self):
        """Test SharePoint connection"""
        # Implement test logic
        pass

    def get_config(self):
        """Get SharePoint configuration"""
        return {
            "sharepoint_site": self.site_field.get_value(),
            "sharepoint_list": self.list_field.get_value(),
            "sharepoint_client_id": self.client_id_field.get_value(),
            "sharepoint_client_secret": self.client_secret_field.get_value(),
            "tenant_id": self.tenant_id_field.get_value(),
        }

    def set_config(self, config):
        """Set SharePoint configuration"""
        self.site_field.set_value(config.get("sharepoint_site", ""))
        self.list_field.set_value(config.get("sharepoint_list", ""))
        self.client_id_field.set_value(config.get("sharepoint_client_id", ""))
        self.client_secret_field.set_value(config.get("sharepoint_client_secret", ""))
        self.tenant_id_field.set_value(config.get("tenant_id", ""))


class DatabaseConfigSection(ConfigSection):
    """Database configuration section"""

    def __init__(self, parent=None):
        super().__init__("Database Configuration", "🗄️", parent)
        self._setup_content()

    def _setup_content(self):
        # Database type selector
        self.db_type_field = create_dropdown_field(
            ["SQL Server", "SQLite"], "Database Type", True
        )
        self.db_type_field.input_widget.currentTextChanged.connect(
            self._on_db_type_changed
        )
        self.add_content(self.db_type_field)

        # SQL Server section
        self.sql_section = QWidget()
        sql_layout = QVBoxLayout(self.sql_section)
        sql_layout.setSpacing(12)

        self.server_field = create_text_field(
            "Server\\Instance or IP:Port", "Server", True
        )
        sql_layout.addWidget(self.server_field)

        self.database_field = create_text_field("Database name", "Database", True)
        sql_layout.addWidget(self.database_field)

        # Credentials in horizontal layout
        cred_layout = QHBoxLayout()
        cred_layout.setSpacing(12)

        self.username_field = create_text_field("Username", "Username", True)
        cred_layout.addWidget(self.username_field)

        self.password_field = create_password_field("Password", True)
        cred_layout.addWidget(self.password_field)

        sql_layout.addLayout(cred_layout)

        self.add_content(self.sql_section)

        # SQLite section
        self.sqlite_section = QWidget()
        sqlite_layout = QVBoxLayout(self.sqlite_section)

        self.sqlite_file_field = FileUploadField("SQLite Files (*.db *.sqlite)")
        sqlite_layout.addWidget(QLabel("Database File:"))
        sqlite_layout.addWidget(self.sqlite_file_field)

        self.add_content(self.sqlite_section)
        self.sqlite_section.hide()

        # Test button
        test_btn = ActionButton.secondary("🔍 Test Connection", size="sm")
        test_btn.clicked.connect(self._test_database)
        self.add_content(test_btn)

    def _on_db_type_changed(self, db_type):
        """Handle database type change"""
        if db_type == "SQL Server":
            self.sql_section.show()
            self.sqlite_section.hide()
        else:
            self.sql_section.hide()
            self.sqlite_section.show()

    def _test_database(self):
        """Test database connection"""
        pass

    def get_config(self):
        """Get database configuration"""
        db_type = self.db_type_field.get_value()
        config = {"database_type": "sqlserver" if db_type == "SQL Server" else "sqlite"}

        if db_type == "SQL Server":
            config.update(
                {
                    "sql_server": self.server_field.get_value(),
                    "sql_database": self.database_field.get_value(),
                    "sql_username": self.username_field.get_value(),
                    "sql_password": self.password_field.get_value(),
                }
            )
        else:
            config.update({"sqlite_file": self.sqlite_file_field.file_label.text()})

        return config

    def set_config(self, config):
        """Set database configuration"""
        db_type = (
            "SQL Server" if config.get("database_type") == "sqlserver" else "SQLite"
        )
        self.db_type_field.set_value(db_type)
        self._on_db_type_changed(db_type)

        if db_type == "SQL Server":
            self.server_field.set_value(config.get("sql_server", ""))
            self.database_field.set_value(config.get("sql_database", ""))
            self.username_field.set_value(config.get("sql_username", ""))
            self.password_field.set_value(config.get("sql_password", ""))


class SyncConfigSection(ConfigSection):
    """Synchronization configuration section"""

    def __init__(self, parent=None):
        super().__init__("Sync Configuration", "🔄", parent)
        self._setup_content()

    def _setup_content(self):
        # Auto sync settings
        auto_sync_layout = QHBoxLayout()

        self.auto_sync_check = ModernCheckBox("Enable Auto Sync")
        auto_sync_layout.addWidget(self.auto_sync_check)

        auto_sync_layout.addStretch()

        self.interval_field = create_number_field(1, 1440, "Interval (min)", False)
        self.interval_field.set_value(10)
        auto_sync_layout.addWidget(self.interval_field)

        auto_sync_widget = QWidget()
        auto_sync_widget.setLayout(auto_sync_layout)
        self.add_content(auto_sync_widget)

        # Sync direction
        direction_layout = QHBoxLayout()

        direction_layout.addWidget(QLabel("Direction:"))

        self.direction_combo = ModernComboBox()
        self.direction_combo.addItems(
            ["SharePoint → SQL", "SQL → SharePoint", "Bidirectional"]
        )
        direction_layout.addWidget(self.direction_combo)
        direction_layout.addStretch()

        direction_widget = QWidget()
        direction_widget.setLayout(direction_layout)
        self.add_content(direction_widget)

        # Batch settings
        batch_layout = QHBoxLayout()

        self.batch_size_field = create_number_field(100, 10000, "Batch Size", False)
        self.batch_size_field.set_value(1000)
        batch_layout.addWidget(self.batch_size_field)

        self.timeout_field = create_number_field(10, 300, "Timeout (sec)", False)
        self.timeout_field.set_value(30)
        batch_layout.addWidget(self.timeout_field)

        batch_widget = QWidget()
        batch_widget.setLayout(batch_layout)
        self.add_content(batch_widget)

    def get_config(self):
        """Get sync configuration"""
        direction_map = {
            "SharePoint → SQL": "spo_to_sql",
            "SQL → SharePoint": "sql_to_spo",
            "Bidirectional": "bidirectional",
        }

        return {
            "auto_sync_enabled": self.auto_sync_check.isChecked(),
            "sync_interval": self.interval_field.get_value() * 60,  # Convert to seconds
            "auto_sync_direction": direction_map.get(
                self.direction_combo.currentText(), "spo_to_sql"
            ),
            "batch_size": self.batch_size_field.get_value(),
            "connection_timeout": self.timeout_field.get_value(),
        }

    def set_config(self, config):
        """Set sync configuration"""
        self.auto_sync_check.setChecked(config.get("auto_sync_enabled", False))
        self.interval_field.set_value(
            config.get("sync_interval", 600) // 60
        )  # Convert to minutes

        direction_map = {
            "spo_to_sql": "SharePoint → SQL",
            "sql_to_spo": "SQL → SharePoint",
            "bidirectional": "Bidirectional",
        }
        direction = direction_map.get(config.get("auto_sync_direction", "spo_to_sql"))
        self.direction_combo.setCurrentText(direction)

        self.batch_size_field.set_value(config.get("batch_size", 1000))
        self.timeout_field.set_value(config.get("connection_timeout", 30))


class ConfigPanel(QWidget):
    """Main 2025 Modern Configuration Panel"""

    # Signals
    config_changed = pyqtSignal()
    test_connection_requested = pyqtSignal(str)  # connection_type

    def __init__(self, controller=None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.config_manager = get_config_manager()
        self._setup_ui()
        self._load_config()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Configuration")
        title.setStyleSheet(
            f"""
            font-size: {Typography.TEXT_2XL}px;
            font-weight: {Typography.WEIGHT_BOLD};
            color: {ModernColors.TEXT_PRIMARY};
        """
        )
        header_layout.addWidget(title)
        header_layout.addStretch()

        # Header actions
        save_btn = ActionButton.primary("💾 Save", size="sm")
        save_btn.clicked.connect(self._save_config)
        header_layout.addWidget(save_btn)

        reset_btn = ActionButton.ghost("🔄 Reset", size="sm")
        reset_btn.clicked.connect(self._reset_config)
        header_layout.addWidget(reset_btn)

        layout.addLayout(header_layout)

        # Scroll area for sections
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(12)

        # Configuration sections
        self.sharepoint_section = SharePointConfigSection()
        self.sharepoint_section.set_expanded(True)  # Expand first section by default
        content_layout.addWidget(self.sharepoint_section)

        self.database_section = DatabaseConfigSection()
        content_layout.addWidget(self.database_section)

        self.sync_section = SyncConfigSection()
        content_layout.addWidget(self.sync_section)

        # Field mapping section
        self.mapping_section = self._create_mapping_section()
        content_layout.addWidget(self.mapping_section)

        content_layout.addStretch()
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)

        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(
            f"""
            color: {ModernColors.TEXT_SECONDARY};
            font-size: {Typography.TEXT_SM}px;
            padding: 8px;
        """
        )
        layout.addWidget(self.status_label)

    def _create_mapping_section(self):
        """Create field mapping section"""
        section = ConfigSection("Field Mapping", "🔗")

        # Mapping tables container
        mapping_container = QWidget()
        mapping_layout = QHBoxLayout(mapping_container)
        mapping_layout.setSpacing(16)

        # SharePoint to SQL mapping
        spo_to_sql_group = QGroupBox("SharePoint → SQL")
        spo_to_sql_group.setStyleSheet(
            f"""
            QGroupBox {{
                font-weight: {Typography.WEIGHT_MEDIUM};
                color: {ModernColors.TEXT_PRIMARY};
                border: 1px solid {ModernColors.GLASS_BORDER};
                border-radius: {BorderRadius.SM}px;
                margin-top: 8px;
                padding-top: 12px;
            }}
        """
        )

        spo_sql_layout = QVBoxLayout(spo_to_sql_group)

        self.spo_to_sql_table = self._create_mapping_table()
        spo_sql_layout.addWidget(self.spo_to_sql_table)

        spo_sql_btn_layout = QHBoxLayout()
        add_spo_sql_btn = IconButton("➕", tooltip="Add mapping", size="sm")
        remove_spo_sql_btn = IconButton("➖", tooltip="Remove mapping", size="sm")
        add_spo_sql_btn.clicked.connect(
            lambda: self._add_mapping_row(self.spo_to_sql_table)
        )
        remove_spo_sql_btn.clicked.connect(
            lambda: self._remove_mapping_row(self.spo_to_sql_table)
        )

        spo_sql_btn_layout.addWidget(add_spo_sql_btn)
        spo_sql_btn_layout.addWidget(remove_spo_sql_btn)
        spo_sql_btn_layout.addStretch()
        spo_sql_layout.addLayout(spo_sql_btn_layout)

        mapping_layout.addWidget(spo_to_sql_group)

        # SQL to SharePoint mapping
        sql_to_spo_group = QGroupBox("SQL → SharePoint")
        sql_to_spo_group.setStyleSheet(
            f"""
            QGroupBox {{
                font-weight: {Typography.WEIGHT_MEDIUM};
                color: {ModernColors.TEXT_PRIMARY};
                border: 1px solid {ModernColors.GLASS_BORDER};
                border-radius: {BorderRadius.SM}px;
                margin-top: 8px;
                padding-top: 12px;
            }}
        """
        )

        sql_spo_layout = QVBoxLayout(sql_to_spo_group)

        self.sql_to_spo_table = self._create_mapping_table()
        sql_spo_layout.addWidget(self.sql_to_spo_table)

        sql_spo_btn_layout = QHBoxLayout()
        add_sql_spo_btn = IconButton("➕", tooltip="Add mapping", size="sm")
        remove_sql_spo_btn = IconButton("➖", tooltip="Remove mapping", size="sm")
        add_sql_spo_btn.clicked.connect(
            lambda: self._add_mapping_row(self.sql_to_spo_table)
        )
        remove_sql_spo_btn.clicked.connect(
            lambda: self._remove_mapping_row(self.sql_to_spo_table)
        )

        sql_spo_btn_layout.addWidget(add_sql_spo_btn)
        sql_spo_btn_layout.addWidget(remove_sql_spo_btn)
        sql_spo_btn_layout.addStretch()
        sql_spo_layout.addLayout(sql_spo_btn_layout)

        mapping_layout.addWidget(sql_to_spo_group)

        section.add_content(mapping_container)
        return section

    def _create_mapping_table(self):
        """Create mapping table widget"""
        table = QTableWidget(3, 2)
        table.setHorizontalHeaderLabels(["Source Field", "Target Field"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        table.setMaximumHeight(150)

        table.setStyleSheet(
            f"""
            QTableWidget {{
                background: {ModernColors.SURFACE_PRIMARY};
                border: 1px solid {ModernColors.GLASS_BORDER};
                border-radius: {BorderRadius.SM}px;
                gridline-color: {ModernColors.GLASS_BORDER};
                color: {ModernColors.TEXT_PRIMARY};
                font-size: {Typography.TEXT_SM}px;
            }}
            QTableWidget::item {{
                padding: 6px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background: {ModernColors.PRIMARY};
            }}
            QHeaderView::section {{
                background: {ModernColors.SURFACE_TERTIARY};
                border: 1px solid {ModernColors.GLASS_BORDER};
                padding: 6px;
                font-weight: {Typography.WEIGHT_MEDIUM};
            }}
        """
        )

        return table

    def _add_mapping_row(self, table):
        """Add new row to mapping table"""
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(""))
        table.setItem(row, 1, QTableWidgetItem(""))

    def _remove_mapping_row(self, table):
        """Remove selected row from mapping table"""
        current_row = table.currentRow()
        if current_row >= 0:
            table.removeRow(current_row)

    def _get_mapping_from_table(self, table):
        """Get mapping dictionary from table"""
        mapping = {}
        for row in range(table.rowCount()):
            source_item = table.item(row, 0)
            target_item = table.item(row, 1)
            if source_item and target_item:
                source = source_item.text().strip()
                target = target_item.text().strip()
                if source and target:
                    mapping[source] = target
        return mapping

    def _set_mapping_to_table(self, table, mapping):
        """Set mapping dictionary to table"""
        table.setRowCount(max(len(mapping), 3))
        for row, (source, target) in enumerate(mapping.items()):
            table.setItem(row, 0, QTableWidgetItem(source))
            table.setItem(row, 1, QTableWidgetItem(target))

    def _load_config(self):
        """Load configuration from config manager"""
        try:
            config = self.config_manager.get_config()

            # Load section configs
            self.sharepoint_section.set_config(config.__dict__)
            self.database_section.set_config(config.__dict__)
            self.sync_section.set_config(config.__dict__)

            # Load mappings
            self._set_mapping_to_table(
                self.spo_to_sql_table, getattr(config, "sharepoint_to_sql_mapping", {})
            )
            self._set_mapping_to_table(
                self.sql_to_spo_table, getattr(config, "sql_to_sharepoint_mapping", {})
            )

            self.status_label.setText("Configuration loaded")

        except Exception as e:
            self.status_label.setText(f"Error loading config: {e}")

    def _save_config(self):
        """Save configuration"""
        try:
            # Collect all configuration
            config_data = {}
            config_data.update(self.sharepoint_section.get_config())
            config_data.update(self.database_section.get_config())
            config_data.update(self.sync_section.get_config())

            # Add mappings
            config_data["sharepoint_to_sql_mapping"] = self._get_mapping_from_table(
                self.spo_to_sql_table
            )
            config_data["sql_to_sharepoint_mapping"] = self._get_mapping_from_table(
                self.sql_to_spo_table
            )

            # Update config manager
            for key, value in config_data.items():
                self.config_manager.update_setting(key, value)

            self.config_manager.save_config()
            self.config_changed.emit()
            self.status_label.setText("✅ Configuration saved successfully")

        except Exception as e:
            self.status_label.setText(f"❌ Error saving config: {e}")

    def _reset_config(self):
        """Reset configuration to defaults"""
        reply = QMessageBox.question(
            self,
            "Reset Configuration",
            "Are you sure you want to reset all settings to default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.config_manager.reload_config()
                self._load_config()
                self.status_label.setText("Configuration reset to defaults")
            except Exception as e:
                self.status_label.setText(f"Error resetting config: {e}")

    def cleanup(self):
        """Cleanup config panel"""
        try:
            # Clear any timers or connections
            pass
        except Exception as e:
            print(f"Config panel cleanup error: {e}")


# Factory function
def create_config_panel(controller=None, parent=None):
    """Create modern config panel instance"""
    return ConfigPanel(controller, parent)
