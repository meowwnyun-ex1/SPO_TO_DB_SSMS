from PyQt6.QtWidgets import QPushButton, QSizePolicy  # Added QSizePolicy
from PyQt6.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    QPoint,
)  # Added QRect, QPoint for better animation control
from PyQt6.QtGui import QFont  # Added QPainter for custom drawing if needed
from ..styles.theme import get_modern_button_style, UltraModernColors


class ModernButton(QPushButton):
    """Modern button with enhanced animations and styling"""

    def __init__(self, text="", variant="primary", size="md", icon="", parent=None):
        super().__init__(parent)
        self.variant = variant
        self.size = size
        self.icon = icon

        # Setup text with icon if provided
        display_text = f"{icon} {text}" if icon and text else text if text else icon
        self.setText(display_text)

        # Set font based on size
        font_sizes = {"sm": 12, "md": 14, "lg": 16}
        font = QFont("Segoe UI", font_sizes.get(size, 14), QFont.Weight.DemiBold)
        self.setFont(font)

        # Apply styling
        self.setStyleSheet(get_modern_button_style(variant, size))

        # Set cursor
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Set size policy to expand horizontally, but maintain content for height
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Animation setup (minimal, relying mostly on stylesheet for hover/press)
        # For more complex animations (e.g., movement), QPropertyAnimation is used.
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)

        self.original_pos = self.pos()  # Store original position for hover animation

    def enterEvent(self, event):
        """Handle mouse hover enter event."""
        super().enterEvent(event)
        self.original_pos = self.pos()  # Update original position in case button moved
        if self.animation.state() == QPropertyAnimation.State.Running:
            self.animation.stop()

        # Move button slightly up for a "lift" effect
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(self.original_pos - QPoint(0, 2))
        self.animation.start()

    def leaveEvent(self, event):
        """Handle mouse hover leave event."""
        super().leaveEvent(event)
        if self.animation.state() == QPropertyAnimation.State.Running:
            self.animation.stop()

        # Move button back to original position
        self.animation.setStartValue(self.pos())
        self.animation.setEndValue(self.original_pos)
        self.animation.start()

    def set_variant(self, variant):
        """Sets the button variant (primary, secondary, ghost, danger, success)."""
        self.variant = variant
        self.setStyleSheet(get_modern_button_style(self.variant, self.size))

    def set_size(self, size):
        """Sets the button size (sm, md, lg)."""
        self.size = size
        font_sizes = {"sm": 12, "md": 14, "lg": 16}
        font = QFont("Segoe UI", font_sizes.get(size, 14), QFont.Weight.DemiBold)
        self.setFont(font)
        self.setStyleSheet(get_modern_button_style(self.variant, self.size))

    def set_icon(self, icon):
        """Sets the button icon (uses text, e.g., emoji or FontAwesome unicode)."""
        self.icon = icon
        display_text = (
            f"{self.icon} {self.text()}"
            if self.icon and self.text()
            else (self.text() if self.text() else self.icon)
        )
        self.setText(display_text)
        # Note: self.text() needs to be handled carefully if it already includes an old icon.
        # For simplicity, if setting a new icon, assume old icon is replaced.

    def setEnabled(self, a0: bool) -> None:
        """Override setEnabled to apply appropriate styles when disabled/enabled."""
        super().setEnabled(a0)
        if a0:
            # Re-apply default style when enabled
            self.setStyleSheet(get_modern_button_style(self.variant, self.size))
        else:
            # Apply disabled style (e.g., desaturate, lower opacity)
            disabled_style = (
                get_modern_button_style(self.variant, self.size)
                + f"""
                QPushButton:disabled {{
                    background: {UltraModernColors.GLASS_BG_DARK};
                    border: 1px solid {UltraModernColors.GLASS_BORDER};
                    color: {UltraModernColors.TEXT_SECONDARY_ALT};
                    opacity: 0.6;
                }}
            """
            )
            self.setStyleSheet(disabled_style)


class IconButton(ModernButton):
    """Icon-only button"""

    def __init__(self, icon="", variant="ghost", size="md", parent=None):
        super().__init__("", variant, size, parent=parent)  # Pass empty text
        self.setText(icon)  # Set icon as text
        # Set fixed size for icon buttons
        if size == "sm":
            self.setFixedSize(32, 32)
        elif size == "lg":
            self.setFixedSize(48, 48)
        else:  # md
            self.setFixedSize(40, 40)
        self.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )  # Fixed size policy


class ActionButton(ModernButton):
    """Pre-styled action buttons"""

    @classmethod
    def primary(cls, text, icon="", size="md", parent=None):
        return cls(text, "primary", size, icon, parent)

    @classmethod
    def secondary(cls, text, icon="", size="md", parent=None):
        return cls(text, "secondary", size, icon, parent)

    @classmethod
    def ghost(cls, text, icon="", size="md", parent=None):
        return cls(text, "ghost", size, icon, parent)

    @classmethod
    def danger(cls, text, icon="", size="md", parent=None):
        btn = cls(text, "primary", size, icon, parent)
        btn.setStyleSheet(
            btn.styleSheet().replace(
                UltraModernColors.PRIMARY_GRADIENT, UltraModernColors.ERROR_GRADIENT
            )
        )
        return btn

    @classmethod
    def success(cls, text, icon="", size="md", parent=None):
        btn = cls(text, "primary", size, icon, parent)
        btn.setStyleSheet(
            btn.styleSheet().replace(
                UltraModernColors.PRIMARY_GRADIENT, UltraModernColors.SUCCESS_GRADIENT
            )
        )
        return btn
