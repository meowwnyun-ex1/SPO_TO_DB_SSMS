# ui/main_window.py - Optimized Main Window with Navigation
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtCore import pyqtSlot
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
    from ui.styles.theme import UltraModernColors, CompactScaling
    from ui.widgets.navigation_bar import CompactNavigationBar, NavigationStack
    from ui.components.dashboard import Dashboard
    from ui.components.config_panel import ConfigPanel
    from ui.widgets.cyber_log_console import CyberLogConsole
    from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity
    from utils.config_manager import get_config_manager
except ImportError as e:
    print(f"Import error in main_window.py: {e}")
    sys.exit(1)

logger = logging.getLogger(__name__)


class CompactSyncPanel(QWidget):
    """Compact sync operations panel"""

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # Import existing dashboard functionality but in compact form
        from ui.widgets.modern_button import ActionButton
        from ui.widgets.holographic_progress_bar import HolographicProgressBar
        from ui.widgets.neon_groupbox import NeonGroupBox

        # Quick Actions Group
        actions_group = NeonGroupBox("Quick Actions")
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(4)

        # Compact buttons
        self.sync_button = ActionButton("🚀 Run Sync", "primary", "sm")
        self.test_button = ActionButton("🌐 Test Connection", "secondary", "sm")
        self.import_button = ActionButton("📊 Import Excel", "ghost", "sm")

        actions_layout.addWidget(self.sync_button)
        actions_layout.addWidget(self.test_button)
        actions_layout.addWidget(self.import_button)
        actions_group.setLayout(actions_layout)

        # Progress Group
        progress_group = NeonGroupBox("Progress")
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(4)

        self.progress_bar = HolographicProgressBar()
        self.progress_bar.setMaximumHeight(16)
        progress_layout.addWidget(self.progress_bar)
        progress_group.setLayout(progress_layout)

        layout.addWidget(actions_group)
        layout.addWidget(progress_group)
        layout.addStretch(1)

    def cleanup(self):
        """Cleanup for sync panel"""
        pass


class CompactLogPanel(QWidget):
    """Compact log viewing panel"""

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Log console takes full space
        self.log_console = CyberLogConsole()
        layout.addWidget(self.log_console)

        # Compact controls
        from ui.widgets.modern_button import ModernButton
        from PyQt6.QtWidgets import QHBoxLayout

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(4)

        self.clear_button = ModernButton("Clear", "danger", "sm", "🗑️")
        self.export_button = ModernButton("Export", "ghost", "sm", "💾")

        controls_layout.addWidget(self.clear_button)
        controls_layout.addWidget(self.export_button)
        controls_layout.addStretch(1)

        layout.addLayout(controls_layout)

        # Connect signals
        self.clear_button.clicked.connect(self.log_console.clear)

    def cleanup(self):
        """Cleanup for log panel"""
        if hasattr(self, "log_console"):
            self.log_console.cleanup()


class OptimizedMainWindow(QMainWindow):
    """
    Optimized main window for 900x500 displays using navigation bar
    instead of splitter layout for better space utilization.
    """

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.config_manager = get_config_manager()
        self.cleanup_done = False

        # Initialize UI components
        self.navigation_bar = None
        self.navigation_stack = None
        self.dashboard = None
        self.config_panel = None
        self.sync_panel = None
        self.log_panel = None

        # Initialize UI
        self._setup_window_properties()
        self._setup_ui()
        self._setup_shortcuts()
        self._connect_signals()

        logger.info("OptimizedMainWindow initialized")

    def _setup_window_properties(self):
        """Setup window properties optimized for 900x500"""
        try:
            config = self.config_manager.get_config()
            self.setWindowTitle(f"{config.app_name} - Compact Mode")

            # Exact 900x500 sizing
            self.setGeometry(100, 100, 900, 500)
            self.setMinimumSize(900, 500)
            self.setMaximumSize(900, 500)  # Lock to specific size

            # Set window icon if available
            icon_path = project_root / "assets" / "icons" / "denso_logo.png"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))

        except Exception as e:
            logger.error(f"Error setting up window properties: {e}")

    def _setup_ui(self):
        """Setup the optimized UI layout"""
        try:
            # Create central widget
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)

            # Main layout - vertical with navigation at top
            main_layout = QVBoxLayout(self.central_widget)
            main_layout.setContentsMargins(2, 2, 2, 2)
            main_layout.setSpacing(2)

            # Create navigation bar
            self.navigation_bar = CompactNavigationBar()
            main_layout.addWidget(self.navigation_bar)

            # Create navigation stack for content
            self.navigation_stack = NavigationStack()
            main_layout.addWidget(self.navigation_stack)

            # Create content panels
            self._create_content_panels()

            # Apply main window styling
            self.setStyleSheet(
                f"""
                QMainWindow {{
                    background-color: {UltraModernColors.GLASS_BG_DARK};
                    color: {UltraModernColors.TEXT_PRIMARY};
                }}
            """
            )

            logger.debug("Optimized UI layout created successfully")

        except Exception as e:
            logger.error(f"Error setting up UI: {e}")
            raise

    def _create_content_panels(self):
        """Create and add content panels to navigation stack"""
        try:
            # Create panels
            self.dashboard = Dashboard(self.controller)
            self.sync_panel = CompactSyncPanel(self.controller)
            self.config_panel = ConfigPanel(self.controller)
            self.log_panel = CompactLogPanel(self.controller)

            # Add panels to stack
            self.navigation_stack.add_panel("dashboard", self.dashboard)
            self.navigation_stack.add_panel("sync", self.sync_panel)
            self.navigation_stack.add_panel("config", self.config_panel)
            self.navigation_stack.add_panel("logs", self.log_panel)

            # Show dashboard by default
            self.navigation_stack.show_panel("dashboard")

            logger.debug("Content panels created and added to stack")

        except Exception as e:
            logger.error(f"Error creating content panels: {e}")
            raise

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        try:
            # F1-F4 for quick navigation
            self.shortcut_f1 = QShortcut(QKeySequence("F1"), self)
            self.shortcut_f1.activated.connect(lambda: self._navigate_to("dashboard"))

            self.shortcut_f2 = QShortcut(QKeySequence("F2"), self)
            self.shortcut_f2.activated.connect(lambda: self._navigate_to("sync"))

            self.shortcut_f3 = QShortcut(QKeySequence("F3"), self)
            self.shortcut_f3.activated.connect(lambda: self._navigate_to("config"))

            self.shortcut_f4 = QShortcut(QKeySequence("F4"), self)
            self.shortcut_f4.activated.connect(lambda: self._navigate_to("logs"))

            # Other shortcuts
            self.shortcut_test = QShortcut(QKeySequence("F5"), self)
            self.shortcut_test.activated.connect(self.controller.test_all_connections)

            self.shortcut_sync = QShortcut(QKeySequence("Ctrl+R"), self)
            self.shortcut_sync.activated.connect(
                lambda: self.controller.run_full_sync("spo_to_sql")
            )

            self.shortcut_quit = QShortcut(QKeySequence("Ctrl+Q"), self)
            self.shortcut_quit.activated.connect(self.close)

            self.shortcut_escape = QShortcut(QKeySequence("Escape"), self)
            self.shortcut_escape.activated.connect(self.close)

            logger.debug("Keyboard shortcuts setup completed")

        except Exception as e:
            logger.error(f"Error setting up shortcuts: {e}")

    def _connect_signals(self):
        """Connect signals between controller and UI components"""
        try:
            # Connect navigation
            self.navigation_bar.navigation_changed.connect(self._on_navigation_changed)

            # Connect controller signals to dashboard/panels
            self.controller.log_message.connect(
                self.log_panel.log_console.add_log_message
            )
            self.controller.progress_updated.connect(self._update_progress)
            self.controller.current_task_update.connect(self._update_current_task)
            self.controller.sync_completed.connect(self._handle_sync_completion)

            # Connect status update signals
            self.controller.sharepoint_status_update.connect(
                lambda status: self._update_connection_status("SharePoint", status)
            )
            self.controller.database_status_update.connect(
                lambda status: self._update_connection_status("Database", status)
            )
            self.controller.last_sync_status_update.connect(self._update_sync_status)
            self.controller.auto_sync_status_update.connect(
                self._update_auto_sync_status
            )

            # Connect UI interaction signals
            self.controller.ui_enable_request.connect(self.toggle_ui_interactivity)

            # Connect dashboard signals to controller (if dashboard has them)
            if hasattr(self.dashboard, "run_sync_requested"):
                self.dashboard.run_sync_requested.connect(self.controller.run_full_sync)
            if hasattr(self.dashboard, "clear_cache_requested"):
                self.dashboard.clear_cache_requested.connect(
                    self.controller.run_cache_cleanup
                )
            if hasattr(self.dashboard, "test_connections_requested"):
                self.dashboard.test_connections_requested.connect(
                    self.controller.test_all_connections
                )

            # Connect sync panel signals
            self.sync_panel.sync_button.clicked.connect(
                lambda: self.controller.run_full_sync("spo_to_sql")
            )
            self.sync_panel.test_button.clicked.connect(
                self.controller.test_all_connections
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

    @pyqtSlot(str)
    def _on_navigation_changed(self, nav_id: str):
        """Handle navigation changes"""
        try:
            self.navigation_stack.show_panel(nav_id)
            self.navigation_bar.set_active_navigation(nav_id)
            logger.debug(f"Navigation changed to: {nav_id}")
        except Exception as e:
            logger.error(f"Error handling navigation change: {e}")

    def _navigate_to(self, nav_id: str):
        """Navigate to specific panel"""
        self.navigation_bar.set_active_navigation(nav_id)
        self.navigation_stack.show_panel(nav_id)

    @pyqtSlot(str, int, str)
    def _update_progress(self, task_name: str, percentage: int, message: str):
        """Update progress across all panels"""
        try:
            # Update sync panel progress
            if hasattr(self.sync_panel, "progress_bar"):
                self.sync_panel.progress_bar.setValue(percentage)

            # Update dashboard progress if available
            if hasattr(self.dashboard, "update_progress"):
                self.dashboard.update_progress(task_name, percentage, message)

        except Exception as e:
            logger.debug(f"Error updating progress: {e}")

    @pyqtSlot(str)
    def _update_current_task(self, task_description: str):
        """Update current task description"""
        try:
            if hasattr(self.dashboard, "update_current_task"):
                self.dashboard.update_current_task(task_description)
        except Exception as e:
            logger.debug(f"Error updating current task: {e}")

    def _update_connection_status(self, service_name: str, status: str):
        """Update connection status indicators"""
        try:
            if hasattr(self.dashboard, "update_status"):
                self.dashboard.update_status(service_name, status)

            # Update navigation badge for connection issues
            if status == "error":
                self.navigation_bar.update_navigation_badge("dashboard", "!")
            elif status == "connected":
                self.navigation_bar.update_navigation_badge("dashboard", "")

        except Exception as e:
            logger.debug(f"Error updating connection status: {e}")

    def _update_sync_status(self, status: str):
        """Update sync status"""
        try:
            if hasattr(self.dashboard, "last_sync_status_card"):
                self.dashboard.last_sync_status_card.set_status(status)
        except Exception as e:
            logger.debug(f"Error updating sync status: {e}")

    def _update_auto_sync_status(self, enabled: bool):
        """Update auto-sync status"""
        try:
            if hasattr(self.dashboard, "auto_sync_status_card"):
                self.dashboard.auto_sync_status_card.set_status(enabled)
        except Exception as e:
            logger.debug(f"Error updating auto-sync status: {e}")

    @pyqtSlot(bool, str, dict)
    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.MEDIUM)
    def _handle_sync_completion(self, success: bool, message: str, stats: dict):
        """Handle sync completion with compact notification"""
        try:
            # Show compact notification instead of large dialog
            if success:
                self._show_compact_notification(
                    "✅ Sync Successful",
                    f"Synced {stats.get('records_added', 0)} records",
                )
            else:
                self._show_compact_notification("❌ Sync Failed", message)

            logger.info(f"Sync completion handled: Success={success}")

        except Exception as e:
            logger.error(f"Error handling sync completion: {e}")

    def _show_compact_notification(self, title: str, message: str):
        """Show compact notification"""
        # For now, just use log message
        # In the future, could implement toast notifications
        self.log_panel.log_console.add_log_message(f"{title}: {message}", "info")

    @pyqtSlot(bool)
    def toggle_ui_interactivity(self, enable: bool):
        """Enable/disable UI elements during operations"""
        try:
            # Disable/enable navigation
            self.navigation_bar.setEnabled(enable)

            # Disable/enable specific buttons
            if hasattr(self.sync_panel, "sync_button"):
                self.sync_panel.sync_button.setEnabled(enable)
            if hasattr(self.sync_panel, "test_button"):
                self.sync_panel.test_button.setEnabled(enable)

            logger.debug(f"UI interactivity {'enabled' if enable else 'disabled'}")

        except Exception as e:
            logger.error(f"Error toggling UI interactivity: {e}")

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.HIGH)
    def closeEvent(self, event: QCloseEvent):
        """Handle window close event with confirmation"""
        try:
            # Show compact confirmation
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "Exit DENSO Neural Matrix?",
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
            event.accept()

    def cleanup(self):
        """Perform safe cleanup of UI components"""
        if self.cleanup_done:
            logger.debug("OptimizedMainWindow cleanup already performed")
            return

        logger.info("Initiating OptimizedMainWindow cleanup...")

        try:
            # Disconnect all signals to prevent crashes
            self._disconnect_signals()

            # Cleanup panels
            panels_to_cleanup = ["dashboard", "config_panel", "sync_panel", "log_panel"]
            for panel_name in panels_to_cleanup:
                panel = getattr(self, panel_name, None)
                if panel and hasattr(panel, "cleanup"):
                    try:
                        panel.cleanup()
                        panel.deleteLater()
                        setattr(self, panel_name, None)
                        logger.debug(f"{panel_name} cleaned up")
                    except Exception as e:
                        logger.error(f"Error cleaning up {panel_name}: {e}")

            # Cleanup navigation components
            if self.navigation_stack:
                self.navigation_stack.cleanup()
                self.navigation_stack.deleteLater()
                self.navigation_stack = None

            if self.navigation_bar:
                self.navigation_bar.cleanup()
                self.navigation_bar.deleteLater()
                self.navigation_bar = None

            # Cleanup shortcuts
            shortcuts = [
                "shortcut_f1",
                "shortcut_f2",
                "shortcut_f3",
                "shortcut_f4",
                "shortcut_test",
                "shortcut_sync",
                "shortcut_quit",
                "shortcut_escape",
            ]
            for shortcut_name in shortcuts:
                shortcut = getattr(self, shortcut_name, None)
                if shortcut:
                    shortcut.deleteLater()

            # Cleanup central widget
            if self.central_widget:
                self.central_widget.deleteLater()
                self.central_widget = None

            self.cleanup_done = True
            logger.info("OptimizedMainWindow cleanup completed successfully")

        except Exception as e:
            logger.error(f"Error during OptimizedMainWindow cleanup: {e}")
            self.cleanup_done = True

    def _disconnect_signals(self):
        """Disconnect all signal connections"""
        try:
            # Navigation signals
            if self.navigation_bar:
                try:
                    self.navigation_bar.navigation_changed.disconnect()
                except (TypeError, RuntimeError):
                    pass

            # Controller signals
            signal_pairs = [
                (
                    self.controller.log_message,
                    self.log_panel.log_console.add_log_message,
                ),
                (self.controller.progress_updated, self._update_progress),
                (self.controller.current_task_update, self._update_current_task),
                (self.controller.sync_completed, self._handle_sync_completion),
                (self.controller.ui_enable_request, self.toggle_ui_interactivity),
            ]

            for signal, slot in signal_pairs:
                try:
                    signal.disconnect(slot)
                except (TypeError, RuntimeError):
                    pass

            # Disconnect lambda connections
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


# Backward compatibility alias
MainWindow = OptimizedMainWindow
