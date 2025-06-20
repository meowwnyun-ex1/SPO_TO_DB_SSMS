# ui/components/config_panel.py - Fixed Config Panel
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QGridLayout,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QFileDialog,
    QMessageBox,
    QCheckBox,
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer, pyqtSignal
import sys
import json
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
    from utils.config_manager import get_config_manager
    from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity
except ImportError as e:
    print(f"Import error in config_panel.py: {e}")
    sys.exit(1)

logger = logging.getLogger(__name__)


class ConfigPanel(QWidget):
    """
    Configuration panel for managing SharePoint and Database settings,
    synchronization options, and data mappings.
    """

    # Signals to communicate with AppController
    config_changed = pyqtSignal()
    request_auto_sync_toggle = pyqtSignal(bool)
    request_update_config_setting = pyqtSignal(
        str, object, str
    )  # key_path, value, value_type

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.config_manager = get_config_manager()
        self.cleanup_done = False

        # Timer for deferred saving
        self._mapping_save_timer = QTimer(self)
        self._mapping_save_timer.setSingleShot(True)
        self._mapping_save_timer.setInterval(1000)
        self._mapping_save_timer.timeout.connect(self._save_field_mappings)

        # Store form field widgets
        self.field_widgets = {}

        self._setup_ui()
        self._load_current_config()
        self._connect_signals()

        logger.info("ConfigPanel initialized")

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.HIGH)
    def _setup_ui(self):
        """Setup the layout and widgets for the configuration panel"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(get_modern_tab_style())
        main_layout.addWidget(self.tab_widget)

        # Add tabs
        self._add_general_settings_tab()
        self._add_sharepoint_tab()
        self._add_database_tab()
        self._add_sync_settings_tab()
        self._add_data_mapping_tab()
        self._add_advanced_settings_tab()

        main_layout.addStretch(1)

    def _add_general_settings_tab(self):
        """Add general settings tab"""
        general_tab = QScrollArea()
        general_tab.setWidgetResizable(True)
        content_widget = QWidget()
        general_tab.setWidget(content_widget)
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # App Info Group
        app_info_group = NeonGroupBox("Application Information")
        app_info_layout = QGridLayout()

        config = self.config_manager.get_config()

        app_name_label = QLabel(f"App Name: {config.app_name}")
        app_name_label.setStyleSheet(
            f"color: {UltraModernColors.TEXT_PRIMARY}; font-weight: bold;"
        )
        app_info_layout.addWidget(app_name_label, 0, 0)

        app_version_label = QLabel(f"Version: {config.app_version}")
        app_version_label.setStyleSheet(f"color: {UltraModernColors.TEXT_SECONDARY};")
        app_info_layout.addWidget(app_version_label, 1, 0)

        app_info_group.setLayout(app_info_layout)
        layout.addWidget(app_info_group)

        # UI Settings Group
        ui_group = NeonGroupBox("UI Settings")
        ui_layout = QGridLayout()

        self.field_widgets["background_image_path"] = FormField(
            ModernLineEdit(), "Background Image Path:"
        )
        ui_layout.addWidget(self.field_widgets["background_image_path"], 0, 0, 1, 2)

        self.field_widgets["enable_background_audio"] = FormField(
            QCheckBox("Enable Background Audio"), ""
        )
        self.field_widgets["enable_background_audio"].input_widget.setStyleSheet(
            get_modern_checkbox_style()
        )
        ui_layout.addWidget(self.field_widgets["enable_background_audio"], 1, 0, 1, 2)

        self.field_widgets["background_audio_path"] = FormField(
            ModernLineEdit(), "Background Audio Path:"
        )
        ui_layout.addWidget(self.field_widgets["background_audio_path"], 2, 0, 1, 2)

        self.field_widgets["background_audio_volume"] = FormField(
            ModernSpinBox(decimal=True, min_val=0.0, max_val=1.0, step=0.05),
            "Audio Volume:",
        )
        ui_layout.addWidget(self.field_widgets["background_audio_volume"], 3, 0, 1, 2)

        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)

        layout.addStretch(1)
        self.tab_widget.addTab(general_tab, "General")

    def _add_sharepoint_tab(self):
        """Add SharePoint configuration tab"""
        sharepoint_tab = QScrollArea()
        sharepoint_tab.setWidgetResizable(True)
        content_widget = QWidget()
        sharepoint_tab.setWidget(content_widget)
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        sp_group = NeonGroupBox("SharePoint Connection")
        sp_layout = QGridLayout()

        self.field_widgets["sharepoint_site"] = FormField(
            ModernLineEdit(), "SharePoint Site URL:"
        )
        sp_layout.addWidget(self.field_widgets["sharepoint_site"], 0, 0, 1, 2)

        self.field_widgets["sharepoint_list"] = FormField(
            ModernLineEdit(), "SharePoint List Name:"
        )
        sp_layout.addWidget(self.field_widgets["sharepoint_list"], 1, 0, 1, 2)

        self.field_widgets["sharepoint_client_id"] = FormField(
            ModernLineEdit(), "Client ID:"
        )
        sp_layout.addWidget(self.field_widgets["sharepoint_client_id"], 2, 0, 1, 2)

        self.field_widgets["sharepoint_client_secret"] = FormField(
            PasswordField(), "Client Secret:"
        )
        sp_layout.addWidget(self.field_widgets["sharepoint_client_secret"], 3, 0, 1, 2)

        self.field_widgets["tenant_id"] = FormField(ModernLineEdit(), "Tenant ID:")
        sp_layout.addWidget(self.field_widgets["tenant_id"], 4, 0, 1, 2)

        self.field_widgets["use_graph_api"] = FormField(
            QCheckBox("Use Graph API (Advanced)"), ""
        )
        self.field_widgets["use_graph_api"].input_widget.setStyleSheet(
            get_modern_checkbox_style()
        )
        sp_layout.addWidget(self.field_widgets["use_graph_api"], 5, 0, 1, 2)

        sp_group.setLayout(sp_layout)
        layout.addWidget(sp_group)
        layout.addStretch(1)
        self.tab_widget.addTab(sharepoint_tab, "SharePoint")

    def _add_database_tab(self):
        """Add database configuration tab"""
        database_tab = QScrollArea()
        database_tab.setWidgetResizable(True)
        content_widget = QWidget()
        database_tab.setWidget(content_widget)
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Database Type Selection
        db_type_group = NeonGroupBox("Database Type")
        db_type_layout = QVBoxLayout()
        self.database_type_selector = HolographicComboBox()
        self.database_type_selector.addItems(["SQL Server", "SQLite"])
        db_type_layout.addWidget(self.database_type_selector)
        db_type_group.setLayout(db_type_layout)
        layout.addWidget(db_type_group)

        # Database Settings Group
        db_settings_group = NeonGroupBox("Database Connection Settings")
        db_settings_layout = QGridLayout()

        # SQL Server fields
        self.field_widgets["sql_server"] = FormField(
            ModernLineEdit(), "Server Address:"
        )
        db_settings_layout.addWidget(self.field_widgets["sql_server"], 0, 0, 1, 2)

        self.field_widgets["sql_database"] = FormField(
            ModernLineEdit(), "Database Name:"
        )
        db_settings_layout.addWidget(self.field_widgets["sql_database"], 1, 0, 1, 2)

        self.field_widgets["sql_username"] = FormField(ModernLineEdit(), "Username:")
        db_settings_layout.addWidget(self.field_widgets["sql_username"], 2, 0, 1, 2)

        self.field_widgets["sql_password"] = FormField(PasswordField(), "Password:")
        db_settings_layout.addWidget(self.field_widgets["sql_password"], 3, 0, 1, 2)

        self.field_widgets["sql_table_name"] = FormField(
            ModernLineEdit(), "Target Table Name:"
        )
        db_settings_layout.addWidget(self.field_widgets["sql_table_name"], 4, 0, 1, 2)

        # SQLite fields
        self.field_widgets["sqlite_file"] = FormField(
            ModernLineEdit(), "SQLite File Path:"
        )
        db_settings_layout.addWidget(self.field_widgets["sqlite_file"], 5, 0)

        self.browse_sqlite_button = ModernButton("Browse...", "secondary", "sm")
        db_settings_layout.addWidget(self.browse_sqlite_button, 5, 1)

        self.field_widgets["sqlite_table_name"] = FormField(
            ModernLineEdit(), "SQLite Table Name:"
        )
        db_settings_layout.addWidget(
            self.field_widgets["sqlite_table_name"], 6, 0, 1, 2
        )

        # Options
        self.field_widgets["sql_create_table"] = FormField(
            QCheckBox("Create Table if Not Exists"), ""
        )
        self.field_widgets["sql_create_table"].input_widget.setStyleSheet(
            get_modern_checkbox_style()
        )
        db_settings_layout.addWidget(self.field_widgets["sql_create_table"], 7, 0, 1, 2)

        self.field_widgets["sql_truncate_before"] = FormField(
            QCheckBox("Truncate Table Before Sync"), ""
        )
        self.field_widgets["sql_truncate_before"].input_widget.setStyleSheet(
            get_modern_checkbox_style()
        )
        db_settings_layout.addWidget(
            self.field_widgets["sql_truncate_before"], 8, 0, 1, 2
        )

        db_settings_group.setLayout(db_settings_layout)
        layout.addWidget(db_settings_group)

        layout.addStretch(1)
        self.tab_widget.addTab(database_tab, "Database")

    def _add_sync_settings_tab(self):
        """Add synchronization settings tab"""
        sync_tab = QScrollArea()
        sync_tab.setWidgetResizable(True)
        content_widget = QWidget()
        sync_tab.setWidget(content_widget)
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Sync Settings Group
        sync_group = NeonGroupBox("Synchronization Settings")
        sync_layout = QGridLayout()

        self.field_widgets["sync_interval"] = FormField(
            ModernSpinBox(min_val=1, max_val=86400), "Sync Interval (seconds):"
        )
        sync_layout.addWidget(self.field_widgets["sync_interval"], 0, 0, 1, 2)

        self.field_widgets["sync_mode"] = FormField(HolographicComboBox(), "Sync Mode:")
        self.field_widgets["sync_mode"].input_widget.addItems(["full", "incremental"])
        sync_layout.addWidget(self.field_widgets["sync_mode"], 1, 0, 1, 2)

        # Auto-sync checkbox (not a FormField, handled separately)
        self.auto_sync_enabled_checkbox = QCheckBox("Enable Auto Synchronization")
        self.auto_sync_enabled_checkbox.setStyleSheet(get_modern_checkbox_style())
        sync_layout.addWidget(self.auto_sync_enabled_checkbox, 2, 0, 1, 2)

        self.field_widgets["auto_sync_direction"] = FormField(
            HolographicComboBox(), "Auto-Sync Direction:"
        )
        self.field_widgets["auto_sync_direction"].input_widget.addItems(
            ["spo_to_sql", "sql_to_spo"]
        )
        sync_layout.addWidget(self.field_widgets["auto_sync_direction"], 3, 0, 1, 2)

        sync_group.setLayout(sync_layout)
        layout.addWidget(sync_group)

        # Excel Import Group
        excel_group = NeonGroupBox("Excel Import Settings")
        excel_layout = QVBoxLayout()

        self.field_widgets["excel_import_mapping"] = FormField(
            ModernTextEdit(), "Excel to DB Column Mapping (JSON):"
        )
        self.field_widgets["excel_import_mapping"].input_widget.setPlaceholderText(
            '{"Excel Column": "DB Column", "Name": "full_name", "Age": "age"}'
        )
        excel_layout.addWidget(self.field_widgets["excel_import_mapping"])

        excel_group.setLayout(excel_layout)
        layout.addWidget(excel_group)

        layout.addStretch(1)
        self.tab_widget.addTab(sync_tab, "Sync & Import")

    def _add_data_mapping_tab(self):
        """Add data mapping configuration tab"""
        mapping_tab = QWidget()
        layout = QVBoxLayout(mapping_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # SharePoint to SQL Mapping
        sp_to_sql_group = NeonGroupBox("SharePoint to SQL Mapping")
        sp_to_sql_layout = QVBoxLayout()

        self.sp_to_sql_table = QTableWidget(5, 2)  # Start with 5 rows
        self.sp_to_sql_table.setHorizontalHeaderLabels(
            ["SharePoint Field", "SQL Column"]
        )
        self.sp_to_sql_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.sp_to_sql_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        sp_to_sql_layout.addWidget(self.sp_to_sql_table)

        # Buttons for SP to SQL table
        sp_to_sql_buttons = QHBoxLayout()
        self.add_sp_to_sql_row_btn = ModernButton("Add Row", "ghost", "sm", icon="➕")
        self.remove_sp_to_sql_row_btn = ModernButton(
            "Remove Row", "danger", "sm", icon="➖"
        )
        sp_to_sql_buttons.addWidget(self.add_sp_to_sql_row_btn)
        sp_to_sql_buttons.addWidget(self.remove_sp_to_sql_row_btn)
        sp_to_sql_buttons.addStretch()
        sp_to_sql_layout.addLayout(sp_to_sql_buttons)

        sp_to_sql_group.setLayout(sp_to_sql_layout)
        layout.addWidget(sp_to_sql_group)

        # SQL to SharePoint Mapping
        sql_to_sp_group = NeonGroupBox("SQL to SharePoint Mapping")
        sql_to_sp_layout = QVBoxLayout()

        self.sql_to_sp_table = QTableWidget(5, 2)  # Start with 5 rows
        self.sql_to_sp_table.setHorizontalHeaderLabels(
            ["SQL Column", "SharePoint Field"]
        )
        self.sql_to_sp_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.sql_to_sp_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        sql_to_sp_layout.addWidget(self.sql_to_sp_table)

        # Buttons for SQL to SP table
        sql_to_sp_buttons = QHBoxLayout()
        self.add_sql_to_sp_row_btn = ModernButton("Add Row", "ghost", "sm", icon="➕")
        self.remove_sql_to_sp_row_btn = ModernButton(
            "Remove Row", "danger", "sm", icon="➖"
        )
        sql_to_sp_buttons.addWidget(self.add_sql_to_sp_row_btn)
        sql_to_sp_buttons.addWidget(self.remove_sql_to_sp_row_btn)
        sql_to_sp_buttons.addStretch()
        sql_to_sp_layout.addLayout(sql_to_sp_buttons)

        sql_to_sp_group.setLayout(sql_to_sp_layout)
        layout.addWidget(sql_to_sp_group)

        layout.addStretch(1)
        self.tab_widget.addTab(mapping_tab, "Data Mapping")

    def _add_advanced_settings_tab(self):
        """Add advanced settings tab"""
        advanced_tab = QScrollArea()
        advanced_tab.setWidgetResizable(True)
        content_widget = QWidget()
        advanced_tab.setWidget(content_widget)
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Performance Group
        perf_group = NeonGroupBox("Performance & Connection")
        perf_layout = QGridLayout()

        self.field_widgets["connection_timeout"] = FormField(
            ModernSpinBox(min_val=1, max_val=300), "Connection Timeout (seconds):"
        )
        perf_layout.addWidget(self.field_widgets["connection_timeout"], 0, 0, 1, 2)

        self.field_widgets["max_retries"] = FormField(
            ModernSpinBox(min_val=0, max_val=10), "Max Retries:"
        )
        perf_layout.addWidget(self.field_widgets["max_retries"], 1, 0, 1, 2)

        self.field_widgets["batch_size"] = FormField(
            ModernSpinBox(min_val=1, max_val=10000), "Batch Size:"
        )
        perf_layout.addWidget(self.field_widgets["batch_size"], 2, 0, 1, 2)

        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)

        # Notifications Group
        notif_group = NeonGroupBox("Notifications")
        notif_layout = QGridLayout()

        self.field_widgets["enable_success_notifications"] = FormField(
            QCheckBox("Enable Success Notifications"), ""
        )
        self.field_widgets["enable_success_notifications"].input_widget.setStyleSheet(
            get_modern_checkbox_style()
        )
        notif_layout.addWidget(
            self.field_widgets["enable_success_notifications"], 0, 0, 1, 2
        )

        self.field_widgets["enable_error_notifications"] = FormField(
            QCheckBox("Enable Error Notifications"), ""
        )
        self.field_widgets["enable_error_notifications"].input_widget.setStyleSheet(
            get_modern_checkbox_style()
        )
        notif_layout.addWidget(
            self.field_widgets["enable_error_notifications"], 1, 0, 1, 2
        )

        notif_group.setLayout(notif_layout)
        layout.addWidget(notif_group)

        # Cache Management Group
        cache_group = NeonGroupBox("Cache Management")
        cache_layout = QGridLayout()

        self.field_widgets["auto_cache_cleanup_enabled"] = FormField(
            QCheckBox("Enable Auto Cache Cleanup"), ""
        )
        self.field_widgets["auto_cache_cleanup_enabled"].input_widget.setStyleSheet(
            get_modern_checkbox_style()
        )
        cache_layout.addWidget(
            self.field_widgets["auto_cache_cleanup_enabled"], 0, 0, 1, 2
        )

        self.field_widgets["cache_cleanup_interval_hours"] = FormField(
            ModernSpinBox(min_val=1, max_val=168), "Cleanup Interval (hours):"
        )
        cache_layout.addWidget(
            self.field_widgets["cache_cleanup_interval_hours"], 1, 0, 1, 2
        )

        cache_group.setLayout(cache_layout)
        layout.addWidget(cache_group)

        layout.addStretch(1)
        self.tab_widget.addTab(advanced_tab, "Advanced")

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
            self._load_mapping_to_table(
                config.sharepoint_to_sql_mapping, self.sp_to_sql_table
            )
            self._load_mapping_to_table(
                config.sql_to_sharepoint_mapping, self.sql_to_sp_table
            )

            # Load Excel import mapping as JSON
            if config.excel_import_mapping:
                try:
                    json_str = json.dumps(config.excel_import_mapping, indent=2)
                    self.field_widgets["excel_import_mapping"].set_value(json_str)
                except Exception as e:
                    logger.error(f"Error loading Excel import mapping: {e}")

            logger.info("Configuration loaded into UI successfully")

        except Exception as e:
            logger.error(f"Error loading configuration: {e}")

    def _load_mapping_to_table(self, mapping: dict, table_widget: QTableWidget):
        """Load dictionary mapping into table widget"""
        try:
            table_widget.clearContents()
            row_count = max(len(mapping), 5)  # Minimum 5 rows
            table_widget.setRowCount(row_count)

            for row, (key, value) in enumerate(mapping.items()):
                table_widget.setItem(row, 0, QTableWidgetItem(str(key)))
                table_widget.setItem(row, 1, QTableWidgetItem(str(value)))

        except Exception as e:
            logger.error(f"Error loading mapping to table: {e}")

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.HIGH)
    def _connect_signals(self):
        """Connect UI signals to handlers"""
        try:
            # Database type selector
            self.database_type_selector.currentIndexChanged.connect(
                self._on_db_type_changed
            )

            # Browse button
            self.browse_sqlite_button.clicked.connect(self._browse_sqlite_file)

            # Auto-sync checkbox
            self.auto_sync_enabled_checkbox.stateChanged.connect(
                self._on_auto_sync_checkbox_changed
            )

            # Mapping table buttons
            self.add_sp_to_sql_row_btn.clicked.connect(
                lambda: self._add_mapping_row(self.sp_to_sql_table)
            )
            self.remove_sp_to_sql_row_btn.clicked.connect(
                lambda: self._remove_mapping_row(self.sp_to_sql_table)
            )
            self.add_sql_to_sp_row_btn.clicked.connect(
                lambda: self._add_mapping_row(self.sql_to_sp_table)
            )
            self.remove_sql_to_sp_row_btn.clicked.connect(
                lambda: self._remove_mapping_row(self.sql_to_sp_table)
            )

            # Table item changes
            self.sp_to_sql_table.itemChanged.connect(self._defer_save_mapping)
            self.sql_to_sp_table.itemChanged.connect(self._defer_save_mapping)

            # Form field changes
            self._connect_form_field_signals()

            logger.debug("ConfigPanel signals connected successfully")

        except Exception as e:
            logger.error(f"Error connecting ConfigPanel signals: {e}")

    def _connect_form_field_signals(self):
        """Connect form field signals for auto-save"""
        for key, field_widget in self.field_widgets.items():
            try:
                input_widget = field_widget.input_widget

                if isinstance(input_widget, ModernLineEdit):
                    input_widget.textChanged.connect(
                        lambda text, k=key: self._defer_save_config_setting(
                            k, text, "str"
                        )
                    )
                elif isinstance(input_widget, ModernTextEdit):
                    input_widget.textChanged.connect(
                        lambda k=key: self._defer_save_config_setting(
                            k, self.field_widgets[k].get_value(), "json_str"
                        )
                    )
                elif isinstance(input_widget, HolographicComboBox):
                    input_widget.currentTextChanged.connect(
                        lambda text, k=key: self._defer_save_config_setting(
                            k, text, "str"
                        )
                    )
                elif isinstance(input_widget, ModernSpinBox):
                    if input_widget.is_decimal:
                        input_widget.valueChanged.connect(
                            lambda value, k=key: self._defer_save_config_setting(
                                k, value, "float"
                            )
                        )
                    else:
                        input_widget.valueChanged.connect(
                            lambda value, k=key: self._defer_save_config_setting(
                                k, value, "int"
                            )
                        )
                elif isinstance(input_widget, QCheckBox):
                    input_widget.stateChanged.connect(
                        lambda state, k=key: self._defer_save_config_setting(
                            k, input_widget.isChecked(), "bool"
                        )
                    )

            except Exception as e:
                logger.debug(f"Error connecting signal for field '{key}': {e}")

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

    @pyqtSlot()
    def _browse_sqlite_file(self):
        """Browse for SQLite file"""
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Select SQLite Database File",
                "",
                "SQLite Database Files (*.db);;All Files (*)",
            )
            if file_name:
                self.field_widgets["sqlite_file"].set_value(file_name)
                self.request_update_config_setting.emit("sqlite_file", file_name, "str")
                logger.info(f"SQLite file selected: {file_name}")
        except Exception as e:
            logger.error(f"Error browsing SQLite file: {e}")

    @pyqtSlot(int)
    def _on_auto_sync_checkbox_changed(self, state: int):
        """Handle auto-sync checkbox change"""
        try:
            is_checked = state == Qt.CheckState.Checked.value
            self.request_auto_sync_toggle.emit(is_checked)
            logger.info(f"Auto-sync toggled: {is_checked}")
        except Exception as e:
            logger.error(f"Error handling auto-sync toggle: {e}")

    def _defer_save_config_setting(self, key_path: str, value, value_type: str):
        """Defer saving configuration setting"""
        try:
            self.request_update_config_setting.emit(key_path, value, value_type)
            logger.debug(f"Config setting queued for save: {key_path} = {value}")
        except Exception as e:
            logger.debug(f"Error deferring config save for '{key_path}': {e}")

    def _add_mapping_row(self, table_widget: QTableWidget):
        """Add new row to mapping table"""
        try:
            row_position = table_widget.rowCount()
            table_widget.insertRow(row_position)
            table_widget.setItem(row_position, 0, QTableWidgetItem(""))
            table_widget.setItem(row_position, 1, QTableWidgetItem(""))
            logger.debug(f"Added row to mapping table at position {row_position}")
        except Exception as e:
            logger.error(f"Error adding mapping row: {e}")

    def _remove_mapping_row(self, table_widget: QTableWidget):
        """Remove selected rows from mapping table"""
        try:
            selected_rows = sorted(
                set(index.row() for index in table_widget.selectedIndexes()),
                reverse=True,
            )

            if not selected_rows:
                QMessageBox.information(
                    self, "No Selection", "Please select row(s) to remove."
                )
                return

            for row in selected_rows:
                table_widget.removeRow(row)

            self._defer_save_mapping()
            logger.debug(f"Removed {len(selected_rows)} rows from mapping table")

        except Exception as e:
            logger.error(f"Error removing mapping rows: {e}")

    @pyqtSlot()
    def _defer_save_mapping(self):
        """Start timer to defer saving mapping changes"""
        if self._mapping_save_timer.isActive():
            self._mapping_save_timer.stop()
        self._mapping_save_timer.start()

    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.MEDIUM)
    def _save_field_mappings(self):
        """Save field mappings from tables to configuration"""
        try:
            logger.info("Saving field mappings...")

            # Get mappings from tables
            sp_to_sql_map = self._get_mapping_from_table(self.sp_to_sql_table)
            sql_to_sp_map = self._get_mapping_from_table(self.sql_to_sp_table)

            # Save mappings
            self.request_update_config_setting.emit(
                "sharepoint_to_sql_mapping", sp_to_sql_map, "dict"
            )
            self.request_update_config_setting.emit(
                "sql_to_sharepoint_mapping", sql_to_sp_map, "dict"
            )

            # Save Excel import mapping if valid JSON
            try:
                excel_import_str = self.field_widgets[
                    "excel_import_mapping"
                ].get_value()
                if excel_import_str.strip():
                    excel_import_dict = json.loads(excel_import_str)
                    self.request_update_config_setting.emit(
                        "excel_import_mapping", excel_import_dict, "dict"
                    )
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON in Excel import mapping: {e}")
            except Exception as e:
                logger.error(f"Error processing Excel import mapping: {e}")

            self.config_changed.emit()
            logger.info("Field mappings saved successfully")

        except Exception as e:
            logger.error(f"Error saving field mappings: {e}")

    def _get_mapping_from_table(self, table_widget: QTableWidget) -> dict:
        """Extract dictionary mapping from table widget"""
        mapping = {}
        try:
            for row in range(table_widget.rowCount()):
                key_item = table_widget.item(row, 0)
                value_item = table_widget.item(row, 1)

                if key_item and value_item:
                    key = key_item.text().strip()
                    value = value_item.text().strip()
                    if key and value:  # Only add non-empty pairs
                        mapping[key] = value

        except Exception as e:
            logger.error(f"Error extracting mapping from table: {e}")

        return mapping

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
            # Stop mapping save timer
            if self._mapping_save_timer and self._mapping_save_timer.isActive():
                self._mapping_save_timer.stop()
                self._mapping_save_timer.deleteLater()
                self._mapping_save_timer = None

            # Disconnect signals
            try:
                self.database_type_selector.currentIndexChanged.disconnect()
                self.browse_sqlite_button.clicked.disconnect()
                self.auto_sync_enabled_checkbox.stateChanged.disconnect()

                # Disconnect table signals
                self.sp_to_sql_table.itemChanged.disconnect()
                self.sql_to_sp_table.itemChanged.disconnect()

                # Disconnect button signals
                self.add_sp_to_sql_row_btn.clicked.disconnect()
                self.remove_sp_to_sql_row_btn.clicked.disconnect()
                self.add_sql_to_sp_row_btn.clicked.disconnect()
                self.remove_sql_to_sp_row_btn.clicked.disconnect()

            except (TypeError, RuntimeError):
                pass  # Signals already disconnected

            # Clean up form field widgets
            for key, field_widget in self.field_widgets.items():
                try:
                    input_widget = field_widget.input_widget
                    # Disconnect based on widget type
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

            # Clean up table widgets
            if hasattr(self, "sp_to_sql_table"):
                self.sp_to_sql_table.deleteLater()
            if hasattr(self, "sql_to_sp_table"):
                self.sql_to_sp_table.deleteLater()

            # Clean up remaining widgets
            widgets_to_cleanup = [
                "tab_widget",
                "database_type_selector",
                "browse_sqlite_button",
                "auto_sync_enabled_checkbox",
                "add_sp_to_sql_row_btn",
                "remove_sp_to_sql_row_btn",
                "add_sql_to_sp_row_btn",
                "remove_sql_to_sp_row_btn",
            ]

            for widget_name in widgets_to_cleanup:
                if hasattr(self, widget_name):
                    widget = getattr(self, widget_name)
                    if widget:
                        widget.deleteLater()
                        setattr(self, widget_name, None)

            # Clean up any remaining child widgets
            for child in self.findChildren(QWidget):
                if child and child != self:
                    child.deleteLater()

            self.cleanup_done = True
            logger.info("ConfigPanel cleanup completed successfully")

        except Exception as e:
            logger.error(f"Error during ConfigPanel cleanup: {e}")
            self.cleanup_done = True  # Mark as done to prevent retry loops
