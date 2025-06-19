from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QCheckBox,
    QSizePolicy,
    QGridLayout,
)
from PyQt6.QtCore import pyqtSignal, pyqtSlot

from ..widgets.status_card import StatusCard
from ..widgets.cyber_log_console import CyberLogConsole
from ..widgets.holographic_progress_bar import HolographicProgressBar
from ..widgets.progress_card import UltraModernProgressCard
from ..styles.theme import (
    UltraModernColors,
    get_ultra_modern_card_style,
    get_gradient_button_style,
    get_neon_checkbox_style,
)
import logging

logger = logging.getLogger(__name__)


class HolographicFrame(QFrame):
    """แก้แล้ว: ลบ shadow effects ที่ทำให้ error"""

    def __init__(self, variant="default", parent=None):
        super().__init__(parent)
        self.variant = variant
        self.setup_holographic_style()

    def setup_holographic_style(self):
        """ใช้ theme system อย่างเดียว"""
        style = get_ultra_modern_card_style(self.variant)
        self.setStyleSheet(style)


class UltraModernDashboard(QWidget):
    """แก้แล้ว: ลด complexity + แยก method ย่อย"""

    clear_cache_requested = pyqtSignal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        # แก้: เก็บ references สำคัญ
        self.status_cards = {}
        self.progress_widgets = {}

        self.setup_ultra_modern_ui()

    def setup_ultra_modern_ui(self):
        """แก้แล้ว: แยกเป็น methods ย่อย"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # สร้าง components แยกกัน
        main_layout.addLayout(self._create_status_cards())
        main_layout.addWidget(self._create_control_panel())
        main_layout.addLayout(self._create_progress_section())
        main_layout.addWidget(self._create_log_section())

        self.add_log_message("🚀 Neural Dashboard online", "info")

    def _create_status_cards(self) -> QHBoxLayout:
        """แก้แล้ว: แยก status cards creation"""
        layout = QHBoxLayout()
        layout.setSpacing(15)

        # สร้าง status cards
        self.status_cards["sharepoint"] = StatusCard(
            "SharePoint Connection", "disconnected"
        )
        self.status_cards["database"] = StatusCard(
            "Database Connection", "disconnected"
        )
        self.status_cards["last_sync"] = StatusCard("Last Sync", "never")

        for card in self.status_cards.values():
            layout.addWidget(card)
            layout.setStretchFactor(card, 1)

        return layout

    def _create_control_panel(self) -> QFrame:
        """แก้แล้ว: แยก control panel creation"""
        control_frame = HolographicFrame(variant="highlight")
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.setSpacing(10)

        # ปุ่มควบคุม
        self.run_sync_button = QPushButton("Initiate Sync")
        self.run_sync_button.setStyleSheet(get_gradient_button_style("primary"))
        self.run_sync_button.clicked.connect(self.controller.run_full_sync)

        self.clear_cache_button = QPushButton("Clear Cache")
        self.clear_cache_button.setStyleSheet(get_gradient_button_style("secondary"))
        self.clear_cache_button.clicked.connect(self.clear_cache)

        self.auto_sync_check = QCheckBox("Auto Sync Enabled")
        self.auto_sync_check.setStyleSheet(get_neon_checkbox_style())
        self.auto_sync_check.stateChanged.connect(self.controller.toggle_auto_sync)

        control_layout.addWidget(self.run_sync_button)
        control_layout.addWidget(self.clear_cache_button)
        control_layout.addStretch(1)
        control_layout.addWidget(self.auto_sync_check)

        return control_frame

    def _create_progress_section(self) -> QGridLayout:
        """แก้แล้ว: แยก progress section creation"""
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)

        # Overall progress
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
        grid_layout.addWidget(progress_frame, 0, 0, 1, 2)

        # Task progress
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
        grid_layout.addWidget(task_frame, 1, 0, 1, 2)

        return grid_layout

    def _create_log_section(self) -> QFrame:
        """แก้แล้ว: แยก log section creation"""
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

        return log_frame

    # แก้แล้ว: ปรับปรุง slot methods
    @pyqtSlot(int)
    def update_overall_progress(self, value):
        """อัปเดตความคืบหน้ารวม"""
        self.overall_progress_bar.setValue(value)
        self.overall_progress_bar.setFormat(f"Overall Progress: {value}%")

    @pyqtSlot(int, int)
    def update_detail_progress(self, current, total):
        """อัปเดตความคืบหน้าของงานย่อย"""
        if hasattr(self.detail_progress_bar, "set_progress"):
            self.detail_progress_bar.set_progress(current, total)

    @pyqtSlot(str, str)
    def add_log_message(self, message, level="info"):
        """เพิ่มข้อความ Log พร้อมเอฟเฟกต์การพิมพ์"""
        self.log_console.add_message_with_typing(message, level)

    @pyqtSlot(str)
    def update_current_task(self, task_description):
        """อัปเดตงานปัจจุบัน"""
        self.current_task_label.setText(f"Current Task: {task_description}")

    # แก้แล้ว: ใช้ status_cards dict
    @pyqtSlot(str)
    def update_sharepoint_status(self, status):
        """อัปเดตสถานะ SharePoint"""
        if "sharepoint" in self.status_cards:
            self.status_cards["sharepoint"].set_status(status)

    @pyqtSlot(str)
    def update_database_status(self, status):
        """อัปเดตสถานะ Database"""
        if "database" in self.status_cards:
            self.status_cards["database"].set_status(status)

    @pyqtSlot(str)
    def update_last_sync_status(self, status):
        """อัปเดตสถานะการซิงค์ครั้งล่าสุด"""
        if "last_sync" in self.status_cards:
            self.status_cards["last_sync"].set_status(status)

    def clear_logs(self):
        """ล้าง logs"""
        self.log_console.clear()
        self.add_log_message("🧹 Neural matrix purged - system ready", "info")

    def set_auto_sync_enabled(self, enabled):
        """ตั้งค่า auto sync"""
        self.auto_sync_check.setChecked(enabled)

    def clear_cache(self):
        """ล้างแคชของระบบ"""
        self.add_log_message("🧹 Clearing system cache...", "info")
        try:
            success = self.controller.clear_system_cache()
            if success:
                self.add_log_message("✅ Cache cleared successfully", "info")
            else:
                self.add_log_message("❌ Failed to clear cache", "error")
        except Exception as e:
            self.add_log_message(f"❌ Cache clear error: {str(e)}", "error")
            logger.error(f"Cache clear error: {e}")

    def cleanup(self):
        """แก้แล้ว: cleanup resources"""
        try:
            # หยุด animations ใน status cards
            for card in self.status_cards.values():
                if hasattr(card, "cleanup_animations"):
                    card.cleanup_animations()

            # หยุด timer ใน log console
            if hasattr(self.log_console, "typing_timer"):
                self.log_console.typing_timer.stop()

            logger.info("🧹 Dashboard cleanup completed")
        except Exception as e:
            logger.error(f"Dashboard cleanup error: {e}")
