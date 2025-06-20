# ui/widgets/navigation_bar.py - Compact Navigation Bar
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QButtonGroup, QLabel
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
import logging

try:
    from ..styles.theme import get_navbar_style, UltraModernColors, CompactScaling
except ImportError:
    # Fallback if import fails
    def get_navbar_style():
        return ""

    class UltraModernColors:
        TEXT_PRIMARY = "#E0E0E0"
        NEON_BLUE = "#00D4FF"

    class CompactScaling:
        FONT_SIZE_SMALL = 8
        NAVBAR_HEIGHT = 32


logger = logging.getLogger(__name__)


class NavigationButton(QPushButton):
    """Custom navigation button with icon and compact design"""

    def __init__(self, text: str, icon: str = "", nav_id: str = "", parent=None):
        super().__init__(parent)
        self.nav_id = nav_id
        self.icon = icon

        # Set button properties
        self.setCheckable(True)
        self.setAutoExclusive(False)  # We'll handle this with QButtonGroup

        # Set text with icon
        display_text = f"{icon} {text}" if icon else text
        self.setText(display_text)

        # Set font
        font = QFont("Segoe UI", CompactScaling.FONT_SIZE_SMALL, QFont.Weight.Normal)
        self.setFont(font)

        # Apply styling
        self.setStyleSheet(
            f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {UltraModernColors.TEXT_PRIMARY};
                font-size: {CompactScaling.FONT_SIZE_SMALL}px;
                padding: 3px 8px;
                margin: 1px;
                border-radius: 2px;
                text-align: left;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.1);
                color: {UltraModernColors.NEON_BLUE};
            }}
            QPushButton:checked {{
                background: {UltraModernColors.NEON_BLUE};
                color: white;
                font-weight: bold;
            }}
        """
        )


class CompactNavigationBar(QWidget):
    """
    Compact navigation bar for 900x500 layout.
    Replaces tab widget with horizontal navigation buttons.
    """

    # Signal emitted when navigation changes
    navigation_changed = pyqtSignal(str)  # nav_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cleanup_done = False
        self.button_group = QButtonGroup(self)
        self.nav_buttons = {}

        self._setup_ui()
        self._setup_default_navigation()
        logger.debug("CompactNavigationBar initialized")

    def _setup_ui(self):
        """Setup the navigation bar layout"""
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(4, 2, 4, 2)
        self.main_layout.setSpacing(2)

        # Apply navigation bar styling
        self.setStyleSheet(get_navbar_style())
        self.setFixedHeight(CompactScaling.NAVBAR_HEIGHT)

        # Add app title/logo
        self.title_label = QLabel("DENSO Neural Matrix")
        self.title_label.setFont(
            QFont("Segoe UI", CompactScaling.FONT_SIZE_SMALL, QFont.Weight.Bold)
        )
        self.title_label.setStyleSheet(
            f"""
            QLabel {{
                color: {UltraModernColors.NEON_BLUE};
                font-weight: bold;
                padding: 4px 8px;
                margin-right: 10px;
            }}
        """
        )
        self.main_layout.addWidget(self.title_label)

        # Navigation buttons container
        self.nav_container = QWidget()
        self.nav_layout = QHBoxLayout(self.nav_container)
        self.nav_layout.setContentsMargins(0, 0, 0, 0)
        self.nav_layout.setSpacing(1)

        self.main_layout.addWidget(self.nav_container)
        self.main_layout.addStretch(1)  # Push everything to the left

        # Connect button group signal
        self.button_group.buttonClicked.connect(self._on_navigation_clicked)

    def _setup_default_navigation(self):
        """Setup default navigation items"""
        nav_items = [
            ("dashboard", "📊", "Dashboard"),
            ("sync", "🔄", "Sync"),
            ("config", "⚙️", "Config"),
            ("logs", "📝", "Logs"),
        ]

        for nav_id, icon, text in nav_items:
            self.add_navigation_item(nav_id, text, icon)

        # Set dashboard as default
        self.set_active_navigation("dashboard")

    def add_navigation_item(self, nav_id: str, text: str, icon: str = ""):
        """Add a new navigation item"""
        try:
            if nav_id in self.nav_buttons:
                logger.warning(f"Navigation item '{nav_id}' already exists")
                return

            button = NavigationButton(text, icon, nav_id)
            self.nav_buttons[nav_id] = button
            self.button_group.addButton(button)
            self.nav_layout.addWidget(button)

            logger.debug(f"Added navigation item: {nav_id}")

        except Exception as e:
            logger.error(f"Error adding navigation item '{nav_id}': {e}")

    def remove_navigation_item(self, nav_id: str):
        """Remove a navigation item"""
        try:
            if nav_id not in self.nav_buttons:
                logger.warning(f"Navigation item '{nav_id}' not found")
                return

            button = self.nav_buttons[nav_id]
            self.button_group.removeButton(button)
            self.nav_layout.removeWidget(button)
            button.deleteLater()
            del self.nav_buttons[nav_id]

            logger.debug(f"Removed navigation item: {nav_id}")

        except Exception as e:
            logger.error(f"Error removing navigation item '{nav_id}': {e}")

    def set_active_navigation(self, nav_id: str):
        """Set the active navigation item"""
        try:
            if nav_id not in self.nav_buttons:
                logger.warning(f"Navigation item '{nav_id}' not found")
                return

            # Uncheck all buttons first
            for button in self.nav_buttons.values():
                button.setChecked(False)

            # Check the selected button
            self.nav_buttons[nav_id].setChecked(True)

            logger.debug(f"Set active navigation: {nav_id}")

        except Exception as e:
            logger.error(f"Error setting active navigation '{nav_id}': {e}")

    def get_active_navigation(self) -> str:
        """Get the currently active navigation item ID"""
        try:
            for nav_id, button in self.nav_buttons.items():
                if button.isChecked():
                    return nav_id
            return ""
        except Exception as e:
            logger.error(f"Error getting active navigation: {e}")
            return ""

    def _on_navigation_clicked(self, button: NavigationButton):
        """Handle navigation button clicks"""
        try:
            nav_id = button.nav_id

            # Uncheck all other buttons
            for other_button in self.nav_buttons.values():
                if other_button != button:
                    other_button.setChecked(False)

            # Ensure clicked button is checked
            button.setChecked(True)

            # Emit navigation change signal
            self.navigation_changed.emit(nav_id)
            logger.debug(f"Navigation changed to: {nav_id}")

        except Exception as e:
            logger.error(f"Error handling navigation click: {e}")

    def update_navigation_badge(self, nav_id: str, badge_text: str = ""):
        """Update navigation item with badge (e.g., error count)"""
        try:
            if nav_id not in self.nav_buttons:
                return

            button = self.nav_buttons[nav_id]
            original_text = button.text().split(" (")[0]  # Remove existing badge

            if badge_text:
                new_text = f"{original_text} ({badge_text})"
            else:
                new_text = original_text

            button.setText(new_text)

        except Exception as e:
            logger.error(f"Error updating navigation badge '{nav_id}': {e}")

    def set_navigation_enabled(self, nav_id: str, enabled: bool):
        """Enable or disable a navigation item"""
        try:
            if nav_id not in self.nav_buttons:
                return

            self.nav_buttons[nav_id].setEnabled(enabled)

        except Exception as e:
            logger.error(f"Error setting navigation enabled '{nav_id}': {e}")

    def cleanup(self):
        """Perform cleanup for NavigationBar"""
        if self.cleanup_done:
            return

        logger.info("CompactNavigationBar cleanup initiated")

        try:
            # Disconnect button group signal
            try:
                self.button_group.buttonClicked.disconnect()
            except (TypeError, RuntimeError):
                pass

            # Clean up navigation buttons
            for nav_id, button in self.nav_buttons.items():
                try:
                    self.button_group.removeButton(button)
                    button.deleteLater()
                except Exception as e:
                    logger.debug(f"Error cleaning up button '{nav_id}': {e}")

            self.nav_buttons.clear()

            # Clean up layouts and widgets
            if hasattr(self, "nav_container"):
                self.nav_container.deleteLater()
            if hasattr(self, "title_label"):
                self.title_label.deleteLater()

            self.cleanup_done = True
            logger.info("CompactNavigationBar cleanup completed")

        except Exception as e:
            logger.error(f"Error during NavigationBar cleanup: {e}")
            self.cleanup_done = True


class NavigationStack(QWidget):
    """
    Widget stack that works with CompactNavigationBar.
    Manages different content panels based on navigation selection.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.panels = {}
        self.current_panel = None
        self.cleanup_done = False

        self._setup_ui()
        logger.debug("NavigationStack initialized")

    def _setup_ui(self):
        """Setup the stack layout"""
        from PyQt6.QtWidgets import QVBoxLayout

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

    def add_panel(self, panel_id: str, widget: QWidget):
        """Add a panel to the stack"""
        try:
            if panel_id in self.panels:
                logger.warning(f"Panel '{panel_id}' already exists")
                return

            self.panels[panel_id] = widget
            widget.hide()  # Hide by default
            self.main_layout.addWidget(widget)

            logger.debug(f"Added panel: {panel_id}")

        except Exception as e:
            logger.error(f"Error adding panel '{panel_id}': {e}")

    def show_panel(self, panel_id: str):
        """Show specific panel and hide others"""
        try:
            if panel_id not in self.panels:
                logger.warning(f"Panel '{panel_id}' not found")
                return

            # Hide current panel
            if self.current_panel and self.current_panel in self.panels:
                self.panels[self.current_panel].hide()

            # Show new panel
            self.panels[panel_id].show()
            self.current_panel = panel_id

            logger.debug(f"Showing panel: {panel_id}")

        except Exception as e:
            logger.error(f"Error showing panel '{panel_id}': {e}")

    def remove_panel(self, panel_id: str):
        """Remove a panel from the stack"""
        try:
            if panel_id not in self.panels:
                logger.warning(f"Panel '{panel_id}' not found")
                return

            widget = self.panels[panel_id]
            self.main_layout.removeWidget(widget)
            widget.deleteLater()
            del self.panels[panel_id]

            if self.current_panel == panel_id:
                self.current_panel = None

            logger.debug(f"Removed panel: {panel_id}")

        except Exception as e:
            logger.error(f"Error removing panel '{panel_id}': {e}")

    def get_current_panel_id(self) -> str:
        """Get the currently visible panel ID"""
        return self.current_panel or ""

    def get_panel(self, panel_id: str) -> QWidget:
        """Get panel widget by ID"""
        return self.panels.get(panel_id)

    def cleanup(self):
        """Perform cleanup for NavigationStack"""
        if self.cleanup_done:
            return

        logger.info("NavigationStack cleanup initiated")

        try:
            # Clean up all panels
            for panel_id, widget in self.panels.items():
                try:
                    if hasattr(widget, "cleanup"):
                        widget.cleanup()
                    widget.deleteLater()
                except Exception as e:
                    logger.debug(f"Error cleaning up panel '{panel_id}': {e}")

            self.panels.clear()
            self.current_panel = None
            self.cleanup_done = True

            logger.info("NavigationStack cleanup completed")

        except Exception as e:
            logger.error(f"Error during NavigationStack cleanup: {e}")
            self.cleanup_done = True
