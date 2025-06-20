# ui/main_window.py - Fixed Main Window
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter, QMessageBox
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon, QCloseEvent, QKeySequence, QShortcut
import sys
import logging
from pathlib import Path

# Add project root to path for imports
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from ui.styles.theme import UltraModernColors
    from ui.components.dashboard import Dashboard
    from ui.components.config_panel import ConfigPanel
    from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity
    from utils.config_manager import get_config_manager
except ImportError as e:
    print(f"Import error in main_window.py: {e}")
    sys.exit(1)

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Main application window for the DENSO Neural Matrix.
    Integrates Dashboard and ConfigPanel with proper signal handling.
    """

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.config_manager = get_config_manager()
        self.cleanup_done = False

        # Initialize UI
        self._setup_window_properties()
        self._setup_ui()
        self._setup_shortcuts()
        self._connect_signals()

        logger.info("MainWindow initialized")

    def _setup_window_properties(self):
        """Setup basic window properties optimized for 900x500"""
        try:
            config = self.config_manager.get_config()
            self.setWindowTitle(config.app_name)
            # Optimized for 900x500 displays
            self.setGeometry(100, 100, 900, 500)
            self.setMinimumSize(900, 500)
            self.setMaximumSize(1200, 700)  # Prevent window from getting too large

            # Set window icon if available
            icon_path = project_root / "assets" / "icons" / "denso_logo.png"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
            else:
                logger.debug(f"Window icon not found: {icon_path}")

        except Exception as e:
            logger.error(f"Error setting up window properties: {e}")

    def _setup_ui(self):
        """Setup the main user interface layout"""
        try:
            # Create central widget
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)

            # Main layout
            main_layout = QHBoxLayout(self.central_widget)
            main_layout.setContentsMargins(5, 5, 5, 5)
            main_layout.setSpacing(5)

            # Create splitter for resizable panels
            self.splitter = QSplitter(Qt.Orientation.Horizontal)
            main_layout.addWidget(self.splitter)

            # Create UI components
            self.dashboard = Dashboard(self.controller)
            self.config_panel = ConfigPanel(self.controller)

            # Add components to splitter
            self.splitter.addWidget(self.dashboard)
            self.splitter.addWidget(self.config_panel)

            # Set initial splitter sizes (60% dashboard, 40% config)
            self.splitter.setSizes([720, 480])  # Based on 1200px width

            # Style the splitter
            self.splitter.setStyleSheet(
                f"""
                QSplitter::handle {{
                    background-color: {UltraModernColors.NEON_PURPLE};
                    width: 2px;
                    margin: 2px;
                    border-radius: 1px;
                }}
                QSplitter::handle:hover {{
                    background-color: {UltraModernColors.NEON_BLUE};
                }}
                QSplitter::handle:pressed {{
                    background-color: {UltraModernColors.NEON_GREEN};
                }}
            """
            )

            # Apply main window styling
            self.setStyleSheet(
                f"""
                QMainWindow {{
                    background-color: transparent;
                    color: {UltraModernColors.TEXT_PRIMARY};
                }}
            """
            )

            logger.debug("Main UI layout created successfully")

        except Exception as e:
            logger.error(f"Error setting up UI: {e}")
            raise

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        try:
            # F5 - Test connections
            self.shortcut_test = QShortcut(QKeySequence("F5"), self)
            self.shortcut_test.activated.connect(self.controller.test_all_connections)

            # Ctrl+R - Refresh/Test connections
            self.shortcut_refresh = QShortcut(QKeySequence("Ctrl+R"), self)
            self.shortcut_refresh.activated.connect(
                self.controller.test_all_connections
            )

            # Ctrl+S - Run sync
            self.shortcut_sync = QShortcut(QKeySequence("Ctrl+S"), self)
            self.shortcut_sync.activated.connect(
                lambda: self.controller.run_full_sync("spo_to_sql")
            )

            # Ctrl+Q - Quit
            self.shortcut_quit = QShortcut(QKeySequence("Ctrl+Q"), self)
            self.shortcut_quit.activated.connect(self.close)

            # Escape - Close
            self.shortcut_escape = QShortcut(QKeySequence("Escape"), self)
            self.shortcut_escape.activated.connect(self.close)

            logger.debug("Keyboard shortcuts setup completed")

        except Exception as e:
            logger.error(f"Error setting up shortcuts: {e}")

    def _connect_signals(self):
        """Connect signals between controller and UI components"""
        try:
            # Connect controller signals to dashboard
            self.controller.log_message.connect(
                self.dashboard.log_console.add_log_message
            )
            self.controller.progress_updated.connect(self.dashboard.update_progress)
            self.controller.current_task_update.connect(
                self.dashboard.update_current_task
            )
            self.controller.sync_completed.connect(self._handle_sync_completion)

            # Connect status update signals
            self.controller.sharepoint_status_update.connect(
                lambda status: self.dashboard.sp_status_card.set_status(status)
            )
            self.controller.database_status_update.connect(
                lambda status: self.dashboard.db_status_card.set_status(status)
            )
            self.controller.last_sync_status_update.connect(
                lambda status: self.dashboard.last_sync_status_card.set_status(status)
            )
            self.controller.auto_sync_status_update.connect(
                lambda status: self.dashboard.auto_sync_status_card.set_status(status)
            )

            # Connect UI interaction signals
            self.controller.ui_enable_request.connect(self.toggle_ui_interactivity)

            # Connect dashboard signals to controller
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

            # Connect config panel signals to controller
            self.config_panel.request_auto_sync_toggle.connect(
                self.controller.toggle_auto_sync
            )
            self.config_panel.request_update_config_setting.connect(
                self.controller.update_setting
            )

            logger.info("All signals connected successfully")

        except Exception as e:
            logger.error(f"Error connecting signals: {e}")
            raise

    @pyqtSlot(bool, str, dict)
    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.MEDIUM)
    def _handle_sync_completion(self, success: bool, message: str, stats: dict):
        """Handle sync completion with detailed statistics"""
        try:
            # Determine icon and title
            if success:
                icon = QMessageBox.Icon.Information
                title = "Sync Completed Successfully"
            else:
                icon = QMessageBox.Icon.Warning
                title = "Sync Failed"

            # Build detailed message
            detailed_message = f"{message}\n\n"
            detailed_message += f"📊 Sync Statistics:\n"
            detailed_message += f"• Total Records: {stats.get('total_records', 0)}\n"
            detailed_message += f"• Records Added: {stats.get('records_added', 0)}\n"
            detailed_message += (
                f"• Records Updated: {stats.get('records_updated', 0)}\n"
            )
            detailed_message += f"• Errors: {stats.get('errors', 0)}\n"
            detailed_message += (
                f"• Duration: {stats.get('duration_seconds', 0):.1f} seconds\n"
            )
            detailed_message += f"• Direction: {stats.get('sync_direction', 'Unknown')}"

            # Show message box
            msg_box = QMessageBox(self)
            msg_box.setIcon(icon)
            msg_box.setWindowTitle(title)
            msg_box.setText(f"<b>{message}</b>")
            msg_box.setDetailedText(detailed_message)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()

            logger.info(f"Sync completion handled: Success={success}")

        except Exception as e:
            logger.error(f"Error handling sync completion: {e}")

    @pyqtSlot(bool)
    def toggle_ui_interactivity(self, enable: bool):
        """Enable/disable UI elements during operations"""
        try:
            # Disable/enable main panels
            self.config_panel.setEnabled(enable)

            # Disable/enable specific dashboard buttons
            if hasattr(self.dashboard, "run_sync_button"):
                self.dashboard.run_sync_button.setEnabled(enable)
            if hasattr(self.dashboard, "test_connection_button"):
                self.dashboard.test_connection_button.setEnabled(enable)
            if hasattr(self.dashboard, "import_excel_button"):
                self.dashboard.import_excel_button.setEnabled(enable)
            if hasattr(self.dashboard, "clear_cache_button"):
                self.dashboard.clear_cache_button.setEnabled(enable)

            # Keep log console and clear logs button always enabled
            if hasattr(self.dashboard, "log_console"):
                self.dashboard.log_console.setEnabled(True)
            if hasattr(self.dashboard, "clear_logs_button"):
                self.dashboard.clear_logs_button.setEnabled(True)

            logger.debug(f"UI interactivity {'enabled' if enable else 'disabled'}")

        except Exception as e:
            logger.error(f"Error toggling UI interactivity: {e}")

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.HIGH)
    def closeEvent(self, event: QCloseEvent):
        """Handle window close event with confirmation"""
        try:
            # Show confirmation dialog
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "Are you sure you want to exit DENSO Neural Matrix?\n\nAny running operations will be stopped.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                logger.info("User confirmed application exit")
                self.cleanup()
                event.accept()
            else:
                logger.info("User cancelled application exit")
                event.ignore()

        except Exception as e:
            logger.error(f"Error in closeEvent: {e}")
            # If there's an error, just accept the close event
            event.accept()

    def cleanup(self):
        """Perform safe cleanup of UI components"""
        if self.cleanup_done:
            logger.debug("MainWindow cleanup already performed")
            return

        logger.info("Initiating MainWindow cleanup...")

        try:
            # Disconnect all signals to prevent crashes
            self._disconnect_signals()

            # Cleanup UI components
            if hasattr(self, "dashboard") and self.dashboard:
                self.dashboard.cleanup()
                self.dashboard.deleteLater()
                self.dashboard = None
                logger.debug("Dashboard cleaned up")

            if hasattr(self, "config_panel") and self.config_panel:
                self.config_panel.cleanup()
                self.config_panel.deleteLater()
                self.config_panel = None
                logger.debug("Config panel cleaned up")

            # Cleanup shortcuts
            if hasattr(self, "shortcut_test"):
                self.shortcut_test.deleteLater()
            if hasattr(self, "shortcut_refresh"):
                self.shortcut_refresh.deleteLater()
            if hasattr(self, "shortcut_sync"):
                self.shortcut_sync.deleteLater()
            if hasattr(self, "shortcut_quit"):
                self.shortcut_quit.deleteLater()
            if hasattr(self, "shortcut_escape"):
                self.shortcut_escape.deleteLater()

            # Cleanup layout components
            if hasattr(self, "splitter") and self.splitter:
                self.splitter.deleteLater()
                self.splitter = None

            if hasattr(self, "central_widget") and self.central_widget:
                self.central_widget.deleteLater()
                self.central_widget = None

            self.cleanup_done = True
            logger.info("MainWindow cleanup completed successfully")

        except Exception as e:
            logger.error(f"Error during MainWindow cleanup: {e}")
            self.cleanup_done = True  # Mark as done to prevent retry loops

    def _disconnect_signals(self):
        """Disconnect all signal connections"""
        try:
            # Disconnect controller signals
            signal_pairs = [
                (
                    self.controller.log_message,
                    self.dashboard.log_console.add_log_message,
                ),
                (self.controller.progress_updated, self.dashboard.update_progress),
                (
                    self.controller.current_task_update,
                    self.dashboard.update_current_task,
                ),
                (self.controller.sync_completed, self._handle_sync_completion),
                (self.controller.ui_enable_request, self.toggle_ui_interactivity),
                # Dashboard to controller
                (self.dashboard.run_sync_requested, self.controller.run_full_sync),
                (
                    self.dashboard.clear_cache_requested,
                    self.controller.run_cache_cleanup,
                ),
                (
                    self.dashboard.test_connections_requested,
                    self.controller.test_all_connections,
                ),
                (
                    self.dashboard.import_excel_requested,
                    self.controller.import_excel_data,
                ),
                # Config panel to controller
                (
                    self.config_panel.request_auto_sync_toggle,
                    self.controller.toggle_auto_sync,
                ),
                (
                    self.config_panel.request_update_config_setting,
                    self.controller.update_setting,
                ),
            ]

            for signal, slot in signal_pairs:
                try:
                    signal.disconnect(slot)
                except (TypeError, RuntimeError):
                    pass  # Signal not connected or already disconnected

            # Disconnect lambda connections (these need to be disconnected differently)
            try:
                self.controller.sharepoint_status_update.disconnect()
                self.controller.database_status_update.disconnect()
                self.controller.last_sync_status_update.disconnect()
                self.controller.auto_sync_status_update.disconnect()
            except (TypeError, RuntimeError):
                pass

            logger.debug("All signals disconnected successfully")

        except Exception as e:
            logger.warning(f"Error disconnecting signals: {e}")

    def keyPressEvent(self, event):
        """Handle additional key press events"""
        try:
            # Let shortcuts handle their events first
            super().keyPressEvent(event)

        except Exception as e:
            logger.error(f"Error in keyPressEvent: {e}")

    def resizeEvent(self, event):
        """Handle window resize events"""
        try:
            super().resizeEvent(event)

            # Maintain splitter proportions on resize for compact display
            if hasattr(self, "splitter") and self.splitter:
                total_width = self.width() - 6  # Account for compact margins
                dashboard_width = int(total_width * 0.6)
                config_width = int(total_width * 0.4)
                self.splitter.setSizes([dashboard_width, config_width])

        except Exception as e:
            logger.debug(f"Error in resizeEvent: {e}")
