from PyQt6.QtWidgets import (
    QFrame,
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

        self.hover_animation = QPropertyAnimation(self, b"pos")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.setup_ui()

    def setup_ui(self):
        """ตั้งค่า UI ของการ์ดความคืบหน้า"""
        self.outer_frame = QFrame(self)
        self.outer_frame.setStyleSheet(get_ultra_modern_card_style("default"))

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.outer_frame)

        card_layout = QVBoxLayout(self.outer_frame)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(10)

        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Inter", 12, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"color: {UltraModernColors.TEXT_PRIMARY};")
        card_layout.addWidget(self.title_label)

        self.progress_bar = QuantumProgressBar()
        self.progress_bar.setValue(self.progress_value)
        self.progress_bar.setMaximum(self.max_progress)
        card_layout.addWidget(self.progress_bar)

        self.progress_text_label = QLabel(
            f"{self.progress_value}/{self.max_progress} (0%)"
        )
        self.progress_text_label.setFont(QFont("Inter", 10))
        self.progress_text_label.setStyleSheet(
            f"color: {UltraModernColors.TEXT_SECONDARY};"
        )
        self.progress_text_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        card_layout.addWidget(self.progress_text_label)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    def set_progress(self, current_value, max_value=100):
        """ตั้งค่าความคืบหน้าของแถบโปรเกรส"""
        self.progress_value = current_value
        self.max_progress = max_value
        self.progress_bar.setMaximum(self.max_progress)
        self.progress_bar.setValue(self.progress_value)

        percentage = (current_value / max_value) * 100 if max_value > 0 else 0
        self.progress_text_label.setText(
            f"{current_value}/{max_value} ({percentage:.1f}%)"
        )

        if current_value >= max_value and max_value > 0:
            self.progress_completed.emit()

    def enterEvent(self, event):
        """Handle mouse hover enter event."""
        super().enterEvent(event)
        current_pos = self.pos()
        target_pos = current_pos + QPoint(0, -5)
        self.hover_animation.setStartValue(current_pos)
        self.hover_animation.setEndValue(target_pos)
        self.hover_animation.start()

    def leaveEvent(self, event):
        """Handle mouse hover leave event."""
        super().leaveEvent(event)
        current_pos = self.pos()
        target_pos = current_pos - QPoint(0, -5)
        self.hover_animation.setStartValue(current_pos)
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
        self.progress_bar.setStyleSheet(get_holographic_progress_style())
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def set_progress(self, value):
        self.progress_bar.setValue(value)
