from PyQt6.QtWidgets import QGroupBox
from PyQt6.QtCore import Qt
from ..styles.theme import get_holographic_groupbox_style


class NeonGroupBox(QGroupBox):
    """แก้แล้ว: ลบ layout conflict"""

    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setStyleSheet(get_holographic_groupbox_style())
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
