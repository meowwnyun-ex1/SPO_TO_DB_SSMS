from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QProgressBar,
    QWidget,
    QGraphicsDropShadowEffect,
    QSizePolicy,  # Re-added QSizePolicy as it was removed in a previous iteration
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QPoint


from ..styles.theme import (
    UltraModernColors,
    get_ultra_modern_card_style,
    get_holographic_progress_style,
)


class QuantumProgressBar(QProgressBar):
    """
    Enhanced progress bar with quantum effects.
    ปรับปรุงแถบความคืบหน้าให้มีสไตล์และสีที่ตรงกับธีมใหม่.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_quantum_style()
        self.setup_neural_animations()

    def setup_quantum_style(self):
        """Setup quantum holographic styling."""
        self.setStyleSheet(get_holographic_progress_style())
        self.setTextVisible(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def setup_neural_animations(self):
        """Setup neural network inspired animations (e.g., subtle glow)."""
        self.opacity_effect = QGraphicsDropShadowEffect(self)
        self.opacity_effect.setBlurRadius(5)
        self.opacity_effect.setColor(QColor(UltraModernColors.NEON_PURPLE).darker(150))
        self.setGraphicsEffect(self.opacity_effect)

        self.animation = QPropertyAnimation(self.opacity_effect, b"blurRadius")
        self.animation.setDuration(1500)
        self.animation.setStartValue(5)
        self.animation.setEndValue(10)
        self.animation.setLoopCount(-1)
        # FIX: Removed setDirection(QPropertyAnimation.Direction.Alternate) which causes AttributeError.
        # Instead, we connect to the finished signal to manually reverse the animation.
        self.animation.finished.connect(self._reverse_animation)
        self.animation.start()

    def _reverse_animation(self):
        """Reverses the blur radius animation values for an alternating effect."""
        # Swap start and end values to create an alternating animation
        start = self.animation.startValue()
        end = self.animation.endValue()
        self.animation.setStartValue(end)
        self.animation.setEndValue(start)
        self.animation.start()


class UltraModernProgressCard(QWidget):
    """
    การ์ดแสดงความคืบหน้าแบบ Ultra Modern พร้อมแถบความคืบหน้าและข้อมูล
    มีการปรับปรุงเอฟเฟกต์เงาและการเคลื่อนไหว
    """

    progress_completed = pyqtSignal()

    def __init__(self, title, initial_progress=0, parent=None):
        super().__init__(parent)
        self.title = title
        self.progress_value = initial_progress
        self.max_progress = 100

        # Initialize hover_animation BEFORE calling setup_ui
        self.hover_animation = QPropertyAnimation(self, b"pos")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.setup_ui()

    def setup_ui(self):
        """ตั้งค่า UI ของการ์ดความคืบหน้า"""
        self.outer_frame = QFrame(self)
        self.outer_frame.setStyleSheet(get_ultra_modern_card_style("default"))

        self.shadow_effect = QGraphicsDropShadowEffect(self.outer_frame)
        self.shadow_effect.setBlurRadius(25)
        self.shadow_effect.setColor(QColor(0, 0, 0, 100))
        self.outer_frame.setGraphicsEffect(self.shadow_effect)

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
        """
        ตั้งค่าความคืบหน้าของแถบโปรเกรส
        Args:
            current_value (int): ค่าปัจจุบัน
            max_value (int): ค่าสูงสุด (ค่าเริ่มต้นคือ 100)
        """
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
        self.shadow_effect.setBlurRadius(30)
        self.shadow_effect.setColor(QColor(0, 0, 0, 150))
        self.outer_frame.update()

    def leaveEvent(self, event):
        """Handle mouse hover leave event."""
        super().leaveEvent(event)
        current_pos = self.pos()
        target_pos = current_pos - QPoint(0, -5)
        self.hover_animation.setStartValue(current_pos)
        self.hover_animation.setEndValue(target_pos)
        self.hover_animation.start()
        self.shadow_effect.setBlurRadius(25)
        self.shadow_effect.setColor(QColor(0, 0, 0, 100))
        self.outer_frame.update()


# Backward compatibility
class ProgressCard(UltraModernProgressCard):
    """Alias for backward compatibility"""

    pass


class CompactProgressIndicator(QWidget):
    """
    Compact progress indicator สำหรับ status bar หรือ small spaces
    """

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
