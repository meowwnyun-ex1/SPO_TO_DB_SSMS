from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QFont, QColor, QPainter

from ..styles.theme import UltraModernColors, get_ultra_modern_card_style


class StatusIndicator(QWidget):
    """ไฟแสดงสถานะวงกลมพร้อมสีและเอฟเฟกต์"""

    def __init__(self, status="disconnected", parent=None):
        super().__init__(parent)
        self.status = status
        self.setFixedSize(16, 16)
        self.pulse_strength = 0.0
        self.pulse_direction = 1

    def paintEvent(self, event):
        """วาดวงกลมแสดงสถานะ"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        colors = {
            "connected": "#7CFC00",  # SUCCESS_COLOR
            "disconnected": "#FF6347",  # ERROR_COLOR
            "error": "#FF6347",
            "success": "#7CFC00",
            "never": "#C0C0C0",  # TEXT_SECONDARY
            "syncing": "#87CEEB",  # NEON_BLUE
            "warning": "#FFFF99",  # NEON_YELLOW
            "in_progress": "#8A2BE2",  # NEON_PURPLE
        }

        color_str = colors.get(self.status, colors["disconnected"])
        # แก้: แปลง string เป็น QColor
        color = QColor(color_str)
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(self.rect())

    def set_status(self, new_status):
        """ตั้งค่าสถานะใหม่"""
        if self.status != new_status:
            self.status = new_status
            self.update()
        else:
            self.update()


class StatusCard(QWidget):
    """การ์ดแสดงสถานะแบบ Ultra Modern"""

    def __init__(self, title, status="disconnected", parent=None):
        super().__init__(parent)
        self.title = title
        self.status = status
        self.description = ""

        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self._animate_pulse)
        self.pulse_strength = 0.0
        self.pulse_direction = 1

        self.hover_animation = QPropertyAnimation(self, b"pos")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.setup_ui()
        self.update_status_display()

    def setup_ui(self):
        """ตั้งค่า UI ของการ์ดสถานะ"""
        self.outer_frame = QFrame(self)
        self.outer_frame.setStyleSheet(get_ultra_modern_card_style("default"))

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.outer_frame)

        card_layout = QHBoxLayout(self.outer_frame)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(10)

        self.indicator = StatusIndicator(self.status, self)
        card_layout.addWidget(self.indicator)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Inter", 12, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"color: {UltraModernColors.TEXT_PRIMARY};")
        text_layout.addWidget(self.title_label)

        self.description_label = QLabel(
            self.description or "Status details will appear here."
        )
        self.description_label.setFont(QFont("Inter", 10))
        self.description_label.setStyleSheet(
            f"color: {UltraModernColors.TEXT_SECONDARY};"
        )
        text_layout.addWidget(self.description_label)

        card_layout.addLayout(text_layout)
        card_layout.addStretch(1)

        self.indicator_symbol = QLabel("")
        self.indicator_symbol.setFont(QFont("Segoe UI", 24))
        self.indicator_symbol.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.indicator_symbol.setStyleSheet(f"color: {UltraModernColors.NEON_PURPLE};")
        card_layout.addWidget(self.indicator_symbol)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    def update_status_display(self):
        """อัปเดตการแสดงผลสถานะของการ์ด"""
        config = {
            "connected": {
                "symbol": "✔",
                "color": UltraModernColors.SUCCESS_COLOR,
            },
            "disconnected": {
                "symbol": "✖",
                "color": UltraModernColors.ERROR_COLOR,
            },
            "error": {
                "symbol": "❗",
                "color": UltraModernColors.ERROR_COLOR,
            },
            "success": {
                "symbol": "✔",
                "color": UltraModernColors.SUCCESS_COLOR,
            },
            "never": {
                "symbol": "…",
                "color": UltraModernColors.TEXT_SECONDARY,
            },
            "syncing": {
                "symbol": "⟳",
                "color": UltraModernColors.NEON_BLUE,
            },
            "warning": {
                "symbol": "⚠",
                "color": UltraModernColors.NEON_YELLOW,
            },
            "in_progress": {
                "symbol": "⟳",
                "color": UltraModernColors.NEON_PURPLE,
            },
        }

        current_config = config.get(self.status, config["disconnected"])
        self.indicator.set_status(self.status)
        self.indicator_symbol.setText(current_config["symbol"])
        self.indicator_symbol.setStyleSheet(f"color: {current_config['color']};")

        # Handle description based on status
        status_descriptions = {
            "connected": "Online and operational.",
            "disconnected": "Offline or connection lost.",
            "error": "An error occurred during operation.",
            "success": "Operation completed successfully.",
            "never": "No previous operations recorded.",
            "syncing": "Synchronization in progress...",
            "warning": "Operation completed with warnings.",
            "in_progress": "Operation ongoing...",
        }

        self.description_label.setText(
            status_descriptions.get(self.status, "Status unknown.")
        )

        # Start/Stop pulse animation
        if self.status == "in_progress" or self.status == "syncing":
            if not self.pulse_timer.isActive():
                self.pulse_strength = 0.0
                self.pulse_direction = 1
                self.pulse_timer.start(50)
        else:
            if self.pulse_timer and self.pulse_timer.isActive():
                self.pulse_timer.stop()
                self.indicator_symbol.setStyleSheet(
                    f"color: {current_config['color']};"
                )
        self.outer_frame.update()

    def set_status(self, status):
        """ตั้งค่าสถานะของการ์ดและอัปเดตการแสดงผล"""
        if self.status != status:
            self.status = status
            self.update_status_display()

    def _animate_pulse(self):
        """Animate the glow effect for 'in_progress' or 'syncing' status."""
        self.pulse_strength += self.pulse_direction * 0.05
        if self.pulse_strength > 1.0:
            self.pulse_strength = 1.0
            self.pulse_direction = -1
        elif self.pulse_strength < 0.0:
            self.pulse_strength = 0.0
            self.pulse_direction = 1

        symbol_config = {
            "syncing": UltraModernColors.NEON_BLUE,
            "in_progress": UltraModernColors.NEON_PURPLE,
        }
        color = symbol_config.get(self.status, UltraModernColors.NEON_PURPLE)

        self.indicator_symbol.setStyleSheet(f"color: {color};")
        self.outer_frame.update()

    def enterEvent(self, event):
        """Handle mouse hover enter event."""
        super().enterEvent(event)
        current_pos = self.pos()
        target_pos = current_pos + QPoint(0, -5)
        self.hover_animation.setStartValue(current_pos)
        self.hover_animation.setEndValue(target_pos)
        self.hover_animation.start()

    def leaveEvent(self, event):
        """Handle mouse hover leave event."""
        super().leaveEvent(event)
        current_pos = self.pos()
        target_pos = current_pos - QPoint(0, -5)
        self.hover_animation.setStartValue(current_pos)
        self.hover_animation.setEndValue(target_pos)
        self.hover_animation.start()

    def cleanup_animations(self):
        """ทำความสะอาด animations"""
        if hasattr(self, "pulse_timer"):
            self.pulse_timer.stop()
        if hasattr(self, "hover_animation"):
            self.hover_animation.stop()


# Backward compatibility
class UltraModernStatusCard(StatusCard):
    """Alias for backward compatibility"""

    pass
