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
from .components.dashboard import UltraModernDashboard
from .components.config_panel import UltraModernConfigPanel
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
    """Status bar แบบ Ultra Modern ลบ shadow effects"""

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

        # Progress indicator
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

        # Animation for progress
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

        # Animate progress for syncing
        if status_type == "syncing":
            self.start_progress_animation()
        else:
            self.stop_progress_animation()

    def start_progress_animation(self):
        """เริ่ม animation สำหรับ syncing"""
        if not self.progress_animation.state() == QPropertyAnimation.State.Running:
            self.progress_animation.setLoopCount(-1)  # Infinite loop
            self.progress_animation.start()

    def stop_progress_animation(self):
        """หยุด animation"""
        if self.progress_animation.state() == QPropertyAnimation.State.Running:
            self.progress_animation.stop()


class MainWindow(QMainWindow):
    """Main Window แก้ไข import errors และ cleanup issues"""

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

        # Set initial status
        if hasattr(self, "status_bar"):
            self.status_bar.set_status(
                "Thammaphon Chittasuwanna (SDM) | Innovation", "ready"
            )

    def setup_modern_ui(self):
        """Setup UI โดยไม่ใช้ shadow effects"""
        self.setWindowTitle("DENSO Neural matrix online by เฮียตอม😎")
        self.setMinimumSize(1200, 800)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        # Create components with error handling
        try:
            self.dashboard = UltraModernDashboard(self.controller)
            self.config_panel = UltraModernConfigPanel(self.controller)
        except Exception as e:
            logger.error(f"Failed to create UI components: {e}")
            self.dashboard = None
            self.config_panel = None
            return

        # Splitter for responsive layout
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setChildrenCollapsible(False)

        if self.dashboard:
            self.main_splitter.addWidget(self.dashboard)
        if self.config_panel:
            self.main_splitter.addWidget(self.config_panel)

        # Set proportional sizes: 70% dashboard, 30% config
        self.main_splitter.setSizes([840, 360])  # Based on 1200px width
        self.main_splitter.setStretchFactor(0, 2)  # Dashboard more flexible
        self.main_splitter.setStretchFactor(1, 1)  # Config panel fixed-ish

        main_layout.addWidget(self.main_splitter)

        # Status bar
        self.status_bar = UltraModernStatusBar(self)
        self.setStatusBar(self.status_bar)

        # Window styling
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a,
                    stop:0.3 #1a0a1a,
                    stop:0.7 #0a1a1a,
                    stop:1 #0a0a0a
                );
                border: 2px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 15px;
            }}
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

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.MEDIUM)
    def _connect_signals(self):
        """เชื่อมต่อ signals โดยตรวจสอบ component ก่อน"""
        if not self.config_panel or not self.controller:
            logger.error("Cannot connect signals - missing components")
            return

        # Config panel signals
        try:
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

            # Auto sync
            self.config_panel.auto_sync_toggled.connect(
                self.controller.toggle_auto_sync
            )
        except Exception as e:
            logger.error(f"Config panel signals failed: {e}")

        if not self.dashboard:
            return

        # Controller to dashboard signals
        try:
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
        """Setup logging handler with error protection"""
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
        """ปรับปรุง close event เพื่อป้องกัน cleanup errors"""
        if self.is_closing or self.cleanup_done:
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
                self._safe_cleanup()
                event.accept()
                QApplication.quit()
            else:
                self.is_closing = False
                event.ignore()

        except Exception as e:
            logger.error(f"Close event error: {e}")
            event.accept()
            QApplication.quit()

    @handle_exceptions(ErrorCategory.SYSTEM, ErrorSeverity.LOW)
    def _safe_cleanup(self):
        """ทำความสะอาดอย่างปลอดภัย"""
        if self.cleanup_done:
            return

        try:
            # Stop controller first
            if self.controller:
                self.controller.cleanup()

            # Remove log handler safely
            if self.ui_log_handler:
                try:
                    logging.getLogger().removeHandler(self.ui_log_handler)
                    self.ui_log_handler = None
                except:
                    pass

            # Stop animations
            if hasattr(self, "status_bar") and hasattr(
                self.status_bar, "progress_animation"
            ):
                self.status_bar.stop_progress_animation()

            # Cleanup components
            if self.dashboard and hasattr(self.dashboard, "cleanup"):
                self.dashboard.cleanup()

            self.cleanup_done = True
            logger.info("Safe cleanup completed")

        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            self.cleanup_done = True

    def keyPressEvent(self, event):
        """Key shortcuts with error handling"""
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
