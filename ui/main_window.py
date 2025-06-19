from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QSplitter,
    QMessageBox,
    QStatusBar,
    QGraphicsOpacityEffect,
    QLabel,
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer, QPropertyAnimation
from PyQt6.QtGui import QCloseEvent
from .components.dashboard import UltraModernDashboard
from .components.config_panel import UltraModernConfigPanel
from .styles.theme import (
    UltraModernColors,
)
from utils.logger import UILogHandler
import logging

logger = logging.getLogger(__name__)


class HolographicStatusBar(QStatusBar):
    """
    Status bar แบบ holographic พร้อม neural network effects
    ปรับให้เข้ากับธีมใหม่และรองรับการแสดงผลสถานะ
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_holographic_style()
        self.setup_status_animations()
        self.current_status = "ready"

        # Ensure the status label exists
        self.status_label = QLabel("Initializing neural matrix...")
        self.status_label.setStyleSheet(
            f"color: {UltraModernColors.TEXT_PRIMARY}; font-weight: bold;"
        )
        self.addPermanentWidget(self.status_label)

    def setup_holographic_style(self):
        """
        ตั้งค่าสไตล์ holographic สำหรับ Status Bar
        สไตล์หลักถูกกำหนดไว้ใน theme.py แล้ว
        """
        # Specific styles for status bar are now handled in apply_ultra_modern_theme
        pass

    def setup_status_animations(self):
        """ตั้งค่าแอนิเมชั่นสถานะ (ถ้ามี)"""
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.7)
        self.animation.setLoopCount(-1)  # Loop indefinitely
        # Fix: Manually set start/end values for alternating effect on loop
        # Ensure only one connection to finished to avoid multiple calls
        self.animation.finished.connect(
            self._reverse_opacity_animation
        )  # Connect to a new method to reverse

        self.animation.start()

    def _reverse_opacity_animation(self):
        """Reverses the start and end values of the opacity animation."""
        # This method is called when the animation finishes, and because loopCount is -1,
        # it means it completed one cycle. We then reverse the values and restart.
        start = self.animation.startValue()
        end = self.animation.endValue()
        self.animation.setStartValue(end)
        self.animation.setEndValue(start)
        self.animation.start()  # Restart the animation with reversed values

    @pyqtSlot(str, str)
    def set_neural_status(self, message, status_type="info"):
        """
        ตั้งค่าสถานะและข้อความใน Status Bar
        Args:
            message (str): ข้อความที่จะแสดง
            status_type (str): ประเภทของสถานะ ('info', 'warning', 'error', 'ready')
        """
        self.current_status = status_type

        # Set text and color based on status type
        color_map = {
            "info": UltraModernColors.TEXT_PRIMARY,
            "warning": UltraModernColors.NEON_YELLOW,
            "error": UltraModernColors.ERROR_COLOR,
            "ready": UltraModernColors.NEON_GREEN,
            "syncing": UltraModernColors.NEON_BLUE,  # Add a syncing color
        }
        text_color = color_map.get(status_type, UltraModernColors.TEXT_PRIMARY)

        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {text_color}; font-weight: bold;")

        # Stop and restart animation for visual feedback on status change
        self.animation.stop()
        # Reset to initial start/end values before starting again
        self.animation.setStartValue(1.0)
        if status_type in ["error", "warning", "syncing"]:
            self.animation.setEndValue(0.4)  # More pronounced pulse for critical states
            self.animation.setDuration(500)
        else:
            self.animation.setEndValue(0.7)
            self.animation.setDuration(1000)

        # Ensure only one connection to finished to avoid multiple calls
        try:
            self.animation.finished.disconnect(self._reverse_opacity_animation)
        except TypeError:
            pass  # Ignore if not connected
        self.animation.finished.connect(self._reverse_opacity_animation)
        self.animation.start()

    def _prepare_shutdown(self, event):
        """Prepare for neural matrix shutdown"""
        logger.info("Initiating neural matrix shutdown sequence...")
        try:
            # Optionally show a confirmation dialog
            reply = QMessageBox.question(
                self,
                "Neural Matrix Shutdown",
                "Are you sure you want to initiate full neural matrix shutdown?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.set_neural_status("Neural matrix shutting down...", "warning")
                # Simulate a delay for shutdown process
                QTimer.singleShot(2000, lambda: self._complete_shutdown(event))
                event.ignore()  # Ignore close event for now, accept after shutdown completes
            else:
                logger.info("Neural matrix shutdown cancelled.")
                event.accept()

        except Exception as e:
            logger.error(f"Error during neural shutdown: {str(e)}")
            event.accept()

    def _complete_shutdown(self, event):
        """Complete neural matrix shutdown"""
        try:
            self.controller.cleanup()
            if self.ui_log_handler:
                logging.getLogger().removeHandler(self.ui_log_handler)

            self.set_neural_status("Neural matrix shutdown complete", "ready")
            event.accept()  # Now accept the close event

        except Exception as e:
            logger.error(f"Error completing neural shutdown: {str(e)}")
            event.accept()


class MainWindow(QMainWindow):
    """
    Main window สำหรับโปรเจคนี้ ใช้แสดงผล Dashboard และ Config Panel
    ปรับให้รองรับการปรับขนาดและแสดงผลในหน้าเดียว
    """

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ui_log_handler = None  # Initialize to None
        self.setup_holographic_ui()
        # Initial status bar message before connecting signals
        self.neural_status_bar.set_neural_status(
            "Neural matrix online. System ready.", "ready"
        )
        self._connect_signals()  # Connect signals after UI setup

        # Set up UI Log Handler after status bar is ready
        self.ui_log_handler = UILogHandler(self.neural_dashboard.add_log_message)
        logging.getLogger().addHandler(self.ui_log_handler)
        logger.info("UI log handler initialized.")

    def setup_holographic_ui(self):
        """
        ตั้งค่า UI แบบ holographic สำหรับ MainWindow
        ใช้ QSplitter เพื่อให้ผู้ใช้สามารถปรับขนาดส่วน Dashboard และ Config Panel ได้
        """
        self.setWindowTitle("SharePoint to SQL Sync - Quantum Matrix")

        # Set minimum size to allow for smaller scaling, but maintain usability
        self.setMinimumSize(800, 600)

        # Central widget setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main horizontal layout to hold the splitter
        main_h_layout = QHBoxLayout(central_widget)
        main_h_layout.setContentsMargins(10, 10, 10, 10)
        main_h_layout.setSpacing(10)

        # Initialize Dashboard and Config Panel
        self.neural_dashboard = UltraModernDashboard(self.controller)
        self.ultra_modern_config_panel = UltraModernConfigPanel(self.controller)

        # Create QSplitter to allow dynamic resizing by user
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.addWidget(self.neural_dashboard)
        self.main_splitter.addWidget(self.ultra_modern_config_panel)

        # Set initial sizes for the splitter sections (e.g., 70% dashboard, 30% config)
        # These percentages will be relative to the initial window size.
        self.main_splitter.setSizes([int(self.width() * 0.7), int(self.width() * 0.3)])

        # Add the splitter to the main layout
        main_h_layout.addWidget(self.main_splitter)

        # Status Bar setup
        self.neural_status_bar = HolographicStatusBar(self)
        self.setStatusBar(self.neural_status_bar)

        # Set object names for styling in QSS if needed
        self.neural_dashboard.setObjectName("neuralDashboard")
        self.ultra_modern_config_panel.setObjectName("configPanel")
        self.main_splitter.setObjectName("mainSplitter")

    def _connect_signals(self):
        """Connect signals to slots"""
        # Connect signals from config panel to dashboard or controller
        self.ultra_modern_config_panel.config_changed.connect(
            self.controller.update_config
        )
        self.ultra_modern_config_panel.test_sharepoint_requested.connect(
            self.controller.test_sharepoint_connection
        )
        self.ultra_modern_config_panel.test_database_requested.connect(
            self.controller.test_database_connection
        )
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
        self.ultra_modern_config_panel.auto_sync_toggled.connect(
            self.controller.toggle_auto_sync
        )
        self.ultra_modern_config_panel.run_sync_requested.connect(
            self.controller.run_full_sync
        )
        self.ultra_modern_config_panel.clear_cache_requested.connect(
            self.neural_dashboard.clear_cache
        )  # Connect to dashboard method

        # Connect controller signals to dashboard/status bar
        self.controller.log_message.connect(self.neural_dashboard.add_log_message)
        # Note: self.controller.status_update needs to be connected to self.neural_status_bar.set_neural_status
        # if the controller emits a generic status_update.
        # Assuming controller emits more specific updates or status_update handles mapping.
        # For now, if controller.status_update is intended for status bar directly:
        self.controller.status_update.connect(self.neural_status_bar.set_neural_status)
        self.controller.progress_update.connect(
            self.neural_dashboard.update_overall_progress
        )
        self.controller.current_task_update.connect(
            self.neural_dashboard.update_current_task
        )
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

        # Connect controller to config panel for enabling/disabling UI
        self.controller.ui_enable_request.connect(
            self.ultra_modern_config_panel.set_ui_enabled
        )

    def closeEvent(self, event: QCloseEvent):
        """
        Handle close event to ensure proper shutdown.
        จัดการเหตุการณ์ปิดหน้าต่างเพื่อให้แน่ใจว่าปิดระบบอย่างถูกต้อง
        """
        self._prepare_shutdown(event)
