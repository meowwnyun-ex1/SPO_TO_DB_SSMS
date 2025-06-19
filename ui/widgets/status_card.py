from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QFont, QColor, QPainter

# Import UltraModernColors for theming
from ..styles.theme import UltraModernColors, get_ultra_modern_card_style


class StatusIndicator(QWidget):
    """
    ไฟแสดงสถานะวงกลมพร้อมสีและเอฟเฟกต์การกระพริบเมื่อสถานะมีการเปลี่ยนแปลง
    """

    def __init__(self, status="disconnected", parent=None):
        super().__init__(parent)
        self.status = status
        self.setFixedSize(16, 16)  # Slightly larger indicator
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(800)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.2)
        self.animation.setLoopCount(2)
        self.animation.finished.connect(
            lambda: self.opacity_effect.setOpacity(1.0)
        )  # Reset opacity after animation

    def paintEvent(self, event):
        """วาดวงกลมแสดงสถานะ"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        colors = {
            "connected": UltraModernColors.SUCCESS_COLOR,
            "disconnected": UltraModernColors.ERROR_COLOR,
            "error": UltraModernColors.ERROR_COLOR,
            "success": UltraModernColors.SUCCESS_COLOR,
            "never": UltraModernColors.TEXT_SECONDARY,
            "syncing": UltraModernColors.NEON_BLUE,
            "warning": UltraModernColors.NEON_YELLOW,
            "in_progress": UltraModernColors.NEON_PURPLE,
        }

        color = colors.get(self.status, colors["disconnected"])
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(self.rect())

    def set_status(self, new_status):
        """ตั้งค่าสถานะใหม่และเรียกใช้แอนิเมชั่น"""
        if self.status != new_status:
            self.status = new_status
            self.animation.start()
            self.update()
        else:
            self.update()


class StatusCard(QWidget):
    """
    การ์ดแสดงสถานะแบบ Ultra Modern พร้อมไฟแสดงสถานะและข้อความ
    มีการปรับปรุงเอฟเฟกต์เงาและการเคลื่อนไหว
    """

    def __init__(self, title, status="disconnected", parent=None):
        super().__init__(parent)
        self.title = title
        self.status = status
        self.description = ""

        # Initialize attributes BEFORE calling setup_ui or update_status_display
        # ต้อง Initialized attribute เหล่านี้ก่อนเรียก setup_ui หรือ update_status_display
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self._animate_pulse)
        self.pulse_strength = 0.0
        self.pulse_direction = 1

        self.hover_animation = QPropertyAnimation(self, b"pos")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.setup_ui()  # Now safe to call
        self.update_status_display()  # Now safe to call

    def setup_ui(self):
        """ตั้งค่า UI ของการ์ดสถานะ"""
        self.outer_frame = QFrame(self)
        self.outer_frame.setStyleSheet(get_ultra_modern_card_style("default"))

        self.shadow_effect = QGraphicsDropShadowEffect(self.outer_frame)
        self.shadow_effect.setBlurRadius(25)
        self.shadow_effect.setColor(QColor(0, 0, 0, 100))
        self.outer_frame.setGraphicsEffect(self.shadow_effect)

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
                "shadow_color": UltraModernColors.SUCCESS_COLOR,
            },
            "disconnected": {
                "symbol": "✖",
                "color": UltraModernColors.ERROR_COLOR,
                "shadow_color": UltraModernColors.ERROR_COLOR,
            },
            "error": {
                "symbol": "❗",
                "color": UltraModernColors.ERROR_COLOR,
                "shadow_color": UltraModernColors.ERROR_COLOR,
            },
            "success": {
                "symbol": "✔",
                "color": UltraModernColors.SUCCESS_COLOR,
                "shadow_color": UltraModernColors.SUCCESS_COLOR,
            },
            "never": {
                "symbol": "…",
                "color": UltraModernColors.TEXT_SECONDARY,
                "shadow_color": UltraModernColors.TEXT_SECONDARY,
            },
            "syncing": {
                "symbol": "⟳",
                "color": UltraModernColors.NEON_BLUE,
                "shadow_color": UltraModernColors.NEON_BLUE,
            },
            "warning": {
                "symbol": "⚠",
                "color": UltraModernColors.NEON_YELLOW,
                "shadow_color": UltraModernColors.NEON_YELLOW,
            },
            "in_progress": {
                "symbol": "⟳",
                "color": UltraModernColors.NEON_PURPLE,
                "shadow_color": UltraModernColors.NEON_PURPLE,
            },
        }

        current_config = config.get(self.status, config["disconnected"])
        self.indicator.set_status(self.status)
        self.indicator_symbol.setText(current_config["symbol"])
        self.indicator_symbol.setStyleSheet(f"color: {current_config['color']};")

        # To simulate text shadow/glow, a QGraphicsDropShadowEffect could be applied to self.indicator_symbol
        # self.symbol_shadow_effect = QGraphicsDropShadowEffect(self.indicator_symbol)
        # self.symbol_shadow_effect.setBlurRadius(10)
        # self.symbol_shadow_effect.setColor(QColor(current_config['shadow_color']))
        # self.indicator_symbol.setGraphicsEffect(self.symbol_shadow_effect)

        # Handle description based on status
        if self.status == "connected":
            self.description_label.setText("Online and operational.")
        elif self.status == "disconnected":
            self.description_label.setText("Offline or connection lost.")
        elif self.status == "error":
            self.description_label.setText("An error occurred during operation.")
        elif self.status == "success":
            self.description_label.setText("Operation completed successfully.")
        elif self.status == "never":
            self.description_label.setText("No previous operations recorded.")
        elif self.status == "syncing":
            self.description_label.setText("Synchronization in progress...")
        elif self.status == "warning":
            self.description_label.setText("Operation completed with warnings.")
        elif self.status == "in_progress":
            self.description_label.setText("Operation ongoing...")

        # Start/Stop pulse animation
        if self.status == "in_progress" or self.status == "syncing":
            if not self.pulse_timer.isActive():
                self.pulse_strength = 0.0
                self.pulse_direction = 1
                self.pulse_timer.start(50)
        else:
            if self.pulse_timer and self.pulse_timer.isActive():
                self.pulse_timer.stop()
                self.shadow_effect.setBlurRadius(25)
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

        current_blur = 20 + 10 * self.pulse_strength
        self.shadow_effect.setBlurRadius(current_blur)

        current_symbol_glow = 5 + 10 * self.pulse_strength

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
        self.shadow_effect.setBlurRadius(30)
        self.shadow_effect.setColor(QColor(0, 0, 0, 150))
        self.outer_frame.update()

    def leaveEvent(self, event):
        """Handle mouse hover leave event."""
        super().leaveEvent(event)
        current_pos = self.pos()
        target_pos = current_pos - QPoint(0, -5)
        self.hover_animation.setStartValue(current_pos)
        self.hover_animation.setEndValue(target_pos)
        self.hover_animation.start()
        self.shadow_effect.setBlurRadius(25)
        self.shadow_effect.setColor(QColor(0, 0, 0, 100))
        self.outer_frame.update()


# Backward compatibility
class UltraModernStatusCard(StatusCard):
    """Alias for backward compatibility"""

    pass
