from PyQt6.QtWidgets import QGroupBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont  # Import QFont for consistency
from ..styles.theme import get_holographic_groupbox_style, UltraModernColors


class NeonGroupBox(QGroupBox):
    """แก้แล้ว: ลบ layout conflict"""

    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setStyleSheet(get_holographic_groupbox_style())
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))  # Set font for the title
        self.setTitle(
            f"<span style='color:{UltraModernColors.TEXT_PRIMARY};'>{title}</span>"
        )  # Set title with color

    def setTitle(self, title: str) -> None:
        """Overrides setTitle to apply custom styling to the title text."""
        # The stylesheet already handles the title appearance.
        # This can be used if we want to programmatically change title color, etc.
        super().setTitle(title)  # Call original setTitle
