from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QFont, QColor, QPainter

from ..styles.theme import UltraModernColors


class CompactStatusIndicator(QWidget):
    """Compact status indicator สำหรับขนาด 900x500"""

    def __init__(self, status="disconnected", parent=None):
        super().__init__(parent)
        self.status = status
        self.setFixedSize(10, 10)  # ลดขนาด

    def paintEvent(self, event):
        """วาดจุดสถานะแบบ compact"""
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
        }

        color = QColor(colors.get(self.status, colors["disconnected"]))

        # วาดวงกลมหลัก
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(self.rect())

        # เพิ่ม highlight เล็กๆ
        highlight_color = QColor(255, 255, 255, 60)
        painter.setBrush(highlight_color)
        highlight_rect = QRect(1, 1, 4, 4)
        painter.drawEllipse(highlight_rect)

    def set_status(self, new_status):
        """ตั้งค่าสถานะใหม่"""
        if self.status != new_status:
            self.status = new_status
            self.update()


class ModernStatusCard(QWidget):
    """Compact Status Card สำหรับ 900x500"""

    def __init__(self, title, status="disconnected", parent=None):
        super().__init__(parent)
        self.title = title
        self.status = status

        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self._animate_pulse)
        self.pulse_opacity = 1.0
        self.pulse_direction = -1

        self.setup_compact_ui()
        self.update_status_display()

    def setup_compact_ui(self):
        """Setup compact UI สำหรับพื้นที่จำกัด"""
        self.outer_frame = QFrame(self)
        self.outer_frame.setStyleSheet(
            f"""
            QFrame {{
                background: {UltraModernColors.GLASS_BG_DARK};
                border: 1px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 8px;
                padding: 8px;
                color: {UltraModernColors.TEXT_PRIMARY};
            }}
            """
        )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.outer_frame)

        card_layout = QVBoxLayout(self.outer_frame)
        card_layout.setContentsMargins(8, 6, 8, 6)
        card_layout.setSpacing(4)

        # Compact header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(6)

        self.status_indicator = CompactStatusIndicator(self.status)
        header_layout.addWidget(self.status_indicator)

        # Compact title
        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.title_label.setStyleSheet(
            f"color: {UltraModernColors.TEXT_PRIMARY}; font-weight: bold;"
        )
        header_layout.addWidget(self.title_label)

        header_layout.addStretch(1)

        # Compact status icon
        self.status_icon = QLabel("")
        self.status_icon.setFont(QFont("Segoe UI Emoji", 16))  # ลดขนาด
        self.status_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_icon.setFixedSize(24, 24)  # ลดขนาด
        header_layout.addWidget(self.status_icon)

        card_layout.addLayout(header_layout)

        # Compact description
        self.description_label = QLabel("")
        self.description_label.setFont(
            QFont("Segoe UI", 8, QFont.Weight.Medium)
        )  # ลดขนาด
        self.description_label.setStyleSheet(
            f"""
            color: {UltraModernColors.TEXT_SECONDARY};
            background: rgba(255, 255, 255, 0.03);
            padding: 4px 6px;
            border-radius: 4px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            """
        )
        self.description_label.setWordWrap(True)
        card_layout.addWidget(self.description_label)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def update_status_display(self):
        """Update status display - compact version"""
        status_config = {
            "connected": {
                "icon": "✨",
                "color": UltraModernColors.SUCCESS_COLOR,
                "description": "Connected & Ready",
                "border_color": UltraModernColors.SUCCESS_COLOR,
            },
            "disconnected": {
                "icon": "⚫",
                "color": UltraModernColors.ERROR_COLOR,
                "description": "Not Connected",
                "border_color": UltraModernColors.ERROR_COLOR,
            },
            "error": {
                "icon": "⚠️",
                "color": UltraModernColors.ERROR_COLOR,
                "description": "Connection Error",
                "border_color": UltraModernColors.ERROR_COLOR,
            },
            "success": {
                "icon": "✅",
                "color": UltraModernColors.SUCCESS_COLOR,
                "description": "Operation Success",
                "border_color": UltraModernColors.SUCCESS_COLOR,
            },
            "never": {
                "icon": "⭕",
                "color": "#999999",
                "description": "No Operations Yet",
                "border_color": "#666666",
            },
            "syncing": {
                "icon": "🔄",
                "color": UltraModernColors.NEON_BLUE,
                "description": "Syncing Data...",
                "border_color": UltraModernColors.NEON_BLUE,
            },
            "warning": {
                "icon": "⚠️",
                "color": UltraModernColors.WARNING_COLOR,
                "description": "Warning State",
                "border_color": UltraModernColors.WARNING_COLOR,
            },
            "in_progress": {
                "icon": "⏳",
                "color": UltraModernColors.NEON_PURPLE,
                "description": "In Progress...",
                "border_color": UltraModernColors.NEON_PURPLE,
            },
            "connecting": {
                "icon": "🔗",
                "color": UltraModernColors.NEON_YELLOW,
                "description": "Connecting...",
                "border_color": UltraModernColors.NEON_YELLOW,
            },
        }

        config = status_config.get(self.status, status_config["disconnected"])

        # Update indicator
        self.status_indicator.set_status(self.status)

        # Update frame border color
        self.outer_frame.setStyleSheet(
            f"""
            QFrame {{
                background: {UltraModernColors.GLASS_BG_DARK};
                border: 1px solid {config['border_color']};
                border-radius: 8px;
                padding: 8px;
                color: {UltraModernColors.TEXT_PRIMARY};
            }}
            """
        )

        # Update compact icon
        self.status_icon.setText(config["icon"])
        self.status_icon.setStyleSheet(
            f"""
            QLabel {{
                color: {config['color']};
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid {config['color']};
                border-radius: 12px;
                padding: 3px;
            }}
            """
        )

        # Update compact description
        self.description_label.setText(config["description"])

        # Start/stop animations for active states
        if self.status in ["in_progress", "syncing", "connecting"]:
            if not self.pulse_timer.isActive():
                self.pulse_opacity = 1.0
                self.pulse_direction = -1
                self.pulse_timer.start(60)  # ช้าลงเล็กน้อย
        else:
            if self.pulse_timer.isActive():
                self.pulse_timer.stop()

    def set_status(self, status):
        """Set new status"""
        if self.status != status:
            self.status = status
            self.update_status_display()

    def _animate_pulse(self):
        """Animate pulsing effect - เบาลง"""
        self.pulse_opacity += self.pulse_direction * 0.02  # ช้าลง

        if self.pulse_opacity <= 0.5:  # เปลี่ยนขอบเขต
            self.pulse_opacity = 0.5
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

        self.status_icon.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                background: rgba(255, 255, 255, {self.pulse_opacity * 0.15});
                border: 1px solid {color};
                border-radius: 12px;
                padding: 3px;
            }}
            """
        )

    def enterEvent(self, event):
        """Compact hover effect"""
        super().enterEvent(event)
        current_config = {
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

        border_color = current_config.get(self.status, UltraModernColors.NEON_PURPLE)

        self.outer_frame.setStyleSheet(
            f"""
            QFrame {{
                background: {UltraModernColors.GLASS_BG_LIGHT};
                border: 2px solid {border_color};
                border-radius: 8px;
                padding: 8px;
                color: {UltraModernColors.TEXT_PRIMARY};
            }}
            """
        )

    def leaveEvent(self, event):
        """Reset hover effect"""
        super().leaveEvent(event)
        self.update_status_display()

    def cleanup_animations(self):
        """Cleanup animations"""
        if hasattr(self, "pulse_timer"):
            self.pulse_timer.stop()


# Compatibility aliases
StatusCard = ModernStatusCard
UltraModernStatusCard = ModernStatusCard
