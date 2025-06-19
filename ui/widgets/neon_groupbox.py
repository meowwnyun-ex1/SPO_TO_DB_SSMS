from PyQt6.QtWidgets import QGroupBox, QVBoxLayout
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

from ..styles.theme import get_holographic_groupbox_style, UltraModernColors


class NeonGroupBox(QGroupBox):
    """
    A custom QGroupBox with neon-themed styling, providing a distinct section for UI elements.
    QGroupBox ที่ปรับแต่งด้วยสไตล์นีออนสำหรับจัดกลุ่มองค์ประกอบ UI
    """

    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setStyleSheet(get_holographic_groupbox_style())
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center align title

        # For better content management, if you intend to add layout directly to groupbox
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(
            15, 25, 15, 15
        )  # Adjust top margin for title
        self.main_layout.setSpacing(10)

        # Optional: Add a subtle glow/shadow effect to the groupbox itself
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(20)
        self.shadow_effect.setColor(QColor(UltraModernColors.NEON_PURPLE).darker(150))
        self.setGraphicsEffect(self.shadow_effect)

        # Animation for a subtle pulse or glow effect on the border (optional)
        self.animation = QPropertyAnimation(self.shadow_effect, b"blurRadius")
        self.animation.setDuration(2000)
        self.animation.setStartValue(15)
        self.animation.setEndValue(25)
        self.animation.setLoopCount(-1)  # Loop indefinitely
        self.animation.setDirection(QPropertyAnimation.Direction.Alternate)
        self.animation.start()
