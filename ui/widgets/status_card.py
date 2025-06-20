from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QColor, QPainter

from ..styles.theme import UltraModernColors, get_modern_card_style


class ModernStatusIndicator(QWidget):
    """Modern status indicator with soft glow effect"""

    def __init__(self, status="disconnected", parent=None):
        super().__init__(parent)
        self.status = status
        self.setFixedSize(16, 16)
        self.glow_radius = 0

    def paintEvent(self, event):
        """วาดจุดสถานะแบบ modern พร้อม glow"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # สีตามสถานะ
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
        }

        color = QColor(colors.get(self.status, colors["disconnected"]))

        # วาดวงกลมหลัก
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(self.rect())

        # เพิ่ม highlight
        highlight_color = QColor(255, 255, 255, 60)
        painter.setBrush(highlight_color)
        highlight_rect = QRect(2, 2, 6, 6)
        painter.drawEllipse(highlight_rect)

    def set_status(self, new_status):
        """ตั้งค่าสถานะใหม่"""
        if self.status != new_status:
            self.status = new_status
            self.update()


class ModernStatusCard(QWidget):
    """Modern status card with enhanced design"""

    def __init__(self, title, status="disconnected", parent=None):
        super().__init__(parent)
        self.title = title
        self.status = status

        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self._animate_pulse)
        self.pulse_opacity = 1.0
        self.pulse_direction = -1

        self.hover_animation = QPropertyAnimation(self, b"pos")
        self.hover_animation.setDuration(300)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.setup_ui()
        self.update_status_display()

    def setup_ui(self):
        """Setup modern UI"""
        self.outer_frame = QFrame(self)
        self.outer_frame.setStyleSheet(get_modern_card_style("default"))

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.outer_frame)

        card_layout = QVBoxLayout(self.outer_frame)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        # Header with icon and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        self.status_indicator = ModernStatusIndicator(self.status)
        header_layout.addWidget(self.status_indicator)

        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Medium))
        self.title_label.setStyleSheet(f"color: {UltraModernColors.TEXT_PRIMARY};")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch(1)

        # Status icon - larger and more prominent
        self.status_icon = QLabel("")
        self.status_icon.setFont(QFont("Segoe UI Emoji", 24))
        self.status_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_icon.setFixedSize(40, 40)
        header_layout.addWidget(self.status_icon)

        card_layout.addLayout(header_layout)

        # Description with better typography
        self.description_label = QLabel("")
        self.description_label.setFont(QFont("Segoe UI", 11))
        self.description_label.setStyleSheet(
            f"""
            color: {UltraModernColors.TEXT_SECONDARY};
            line-height: 1.4;
            """
        )
        self.description_label.setWordWrap(True)
        card_layout.addWidget(self.description_label)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(120)  # Fixed height for consistency

    def update_status_display(self):
        """Update status display with modern design"""
        status_config = {
            "connected": {
                "icon": "✨",
                "color": UltraModernColors.SUCCESS_COLOR,
                "description": "Connected and operational",
                "card_style": "default",
            },
            "disconnected": {
                "icon": "⚫",
                "color": UltraModernColors.ERROR_COLOR,
                "description": "Not connected",
                "card_style": "default",
            },
            "error": {
                "icon": "⚠️",
                "color": UltraModernColors.ERROR_COLOR,
                "description": "Connection error",
                "card_style": "error",
            },
            "success": {
                "icon": "✅",
                "color": UltraModernColors.SUCCESS_COLOR,
                "description": "Operation completed successfully",
                "card_style": "success",
            },
            "never": {
                "icon": "⭕",
                "color": "#666666",
                "description": "No operations yet",
                "card_style": "default",
            },
            "syncing": {
                "icon": "🔄",
                "color": UltraModernColors.NEON_BLUE,
                "description": "Synchronizing data...",
                "card_style": "default",
            },
            "warning": {
                "icon": "⚠️",
                "color": UltraModernColors.WARNING_COLOR,
                "description": "Warning detected",
                "card_style": "default",
            },
            "in_progress": {
                "icon": "⏳",
                "color": UltraModernColors.NEON_PURPLE,
                "description": "Operation in progress...",
                "card_style": "default",
            },
            "connecting": {
                "icon": "🔗",
                "color": UltraModernColors.NEON_YELLOW,
                "description": "Connecting...",
                "card_style": "default",
            },
        }

        config = status_config.get(self.status, status_config["disconnected"])

        # Update indicator
        self.status_indicator.set_status(self.status)

        # Update icon with modern styling
        self.status_icon.setText(config["icon"])
        self.status_icon.setStyleSheet(
            f"""
            QLabel {{
                color: {config['color']};
                background: rgba(255, 255, 255, 0.05);
                border-radius: 20px;
                padding: 8px;
            }}
            """
        )

        # Update description
        self.description_label.setText(config["description"])

        # Update card style if needed
        if config["card_style"] != "default":
            self.outer_frame.setStyleSheet(get_modern_card_style(config["card_style"]))
        else:
            self.outer_frame.setStyleSheet(get_modern_card_style("default"))

        # Start/stop animations for active states
        if self.status in ["in_progress", "syncing", "connecting"]:
            if not self.pulse_timer.isActive():
                self.pulse_opacity = 1.0
                self.pulse_direction = -1
                self.pulse_timer.start(50)
        else:
            if self.pulse_timer.isActive():
                self.pulse_timer.stop()
                self.status_icon.setStyleSheet(
                    f"""
                    QLabel {{
                        color: {config['color']};
                        background: rgba(255, 255, 255, 0.05);
                        border-radius: 20px;
                        padding: 8px;
                    }}
                    """
                )

    def set_status(self, status):
        """Set new status"""
        if self.status != status:
            self.status = status
            self.update_status_display()

    def _animate_pulse(self):
        """Animate pulsing effect for active states"""
        self.pulse_opacity += self.pulse_direction * 0.03

        if self.pulse_opacity <= 0.4:
            self.pulse_opacity = 0.4
            self.pulse_direction = 1
        elif self.pulse_opacity >= 1.0:
            self.pulse_opacity = 1.0
            self.pulse_direction = -1

        # Apply pulsing effect
        config = {
            "syncing": UltraModernColors.NEON_BLUE,
            "in_progress": UltraModernColors.NEON_PURPLE,
            "connecting": UltraModernColors.NEON_YELLOW,
        }

        color = config.get(self.status, UltraModernColors.NEON_PURPLE)
        opacity = int(self.pulse_opacity * 255)

        self.status_icon.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                background: rgba(255, 255, 255, {self.pulse_opacity * 0.1});
                border-radius: 20px;
                padding: 8px;
                border: 2px solid rgba(157, 78, 221, {self.pulse_opacity * 0.5});
            }}
            """
        )

    def enterEvent(self, event):
        """Modern hover effect"""
        super().enterEvent(event)
        self.outer_frame.setStyleSheet(
            self.outer_frame.styleSheet().replace(
                UltraModernColors.GLASS_BG, UltraModernColors.GLASS_BG_LIGHT
            )
        )

    def leaveEvent(self, event):
        """Reset hover effect"""
        super().leaveEvent(event)
        # Reset to original style based on current status
        status_config = {"error": "error", "success": "success"}
        style_variant = status_config.get(self.status, "default")
        self.outer_frame.setStyleSheet(get_modern_card_style(style_variant))

    def cleanup_animations(self):
        """Cleanup animations"""
        if hasattr(self, "pulse_timer"):
            self.pulse_timer.stop()
        if hasattr(self, "hover_animation"):
            self.hover_animation.stop()


# Compatibility aliases
StatusCard = ModernStatusCard
UltraModernStatusCard = ModernStatusCard
