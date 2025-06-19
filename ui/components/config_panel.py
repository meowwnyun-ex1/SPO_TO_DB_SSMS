from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QFormLayout,
    QLineEdit,
    QCheckBox,
    QSpinBox,
    QPushButton,
    QLabel,
    QSizePolicy,
)
from PyQt6.QtCore import pyqtSignal, Qt, pyqtSlot
from ..styles.theme import (
    get_holographic_tab_style,
    get_ultra_modern_input_style,
    get_neon_checkbox_style,
    get_ultra_modern_button_style,
    UltraModernColors,
)
from utils.config_validation import quick_validate_sharepoint, quick_validate_database
from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity

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
            config.client_id,
            config.client_secret,
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
        self.config.db_type = ui_data.get("db_type", "SQL Server")
        self.config.db_host = ui_data.get("db_host", "")
        self.config.db_port = ui_data.get("db_port", 1433)
        self.config.db_name = ui_data.get("db_name", "")
        self.config.db_table = ui_data.get("db_table", "")
        self.config.db_username = ui_data.get("db_username", "")
        self.config.db_password = ui_data.get("db_password", "")
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

        # แก้: ใช้ config_manager แทน config.save_config()
        self.config_manager.save_config(self.config)
        return True


class UltraModernConfigPanel(QWidget):
    """แก้แล้ว: แยก business logic ออกไป, เหลือแค่ UI"""

    # Signals
    config_changed = pyqtSignal(object)
    test_sharepoint_requested = pyqtSignal()
    test_database_requested = pyqtSignal()
    refresh_sites_requested = pyqtSignal()
    refresh_lists_requested = pyqtSignal()
    refresh_databases_requested = pyqtSignal()
    refresh_tables_requested = pyqtSignal()
    auto_sync_toggled = pyqtSignal(bool)
    run_sync_requested = pyqtSignal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # แก้: แยก data management ออกมา
        self.data_manager = ConfigDataManager()
        self.validator = ConfigValidator()

        # UI components cache
        self.inputs = {}

        self.setup_ultra_modern_ui()
        self._load_config_to_ui()

    def setup_ultra_modern_ui(self):
        """แก้แล้ว: เน้น UI structure อย่างเดียว"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(get_holographic_tab_style())
        self.tab_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # สร้าง tabs
        self._create_sharepoint_tab()
        self._create_database_tab()
        self._create_general_tab()

        layout.addWidget(self.tab_widget)
        layout.addStretch(1)

        self._connect_signals()

    def _create_sharepoint_tab(self):
        """สร้าง SharePoint tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        group = NeonGroupBox("☁️ SharePoint Connection")
        form_layout = QFormLayout(group)
        form_layout.setSpacing(16)

        # SharePoint URL
        self.inputs["sharepoint_url"] = QLineEdit()
        self.inputs["sharepoint_url"].setPlaceholderText(
            "https://company.sharepoint.com"
        )
        self.inputs["sharepoint_url"].setStyleSheet(get_ultra_modern_input_style())
        form_layout.addRow(
            self._create_label("SharePoint URL:"), self.inputs["sharepoint_url"]
        )

        # Site selection
        self.inputs["sharepoint_site"] = HolographicComboBox()
        self.refresh_sites_button = QPushButton("Refresh Sites")
        self.refresh_sites_button.setStyleSheet(get_ultra_modern_button_style("ghost"))
        site_layout = QHBoxLayout()
        site_layout.addWidget(self.inputs["sharepoint_site"])
        site_layout.addWidget(self.refresh_sites_button)
        form_layout.addRow(self._create_label("Site Name:"), site_layout)

        # List selection
        self.inputs["sharepoint_list"] = HolographicComboBox()
        self.refresh_lists_button = QPushButton("Refresh Lists")
        self.refresh_lists_button.setStyleSheet(get_ultra_modern_button_style("ghost"))
        list_layout = QHBoxLayout()
        list_layout.addWidget(self.inputs["sharepoint_list"])
        list_layout.addWidget(self.refresh_lists_button)
        form_layout.addRow(self._create_label("List Name:"), list_layout)

        layout.addWidget(group)

        # Test button
        test_button = QPushButton("Test SharePoint Connection")
        test_button.setStyleSheet(get_ultra_modern_button_style("primary"))
        test_button.clicked.connect(self.test_sharepoint_requested)
        layout.addWidget(test_button)
        layout.addStretch(1)

        self.tab_widget.addTab(tab, "SharePoint")

    def _create_database_tab(self):
        """สร้าง Database tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        group = NeonGroupBox("💾 Database Connection")
        form_layout = QFormLayout(group)
        form_layout.setSpacing(16)

        # Database type
        self.inputs["db_type"] = HolographicComboBox()
        self.inputs["db_type"].addItems(["SQL Server", "PostgreSQL", "MySQL"])
        form_layout.addRow(self._create_label("DB Type:"), self.inputs["db_type"])

        # Host & Port
        self.inputs["db_host"] = QLineEdit()
        self.inputs["db_host"].setPlaceholderText("localhost")
        self.inputs["db_host"].setStyleSheet(get_ultra_modern_input_style())
        form_layout.addRow(self._create_label("DB Host:"), self.inputs["db_host"])

        self.inputs["db_port"] = QSpinBox()
        self.inputs["db_port"].setRange(1, 65535)
        self.inputs["db_port"].setValue(1433)
        self.inputs["db_port"].setStyleSheet(get_ultra_modern_input_style())
        form_layout.addRow(self._create_label("DB Port:"), self.inputs["db_port"])

        # Database & Table
        self.inputs["db_name"] = HolographicComboBox()
        self.refresh_databases_button = QPushButton("Refresh DBs")
        self.refresh_databases_button.setStyleSheet(
            get_ultra_modern_button_style("ghost")
        )
        db_layout = QHBoxLayout()
        db_layout.addWidget(self.inputs["db_name"])
        db_layout.addWidget(self.refresh_databases_button)
        form_layout.addRow(self._create_label("DB Name:"), db_layout)

        self.inputs["db_table"] = HolographicComboBox()
        self.refresh_tables_button = QPushButton("Refresh Tables")
        self.refresh_tables_button.setStyleSheet(get_ultra_modern_button_style("ghost"))
        table_layout = QHBoxLayout()
        table_layout.addWidget(self.inputs["db_table"])
        table_layout.addWidget(self.refresh_tables_button)
        form_layout.addRow(self._create_label("Table Name:"), table_layout)

        # Credentials
        self.inputs["db_username"] = QLineEdit()
        self.inputs["db_username"].setPlaceholderText("username")
        self.inputs["db_username"].setStyleSheet(get_ultra_modern_input_style())
        form_layout.addRow(self._create_label("DB User:"), self.inputs["db_username"])

        self.inputs["db_password"] = QLineEdit()
        self.inputs["db_password"].setEchoMode(QLineEdit.EchoMode.Password)
        self.inputs["db_password"].setPlaceholderText("password")
        self.inputs["db_password"].setStyleSheet(get_ultra_modern_input_style())
        form_layout.addRow(self._create_label("DB Pass:"), self.inputs["db_password"])

        layout.addWidget(group)

        # Test button
        test_button = QPushButton("Test Database Connection")
        test_button.setStyleSheet(get_ultra_modern_button_style("primary"))
        test_button.clicked.connect(self.test_database_requested)
        layout.addWidget(test_button)
        layout.addStretch(1)

        self.tab_widget.addTab(tab, "Database")

    def _create_general_tab(self):
        """สร้าง General tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Sync settings
        sync_group = NeonGroupBox("⏱️ Synchronization Protocol")
        sync_layout = QFormLayout(sync_group)
        sync_layout.setSpacing(16)

        self.inputs["sync_interval"] = QSpinBox()
        self.inputs["sync_interval"].setRange(1, 1440)
        self.inputs["sync_interval"].setValue(60)
        self.inputs["sync_interval"].setSuffix(" minutes")
        self.inputs["sync_interval"].setStyleSheet(get_ultra_modern_input_style())
        sync_layout.addRow(
            self._create_label("Sync Interval:"), self.inputs["sync_interval"]
        )

        self.inputs["auto_sync_enabled"] = QCheckBox("◦ Enable Automatic Sync")
        self.inputs["auto_sync_enabled"].setStyleSheet(get_neon_checkbox_style())
        sync_layout.addRow("", self.inputs["auto_sync_enabled"])

        layout.addWidget(sync_group)

        # Performance settings
        perf_group = NeonGroupBox("⚡ Performance Tuning")
        perf_layout = QFormLayout(perf_group)
        perf_layout.setSpacing(16)

        self.inputs["batch_size"] = QSpinBox()
        self.inputs["batch_size"].setRange(100, 10000)
        self.inputs["batch_size"].setSingleStep(100)
        self.inputs["batch_size"].setValue(1000)
        self.inputs["batch_size"].setStyleSheet(get_ultra_modern_input_style())
        perf_layout.addRow(self._create_label("Batch Size:"), self.inputs["batch_size"])

        self.inputs["parallel_processing"] = QCheckBox("◦ Enable parallel processing")
        self.inputs["parallel_processing"].setStyleSheet(get_neon_checkbox_style())
        perf_layout.addRow("", self.inputs["parallel_processing"])

        layout.addWidget(perf_group)

        # Notification settings
        notif_group = NeonGroupBox("◈ Notifications")
        notif_layout = QFormLayout(notif_group)
        notif_layout.setSpacing(16)

        self.inputs["success_notifications"] = QCheckBox("◦ Success notifications")
        self.inputs["success_notifications"].setStyleSheet(get_neon_checkbox_style())
        self.inputs["success_notifications"].setChecked(True)
        notif_layout.addRow("", self.inputs["success_notifications"])

        self.inputs["error_notifications"] = QCheckBox("◦ Error notifications")
        self.inputs["error_notifications"].setStyleSheet(get_neon_checkbox_style())
        self.inputs["error_notifications"].setChecked(True)
        notif_layout.addRow("", self.inputs["error_notifications"])

        layout.addWidget(notif_group)
        layout.addStretch(1)

        self.tab_widget.addTab(tab, "General")

    def _create_label(self, text):
        """สร้าง label พร้อม styling"""
        label = QLabel(text)
        label.setStyleSheet(
            f"color: {UltraModernColors.TEXT_ACCENT}; font-weight: bold; padding-right: 5px;"
        )
        label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return label

    def _connect_signals(self):
        """เชื่อมต่อ signals"""
        # Input changes → save config (แก้: ใช้ lambda เพื่อไม่ส่ง arguments)
        for key, widget in self.inputs.items():
            if isinstance(widget, (QLineEdit, QSpinBox)):
                if hasattr(widget, "textChanged"):
                    widget.textChanged.connect(lambda: self._save_config_from_ui())
                else:
                    widget.valueChanged.connect(lambda: self._save_config_from_ui())
            elif isinstance(widget, QCheckBox):
                widget.stateChanged.connect(lambda: self._save_config_from_ui())
            elif isinstance(widget, HolographicComboBox):
                widget.currentTextChanged.connect(lambda: self._save_config_from_ui())

        # Auto sync toggle
        self.inputs["auto_sync_enabled"].stateChanged.connect(
            lambda: self.auto_sync_toggled.emit(
                self.inputs["auto_sync_enabled"].isChecked()
            )
        )

        # Refresh buttons
        self.refresh_sites_button.clicked.connect(self.refresh_sites_requested)
        self.refresh_lists_button.clicked.connect(self.refresh_lists_requested)
        self.refresh_databases_button.clicked.connect(self.refresh_databases_requested)
        self.refresh_tables_button.clicked.connect(self.refresh_tables_requested)

    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.LOW)
    def _save_config_from_ui(self):
        """บันทึก config จาก UI"""
        ui_data = {}
        for key, widget in self.inputs.items():
            if isinstance(widget, QLineEdit):
                ui_data[key] = widget.text()
            elif isinstance(widget, QSpinBox):
                ui_data[key] = widget.value()
            elif isinstance(widget, QCheckBox):
                ui_data[key] = widget.isChecked()
            elif isinstance(widget, HolographicComboBox):
                ui_data[key] = widget.currentText()

        success = self.data_manager.save_config(ui_data)
        if success:
            self.config_changed.emit(self.data_manager.config)
            logger.info("Configuration updated")

    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.LOW)
    def _load_config_to_ui(self):
        """โหลด config มาแสดงใน UI"""
        config = self.data_manager.load_config()

        # Map config to UI
        if "sharepoint_url" in self.inputs:
            self.inputs["sharepoint_url"].setText(config.sharepoint_url)
        if "db_host" in self.inputs:
            self.inputs["db_host"].setText(config.db_host)
        if "db_port" in self.inputs:
            self.inputs["db_port"].setValue(config.db_port)
        if "sync_interval" in self.inputs:
            self.inputs["sync_interval"].setValue(config.sync_interval)
        if "batch_size" in self.inputs:
            self.inputs["batch_size"].setValue(config.batch_size)
        if "auto_sync_enabled" in self.inputs:
            self.inputs["auto_sync_enabled"].setChecked(config.auto_sync_enabled)

        logger.info("Configuration loaded to UI")

    # UI state management
    @pyqtSlot(bool)
    def set_ui_enabled(self, enable: bool):
        """เปิด/ปิด UI elements"""
        self.tab_widget.setEnabled(enable)
        self.refresh_sites_button.setEnabled(enable)
        self.refresh_lists_button.setEnabled(enable)
        self.refresh_databases_button.setEnabled(enable)
        self.refresh_tables_button.setEnabled(enable)

    # Data population slots
    @pyqtSlot(list)
    def populate_sharepoint_sites(self, sites):
        if "sharepoint_site" in self.inputs:
            self.inputs["sharepoint_site"].clear()
            self.inputs["sharepoint_site"].addItems(sites)

    @pyqtSlot(list)
    def populate_sharepoint_lists(self, lists):
        if "sharepoint_list" in self.inputs:
            self.inputs["sharepoint_list"].clear()
            self.inputs["sharepoint_list"].addItems(lists)

    @pyqtSlot(list)
    def populate_database_names(self, db_names):
        if "db_name" in self.inputs:
            self.inputs["db_name"].clear()
            self.inputs["db_name"].addItems(db_names)

    @pyqtSlot(list)
    def populate_database_tables(self, tables):
        if "db_table" in self.inputs:
            self.inputs["db_table"].clear()
            self.inputs["db_table"].addItems(tables)
