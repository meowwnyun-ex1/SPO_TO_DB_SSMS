# Updated main_window.py - Complete Signal Integration
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
from .styles.theme import apply_gradient_theme
from utils.logger import UILogHandler
import logging

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main window พร้อม Signal Integration ครบถ้วน"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ui_log_handler = None

        self.setup_window()
        self.setup_ui()
        self.setup_signal_connections()  # ครบถ้วนทุก signals
        self.setup_logging()
        self.load_initial_state()

        logger.info("🎉 Main window initialized with complete signal integration")

    def setup_window(self):
        """ตั้งค่าหน้าต่างหลัก"""
        self.setWindowTitle("SharePoint to SQL by เฮียตอม😎")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)

        apply_gradient_theme(self)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("🟢 ระบบพร้อมใช้งาน")

    def setup_ui(self):
        """สร้าง UI components"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        # Splitter for responsive layout
        splitter = QSplitter(Qt.Horizontal)

        # Main components
        self.dashboard = Dashboard(self.controller)
        self.config_panel = ConfigPanel(self.controller)

        splitter.addWidget(self.dashboard)
        splitter.addWidget(self.config_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([400, 800])

        layout.addWidget(splitter)

    def setup_signal_connections(self):
        """ตั้งค่า Signal Connections แบบครบถ้วน"""

        # === CONTROLLER → UI SIGNALS ===

        # Core status signals
        self.controller.status_changed.connect(self.on_status_changed)
        self.controller.progress_updated.connect(self.on_progress_updated)
        self.controller.sync_completed.connect(self.on_sync_completed)
        self.controller.log_message.connect(self.on_log_message)

        # === DASHBOARD → CONTROLLER SIGNALS ===

        # Connection testing
        self.dashboard.test_connections_requested.connect(
            self.controller.test_all_connections
        )

        # Sync operations
        self.dashboard.start_sync_requested.connect(self.controller.start_sync)
        self.dashboard.stop_sync_requested.connect(self.controller.stop_sync)

        # UI operations
        self.dashboard.clear_logs_requested.connect(self.clear_logs)
        self.dashboard.auto_sync_toggled.connect(self.controller.toggle_auto_sync)

        # === CONFIG PANEL → CONTROLLER SIGNALS ===

        # Configuration
        self.config_panel.config_changed.connect(self.controller.save_config)

        # Individual connection tests
        self.config_panel.test_sharepoint_requested.connect(
            self.controller.test_sharepoint_connection
        )
        self.config_panel.test_database_requested.connect(
            self.controller.test_database_connection
        )

        # Data refresh operations
        self.config_panel.refresh_sites_requested.connect(self._handle_refresh_sites)
        self.config_panel.refresh_lists_requested.connect(self._handle_refresh_lists)
        self.config_panel.refresh_databases_requested.connect(
            self._handle_refresh_databases
        )
        self.config_panel.refresh_tables_requested.connect(self._handle_refresh_tables)

        # === CROSS-COMPONENT SIGNALS ===

        # Dashboard status updates affect config panel
        self.controller.status_changed.connect(self._update_config_panel_status)

        logger.debug("✅ All signal connections established")

    def setup_logging(self):
        """ตั้งค่า UI logging handler"""
        self.ui_log_handler = UILogHandler(self.on_log_message)
        self.ui_log_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(self.ui_log_handler)

    def load_initial_state(self):
        """โหลดสถานะเริ่มต้น"""
        try:
            config = self.controller.get_config()
            self.config_panel.load_config(config)

            # Test connections in background
            QTimer.singleShot(100, self.controller.test_sharepoint_connection)
            QTimer.singleShot(200, self.controller.test_database_connection)

            logger.info("✅ Initial state loaded successfully")

        except Exception as e:
            logger.error(f"❌ Failed to load initial state: {str(e)}")
            self.show_error_message("การโหลดสถานะเริ่มต้น", str(e))

    # === SLOT IMPLEMENTATIONS ===

    @pyqtSlot(str, str)
    def on_status_changed(self, service, status):
        """จัดการการเปลี่ยนแปลงสถานะ"""
        self.dashboard.update_connection_status(service, status)

        # Update status bar
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
        """จัดการการอัพเดทความคืบหน้า"""
        self.dashboard.update_progress(message, progress, level)

        if progress > 0:
            self.status_bar.showMessage(f"🔄 {message} ({progress}%)")

    @pyqtSlot(bool, str, dict)
    def on_sync_completed(self, success, message, stats):
        """จัดการเมื่อซิงค์เสร็จสิ้น"""
        self.dashboard.on_sync_completed(success, message, stats)

        if success:
            records = stats.get("records_inserted", 0)
            duration = stats.get("duration", 0)
            self.status_bar.showMessage(
                f"✅ ซิงค์สำเร็จ: {records} รายการ ใน {duration:.1f} วินาที"
            )
            self.show_success_message("การซิงค์เสร็จสิ้น", message)
        else:
            self.status_bar.showMessage(f"❌ ซิงค์ล้มเหลว: {message}")
            self.show_error_message("การซิงค์ล้มเหลว", message)

    @pyqtSlot(str, str)
    def on_log_message(self, message, level):
        """จัดการข้อความ log"""
        self.dashboard.add_log_message(message, level)

    # === REFRESH HANDLERS ===

    def _handle_refresh_sites(self):
        """จัดการการรีเฟรช SharePoint Sites"""
        try:
            self.status_bar.showMessage("🔍 กำลังดึงรายการไซต์...")
            sites = self.controller.get_sharepoint_sites()
            # Update config panel with sites
            # self.config_panel.update_sharepoint_sites(sites)
            self.status_bar.showMessage(f"📡 พบไซต์ {len(sites)} รายการ")
        except Exception as e:
            logger.error(f"Failed to refresh sites: {str(e)}")
            self.show_error_message("การดึงรายการไซต์", str(e))

    def _handle_refresh_lists(self):
        """จัดการการรีเฟรช SharePoint Lists"""
        try:
            self.status_bar.showMessage("📋 กำลังดึงรายการลิสต์...")
            config = self.config_panel.get_config()
            lists = self.controller.get_sharepoint_lists(config.site_url)
            self.config_panel.update_sharepoint_lists(lists)
            self.status_bar.showMessage(f"📋 พบลิสต์ {len(lists)} รายการ")
        except Exception as e:
            logger.error(f"Failed to refresh lists: {str(e)}")
            self.show_error_message("การดึงรายการลิสต์", str(e))

    def _handle_refresh_databases(self):
        """จัดการการรีเฟรช Databases"""
        try:
            self.status_bar.showMessage("🗄️ กำลังดึงรายการฐานข้อมูล...")
            databases = self.controller.get_databases()
            self.config_panel.update_databases(databases)
            self.status_bar.showMessage(f"🗄️ พบฐานข้อมูล {len(databases)} รายการ")
        except Exception as e:
            logger.error(f"Failed to refresh databases: {str(e)}")
            self.show_error_message("การดึงรายการฐานข้อมูล", str(e))

    def _handle_refresh_tables(self):
        """จัดการการรีเฟรช Tables"""
        try:
            self.status_bar.showMessage("📊 กำลังดึงรายการตาราง...")
            tables = self.controller.get_tables()
            self.config_panel.update_tables(tables)
            self.status_bar.showMessage(f"📊 พบตาราง {len(tables)} รายการ")
        except Exception as e:
            logger.error(f"Failed to refresh tables: {str(e)}")
            self.show_error_message("การดึงรายการตาราง", str(e))

    def _update_config_panel_status(self, service, status):
        """อัพเดทสถานะใน Config Panel"""
        # Enable/disable refresh buttons based on connection status
        if service == "SharePoint" and status == "connected":
            # Enable SharePoint refresh buttons
            pass
        elif service == "Database" and status == "connected":
            # Enable Database refresh buttons
            pass

    # === UTILITY METHODS ===

    def clear_logs(self):
        """ล้าง Log Console"""
        self.dashboard.clear_logs()
        logger.info("🧹 Log console cleared by user")

    def show_success_message(self, title, message):
        """แสดงข้อความสำเร็จ"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def show_error_message(self, title, message):
        """แสดงข้อความข้อผิดพลาด"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def show_question_dialog(self, title, message):
        """แสดง Dialog ถามยืนยัน"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        return msg_box.exec_() == QMessageBox.Yes

    # === EVENT HANDLERS ===

    def closeEvent(self, event: QCloseEvent):
        """จัดการการปิดโปรแกรม"""
        try:
            # Check if sync is running
            if self.controller.get_sync_status()["is_running"]:
                if not self.show_question_dialog(
                    "ยืนยันการปิดโปรแกรม", "การซิงค์กำลังดำเนินการอยู่\nคุณต้องการปิดโปรแกรมหรือไม่?"
                ):
                    event.ignore()
                    return

                self.controller.stop_sync()

            # Cleanup
            self.controller.cleanup()

            if self.ui_log_handler:
                logging.getLogger().removeHandler(self.ui_log_handler)

            logger.info("🔄 Application closing gracefully")
            event.accept()

        except Exception as e:
            logger.error(f"❌ Error during application close: {str(e)}")
            event.accept()

    def keyPressEvent(self, event):
        """จัดการ Keyboard Shortcuts"""
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


# === ERROR HANDLING SYSTEM ===


class ErrorHandler:
    """Centralized Error Handling System"""

    @staticmethod
    def handle_connection_error(error, service_name):
        """จัดการข้อผิดพลาดการเชื่อมต่อ"""
        error_types = {
            "timeout": f"การเชื่อมต่อ {service_name} หมดเวลา",
            "auth": f"การยืนยันตัวตน {service_name} ล้มเหลว",
            "network": f"ปัญหาเครือข่ายในการเชื่อมต่อ {service_name}",
            "config": f"การตั้งค่า {service_name} ไม่ถูกต้อง",
        }

        # Determine error type
        error_str = str(error).lower()
        if "timeout" in error_str:
            return error_types["timeout"]
        elif "auth" in error_str or "401" in error_str:
            return error_types["auth"]
        elif "network" in error_str or "connection" in error_str:
            return error_types["network"]
        else:
            return error_types["config"]

    @staticmethod
    def handle_sync_error(error, phase):
        """จัดการข้อผิดพลาดการซิงค์"""
        phase_messages = {
            "fetch": "การดึงข้อมูลจาก SharePoint ล้มเหลว",
            "transform": "การประมวลผลข้อมูลล้มเหลว",
            "load": "การบันทึกข้อมูลลงฐานข้อมูลล้มเหลว",
        }

        base_message = phase_messages.get(phase, "การซิงค์ล้มเหลว")
        return f"{base_message}: {str(error)}"

    @staticmethod
    def suggest_solution(error_type, service_name):
        """แนะนำวิธีแก้ปัญหา"""
        solutions = {
            ("timeout", "SharePoint"): [
                "ตรวจสอบการเชื่อมต่ออินเทอร์เน็ต",
                "เพิ่มค่า Connection Timeout ในการตั้งค่า",
                "ลองเชื่อมต่อใหม่ในเวลาอื่น",
            ],
            ("auth", "SharePoint"): [
                "ตรวจสอบ Client ID และ Client Secret",
                "ยืนยัน Tenant ID ให้ถูกต้อง",
                "ตรวจสอบสิทธิ์การเข้าถึง SharePoint",
            ],
            ("config", "Database"): [
                "ตรวจสอบ Server Name และ Database Name",
                "ยืนยัน Username และ Password",
                "ตรวจสอบการตั้งค่า Firewall",
            ],
        }

        return solutions.get(
            (error_type, service_name),
            ["ตรวจสอบการตั้งค่าทั้งหมด", "ลองเชื่อมต่อใหม่", "ติดต่อผู้ดูแลระบบหากปัญหายังคงอยู่"],
        )


# === SIGNAL FLOW DIAGRAM ===
"""
Signal Flow Architecture:

UI Components          Controller            Business Logic
    │                     │                      │
    ├─ Dashboard          │                      │
    │  ├─ test_btn ────────┼─ test_connections ──┼─ ConnectionManager
    │  ├─ sync_btn ────────┼─ start_sync ────────┼─ SyncEngine  
    │  └─ auto_sync ───────┼─ toggle_auto_sync ──┼─ Timer
    │                     │                      │
    ├─ ConfigPanel        │                      │
    │  ├─ config_change ───┼─ save_config ───────┼─ ConfigManager
    │  ├─ test_sp ─────────┼─ test_sharepoint ───┼─ SPConnector
    │  └─ refresh_* ───────┼─ get_* ─────────────┼─ Connectors
    │                     │                      │
    └─ MainWindow         │                      │
       ├─ status_update ←─┼─ status_changed ←───┼─ Events
       ├─ progress ←──────┼─ progress_updated ←─┼─ SyncThread
       └─ completion ←────┼─ sync_completed ←───┼─ SyncEngine

Error Handling Flow:
    Exception → ErrorHandler → Log → UI Notification → User Action
"""
