from PyQt6.QtWidgets import QComboBox
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QFont  # Import QFont for consistency with other widgets

from ..styles.theme import UltraModernColors, get_ultra_modern_input_style


class HolographicComboBox(QComboBox):
    """แก้แล้ว: ลบ shadow effects เพื่อป้องกัน import error"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(get_ultra_modern_input_style())
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(
            QFont("Segoe UI", 14, QFont.Weight.Normal)
        )  # Set font for consistency

        # แก้: ลบ shadow effects ที่ทำให้เกิด import error
        self.hover_animation = QPropertyAnimation(self, b"pos")
        self.hover_animation.setDuration(150)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

    def enterEvent(self, event):
        """แก้แล้ว: ลบ shadow effects"""
        super().enterEvent(event)

        if self.hover_animation.state() == QPropertyAnimation.State.Running:
            self.hover_animation.stop()

        current_pos = self.pos()
        target_pos = current_pos - QPoint(0, 2)
        self.hover_animation.setStartValue(current_pos)
        self.hover_animation.setEndValue(target_pos)
        self.hover_animation.start()

    def leaveEvent(self, event):
        """แก้แล้ว: ลบ shadow effects"""
        super().leaveEvent(event)

        if self.hover_animation.state() == QPropertyAnimation.State.Running:
            self.hover_animation.stop()

        current_pos = self.pos()
        target_pos = current_pos + QPoint(0, 2)
        self.hover_animation.setStartValue(current_pos)
        self.hover_animation.setEndValue(target_pos)
        self.hover_animation.start()

    def focusInEvent(self, event):
        """แก้แล้ว: focus styling อย่างเดียว"""
        super().focusInEvent(event)
        # Apply focus style with a distinct border color
        self.setStyleSheet(
            get_ultra_modern_input_style()
            + f"QComboBox {{ border: 2px solid {UltraModernColors.NEON_PURPLE}; }}"
            + f"QComboBox::drop-down {{ border-color: {UltraModernColors.NEON_PURPLE}; }}"  # Also highlight dropdown arrow
        )

    def focusOutEvent(self, event):
        """แก้แล้ว: reset styling"""
        super().focusOutEvent(event)
        # Reset to default style when focus is lost
        self.setStyleSheet(get_ultra_modern_input_style())
