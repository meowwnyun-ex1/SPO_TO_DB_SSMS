from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QGraphicsDropShadowEffect, QColor
from ..styles.theme import get_gradient_button_style


class ModernButton(QPushButton):
    """Modern animated button with hover effects"""

    def __init__(self, text, color1="#4CAF50", color2="#388E3C", size="normal"):
        super().__init__(text)
        self.color1 = color1
        self.color2 = color2
        self.size = size
        self.original_geometry = None
        self.setup_ui()
        self.setup_animations()

    def setup_ui(self):
        """ตั้งค่า UI"""
        self.setStyleSheet(
            get_gradient_button_style(self.color1, self.color2, self.size)
        )

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

    def setup_animations(self):
        """ตั้งค่า animations"""
        self.hover_animation = QPropertyAnimation(self, b"geometry")
        self.hover_animation.setDuration(150)
        self.hover_animation.setEasingCurve(QEasingCurve.OutCubic)

    def enterEvent(self, event):
        """เมื่อ mouse hover"""
        super().enterEvent(event)
        if self.original_geometry is None:
            self.original_geometry = self.geometry()

        # Slight scale effect
        new_geometry = QRect(
            self.original_geometry.x() - 2,
            self.original_geometry.y() - 1,
            self.original_geometry.width() + 4,
            self.original_geometry.height() + 2,
        )

        self.hover_animation.setStartValue(self.geometry())
        self.hover_animation.setEndValue(new_geometry)
        self.hover_animation.start()

    def leaveEvent(self, event):
        """เมื่อ mouse leave"""
        super().leaveEvent(event)
        if self.original_geometry:
            self.hover_animation.setStartValue(self.geometry())
            self.hover_animation.setEndValue(self.original_geometry)
            self.hover_animation.start()

    def update_colors(self, color1, color2):
        """อัพเดทสี"""
        self.color1 = color1
        self.color2 = color2
        self.setStyleSheet(get_gradient_button_style(color1, color2, self.size))
