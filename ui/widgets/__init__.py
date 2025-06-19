from .status_card import StatusCard
from .progress_card import ProgressCard
from .connection_status import ConnectionStatusWidget
from .control_panel import ControlPanel
from .modern_button import ModernButton

__all__ = [
    "StatusCard",
    "ProgressCard",
    "ConnectionStatusWidget",
    "ControlPanel",
    "ModernButton",
]

# ui/widgets/control_panel.py
from PyQt5.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QGridLayout,
    QPushButton,
    QCheckBox,
    QLabel,
)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont
from ..styles.theme import get_card_style, get_gradient_button_style, get_checkbox_style


class ControlPanel(QFrame):
    """Control Panel สำหรับควบคุมการทำงาน"""

    # Signals
    test_connections_clicked = pyqtSignal()
    start_sync_clicked = pyqtSignal()
    stop_sync_clicked = pyqtSignal()
    clear_logs_clicked = pyqtSignal()
    auto_sync_toggled = pyqtSignal(bool)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.sync_running = False
        self.setup_ui()

    def setup_ui(self):
        """ตั้งค่า UI"""
        self.setStyleSheet(get_card_style())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title = QLabel("Control Panel")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setStyleSheet("color: rgba(255,255,255,0.9);")
        layout.addWidget(title)

        # Main Buttons
        main_layout = QGridLayout()

        # Test Connections
        self.test_btn = QPushButton("🔍 Test Connections")
        self.test_btn.setStyleSheet(get_gradient_button_style("#2196F3", "#1976D2"))
        self.test_btn.clicked.connect(self.test_connections_clicked.emit)
        main_layout.addWidget(self.test_btn, 0, 0)

        # Start/Stop Sync
        self.sync_btn = QPushButton("🚀 Start Sync")
        self.sync_btn.setStyleSheet(get_gradient_button_style("#4CAF50", "#388E3C"))
        self.sync_btn.clicked.connect(self._toggle_sync)
        main_layout.addWidget(self.sync_btn, 0, 1)

        # Clear Logs
        self.clear_btn = QPushButton("🧹 Clear Logs")
        self.clear_btn.setStyleSheet(
            get_gradient_button_style("#FF9800", "#F57C00", "small")
        )
        self.clear_btn.clicked.connect(self.clear_logs_clicked.emit)
        main_layout.addWidget(self.clear_btn, 1, 0)

        # Auto Sync Toggle
        self.auto_sync_check = QCheckBox("🔄 Auto Sync")
        self.auto_sync_check.setStyleSheet(get_checkbox_style())
        self.auto_sync_check.toggled.connect(self.auto_sync_toggled.emit)
        main_layout.addWidget(self.auto_sync_check, 1, 1)

        layout.addLayout(main_layout)

    def _toggle_sync(self):
        """Toggle การซิงค์"""
        if self.sync_running:
            self.stop_sync_clicked.emit()
            self.set_sync_running(False)
        else:
            self.start_sync_clicked.emit()
            self.set_sync_running(True)

    def set_sync_running(self, running):
        """ตั้งค่าสถานะการซิงค์"""
        self.sync_running = running

        if running:
            self.sync_btn.setText("⏹️ Stop Sync")
            self.sync_btn.setStyleSheet(get_gradient_button_style("#f44336", "#d32f2f"))
        else:
            self.sync_btn.setText("🚀 Start Sync")
            self.sync_btn.setStyleSheet(get_gradient_button_style("#4CAF50", "#388E3C"))

    def set_auto_sync_enabled(self, enabled):
        """ตั้งค่า Auto Sync"""
        self.auto_sync_check.setChecked(enabled)
