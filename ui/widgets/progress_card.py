# ui/widgets/holographic_progress_bar.py - Modern 2025 Progress Bar
from PyQt6.QtWidgets import QProgressBar, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QPainter, QLinearGradient, QColor, QFont, QPen
import sys
from pathlib import Path

current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from ui.styles.theme import ModernColors, Typography, BorderRadius
except ImportError:

    class ModernColors:
        PRIMARY = "#6366F1"
        SURFACE_SECONDARY = "#1E293B"
        TEXT_PRIMARY = "#F8FAFC"


class ModernProgressBar(QProgressBar):
    """2025 Modern progress bar with animations"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()
        self._setup_animations()

    def _setup_style(self):
        """Setup modern progress bar styling"""
        self.setTextVisible(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFont(
            QFont(Typography.PRIMARY_FONT, Typography.TEXT_SM, Typography.WEIGHT_MEDIUM)
        )

        self.setStyleSheet(
            f"""
            QProgressBar {{
                background: {ModernColors.SURFACE_SECONDARY};
                border: none;
                border-radius: {BorderRadius.SM}px;
                height: 12px;
                text-align: center;
                color: {ModernColors.TEXT_PRIMARY};
                font-weight: {Typography.WEIGHT_MEDIUM};
                font-size: {Typography.TEXT_SM}px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ModernColors.PRIMARY},
                    stop:0.5 #8B5CF6,
                    stop:1 #06B6D4
                );
                border-radius: {BorderRadius.SM}px;
                margin: 1px;
            }}
        """
        )

    def _setup_animations(self):
        """Setup progress animations"""
        self.glow_animation = QPropertyAnimation(self, b"styleSheet")
        self.glow_animation.setDuration(1500)
        self.glow_animation.setLoopCount(-1)
        self.glow_animation.setEasingCurve(QEasingCurve.Type.InOutSine)

    def start_glow_animation(self):
        """Start glowing animation for active progress"""
        normal_style = self.styleSheet()
        glow_style = normal_style.replace(
            f"border: none;", f"border: 1px solid {ModernColors.PRIMARY};"
        )

        self.glow_animation.setKeyValueAt(0, normal_style)
        self.glow_animation.setKeyValueAt(0.5, glow_style)
        self.glow_animation.setKeyValueAt(1, normal_style)
        self.glow_animation.start()

    def stop_glow_animation(self):
        """Stop glowing animation"""
        self.glow_animation.stop()


class CircularProgressBar(QWidget):
    """Circular progress indicator"""

    value_changed = pyqtSignal(int)

    def __init__(self, size=80, parent=None):
        super().__init__(parent)
        self.size = size
        self.value = 0
        self.maximum = 100
        self.minimum = 0
        self.setFixedSize(size, size)

        # Animation
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def paintEvent(self, event):
        """Custom paint for circular progress"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate dimensions
        rect = self.rect().adjusted(10, 10, -10, -10)

        # Background circle
        painter.setPen(QPen(QColor(ModernColors.SURFACE_SECONDARY), 8))
        painter.drawEllipse(rect)

        # Progress arc
        if self.value > 0:
            progress_angle = int(360 * self.value / self.maximum)

            # Create gradient
            gradient = QLinearGradient(0, 0, rect.width(), 0)
            gradient.setColorAt(0, QColor(ModernColors.PRIMARY))
            gradient.setColorAt(0.5, QColor("#8B5CF6"))
            gradient.setColorAt(1, QColor("#06B6D4"))

            pen = QPen(QColor(ModernColors.PRIMARY), 8)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)

            painter.drawArc(rect, 90 * 16, -progress_angle * 16)

        # Center text
        painter.setPen(QColor(ModernColors.TEXT_PRIMARY))
        painter.setFont(
            QFont(Typography.PRIMARY_FONT, Typography.TEXT_LG, Typography.WEIGHT_BOLD)
        )
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{self.value}%")

    def setValue(self, value):
        """Set progress value with animation"""
        value = max(self.minimum, min(self.maximum, value))

        self.animation.setStartValue(self.value)
        self.animation.setEndValue(value)
        self.animation.valueChanged.connect(self._update_value)
        self.animation.start()

    def _update_value(self, value):
        """Update internal value and repaint"""
        self.value = value
        self.value_changed.emit(value)
        self.update()

    def setRange(self, minimum, maximum):
        """Set progress range"""
        self.minimum = minimum
        self.maximum = maximum


class ProgressCard(QWidget):
    """Progress card with title and description"""

    def __init__(self, title="Progress", description="", parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self._setup_ui()

    def _setup_ui(self):
        """Setup progress card layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Header
        header_layout = QHBoxLayout()

        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet(
            f"""
            font-size: {Typography.TEXT_BASE}px;
            font-weight: {Typography.WEIGHT_SEMIBOLD};
            color: {ModernColors.TEXT_PRIMARY};
        """
        )
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        self.percentage_label = QLabel("0%")
        self.percentage_label.setStyleSheet(
            f"""
            font-size: {Typography.TEXT_SM}px;
            font-weight: {Typography.WEIGHT_MEDIUM};
            color: {ModernColors.TEXT_SECONDARY};
        """
        )
        header_layout.addWidget(self.percentage_label)

        layout.addLayout(header_layout)

        # Progress bar
        self.progress_bar = ModernProgressBar()
        self.progress_bar.valueChanged.connect(self._update_percentage)
        layout.addWidget(self.progress_bar)

        # Description
        if self.description:
            self.desc_label = QLabel(self.description)
            self.desc_label.setStyleSheet(
                f"""
                font-size: {Typography.TEXT_SM}px;
                color: {ModernColors.TEXT_SECONDARY};
            """
            )
            self.desc_label.setWordWrap(True)
            layout.addWidget(self.desc_label)

        # Card styling
        self.setStyleSheet(
            f"""
            QWidget {{
                background: {ModernColors.SURFACE_SECONDARY};
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: {BorderRadius.MD}px;
            }}
            QWidget:hover {{
                border-color: {ModernColors.PRIMARY};
            }}
        """
        )
        self.setMinimumHeight(100)

    def _update_percentage(self, value):
        """Update percentage display"""
        self.percentage_label.setText(f"{value}%")

        # Change color based on progress
        if value >= 100:
            color = ModernColors.SUCCESS
        elif value >= 75:
            color = ModernColors.PRIMARY
        elif value >= 25:
            color = ModernColors.WARNING
        else:
            color = ModernColors.TEXT_SECONDARY

        self.percentage_label.setStyleSheet(
            f"""
            font-size: {Typography.TEXT_SM}px;
            font-weight: {Typography.WEIGHT_MEDIUM};
            color: {color};
        """
        )

    def set_progress(self, value, description=None):
        """Update progress value and description"""
        self.progress_bar.setValue(value)

        if description and hasattr(self, "desc_label"):
            self.desc_label.setText(description)

        # Start glow animation for active progress
        if 0 < value < 100:
            self.progress_bar.start_glow_animation()
        else:
            self.progress_bar.stop_glow_animation()

    def set_title(self, title):
        """Update progress title"""
        self.title = title
        self.title_label.setText(title)


class MultiStepProgress(QWidget):
    """Multi-step progress indicator"""

    step_completed = pyqtSignal(int)  # step_index

    def __init__(self, steps=None, parent=None):
        super().__init__(parent)
        self.steps = steps or ["Step 1", "Step 2", "Step 3"]
        self.current_step = 0
        self._setup_ui()

    def _setup_ui(self):
        """Setup multi-step progress layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Step indicators
        self.step_layout = QHBoxLayout()
        self.step_layout.setSpacing(4)

        self.step_widgets = []

        for i, step_name in enumerate(self.steps):
            step_widget = self._create_step_widget(i, step_name)
            self.step_widgets.append(step_widget)
            self.step_layout.addWidget(step_widget)

            # Add connector line (except for last step)
            if i < len(self.steps) - 1:
                line = self._create_connector_line()
                self.step_layout.addWidget(line)

        layout.addLayout(self.step_layout)

        # Overall progress bar
        self.overall_progress = ModernProgressBar()
        self.overall_progress.setMaximum(len(self.steps))
        layout.addWidget(self.overall_progress)

    def _create_step_widget(self, index, name):
        """Create individual step widget"""
        widget = QWidget()
        widget.setFixedSize(120, 60)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)

        # Step number circle
        number_label = QLabel(str(index + 1))
        number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        number_label.setFixedSize(24, 24)
        number_label.setStyleSheet(
            f"""
            QLabel {{
                background: {ModernColors.SURFACE_TERTIARY};
                border: 2px solid {ModernColors.TEXT_SECONDARY};
                border-radius: 12px;
                color: {ModernColors.TEXT_SECONDARY};
                font-weight: {Typography.WEIGHT_BOLD};
                font-size: {Typography.TEXT_SM}px;
            }}
        """
        )

        # Center the circle
        circle_layout = QHBoxLayout()
        circle_layout.addStretch()
        circle_layout.addWidget(number_label)
        circle_layout.addStretch()
        layout.addLayout(circle_layout)

        # Step name
        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet(
            f"""
            font-size: {Typography.TEXT_XS}px;
            color: {ModernColors.TEXT_SECONDARY};
            font-weight: {Typography.WEIGHT_MEDIUM};
        """
        )
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

        widget.number_label = number_label
        widget.name_label = name_label
        widget.step_index = index

        return widget

    def _create_connector_line(self):
        """Create connector line between steps"""
        line = QWidget()
        line.setFixedHeight(2)
        line.setStyleSheet(
            f"""
            QWidget {{
                background: {ModernColors.TEXT_SECONDARY};
                border-radius: 1px;
            }}
        """
        )
        return line

    def set_current_step(self, step_index):
        """Set current active step"""
        self.current_step = step_index

        for i, widget in enumerate(self.step_widgets):
            if i < step_index:
                # Completed step
                widget.number_label.setStyleSheet(
                    f"""
                    QLabel {{
                        background: {ModernColors.SUCCESS};
                        border: 2px solid {ModernColors.SUCCESS};
                        border-radius: 12px;
                        color: white;
                        font-weight: {Typography.WEIGHT_BOLD};
                        font-size: {Typography.TEXT_SM}px;
                    }}
                """
                )
                widget.name_label.setStyleSheet(
                    f"""
                    font-size: {Typography.TEXT_XS}px;
                    color: {ModernColors.SUCCESS};
                    font-weight: {Typography.WEIGHT_MEDIUM};
                """
                )
            elif i == step_index:
                # Current step
                widget.number_label.setStyleSheet(
                    f"""
                    QLabel {{
                        background: {ModernColors.PRIMARY};
                        border: 2px solid {ModernColors.PRIMARY};
                        border-radius: 12px;
                        color: white;
                        font-weight: {Typography.WEIGHT_BOLD};
                        font-size: {Typography.TEXT_SM}px;
                    }}
                """
                )
                widget.name_label.setStyleSheet(
                    f"""
                    font-size: {Typography.TEXT_XS}px;
                    color: {ModernColors.PRIMARY};
                    font-weight: {Typography.WEIGHT_SEMIBOLD};
                """
                )
            else:
                # Future step
                widget.number_label.setStyleSheet(
                    f"""
                    QLabel {{
                        background: {ModernColors.SURFACE_TERTIARY};
                        border: 2px solid {ModernColors.TEXT_SECONDARY};
                        border-radius: 12px;
                        color: {ModernColors.TEXT_SECONDARY};
                        font-weight: {Typography.WEIGHT_BOLD};
                        font-size: {Typography.TEXT_SM}px;
                    }}
                """
                )
                widget.name_label.setStyleSheet(
                    f"""
                    font-size: {Typography.TEXT_XS}px;
                    color: {ModernColors.TEXT_SECONDARY};
                    font-weight: {Typography.WEIGHT_MEDIUM};
                """
                )

        # Update overall progress
        self.overall_progress.setValue(step_index)

        if step_index > 0:
            self.step_completed.emit(step_index - 1)

    def next_step(self):
        """Move to next step"""
        if self.current_step < len(self.steps):
            self.set_current_step(self.current_step + 1)

    def previous_step(self):
        """Move to previous step"""
        if self.current_step > 0:
            self.set_current_step(self.current_step - 1)

    def reset(self):
        """Reset to first step"""
        self.set_current_step(0)


# Backward compatibility
HolographicProgressBar = ModernProgressBar
