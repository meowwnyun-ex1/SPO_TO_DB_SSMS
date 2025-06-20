from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ..styles.theme import get_modern_button_style, UltraModernColors


class ModernButton(QPushButton):
    """Modern button with enhanced animations and styling"""

    def __init__(self, text="", variant="primary", size="md", icon="", parent=None):
        super().__init__(parent)
        self.variant = variant
        self.size = size
        self.icon = icon

        # Setup text with icon if provided
        display_text = f"{icon} {text}" if icon else text
        self.setText(display_text)

        # Set font based on size
        font_sizes = {"sm": 12, "md": 14, "lg": 16}
        font = QFont("Segoe UI", font_sizes.get(size, 14), QFont.Weight.DemiBold)
        self.setFont(font)

        # Apply styling
        self.setStyleSheet(get_modern_button_style(variant, size))

        # Set cursor
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Animation setup
        self.setup_animations()

    def setup_animations(self):
        """Setup hover and press animations"""
        # Note: Qt stylesheets handle most animations
        # This is for additional custom animations if needed
        pass

    def set_variant(self, variant):
        """Change button variant"""
        self.variant = variant
        self.setStyleSheet(get_modern_button_style(variant, self.size))

    def set_loading(self, loading=True):
        """Set loading state"""
        if loading:
            self.setText("⏳ Loading...")
            self.setEnabled(False)
        else:
            # Restore original text
            display_text = f"{self.icon} {self.text()}" if self.icon else self.text()
            self.setText(display_text.replace("⏳ Loading...", ""))
            self.setEnabled(True)


class IconButton(ModernButton):
    """Icon-only button"""

    def __init__(self, icon="", variant="ghost", size="md", parent=None):
        super().__init__("", variant, size, parent=parent)
        self.setText(icon)
        self.setFixedSize(40, 40) if size == "md" else self.setFixedSize(32, 32)


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
