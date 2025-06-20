from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QSizePolicy,
    QGridLayout,
    QCheckBox,
)
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont

from ..widgets.status_card import ModernStatusCard
from ..widgets.cyber_log_console import CyberLogConsole
from ..widgets.holographic_progress_bar import HolographicProgressBar
from ..widgets.modern_button import ActionButton
from ..styles.theme import (
    UltraModernColors,
    get_modern_card_style,
    get_modern_checkbox_style,
)
import logging

logger = logging.getLogger(__name__)


class ModernFrame(QFrame):
    """Modern frame with glassmorphism effect"""

    def __init__(self, variant="default", parent=None):
        super().__init__(parent)
        self.variant = variant
        self.setup_modern_style()

    def setup_modern_style(self):
        """Apply modern styling"""
        self.setStyleSheet(get_modern_card_style(self.variant))


class ModernDashboard(QWidget):
    """แก้แล้ว: Modern Dashboard ที่ดูดีขึ้น"""

    clear_cache_requested = pyqtSignal()

    def __init__(self, controller):
        super().__init__(parent=None)
        self.controller = controller

        # Store references
        self.status_cards = {}
        self.progress_widgets = {}

        self.setup_modern_ui()

    def setup_modern_ui(self):
        """แก้แล้ว: Setup modern dashboard UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Create sections
        main_layout.addLayout(self._create_status_section())
        main_layout.addWidget(self._create_control_section())
        main_layout.addLayout(self._create_progress_section())
        main_layout.addWidget(self._create_log_section())

        self.add_log_message("🚀 Modern Dashboard initialized", "info")

    def _create_status_section(self) -> QHBoxLayout:
        """แก้แล้ว: Status cards section"""
        layout = QHBoxLayout()
        layout.setSpacing(12)

        # Create modern status cards
        self.status_cards["sharepoint"] = ModernStatusCard("SharePoint", "disconnected")
        self.status_cards["database"] = ModernStatusCard("Database", "disconnected")
        self.status_cards["last_sync"] = ModernStatusCard("Last Sync", "never")

        for card in self.status_cards.values():
            card.setMaximumHeight(110)
            layout.addWidget(card)

        return layout

    def _create_control_section(self) -> QFrame:
        """แก้แล้ว: Control panel section"""
        control_frame = ModernFrame(variant="highlight")
        control_frame.setMaximumHeight(70)
        control_layout = QHBoxLayout(control_frame)
        control_layout.setContentsMargins(20, 15, 20, 15)
        control_layout.setSpacing(15)

        # Action buttons
        self.run_sync_btn = ActionButton.primary("🚀 Start Sync", size="sm")
        self.run_sync_btn.clicked.connect(self.controller.run_full_sync)

        self.clear_cache_btn = ActionButton.secondary("🧹 Clear Cache", size="sm")
        self.clear_cache_btn.clicked.connect(self.clear_cache)

        self.test_connections_btn = ActionButton.ghost("🔧 Test All", size="sm")
        self.test_connections_btn.clicked.connect(self.controller.test_all_connections)

        control_layout.addWidget(self.run_sync_btn)
        control_layout.addWidget(self.clear_cache_btn)
        control_layout.addWidget(self.test_connections_btn)
        control_layout.addStretch(1)

        # Auto sync toggle
        self.auto_sync_check = QCheckBox("⚡ Auto Sync")
        self.auto_sync_check.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.auto_sync_check.setStyleSheet(get_modern_checkbox_style())
        self.auto_sync_check.stateChanged.connect(self.controller.toggle_auto_sync)
        control_layout.addWidget(self.auto_sync_check)

        return control_frame

    def _create_progress_section(self) -> QGridLayout:
        """แก้แล้ว: Progress monitoring section"""
        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)

        # Overall progress card
        progress_frame = ModernFrame()
        progress_frame.setMaximumHeight(90)
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(20, 12, 20, 12)
        progress_layout.setSpacing(8)

        # Progress header
        progress_header = QLabel("📊 Sync Progress")
        progress_header.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        progress_header.setStyleSheet(f"color: {UltraModernColors.TEXT_PRIMARY};")
        progress_layout.addWidget(progress_header)

        # Progress bar
        self.overall_progress_bar = HolographicProgressBar()
        self.overall_progress_bar.setTextVisible(True)
        self.overall_progress_bar.setFixedHeight(24)
        progress_layout.addWidget(self.overall_progress_bar)

        # Current task label
        self.current_task_label = QLabel("💤 System idle")
        self.current_task_label.setFont(QFont("Segoe UI", 10))
        self.current_task_label.setStyleSheet(
            f"color: {UltraModernColors.TEXT_SECONDARY}; margin-top: 4px;"
        )
        progress_layout.addWidget(self.current_task_label)

        grid_layout.addWidget(progress_frame, 0, 0, 1, 2)

        # Statistics card
        stats_frame = ModernFrame()
        stats_frame.setMaximumHeight(70)
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setContentsMargins(20, 12, 20, 12)
        stats_layout.setSpacing(8)

        stats_header = QLabel("📈 Statistics")
        stats_header.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        stats_header.setStyleSheet(f"color: {UltraModernColors.TEXT_PRIMARY};")
        stats_layout.addWidget(stats_header)

        self.stats_label = QLabel("Ready to sync")
        self.stats_label.setFont(QFont("Segoe UI", 10))
        self.stats_label.setStyleSheet(f"color: {UltraModernColors.TEXT_SECONDARY};")
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)

        grid_layout.addWidget(stats_frame, 1, 0, 1, 2)

        return grid_layout

    def _create_log_section(self) -> QFrame:
        """แก้แล้ว: Log console section ที่ดูดีขึ้น"""
        log_frame = QFrame()
        # แก้: ใช้ style ที่ดูดีกว่า
        log_frame.setStyleSheet(
            f"""
            QFrame {{
                background: {UltraModernColors.GLASS_BG_DARK};
                border: 2px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 16px;
                margin: 5px;
            }}
            """
        )

        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(20, 15, 20, 15)
        log_layout.setSpacing(10)

        # Log header with controls
        header_layout = QHBoxLayout()

        log_header = QLabel("📋 System Log")
        log_header.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        log_header.setStyleSheet(
            f"""
            color: {UltraModernColors.TEXT_PRIMARY};
            background: {UltraModernColors.GLASS_BG};
            padding: 8px 16px;
            border-radius: 8px;
            border: 1px solid {UltraModernColors.NEON_PURPLE};
            """
        )
        header_layout.addWidget(log_header)

        header_layout.addStretch()

        # Clear log button
        clear_log_btn = ActionButton.ghost("🗑️ Clear", size="sm")
        clear_log_btn.clicked.connect(self.clear_logs)
        header_layout.addWidget(clear_log_btn)

        log_layout.addLayout(header_layout)

        # แก้: Log console ที่ดูดีขึ้น
        log_container = QFrame()
        log_container.setStyleSheet(
            f"""
            QFrame {{
                background: rgba(0, 0, 0, 0.8);
                border: 1px solid {UltraModernColors.NEON_BLUE};
                border-radius: 12px;
                margin: 5px;
            }}
            """
        )

        log_container_layout = QVBoxLayout(log_container)
        log_container_layout.setContentsMargins(10, 10, 10, 10)

        self.log_console = CyberLogConsole()
        self.log_console.setMinimumHeight(140)
        self.log_console.setMaximumHeight(200)
        self.log_console.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        # แก้: ปรับ style ของ log console
        self.log_console.setStyleSheet(
            f"""
            QTextEdit {{
                background: rgba(0, 0, 0, 0.9);
                border: none;
                border-radius: 8px;
                color: {UltraModernColors.TEXT_PRIMARY};
                padding: 12px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10px;
                selection-background-color: {UltraModernColors.NEON_PURPLE};
            }}
            QScrollBar:vertical {{
                border: none;
                background: rgba(0, 0, 0, 0.3);
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {UltraModernColors.NEON_PURPLE};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {UltraModernColors.NEON_PINK};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: none;
                border: none;
            }}
            """
        )

        log_container_layout.addWidget(self.log_console)
        log_layout.addWidget(log_container)

        return log_frame

    # Slot methods
    @pyqtSlot(int)
    def update_overall_progress(self, value):
        """Update overall progress"""
        self.overall_progress_bar.setValue(value)
        self.overall_progress_bar.setFormat(f"Progress: {value}%")

    @pyqtSlot(str, str)
    def add_log_message(self, message, level="info"):
        """Add log message with typing effect"""
        self.log_console.add_message_with_typing(message, level)

    @pyqtSlot(str)
    def update_current_task(self, task_description):
        """Update current task display"""
        icon_map = {
            "Idle": "💤",
            "Connecting": "🔗",
            "Downloading": "⬇️",
            "Processing": "⚙️",
            "Saving": "💾",
            "Completed": "✅",
        }

        # Extract task type for icon
        task_type = task_description.split()[0] if task_description else "Idle"
        icon = icon_map.get(task_type, "⚙️")

        # ตัดข้อความให้สั้นลง
        short_task = (
            task_description[:40] + "..."
            if len(task_description) > 40
            else task_description
        )
        self.current_task_label.setText(f"{icon} {short_task}")

    # Status update methods
    @pyqtSlot(str)
    def update_sharepoint_status(self, status):
        """Update SharePoint status"""
        if "sharepoint" in self.status_cards:
            self.status_cards["sharepoint"].set_status(status)

    @pyqtSlot(str)
    def update_database_status(self, status):
        """Update database status"""
        if "database" in self.status_cards:
            self.status_cards["database"].set_status(status)

    @pyqtSlot(str)
    def update_last_sync_status(self, status):
        """Update last sync status"""
        if "last_sync" in self.status_cards:
            self.status_cards["last_sync"].set_status(status)

    @pyqtSlot(bool)
    def set_auto_sync_enabled(self, enabled):
        """Set auto sync checkbox state"""
        self.auto_sync_check.setChecked(enabled)

    def update_statistics(self, stats):
        """Update statistics display"""
        if stats:
            records = stats.get("records_inserted", 0)
            duration = stats.get("duration", 0)
            errors = stats.get("errors", 0)

            stats_text = f"Records: {records} • Duration: {duration:.1f}s"
            if errors > 0:
                stats_text += f" • Errors: {errors}"

            self.stats_label.setText(stats_text)

    def clear_logs(self):
        """Clear log console"""
        self.log_console.clear()
        self.add_log_message("🧹 Log console cleared", "info")

    def clear_cache(self):
        """Clear system cache"""
        self.add_log_message("🧹 Clearing system cache...", "info")
        try:
            success = self.controller.clear_system_cache()
            if success:
                self.add_log_message("✅ Cache cleared successfully", "success")
            else:
                self.add_log_message("❌ Failed to clear cache", "error")
        except Exception as e:
            self.add_log_message(f"❌ Cache clear error: {str(e)}", "error")
            logger.error(f"Cache clear error: {e}")

    def cleanup(self):
        """Cleanup resources"""
        try:
            # Stop animations in status cards
            for card in self.status_cards.values():
                if hasattr(card, "cleanup_animations"):
                    card.cleanup_animations()

            # Stop typing timer in log console
            if hasattr(self.log_console, "typing_timer"):
                self.log_console.typing_timer.stop()

            logger.info("🧹 Modern Dashboard cleanup completed")
        except Exception as e:
            logger.error(f"Dashboard cleanup error: {e}")


# Compatibility alias
UltraModernDashboard = ModernDashboard
