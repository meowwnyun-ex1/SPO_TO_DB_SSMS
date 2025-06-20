# ui/widgets/status_card.py - Compact Status Card Widget
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QPainter
from typing import Any
import logging

try:
    from ..styles.theme import UltraModernColors, get_modern_card_style, CompactScaling
except ImportError:
    # Fallback if import fails
    class UltraModernColors:
        GLASS_BG_DARK = "rgba(10, 10, 10, 0.92)"
        GLASS_BG_LIGHT = "rgba(25, 25, 25, 0.75)"
        GLASS_BORDER = "rgba(255, 255, 255, 0.15)"
        TEXT_PRIMARY = "#E0E0E0"
        TEXT_SECONDARY = "#A0A0A0"
        TEXT_SECONDARY_ALT = "#707070"
        SUCCESS_COLOR = "#00FF7F"
        ERROR_COLOR = "#FF6347"
        WARNING_COLOR = "#FFD700"
        NEON_BLUE = "#00D4FF"
        NEON_PURPLE = "#9D4EDD"
        NEON_GREEN = "#00F5A0"
        NEON_PINK = "#FF006E"
        NEON_YELLOW = "#FFD23F"

    class CompactScaling:
        FONT_SIZE_TINY = 7
        FONT_SIZE_SMALL = 8
        FONT_SIZE_NORMAL = 9
        STATUS_CARD_HEIGHT = 40

    def get_modern_card_style():
        return ""


logger = logging.getLogger(__name__)


class UltraCompactStatusIndicator(QWidget):
    """Ultra-compact status indicator dot"""

    def __init__(self, status="disconnected", parent=None):
        super().__init__(parent)
        self.status = status
        self.setFixedSize(12, 12)  # Smaller for ultra-compact layout

    def paintEvent(self, event):
        """Paint compact status dot"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        colors = {
            "connected": UltraModernColors.SUCCESS_COLOR,
            "disconnected": UltraModernColors.ERROR_COLOR,
            "error": UltraModernColors.ERROR_COLOR,
            "success": UltraModernColors.SUCCESS_COLOR,
            "never": "#666666",
            "syncing": UltraModernColors.NEON_BLUE,
            "warning": UltraModernColors.WARNING_COLOR,
            "in_progress": UltraModernColors.NEON_PURPLE,
            "connecting": UltraModernColors.NEON_YELLOW,
            "failed": UltraModernColors.ERROR_COLOR,
        }

        color = QColor(colors.get(self.status, UltraModernColors.TEXT_SECONDARY_ALT))

        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)

        # Draw filled circle
        rect = self.rect().adjusted(2, 2, -2, -2)
        painter.drawEllipse(rect)

        # Add pulse effect for active states
        if self.status in ["connecting", "syncing", "in_progress"]:
            # Simple pulsing ring
            painter.setBrush(Qt.BrushStyle.NoBrush)
            pen = painter.pen()
            pen.setColor(color)
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawEllipse(self.rect().adjusted(1, 1, -1, -1))

    def set_status(self, status: str):
        """Set status and trigger repaint"""
        if self.status != status:
            self.status = status
            self.update()


class ModernStatusCard(QWidget):
    """
    Ultra-compact status card optimized for 900x500 display.
    Single line layout with minimal height.
    """

    def __init__(
        self,
        title: str,
        initial_status: Any,
        is_boolean_status: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.title = title
        self._status = initial_status
        self.is_boolean_status = is_boolean_status
        self.pulse_animation = None

        self._setup_ui()
        self.update_status_display()

    def _setup_ui(self):
        """Setup ultra-compact card layout"""
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(6, 4, 6, 4)  # Minimal margins
        self.main_layout.setSpacing(6)

        # Apply compact card styling
        self.setStyleSheet(
            f"""
            QWidget {{
                background: {UltraModernColors.GLASS_BG_DARK};
                border: 1px solid {UltraModernColors.GLASS_BORDER};
                border-radius: 4px;
                min-height: {CompactScaling.STATUS_CARD_HEIGHT}px;
                max-height: {CompactScaling.STATUS_CARD_HEIGHT}px;
            }}
            QWidget:hover {{
                border-color: {UltraModernColors.NEON_BLUE};
                background: {UltraModernColors.GLASS_BG_LIGHT};
            }}
        """
        )

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Title label - compact font
        self.title_label = QLabel(self.title)
        self.title_label.setFont(
            QFont("Segoe UI", CompactScaling.FONT_SIZE_SMALL, QFont.Weight.Normal)
        )
        self.title_label.setStyleSheet(
            f"color: {UltraModernColors.TEXT_PRIMARY}; border: none; background: transparent;"
        )
        self.main_layout.addWidget(self.title_label)

        self.main_layout.addStretch(1)  # Push status to right

        # Status label - compact
        self.status_label = QLabel()
        self.status_label.setFont(
            QFont("Segoe UI", CompactScaling.FONT_SIZE_SMALL, QFont.Weight.Bold)
        )
        self.status_label.setStyleSheet("border: none; background: transparent;")
        self.main_layout.addWidget(self.status_label)

        # Status indicator dot
        self.status_indicator = UltraCompactStatusIndicator(
            self.current_status_string()
        )
        self.main_layout.addWidget(self.status_indicator)

    def current_status_string(self) -> str:
        """Convert status to string representation"""
        if self.is_boolean_status:
            return "connected" if self._status else "disconnected"
        return str(self._status) if self._status else "never"

    def update_status_display(self):
        """Update status display with compact styling"""
        status_str = self.current_status_string()

        # Status text and colors
        status_configs = {
            "connected": ("✓", UltraModernColors.SUCCESS_COLOR),
            "disconnected": ("✗", UltraModernColors.ERROR_COLOR),
            "error": ("!", UltraModernColors.ERROR_COLOR),
            "success": ("✓", UltraModernColors.SUCCESS_COLOR),
            "never": ("-", UltraModernColors.TEXT_SECONDARY_ALT),
            "syncing": ("⟳", UltraModernColors.NEON_PURPLE),
            "warning": ("⚠", UltraModernColors.WARNING_COLOR),
            "in_progress": ("⟳", UltraModernColors.NEON_PURPLE),
            "connecting": ("⟳", UltraModernColors.NEON_YELLOW),
            "failed": ("✗", UltraModernColors.ERROR_COLOR),
        }

        symbol, color = status_configs.get(
            status_str, ("?", UltraModernColors.TEXT_SECONDARY)
        )

        # Update status label with symbol and color
        self.status_label.setStyleSheet(
            f"color: {color}; border: none; background: transparent;"
        )
        self.status_label.setText(symbol)

        # Update status indicator
        self.status_indicator.set_status(status_str)

        # Update card border color based on status
        border_color = (
            color if status_str != "never" else UltraModernColors.GLASS_BORDER
        )
        self.setStyleSheet(
            f"""
            QWidget {{
                background: {UltraModernColors.GLASS_BG_DARK};
                border: 1px solid {border_color};
                border-radius: 4px;
                min-height: {CompactScaling.STATUS_CARD_HEIGHT}px;
                max-height: {CompactScaling.STATUS_CARD_HEIGHT}px;
            }}
            QWidget:hover {{
                border-color: {UltraModernColors.NEON_BLUE};
                background: {UltraModernColors.GLASS_BG_LIGHT};
            }}
        """
        )

        # Manage pulse animation for active states
        if status_str in ["connecting", "in_progress", "syncing"]:
            self._start_pulse_animation()
        else:
            self._stop_pulse_animation()

    def set_status(self, status: Any):
        """Set new status and update display"""
        if self.is_boolean_status:
            # Convert various boolean representations
            if isinstance(status, str):
                self._status = status.lower() in (
                    "true",
                    "1",
                    "yes",
                    "on",
                    "connected",
                    "enabled",
                )
            else:
                self._status = bool(status)
        else:
            self._status = status

        self.update_status_display()

    def _start_pulse_animation(self):
        """Start subtle pulse animation for active states"""
        if self.pulse_animation:
            return  # Already running

        try:
            self.pulse_animation = QPropertyAnimation(self, b"styleSheet")
            self.pulse_animation.setDuration(2000)  # 2 second cycle
            self.pulse_animation.setLoopCount(-1)  # Infinite loop
            self.pulse_animation.setEasingCurve(QEasingCurve.Type.InOutSine)

            # Animate border color opacity
            base_style = f"""
                QWidget {{
                    background: {UltraModernColors.GLASS_BG_DARK};
                    border: 1px solid {UltraModernColors.NEON_PURPLE};
                    border-radius: 4px;
                    min-height: {CompactScaling.STATUS_CARD_HEIGHT}px;
                    max-height: {CompactScaling.STATUS_CARD_HEIGHT}px;
                }}
            """

            bright_style = f"""
                QWidget {{
                    background: {UltraModernColors.GLASS_BG_LIGHT};
                    border: 2px solid {UltraModernColors.NEON_PURPLE};
                    border-radius: 4px;
                    min-height: {CompactScaling.STATUS_CARD_HEIGHT}px;
                    max-height: {CompactScaling.STATUS_CARD_HEIGHT}px;
                }}
            """

            self.pulse_animation.setKeyValueAt(0, base_style)
            self.pulse_animation.setKeyValueAt(0.5, bright_style)
            self.pulse_animation.setKeyValueAt(1, base_style)

            self.pulse_animation.start()

        except Exception as e:
            logger.debug(f"Error starting pulse animation: {e}")

    def _stop_pulse_animation(self):
        """Stop pulse animation"""
        if self.pulse_animation:
            try:
                self.pulse_animation.stop()
                self.pulse_animation.deleteLater()
                self.pulse_animation = None
                # Reset to normal styling
                self.update_status_display()
            except Exception as e:
                logger.debug(f"Error stopping pulse animation: {e}")

    def cleanup_animations(self):
        """Cleanup animations"""
        self._stop_pulse_animation()

    def enterEvent(self, event):
        """Handle mouse enter - show tooltip with detailed status"""
        super().enterEvent(event)
        try:
            # Create detailed tooltip
            status_str = self.current_status_string()
            detailed_status = {
                "connected": "Connection established",
                "disconnected": "Not connected",
                "error": "Connection error",
                "success": "Operation successful",
                "never": "Never attempted",
                "syncing": "Synchronization in progress",
                "warning": "Warning condition",
                "in_progress": "Operation in progress",
                "connecting": "Attempting connection",
                "failed": "Operation failed",
            }

            tooltip = f"{self.title}: {detailed_status.get(status_str, status_str)}"
            self.setToolTip(tooltip)

        except Exception as e:
            logger.debug(f"Error setting tooltip: {e}")

    def leaveEvent(self, event):
        """Handle mouse leave"""
        super().leaveEvent(event)


class StatusCardGroup(QWidget):
    """Group of status cards in compact grid layout"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.status_cards = {}
        self._setup_ui()

    def _setup_ui(self):
        """Setup grid layout for status cards"""
        from PyQt6.QtWidgets import QGridLayout

        self.grid_layout = QGridLayout(self)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(4)  # Minimal spacing

    def add_status_card(
        self,
        card_id: str,
        title: str,
        initial_status: Any,
        row: int,
        col: int,
        is_boolean: bool = False,
    ):
        """Add status card to grid"""
        try:
            card = ModernStatusCard(title, initial_status, is_boolean)
            self.status_cards[card_id] = card
            self.grid_layout.addWidget(card, row, col)
            logger.debug(f"Added status card: {card_id} at ({row}, {col})")
        except Exception as e:
            logger.error(f"Error adding status card '{card_id}': {e}")

    def update_status(self, card_id: str, status: Any):
        """Update specific status card"""
        try:
            if card_id in self.status_cards:
                self.status_cards[card_id].set_status(status)
        except Exception as e:
            logger.debug(f"Error updating status card '{card_id}': {e}")

    def get_status_card(self, card_id: str) -> ModernStatusCard:
        """Get status card by ID"""
        return self.status_cards.get(card_id)

    def cleanup(self):
        """Cleanup all status cards"""
        try:
            for card in self.status_cards.values():
                if hasattr(card, "cleanup_animations"):
                    card.cleanup_animations()
                card.deleteLater()
            self.status_cards.clear()
        except Exception as e:
            logger.error(f"Error during status card group cleanup: {e}")


# Backward compatibility - compact status display helper
class CompactStatusDisplay(QWidget):
    """Ultra-compact status display for tight spaces"""

    def __init__(self, statuses: dict, parent=None):
        super().__init__(parent)
        self.statuses = statuses
        self._setup_ui()

    def _setup_ui(self):
        """Setup ultra-compact horizontal status display"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)

        self.indicators = {}

        for status_id, (label, initial_value) in self.statuses.items():
            # Mini label
            label_widget = QLabel(label)
            label_widget.setFont(QFont("Segoe UI", CompactScaling.FONT_SIZE_TINY))
            label_widget.setStyleSheet(f"color: {UltraModernColors.TEXT_SECONDARY};")

            # Mini indicator
            indicator = UltraCompactStatusIndicator(initial_value)

            self.indicators[status_id] = indicator

            layout.addWidget(label_widget)
            layout.addWidget(indicator)

        layout.addStretch(1)
        self.setMaximumHeight(20)  # Ultra-compact height

    def update_status(self, status_id: str, status: str):
        """Update mini status indicator"""
        if status_id in self.indicators:
            self.indicators[status_id].set_status(status)
