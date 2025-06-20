from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QSizePolicy,
    QGridLayout,
    QCheckBox,
    QComboBox,
)
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont

# ใช้ relative imports
try:
    from ..widgets.status_card import ModernStatusCard
    from ..widgets.cyber_log_console import CyberLogConsole
    from ..widgets.holographic_progress_bar import HolographicProgressBar
    from ..widgets.modern_button import ActionButton
    from ..styles.theme import (
        UltraModernColors,
        get_modern_card_style,
        get_modern_checkbox_style,
    )
except ImportError:
    # Fallback imports
    import sys
    import os

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from ui.widgets.status_card import ModernStatusCard
    from ui.widgets.cyber_log_console import CyberLogConsole
    from ui.widgets.holographic_progress_bar import HolographicProgressBar
    from ui.widgets.modern_button import ActionButton
    from ui.styles.theme import (
        UltraModernColors,
        get_modern_card_style,
        get_modern_checkbox_style,
    )

import logging

logger = logging.getLogger(__name__)


class CompactFrame(QFrame):
    """Compact frame สำหรับพื้นที่จำกัด"""

    def __init__(self, variant="default", parent=None):
        super().__init__(parent)
        self.variant = variant
        self.setup_compact_style()

    def setup_compact_style(self):
        """Apply compact styling"""
        self.setStyleSheet(
            f"""
            QFrame {{
                background: {UltraModernColors.GLASS_BG_DARK};
                border: 1px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 8px;
                margin: 2px;
                padding: 8px;
            }}
            """
        )


class SyncDirectionSelector(QWidget):
    """ตัวเลือกทิศทางการ sync ใหม่"""

    direction_changed = pyqtSignal(
        str
    )  # "spo_to_sql", "sql_to_spo", "excel_to_spo", "excel_to_sql"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        # Direction selector
        direction_label = QLabel("Sync:")
        direction_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        direction_label.setStyleSheet(f"color: {UltraModernColors.TEXT_PRIMARY};")
        layout.addWidget(direction_label)

        self.direction_combo = QComboBox()
        self.direction_combo.addItems(
            ["SPO → SQL", "SQL → SPO", "Excel → SPO", "Excel → SQL"]
        )
        self.direction_combo.setStyleSheet(
            f"""
            QComboBox {{
                background: {UltraModernColors.GLASS_BG};
                border: 1px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 6px;
                padding: 4px 8px;
                color: {UltraModernColors.TEXT_PRIMARY};
                font-size: 9px;
                min-width: 80px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background: {UltraModernColors.GLASS_BG_DARK};
                border: 1px solid {UltraModernColors.NEON_PURPLE};
                selection-background-color: {UltraModernColors.NEON_PURPLE};
            }}
            """
        )
        self.direction_combo.currentTextChanged.connect(self._on_direction_changed)
        layout.addWidget(self.direction_combo)

        layout.addStretch()

    def _on_direction_changed(self, text):
        """Map UI text to direction codes"""
        direction_map = {
            "SPO → SQL": "spo_to_sql",
            "SQL → SPO": "sql_to_spo",
            "Excel → SPO": "excel_to_spo",
            "Excel → SQL": "excel_to_sql",
        }
        direction = direction_map.get(text, "spo_to_sql")
        self.direction_changed.emit(direction)

    def get_current_direction(self):
        """Get current sync direction"""
        direction_map = {
            "SPO → SQL": "spo_to_sql",
            "SQL → SPO": "sql_to_spo",
            "Excel → SPO": "excel_to_spo",
            "Excel → SQL": "excel_to_sql",
        }
        return direction_map.get(self.direction_combo.currentText(), "spo_to_sql")


class ModernDashboard(QWidget):
    """Enhanced Dashboard สำหรับขนาด 900x500"""

    clear_cache_requested = pyqtSignal()
    sync_direction_changed = pyqtSignal(str)

    def __init__(self, controller):
        super().__init__(parent=None)
        self.controller = controller

        # Store references
        self.status_cards = {}
        self.progress_widgets = {}

        self.setup_compact_ui()

    def setup_compact_ui(self):
        """Setup compact dashboard UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # Create compact sections
        main_layout.addLayout(self._create_status_section())
        main_layout.addWidget(self._create_control_section())
        main_layout.addLayout(self._create_progress_section())
        main_layout.addWidget(self._create_log_section())

        self.add_log_message("🚀 Compact Dashboard initialized", "info")

    def _create_status_section(self) -> QHBoxLayout:
        """Compact status cards"""
        layout = QHBoxLayout()
        layout.setSpacing(8)

        # Create compact status cards
        self.status_cards["sharepoint"] = ModernStatusCard("SharePoint", "disconnected")
        self.status_cards["database"] = ModernStatusCard("Database", "disconnected")
        self.status_cards["last_sync"] = ModernStatusCard("Last Sync", "never")

        for card in self.status_cards.values():
            card.setMaximumHeight(85)  # ลดความสูง
            card.setMinimumHeight(85)
            layout.addWidget(card)

        return layout

    def _create_control_section(self) -> QFrame:
        """Compact control panel"""
        control_frame = CompactFrame()
        control_frame.setMaximumHeight(60)  # ลดความสูง
        control_layout = QVBoxLayout(control_frame)
        control_layout.setContentsMargins(10, 8, 10, 8)
        control_layout.setSpacing(6)

        # Top row - Sync direction
        top_row = QHBoxLayout()
        self.sync_direction = SyncDirectionSelector()
        self.sync_direction.direction_changed.connect(self.sync_direction_changed)
        top_row.addWidget(self.sync_direction)

        # Auto sync checkbox
        self.auto_sync_check = QCheckBox("⚡ Auto")
        self.auto_sync_check.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        self.auto_sync_check.setStyleSheet(get_modern_checkbox_style())
        self.auto_sync_check.stateChanged.connect(self.controller.toggle_auto_sync)
        top_row.addWidget(self.auto_sync_check)
        control_layout.addLayout(top_row)

        # Bottom row - Action buttons
        button_row = QHBoxLayout()

        self.run_sync_btn = ActionButton.primary("▶ Sync", size="sm")
        self.run_sync_btn.setMaximumHeight(30)
        self.run_sync_btn.clicked.connect(self._handle_sync_click)

        self.test_connections_btn = ActionButton.ghost("🔧 Test", size="sm")
        self.test_connections_btn.setMaximumHeight(30)
        self.test_connections_btn.clicked.connect(self.controller.test_all_connections)

        self.clear_cache_btn = ActionButton.secondary("🧹 Cache", size="sm")
        self.clear_cache_btn.setMaximumHeight(30)
        self.clear_cache_btn.clicked.connect(self.clear_cache)

        button_row.addWidget(self.run_sync_btn)
        button_row.addWidget(self.test_connections_btn)
        button_row.addWidget(self.clear_cache_btn)
        button_row.addStretch()

        control_layout.addLayout(button_row)

        return control_frame

    def _create_progress_section(self) -> QGridLayout:
        """Compact progress section"""
        grid_layout = QGridLayout()
        grid_layout.setSpacing(8)

        # Progress card
        progress_frame = CompactFrame()
        progress_frame.setMaximumHeight(60)  # ลดความสูง
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(10, 8, 10, 8)
        progress_layout.setSpacing(4)

        # Progress header และ bar ในบรรทัดเดียว
        header_layout = QHBoxLayout()
        progress_header = QLabel("📊 Progress")
        progress_header.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        progress_header.setStyleSheet(f"color: {UltraModernColors.TEXT_PRIMARY};")
        header_layout.addWidget(progress_header)

        # Progress bar
        self.overall_progress_bar = HolographicProgressBar()
        self.overall_progress_bar.setTextVisible(True)
        self.overall_progress_bar.setFixedHeight(18)  # ลดความสูง
        header_layout.addWidget(self.overall_progress_bar, 1)
        progress_layout.addLayout(header_layout)

        # Current task
        self.current_task_label = QLabel("💤 System idle")
        self.current_task_label.setFont(QFont("Segoe UI", 9))
        self.current_task_label.setStyleSheet(
            f"color: {UltraModernColors.TEXT_SECONDARY};"
        )
        progress_layout.addWidget(self.current_task_label)

        grid_layout.addWidget(progress_frame, 0, 0, 1, 2)

        return grid_layout

    def _create_log_section(self) -> QFrame:
        """Compact log console"""
        log_frame = QFrame()
        log_frame.setStyleSheet(
            f"""
            QFrame {{
                background: {UltraModernColors.GLASS_BG_DARK};
                border: 1px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 8px;
                margin: 2px;
            }}
            """
        )

        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(10, 8, 10, 8)
        log_layout.setSpacing(6)

        # Compact log header
        header_layout = QHBoxLayout()

        log_header = QLabel("📋 System Log")
        log_header.setFont(QFont("Segoe UI", 10, QFont.Weight.DemiBold))
        log_header.setStyleSheet(
            f"""
            color: {UltraModernColors.TEXT_PRIMARY};
            background: {UltraModernColors.GLASS_BG};
            padding: 4px 8px;
            border-radius: 4px;
            border: 1px solid {UltraModernColors.NEON_PURPLE};
            """
        )
        header_layout.addWidget(log_header)
        header_layout.addStretch()

        # Clear log button
        clear_log_btn = ActionButton.ghost("🗑️", size="sm")
        clear_log_btn.setMaximumHeight(24)
        clear_log_btn.setMaximumWidth(30)
        clear_log_btn.clicked.connect(self.clear_logs)
        header_layout.addWidget(clear_log_btn)

        log_layout.addLayout(header_layout)

        # Compact log console
        self.log_console = CyberLogConsole()
        self.log_console.setMinimumHeight(90)  # ลดความสูง
        self.log_console.setMaximumHeight(120)
        self.log_console.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

        # Enhanced compact styling
        self.log_console.setStyleSheet(
            f"""
            QTextEdit {{
                background: rgba(0, 0, 0, 0.9);
                border: none;
                border-radius: 6px;
                color: {UltraModernColors.TEXT_PRIMARY};
                padding: 6px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9px;
                line-height: 1.2;
            }}
            QScrollBar:vertical {{
                border: none;
                background: rgba(0, 0, 0, 0.3);
                width: 6px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {UltraModernColors.NEON_PURPLE};
                border-radius: 3px;
                min-height: 15px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {UltraModernColors.NEON_PINK};
            }}
            """
        )

        log_layout.addWidget(self.log_console)

        return log_frame

    def _handle_sync_click(self):
        """Handle sync button click with direction awareness"""
        direction = self.sync_direction.get_current_direction()

        # Set sync direction in controller before starting
        if hasattr(self.controller, "set_sync_direction"):
            self.controller.set_sync_direction(direction)

        # Start sync based on direction
        if direction == "spo_to_sql":
            self.controller.run_full_sync()
        elif direction == "sql_to_spo":
            if hasattr(self.controller, "run_reverse_sync"):
                self.controller.run_reverse_sync()
            else:
                self.add_log_message("⚠️ Reverse sync not yet implemented", "warning")
        elif direction.startswith("excel_"):
            if hasattr(self.controller, "run_excel_import"):
                self.controller.run_excel_import(direction)
            else:
                self.add_log_message("⚠️ Excel import not yet implemented", "warning")

    # Slot methods
    @pyqtSlot(int)
    def update_overall_progress(self, value):
        """Update overall progress"""
        self.overall_progress_bar.setValue(value)
        self.overall_progress_bar.setFormat(f"{value}%")

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

        # ตัดข้อความให้สั้นลงสำหรับ compact UI
        short_task = (
            task_description[:25] + "..."
            if len(task_description) > 25
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

            # แสดงใน current task แทน
            stats_text = f"✅ Complete: {records} records in {duration:.1f}s"
            if errors > 0:
                stats_text = f"⚠️ Done: {records} records, {errors} errors"

            self.current_task_label.setText(stats_text)

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

            logger.info("🧹 Compact Dashboard cleanup completed")
        except Exception as e:
            logger.error(f"Dashboard cleanup error: {e}")


# Compatibility alias
UltraModernDashboard = ModernDashboard
