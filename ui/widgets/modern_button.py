# ui/widgets/modern_button.py - Modern 2025 Button System
from PyQt6.QtWidgets import QPushButton, QSizePolicy
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal
from PyQt6.QtGui import QFont
import sys
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from ui.styles.theme import ModernColors, Typography, BorderRadius, get_button_style
except ImportError:
    # Fallback minimal colors
    class ModernColors:
        PRIMARY = "#6366F1"
        SUCCESS = "#10B981"
        ERROR = "#EF4444"
        TEXT_PRIMARY = "#F8FAFC"


class ModernButton(QPushButton):
    """2025 Modern Button with animations and variants"""

    clicked_with_animation = pyqtSignal()

    def __init__(self, text="", icon="", variant="primary", size="md", parent=None):
        super().__init__(parent)

        self.variant = variant
        self.size = size
        self.icon = icon
        self.is_animating = False

        # Setup button content
        display_text = f"{icon} {text}" if icon and text else (text or icon)
        self.setText(display_text)

        # Apply styling
        self._apply_style()
        self._setup_animations()

        # Properties
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def _apply_style(self):
        """Apply modern styling based on variant and size"""
        # Font configuration
        font_sizes = {"sm": 12, "md": 14, "lg": 16}
        font = QFont(Typography.PRIMARY_FONT, font_sizes.get(self.size, 14))
        font.setWeight(Typography.WEIGHT_MEDIUM)
        self.setFont(font)

        # Size configuration
        heights = {"sm": 32, "md": 40, "lg": 48}
        self.setMinimumHeight(heights.get(self.size, 40))

        # Apply button style
        self.setStyleSheet(get_button_style(self.variant, self.size))

        # Size policy
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

    def _setup_animations(self):
        """Setup smooth animations"""
        # Scale animation for press effect
        self.scale_animation = QPropertyAnimation(self, b"geometry")
        self.scale_animation.setDuration(150)
        self.scale_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Store original geometry
        self.original_geometry = None

    def mousePressEvent(self, event):
        """Handle mouse press with animation"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_press_animation()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release with animation"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_release_animation()
        super().mouseReleaseEvent(event)

        # Emit custom signal after animation
        if self.rect().contains(event.pos()):
            self.clicked_with_animation.emit()

    def _start_press_animation(self):
        """Start press down animation"""
        if self.is_animating:
            return

        self.is_animating = True
        current_rect = self.geometry()

        # Store original if not set
        if self.original_geometry is None:
            self.original_geometry = current_rect

        # Create pressed geometry (slightly smaller)
        pressed_rect = QRect(
            current_rect.x() + 1,
            current_rect.y() + 1,
            current_rect.width() - 2,
            current_rect.height() - 2,
        )

        self.scale_animation.setStartValue(current_rect)
        self.scale_animation.setEndValue(pressed_rect)
        self.scale_animation.start()

    def _start_release_animation(self):
        """Start release animation back to original size"""
        if not self.is_animating or self.original_geometry is None:
            self.is_animating = False
            return

        current_rect = self.geometry()

        self.scale_animation.setStartValue(current_rect)
        self.scale_animation.setEndValue(self.original_geometry)
        self.scale_animation.finished.connect(self._animation_finished)
        self.scale_animation.start()

    def _animation_finished(self):
        """Reset animation state"""
        self.is_animating = False
        try:
            self.scale_animation.finished.disconnect()
        except TypeError:
            pass

    def resizeEvent(self, event):
        """Update original geometry on resize"""
        super().resizeEvent(event)
        if not self.is_animating:
            self.original_geometry = self.geometry()

    def set_variant(self, variant: str):
        """Change button variant"""
        self.variant = variant
        self._apply_style()

    def set_size(self, size: str):
        """Change button size"""
        self.size = size
        self._apply_style()

    def set_loading(self, loading: bool):
        """Set loading state"""
        if loading:
            self.setText("⏳ Loading...")
            self.setEnabled(False)
        else:
            display_text = f"{self.icon} {self.text()}" if self.icon else self.text()
            self.setText(display_text)
            self.setEnabled(True)


class IconButton(ModernButton):
    """Icon-only button for compact spaces"""

    def __init__(self, icon="", variant="ghost", size="md", tooltip="", parent=None):
        super().__init__("", icon, variant, size, parent)

        # Make it square
        sizes = {"sm": 32, "md": 40, "lg": 48}
        button_size = sizes.get(size, 40)
        self.setFixedSize(button_size, button_size)

        # Set tooltip if provided
        if tooltip:
            self.setToolTip(tooltip)

        # Icon-specific styling
        self.setStyleSheet(
            self.styleSheet()
            + f"""
            QPushButton {{
                text-align: center;
                padding: 0px;
            }}
        """
        )


class ActionButton(ModernButton):
    """Pre-configured action buttons for common actions"""

    @classmethod
    def primary(cls, text, icon="", size="md", parent=None):
        return cls(text, icon, "primary", size, parent)

    @classmethod
    def secondary(cls, text, icon="", size="md", parent=None):
        return cls(text, icon, "secondary", size, parent)

    @classmethod
    def accent(cls, text, icon="", size="md", parent=None):
        return cls(text, icon, "accent", size, parent)

    @classmethod
    def success(cls, text, icon="", size="md", parent=None):
        return cls(text, icon, "success", size, parent)

    @classmethod
    def danger(cls, text, icon="", size="md", parent=None):
        return cls(text, icon, "danger", size, parent)

    @classmethod
    def ghost(cls, text, icon="", size="md", parent=None):
        return cls(text, icon, "ghost", size, parent)


class FloatingActionButton(IconButton):
    """Floating Action Button (FAB) for primary actions"""

    def __init__(self, icon="➕", tooltip="Add", parent=None):
        super().__init__(icon, "primary", "lg", tooltip, parent)

        # FAB-specific styling
        self.setStyleSheet(
            self.styleSheet()
            + f"""
            QPushButton {{
                border-radius: 24px;
                box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
            }}
            QPushButton:hover {{
                transform: translateY(-2px);
                box-shadow: 0 12px 35px rgba(99, 102, 241, 0.5);
            }}
        """
        )

        # Position as floating
        self.setFixedSize(48, 48)


class ButtonGroup(object):
    """Utility class for managing button groups"""

    def __init__(self, buttons=None, exclusive=True):
        self.buttons = buttons or []
        self.exclusive = exclusive
        self.active_button = None

        self._setup_group()

    def _setup_group(self):
        """Setup button group behavior"""
        for button in self.buttons:
            button.clicked.connect(
                lambda checked, btn=button: self._on_button_clicked(btn)
            )

    def _on_button_clicked(self, clicked_button):
        """Handle button click in group"""
        if self.exclusive:
            # Deactivate all other buttons
            for button in self.buttons:
                if button != clicked_button:
                    button.set_variant("ghost")

            # Activate clicked button
            clicked_button.set_variant("primary")
            self.active_button = clicked_button

    def add_button(self, button):
        """Add button to group"""
        self.buttons.append(button)
        button.clicked.connect(lambda checked, btn=button: self._on_button_clicked(btn))

    def remove_button(self, button):
        """Remove button from group"""
        if button in self.buttons:
            self.buttons.remove(button)
            try:
                button.clicked.disconnect()
            except TypeError:
                pass

    def set_active(self, button):
        """Set specific button as active"""
        if button in self.buttons:
            self._on_button_clicked(button)


class ToggleButton(ModernButton):
    """Toggle button with on/off states"""

    toggled = pyqtSignal(bool)

    def __init__(self, text="", icon="", size="md", parent=None):
        super().__init__(text, icon, "ghost", size, parent)

        self.is_toggled = False
        self.off_text = text
        self.on_text = text
        self.off_icon = icon
        self.on_icon = icon

        self.clicked.connect(self._toggle)

    def _toggle(self):
        """Toggle button state"""
        self.is_toggled = not self.is_toggled
        self._update_appearance()
        self.toggled.emit(self.is_toggled)

    def _update_appearance(self):
        """Update button appearance based on state"""
        if self.is_toggled:
            self.set_variant("primary")
            display_text = (
                f"{self.on_icon} {self.on_text}" if self.on_icon else self.on_text
            )
        else:
            self.set_variant("ghost")
            display_text = (
                f"{self.off_icon} {self.off_text}" if self.off_icon else self.off_text
            )

        self.setText(display_text)

    def set_toggle_text(self, off_text: str, on_text: str):
        """Set different text for on/off states"""
        self.off_text = off_text
        self.on_text = on_text
        self._update_appearance()

    def set_toggle_icon(self, off_icon: str, on_icon: str):
        """Set different icons for on/off states"""
        self.off_icon = off_icon
        self.on_icon = on_icon
        self._update_appearance()

    def set_toggled(self, toggled: bool, emit_signal=True):
        """Programmatically set toggle state"""
        if self.is_toggled != toggled:
            self.is_toggled = toggled
            self._update_appearance()
            if emit_signal:
                self.toggled.emit(self.is_toggled)


class SplitButton(ModernButton):
    """Split button with dropdown arrow"""

    dropdown_clicked = pyqtSignal()

    def __init__(self, text="", icon="", variant="primary", size="md", parent=None):
        super().__init__(text, icon, variant, size, parent)

        # Add dropdown arrow
        current_text = self.text()
        self.setText(f"{current_text} ▼")

        # Override click behavior
        self.clicked.disconnect()
        self.clicked.connect(self._handle_click)

    def _handle_click(self):
        """Handle click on split button"""
        # For now, just emit dropdown signal
        # In a real implementation, you'd check click position
        self.dropdown_clicked.emit()

    def mousePressEvent(self, event):
        """Handle split button click detection"""
        # Calculate if click is on dropdown area (right 25%)
        click_x = event.pos().x()
        button_width = self.width()
        dropdown_start = button_width * 0.75

        if click_x >= dropdown_start:
            # Clicked on dropdown area
            self.dropdown_clicked.emit()
        else:
            # Clicked on main button area
            super().mousePressEvent(event)


# Quick creation functions
def create_primary_button(text, icon="", size="md", parent=None):
    """Quick primary button creation"""
    return ActionButton.primary(text, icon, size, parent)


def create_icon_button(icon, tooltip="", variant="ghost", size="md", parent=None):
    """Quick icon button creation"""
    return IconButton(icon, variant, size, tooltip, parent)


def create_fab(icon="➕", tooltip="Add", parent=None):
    """Quick FAB creation"""
    return FloatingActionButton(icon, tooltip, parent)
