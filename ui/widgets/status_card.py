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


class ModernStatusIndicator(QWidget):
    """Modern status indicator with soft glow effect"""

    def __init__(self, status="disconnected", parent=None):
        super().__init__(parent)
        self.status = status
        self.setFixedSize(14, 14)
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
        highlight_color = QColor(255, 255, 255, 80)
        painter.setBrush(highlight_color)
        highlight_rect = QRect(2, 2, 6, 6)
        painter.drawEllipse(highlight_rect)

    def set_status(self, new_status):
        """ตั้งค่าสถานะใหม่"""
        if self.status != new_status:
            self.status = new_status
            self.update()


class ModernStatusCard(QWidget):
    """แก้แล้ว: Status card ที่แสดงหัวข้อชัดเจน ไม่โปร่งเวลา hover"""

    def __init__(self, title, status="disconnected", parent=None):
        super().__init__(parent)
        self.title = title
        self.status = status

        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self._animate_pulse)
        self.pulse_opacity = 1.0
        self.pulse_direction = -1

        self.setup_ui()
        self.update_status_display()

    def setup_ui(self):
        """แก้แล้ว: Setup UI ให้หัวข้อชัดเจน"""
        self.outer_frame = QFrame(self)
        self.outer_frame.setStyleSheet(
            f"""
            QFrame {{
                background: {UltraModernColors.GLASS_BG_DARK};
                border: 2px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 16px;
                padding: 16px;
                color: {UltraModernColors.TEXT_PRIMARY};
            }}
            """
        )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.outer_frame)

        card_layout = QVBoxLayout(self.outer_frame)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(12)

        # Header with icon and title - ชัดเจนขึ้น
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        self.status_indicator = ModernStatusIndicator(self.status)
        header_layout.addWidget(self.status_indicator)

        # แก้: ให้หัวข้อชัดเจนขึ้น ลบ text-shadow
        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.title_label.setStyleSheet(
            f"""
            color: {UltraModernColors.TEXT_PRIMARY};
            font-weight: bold;
            """
        )
        header_layout.addWidget(self.title_label)

        header_layout.addStretch(1)

        # Status icon - ใหญ่และชัดขึ้น
        self.status_icon = QLabel("")
        self.status_icon.setFont(QFont("Segoe UI Emoji", 22))
        self.status_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_icon.setFixedSize(35, 35)
        header_layout.addWidget(self.status_icon)

        card_layout.addLayout(header_layout)

        # Description with better visibility
        self.description_label = QLabel("")
        self.description_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.description_label.setStyleSheet(
            f"""
            color: {UltraModernColors.TEXT_SECONDARY};
            background: rgba(255, 255, 255, 0.05);
            padding: 8px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            """
        )
        self.description_label.setWordWrap(True)
        card_layout.addWidget(self.description_label)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(110)

    def update_status_display(self):
        """Update status display with better visibility"""
        status_config = {
            "connected": {
                "icon": "✨",
                "color": UltraModernColors.SUCCESS_COLOR,
                "description": "System Connected & Operational",
                "border_color": UltraModernColors.SUCCESS_COLOR,
            },
            "disconnected": {
                "icon": "⚫",
                "color": UltraModernColors.ERROR_COLOR,
                "description": "Not Connected - Check Settings",
                "border_color": UltraModernColors.ERROR_COLOR,
            },
            "error": {
                "icon": "⚠️",
                "color": UltraModernColors.ERROR_COLOR,
                "description": "Connection Error Detected",
                "border_color": UltraModernColors.ERROR_COLOR,
            },
            "success": {
                "icon": "✅",
                "color": UltraModernColors.SUCCESS_COLOR,
                "description": "Operation Completed Successfully",
                "border_color": UltraModernColors.SUCCESS_COLOR,
            },
            "never": {
                "icon": "⭕",
                "color": "#999999",
                "description": "No Operations Performed Yet",
                "border_color": "#666666",
            },
            "syncing": {
                "icon": "🔄",
                "color": UltraModernColors.NEON_BLUE,
                "description": "Synchronizing Data in Progress",
                "border_color": UltraModernColors.NEON_BLUE,
            },
            "warning": {
                "icon": "⚠️",
                "color": UltraModernColors.WARNING_COLOR,
                "description": "Warning - Attention Required",
                "border_color": UltraModernColors.WARNING_COLOR,
            },
            "in_progress": {
                "icon": "⏳",
                "color": UltraModernColors.NEON_PURPLE,
                "description": "Operation in Progress",
                "border_color": UltraModernColors.NEON_PURPLE,
            },
            "connecting": {
                "icon": "🔗",
                "color": UltraModernColors.NEON_YELLOW,
                "description": "Establishing Connection",
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
                border: 2px solid {config['border_color']};
                border-radius: 16px;
                padding: 16px;
                color: {UltraModernColors.TEXT_PRIMARY};
            }}
            """
        )

        # Update icon with better styling
        self.status_icon.setText(config["icon"])
        self.status_icon.setStyleSheet(
            f"""
            QLabel {{
                color: {config['color']};
                background: rgba(255, 255, 255, 0.1);
                border: 2px solid {config['color']};
                border-radius: 17px;
                padding: 6px;
            }}
            """
        )

        # Update description
        self.description_label.setText(config["description"])

        # Start/stop animations for active states
        if self.status in ["in_progress", "syncing", "connecting"]:
            if not self.pulse_timer.isActive():
                self.pulse_opacity = 1.0
                self.pulse_direction = -1
                self.pulse_timer.start(50)
        else:
            if self.pulse_timer.isActive():
                self.pulse_timer.stop()

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

        self.status_icon.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                background: rgba(255, 255, 255, {self.pulse_opacity * 0.2});
                border: 2px solid {color};
                border-radius: 17px;
                padding: 6px;
            }}
            """
        )

    def enterEvent(self, event):
        """แก้แล้ว: Hover effect ไม่ให้โปร่ง"""
        super().enterEvent(event)
        # เพิ่มความสว่างแทนการทำให้โปร่ง
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
                border: 3px solid {border_color};
                border-radius: 16px;
                padding: 16px;
                color: {UltraModernColors.TEXT_PRIMARY};
            }}
            """
        )

    def leaveEvent(self, event):
        """แก้แล้ว: Reset hover effect"""
        super().leaveEvent(event)
        self.update_status_display()  # กลับไปสถานะเดิม

    def cleanup_animations(self):
        """Cleanup animations"""
        if hasattr(self, "pulse_timer"):
            self.pulse_timer.stop()


# Compatibility aliases
StatusCard = ModernStatusCard
UltraModernStatusCard = ModernStatusCard
