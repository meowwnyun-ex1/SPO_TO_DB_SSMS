# ui/components/config_panel.py - Enhanced Config Panel with Robustness
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QStackedWidget,
    QTabWidget,
    QGridLayout,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QFileDialog,
    QMessageBox,
    QCheckBox,  # Added for auto-sync
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
import sys
import os
import logging

# Add project root to path (for absolute imports)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(
    os.path.dirname(current_dir)
)  # Go up two levels from ui/components
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import necessary components with fallbacks for robustness
try:
    from ui.styles.theme import (
        get_modern_tab_style,
        UltraModernColors,
        get_modern_groupbox_style,
        get_modern_checkbox_style,  # Added
    )
    from ui.widgets.modern_button import ActionButton, ModernButton
    from ui.widgets.modern_input import (
        ModernLineEdit,
        ModernSpinBox,
        FormField,
        PasswordField,
        SearchField,
        ModernTextEdit,
    )
    from ui.widgets.holographic_combobox import HolographicComboBox  # Added
    from ui.widgets.neon_groupbox import NeonGroupBox  # Added
    from utils.config_manager import (
        ConfigManager,
        Config,
    )  # Import Config for type hinting
    from utils.config_validation import (
        SharePointValidator,
        DatabaseValidator,
        GeneralValidator,
        ValidationResult,
    )  # Import validators
    from utils.error_handling import (
        handle_exceptions,
        ErrorCategory,
        ErrorSeverity,
        get_error_handler,
    )
except ImportError as e:
    print(
        f"CRITICAL IMPORT ERROR in config_panel.py: {e}. Ensure dependencies are installed."
    )
    sys.exit(1)


logger = logging.getLogger(__name__)


class ConfigPanel(QWidget):
    """
    Configuration panel for managing SharePoint and Database settings,
    synchronization options, and data mappings.
    """

    # Signals to communicate with AppController for config changes
    config_changed = pyqtSignal()  # General signal for any config change
    request_auto_sync_toggle = pyqtSignal(
        bool
    )  # Request AppController to toggle auto sync
    request_update_config_setting = pyqtSignal(
        str, Any, str
    )  # key_path, value, value_type

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.config_manager = ConfigManager()
        self.cleanup_done = False
        self._mapping_save_timer = QTimer(self)
        self._mapping_save_timer.setSingleShot(True)
        self._mapping_save_timer.setInterval(1000)  # Save after 1 second of no changes
        self._mapping_save_timer.timeout.connect(self._save_field_mappings)

        self.field_widgets = (
            {}
        )  # To hold references to FormField widgets for easy access

        self._setup_ui()
        self._load_current_config()
        self._connect_signals()
        logger.info("ConfigPanel initialized.")

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.HIGH)
    def _setup_ui(self):
        """Sets up the layout and widgets for the configuration panel."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(get_modern_tab_style())
        main_layout.addWidget(self.tab_widget)

        self._add_general_settings_tab()
        self._add_sharepoint_tab()
        self._add_database_tab()
        self._add_sync_settings_tab()
        self._add_data_mapping_tab()
        self._add_advanced_settings_tab()

        main_layout.addStretch(1)  # Push tabs to the top

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.MEDIUM)
    def _add_general_settings_tab(self):
        general_tab = QScrollArea()
        general_tab.setWidgetResizable(True)
        content_widget = QWidget()
        general_tab.setWidget(content_widget)
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # App Info Group
        app_info_group = NeonGroupBox("Application Information")
        app_info_layout = QGridLayout(app_info_group)
        app_info_layout.addWidget(QLabel("App Name:"), 0, 0)
        app_name_label = QLabel(self.config_manager.get_setting("app_name"))
        app_name_label.setStyleSheet(
            f"color: {UltraModernColors.TEXT_PRIMARY}; font-weight: bold;"
        )
        app_info_layout.addWidget(app_name_label, 0, 1)

        app_info_layout.addWidget(QLabel("Version:"), 1, 0)
        app_version_label = QLabel(self.config_manager.get_setting("app_version"))
        app_version_label.setStyleSheet(f"color: {UltraModernColors.TEXT_SECONDARY};")
        app_info_layout.addWidget(app_version_label, 1, 1)
        app_info_group.setLayout(app_info_layout)
        layout.addWidget(app_info_group)

        # UI Settings Group
        ui_group = NeonGroupBox("UI Settings")
        ui_layout = QGridLayout(ui_group)
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

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.MEDIUM)
    def _add_sharepoint_tab(self):
        sharepoint_tab = QScrollArea()
        sharepoint_tab.setWidgetResizable(True)
        content_widget = QWidget()
        sharepoint_tab.setWidget(content_widget)
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        sp_group = NeonGroupBox("SharePoint Connection")
        sp_layout = QGridLayout(sp_group)

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

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.MEDIUM)
    def _add_database_tab(self):
        database_tab = QScrollArea()
        database_tab.setWidgetResizable(True)
        content_widget = QWidget()
        database_tab.setWidget(content_widget)
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        db_type_group = NeonGroupBox("Database Type")
        db_type_layout = QVBoxLayout(db_type_group)
        self.database_type_selector = HolographicComboBox()
        self.database_type_selector.addItems(["SQL Server", "SQLite"])
        db_type_layout.addWidget(self.database_type_selector)
        db_type_group.setLayout(db_type_layout)
        layout.addWidget(db_type_group)

        self.db_stacked_widget = QStackedWidget()
        layout.addWidget(self.db_stacked_widget)

        # SQL Server Settings
        sql_server_widget = QWidget()
        sql_layout = QGridLayout(sql_server_widget)
        self.field_widgets["sql_server"] = FormField(
            ModernLineEdit(), "Server Address:"
        )
        sql_layout.addWidget(self.field_widgets["sql_server"], 0, 0, 1, 2)
        self.field_widgets["sql_database"] = FormField(
            ModernLineEdit(), "Database Name:"
        )
        sql_layout.addWidget(self.field_widgets["sql_database"], 1, 0, 1, 2)
        self.field_widgets["sql_username"] = FormField(ModernLineEdit(), "Username:")
        sql_layout.addWidget(self.field_widgets["sql_username"], 2, 0, 1, 2)
        self.field_widgets["sql_password"] = FormField(PasswordField(), "Password:")
        sql_layout.addWidget(self.field_widgets["sql_password"], 3, 0, 1, 2)
        self.field_widgets["sql_table_name"] = FormField(
            ModernLineEdit(), "Target Table Name:"
        )
        sql_layout.addWidget(self.field_widgets["sql_table_name"], 4, 0, 1, 2)
        self.field_widgets["sql_create_table"] = FormField(
            QCheckBox("Create Table if Not Exists"), ""
        )
        self.field_widgets["sql_create_table"].input_widget.setStyleSheet(
            get_modern_checkbox_style()
        )
        sql_layout.addWidget(self.field_widgets["sql_create_table"], 5, 0, 1, 2)
        self.field_widgets["sql_truncate_before"] = FormField(
            QCheckBox("Truncate Table Before Sync"), ""
        )
        self.field_widgets["sql_truncate_before"].input_widget.setStyleSheet(
            get_modern_checkbox_style()
        )
        sql_layout.addWidget(self.field_widgets["sql_truncate_before"], 6, 0, 1, 2)

        self.db_stacked_widget.addWidget(sql_server_widget)

        # SQLite Settings
        sqlite_widget = QWidget()
        sqlite_layout = QGridLayout(sqlite_widget)
        self.field_widgets["sqlite_file"] = FormField(
            ModernLineEdit(), "SQLite File Path:"
        )
        sqlite_layout.addWidget(self.field_widgets["sqlite_file"], 0, 0)
        self.browse_sqlite_button = ModernButton("Browse...", "secondary", "sm")
        sqlite_layout.addWidget(self.browse_sqlite_button, 0, 1)
        self.field_widgets["sqlite_table_name"] = FormField(
            ModernLineEdit(), "Target Table Name:"
        )
        sqlite_layout.addWidget(self.field_widgets["sqlite_table_name"], 1, 0, 1, 2)
        self.field_widgets["sqlite_create_table"] = FormField(
            QCheckBox("Create Table if Not Exists"), ""
        )
        self.field_widgets["sqlite_create_table"].input_widget.setStyleSheet(
            get_modern_checkbox_style()
        )
        sqlite_layout.addWidget(self.field_widgets["sqlite_create_table"], 2, 0, 1, 2)
        self.db_stacked_widget.addWidget(sqlite_widget)

        layout.addStretch(1)
        self.tab_widget.addTab(database_tab, "Database")

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.MEDIUM)
    def _add_sync_settings_tab(self):
        sync_tab = QScrollArea()
        sync_tab.setWidgetResizable(True)
        content_widget = QWidget()
        sync_tab.setWidget(content_widget)
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        sync_group = NeonGroupBox("Synchronization Settings")
        sync_layout = QGridLayout(sync_group)

        self.field_widgets["sync_interval"] = FormField(
            ModernSpinBox(min_val=1), "Sync Interval (minutes):"
        )
        sync_layout.addWidget(self.field_widgets["sync_interval"], 0, 0, 1, 2)

        self.field_widgets["sync_mode"] = FormField(HolographicComboBox(), "Sync Mode:")
        self.field_widgets["sync_mode"].input_widget.addItems(["full", "incremental"])
        sync_layout.addWidget(self.field_widgets["sync_mode"], 1, 0, 1, 2)

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

        self.field_widgets["full_sync_on_startup"] = FormField(
            QCheckBox("Run Full Sync on Startup"), ""
        )
        self.field_widgets["full_sync_on_startup"].input_widget.setStyleSheet(
            get_modern_checkbox_style()
        )
        sync_layout.addWidget(self.field_widgets["full_sync_on_startup"], 4, 0, 1, 2)

        sync_group.setLayout(sync_layout)
        layout.addWidget(sync_group)

        excel_import_group = NeonGroupBox("Excel Import Settings")
        excel_import_layout = QVBoxLayout(excel_import_group)
        self.field_widgets["excel_import_mapping"] = FormField(
            ModernTextEdit(), "Excel to DB Column Mapping (JSON):"
        )
        excel_import_layout.addWidget(self.field_widgets["excel_import_mapping"])
        # Add placeholder for a button to open file dialog and set excel_import_path if needed
        excel_import_group.setLayout(excel_import_layout)
        layout.addWidget(excel_import_group)

        layout.addStretch(1)
        self.tab_widget.addTab(sync_tab, "Sync & Import")

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.MEDIUM)
    def _add_data_mapping_tab(self):
        mapping_tab = QWidget()
        layout = QVBoxLayout(mapping_tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # SharePoint to SQL Mapping
        sp_to_sql_group = NeonGroupBox("SharePoint to SQL Mapping")
        sp_to_sql_layout = QVBoxLayout(sp_to_sql_group)
        self.sp_to_sql_table = QTableWidget(0, 2)
        self.sp_to_sql_table.setHorizontalHeaderLabels(
            ["SharePoint Field", "SQL Column"]
        )
        self.sp_to_sql_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.sp_to_sql_table.setVerticalHeaderLabels(
            ["Row 1", "Row 2", "Row 3", "Row 4", "Row 5"]
        )  # Initial rows
        self.sp_to_sql_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        sp_to_sql_layout.addWidget(self.sp_to_sql_table)

        sp_to_sql_buttons_layout = QHBoxLayout()
        self.add_sp_to_sql_row_btn = ModernButton("Add Row", "ghost", "sm", icon="➕")
        self.remove_sp_to_sql_row_btn = ModernButton(
            "Remove Row", "danger", "sm", icon="➖"
        )
        sp_to_sql_buttons_layout.addWidget(self.add_sp_to_sql_row_btn)
        sp_to_sql_buttons_layout.addWidget(self.remove_sp_to_sql_row_btn)
        sp_to_sql_layout.addLayout(sp_to_sql_buttons_layout)
        sp_to_sql_group.setLayout(sp_to_sql_layout)
        layout.addWidget(sp_to_sql_group)

        # SQL to SharePoint Mapping
        sql_to_sp_group = NeonGroupBox("SQL to SharePoint Mapping")
        sql_to_sp_layout = QVBoxLayout(sql_to_sp_group)
        self.sql_to_sp_table = QTableWidget(0, 2)
        self.sql_to_sp_table.setHorizontalHeaderLabels(
            ["SQL Column", "SharePoint Field"]
        )
        self.sql_to_sp_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.sql_to_sp_table.setVerticalHeaderLabels(
            ["Row 1", "Row 2", "Row 3", "Row 4", "Row 5"]
        )  # Initial rows
        self.sql_to_sp_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        sql_to_sp_layout.addWidget(self.sql_to_sp_table)

        sql_to_sp_buttons_layout = QHBoxLayout()
        self.add_sql_to_sp_row_btn = ModernButton("Add Row", "ghost", "sm", icon="➕")
        self.remove_sql_to_sp_row_btn = ModernButton(
            "Remove Row", "danger", "sm", icon="➖"
        )
        sql_to_sp_buttons_layout.addWidget(self.add_sql_to_sp_row_btn)
        sql_to_sp_buttons_layout.addWidget(self.remove_sql_to_sp_row_btn)
        sql_to_sp_layout.addLayout(sql_to_sp_buttons_layout)
        sql_to_sp_group.setLayout(sql_to_sp_layout)
        layout.addWidget(sql_to_sp_group)

        layout.addStretch(1)
        self.tab_widget.addTab(mapping_tab, "Data Mapping")

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.MEDIUM)
    def _add_advanced_settings_tab(self):
        advanced_tab = QScrollArea()
        advanced_tab.setWidgetResizable(True)
        content_widget = QWidget()
        advanced_tab.setWidget(content_widget)
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Connection and Performance Group
        conn_perf_group = NeonGroupBox("Connection & Performance")
        conn_perf_layout = QGridLayout(conn_perf_group)

        self.field_widgets["connection_timeout"] = FormField(
            ModernSpinBox(min_val=1), "Connection Timeout (seconds):"
        )
        conn_perf_layout.addWidget(self.field_widgets["connection_timeout"], 0, 0, 1, 2)

        self.field_widgets["max_retries"] = FormField(
            ModernSpinBox(min_val=0), "Max Retries for Network Ops:"
        )
        conn_perf_layout.addWidget(self.field_widgets["max_retries"], 1, 0, 1, 2)

        self.field_widgets["batch_size"] = FormField(
            ModernSpinBox(min_val=1), "Batch Size for Data Transfer:"
        )
        conn_perf_layout.addWidget(self.field_widgets["batch_size"], 2, 0, 1, 2)

        self.field_widgets["enable_parallel_processing"] = FormField(
            QCheckBox("Enable Parallel Processing"), ""
        )
        self.field_widgets["enable_parallel_processing"].input_widget.setStyleSheet(
            get_modern_checkbox_style()
        )
        conn_perf_layout.addWidget(
            self.field_widgets["enable_parallel_processing"], 3, 0, 1, 2
        )

        conn_perf_group.setLayout(conn_perf_layout)
        layout.addWidget(conn_perf_group)

        # Logging & Notifications Group
        log_notif_group = NeonGroupBox("Logging & Notifications")
        log_notif_layout = QGridLayout(log_notif_group)

        self.field_widgets["log_level"] = FormField(HolographicComboBox(), "Log Level:")
        self.field_widgets["log_level"].input_widget.addItems(
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        )
        log_notif_layout.addWidget(self.field_widgets["log_level"], 0, 0, 1, 2)

        self.field_widgets["enable_error_notifications"] = FormField(
            QCheckBox("Enable Error Popups"), ""
        )
        self.field_widgets["enable_error_notifications"].input_widget.setStyleSheet(
            get_modern_checkbox_style()
        )
        log_notif_layout.addWidget(
            self.field_widgets["enable_error_notifications"], 1, 0, 1, 2
        )

        self.field_widgets["enable_success_notifications"] = FormField(
            QCheckBox("Enable Success Popups"), ""
        )
        self.field_widgets["enable_success_notifications"].input_widget.setStyleSheet(
            get_modern_checkbox_style()
        )
        log_notif_layout.addWidget(
            self.field_widgets["enable_success_notifications"], 2, 0, 1, 2
        )

        log_notif_group.setLayout(log_notif_layout)
        layout.addWidget(log_notif_group)

        # Cache Management Group
        cache_group = NeonGroupBox("Cache Management")
        cache_layout = QGridLayout(cache_group)
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
            ModernSpinBox(min_val=1), "Cleanup Interval (hours):"
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
        """Loads current configuration into the UI fields."""
        config = self.config_manager.get_config()

        for key, field_widget in self.field_widgets.items():
            # Handle nested config paths
            value = self.config_manager.get_setting(key)
            if value is not None:
                field_widget.set_value(value)
            else:
                logger.warning(
                    f"Config key '{key}' not found or is None. Defaulting to widget's initial state."
                )

        # Special handling for auto_sync_enabled_checkbox as it's not a FormField wrapper
        self.auto_sync_enabled_checkbox.setChecked(config.auto_sync_enabled)

        # Set initial selection for database type selector
        db_type = config.database_type.lower()
        if db_type == "sqlserver":
            self.database_type_selector.setCurrentText("SQL Server")
            self.db_stacked_widget.setCurrentIndex(0)  # Index for SQL Server widget
        elif db_type == "sqlite":
            self.database_type_selector.setCurrentText("SQLite")
            self.db_stacked_widget.setCurrentIndex(1)  # Index for SQLite widget

        # Load mapping tables
        self._load_field_mapping_to_table(
            config.sharepoint_to_sql_mapping, self.sp_to_sql_table
        )
        self._load_field_mapping_to_table(
            config.sql_to_sharepoint_mapping, self.sql_to_sp_table
        )

        # Load Excel import mapping as JSON string
        excel_import_map = config.excel_import_mapping
        if excel_import_map:
            try:
                self.field_widgets["excel_import_mapping"].set_value(
                    json.dumps(excel_import_map, indent=2)
                )
            except TypeError as e:
                logger.error(
                    f"Error converting Excel import mapping to JSON string: {e}"
                )
                self.field_widgets["excel_import_mapping"].set_value(
                    "{}"
                )  # Set empty if error

        logger.info("Current configuration loaded into ConfigPanel UI.")

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.MEDIUM)
    def _load_field_mapping_to_table(self, mapping: dict, table_widget: QTableWidget):
        """Helper to load dictionary mapping into a QTableWidget."""
        table_widget.clearContents()
        table_widget.setRowCount(0)
        for key, value in mapping.items():
            row_position = table_widget.rowCount()
            table_widget.insertRow(row_position)
            table_widget.setItem(row_position, 0, QTableWidgetItem(str(key)))
            table_widget.setItem(row_position, 1, QTableWidgetItem(str(value)))
        # Ensure some empty rows for usability if the map is small
        if table_widget.rowCount() < 5:
            table_widget.setRowCount(5)

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.HIGH)
    def _connect_signals(self):
        """Connects UI elements to internal logic and config manager."""
        # Connect database type selector
        self.database_type_selector.currentIndexChanged.connect(
            self._on_db_type_changed
        )
        self.browse_sqlite_button.clicked.connect(self._browse_sqlite_file)

        # Connect all FormField input widgets to a generic save handler
        for key, field_widget in self.field_widgets.items():
            input_widget = field_widget.input_widget
            if isinstance(input_widget, QLineEdit):
                input_widget.textChanged.connect(
                    lambda text, k=key: self._defer_save_config_setting(k, text, "str")
                )
            elif isinstance(input_widget, ModernTextEdit):  # For JSON mapping
                input_widget.textChanged.connect(
                    lambda text, k=key: self._defer_save_config_setting(
                        k, text, "json_str"
                    )
                )
            elif isinstance(input_widget, QComboBox):
                input_widget.currentIndexChanged.connect(
                    lambda index, k=key: self._defer_save_config_setting(
                        k, input_widget.currentText(), "str"
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

        # Connect auto_sync_enabled checkbox directly
        self.auto_sync_enabled_checkbox.stateChanged.connect(
            self._on_auto_sync_checkbox_changed
        )

        # Connect mapping table buttons
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

        # Connect table item changed signal to deferred save
        self.sp_to_sql_table.itemChanged.connect(self._defer_save_mapping)
        self.sql_to_sp_table.itemChanged.connect(self._defer_save_mapping)

        # Connect AppController's config_updated signal to reload config in UI
        self.controller.config_changed.connect(
            self._load_current_config
        )  # Or a more specific signal

        logger.debug("ConfigPanel signals connected.")

    @pyqtSlot(int)
    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.LOW)
    def _on_db_type_changed(self, index: int):
        """Handles change in database type selector."""
        self.db_stacked_widget.setCurrentIndex(index)
        selected_db_type = (
            self.database_type_selector.currentText().lower().replace(" ", "")
        )
        # Update config manager immediately for database_type
        self.request_update_config_setting.emit(
            "database_type", selected_db_type, "str"
        )
        if selected_db_type == "sqlserver":
            self.request_update_config_setting.emit(
                "db_type", "SQL Server", "str"
            )  # Ensure db_type is consistent
        elif selected_db_type == "sqlite":
            self.request_update_config_setting.emit("db_type", "SQLite", "str")

    @pyqtSlot()
    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.MEDIUM)
    def _browse_sqlite_file(self):
        """Opens a file dialog to select SQLite database file."""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Select SQLite Database File",
            "",
            "SQLite Database Files (*.db);;All Files (*)",
        )
        if file_name:
            self.field_widgets["sqlite_file"].set_value(file_name)
            self.request_update_config_setting.emit("sqlite_file", file_name, "str")
            logger.info(f"SQLite file path set to: {file_name}")

    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.LOW)
    def _defer_save_config_setting(self, key_path: str, value: Any, value_type: str):
        """Defers saving a config setting to prevent rapid saves."""
        # This will eventually trigger the AppController's update_setting method
        # For now, directly update via ConfigManager and let its signal handle reload.
        self.request_update_config_setting.emit(key_path, value, value_type)
        logger.debug(f"Deferred save for {key_path}: {value}")

    @pyqtSlot(int)
    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.LOW)
    def _on_auto_sync_checkbox_changed(self, state: int):
        """Handles changes in the auto-sync checkbox and requests AppController to toggle."""
        is_checked = state == Qt.CheckState.Checked.value
        self.request_auto_sync_toggle.emit(is_checked)
        logger.info(f"Auto-sync checkbox changed to: {is_checked}")

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.LOW)
    def _add_mapping_row(self, table_widget: QTableWidget):
        """Adds a new empty row to a mapping table."""
        row_position = table_widget.rowCount()
        table_widget.insertRow(row_position)
        table_widget.setItem(row_position, 0, QTableWidgetItem(""))
        table_widget.setItem(row_position, 1, QTableWidgetItem(""))
        table_widget.setVerticalHeaderLabels(
            [f"Row {i+1}" for i in range(table_widget.rowCount())]
        )  # Update row headers

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.LOW)
    def _remove_mapping_row(self, table_widget: QTableWidget):
        """Removes selected rows from a mapping table."""
        selected_rows = sorted(
            set(index.row() for index in table_widget.selectedIndexes()), reverse=True
        )
        if not selected_rows:
            QMessageBox.information(
                self, "No Row Selected", "Please select row(s) to remove."
            )
            return

        for row in selected_rows:
            table_widget.removeRow(row)
        table_widget.setVerticalHeaderLabels(
            [f"Row {i+1}" for i in range(table_widget.rowCount())]
        )  # Update row headers
        self._defer_save_mapping()  # Trigger save after modification

    @pyqtSlot()
    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.LOW)
    def _defer_save_mapping(self):
        """Starts a timer to defer saving mapping changes."""
        if self._mapping_save_timer.isActive():
            self._mapping_save_timer.stop()
        self._mapping_save_timer.start()

    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.MEDIUM)
    def _save_field_mappings(self):
        """Saves the field mappings from the table widgets to config."""
        logger.info("Saving field mappings...")

        sp_to_sql_map = self._get_mapping_from_table(self.sp_to_sql_table)
        sql_to_sp_map = self._get_mapping_from_table(self.sql_to_sp_table)

        # Validate mappings before saving
        sp_to_sql_valid = GeneralValidator.validate_mapping(sp_to_sql_map)
        sql_to_sp_valid = GeneralValidator.validate_mapping(sql_to_sp_map)

        if not sp_to_sql_valid.is_valid:
            self.controller.log_message.emit(
                f"SharePoint to SQL mapping invalid: {sp_to_sql_valid.message}", "error"
            )
            logger.error(
                f"SharePoint to SQL mapping validation failed: {sp_to_sql_valid.message}"
            )
        else:
            self.config_manager.update_setting(
                "sharepoint_to_sql_mapping", sp_to_sql_map
            )

        if not sql_to_sp_valid.is_valid:
            self.controller.log_message.emit(
                f"SQL to SharePoint mapping invalid: {sql_to_sp_valid.message}", "error"
            )
            logger.error(
                f"SQL to SharePoint mapping validation failed: {sql_to_sp_valid.message}"
            )
        else:
            self.config_manager.update_setting(
                "sql_to_sharepoint_mapping", sql_to_sp_map
            )

        # Save Excel import mapping from its text edit field
        excel_import_map_str = self.field_widgets["excel_import_mapping"].get_value()
        try:
            excel_import_map_dict = json.loads(excel_import_map_str)
            excel_import_map_valid = GeneralValidator.validate_mapping(
                excel_import_map_dict
            )
            if excel_import_map_valid.is_valid:
                self.config_manager.update_setting(
                    "excel_import_mapping", excel_import_map_dict
                )
            else:
                self.controller.log_message.emit(
                    f"Excel import mapping invalid: {excel_import_map_valid.message}",
                    "error",
                )
                logger.error(
                    f"Excel import mapping validation failed: {excel_import_map_valid.message}"
                )
        except json.JSONDecodeError:
            self.controller.log_message.emit(
                "Excel import mapping is not a valid JSON. Please correct it.", "error"
            )
            logger.error("Excel import mapping JSON decode error.")
        except Exception as e:
            self.controller.log_message.emit(
                f"Error parsing Excel import mapping: {e}", "error"
            )
            logger.error(f"Error parsing Excel import mapping: {e}")

        self.config_changed.emit()  # Notify parent (AppController) that config has changed
        logger.info("Field mappings saved.")

    @handle_exceptions(ErrorCategory.DATA, ErrorSeverity.LOW)
    def _get_mapping_from_table(self, table_widget: QTableWidget) -> dict:
        """Helper to retrieve dictionary mapping from a QTableWidget."""
        mapping = {}
        for row in range(table_widget.rowCount()):
            key_item = table_widget.item(row, 0)
            value_item = table_widget.item(row, 1)
            if key_item and value_item:
                key = key_item.text().strip()
                value = value_item.text().strip()
                if key and value:  # Only add if both key and value are non-empty
                    mapping[key] = value
        return mapping

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.CRITICAL)
    def cleanup(self):
        """Performs cleanup for the ConfigPanel."""
        if self.cleanup_done:
            logger.debug("ConfigPanel cleanup already performed, skipping.")
            return

        logger.info("Initiating ConfigPanel cleanup...")
        try:
            # Stop deferred save timer if active
            if self._mapping_save_timer and self._mapping_save_timer.isActive():
                self._mapping_save_timer.stop()
                self._mapping_save_timer.deleteLater()
                self._mapping_save_timer = None
                logger.debug("Mapping save timer stopped and deleted.")

            # Disconnect all signals from form fields
            for key, field_widget in self.field_widgets.items():
                input_widget = field_widget.input_widget
                if isinstance(input_widget, QLineEdit):
                    try:
                        input_widget.textChanged.disconnect()
                    except TypeError:
                        pass
                elif isinstance(input_widget, ModernTextEdit):
                    try:
                        input_widget.textChanged.disconnect()
                    except TypeError:
                        pass
                elif isinstance(input_widget, QComboBox):
                    try:
                        input_widget.currentIndexChanged.disconnect()
                    except TypeError:
                        pass
                elif isinstance(input_widget, ModernSpinBox):
                    try:
                        input_widget.valueChanged.disconnect()
                    except TypeError:
                        pass
                elif isinstance(input_widget, QCheckBox):
                    try:
                        input_widget.stateChanged.disconnect()
                    except TypeError:
                        pass
                field_widget.deleteLater()  # Delete the FormField wrapper

            # Disconnect specific signals
            self.database_type_selector.currentIndexChanged.disconnect(
                self._on_db_type_changed
            )
            self.browse_sqlite_button.clicked.disconnect(self._browse_sqlite_file)
            self.auto_sync_enabled_checkbox.stateChanged.disconnect(
                self._on_auto_sync_checkbox_changed
            )
            self.add_sp_to_sql_row_btn.clicked.disconnect()
            self.remove_sp_to_sql_row_btn.clicked.disconnect()
            self.add_sql_to_sp_row_btn.clicked.disconnect()
            self.remove_sql_to_sp_row_btn.clicked.disconnect()

            # Disconnect table item changed signals
            self.sp_to_sql_table.itemChanged.disconnect(self._defer_save_mapping)
            self.sql_to_sp_table.itemChanged.disconnect(self._defer_save_mapping)

            # Disconnect AppController's config_updated signal (if connected)
            try:
                self.controller.config_changed.disconnect(self._load_current_config)
            except TypeError:
                pass  # Signal might not be connected if app closed before full init

            # Ensure all child widgets are properly cleaned up
            for child in self.findChildren(QWidget):
                if child is not self:  # Don't delete self
                    child.deleteLater()

            self.cleanup_done = True
            logger.info("ConfigPanel cleanup completed.")
        except Exception as e:
            logger.error(f"Error during ConfigPanel cleanup: {e}", exc_info=True)
            self.cleanup_done = True  # Mark as done to prevent recursive errors
