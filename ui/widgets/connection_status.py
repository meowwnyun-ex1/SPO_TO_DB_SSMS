from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont
from .status_card import StatusCard


class ConnectionStatusWidget(QWidget):
    """Widget สำหรับแสดงสถานะการเชื่อมต่อทั้งหมด"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """ตั้งค่า UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title = QLabel("Connection Status")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setStyleSheet("color: rgba(255,255,255,0.9); margin-bottom: 10px;")
        layout.addWidget(title)

        # Status Cards Layout
        cards_layout = QHBoxLayout()

        # SharePoint Status
        self.sharepoint_card = StatusCard("SharePoint")
        cards_layout.addWidget(self.sharepoint_card)

        # Database Status
        self.database_card = StatusCard("Database")
        cards_layout.addWidget(self.database_card)

        layout.addLayout(cards_layout)

    def update_service_status(self, service, status):
        """อัพเดทสถานะของบริการ"""
        if service == "SharePoint":
            self.sharepoint_card.update_status(status)
        elif service == "Database":
            self.database_card.update_status(status)
