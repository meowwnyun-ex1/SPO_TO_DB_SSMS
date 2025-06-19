from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from ..styles.theme import get_card_style


class StatusCard(QFrame):
    """Status Card Widget สำหรับแสดงสถานะ"""

    status_clicked = pyqtSignal(str)  # service name

    def __init__(self, title, initial_status="disconnected"):
        super().__init__()
        self.service_name = title
        self.setup_ui()
        self.update_status(initial_status)

    def setup_ui(self):
        """ตั้งค่า UI"""
        self.setStyleSheet(get_card_style())
        self.setFixedHeight(80)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)

        # Title
        self.title_label = QLabel(self.service_name)
        self.title_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.title_label.setStyleSheet("color: rgba(255,255,255,0.9);")
        layout.addWidget(self.title_label)

        # Status Layout
        status_layout = QHBoxLayout()

        # Status Indicator
        self.status_indicator = QLabel("●")
        self.status_indicator.setFont(QFont("Segoe UI", 14))
        status_layout.addWidget(self.status_indicator)

        # Status Text
        self.status_label = QLabel("Disconnected")
        self.status_label.setFont(QFont("Segoe UI", 10))
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()
        layout.addLayout(status_layout)

    def update_status(self, status, message=""):
        """อัพเดทสถานะ"""
        status_config = {
            "connected": {"color": "#4CAF50", "text": "Connected", "indicator": "●"},
            "connecting": {
                "color": "#FF9800",
                "text": "Connecting...",
                "indicator": "◐",
            },
            "disconnected": {
                "color": "#757575",
                "text": "Disconnected",
                "indicator": "○",
            },
            "error": {"color": "#F44336", "text": "Error", "indicator": "✕"},
            "success": {
                "color": "#4CAF50",
                "text": message or "Success",
                "indicator": "✓",
            },
            "never": {"color": "#757575", "text": "Never synced", "indicator": "○"},
        }

        config = status_config.get(status, status_config["disconnected"])

        self.status_indicator.setText(config["indicator"])
        self.status_indicator.setStyleSheet(f"color: {config['color']};")

        self.status_label.setText(config["text"])
        self.status_label.setStyleSheet(f"color: {config['color']};")

    def mousePressEvent(self, event):
        """จัดการการคลิก"""
        if event.button() == Qt.LeftButton:
            self.status_clicked.emit(self.service_name)
        super().mousePressEvent(event)
