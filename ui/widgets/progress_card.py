from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtGui import QFont
from ..styles.theme import get_card_style, get_progress_bar_style


class ProgressCard(QFrame):
    """Progress Card สำหรับแสดงความคืบหน้า"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """ตั้งค่า UI"""
        self.setStyleSheet(get_card_style())
        self.setFixedHeight(120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title = QLabel("Progress Tracking")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setStyleSheet("color: rgba(255,255,255,0.9);")
        layout.addWidget(title)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(get_progress_bar_style())
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Progress Message
        self.message_label = QLabel("Ready")
        self.message_label.setFont(QFont("Segoe UI", 10))
        self.message_label.setStyleSheet("color: rgba(255,255,255,0.8);")
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)

        # Stats Label
        self.stats_label = QLabel("")
        self.stats_label.setFont(QFont("Segoe UI", 9))
        self.stats_label.setStyleSheet("color: rgba(255,255,255,0.6);")
        layout.addWidget(self.stats_label)

    def update_progress(self, message, progress, level="info"):
        """อัพเดทความคืบหน้า"""
        self.message_label.setText(message)

        if progress > 0:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(progress)

            # Update color based on level
            if level == "error":
                style = get_progress_bar_style().replace("#00d4ff", "#f44336")
            elif level == "warning":
                style = get_progress_bar_style().replace("#00d4ff", "#ff9800")
            else:
                style = get_progress_bar_style()

            self.progress_bar.setStyleSheet(style)
        else:
            self.progress_bar.setVisible(False)

    def update_stats(self, stats_text):
        """อัพเดทสถิติ"""
        self.stats_label.setText(stats_text)

    def reset(self):
        """รีเซ็ตการแสดงผล"""
        self.progress_bar.setVisible(False)
        self.message_label.setText("Ready")
        self.stats_label.setText("")
