from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QSplitter,
    QMessageBox,
    QStatusBar,
)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer
from PyQt5.QtGui import QCloseEvent
from .components.dashboard import Dashboard
from .components.config_panel import ConfigPanel
from utils.logger import UILogHandler
import logging

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ui_log_handler = None
        self.setup_window()
        self.setup_ui()
        self.setup_signal_connections()
        self.setup_logging()
        self.load_initial_state()

    def setup_window(self):
        """Window configuration"""
        self.setWindowTitle("SharePoint to SQL by เฮียตอม😎")
        self.setGeometry(100, 100, 1600, 1000)
        self.setMinimumSize(1400, 900)

        # Clean dark theme
        self.setStyleSheet(
            """
            QMainWindow {
                background: #1a1a2e;
                color: #ffffff;
            }
            QSplitter {
                background: transparent;
                border: none;
            }
            QSplitter::handle {
                background: #4a5568;
                width: 2px;
                margin: 10px;
                border-radius: 1px;
            }
            QSplitter::handle:hover {
                background: #00d4ff;
            }
        """
        )

        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(
            """
            QStatusBar {
                background: #16213e;
                color: #ffffff;
                border-top: 1px solid #4a5568;
                padding: 8px 15px;
                font-size: 12px;
            }
        """
        )
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("🟢 ระบบพร้อมใช้งาน")

    def setup_ui(self):
        """Main layout - fixed spacing and alignment"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main horizontal layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        main_layout.setSpacing(0)  # Remove spacing

        # Splitter for responsive design
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        # Create components
        self.dashboard = Dashboard(self.controller)
        self.config_panel = ConfigPanel(self.controller)

        # Add to splitter
        splitter.addWidget(self.dashboard)
        splitter.addWidget(self.config_panel)

        # Set proportions (dashboard: config = 1:2)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([500, 1000])  # Fixed initial sizes

        main_layout.addWidget(splitter)

    def setup_signal_connections(self):
        """Signal connections"""
        # Controller → UI
        self.controller.status_changed.connect(self.on_status_changed)
        self.controller.progress_updated.connect(self.on_progress_updated)
        self.controller.sync_completed.connect(self.on_sync_completed)
        self.controller.log_message.connect(self.on_log_message)

        # Dashboard → Controller
        self.dashboard.test_connections_requested.connect(
            self.controller.test_all_connections
        )
        self.dashboard.start_sync_requested.connect(self.controller.start_sync)
        self.dashboard.stop_sync_requested.connect(self.controller.stop_sync)
        self.dashboard.clear_logs_requested.connect(self.clear_logs)
        self.dashboard.auto_sync_toggled.connect(self.controller.toggle_auto_sync)

        # Config Panel → Controller
        self.config_panel.config_changed.connect(self.controller.save_config)
        self.config_panel.test_sharepoint_requested.connect(
            self.controller.test_sharepoint_connection
        )
        self.config_panel.test_database_requested.connect(
            self.controller.test_database_connection
        )
        self.config_panel.refresh_sites_requested.connect(self._handle_refresh_sites)
        self.config_panel.refresh_lists_requested.connect(self._handle_refresh_lists)
        self.config_panel.refresh_databases_requested.connect(
            self._handle_refresh_databases
        )
        self.config_panel.refresh_tables_requested.connect(self._handle_refresh_tables)

    def setup_logging(self):
        """UI logging handler"""
        self.ui_log_handler = UILogHandler(self.on_log_message)
        self.ui_log_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(self.ui_log_handler)

    def load_initial_state(self):
        """Load initial configuration"""
        try:
            config = self.controller.get_config()
            self.config_panel.load_config(config)
            QTimer.singleShot(100, self.controller.test_sharepoint_connection)
            QTimer.singleShot(200, self.controller.test_database_connection)
        except Exception as e:
            logger.error(f"Failed to load initial state: {str(e)}")

    # Slot handlers
    @pyqtSlot(str, str)
    def on_status_changed(self, service, status):
        self.dashboard.update_connection_status(service, status)
        status_messages = {
            ("SharePoint", "connected"): "🟢 SharePoint เชื่อมต่อแล้ว",
            ("Database", "connected"): "🟢 ฐานข้อมูลเชื่อมต่อแล้ว",
            ("SharePoint", "error"): "🔴 SharePoint เชื่อมต่อล้มเหลว",
            ("Database", "error"): "🔴 ฐานข้อมูลเชื่อมต่อล้มเหลว",
        }
        message = status_messages.get((service, status), f"📡 {service}: {status}")
        self.status_bar.showMessage(message)

    @pyqtSlot(str, int, str)
    def on_progress_updated(self, message, progress, level):
        self.dashboard.update_progress(message, progress, level)
        if progress > 0:
            self.status_bar.showMessage(f"🔄 {message} ({progress}%)")

    @pyqtSlot(bool, str)
    def on_sync_completed(self, success, message):
        stats = {}
        self.dashboard.on_sync_completed(success, message, stats)

        if success:
            self.status_bar.showMessage(f"✅ ซิงค์สำเร็จ: {message}")
            self.show_success_message("การซิงค์เสร็จสิ้น", message)
        else:
            self.status_bar.showMessage(f"❌ ซิงค์ล้มเหลว: {message}")
            self.show_error_message("การซิงค์ล้มเหลว", message)

    @pyqtSlot(str, str)
    def on_log_message(self, message, level):
        self.dashboard.add_log_message(message, level)

    # Refresh handlers
    def _handle_refresh_sites(self):
        try:
            self.status_bar.showMessage("🔍 กำลังดึงรายการไซต์...")
            sites = self.controller.get_sharepoint_sites()
            self.status_bar.showMessage(f"📡 พบไซต์ {len(sites)} รายการ")
        except Exception as e:
            self.show_error_message("การดึงรายการไซต์", str(e))

    def _handle_refresh_lists(self):
        try:
            self.status_bar.showMessage("📋 กำลังดึงรายการลิสต์...")
            config = self.config_panel.get_config()
            lists = self.controller.get_sharepoint_lists(config.site_url)
            self.config_panel.update_sharepoint_lists(lists)
            self.status_bar.showMessage(f"📋 พบลิสต์ {len(lists)} รายการ")
        except Exception as e:
            self.show_error_message("การดึงรายการลิสต์", str(e))

    def _handle_refresh_databases(self):
        try:
            self.status_bar.showMessage("🗄️ กำลังดึงรายการฐานข้อมูล...")
            databases = self.controller.get_databases()
            self.config_panel.update_databases(databases)
            self.status_bar.showMessage(f"🗄️ พบฐานข้อมูล {len(databases)} รายการ")
        except Exception as e:
            self.show_error_message("การดึงรายการฐานข้อมูล", str(e))

    def _handle_refresh_tables(self):
        try:
            self.status_bar.showMessage("📊 กำลังดึงรายการตาราง...")
            tables = self.controller.get_tables()
            self.config_panel.update_tables(tables)
            self.status_bar.showMessage(f"📊 พบตาราง {len(tables)} รายการ")
        except Exception as e:
            self.show_error_message("การดึงรายการตาราง", str(e))

    # Utility methods
    def clear_logs(self):
        self.dashboard.clear_logs()

    def show_success_message(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

    def show_error_message(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

    def closeEvent(self, event: QCloseEvent):
        try:
            if self.controller.get_sync_status()["is_running"]:
                reply = QMessageBox.question(
                    self,
                    "ยืนยันการปิดโปรแกรม",
                    "การซิงค์กำลังดำเนินการอยู่\nคุณต้องการปิดโปรแกรมหรือไม่?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    event.ignore()
                    return
                self.controller.stop_sync()

            self.controller.cleanup()
            if self.ui_log_handler:
                logging.getLogger().removeHandler(self.ui_log_handler)
            event.accept()
        except Exception as e:
            logger.error(f"Error during close: {str(e)}")
            event.accept()
