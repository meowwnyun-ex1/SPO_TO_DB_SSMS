# ui/components/config_panel.py - Compact Configuration Panel
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QMessageBox,
    QCheckBox,
    QLabel,
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer, pyqtSignal
import sys
import logging
from pathlib import Path

# Add project root to path for imports
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from ui.styles.theme import (
        get_modern_tab_style,
        UltraModernColors,
        get_modern_checkbox_style,
        CompactScaling,
    )
    from ui.widgets.modern_button import ModernButton
    from ui.widgets.modern_input import (
        ModernLineEdit,
        ModernSpinBox,
        FormField,
        PasswordField,
        ModernTextEdit,
    )
    from ui.widgets.holographic_combobox import HolographicComboBox
    from ui.widgets.neon_groupbox import NeonGroupBox
    from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity
    from utils.config_manager import get_simple_config_manager

except ImportError as e:
    print(f"Import error in config_panel.py: {e}")
    sys.exit(1)

logger = logging.getLogger(__name__)


class CompactFormField(QWidget):
    """Ultra-compact form field for 900x500 display"""

    def __init__(self, input_widget, label_text="", parent=None):
        super().__init__(parent)
        self.input_widget = input_widget
        self.label_text = label_text
        self._setup_ui()

    def _setup_ui(self):
        """Setup compact form layout"""
        layout = QHBoxLayout(self)  # Horizontal layout to save vertical space
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        if self.label_text:
            self.label = QLabel(self.label_text)
            self.label.setFont(
                QFont("Segoe UI", CompactScaling.FONT_SIZE_SMALL, QFont.Weight.Normal)
            )
            self.label.setStyleSheet(f"color: {UltraModernColors.TEXT_PRIMARY};")
            self.label.setMinimumWidth(100)  # Fixed width for alignment
            self.label.setMaximumWidth(100)
            layout.addWidget(self.label)

        # Handle checkbox specially
        if isinstance(self.input_widget, QCheckBox):
            # For checkboxes, no separate label needed
            layout.addWidget(self.input_widget)
            if hasattr(self, "label"):
                self.label.hide()
        else:
            self.input_widget.setMaximumHeight(22)  # Compact height
            layout.addWidget(self.input_widget)

    def get_value(self):
        """Get value from input widget"""
        if isinstance(self.input_widget, QLineEdit):
            return self.input_widget.text()
        elif isinstance(self.input_widget, ModernTextEdit):
            return self.input_widget.toPlainText()
        elif isinstance(self.input_widget, HolographicComboBox):
            return self.input_widget.currentText()
        elif isinstance(self.input_widget, ModernSpinBox):
            return self.input_widget.value()
        elif isinstance(self.input_widget, QCheckBox):
            return self.input_widget.isChecked()
        return None

    def set_value(self, value):
        """Set value to input widget"""
        if isinstance(self.input_widget, QLineEdit):
            self.input_widget.setText(str(value))
        elif isinstance(self.input_widget, ModernTextEdit):
            self.input_widget.setText(str(value))
        elif isinstance(self.input_widget, HolographicComboBox):
            index = self.input_widget.findText(str(value))
            if index >= 0:
                self.input_widget.setCurrentIndex(index)
        elif isinstance(self.input_widget, ModernSpinBox):
            self.input_widget.setValue(
                float(value) if self.input_widget.is_decimal else int(value)
            )
        elif isinstance(self.input_widget, QCheckBox):
            self.input_widget.setChecked(bool(value))


class CompactMappingTable(QWidget):
    """Compact mapping table with minimal height"""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self._setup_ui()

    def _setup_ui(self):
        """Setup compact table layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        # Title
        title_label = QLabel(self.title)
        title_label.setFont(
            QFont("Segoe UI", CompactScaling.FONT_SIZE_SMALL, QFont.Weight.Bold)
        )
        title_label.setStyleSheet(f"color: {UltraModernColors.NEON_BLUE};")
        layout.addWidget(title_label)

        # Compact table
        self.table = QTableWidget(3, 2)  # Start with 3 rows only
        self.table.setHorizontalHeaderLabels(["Source", "Target"])
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setMaximumHeight(120)  # Limit table height
        self.table.setMinimumHeight(80)

        # Style table for compact view
        self.table.setStyleSheet(
            f"""
            QTableWidget {{
                background: {UltraModernColors.GLASS_BG_DARK};
                border: 1px solid {UltraModernColors.GLASS_BORDER};
                border-radius: 3px;
                gridline-color: {UltraModernColors.GLASS_BORDER};
                font-size: {CompactScaling.FONT_SIZE_SMALL}px;
            }}
            QTableWidget::item {{
                padding: 2px;
                min-height: 18px;
            }}
            QHeaderView::section {{
                background: {UltraModernColors.GLASS_BG_LIGHT};
                border: 1px solid {UltraModernColors.GLASS_BORDER};
                padding: 3px;
                font-size: {CompactScaling.FONT_SIZE_TINY}px;
                font-weight: bold;
            }}
        """
        )
        layout.addWidget(self.table)

        # Compact button row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(2)

        self.add_button = ModernButton("+ Add", "ghost", "sm")
        self.remove_button = ModernButton("- Remove", "danger", "sm")

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch(1)

        layout.addLayout(button_layout)

        # Connect signals
        self.add_button.clicked.connect(self._add_row)
        self.remove_button.clicked.connect(self._remove_row)

    def _add_row(self):
        """Add new row to table"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(""))
        self.table.setItem(row, 1, QTableWidgetItem(""))

    def _remove_row(self):
        """Remove selected rows"""
        selected_rows = sorted(
            set(index.row() for index in self.table.selectedIndexes()), reverse=True
        )
        if not selected_rows:
            selected_rows = (
                [self.table.rowCount() - 1] if self.table.rowCount() > 0 else []
            )

        for row in selected_rows:
            self.table.removeRow(row)

    def get_mapping(self) -> dict:
        """Get mapping dictionary from table"""
        mapping = {}
        for row in range(self.table.rowCount()):
            source_item = self.table.item(row, 0)
            target_item = self.table.item(row, 1)
            if source_item and target_item:
                source = source_item.text().strip()
                target = target_item.text().strip()
                if source and target:
                    mapping[source] = target
        return mapping

    def set_mapping(self, mapping: dict):
        """Set mapping dictionary to table"""
        self.table.clearContents()
        self.table.setRowCount(max(len(mapping), 3))

        for row, (source, target) in enumerate(mapping.items()):
            self.table.setItem(row, 0, QTableWidgetItem(str(source)))
            self.table.setItem(row, 1, QTableWidgetItem(str(target)))


class ConfigPanel(QWidget):
    """
    Compact configuration panel optimized for 900x500 display.
    Uses accordion-style collapsible sections instead of tabs.
    """

    # Signals to communicate with AppController
    config_changed = pyqtSignal()
    request_auto_sync_toggle = pyqtSignal(bool)
    request_update_config_setting = pyqtSignal(str, object, str)

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.config_manager = get_simple_config_manager()
        self.cleanup_done = False

        # Timer for deferred saving
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(500)  # Faster save for compact UI
        self._save_timer.timeout.connect(self._save_all_settings)

        # Store form field widgets
        self.field_widgets = {}
        self.mapping_tables = {}

        self._setup_ui()
        self._load_current_config()
        self._connect_signals()

        logger.info("Compact ConfigPanel initialized")

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.HIGH)
    def _setup_ui(self):
        """Setup compact configuration layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        # Create scroll area for main content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        content_widget = QWidget()
        scroll_area.setWidget(content_widget)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(4, 4, 4, 4)
        content_layout.setSpacing(6)

        # Add configuration sections
        self._add_connection_section(content_layout)
        self._add_sync_section(content_layout)
        self._add_mapping_section(content_layout)

        content_layout.addStretch(1)
        main_layout.addWidget(scroll_area)

        # Add action buttons at bottom
        self._add_action_buttons(main_layout)

    def _add_connection_section(self, layout):
        """Add connection configuration section"""
        connection_group = NeonGroupBox("Connection Settings")
        connection_layout = QVBoxLayout()
        connection_layout.setSpacing(3)

        # SharePoint settings - most essential only
        sp_fields = [
            ("sharepoint_site", "SharePoint Site URL:"),
            ("sharepoint_list", "List Name:"),
            ("sharepoint_client_id", "Client ID:"),
            ("sharepoint_client_secret", "Client Secret:"),
            ("tenant_id", "Tenant ID:"),
        ]

        for field_name, label in sp_fields:
            if field_name == "sharepoint_client_secret":
                widget = PasswordField()
            else:
                widget = ModernLineEdit()

            field = CompactFormField(widget, label)
            self.field_widgets[field_name] = field
            connection_layout.addWidget(field)

        # Database settings
        db_layout = QHBoxLayout()
        db_layout.setSpacing(4)

        # Database type selector
        db_type_field = CompactFormField(HolographicComboBox(), "DB Type:")
        db_type_field.input_widget.addItems(["SQL Server", "SQLite"])
        self.database_type_selector = db_type_field.input_widget
        self.field_widgets["database_type"] = db_type_field
        db_layout.addWidget(db_type_field)

        connection_layout.addLayout(db_layout)

        # SQL Server fields in compact grid
        sql_grid = QGridLayout()
        sql_grid.setSpacing(2)

        sql_fields = [
            ("sql_server", "Server:", 0, 0),
            ("sql_database", "Database:", 0, 1),
            ("sql_username", "Username:", 1, 0),
            ("sql_password", "Password:", 1, 1),
        ]

        for field_name, label, row, col in sql_fields:
            widget = PasswordField() if "password" in field_name else ModernLineEdit()
            field = CompactFormField(widget, label)
            self.field_widgets[field_name] = field
            sql_grid.addWidget(field, row, col)

        connection_layout.addLayout(sql_grid)

        connection_group.setLayout(connection_layout)
        layout.addWidget(connection_group)

    def _add_sync_section(self, layout):
        """Add sync configuration section"""
        sync_group = NeonGroupBox("Sync Settings")
        sync_layout = QVBoxLayout()
        sync_layout.setSpacing(3)

        # Sync settings in compact rows
        sync_fields = [
            (
                "sync_interval",
                "Interval (sec):",
                ModernSpinBox(min_val=30, max_val=3600),
            ),
            ("batch_size", "Batch Size:", ModernSpinBox(min_val=100, max_val=10000)),
        ]

        for field_name, label, widget in sync_fields:
            field = CompactFormField(widget, label)
            self.field_widgets[field_name] = field
            sync_layout.addWidget(field)

        # Auto-sync checkbox
        auto_sync_checkbox = QCheckBox("Enable Auto Synchronization")
        auto_sync_checkbox.setStyleSheet(get_modern_checkbox_style())
        self.auto_sync_enabled_checkbox = auto_sync_checkbox
        sync_layout.addWidget(auto_sync_checkbox)

        sync_group.setLayout(sync_layout)
        layout.addWidget(sync_group)

    def _add_mapping_section(self, layout):
        """Add data mapping section with horizontal split"""
        mapping_group = NeonGroupBox("Data Mapping")
        mapping_layout = QHBoxLayout()  # Horizontal split for better space usage
        mapping_layout.setSpacing(4)

        # SharePoint to SQL mapping
        self.sp_to_sql_table = CompactMappingTable("SPO → SQL")
        self.mapping_tables["sharepoint_to_sql_mapping"] = self.sp_to_sql_table
        mapping_layout.addWidget(self.sp_to_sql_table)

        # SQL to SharePoint mapping
        self.sql_to_sp_table = CompactMappingTable("SQL → SPO")
        self.mapping_tables["sql_to_sharepoint_mapping"] = self.sql_to_sp_table
        mapping_layout.addWidget(self.sql_to_sp_table)

        mapping_group.setLayout(mapping_layout)
        layout.addWidget(mapping_group)

    def _add_action_buttons(self, layout):
        """Add action buttons at bottom"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(4)

        self.test_button = ModernButton("🌐 Test Connections", "secondary", "sm")
        self.save_button = ModernButton("💾 Save Config", "primary", "sm")
        self.reset_button = ModernButton("🔄 Reset", "ghost", "sm")

        button_layout.addWidget(self.test_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch(1)

        layout.addLayout(button_layout)

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.MEDIUM)
    def _load_current_config(self):
        """Load current configuration into UI fields"""
        try:
            config = self.config_manager.get_config()

            # Load field values
            for key, field_widget in self.field_widgets.items():
                try:
                    value = getattr(config, key, None)
                    if value is not None:
                        field_widget.set_value(value)
                except Exception as e:
                    logger.debug(f"Error loading config key '{key}': {e}")

            # Load auto-sync checkbox
            self.auto_sync_enabled_checkbox.setChecked(config.auto_sync_enabled)

            # Set database type selector
            if config.database_type.lower() == "sqlserver":
                self.database_type_selector.setCurrentText("SQL Server")
            else:
                self.database_type_selector.setCurrentText("SQLite")

            # Load mapping tables
            for mapping_key, table_widget in self.mapping_tables.items():
                mapping_data = getattr(config, mapping_key, {})
                table_widget.set_mapping(mapping_data)

            logger.info("Configuration loaded into compact UI successfully")

        except Exception as e:
            logger.error(f"Error loading configuration: {e}")

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.HIGH)
    def _connect_signals(self):
        """Connect UI signals to handlers"""
        try:
            # Database type selector
            self.database_type_selector.currentIndexChanged.connect(
                self._on_db_type_changed
            )

            # Auto-sync checkbox
            self.auto_sync_enabled_checkbox.stateChanged.connect(
                self._on_auto_sync_checkbox_changed
            )

            # Action buttons
            self.test_button.clicked.connect(self._test_connections)
            self.save_button.clicked.connect(self._save_all_settings)
            self.reset_button.clicked.connect(self._reset_config)

            # Form field changes - connect to deferred save
            self._connect_form_field_signals()

            # Mapping table changes
            for table in self.mapping_tables.values():
                table.table.itemChanged.connect(self._defer_save)

            logger.debug("Compact ConfigPanel signals connected successfully")

        except Exception as e:
            logger.error(f"Error connecting ConfigPanel signals: {e}")

    def _connect_form_field_signals(self):
        """Connect form field signals for auto-save"""
        for key, field_widget in self.field_widgets.items():
            try:
                input_widget = field_widget.input_widget

                if isinstance(input_widget, ModernLineEdit):
                    input_widget.textChanged.connect(self._defer_save)
                elif isinstance(input_widget, HolographicComboBox):
                    input_widget.currentTextChanged.connect(self._defer_save)
                elif isinstance(input_widget, ModernSpinBox):
                    input_widget.valueChanged.connect(self._defer_save)
                elif isinstance(input_widget, QCheckBox):
                    input_widget.stateChanged.connect(self._defer_save)

            except Exception as e:
                logger.debug(f"Error connecting signal for field '{key}': {e}")

    @pyqtSlot()
    def _defer_save(self):
        """Start timer to defer saving changes"""
        if not self._save_timer.isActive():
            self._save_timer.start()

    @pyqtSlot()
    def _save_all_settings(self):
        """Save all configuration settings"""
        try:
            logger.info("Saving all configuration settings...")

            # Save form fields
            for key, field_widget in self.field_widgets.items():
                try:
                    value = field_widget.get_value()
                    if value is not None:
                        # Determine value type for proper conversion
                        if key in ["sync_interval", "batch_size"]:
                            value_type = "int"
                        elif "password" in key or "secret" in key:
                            value_type = "str"
                        else:
                            value_type = "str"

                        self.request_update_config_setting.emit(key, value, value_type)
                except Exception as e:
                    logger.error(f"Error saving field '{key}': {e}")

            # Save mapping tables
            for mapping_key, table_widget in self.mapping_tables.items():
                try:
                    mapping_data = table_widget.get_mapping()
                    self.request_update_config_setting.emit(
                        mapping_key, mapping_data, "dict"
                    )
                except Exception as e:
                    logger.error(f"Error saving mapping '{mapping_key}': {e}")

            # Save auto-sync setting
            self.request_update_config_setting.emit(
                "auto_sync_enabled", self.auto_sync_enabled_checkbox.isChecked(), "bool"
            )

            self.config_changed.emit()
            logger.info("All configuration settings saved successfully")

        except Exception as e:
            logger.error(f"Error saving configuration settings: {e}")

    @pyqtSlot(int)
    def _on_db_type_changed(self, index: int):
        """Handle database type change"""
        try:
            selected_type = "sqlserver" if index == 0 else "sqlite"
            self.request_update_config_setting.emit(
                "database_type", selected_type, "str"
            )
            logger.info(f"Database type changed to: {selected_type}")
        except Exception as e:
            logger.error(f"Error handling database type change: {e}")

    @pyqtSlot(int)
    def _on_auto_sync_checkbox_changed(self, state: int):
        """Handle auto-sync checkbox change"""
        try:
            is_checked = state == Qt.CheckState.Checked.value
            self.request_auto_sync_toggle.emit(is_checked)
            logger.info(f"Auto-sync toggled: {is_checked}")
        except Exception as e:
            logger.error(f"Error handling auto-sync toggle: {e}")

    @pyqtSlot()
    def _test_connections(self):
        """Test connections with current settings"""
        try:
            # Save current settings first
            self._save_all_settings()
            # Request connection test from controller
            if hasattr(self.controller, "test_all_connections"):
                self.controller.test_all_connections()
        except Exception as e:
            logger.error(f"Error testing connections: {e}")

    @pyqtSlot()
    def _reset_config(self):
        """Reset configuration to defaults"""
        try:
            reply = QMessageBox.question(
                self,
                "Reset Configuration",
                "Reset all settings to default values?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Reload config from file
                self.config_manager.reload_config()
                self._load_current_config()
                logger.info("Configuration reset to defaults")

        except Exception as e:
            logger.error(f"Error resetting configuration: {e}")

    # Methods for external updates (called by MainWindow)
    def update_sharepoint_sites(self, sites: list):
        """Update SharePoint sites dropdown (placeholder for future)"""
        logger.debug(f"SharePoint sites updated: {len(sites)} sites")

    def update_sharepoint_lists(self, lists: list):
        """Update SharePoint lists dropdown (placeholder for future)"""
        logger.debug(f"SharePoint lists updated: {len(lists)} lists")

    def update_database_names(self, databases: list):
        """Update database names dropdown (placeholder for future)"""
        logger.debug(f"Database names updated: {len(databases)} databases")

    def update_database_tables(self, tables: list):
        """Update database tables dropdown (placeholder for future)"""
        logger.debug(f"Database tables updated: {len(tables)} tables")

    def cleanup(self):
        """Perform cleanup for ConfigPanel"""
        if self.cleanup_done:
            logger.debug("ConfigPanel cleanup already performed")
            return

        logger.info("Initiating ConfigPanel cleanup...")

        try:
            # Stop save timer
            if self._save_timer and self._save_timer.isActive():
                self._save_timer.stop()
                self._save_timer.deleteLater()
                self._save_timer = None

            # Disconnect signals
            try:
                self.database_type_selector.currentIndexChanged.disconnect()
                self.auto_sync_enabled_checkbox.stateChanged.disconnect()
                self.test_button.clicked.disconnect()
                self.save_button.clicked.disconnect()
                self.reset_button.clicked.disconnect()
            except (TypeError, RuntimeError):
                pass

            # Clean up form field widgets
            for field_widget in self.field_widgets.values():
                try:
                    input_widget = field_widget.input_widget
                    if hasattr(input_widget, "textChanged"):
                        input_widget.textChanged.disconnect()
                    elif hasattr(input_widget, "currentTextChanged"):
                        input_widget.currentTextChanged.disconnect()
                    elif hasattr(input_widget, "valueChanged"):
                        input_widget.valueChanged.disconnect()
                    elif hasattr(input_widget, "stateChanged"):
                        input_widget.stateChanged.disconnect()
                except (TypeError, RuntimeError):
                    pass
                field_widget.deleteLater()

            self.field_widgets.clear()

            # Clean up mapping tables
            for table_widget in self.mapping_tables.values():
                try:
                    table_widget.table.itemChanged.disconnect()
                    table_widget.deleteLater()
                except (TypeError, RuntimeError):
                    pass

            self.mapping_tables.clear()

            # Clean up remaining widgets
            for child in self.findChildren(QWidget):
                if child and child != self:
                    child.deleteLater()

            self.cleanup_done = True
            logger.info("ConfigPanel cleanup completed successfully")

        except Exception as e:
            logger.error(f"Error during ConfigPanel cleanup: {e}")
            self.cleanup_done = True
