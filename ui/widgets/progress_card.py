from PyQt6.QtWidgets import (
    QVBoxLayout,
    QLabel,
    QProgressBar,
    QWidget,
    QSizePolicy,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QPoint

from ..styles.theme import (
    UltraModernColors,
    get_ultra_modern_card_style,
    get_holographic_progress_style,
)


class QuantumProgressBar(QProgressBar):
    """Enhanced progress bar with quantum effects."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_quantum_style()

    def setup_quantum_style(self):
        """Setup quantum holographic styling."""
        self.setStyleSheet(get_holographic_progress_style())
        self.setTextVisible(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class UltraModernProgressCard(QWidget):
    """Progress card แบบ Ultra Modern ลบ shadow effects"""

    progress_completed = pyqtSignal()

    def __init__(self, title, initial_progress=0, parent=None):
        super().__init__(parent)
        self.title = title
        self.progress_value = initial_progress
        self.max_progress = 100

        # Animation for hover effect
        self.hover_animation = QPropertyAnimation(self, b"pos")
        self.hover_animation.setDuration(150)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        self._setup_ui()
        self.set_progress(initial_progress)  # Set initial progress

    def _setup_ui(self):
        """Sets up the layout and widgets for the progress card."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Apply the card style to the QWidget itself
        self.setStyleSheet(get_ultra_modern_card_style())
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(100)  # Ensure a consistent minimum height

        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"color: {UltraModernColors.NEON_BLUE};")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title_label)

        self.progress_bar = QuantumProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(self.max_progress)
        main_layout.addWidget(self.progress_bar)

        self.status_message_label = QLabel("")
        self.status_message_label.setFont(QFont("Segoe UI", 10))
        self.status_message_label.setStyleSheet(
            f"color: {UltraModernColors.TEXT_PRIMARY};"
        )
        self.status_message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_message_label)

        main_layout.addStretch(1)  # Push content to the top

    def set_progress(self, value: int, message: str = ""):
        """Sets the progress value and updates the message."""
        self.progress_value = max(0, min(value, self.max_progress))  # Clamp value
        self.progress_bar.setValue(self.progress_value)
        self.status_message_label.setText(message)

        if (
            self.progress_value >= self.max_progress and self.max_value > 0
        ):  # Ensure max_value is set and > 0
            self.progress_completed.emit()

    def enterEvent(self, event):
        """Handle mouse hover enter event."""
        super().enterEvent(event)
        # Store initial position when hover starts to ensure accurate return
        self.initial_pos_on_hover = self.pos()
        if self.hover_animation.state() == QPropertyAnimation.State.Running:
            self.hover_animation.stop()

        target_pos = self.initial_pos_on_hover + QPoint(0, -5)  # Move up by 5 pixels
        self.hover_animation.setStartValue(self.initial_pos_on_hover)
        self.hover_animation.setEndValue(target_pos)
        self.hover_animation.start()

    def leaveEvent(self, event):
        """Handle mouse hover leave event."""
        super().leaveEvent(event)
        if self.hover_animation.state() == QPropertyAnimation.State.Running:
            self.hover_animation.stop()

        # Move back to the initial position stored when hover started
        target_pos = self.initial_pos_on_hover  # Return to where it was
        self.hover_animation.setStartValue(self.pos())
        self.hover_animation.setEndValue(target_pos)
        self.hover_animation.start()


# Backward compatibility
class ProgressCard(UltraModernProgressCard):
    """Alias for backward compatibility"""

    pass


class CompactProgressIndicator(QWidget):
    """Compact progress indicator สำหรับ status bar หรือ small spaces"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 15)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(0, 0, 120, 15)
        self.progress_bar.setTextVisible(False)  # No text for compact
        self.progress_bar.setStyleSheet(
            f"""
            QProgressBar {{
                background-color: {UltraModernColors.GLASS_BG_DARK};
                border: 1px solid {UltraModernColors.GLASS_BORDER};
                border-radius: 6px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {UltraModernColors.NEON_GREEN},
                    stop:1 {UltraModernColors.NEON_BLUE}
                );
                border-radius: 5px;
            }}
            """
        )

    @pyqtSlot(int)
    def set_progress(self, value: int):
        """Sets the progress value for the compact indicator."""
        self.progress_bar.setValue(value)
