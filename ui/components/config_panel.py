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
    QLabel,  # Added QLabel for creating neon labels
    QSizePolicy,  # Import QSizePolicy for setSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt, pyqtSlot  # Added pyqtSlot
from ..styles.theme import (
    get_holographic_tab_style,
    get_ultra_modern_input_style,
    get_neon_checkbox_style,
    get_ultra_modern_button_style,  # Import for buttons
    UltraModernColors,  # Import for colors
)
from utils.config_manager import AppConfig

# Corrected import paths for widgets: from .widgets.x to from ..widgets.x
from ..widgets.holographic_combobox import HolographicComboBox
from ..widgets.neon_groupbox import NeonGroupBox
import logging

logger = logging.getLogger(__name__)


class UltraModernConfigPanel(
    QWidget
):  # Renamed class from ConfigPanel to UltraModernConfigPanel
    """
    Ultra Modern Configuration Panel with responsive design
    ปรับให้แสดงผลในหน้าเดียวโดยไม่มี Scrollbar และปรับขนาดได้
    """

    # Signals
    config_changed = pyqtSignal(object)
    test_sharepoint_requested = pyqtSignal()
    test_database_requested = pyqtSignal()
    refresh_sites_requested = pyqtSignal()
    refresh_lists_requested = pyqtSignal()
    refresh_databases_requested = pyqtSignal()
    refresh_tables_requested = pyqtSignal()
    auto_sync_toggled = pyqtSignal(bool)  # Signal for auto sync toggle
    run_sync_requested = pyqtSignal()  # Signal for manual sync run

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.config = AppConfig()
        self.setup_ultra_modern_ui()
        self.setup_background_effects()  # Keep if it adds specific effects not handled by parent
        self._load_config_to_ui()  # Load initial config

    def setup_ultra_modern_ui(self):
        """
        ตั้งค่า UI แบบ ultra modern สำหรับ Config Panel
        ใช้ QTabWidget และ QFormLayout เพื่อจัดเรียงข้อมูล
        """
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)  # Adjusted spacing

        # Tab Widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(get_holographic_tab_style())
        self.tab_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )  # Allow tabs to expand

        # SharePoint Tab
        sharepoint_tab = QWidget()
        sharepoint_layout = QVBoxLayout(sharepoint_tab)
        sharepoint_layout.setContentsMargins(15, 15, 15, 15)
        sharepoint_layout.setSpacing(15)

        sharepoint_group = NeonGroupBox("☁️ SharePoint Connection")
        sharepoint_form_layout = QFormLayout(sharepoint_group)
        sharepoint_form_layout.setSpacing(16)

        self.sharepoint_url_input = QLineEdit()
        self.sharepoint_url_input.setPlaceholderText(
            "https://yourcompany.sharepoint.com"
        )
        self.sharepoint_url_input.setStyleSheet(get_ultra_modern_input_style())
        sharepoint_form_layout.addRow(
            self.create_neon_label("SharePoint URL:"), self.sharepoint_url_input
        )

        self.sharepoint_site_combo = HolographicComboBox()
        self.sharepoint_site_combo.setStyleSheet(get_ultra_modern_input_style())
        self.refresh_sites_button = QPushButton("Refresh Sites")
        self.refresh_sites_button.setStyleSheet(get_ultra_modern_button_style("ghost"))
        site_h_layout = QHBoxLayout()
        site_h_layout.addWidget(self.sharepoint_site_combo)
        site_h_layout.addWidget(self.refresh_sites_button)
        sharepoint_form_layout.addRow(
            self.create_neon_label("Site Name:"), site_h_layout
        )

        self.sharepoint_list_combo = HolographicComboBox()
        self.sharepoint_list_combo.setStyleSheet(get_ultra_modern_input_style())
        self.refresh_lists_button = QPushButton("Refresh Lists")
        self.refresh_lists_button.setStyleSheet(get_ultra_modern_button_style("ghost"))
        list_h_layout = QHBoxLayout()
        list_h_layout.addWidget(self.sharepoint_list_combo)
        list_h_layout.addWidget(self.refresh_lists_button)
        sharepoint_form_layout.addRow(
            self.create_neon_label("List Name:"), list_h_layout
        )

        sharepoint_layout.addWidget(sharepoint_group)

        # Test SharePoint Connection Button
        test_sharepoint_button = QPushButton("Test SharePoint Connection")
        test_sharepoint_button.setStyleSheet(get_ultra_modern_button_style("primary"))
        sharepoint_layout.addWidget(test_sharepoint_button)
        sharepoint_layout.addStretch(1)  # Pushes content to top

        self.tab_widget.addTab(sharepoint_tab, "SharePoint")

        # Database Tab
        database_tab = QWidget()
        database_layout = QVBoxLayout(database_tab)
        database_layout.setContentsMargins(15, 15, 15, 15)
        database_layout.setSpacing(15)

        db_group = NeonGroupBox("💾 Database Connection")
        db_form_layout = QFormLayout(db_group)
        db_form_layout.setSpacing(16)

        self.db_type_combo = HolographicComboBox()
        self.db_type_combo.addItems(["SQL Server", "PostgreSQL", "MySQL"])
        self.db_type_combo.setStyleSheet(get_ultra_modern_input_style())
        db_form_layout.addRow(self.create_neon_label("DB Type:"), self.db_type_combo)

        self.db_host_input = QLineEdit()
        self.db_host_input.setPlaceholderText("localhost")
        self.db_host_input.setStyleSheet(get_ultra_modern_input_style())
        db_form_layout.addRow(self.create_neon_label("DB Host:"), self.db_host_input)

        self.db_port_spinbox = QSpinBox()
        self.db_port_spinbox.setRange(1, 65535)
        self.db_port_spinbox.setValue(1433)  # Default for SQL Server
        self.db_port_spinbox.setStyleSheet(get_ultra_modern_input_style())
        db_form_layout.addRow(self.create_neon_label("DB Port:"), self.db_port_spinbox)

        self.db_name_combo = HolographicComboBox()
        self.db_name_combo.setStyleSheet(get_ultra_modern_input_style())
        self.refresh_databases_button = QPushButton("Refresh DBs")
        self.refresh_databases_button.setStyleSheet(
            get_ultra_modern_button_style("ghost")
        )
        db_name_h_layout = QHBoxLayout()
        db_name_h_layout.addWidget(self.db_name_combo)
        db_name_h_layout.addWidget(self.refresh_databases_button)
        db_form_layout.addRow(self.create_neon_label("DB Name:"), db_name_h_layout)

        self.db_table_combo = HolographicComboBox()
        self.db_table_combo.setStyleSheet(get_ultra_modern_input_style())
        self.refresh_tables_button = QPushButton("Refresh Tables")
        self.refresh_tables_button.setStyleSheet(get_ultra_modern_button_style("ghost"))
        db_table_h_layout = QHBoxLayout()
        db_table_h_layout.addWidget(self.db_table_combo)
        db_table_h_layout.addWidget(self.refresh_tables_button)
        db_form_layout.addRow(self.create_neon_label("Table Name:"), db_table_h_layout)

        self.db_username_input = QLineEdit()
        self.db_username_input.setPlaceholderText("username")
        self.db_username_input.setStyleSheet(get_ultra_modern_input_style())
        db_form_layout.addRow(
            self.create_neon_label("DB User:"), self.db_username_input
        )

        self.db_password_input = QLineEdit()
        self.db_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.db_password_input.setPlaceholderText("password")
        self.db_password_input.setStyleSheet(get_ultra_modern_input_style())
        db_form_layout.addRow(
            self.create_neon_label("DB Pass:"), self.db_password_input
        )

        db_layout.addWidget(db_group)

        # Test Database Connection Button
        test_database_button = QPushButton("Test Database Connection")
        test_database_button.setStyleSheet(get_ultra_modern_button_style("primary"))
        database_layout.addWidget(test_database_button)
        database_layout.addStretch(1)  # Pushes content to top

        self.tab_widget.addTab(database_tab, "Database")

        # General Settings Tab
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        general_layout.setContentsMargins(15, 15, 15, 15)
        general_layout.setSpacing(15)

        # Sync Frequency
        sync_group = NeonGroupBox("⏱️ Synchronization Protocol")
        sync_layout = QFormLayout(sync_group)
        sync_layout.setSpacing(16)

        self.sync_interval_spinbox = QSpinBox()
        self.sync_interval_spinbox.setRange(1, 1440)  # Minutes, up to 24 hours
        self.sync_interval_spinbox.setValue(60)  # Default to 60 minutes
        self.sync_interval_spinbox.setSuffix(" minutes")
        self.sync_interval_spinbox.setStyleSheet(get_ultra_modern_input_style())
        sync_layout.addRow(
            self.create_neon_label("Sync Interval:"), self.sync_interval_spinbox
        )

        self.auto_sync_enable_check = QCheckBox("◦ Enable Automatic Sync")
        self.auto_sync_enable_check.setStyleSheet(get_neon_checkbox_style())
        self.auto_sync_enable_check.setChecked(False)  # Default to false
        sync_layout.addRow("", self.auto_sync_enable_check)

        general_layout.addWidget(sync_group)

        # Performance Settings
        perf_group = NeonGroupBox("⚡ Quantum Performance Tuning")
        perf_layout = QFormLayout(perf_group)
        perf_layout.setSpacing(16)

        self.batch_size_spinbox = QSpinBox()
        self.batch_size_spinbox.setRange(100, 10000)
        self.batch_size_spinbox.setSingleStep(100)
        self.batch_size_spinbox.setValue(1000)
        self.batch_size_spinbox.setStyleSheet(get_ultra_modern_input_style())
        perf_layout.addRow(
            self.create_neon_label("Batch Size:"), self.batch_size_spinbox
        )

        self.parallel_check = QCheckBox("◦ Enable parallel quantum processing")
        self.parallel_check.setStyleSheet(get_neon_checkbox_style())
        perf_layout.addRow("", self.parallel_check)

        general_layout.addWidget(perf_group)

        # Matrix Monitoring Settings
        log_group = NeonGroupBox("◎ Neural Activity Monitoring")
        log_layout = QFormLayout(log_group)
        log_layout.setSpacing(16)

        # Log Level
        self.log_level_combo = HolographicComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level_combo.setCurrentText("INFO")
        self.log_level_combo.setStyleSheet(get_ultra_modern_input_style())
        log_layout.addRow(
            self.create_neon_label("Monitor Level:"), self.log_level_combo
        )

        general_layout.addWidget(log_group)

        # Notification Matrix
        notif_group = NeonGroupBox("◈ Alert Transmission Protocol")
        notif_layout = QFormLayout(notif_group)
        notif_layout.setSpacing(16)

        self.success_notif_check = QCheckBox("◦ Success neural transmissions")
        self.success_notif_check.setStyleSheet(get_neon_checkbox_style())
        self.success_notif_check.setChecked(True)
        notif_layout.addRow("", self.success_notif_check)

        self.error_notif_check = QCheckBox("◦ Error neural alerts")
        self.error_notif_check.setStyleSheet(get_neon_checkbox_style())
        self.error_notif_check.setChecked(True)
        notif_layout.addRow("", self.error_notif_check)

        general_layout.addWidget(notif_group)
        general_layout.addStretch(1)  # Pushes content to top

        self.tab_widget.addTab(general_tab, "General")

        layout.addWidget(self.tab_widget)
        layout.addStretch(1)  # Ensures the tab widget expands

        self._connect_signals()

    def create_neon_label(self, text):
        """Creates a QLabel with neon text style."""
        label = QLabel(text)
        label.setStyleSheet(
            f"color: {UltraModernColors.TEXT_ACCENT}; font-weight: bold; padding-right: 5px;"
        )
        label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return label

    def setup_background_effects(self):
        """Setup subtle background effects for the panel."""
        # This can be used for internal panel-specific background effects if needed
        # For now, it mainly relies on the parent's transparent background and global theme.
        pass

    def _connect_signals(self):
        """Connect UI elements to config update logic and controller signals."""
        # Connect input fields to config update
        self.sharepoint_url_input.textChanged.connect(self._save_config_from_ui)
        self.sharepoint_site_combo.currentTextChanged.connect(self._save_config_from_ui)
        self.sharepoint_list_combo.currentTextChanged.connect(self._save_config_from_ui)
        self.db_type_combo.currentTextChanged.connect(self._save_config_from_ui)
        self.db_host_input.textChanged.connect(self._save_config_from_ui)
        self.db_port_spinbox.valueChanged.connect(self._save_config_from_ui)
        self.db_name_combo.currentTextChanged.connect(self._save_config_from_ui)
        self.db_table_combo.currentTextChanged.connect(self._save_config_from_ui)
        self.db_username_input.textChanged.connect(self._save_config_from_ui)
        self.db_password_input.textChanged.connect(self._save_config_from_ui)
        self.sync_interval_spinbox.valueChanged.connect(self._save_config_from_ui)
        self.batch_size_spinbox.valueChanged.connect(self._save_config_from_ui)
        self.log_level_combo.currentTextChanged.connect(self._save_config_from_ui)

        self.parallel_check.stateChanged.connect(self._save_config_from_ui)
        self.success_notif_check.stateChanged.connect(self._save_config_from_ui)
        self.error_notif_check.stateChanged.connect(self._save_config_from_ui)
        self.auto_sync_enable_check.stateChanged.connect(
            self.auto_sync_toggled
        )  # Emit specific signal for auto sync

        # Connect buttons to emit signals
        self.findChild(QPushButton, "Test SharePoint Connection").clicked.connect(
            self.test_sharepoint_requested
        )
        self.findChild(QPushButton, "Test Database Connection").clicked.connect(
            self.test_database_requested
        )
        self.refresh_sites_button.clicked.connect(self.refresh_sites_requested)
        self.refresh_lists_button.clicked.connect(self.refresh_lists_requested)
        self.refresh_databases_button.clicked.connect(self.refresh_databases_requested)
        self.refresh_tables_button.clicked.connect(self.refresh_tables_requested)

        # Manual Sync button (if present, otherwise connect to Dashboard's Run Sync)
        # This panel does not have a "Run Sync" button, it's on the dashboard.
        # But if you add one here, connect it to self.run_sync_requested.

    def _save_config_from_ui(self):
        """Save current UI values to config manager and emit config_changed signal."""
        try:
            self.config.sharepoint_url = self.sharepoint_url_input.text()
            self.config.sharepoint_site = self.sharepoint_site_combo.currentText()
            self.config.sharepoint_list = self.sharepoint_list_combo.currentText()
            self.config.db_type = self.db_type_combo.currentText()
            self.config.db_host = self.db_host_input.text()
            self.config.db_port = self.db_port_spinbox.value()
            self.config.db_name = self.db_name_combo.currentText()
            self.config.db_table = self.db_table_combo.currentText()
            self.config.db_username = self.db_username_input.text()
            self.config.db_password = (
                self.db_password_input.text()
            )  # Be careful with password handling
            self.config.sync_interval = self.sync_interval_spinbox.value()
            self.config.batch_size = self.batch_size_spinbox.value()
            self.config.log_level = self.log_level_combo.currentText()
            self.config.enable_parallel_processing = self.parallel_check.isChecked()
            self.config.enable_success_notifications = (
                self.success_notif_check.isChecked()
            )
            self.config.enable_error_notifications = self.error_notif_check.isChecked()
            self.config.auto_sync_enabled = self.auto_sync_enable_check.isChecked()

            self.config.save_config()
            self.config_changed.emit(self.config)  # Emit the updated config object
            logger.info("Configuration updated and saved.")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")

    def _load_config_to_ui(self):
        """Load configuration from config manager to UI elements."""
        try:
            self.config.load_config()  # Ensure config is loaded
            self.sharepoint_url_input.setText(self.config.sharepoint_url)
            self.sharepoint_site_combo.setCurrentText(self.config.sharepoint_site)
            self.sharepoint_list_combo.setCurrentText(self.config.sharepoint_list)
            self.db_type_combo.setCurrentText(self.config.db_type)
            self.db_host_input.setText(self.config.db_host)
            self.db_port_spinbox.setValue(self.config.db_port)
            self.db_name_combo.setCurrentText(self.config.db_name)
            self.db_table_combo.setCurrentText(self.config.db_table)
            self.db_username_input.setText(self.config.db_username)
            self.db_password_input.setText(self.config.db_password)
            self.sync_interval_spinbox.setValue(self.config.sync_interval)
            self.batch_size_spinbox.setValue(self.config.batch_size)
            self.log_level_combo.setCurrentText(self.config.log_level)
            self.parallel_check.setChecked(self.config.enable_parallel_processing)
            self.success_notif_check.setChecked(
                self.config.enable_success_notifications
            )
            self.error_notif_check.setChecked(self.config.enable_error_notifications)
            self.auto_sync_enable_check.setChecked(self.config.auto_sync_enabled)
            logger.info("Configuration loaded to UI.")
        except Exception as e:
            logger.error(f"Failed to load configuration to UI: {e}")

    @pyqtSlot(bool)
    def set_ui_enabled(self, enable: bool):
        """Enable or disable UI elements based on operation status."""
        # Example: Disable inputs during sync operation
        # This will need to iterate through relevant input widgets
        # For simplicity, disabling entire tab for now
        self.tab_widget.setEnabled(enable)
        self.refresh_sites_button.setEnabled(enable)
        self.refresh_lists_button.setEnabled(enable)
        self.refresh_databases_button.setEnabled(enable)
        self.refresh_tables_button.setEnabled(enable)
        self.findChild(QPushButton, "Test SharePoint Connection").setEnabled(enable)
        self.findChild(QPushButton, "Test Database Connection").setEnabled(enable)

    @pyqtSlot(list)
    def populate_sharepoint_sites(self, sites):
        self.sharepoint_site_combo.clear()
        self.sharepoint_site_combo.addItems(sites)
        if self.config.sharepoint_site in sites:
            self.sharepoint_site_combo.setCurrentText(self.config.sharepoint_site)
        self._save_config_from_ui()

    @pyqtSlot(list)
    def populate_sharepoint_lists(self, lists):
        self.sharepoint_list_combo.clear()
        self.sharepoint_list_combo.addItems(lists)
        if self.config.sharepoint_list in lists:
            self.sharepoint_list_combo.setCurrentText(self.config.sharepoint_list)
        self._save_config_from_ui()

    @pyqtSlot(list)
    def populate_database_names(self, db_names):
        self.db_name_combo.clear()
        self.db_name_combo.addItems(db_names)
        if self.config.db_name in db_names:
            self.db_name_combo.setCurrentText(self.config.db_name)
        self._save_config_from_ui()

    @pyqtSlot(list)
    def populate_database_tables(self, tables):
        self.db_table_combo.clear()
        self.db_table_combo.addItems(tables)
        if self.config.db_table in tables:
            self.db_table_combo.setCurrentText(self.config.db_table)
        self._save_config_from_ui()
