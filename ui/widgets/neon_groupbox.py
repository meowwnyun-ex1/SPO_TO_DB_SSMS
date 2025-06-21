# ui/widgets/neon_groupbox.py - Modern 2025 GroupBox
from PyQt6.QtWidgets import (
    QGroupBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QFont
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
        SURFACE_TERTIARY = "#334155"
        TEXT_PRIMARY = "#F8FAFC"
        GLASS_BORDER = "rgba(255, 255, 255, 0.1)"


class ModernGroupBox(QGroupBox):
    """2025 Modern GroupBox with enhanced styling"""

    def __init__(self, title="", icon="", collapsible=False, parent=None):
        super().__init__(title, parent)
        self.icon = icon
        self.collapsible = collapsible
        self.is_collapsed = False
        self._setup_style()

        if collapsible:
            self._setup_collapsible()

    def _setup_style(self):
        """Setup modern group box styling"""
        display_title = f"{self.icon} {self.title()}" if self.icon else self.title()
        self.setTitle(display_title)

        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setFont(
            QFont(
                Typography.PRIMARY_FONT,
                Typography.TEXT_BASE,
                Typography.WEIGHT_SEMIBOLD,
            )
        )

        self.setStyleSheet(
            f"""
            QGroupBox {{
                background: {ModernColors.SURFACE_SECONDARY};
                border: 1px solid {ModernColors.GLASS_BORDER};
                border-radius: {BorderRadius.MD}px;
                margin-top: 16px;
                padding-top: 20px;
                color: {ModernColors.TEXT_PRIMARY};
                font-weight: {Typography.WEIGHT_SEMIBOLD};
                font-size: {Typography.TEXT_BASE}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 8px 16px;
                background: {ModernColors.PRIMARY};
                border: none;
                border-radius: {BorderRadius.SM}px;
                color: white;
                font-weight: {Typography.WEIGHT_SEMIBOLD};
                font-size: {Typography.TEXT_SM}px;
                left: 12px;
                top: -8px;
            }}
        """
        )

    def _setup_collapsible(self):
        """Setup collapsible functionality"""
        # Make title clickable for collapsible groups
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Animation for collapse/expand
        self.animation = QPropertyAnimation(self, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Store original height
        self.original_height = self.sizeHint().height()

    def mousePressEvent(self, event):
        """Handle mouse press for collapsible groups"""
        if self.collapsible and event.button() == Qt.MouseButton.LeftButton:
            # Check if click is in title area
            title_rect = self.style().subControlRect(
                self.style().ComplexControl.CC_GroupBox,
                self.style().SubControl.SC_GroupBoxLabel,
                None,
                self,
            )

            if title_rect.contains(event.pos()):
                self.toggle_collapsed()
                return

        super().mousePressEvent(event)

    def toggle_collapsed(self):
        """Toggle collapsed state"""
        self.is_collapsed = not self.is_collapsed

        if self.is_collapsed:
            self.collapse()
        else:
            self.expand()

    def collapse(self):
        """Collapse the group box"""
        self.is_collapsed = True

        # Update title to show collapsed state
        title = self.title()
        if not title.endswith(" ▶"):
            title = title.replace(" ▼", "") + " ▶"
            self.setTitle(title)

        # Animate to collapsed height (just title)
        self.animation.setStartValue(self.height())
        self.animation.setEndValue(50)  # Just enough for title
        self.animation.start()

        # Hide content
        for child in self.findChildren(QWidget):
            if child != self:
                child.hide()

    def expand(self):
        """Expand the group box"""
        self.is_collapsed = False

        # Update title to show expanded state
        title = self.title()
        if not title.endswith(" ▼"):
            title = title.replace(" ▶", "") + " ▼"
            self.setTitle(title)

        # Show content first
        for child in self.findChildren(QWidget):
            if child != self:
                child.show()

        # Animate to expanded height
        self.animation.setStartValue(self.height())
        self.animation.setEndValue(self.sizeHint().height())
        self.animation.start()

    def set_variant(self, variant):
        """Set group box color variant"""
        variants = {
            "primary": ModernColors.PRIMARY,
            "success": ModernColors.SUCCESS,
            "warning": ModernColors.WARNING,
            "error": ModernColors.ERROR,
            "info": "#06B6D4",  # Cyan
        }

        color = variants.get(variant, ModernColors.PRIMARY)

        self.setStyleSheet(
            f"""
            QGroupBox {{
                background: {ModernColors.SURFACE_SECONDARY};
                border: 1px solid {color}40;
                border-radius: {BorderRadius.MD}px;
                margin-top: 16px;
                padding-top: 20px;
                color: {ModernColors.TEXT_PRIMARY};
                font-weight: {Typography.WEIGHT_SEMIBOLD};
                font-size: {Typography.TEXT_BASE}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 8px 16px;
                background: {color};
                border: none;
                border-radius: {BorderRadius.SM}px;
                color: white;
                font-weight: {Typography.WEIGHT_SEMIBOLD};
                font-size: {Typography.TEXT_SM}px;
                left: 12px;
                top: -8px;
            }}
        """
        )


class CardGroupBox(QWidget):
    """Card-style group box alternative"""

    def __init__(self, title="", icon="", parent=None):
        super().__init__(parent)
        self.title_text = title
        self.icon = icon
        self._setup_ui()

    def _setup_ui(self):
        """Setup card-style group box"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        self.header = QWidget()
        self.header.setStyleSheet(
            f"""
            QWidget {{
                background: {ModernColors.PRIMARY};
                border-radius: {BorderRadius.SM}px {BorderRadius.SM}px 0 0;
                padding: 12px 16px;
            }}
        """
        )

        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Title
        display_title = (
            f"{self.icon} {self.title_text}" if self.icon else self.title_text
        )
        self.title_label = QLabel(display_title)
        self.title_label.setStyleSheet(
            f"""
            color: white;
            font-size: {Typography.TEXT_BASE}px;
            font-weight: {Typography.WEIGHT_SEMIBOLD};
        """
        )
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        layout.addWidget(self.header)

        # Content area
        self.content_area = QWidget()
        self.content_area.setStyleSheet(
            f"""
            QWidget {{
                background: {ModernColors.SURFACE_SECONDARY};
                border: 1px solid {ModernColors.GLASS_BORDER};
                border-top: none;
                border-radius: 0 0 {BorderRadius.SM}px {BorderRadius.SM}px;
                padding: 16px;
            }}
        """
        )

        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.content_area)

    def addWidget(self, widget):
        """Add widget to content area"""
        self.content_layout.addWidget(widget)

    def addLayout(self, layout):
        """Add layout to content area"""
        self.content_layout.addLayout(layout)

    def setTitle(self, title):
        """Set card title"""
        self.title_text = title
        display_title = f"{self.icon} {title}" if self.icon else title
        self.title_label.setText(display_title)


class AccordionGroupBox(QWidget):
    """Accordion-style collapsible group box"""

    toggled = pyqtSignal(bool)  # expanded state

    def __init__(self, title="", icon="", expanded=False, parent=None):
        super().__init__(parent)
        self.title_text = title
        self.icon = icon
        self.is_expanded = expanded
        self._setup_ui()

    def _setup_ui(self):
        """Setup accordion group box"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        # Toggle button (header)
        self.toggle_btn = QPushButton()
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(self.is_expanded)
        self.toggle_btn.clicked.connect(self._on_toggle)
        self._update_toggle_text()

        self.toggle_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {ModernColors.SURFACE_TERTIARY};
                border: 1px solid {ModernColors.GLASS_BORDER};
                border-radius: {BorderRadius.SM}px;
                padding: 12px 16px;
                text-align: left;
                font-size: {Typography.TEXT_BASE}px;
                font-weight: {Typography.WEIGHT_MEDIUM};
                color: {ModernColors.TEXT_PRIMARY};
            }}
            QPushButton:hover {{
                background: {ModernColors.SURFACE_ELEVATED};
                border-color: {ModernColors.PRIMARY};
            }}
            QPushButton:checked {{
                background: {ModernColors.PRIMARY};
                color: white;
                border-color: {ModernColors.PRIMARY};
            }}
        """
        )

        layout.addWidget(self.toggle_btn)

        # Content container
        self.content_container = QWidget()
        self.content_container.setStyleSheet(
            f"""
            QWidget {{
                background: {ModernColors.SURFACE_SECONDARY};
                border: 1px solid {ModernColors.GLASS_BORDER};
                border-top: none;
                border-radius: 0 0 {BorderRadius.SM}px {BorderRadius.SM}px;
                padding: 16px;
            }}
        """
        )

        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.content_container)

        # Set initial state
        self.content_container.setVisible(self.is_expanded)

        # Animation
        self.animation = QPropertyAnimation(self.content_container, b"maximumHeight")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _update_toggle_text(self):
        """Update toggle button text"""
        arrow = "▼" if self.is_expanded else "▶"
        display_title = (
            f"{self.icon} {self.title_text} {arrow}"
            if self.icon
            else f"{self.title_text} {arrow}"
        )
        self.toggle_btn.setText(display_title)

    def _on_toggle(self, checked):
        """Handle toggle button click"""
        self.is_expanded = checked
        self._update_toggle_text()
