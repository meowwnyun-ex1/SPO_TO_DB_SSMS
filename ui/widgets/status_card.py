# ui/widgets/status_card.py - Modern 2025 Status Card
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QColor
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
        SUCCESS = "#10B981"
        ERROR = "#EF4444"
        WARNING = "#F59E0B"
        TEXT_PRIMARY = "#F8FAFC"


class StatusDot(QWidget):
    """Animated status indicator dot"""

    def __init__(self, size=8, parent=None):
        super().__init__(parent)
        self.status = "disconnected"
        self.dot_size = size
        self.setFixedSize(size + 4, size + 4)

        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self.update)
        self.pulse_value = 0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        colors = {
            "connected": ModernColors.SUCCESS,
            "disconnected": ModernColors.ERROR,
            "connecting": ModernColors.WARNING,
            "syncing": ModernColors.PRIMARY,
            "error": ModernColors.ERROR,
        }

        base_color = QColor(colors.get(self.status, ModernColors.ERROR))

        # Draw pulsing ring for active states
        if self.status in ["connecting", "syncing"] and self.pulse_timer.isActive():
            ring_color = QColor(base_color)
            ring_color.setAlpha(int(100 * (1 - self.pulse_value)))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(ring_color)
            ring_size = self.dot_size + int(4 * self.pulse_value)
            painter.drawEllipse(
                2 - int(2 * self.pulse_value),
                2 - int(2 * self.pulse_value),
                ring_size,
                ring_size,
            )

        # Draw main dot
        painter.setBrush(base_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, self.dot_size, self.dot_size)

    def set_status(self, status):
        self.status = status
        if status in ["connecting", "syncing"]:
            self.pulse_timer.start(50)
        else:
            self.pulse_timer.stop()
            self.pulse_value = 0
        self.update()

    def _update_pulse(self):
        self.pulse_value = (self.pulse_value + 0.1) % 1.0


class ModernStatusCard(QWidget):
    """2025 Modern status card with animations"""

    status_clicked = pyqtSignal(str)

    def __init__(self, title, initial_status="disconnected", parent=None):
        super().__init__(parent)
        self.title = title
        self.status = initial_status
        self._setup_ui()
        self._setup_animations()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        # Header with title and status dot
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet(
            f"""
            font-size: {Typography.TEXT_SM}px;
            font-weight: {Typography.WEIGHT_MEDIUM};
            color: {ModernColors.TEXT_SECONDARY};
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """
        )
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # Status dot
        self.status_dot = StatusDot(8)
        self.status_dot.set_status(self.status)
        header_layout.addWidget(self.status_dot)

        layout.addLayout(header_layout)

        # Status text
        self.status_label = QLabel(self._format_status(self.status))
        self.status_label.setStyleSheet(
            f"""
            font-size: {Typography.TEXT_BASE}px;
            font-weight: {Typography.WEIGHT_SEMIBOLD};
            color: {self._get_status_color(self.status)};
        """
        )
        layout.addWidget(self.status_label)

        # Card styling
        self._update_card_style()
        self.setMinimumHeight(70)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _setup_animations(self):
        # Hover animation
        self.hover_animation = QPropertyAnimation(self, b"styleSheet")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _format_status(self, status):
        status_map = {
            "connected": "Connected",
            "disconnected": "Disconnected",
            "connecting": "Connecting...",
            "syncing": "Syncing...",
            "error": "Error",
            "success": "Success",
        }
        return status_map.get(status, status.title())

    def _get_status_color(self, status):
        colors = {
            "connected": ModernColors.SUCCESS,
            "disconnected": ModernColors.ERROR,
            "connecting": ModernColors.WARNING,
            "syncing": ModernColors.PRIMARY,
            "error": ModernColors.ERROR,
            "success": ModernColors.SUCCESS,
        }
        return colors.get(status, ModernColors.TEXT_PRIMARY)

    def _update_card_style(self):
        border_color = self._get_status_color(self.status)
        self.setStyleSheet(
            f"""
            QWidget {{
                background: {ModernColors.SURFACE_SECONDARY};
                border: 1px solid {border_color}40;
                border-radius: {BorderRadius.BASE}px;
            }}
            QWidget:hover {{
                border-color: {border_color};
                background: rgba(30, 41, 59, 0.8);
                transform: translateY(-1px);
            }}
        """
        )

    def set_status(self, status):
        """Update card status with animation"""
        if self.status == status:
            return

        self.status = status
        self.status_dot.set_status(status)

        # Update text with color transition
        new_color = self._get_status_color(status)
        self.status_label.setText(self._format_status(status))
        self.status_label.setStyleSheet(
            f"""
            font-size: {Typography.TEXT_BASE}px;
            font-weight: {Typography.WEIGHT_SEMIBOLD};
            color: {new_color};
        """
        )

        # Update card border
        self._update_card_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.status_clicked.emit(self.title)
        super().mousePressEvent(event)


class CompactStatusCard(QWidget):
    """Compact version for tight spaces"""

    def __init__(self, title, initial_status="disconnected", parent=None):
        super().__init__(parent)
        self.title = title
        self.status = initial_status
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # Status dot
        self.status_dot = StatusDot(6)
        self.status_dot.set_status(self.status)
        layout.addWidget(self.status_dot)

        # Title
        title_label = QLabel(self.title)
        title_label.setStyleSheet(
            f"""
            font-size: {Typography.TEXT_SM}px;
            color: {ModernColors.TEXT_PRIMARY};
            font-weight: {Typography.WEIGHT_MEDIUM};
        """
        )
        layout.addWidget(title_label)

        layout.addStretch()

        # Status text
        self.status_label = QLabel(self._format_status(self.status))
        self.status_label.setStyleSheet(
            f"""
            font-size: {Typography.TEXT_SM}px;
            color: {self._get_status_color(self.status)};
            font-weight: {Typography.WEIGHT_MEDIUM};
        """
        )
        layout.addWidget(self.status_label)

        # Compact styling
        self.setStyleSheet(
            f"""
            QWidget {{
                background: {ModernColors.SURFACE_TERTIARY};
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: {BorderRadius.SM}px;
            }}
        """
        )
        self.setMaximumHeight(40)

    def _format_status(self, status):
        status_map = {
            "connected": "✓",
            "disconnected": "✗",
            "connecting": "⟳",
            "syncing": "⟳",
            "error": "!",
            "success": "✓",
        }
        return status_map.get(status, "?")

    def _get_status_color(self, status):
        colors = {
            "connected": ModernColors.SUCCESS,
            "disconnected": ModernColors.ERROR,
            "connecting": ModernColors.WARNING,
            "syncing": ModernColors.PRIMARY,
            "error": ModernColors.ERROR,
            "success": ModernColors.SUCCESS,
        }
        return colors.get(status, ModernColors.TEXT_SECONDARY)

    def set_status(self, status):
        self.status = status
        self.status_dot.set_status(status)
        self.status_label.setText(self._format_status(status))
        self.status_label.setStyleSheet(
            f"""
            font-size: {Typography.TEXT_SM}px;
            color: {self._get_status_color(status)};
            font-weight: {Typography.WEIGHT_MEDIUM};
        """
        )


class StatusCardGroup(QWidget):
    """Container for managing multiple status cards"""

    def __init__(self, cards_config=None, compact=False, parent=None):
        super().__init__(parent)
        self.cards = {}
        self.compact = compact
        self._setup_ui(cards_config or [])

    def _setup_ui(self, cards_config):
        if self.compact:
            layout = QVBoxLayout(self)
            layout.setSpacing(4)
        else:
            layout = QGridLayout(self)
            layout.setSpacing(12)

        layout.setContentsMargins(0, 0, 0, 0)

        for i, config in enumerate(cards_config):
            card_id = config.get("id", f"card_{i}")
            title = config.get("title", f"Status {i+1}")
            initial_status = config.get("status", "disconnected")

            if self.compact:
                card = CompactStatusCard(title, initial_status)
                layout.addWidget(card)
            else:
                card = ModernStatusCard(title, initial_status)
                row = i // 2
                col = i % 2
                layout.addWidget(card, row, col)

            self.cards[card_id] = card

    def update_status(self, card_id, status):
        """Update specific card status"""
        if card_id in self.cards:
            self.cards[card_id].set_status(status)

    def get_card(self, card_id):
        """Get card instance by ID"""
        return self.cards.get(card_id)

    def add_card(self, card_id, title, initial_status="disconnected"):
        """Dynamically add new card"""
        if self.compact:
            card = CompactStatusCard(title, initial_status)
        else:
            card = ModernStatusCard(title, initial_status)

        self.cards[card_id] = card
        self.layout().addWidget(card)
        return card

    def remove_card(self, card_id):
        """Remove card by ID"""
        if card_id in self.cards:
            card = self.cards.pop(card_id)
            self.layout().removeWidget(card)
            card.deleteLater()


# Factory functions
def create_status_card(title, status="disconnected", compact=False, parent=None):
    """Create status card instance"""
    if compact:
        return CompactStatusCard(title, status, parent)
    return ModernStatusCard(title, status, parent)


def create_status_group(cards_config, compact=False, parent=None):
    """Create status card group"""
    return StatusCardGroup(cards_config, compact, parent)
