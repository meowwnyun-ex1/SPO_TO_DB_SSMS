# ui/components/dashboard.py - Fixed Dashboard Component
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QFileDialog, QMessageBox
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt6.QtGui import QFont
import logging
import sys
from pathlib import Path

# Add project root to path for imports
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from ui.widgets.status_card import ModernStatusCard
    from ui.widgets.cyber_log_console import CyberLogConsole
    from ui.widgets.holographic_progress_bar import HolographicProgressBar
    from ui.widgets.modern_button import ActionButton
    from ui.styles.theme import UltraModernColors
    from ui.widgets.neon_groupbox import NeonGroupBox
    from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity
    from utils.config_manager import get_config_manager
except ImportError as e:
    print(f"Import error in dashboard.py: {e}")
    sys.exit(1)

logger = logging.getLogger(__name__)


class Dashboard(QWidget):
    """
    Main dashboard panel displaying synchronization status, logs, and controls.
    """

    # Signals to communicate with AppController
    run_sync_requested = pyqtSignal(str)  # Direction: 'spo_to_sql' or 'sql_to_spo'
    clear_cache_requested = pyqtSignal()
    test_connections_requested = pyqtSignal()
    import_excel_requested = pyqtSignal(
        str, str, dict
    )  # filePath, tableName, columnMapping

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.config_manager = get_config_manager()
        self.cleanup_done = False

        self._setup_ui()
        self._connect_signals()

        logger.info("Dashboard initialized")

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.HIGH)
    def _setup_ui(self):
        """Setup the layout and widgets for the dashboard"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # 1. Status Cards Section
        self._create_status_section(main_layout)

        # 2. Progress Section
        self._create_progress_section(main_layout)

        # 3. Action Buttons Section
        self._create_actions_section(main_layout)

        # 4. Log Console Section
        self._create_log_section(main_layout)

        main_layout.addStretch(1)  # Push content to top

    def _create_status_section(self, main_layout):
        """Create status cards section"""
        status_groupbox = NeonGroupBox("System Status")
        status_layout = QGridLayout()
        status_layout.setContentsMargins(10, 30, 10, 10)
        status_layout.setSpacing(10)

        # Initialize status cards
        self.sp_status_card = ModernStatusCard("SharePoint Connection", "disconnected")
        self.db_status_card = ModernStatusCard("Database Connection", "disconnected")
        self.last_sync_status_card = ModernStatusCard("Last Sync Status", "never")
        self.auto_sync_status_card = ModernStatusCard(
            "Auto-Sync", False, is_boolean_status=True
        )

        # Add to grid layout
        status_layout.addWidget(self.sp_status_card, 0, 0)
        status_layout.addWidget(self.db_status_card, 0, 1)
        status_layout.addWidget(self.last_sync_status_card, 1, 0)
        status_layout.addWidget(self.auto_sync_status_card, 1, 1)

        status_groupbox.setLayout(status_layout)
        main_layout.addWidget(status_groupbox)

    def _create_progress_section(self, main_layout):
        """Create progress and current task section"""
        progress_groupbox = NeonGroupBox("Current Operation")
        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(10, 30, 10, 10)
        progress_layout.setSpacing(10)

        # Current task label
        self.current_task_label = QLabel("Idle")
        self.current_task_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.current_task_label.setStyleSheet(f"color: {UltraModernColors.NEON_GREEN};")
        self.current_task_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.current_task_label)

        # Progress bar
        self.progress_bar = HolographicProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        progress_groupbox.setLayout(progress_layout)
        main_layout.addWidget(progress_groupbox)

    def _create_actions_section(self, main_layout):
        """Create action buttons section"""
        buttons_groupbox = NeonGroupBox("Actions")
        buttons_layout = QGridLayout()
        buttons_layout.setContentsMargins(10, 30, 10, 10)
        buttons_layout.setSpacing(10)

        # Create action buttons
        self.run_sync_button = ActionButton(
            "Run Sync (SPO → SQL)", "primary", "md", icon="🚀"
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
        self.import_excel_button = ActionButton(
            "Import Excel to DB", "secondary", "md", icon="📊"
        )

        # Add buttons to grid
        buttons_layout.addWidget(self.run_sync_button, 0, 0)
        buttons_layout.addWidget(self.test_connection_button, 0, 1)
        buttons_layout.addWidget(self.import_excel_button, 1, 0)
        buttons_layout.addWidget(self.clear_cache_button, 1, 1)
        buttons_layout.addWidget(self.clear_logs_button, 2, 0, 1, 2)  # Span two columns

        buttons_groupbox.setLayout(buttons_layout)
        main_layout.addWidget(buttons_groupbox)

    def _create_log_section(self, main_layout):
        """Create log console section"""
        log_groupbox = NeonGroupBox("System Logs")
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(10, 30, 10, 10)
        log_layout.setSpacing(5)

        self.log_console = CyberLogConsole()
        self.log_console.setMinimumHeight(150)
        log_layout.addWidget(self.log_console)

        log_groupbox.setLayout(log_layout)
        main_layout.addWidget(log_groupbox)

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.HIGH)
    def _connect_signals(self):
        """Connect UI elements to controller actions"""
        try:
            # Connect button signals
            self.run_sync_button.clicked.connect(self._on_run_sync_clicked)
            self.test_connection_button.clicked.connect(
                self.test_connections_requested.emit
            )
            self.clear_cache_button.clicked.connect(self.clear_cache_requested.emit)
            self.clear_logs_button.clicked.connect(self.log_console.clear)
            self.import_excel_button.clicked.connect(self._on_import_excel_clicked)

            logger.debug("Dashboard signals connected successfully")

        except Exception as e:
            logger.error(f"Error connecting dashboard signals: {e}")

    @pyqtSlot()
    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.MEDIUM)
    def _on_run_sync_clicked(self):
        """Handle Run Sync button click"""
        try:
            # Get sync direction from config
            config = self.config_manager.get_config()
            sync_direction = getattr(config, "auto_sync_direction", "spo_to_sql")

            # Emit signal to request sync
            self.run_sync_requested.emit(sync_direction)
            logger.info(f"Sync requested: {sync_direction}")

        except Exception as e:
            logger.error(f"Error handling sync button click: {e}")

    @pyqtSlot()
    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.MEDIUM)
    def _on_import_excel_clicked(self):
        """Handle Import Excel button click"""
        try:
            # Open file dialog
            file_dialog = QFileDialog(self)
            file_dialog.setWindowTitle("Select Excel File for Import")
            file_dialog.setNameFilter("Excel Files (*.xlsx *.xls)")
            file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

            if file_dialog.exec():
                selected_files = file_dialog.selectedFiles()
                if selected_files:
                    selected_file = selected_files[0]
                    logger.info(f"Selected Excel file: {selected_file}")

                    # Get target table and mapping from config
                    config = self.config_manager.get_config()
                    target_table = getattr(config, "sql_table_name", "imported_data")
                    column_mapping = getattr(config, "excel_import_mapping", {})

                    if not column_mapping:
                        # Show warning about missing mapping
                        QMessageBox.warning(
                            self,
                            "Missing Configuration",
                            "Excel import mapping is not configured.\n"
                            "Please set up column mapping in the Configuration panel.",
                            QMessageBox.StandardButton.Ok,
                        )
                        return

                    # Emit signal to request import
                    self.import_excel_requested.emit(
                        selected_file, target_table, column_mapping
                    )
                    logger.info(
                        f"Excel import requested: {selected_file} → {target_table}"
                    )

        except Exception as e:
            logger.error(f"Error handling Excel import: {e}")
            QMessageBox.critical(
                self,
                "Import Error",
                f"Failed to start Excel import:\n{e}",
                QMessageBox.StandardButton.Ok,
            )

    @pyqtSlot(str, int, str)
    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.LOW)
    def update_progress(self, task_name: str, percentage: int, message: str):
        """Update progress bar and current task label"""
        try:
            self.current_task_label.setText(f"{task_name}: {message}")
            self.progress_bar.setValue(max(0, min(100, percentage)))  # Clamp to 0-100
            logger.debug(f"Progress updated: {task_name} - {percentage}% - {message}")

        except Exception as e:
            logger.debug(f"Error updating progress: {e}")

    @pyqtSlot(str)
    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.LOW)
    def update_current_task(self, task_description: str):
        """Update current task description label"""
        try:
            self.current_task_label.setText(task_description)
            logger.debug(f"Task updated: {task_description}")

        except Exception as e:
            logger.debug(f"Error updating current task: {e}")

    @pyqtSlot(str, str)
    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.LOW)
    def update_status(self, service_name: str, status: str):
        """Update specific status cards"""
        try:
            if service_name == "SharePoint" and hasattr(self, "sp_status_card"):
                self.sp_status_card.set_status(status)
            elif service_name == "Database" and hasattr(self, "db_status_card"):
                self.db_status_card.set_status(status)

            logger.debug(f"Status updated: {service_name} → {status}")

        except Exception as e:
            logger.debug(f"Error updating status: {e}")

    def cleanup(self):
        """Perform cleanup for the Dashboard"""
        if self.cleanup_done:
            logger.debug("Dashboard cleanup already performed")
            return

        logger.info("Initiating Dashboard cleanup...")

        try:
            # Clean up log console first (it may have timers)
            if hasattr(self, "log_console") and self.log_console:
                self.log_console.cleanup()
                self.log_console.deleteLater()
                self.log_console = None
                logger.debug("Log console cleaned up")

            # Disconnect button signals
            button_signal_pairs = [
                (self.run_sync_button, self._on_run_sync_clicked),
                (self.test_connection_button, self.test_connections_requested.emit),
                (self.clear_cache_button, self.clear_cache_requested.emit),
                (self.import_excel_button, self._on_import_excel_clicked),
            ]

            for button, slot in button_signal_pairs:
                try:
                    if hasattr(button, "clicked"):
                        button.clicked.disconnect(slot)
                except (TypeError, RuntimeError):
                    pass  # Signal not connected

            # Special handling for clear logs button
            try:
                if hasattr(self, "clear_logs_button") and hasattr(self, "log_console"):
                    if self.log_console:  # Only disconnect if log_console still exists
                        self.clear_logs_button.clicked.disconnect(
                            self.log_console.clear
                        )
            except (TypeError, RuntimeError):
                pass

            # Clean up status cards
            status_cards = [
                "sp_status_card",
                "db_status_card",
                "last_sync_status_card",
                "auto_sync_status_card",
            ]

            for card_name in status_cards:
                if hasattr(self, card_name):
                    card = getattr(self, card_name)
                    if card:
                        # Clean up any animations in status cards
                        if hasattr(card, "cleanup_animations"):
                            card.cleanup_animations()
                        card.deleteLater()
                        setattr(self, card_name, None)

            # Clean up other widgets
            widgets_to_cleanup = [
                "progress_bar",
                "current_task_label",
                "run_sync_button",
                "test_connection_button",
                "clear_cache_button",
                "clear_logs_button",
                "import_excel_button",
            ]

            for widget_name in widgets_to_cleanup:
                if hasattr(self, widget_name):
                    widget = getattr(self, widget_name)
                    if widget:
                        widget.deleteLater()
                        setattr(self, widget_name, None)

            # Clean up remaining child widgets
            for child in self.findChildren(QWidget):
                if child and child != self:
                    child.deleteLater()

            self.cleanup_done = True
            logger.info("Dashboard cleanup completed successfully")

        except Exception as e:
            logger.error(f"Error during Dashboard cleanup: {e}")
            self.cleanup_done = True  # Mark as done to prevent retry loops
