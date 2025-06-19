from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QCheckBox,
    QSizePolicy,
    QGraphicsDropShadowEffect,
    QGridLayout,
)
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QColor
from ..widgets.status_card import StatusCard
from ..widgets.cyber_log_console import CyberLogConsole
from ..widgets.holographic_progress_bar import HolographicProgressBar
from ..widgets.progress_card import UltraModernProgressCard
from ..styles.theme import (
    UltraModernColors,
    get_ultra_modern_card_style,
    get_gradient_button_style,
    get_neon_checkbox_style,  # Added get_neon_checkbox_style
)
import logging

logger = logging.getLogger(__name__)


class HolographicFrame(QFrame):
    """
    เฟรมแบบ holographic พร้อม dimensional effects
    ใช้สำหรับสร้างส่วนต่างๆ ของ UI ให้มีสไตล์
    """

    def __init__(self, variant="default", parent=None):
        super().__init__(parent)
        self.variant = variant
        self.setup_holographic_style()
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(20)
        self.shadow_effect.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(self.shadow_effect)

    def setup_holographic_style(self):
        """ตั้งค่าสไตล์ holographic"""
        style = get_ultra_modern_card_style(self.variant)
        self.setStyleSheet(style)


class UltraModernDashboard(QWidget):
    """
    Dashboard หลักของระบบ แสดงสถานะการเชื่อมต่อ, ความคืบหน้า, และ Log
    ปรับให้รองรับการแสดงผลในหน้าเดียวโดยไม่มี Scrollbar
    """

    clear_cache_requested = pyqtSignal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ultra_modern_ui()

    def setup_ultra_modern_ui(self):
        """
        ตั้งค่า UI แบบ ultra modern สำหรับ Dashboard
        ใช้ QGridLayout เพื่อการจัดเรียงที่ยืดหยุ่นและตอบสนอง
        """
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        top_h_layout = QHBoxLayout()
        top_h_layout.setSpacing(15)

        self.sharepoint_status_card = StatusCard(
            "SharePoint Connection", "disconnected"
        )
        self.database_status_card = StatusCard("Database Connection", "disconnected")
        self.last_sync_status_card = StatusCard("Last Sync", "never")

        top_h_layout.addWidget(self.sharepoint_status_card)
        top_h_layout.addWidget(self.database_status_card)
        top_h_layout.addWidget(self.last_sync_status_card)
        top_h_layout.setStretchFactor(self.sharepoint_status_card, 1)
        top_h_layout.setStretchFactor(self.database_status_card, 1)
        top_h_layout.setStretchFactor(self.last_sync_status_card, 1)

        control_frame = HolographicFrame(variant="highlight")
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.setSpacing(10)

        self.run_sync_button = QPushButton("Initiate Sync")
        self.run_sync_button.setStyleSheet(get_gradient_button_style("primary"))
        self.run_sync_button.clicked.connect(self.controller.run_full_sync)

        self.clear_cache_button = QPushButton("Clear Cache")
        self.clear_cache_button.setStyleSheet(get_gradient_button_style("secondary"))
        self.clear_cache_button.clicked.connect(self.clear_cache)

        self.auto_sync_check = QCheckBox("Auto Sync Enabled")
        # Corrected: Use get_neon_checkbox_style()
        self.auto_sync_check.setStyleSheet(get_neon_checkbox_style())
        self.auto_sync_check.stateChanged.connect(self.controller.toggle_auto_sync)

        control_layout.addWidget(self.run_sync_button)
        control_layout.addWidget(self.clear_cache_button)
        control_layout.addStretch(1)
        control_layout.addWidget(self.auto_sync_check)

        main_layout.addLayout(top_h_layout)
        main_layout.addWidget(control_frame)

        middle_grid_layout = QGridLayout()
        middle_grid_layout.setSpacing(15)

        progress_frame = HolographicFrame()
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(15, 15, 15, 15)
        self.overall_progress_label = QLabel("Overall Sync Progress:")
        self.overall_progress_label.setStyleSheet(
            f"color: {UltraModernColors.TEXT_PRIMARY}; font-weight: bold;"
        )
        self.overall_progress_bar = HolographicProgressBar()
        self.overall_progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.overall_progress_label)
        progress_layout.addWidget(self.overall_progress_bar)

        middle_grid_layout.addWidget(progress_frame, 0, 0, 1, 2)

        task_frame = HolographicFrame()
        task_layout = QVBoxLayout(task_frame)
        task_layout.setContentsMargins(15, 15, 15, 15)
        self.current_task_label = QLabel("Current Task: Idle")
        self.current_task_label.setStyleSheet(
            f"color: {UltraModernColors.TEXT_ACCENT}; font-size: 14px; font-weight: bold;"
        )
        self.detail_progress_bar = UltraModernProgressCard("Task Progress", 0)

        task_layout.addWidget(self.current_task_label)
        task_layout.addWidget(self.detail_progress_bar)

        middle_grid_layout.addWidget(task_frame, 1, 0, 1, 2)

        log_frame = HolographicFrame()
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(15, 15, 15, 15)
        log_label = QLabel("System Log:")
        log_label.setStyleSheet(
            f"color: {UltraModernColors.TEXT_PRIMARY}; font-weight: bold;"
        )
        self.log_console = CyberLogConsole()
        self.log_console.setMinimumHeight(150)
        self.log_console.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        log_layout.addWidget(log_label)
        log_layout.addWidget(self.log_console)

        middle_grid_layout.addWidget(log_frame, 2, 0, 1, 2)

        middle_grid_layout.setColumnStretch(0, 1)
        middle_grid_layout.setColumnStretch(1, 1)

        main_layout.addLayout(middle_grid_layout)
        main_layout.setStretchFactor(middle_grid_layout, 1)

        self.add_log_message(
            "Neural Dashboard initialized. Awaiting commands...", "info"
        )

    @pyqtSlot(int)
    def update_overall_progress(self, value):
        """อัปเดตความคืบหน้ารวม"""
        self.overall_progress_bar.setValue(value)
        self.overall_progress_bar.setFormat(f"Overall Progress: {value}%")

    @pyqtSlot(int, int)
    def update_detail_progress(self, current, total):
        """อัปเดตความคืบหน้าของงานย่อย"""
        if isinstance(self.detail_progress_bar, UltraModernProgressCard):
            self.detail_progress_bar.set_progress(current, total)
        else:
            logger.warning(
                "detail_progress_bar is not an UltraModernProgressCard instance."
            )

    @pyqtSlot(str, str)
    def add_log_message(self, message, level="info"):
        """
        เพิ่มข้อความ Log พร้อมเอฟเฟกต์การพิมพ์
        Args:
            message (str): ข้อความ Log
            level (str): ระดับ Log ('info', 'warning', 'error')
        """
        self.log_console.add_message_with_typing(message, level)

    @pyqtSlot(str)
    def update_current_task(self, task_description):
        """อัปเดตงานปัจจุบันที่กำลังดำเนินการ"""
        self.current_task_label.setText(f"Current Task: {task_description}")

    @pyqtSlot(str)
    def update_sharepoint_status(self, status):
        """อัปเดตสถานะ SharePoint"""
        self.sharepoint_status_card.set_status(status)

    @pyqtSlot(str)
    def update_database_status(self, status):
        """อัปเดตสถานะ Database"""
        self.database_status_card.set_status(status)

    @pyqtSlot(str)
    def update_last_sync_status(self, status):
        """อัปเดตสถานะการซิงค์ครั้งล่าสุด"""
        self.last_sync_status_card.set_status(status)

    def clear_logs(self):
        """ล้าง logs"""
        self.log_console.clear()
        self.add_log_message("Neural matrix purged - system ready", "info")

    def set_auto_sync_enabled(self, enabled):
        """ตั้งค่า auto sync"""
        self.auto_sync_check.setChecked(enabled)

    def clear_cache(self):
        """ล้างแคชของระบบ"""
        self.add_log_message("Clearing system cache...", "info")
        success = self.controller.clear_system_cache()
        if success:
            self.add_log_message("Cache cleared successfully", "info")
        else:
            self.add_log_message("Failed to clear cache", "error")

    def resizeEvent(self, event):
        """Handle responsive behavior - only if manual adjustments are needed beyond layout stretch factors"""
        super().resizeEvent(event)
