from PyQt6.QtWidgets import QComboBox
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint

from ..styles.theme import UltraModernColors, get_ultra_modern_input_style


class HolographicComboBox(QComboBox):
    """
    A custom QComboBox with holographic styling and interactive effects.
    QComboBox ที่ปรับแต่งด้วยสไตล์ holographic และเอฟเฟกต์แบบโต้ตอบ
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(get_ultra_modern_input_style())
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # Indicate clickable

        # Drop shadow for a more "floating" look
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(15)
        self.shadow_effect.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(self.shadow_effect)

        # Animation for focus/hover effect
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)

    def enterEvent(self, event):
        """Handle mouse hover enter event."""
        super().enterEvent(event)
        # Subtle lift effect
        current_pos = self.pos()
        target_pos = current_pos - QPoint(0, 2)
        self.animation.setStartValue(current_pos)
        self.animation.setEndValue(target_pos)
        self.animation.start()
        # Enhance shadow
        self.shadow_effect.setBlurRadius(20)
        self.shadow_effect.setColor(QColor(UltraModernColors.NEON_BLUE).darker(100))

    def leaveEvent(self, event):
        """Handle mouse hover leave event."""
        super().leaveEvent(event)
        # Return to original position
        current_pos = self.pos()
        target_pos = current_pos + QPoint(0, 2)
        self.animation.setStartValue(current_pos)
        self.animation.setEndValue(target_pos)
        self.animation.start()
        # Reset shadow
        self.shadow_effect.setBlurRadius(15)
        self.shadow_effect.setColor(QColor(0, 0, 0, 100))

    def focusInEvent(self, event):
        """Handle focus in event."""
        super().focusInEvent(event)
        self.setStyleSheet(
            get_ultra_modern_input_style()
            + f"QComboBox {{ border: 2px solid {UltraModernColors.NEON_PURPLE}; }}"
        )
        self.shadow_effect.setBlurRadius(25)
        self.shadow_effect.setColor(QColor(UltraModernColors.NEON_PURPLE))

    def focusOutEvent(self, event):
        """Handle focus out event."""
        super().focusOutEvent(event)
        self.setStyleSheet(get_ultra_modern_input_style())
        self.shadow_effect.setBlurRadius(15)
        self.shadow_effect.setColor(QColor(0, 0, 0, 100))
