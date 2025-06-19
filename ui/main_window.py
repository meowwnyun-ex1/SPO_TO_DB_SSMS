from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QSplitter,
    QMessageBox,
    QStatusBar,
)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer
from PyQt5.QtGui import QIcon, QCloseEvent

from .components.dashboard import Dashboard
from .components.config_panel import ConfigPanel
from .styles.theme import apply_gradient_theme
from utils.logger import UILogHandler
import logging

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ui_log_handler = None

        self.setup_window()
        self.setup_ui()
        self.setup_connections()
        self.setup_logging()

        # Load initial state
        self.load_initial_state()

        logger.info("Main window initialized successfully")

    def setup_window(self):
        """Setup main window properties"""
        self.setWindowTitle("SharePoint to SQL by เฮียตอม😎")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)

        # Set window icon
        try:
            self.setWindowIcon(QIcon("assets/icon.png"))
        except:
            pass  # Icon file not found

        # Apply gradient theme
        apply_gradient_theme(self)

        # Setup status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("🟢 ระบบพร้อมใช้งาน")

    def setup_ui(self):
        """Setup UI components"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout with splitter
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        # Create splitter for responsive layout
        splitter = QSplitter(Qt.Horizontal)

        # Create main components
        self.dashboard = Dashboard(self.controller)
        self.config_panel = ConfigPanel(self.controller)

        # Add components to splitter
        splitter.addWidget(self.dashboard)
        splitter.addWidget(self.config_panel)

        # Set splitter proportions (1:2 ratio)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([400, 800])

        # Add to main layout
        layout.addWidget(splitter)

        logger.debug("UI components created successfully")

    def setup_connections(self):
        """Setup signal connections"""
        # Controller signals
        self.controller.status_changed.connect(self.on_status_changed)
        self.controller.progress_updated.connect(self.on_progress_updated)
        self.controller.sync_completed.connect(self.on_sync_completed)
        self.controller.log_message.connect(self.on_log_message)

        # Dashboard signals
        self.dashboard.test_connections_requested.connect(
            self.controller.test_all_connections
        )
        self.dashboard.start_sync_requested.connect(self.controller.start_sync)
        self.dashboard.stop_sync_requested.connect(self.controller.stop_sync)
        self.dashboard.clear_logs_requested.connect(self.clear_logs)
        self.dashboard.auto_sync_toggled.connect(self.controller.toggle_auto_sync)

        # Config panel signals
        self.config_panel.config_changed.connect(self.controller.save_config)
        self.config_panel.test_sharepoint_requested.connect(
            self.controller.test_sharepoint_connection
        )
        self.config_panel.test_database_requested.connect(
            self.controller.test_database_connection
        )
        self.config_panel.refresh_sites_requested.connect(
            self.controller.get_sharepoint_sites
        )
        self.config_panel.refresh_lists_requested.connect(
            self.controller.get_sharepoint_lists
        )
        self.config_panel.refresh_databases_requested.connect(
            self.controller.get_databases
        )
        self.config_panel.refresh_tables_requested.connect(self.controller.get_tables)

        logger.debug("Signal connections established")

    def setup_logging(self):
        """Setup UI logging handler"""
        self.ui_log_handler = UILogHandler(self.on_log_message)
        self.ui_log_handler.setLevel(logging.INFO)

        # Add to root logger
        logging.getLogger().addHandler(self.ui_log_handler)

        logger.debug("UI logging handler setup complete")

    def load_initial_state(self):
        """Load initial application state"""
        try:
            # Load configuration
            config = self.controller.get_config()
            self.config_panel.load_config(config)

            # Update connection status
            self.update_connection_status()

            # Setup auto-sync if enabled
            if config.auto_sync_enabled:
                self.controller.toggle_auto_sync(True, config.sync_interval)
                self.dashboard.set_auto_sync_enabled(True)

            logger.info("Initial state loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load initial state: {str(e)}")
            self.show_error_message("การโหลดสถานะเริ่มต้น", str(e))

    def update_connection_status(self):
        """Update connection status indicators"""
        try:
            config = self.controller.get_config()

            # Test connections in background (non-blocking)
            QTimer.singleShot(100, lambda: self.controller.test_sharepoint_connection())
            QTimer.singleShot(200, lambda: self.controller.test_database_connection())

        except Exception as e:
            logger.warning(f"Failed to update connection status: {str(e)}")

    # Slot methods
    @pyqtSlot(str, str)
    def on_status_changed(self, service, status):
        """Handle status change signals"""
        self.dashboard.update_connection_status(service, status)

        # Update status bar
        if service == "SharePoint" and status == "connected":
            self.status_bar.showMessage("🟢 SharePoint เชื่อมต่อแล้ว")
        elif service == "Database" and status == "connected":
            self.status_bar.showMessage("🟢 ฐานข้อมูลเชื่อมต่อแล้ว")
        elif status == "error":
            self.status_bar.showMessage(f"🔴 {service} เชื่อมต่อล้มเหลว")

    @pyqtSlot(str, int, str)
    def on_progress_updated(self, message, progress, level):
        """Handle progress update signals"""
        self.dashboard.update_progress(message, progress, level)

        # Update status bar during sync
        if progress > 0:
            self.status_bar.showMessage(f"🔄 {message} ({progress}%)")

    @pyqtSlot(bool, str, dict)
    def on_sync_completed(self, success, message, stats):
        """Handle sync completion signals"""
        self.dashboard.on_sync_completed(success, message, stats)

        # Update status bar
        if success:
            records = stats.get("records_inserted", 0)
            duration = stats.get("duration", 0)
            self.status_bar.showMessage(
                f"✅ ซิงค์สำเร็จ: {records} รายการ ใน {duration:.1f} วินาที"
            )
        else:
            self.status_bar.showMessage(f"❌ ซิงค์ล้มเหลว: {message}")

        # Show completion message
        if success:
            self.show_success_message("การซิงค์เสร็จสิ้น", message)
        else:
            self.show_error_message("การซิงค์ล้มเหลว", message)

    @pyqtSlot(str, str)
    def on_log_message(self, message, level):
        """Handle log message signals"""
        self.dashboard.add_log_message(message, level)

    def clear_logs(self):
        """Clear log console"""
        self.dashboard.clear_logs()
        logger.info("Log console cleared by user")

    # Utility methods
    def show_success_message(self, title, message):
        """Show success message dialog"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def show_error_message(self, title, message):
        """Show error message dialog"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def show_warning_message(self, title, message):
        """Show warning message dialog"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def show_question_dialog(self, title, message):
        """Show question dialog and return user response"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        return msg_box.exec_() == QMessageBox.Yes

    def save_window_state(self):
        """Save window geometry and state"""
        try:
            config = self.controller.get_config()
            config.window_geometry = {
                "x": self.x(),
                "y": self.y(),
                "width": self.width(),
                "height": self.height(),
                "maximized": self.isMaximized(),
            }
            self.controller.save_config(config)

        except Exception as e:
            logger.warning(f"Failed to save window state: {str(e)}")

    def restore_window_state(self):
        """Restore window geometry and state"""
        try:
            config = self.controller.get_config()
            geometry = config.window_geometry

            if geometry:
                self.setGeometry(
                    geometry.get("x", 100),
                    geometry.get("y", 100),
                    geometry.get("width", 1400),
                    geometry.get("height", 900),
                )

                if geometry.get("maximized", False):
                    self.showMaximized()

        except Exception as e:
            logger.warning(f"Failed to restore window state: {str(e)}")

    def closeEvent(self, event: QCloseEvent):
        """Handle window close event"""
        try:
            # Check if sync is running
            if self.controller.get_sync_status()["is_running"]:
                if not self.show_question_dialog(
                    "ยืนยันการปิดโปรแกรม", "การซิงค์กำลังดำเนินการอยู่\nคุณต้องการปิดโปรแกรมหรือไม่?"
                ):
                    event.ignore()
                    return

                # Stop sync
                self.controller.stop_sync()

            # Save window state
            self.save_window_state()

            # Cleanup
            self.controller.cleanup()

            # Remove UI log handler
            if self.ui_log_handler:
                logging.getLogger().removeHandler(self.ui_log_handler)

            logger.info("Application closing gracefully")
            event.accept()

        except Exception as e:
            logger.error(f"Error during application close: {str(e)}")
            event.accept()  # Force close even if there's an error

    def keyPressEvent(self, event):
        """Handle key press events"""
        # F5 - Refresh connections
        if event.key() == Qt.Key_F5:
            self.controller.test_all_connections()

        # F9 - Start/Stop sync
        elif event.key() == Qt.Key_F9:
            if self.controller.get_sync_status()["is_running"]:
                self.controller.stop_sync()
            else:
                self.controller.start_sync()

        # Ctrl+L - Clear logs
        elif event.key() == Qt.Key_L and event.modifiers() == Qt.ControlModifier:
            self.clear_logs()

        # Ctrl+S - Save configuration
        elif event.key() == Qt.Key_S and event.modifiers() == Qt.ControlModifier:
            config = self.config_panel.get_config()
            self.controller.save_config(config)
            self.show_success_message("บันทึกการตั้งค่า", "บันทึกการตั้งค่าเรียบร้อยแล้ว")

        else:
            super().keyPressEvent(event)

    def resizeEvent(self, event):
        """Handle window resize event"""
        super().resizeEvent(event)

        # Update gradient background on resize
        try:
            apply_gradient_theme(self)
        except:
            pass  # Ignore errors during resize

    def get_current_config(self):
        """Get current configuration from UI"""
        return self.config_panel.get_config()

    def set_config(self, config):
        """Set configuration in UI"""
        self.config_panel.load_config(config)

    def get_sync_status(self):
        """Get current sync status"""
        return self.controller.get_sync_status()

    def is_sync_running(self):
        """Check if sync is currently running"""
        return self.controller.get_sync_status()["is_running"]
