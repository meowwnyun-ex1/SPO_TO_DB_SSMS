from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QSplitter,
    QMessageBox,
    QStatusBar,
    QGraphicsOpacityEffect,
    QLabel,
    QApplication,
)
from PyQt6.QtCore import Qt, pyqtSlot, QPropertyAnimation
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


class HolographicStatusBar(QStatusBar):
    """แก้แล้ว: ลด animation complexity"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_status = "ready"

        self.status_label = QLabel("Initializing neural matrix...")
        self.status_label.setStyleSheet(
            f"color: {UltraModernColors.TEXT_PRIMARY}; font-weight: bold;"
        )
        self.addPermanentWidget(self.status_label)

        # แก้: ลด animation เหลือแค่ opacity
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")

    @pyqtSlot(str, str)
    def set_neural_status(self, message, status_type="info"):
        """แก้แล้ว: ลด animation logic"""
        self.current_status = status_type

        color_map = {
            "info": UltraModernColors.TEXT_PRIMARY,
            "warning": UltraModernColors.NEON_YELLOW,
            "error": UltraModernColors.ERROR_COLOR,
            "ready": UltraModernColors.NEON_GREEN,
            "syncing": UltraModernColors.NEON_BLUE,
        }

        self.status_label.setText(message)
        self.status_label.setStyleSheet(
            f"color: {color_map.get(status_type, UltraModernColors.TEXT_PRIMARY)}; font-weight: bold;"
        )


class MainWindow(QMainWindow):
    """แก้แล้ว: ลด signal connections, แก้ error handling"""

    def __init__(self, controller):
        super().__init__(parent=None)
        self.controller = controller
        self.ui_log_handler = None
        self.is_closing = False

        # แก้: เพิ่ม error handler
        self.error_handler = get_error_handler()
        self.error_handler.error_occurred.connect(self._handle_application_error)

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        self.setup_holographic_ui()
        self.neural_status_bar.set_neural_status("Neural matrix online", "ready")
        self._connect_signals()
        self._setup_logging()

    def setup_holographic_ui(self):
        """UI setup อย่างเดียว"""
        self.setWindowTitle("SharePoint to SQL Sync - Quantum Matrix")
        self.setMinimumSize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # แก้: สร้าง components พร้อม error handling
        try:
            self.neural_dashboard = UltraModernDashboard(self.controller)
            self.ultra_modern_config_panel = UltraModernConfigPanel(self.controller)
        except Exception as e:
            logger.error(f"Failed to create UI components: {e}")
            self.neural_dashboard = None
            self.ultra_modern_config_panel = None
            return

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.addWidget(self.neural_dashboard)
        self.main_splitter.addWidget(self.ultra_modern_config_panel)
        self.main_splitter.setSizes([700, 300])

        main_layout.addWidget(self.main_splitter)

        self.neural_status_bar = HolographicStatusBar(self)
        self.setStatusBar(self.neural_status_bar)

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.MEDIUM)
    def _connect_signals(self):
        """แก้แล้ว: ลด connections + error handling"""
        if not self.ultra_modern_config_panel or not self.controller:
            logger.error("Cannot connect signals - missing components")
            return

        # Core config connections
        self.ultra_modern_config_panel.config_changed.connect(
            self.controller.update_config
        )
        self.ultra_modern_config_panel.test_sharepoint_requested.connect(
            self.controller.test_sharepoint_connection
        )
        self.ultra_modern_config_panel.test_database_requested.connect(
            self.controller.test_database_connection
        )

        # Data refresh connections
        self.ultra_modern_config_panel.refresh_sites_requested.connect(
            self.controller.refresh_sharepoint_sites
        )
        self.ultra_modern_config_panel.refresh_lists_requested.connect(
            self.controller.refresh_sharepoint_lists
        )
        self.ultra_modern_config_panel.refresh_databases_requested.connect(
            self.controller.refresh_database_names
        )
        self.ultra_modern_config_panel.refresh_tables_requested.connect(
            self.controller.refresh_database_tables
        )

        # Auto sync
        self.ultra_modern_config_panel.auto_sync_toggled.connect(
            self.controller.toggle_auto_sync
        )

        if not self.neural_dashboard:
            return

        # Controller to dashboard connections
        self.controller.log_message.connect(self.neural_dashboard.add_log_message)
        self.controller.log_message.connect(self.neural_status_bar.set_neural_status)
        self.controller.progress_update.connect(
            self.neural_dashboard.update_overall_progress
        )
        self.controller.current_task_update.connect(
            self.neural_dashboard.update_current_task
        )

        # Status updates
        self.controller.sharepoint_status_update.connect(
            self.neural_dashboard.update_sharepoint_status
        )
        self.controller.database_status_update.connect(
            self.neural_dashboard.update_database_status
        )
        self.controller.last_sync_status_update.connect(
            self.neural_dashboard.update_last_sync_status
        )
        self.controller.auto_sync_status_update.connect(
            self.neural_dashboard.set_auto_sync_enabled
        )

        # Data population
        self.controller.sharepoint_sites_updated.connect(
            self.ultra_modern_config_panel.populate_sharepoint_sites
        )
        self.controller.sharepoint_lists_updated.connect(
            self.ultra_modern_config_panel.populate_sharepoint_lists
        )
        self.controller.database_names_updated.connect(
            self.ultra_modern_config_panel.populate_database_names
        )
        self.controller.database_tables_updated.connect(
            self.ultra_modern_config_panel.populate_database_tables
        )

        # UI control
        self.controller.ui_enable_request.connect(
            self.ultra_modern_config_panel.set_ui_enabled
        )

        logger.info("✅ Signal connections established")

    def _setup_logging(self):
        """แก้แล้ว: ตรวจสอบก่อน setup logging"""
        if self.neural_dashboard:
            self.ui_log_handler = NeuraUILogHandler(
                self.neural_dashboard.add_log_message
            )
            logging.getLogger().addHandler(self.ui_log_handler)
            logger.info("UI log handler initialized")

    @pyqtSlot(object)
    def _handle_application_error(self, error_info):
        """แก้แล้ว: จัดการ error ที่เกิดใน application"""
        error_msg = f"Application Error: {error_info.message}"

        if self.neural_status_bar:
            self.neural_status_bar.set_neural_status(error_msg, "error")

        logger.error(error_msg)

    def closeEvent(self, event: QCloseEvent):
        """แก้แล้ว: ลด complexity ของ close event"""
        if self.is_closing:
            event.accept()
            return

        self.is_closing = True

        try:
            reply = QMessageBox.question(
                self,
                "Neural Matrix Shutdown",
                "Shutdown the neural matrix?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.neural_status_bar.set_neural_status("Shutting down...", "warning")
                QApplication.processEvents()
                self._cleanup_resources()
                event.accept()
                QApplication.quit()
            else:
                self.is_closing = False
                event.ignore()

        except Exception as e:
            logger.error(f"Shutdown error: {e}")
            event.accept()
            QApplication.quit()

    @handle_exceptions(ErrorCategory.SYSTEM, ErrorSeverity.LOW)
    def _cleanup_resources(self):
        """ทำความสะอาดทรัพยากร"""
        if self.controller:
            self.controller.cleanup()

        if self.ui_log_handler:
            logging.getLogger().removeHandler(self.ui_log_handler)

        if hasattr(self.neural_status_bar, "animation"):
            self.neural_status_bar.animation.stop()

        if self.neural_dashboard and hasattr(self.neural_dashboard, "cleanup"):
            self.neural_dashboard.cleanup()

        logger.info("🧹 Resources cleaned")

    def keyPressEvent(self, event):
        """แก้แล้ว: เพิ่ม error handling"""
        try:
            if event.key() == Qt.Key.Key_Escape:
                self.close()
            elif event.key() == Qt.Key.Key_F5 and self.controller:
                self.controller.run_full_sync()
            elif event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                if event.key() == Qt.Key.Key_Q:
                    self.close()
            else:
                super().keyPressEvent(event)
        except Exception as e:
            logger.error(f"Key press error: {e}")
            super().keyPressEvent(event)
