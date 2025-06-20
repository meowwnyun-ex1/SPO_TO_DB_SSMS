# ui/components/dashboard.py - Enhanced Dashboard with Real-time Updates and Cleanup
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt6.QtGui import QFont
import logging
import sys
import os

# Add project root to path for absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(
    os.path.dirname(current_dir)
)  # Go up three levels to project root
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import components with fallbacks
try:
    from ui.widgets.status_card import ModernStatusCard
    from ui.widgets.cyber_log_console import CyberLogConsole
    from ui.widgets.holographic_progress_bar import HolographicProgressBar
    from ui.widgets.modern_button import ActionButton
    from ui.styles.theme import (
        UltraModernColors,
        get_modern_card_style,
        get_modern_checkbox_style,
        get_modern_groupbox_style,  # Ensure this is correctly imported
    )
    from ui.widgets.neon_groupbox import NeonGroupBox
    from controller.app_controller import AppController  # For type hinting
    from utils.error_handling import (
        handle_exceptions,
        ErrorCategory,
        ErrorSeverity,
        get_error_handler,
    )
    from utils.config_manager import ConfigManager  # For config access
except ImportError as e:
    print(
        f"CRITICAL IMPORT ERROR in dashboard.py: {e}. Ensure dependencies are installed."
    )
    sys.exit(1)


logger = logging.getLogger(__name__)


class Dashboard(QWidget):
    """
    The main dashboard panel displaying synchronization status, logs, and controls.
    """

    # Signals to communicate with AppController
    run_sync_requested = pyqtSignal(str)  # Direction: 'spo_to_sql' or 'sql_to_spo'
    clear_cache_requested = pyqtSignal()
    test_connections_requested = pyqtSignal()
    import_excel_requested = pyqtSignal(
        str, str, dict
    )  # filePath, tableName, columnMapping

    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.config_manager = ConfigManager()
        self.cleanup_done = False  # Flag to prevent multiple cleanup calls
        self._setup_ui()
        self._connect_signals()
        logger.info("Dashboard initialized.")

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.HIGH)
    def _setup_ui(self):
        """Sets up the layout and widgets for the dashboard."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # 1. Status Cards Section
        status_groupbox = NeonGroupBox("System Status")
        status_layout = QGridLayout(status_groupbox)
        status_layout.setContentsMargins(10, 30, 10, 10)
        status_layout.setSpacing(10)

        # Initialize status cards
        self.sp_status_card = ModernStatusCard("SharePoint Connection", "disconnected")
        self.db_status_card = ModernStatusCard("Database Connection", "disconnected")
        self.last_sync_status_card = ModernStatusCard("Last Sync Status", "never")
        self.auto_sync_status_card = ModernStatusCard(
            "Auto-Sync", False, is_boolean_status=True
        )

        status_layout.addWidget(self.sp_status_card, 0, 0)
        status_layout.addWidget(self.db_status_card, 0, 1)
        status_layout.addWidget(self.last_sync_status_card, 1, 0)
        status_layout.addWidget(self.auto_sync_status_card, 1, 1)

        status_groupbox.setLayout(status_layout)
        main_layout.addWidget(status_groupbox)

        # 2. Progress and Current Task Section
        progress_groupbox = NeonGroupBox("Current Operation")
        progress_layout = QVBoxLayout(progress_groupbox)
        progress_layout.setContentsMargins(10, 30, 10, 10)
        progress_layout.setSpacing(10)

        self.current_task_label = QLabel("Idle")
        self.current_task_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.current_task_label.setStyleSheet(f"color: {UltraModernColors.NEON_GREEN};")
        self.current_task_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.current_task_label)

        self.progress_bar = HolographicProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        progress_groupbox.setLayout(progress_layout)
        main_layout.addWidget(progress_groupbox)

        # 3. Action Buttons Section
        buttons_groupbox = NeonGroupBox("Actions")
        buttons_layout = QGridLayout(buttons_groupbox)
        buttons_layout.setContentsMargins(10, 30, 10, 10)
        buttons_layout.setSpacing(10)

        self.run_sync_button = ActionButton(
            "Run Sync (SPO to SQL)", "primary", "md", icon="🚀"
        )
        self.test_connection_button = ActionButton(
            "Test Connections", "secondary", "md", icon="🌐"
        )
        self.clear_cache_button = ActionButton(
            "Clear System Cache", "ghost", "md", icon="🧹"
        )
        self.clear_logs_button = ActionButton(
            "Clear Log Console", "danger", "md", icon="🗑️"
        )

        # Add Excel Import Button - placeholder action
        self.import_excel_button = ActionButton(
            "Import Excel to DB", "secondary", "md", icon="📊"
        )

        buttons_layout.addWidget(self.run_sync_button, 0, 0)
        buttons_layout.addWidget(self.test_connection_button, 0, 1)
        buttons_layout.addWidget(
            self.import_excel_button, 1, 0
        )  # New row for Excel import
        buttons_layout.addWidget(self.clear_cache_button, 1, 1)
        buttons_layout.addWidget(self.clear_logs_button, 2, 0, 1, 2)  # Span two columns

        buttons_groupbox.setLayout(buttons_layout)
        main_layout.addWidget(buttons_groupbox)

        # 4. Log Console Section
        log_groupbox = NeonGroupBox("System Logs")
        log_layout = QVBoxLayout(log_groupbox)
        log_layout.setContentsMargins(10, 30, 10, 10)
        log_layout.setSpacing(5)

        self.log_console = CyberLogConsole()
        self.log_console.setMinimumHeight(150)  # Ensure it's tall enough
        log_layout.addWidget(self.log_console)

        log_groupbox.setLayout(log_layout)
        main_layout.addWidget(log_groupbox)

        main_layout.addStretch(1)  # Pushes content to top

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.HIGH)
    def _connect_signals(self):
        """Connects UI elements to controller actions."""
        # Connect Dashboard buttons to AppController methods indirectly via signals
        self.run_sync_button.clicked.connect(self._on_run_sync_clicked)
        self.test_connection_button.clicked.connect(
            self.test_connections_requested.emit
        )
        self.clear_cache_button.clicked.connect(self.clear_cache_requested.emit)
        self.clear_logs_button.clicked.connect(self.log_console.clear)
        self.import_excel_button.clicked.connect(self._on_import_excel_clicked)

        # Connect AppController signals to Dashboard UI updates
        # These will be connected in MainWindow to bridge AppController to Dashboard instance
        logger.debug("Dashboard internal signals connected.")

    @pyqtSlot()
    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.MEDIUM)
    def _on_run_sync_clicked(self):
        """Handles the 'Run Sync' button click."""
        # For now, always trigger SharePoint to SQL sync.
        # Future: Add a dropdown to select sync direction.
        sync_direction = self.config_manager.get_setting(
            "sync_mode"
        )  # Use sync_mode from config
        if sync_direction == "full":  # Assuming "full" means spo_to_sql for now
            self.run_sync_requested.emit("spo_to_sql")
        else:  # Add other sync modes later
            self.run_sync_requested.emit("spo_to_sql")  # Default to SPO to SQL

    @pyqtSlot()
    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.MEDIUM)
    def _on_import_excel_clicked(self):
        """Handles the 'Import Excel' button click."""
        # This will open a file dialog and then trigger the import
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select Excel File for Import")
        file_dialog.setNameFilter("Excel Files (*.xlsx *.xls)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]
            logger.info(f"Selected Excel file: {selected_file}")

            # Placeholder for actual table name and column mapping.
            # These should ideally come from config or user input in ConfigPanel.
            target_table = self.config_manager.get_setting(
                "sql_table_name"
            )  # Example target
            # Example mapping: 'Excel Column Name': 'Database_Column_Name'
            # This needs to be dynamically configurable for a real app.
            column_mapping = self.config_manager.get_setting(
                "excel_import_mapping"
            )  # Assuming this config exists now

            if not column_mapping:
                self.log_console.add_log_message(
                    "Excel import mapping is not configured. Please set it in config.",
                    "error",
                )
                return

            self.import_excel_requested.emit(
                selected_file, target_table, column_mapping
            )

    @pyqtSlot(str, int, str)
    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.LOW)
    def update_progress(self, task_name: str, percentage: int, message: str):
        """Updates the progress bar and current task label."""
        self.current_task_label.setText(f"{task_name}: {message}")
        self.progress_bar.setValue(percentage)
        logger.debug(f"Dashboard Progress: {task_name} - {percentage}% - {message}")

    @pyqtSlot(str)
    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.LOW)
    def update_current_task(self, task_description: str):
        """Updates the current task description label."""
        self.current_task_label.setText(task_description)

    @pyqtSlot(str, str)
    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.LOW)
    def update_status(self, service_name: str, status: str):
        """Updates specific status cards."""
        if service_name == "SharePoint":
            self.sp_status_card.set_status(status)
        elif service_name == "Database":
            self.db_status_card.set_status(status)
        logger.debug(f"Dashboard Status Update: {service_name} to {status}")

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.CRITICAL)
    def cleanup(self):
        """Performs cleanup for the Dashboard."""
        if self.cleanup_done:
            logger.debug("Dashboard cleanup already performed, skipping.")
            return

        logger.info("Initiating Dashboard cleanup...")

        # Explicitly clean up widgets that might have timers/threads
        if hasattr(self, "log_console") and self.log_console:
            self.log_console.cleanup()
            self.log_console.deleteLater()
            self.log_console = None
            logger.debug("CyberLogConsole cleanup and deletion.")

        # Disconnect signals
        try:
            # Check if signals are connected before disconnecting to avoid TypeError
            if self.run_sync_button.receivers(self.run_sync_button.clicked) > 0:
                self.run_sync_button.clicked.disconnect(self._on_run_sync_clicked)
            if (
                self.test_connection_button.receivers(
                    self.test_connection_button.clicked
                )
                > 0
            ):
                self.test_connection_button.clicked.disconnect(
                    self.test_connections_requested.emit
                )
            if self.clear_cache_button.receivers(self.clear_cache_button.clicked) > 0:
                self.clear_cache_button.clicked.disconnect(
                    self.clear_cache_requested.emit
                )
            if self.clear_logs_button.receivers(self.clear_logs_button.clicked) > 0:
                # Disconnect log_console.clear only if log_console exists
                if (
                    self.log_console
                    and self.clear_logs_button.receivers(self.clear_logs_button.clicked)
                    > 0
                ):
                    try:
                        self.clear_logs_button.clicked.disconnect(
                            self.log_console.clear
                        )
                    except TypeError:  # Catch if it was already disconnected
                        pass
            if self.import_excel_button.receivers(self.import_excel_button.clicked) > 0:
                self.import_excel_button.clicked.disconnect(
                    self._on_import_excel_clicked
                )
            logger.info("Disconnected Dashboard signals.")
        except Exception as e:
            logger.warning(f"Error during Dashboard signal disconnection: {e}")

        # Mark other significant widgets for deletion
        if self.progress_bar:
            self.progress_bar.deleteLater()
            self.progress_bar = None
            logger.debug("HolographicProgressBar deleted.")
        if self.run_sync_button:
            self.run_sync_button.deleteLater()
            self.run_sync_button = None
        if self.clear_logs_button:
            self.clear_logs_button.deleteLater()
            self.clear_logs_button = None
        if self.clear_cache_button:
            self.clear_cache_button.deleteLater()
            self.clear_cache_button = None
        if self.test_connection_button:
            self.test_connection_button.deleteLater()
            self.test_connection_button = None
        if self.import_excel_button:
            self.import_excel_button.deleteLater()
            self.import_excel_button = None
        if self.current_task_label:
            self.current_task_label.deleteLater()
            self.current_task_label = None

        if hasattr(self, "sp_status_card") and self.sp_status_card:
            self.sp_status_card.deleteLater()
        if hasattr(self, "db_status_card") and self.db_status_card:
            self.db_status_card.deleteLater()
        if hasattr(self, "last_sync_status_card") and self.last_sync_status_card:
            self.last_sync_status_card.deleteLater()
        if hasattr(self, "auto_sync_status_card") and self.auto_sync_status_card:
            self.auto_sync_status_card.deleteLater()

        # Delete remaining child widgets
        for child in self.findChildren(QWidget):
            if child is not self:
                child.deleteLater()

        self.cleanup_done = True
        logger.info("Dashboard cleanup completed.")
