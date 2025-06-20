from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QSplitter,
    QMessageBox,
    QStatusBar,
    QLabel,
    QApplication,
)
from PyQt6.QtCore import Qt, pyqtSlot, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QCloseEvent
from .components.dashboard import ModernDashboard
from .components.config_panel import ModernConfigPanel
from .styles.theme import UltraModernColors
from utils.logger import NeuraUILogHandler
from utils.error_handling import (
    handle_exceptions,
    ErrorCategory,
    ErrorSeverity,
    get_error_handler,
)
import logging

logger = logging.getLogger(__name__)


class UltraModernStatusBar(QStatusBar):
    """Status bar แบบ Ultra Modern"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_status = "ready"

        self.status_label = QLabel("DENSO Neural matrix initializing...")
        self.status_label.setStyleSheet(
            f"""
            QLabel {{
                color: {UltraModernColors.TEXT_PRIMARY};
                font-weight: bold;
                font-size: 14px;
                padding: 5px 10px;
                background: {UltraModernColors.GLASS_BG_DARK};
                border: 1px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 8px;
                margin: 2px;
            }}
            """
        )
        self.addPermanentWidget(self.status_label)

        self.progress_label = QLabel("◦◦◦")
        self.progress_label.setStyleSheet(
            f"""
            QLabel {{
                color: {UltraModernColors.NEON_BLUE};
                font-weight: bold;
                font-size: 16px;
                padding: 2px 8px;
            }}
            """
        )
        self.addWidget(self.progress_label)

        self.progress_animation = QPropertyAnimation(self.progress_label, b"pos")
        self.progress_animation.setDuration(1000)
        self.progress_animation.setEasingCurve(QEasingCurve.Type.InOutSine)

    @pyqtSlot(str, str)
    def set_status(self, message, status_type="info"):
        """อัปเดตสถานะ status bar"""
        self.current_status = status_type

        color_map = {
            "info": UltraModernColors.TEXT_PRIMARY,
            "warning": UltraModernColors.NEON_YELLOW,
            "error": UltraModernColors.ERROR_COLOR,
            "ready": UltraModernColors.NEON_GREEN,
            "syncing": UltraModernColors.NEON_BLUE,
            "success": UltraModernColors.SUCCESS_COLOR,
        }

        icon_map = {
            "info": "◉",
            "warning": "◈",
            "error": "◆",
            "ready": "◎",
            "syncing": "⟳",
            "success": "✓",
        }

        status_color = color_map.get(status_type, UltraModernColors.TEXT_PRIMARY)
        status_icon = icon_map.get(status_type, "◉")

        self.status_label.setText(f"{status_icon} {message}")
        self.status_label.setStyleSheet(
            f"""
            QLabel {{
                color: {status_color};
                font-weight: bold;
                font-size: 14px;
                padding: 5px 10px;
                background: {UltraModernColors.GLASS_BG_DARK};
                border: 1px solid {status_color};
                border-radius: 8px;
                margin: 2px;
            }}
            """
        )

        if status_type == "syncing":
            self.start_progress_animation()
        else:
            self.stop_progress_animation()

    def start_progress_animation(self):
        """เริ่ม animation สำหรับ syncing"""
        if self.progress_animation.state() != QPropertyAnimation.State.Running:
            self.progress_animation.setLoopCount(-1)
            self.progress_animation.start()

    def stop_progress_animation(self):
        """หยุด animation"""
        if self.progress_animation.state() == QPropertyAnimation.State.Running:
            self.progress_animation.stop()

    def cleanup(self):
        """ทำความสะอาด animations"""
        self.stop_progress_animation()


class MainWindow(QMainWindow):
    """Main Window - แก้บัค cleanup และรองรับรูปพื้นหลัง"""

    def __init__(self, controller):
        super().__init__(parent=None)
        self.controller = controller
        self.ui_log_handler = None
        self.is_closing = False
        self.cleanup_done = False

        # Error handler
        self.error_handler = get_error_handler()
        self.error_handler.error_occurred.connect(self._handle_application_error)

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        self.setup_modern_ui()
        self._connect_signals()
        self._setup_logging()

        if hasattr(self, "status_bar"):
            self.status_bar.set_status(
                "Thammaphon Chittasuwanna (SDM) | Innovation", "ready"
            )

    def setup_modern_ui(self):
        """Setup UI โดยปรับขนาดให้เหมาะสมกับรูปพื้นหลัง"""
        self.setWindowTitle("DENSO Neural matrix online by เฮียตอม😎")

        # แก้: ปรับขนาดให้เหมาะกับหน้าจอ 1920x1080 และรูปพื้นหลัง
        self.setMinimumSize(1100, 750)

        # ปรับขนาดตามขนาดหน้าจอ
        screen = QApplication.primaryScreen()
        if screen:
            screen_size = screen.availableGeometry()
            # ใช้ 80% ของหน้าจอ
            width = min(1400, int(screen_size.width() * 0.8))
            height = min(900, int(screen_size.height() * 0.8))
            self.resize(width, height)
        else:
            self.resize(1300, 850)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # แก้: ลด margin เพื่อให้เห็นรูปพื้นหลังมากขึ้น
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        try:
            self.dashboard = ModernDashboard(self.controller)
            self.config_panel = ModernConfigPanel(self.controller)
        except Exception as e:
            logger.error(f"Failed to create UI components: {e}")
            self.dashboard = None
            self.config_panel = None
            return

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setChildrenCollapsible(False)

        if self.dashboard:
            self.main_splitter.addWidget(self.dashboard)
        if self.config_panel:
            self.main_splitter.addWidget(self.config_panel)

        # แก้: ปรับสัดส่วน 70% : 30%
        total_width = self.width() - 50  # หัก margin
        self.main_splitter.setSizes([int(total_width * 0.7), int(total_width * 0.3)])
        self.main_splitter.setStretchFactor(0, 7)
        self.main_splitter.setStretchFactor(1, 3)

        main_layout.addWidget(self.main_splitter)

        self.status_bar = UltraModernStatusBar(self)
        self.setStatusBar(self.status_bar)

        # Window styling - เตรียมไว้สำหรับรูปพื้นหลัง
        self.setStyleSheet(
            f"""
            QSplitter::handle {{
                background: {UltraModernColors.NEON_PURPLE};
                width: 3px;
                border-radius: 1px;
            }}
            QSplitter::handle:hover {{
                background: {UltraModernColors.NEON_PINK};
            }}
            """
        )

        # จัดหน้าต่างให้อยู่กลางจอ
        self._center_window()

    def _center_window(self):
        """จัดหน้าต่างให้อยู่กลางจอ"""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = self.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())

    def apply_background_with_transparency(self):
        """ปรับ transparency ของ components เพื่อให้เห็นรูปพื้นหลัง"""
        # ทำให้ dashboard และ config panel มี transparency
        if self.dashboard:
            self.dashboard.setStyleSheet(
                self.dashboard.styleSheet()
                + """
                QWidget {
                    background: rgba(0, 0, 0, 0.7);
                }
                """
            )

        if self.config_panel:
            self.config_panel.setStyleSheet(
                self.config_panel.styleSheet()
                + """
                QWidget {
                    background: rgba(0, 0, 0, 0.7);
                }
                """
            )

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.MEDIUM)
    def _connect_signals(self):
        """เชื่อมต่อ signals"""
        if not self.config_panel or not self.controller:
            logger.error("Cannot connect signals - missing components")
            return

        try:
            # Config panel signals
            self.config_panel.config_changed.connect(self.controller.update_config)
            self.config_panel.test_sharepoint_requested.connect(
                self.controller.test_sharepoint_connection
            )
            self.config_panel.test_database_requested.connect(
                self.controller.test_database_connection
            )

            # Refresh signals
            self.config_panel.refresh_sites_requested.connect(
                self.controller.refresh_sharepoint_sites
            )
            self.config_panel.refresh_lists_requested.connect(
                self.controller.refresh_sharepoint_lists
            )
            self.config_panel.refresh_databases_requested.connect(
                self.controller.refresh_database_names
            )
            self.config_panel.refresh_tables_requested.connect(
                self.controller.refresh_database_tables
            )

            self.config_panel.auto_sync_toggled.connect(
                self.controller.toggle_auto_sync
            )
        except Exception as e:
            logger.error(f"Config panel signals failed: {e}")

        if not self.dashboard:
            return

        try:
            # Controller to dashboard signals
            self.controller.log_message.connect(self.dashboard.add_log_message)
            self.controller.log_message.connect(self.status_bar.set_status)
            self.controller.progress_update.connect(
                self.dashboard.update_overall_progress
            )
            self.controller.current_task_update.connect(
                self.dashboard.update_current_task
            )

            # Status updates
            self.controller.sharepoint_status_update.connect(
                self.dashboard.update_sharepoint_status
            )
            self.controller.database_status_update.connect(
                self.dashboard.update_database_status
            )
            self.controller.last_sync_status_update.connect(
                self.dashboard.update_last_sync_status
            )
            self.controller.auto_sync_status_update.connect(
                self.dashboard.set_auto_sync_enabled
            )

            # Data population
            self.controller.sharepoint_sites_updated.connect(
                self.config_panel.populate_sharepoint_sites
            )
            self.controller.sharepoint_lists_updated.connect(
                self.config_panel.populate_sharepoint_lists
            )
            self.controller.database_names_updated.connect(
                self.config_panel.populate_database_names
            )
            self.controller.database_tables_updated.connect(
                self.config_panel.populate_database_tables
            )

            # UI control
            self.controller.ui_enable_request.connect(self.config_panel.set_ui_enabled)

            logger.info("Signal connections established successfully")
        except Exception as e:
            logger.error(f"Dashboard signals failed: {e}")

    def _setup_logging(self):
        """Setup logging handler"""
        if self.dashboard and hasattr(self.dashboard, "add_log_message"):
            try:
                self.ui_log_handler = NeuraUILogHandler(self.dashboard.add_log_message)
                logging.getLogger().addHandler(self.ui_log_handler)
                logger.info("UI log handler initialized")
            except Exception as e:
                logger.error(f"Failed to setup UI logging: {e}")

    @pyqtSlot(object)
    def _handle_application_error(self, error_info):
        """จัดการ application errors"""
        error_msg = f"Application Error: {error_info.message}"
        if hasattr(self, "status_bar"):
            self.status_bar.set_status(error_msg, "error")
        logger.error(error_msg)

    def closeEvent(self, event: QCloseEvent):
        """แก้บัค cleanup - ป้องกัน double cleanup"""
        if self.is_closing:
            event.accept()
            return

        self.is_closing = True

        try:
            reply = QMessageBox.question(
                self,
                "DENSO Neural matrix Shutdown",
                "Shutdown the DENSO Neural matrix system?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                if hasattr(self, "status_bar"):
                    self.status_bar.set_status("System shutting down...", "warning")

                QApplication.processEvents()

                # แก้: ทำ cleanup ครั้งเดียว
                if not self.cleanup_done:
                    self._safe_cleanup()

                event.accept()
                QApplication.quit()
            else:
                self.is_closing = False
                event.ignore()

        except Exception as e:
            logger.error(f"Close event error: {e}")
            if not self.cleanup_done:
                self._safe_cleanup()
            event.accept()
            QApplication.quit()

    @handle_exceptions(ErrorCategory.SYSTEM, ErrorSeverity.LOW)
    def _safe_cleanup(self):
        """แก้บัค: ทำความสะอาดอย่างปลอดภัย"""
        if self.cleanup_done:
            return

        try:
            # 1. Stop controller first
            if self.controller and hasattr(self.controller, "cleanup"):
                self.controller.cleanup()

            # 2. Remove log handler safely
            if self.ui_log_handler:
                try:
                    logging.getLogger().removeHandler(self.ui_log_handler)
                except:
                    pass
                self.ui_log_handler = None

            # 3. Stop status bar animations
            if hasattr(self, "status_bar"):
                self.status_bar.cleanup()

            # 4. Cleanup dashboard
            if self.dashboard and hasattr(self.dashboard, "cleanup"):
                self.dashboard.cleanup()

            # 5. Mark cleanup as done
            self.cleanup_done = True
            logger.info("Safe cleanup completed")

        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            self.cleanup_done = True

    def keyPressEvent(self, event):
        """Key shortcuts"""
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
            logger.error(f"Key press error: {e}")
            super().keyPressEvent(event)
