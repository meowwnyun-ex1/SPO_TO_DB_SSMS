# ui/main_window.py - Enhanced Main Application Window
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QSplitter,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSlot  # Corrected: QCloseEvent moved to QtGui
from PyQt6.QtGui import QIcon, QCloseEvent  # Corrected: QCloseEvent moved here
import sys
import os
import logging

# Ensure project root is in path for absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Attempt to import components with fallbacks for robustness
try:
    from ui.styles.theme import (
        UltraModernColors,
        apply_ultra_modern_theme,
        get_modern_button_style,
        get_modern_input_style,
    )
    from ui.components.dashboard import Dashboard
    from ui.components.config_panel import ConfigPanel
    from utils.logger import NeuraUILogHandler
    from utils.error_handling import (
        handle_exceptions,
        ErrorCategory,
        ErrorSeverity,
        get_error_handler,
    )
    from controller.app_controller import AppController  # For type hinting
    from utils.config_manager import ConfigManager  # For config access
except ImportError as e:
    print(
        f"CRITICAL IMPORT ERROR in main_window.py: {e}. Ensure dependencies are installed."
    )
    # Fallback/exit strategy if core UI components can't be loaded
    sys.exit(1)


logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Main application window for the DENSO Neural Matrix.
    Integrates Dashboard and ConfigPanel, and handles global UI interactions.
    """

    def __init__(self, controller: AppController, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.config_manager = ConfigManager()
        self.cleanup_done = False  # Flag to prevent multiple cleanups

        self.setWindowTitle(self.config_manager.get_setting("app_name"))
        self.setGeometry(100, 100, 1200, 800)  # Initial window size
        self.setMinimumSize(900, 600)  # Minimum size to maintain usability

        # Set window icon
        icon_path = os.path.join(project_root, "assets/icons/denso_logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            logger.warning(f"Application icon not found: {icon_path}")

        self._setup_ui()
        self._connect_signals()
        logger.info("MainWindow initialized.")

    def _setup_ui(self):
        """Sets up the main user interface layout."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(
            0, 0, 0, 0
        )  # Remove margins around the central widget
        main_layout.setSpacing(0)  # Remove spacing between widgets in the main layout

        # Create a splitter to allow resizing of panels
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        # Left Panel (Dashboard)
        self.dashboard = Dashboard(self.controller)
        self.dashboard.setMinimumWidth(500)  # Ensure dashboard has enough space
        self.splitter.addWidget(self.dashboard)

        # Right Panel (ConfigPanel)
        self.config_panel = ConfigPanel(self.controller)
        self.config_panel.setMinimumWidth(350)
        self.splitter.addWidget(self.config_panel)

        # Set initial sizes for the splitter sections
        self.splitter.setSizes([self.width() * 0.6, self.width() * 0.4])

        # Apply general main window styling (if not handled by main.py's background)
        # This is for other QMainWindow elements like title bar, etc.
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background-color: transparent; /* Background image is handled by main.py */
                color: {UltraModernColors.TEXT_PRIMARY};
            }}
            QSplitter::handle {{
                background-color: {UltraModernColors.NEON_PURPLE};
                width: 2px;
            }}
            QSplitter::handle:hover {{
                background-color: {UltraModernColors.NEON_BLUE};
            }}
        """
        )

    def _connect_signals(self):
        """Connects signals from controller to UI elements."""
        try:
            self.controller.log_message.connect(
                self.dashboard.log_console.add_log_message
            )
            self.controller.status_changed.connect(self.dashboard.update_status)
            self.controller.progress_updated.connect(self.dashboard.update_progress)
            self.controller.current_task_update.connect(
                self.dashboard.update_current_task
            )
            self.controller.sync_completed.connect(self._handle_sync_completion)

            # Connect signals for config panel updates
            self.controller.sharepoint_sites_updated.connect(
                self.config_panel.update_sharepoint_sites
            )
            self.controller.sharepoint_lists_updated.connect(
                self.config_panel.update_sharepoint_lists
            )
            self.controller.database_names_updated.connect(
                self.config_panel.update_database_names
            )
            self.controller.database_tables_updated.connect(
                self.config_panel.update_database_tables
            )

            # Signals for connection statuses
            self.controller.sharepoint_status_update.connect(
                lambda s: self.dashboard.sp_status_card.set_status(s)
            )
            self.controller.database_status_update.connect(
                lambda s: self.dashboard.db_status_card.set_status(s)
            )
            self.controller.last_sync_status_update.connect(
                lambda s: self.dashboard.last_sync_status_card.set_status(s)
            )
            self.controller.auto_sync_status_update.connect(
                lambda s: self.dashboard.auto_sync_status_card.set_status(s)
            )
            self.controller.ui_enable_request.connect(self.toggle_ui_interactivity)

            # Connect ConfigPanel signals to AppController slots
            self.config_panel.request_auto_sync_toggle.connect(
                self.controller.toggle_auto_sync
            )
            self.config_panel.request_update_config_setting.connect(
                self.controller.update_setting
            )

            # Connect Dashboard signals to AppController slots
            self.dashboard.run_sync_requested.connect(self.controller.run_full_sync)
            self.dashboard.clear_cache_requested.connect(
                self.controller.run_cache_cleanup
            )
            self.dashboard.test_connections_requested.connect(
                self.controller.test_all_connections
            )
            self.dashboard.import_excel_requested.connect(
                self.controller.import_excel_data
            )

            logger.info("MainWindow signals connected.")
        except Exception as e:
            logger.error(f"Error connecting signals in MainWindow: {e}", exc_info=True)
            get_error_handler().handle_error(
                ErrorCategory.UI,
                ErrorSeverity.HIGH,
                f"Failed to connect UI signals: {e}",
            )

    @pyqtSlot(bool, str, dict)
    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.MEDIUM)
    def _handle_sync_completion(self, success: bool, message: str, stats: dict):
        """Handles the completion of a synchronization process."""
        icon = QMessageBox.Icon.Information if success else QMessageBox.Icon.Warning
        title = "Sync Complete" if success else "Sync Failed"
        detailed_message = message + "\n\n"
        detailed_message += (
            f"Total Records Processed: {stats.get('total_records', 0)}\n"
        )
        detailed_message += f"Records Added: {stats.get('records_added', 0)}\n"
        detailed_message += f"Records Updated: {stats.get('records_updated', 0)}\n"
        detailed_message += f"Errors: {stats.get('errors', 0)}\n"

        QMessageBox.information(
            self, title, detailed_message, QMessageBox.StandardButton.Ok, icon
        )
        logger.info(f"Sync completion handled. Success: {success}, Message: {message}")

        # Update last sync status based on overall success
        if success:
            self.dashboard.last_sync_status_card.set_status("success")
        else:
            self.dashboard.last_sync_status_card.set_status(
                "failed"
            )  # Changed from "error" to "failed" for clarity

    @pyqtSlot(bool)
    def toggle_ui_interactivity(self, enable: bool):
        """Enables/disables UI elements based on background process status."""
        logger.info(f"UI interactivity {'enabled' if enable else 'disabled'}.")
        # Disable main controls while sync is running
        self.config_panel.setEnabled(enable)
        self.dashboard.run_sync_button.setEnabled(enable)
        self.dashboard.clear_logs_button.setEnabled(enable)
        self.dashboard.clear_cache_button.setEnabled(enable)
        self.dashboard.test_connection_button.setEnabled(
            enable
        )  # Also disable test connection
        self.dashboard.import_excel_button.setEnabled(
            enable
        )  # Disable import excel button
        # You might want to keep the log console enabled
        self.dashboard.log_console.setReadOnly(not enable)

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.HIGH)
    def closeEvent(self, event: QCloseEvent):
        """Overrides the close event to provide cleanup and confirmation."""
        logger.info("MainWindow close event triggered.")
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to exit the DENSO Neural Matrix application?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.cleanup()  # Perform explicit cleanup before accepting close
            event.accept()
        else:
            event.ignore()

    def cleanup(self):
        """
        Performs safe cleanup of child widgets and disconnects signals to prevent crashes.
        """
        if self.cleanup_done:
            logger.debug("MainWindow cleanup already performed, skipping.")
            return

        logger.info("Initiating MainWindow safe cleanup...")
        try:
            # Disconnect controller signals from UI elements
            try:
                self.controller.log_message.disconnect(
                    self.dashboard.log_console.add_log_message
                )
                self.controller.status_changed.disconnect(self.dashboard.update_status)
                self.controller.progress_updated.disconnect(
                    self.dashboard.update_progress
                )
                self.controller.current_task_update.disconnect(
                    self.dashboard.update_current_task
                )
                self.controller.sync_completed.disconnect(self._handle_sync_completion)

                self.controller.sharepoint_sites_updated.disconnect(
                    self.config_panel.update_sharepoint_sites
                )
                self.controller.sharepoint_lists_updated.disconnect(
                    self.config_panel.update_sharepoint_lists
                )
                self.controller.database_names_updated.disconnect(
                    self.config_panel.update_database_names
                )
                self.controller.database_tables_updated.disconnect(
                    self.config_panel.update_database_tables
                )

                # Disconnect connections made with lambdas or direct slots
                self.controller.sharepoint_status_update.disconnect(
                    self.dashboard.sp_status_card.set_status
                )
                self.controller.database_status_update.disconnect(
                    self.dashboard.db_status_card.set_status
                )
                self.controller.last_sync_status_update.disconnect(
                    self.dashboard.last_sync_status_card.set_status
                )
                self.controller.auto_sync_status_update.disconnect(
                    self.dashboard.auto_sync_status_card.set_status
                )
                self.controller.ui_enable_request.disconnect(
                    self.toggle_ui_interactivity
                )

                # Disconnect ConfigPanel signals from AppController slots
                self.config_panel.request_auto_sync_toggle.disconnect(
                    self.controller.toggle_auto_sync
                )
                self.config_panel.request_update_config_setting.disconnect(
                    self.controller.update_setting
                )

                # Disconnect Dashboard signals from AppController slots
                self.dashboard.run_sync_requested.disconnect(
                    self.controller.run_full_sync
                )
                self.dashboard.clear_cache_requested.disconnect(
                    self.controller.run_cache_cleanup
                )
                self.dashboard.test_connections_requested.disconnect(
                    self.controller.test_all_connections
                )
                self.dashboard.import_excel_requested.disconnect(
                    self.controller.import_excel_data
                )

                logger.info(
                    "Disconnected MainWindow-specific signals from controller and UI components."
                )
            except TypeError as e:
                logger.debug(
                    f"Attempted to disconnect non-connected signal in MainWindow cleanup: {e}"
                )
            except Exception as e:
                logger.warning(f"Error during MainWindow signal disconnection: {e}")

            # Explicitly clean up child widgets to avoid segfaults
            if self.dashboard:
                self.dashboard.cleanup()
                self.dashboard.deleteLater()
                self.dashboard = None
                logger.info("Dashboard cleaned up.")

            if self.config_panel:
                self.config_panel.cleanup()
                self.config_panel.deleteLater()
                self.config_panel = None
                logger.info("ConfigPanel cleaned up.")

            if self.splitter:
                # The splitter takes ownership of its widgets, so deleting widgets inside is often enough
                # But explicit deleteLater on splitter itself ensures it's removed from layout
                self.splitter.deleteLater()
                self.splitter = None
                logger.info("Splitter cleaned up.")

            if self.central_widget:
                self.central_widget.deleteLater()
                self.central_widget = None
                logger.info("Central widget cleaned up.")

            self.cleanup_done = True
            logger.info("MainWindow safe cleanup completed.")

        except Exception as e:
            logger.critical(
                f"Critical error during MainWindow cleanup: {e}", exc_info=True
            )
            self.cleanup_done = True

    def keyPressEvent(self, event):
        """Handles global keyboard shortcuts."""
        try:
            if event.key() == Qt.Key.Key_Escape:
                self.close()
            elif event.key() == Qt.Key.Key_F5 and self.controller:
                self.controller.run_full_sync()
            elif event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                if event.key() == Qt.Key.Key_Q:
                    self.close()
                elif event.key() == Qt.Key.Key_R and self.controller:
                    self.controller.test_all_connections()
            else:
                super().keyPressEvent(event)
        except Exception as e:
            logger.error(f"Error in keyPressEvent: {e}", exc_info=True)
            get_error_handler().handle_error(
                ErrorCategory.UI, ErrorSeverity.MEDIUM, f"Keyboard event error: {e}"
            )
