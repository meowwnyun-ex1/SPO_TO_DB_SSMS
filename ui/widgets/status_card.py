from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QPainter
from typing import Any  # Added import for Any

from ..styles.theme import UltraModernColors, get_modern_card_style


class CompactStatusIndicator(QWidget):
    """Compact status indicator สำหรับขนาด 900x500"""

    def __init__(self, status="disconnected", parent=None):
        super().__init__(parent)
        self.status = status
        self.setFixedSize(16, 16)  # Increased size for better visibility

    def paintEvent(self, event):
        """วาดจุดสถานะแบบ compact"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        colors = {
            "connected": UltraModernColors.SUCCESS_COLOR,
            "disconnected": UltraModernColors.ERROR_COLOR,
            "error": UltraModernColors.ERROR_COLOR,
            "success": UltraModernColors.SUCCESS_COLOR,  # For last sync success
            "never": "#666666",
            "syncing": UltraModernColors.NEON_BLUE,
            "warning": UltraModernColors.WARNING_COLOR,
            "in_progress": UltraModernColors.NEON_PURPLE,
            "connecting": UltraModernColors.NEON_YELLOW,
            "failed": UltraModernColors.ERROR_COLOR,  # For last sync failure
        }

        color = QColor(
            colors.get(self.status, UltraModernColors.TEXT_SECONDARY_ALT)
        )  # Default to gray

        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)

        # Draw a rounded rectangle/circle
        rect = self.rect().adjusted(2, 2, -2, -2)  # Small padding
        painter.drawEllipse(rect)
        # painter.drawRoundedRect(rect, 4, 4) # Can use rounded rectangle too

        # Optional: Add a subtle pulse animation if status is "connecting" or "syncing"
        if self.status in ["connecting", "syncing", "in_progress"]:
            # A simple pulsing effect can be done with QPropertyAnimation on opacity
            pass  # This is best handled by a QPropertyAnimation on the parent widget or a separate logic

    def set_status(self, status: str):
        """Sets the status and triggers a repaint."""
        if self.status != status:
            self.status = status
            self.update()  # Trigger repaint


class ModernStatusCard(QWidget):
    """
    Compact status card for displaying connection/sync status.
    Uses glassmorphism style with neon accents.
    """

    def __init__(
        self,
        title: str,
        initial_status: Any,
        is_boolean_status: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.title = title
        self._status = initial_status  # Can be string or boolean
        self.is_boolean_status = is_boolean_status  # If true, initial_status is boolean

        self.pulse_animation = None  # Initialize animation reference

        self._setup_ui()
        self.update_status_display()  # Set initial status display

    def _setup_ui(self):
        """Sets up the layout and widgets for the status card."""
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # Apply the card style to the QWidget itself
        self.setStyleSheet(get_modern_card_style())
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(70)  # Ensure a consistent minimum height

        # Outer frame for consistent styling and hover effects
        self.outer_frame = QFrame(self)
        self.outer_frame.setStyleSheet(
            self._get_frame_style(self.current_status_string())
        )  # Initial style
        self.outer_frame.setContentsMargins(0, 0, 0, 0)  # No extra margins on frame
        self.outer_frame.setFrameShape(QFrame.Shape.NoFrame)  # No frame border

        frame_layout = QHBoxLayout(self.outer_frame)
        frame_layout.setContentsMargins(15, 10, 15, 10)
        frame_layout.setSpacing(10)

        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.SemiBold))
        self.title_label.setStyleSheet(f"color: {UltraModernColors.TEXT_PRIMARY};")
        frame_layout.addWidget(self.title_label)

        frame_layout.addStretch(1)  # Pushes status to the right

        self.status_label = QLabel()
        self.status_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.status_label.setStyleSheet(
            f"color: {UltraModernColors.TEXT_PRIMARY};"
        )  # Color will be updated by code
        frame_layout.addWidget(self.status_label)

        self.status_indicator = CompactStatusIndicator(self.current_status_string())
        frame_layout.addWidget(self.status_indicator)

        self.main_layout.addWidget(self.outer_frame)

    def current_status_string(self) -> str:
        """Returns the status as a string, converting boolean if necessary."""
        if self.is_boolean_status:
            return (
                "in_progress" if self._status else "never"
            )  # 'in_progress' for True, 'never' for False for consistency
        return self._status

    def _get_frame_style(self, status: str, is_hover: bool = False) -> str:
        """Generates the QFrame stylesheet based on status and hover state."""
        base_style = get_modern_card_style()  # Get base card style

        border_colors = {
            "connected": UltraModernColors.SUCCESS_COLOR,
            "disconnected": UltraModernColors.ERROR_COLOR,
            "error": UltraModernColors.ERROR_COLOR,
            "success": UltraModernColors.SUCCESS_COLOR,
            "never": UltraModernColors.GLASS_BORDER,  # Default grey border
            "syncing": UltraModernColors.NEON_BLUE,
            "warning": UltraModernColors.WARNING_COLOR,
            "in_progress": UltraModernColors.NEON_PURPLE,
            "connecting": UltraModernColors.NEON_YELLOW,
            "failed": UltraModernColors.ERROR_COLOR,
        }

        current_border_color = border_colors.get(status, UltraModernColors.GLASS_BORDER)

        # Adjust border color for hover state
        if is_hover:
            # Make the border slightly brighter or use a distinct accent color on hover
            hover_border_color = (
                UltraModernColors.NEON_BLUE
                if status in ["connected", "success"]
                else (
                    UltraModernColors.NEON_PINK
                    if status in ["error", "failed", "disconnected"]
                    else UltraModernColors.NEON_GREEN
                )
            )  # General hover accent
            current_border_color = hover_border_color

        # Apply internal frame style, overriding relevant parts of base_style
        # The base_style (get_modern_card_style) is for the outer QWidget,
        # so this is for the inner QFrame's appearance.
        frame_style = f"""
            QFrame {{
                background: {UltraModernColors.GLASS_BG_LIGHT if is_hover else UltraModernColors.GLASS_BG_DARK};
                border: 2px solid {current_border_color};
                border-radius: 8px;
                padding: 8px; /* Internal padding */
                color: {UltraModernColors.TEXT_PRIMARY};
            }}
        """
        return frame_style

    def update_status_display(self):
        """Updates the text label and indicator based on the current status."""
        status_str = self.current_status_string()

        # Update labels and colors based on status
        text_color = UltraModernColors.TEXT_PRIMARY
        display_text = status_str.replace(
            "_", " "
        ).title()  # Convert 'in_progress' to 'In Progress'

        if status_str == "connected" or status_str == "success":
            text_color = UltraModernColors.SUCCESS_COLOR
            display_text = "Connected" if status_str == "connected" else "Success"
        elif (
            status_str == "disconnected"
            or status_str == "error"
            or status_str == "failed"
        ):
            text_color = UltraModernColors.ERROR_COLOR
            display_text = (
                "Disconnected"
                if status_str == "disconnected"
                else "Error" if status_str == "error" else "Failed"
            )
        elif status_str == "connecting":
            text_color = UltraModernColors.NEON_YELLOW
            display_text = "Connecting..."
        elif status_str == "syncing" or status_str == "in_progress":
            text_color = UltraModernColors.NEON_PURPLE
            display_text = "In Progress"
        elif status_str == "never":
            text_color = UltraModernColors.TEXT_SECONDARY_ALT
            display_text = "Never Run"

        self.status_label.setStyleSheet(f"color: {text_color};")
        self.status_label.setText(display_text)
        self.status_indicator.set_status(status_str)

        # Apply the frame style based on current status (non-hover)
        self.outer_frame.setStyleSheet(
            self._get_frame_style(status_str, is_hover=False)
        )

        # Manage pulse animation (if needed for 'connecting' or 'in_progress')
        if status_str in ["connecting", "in_progress", "syncing"]:
            self._start_pulse_animation()
        else:
            self._stop_pulse_animation()

    def set_status(self, status: Any):
        """
        Public method to set the status of the card.
        Accepts string for general statuses or boolean for is_boolean_status cards.
        """
        # Convert boolean input to appropriate string status
        if self.is_boolean_status:
            self._status = (
                "in_progress" if status else "never"
            )  # Map True to "in_progress", False to "never"
        else:
            self._status = status
        self.update_status_display()

    def _start_pulse_animation(self):
        """Starts a pulsating animation for the border."""
        if self.pulse_animation is None:
            self.pulse_animation = QPropertyAnimation(self.outer_frame, b"styleSheet")
            self.pulse_animation.setDuration(1000)  # 1 second for a full pulse
            self.pulse_animation.setLoopCount(QPropertyAnimation.Loop.Infinite)
            self.pulse_animation.setEasingCurve(
                QEasingCurve.Type.InOutSine
            )  # Smooth pulse

            # Define animation values
            start_color = UltraModernColors.NEON_PURPLE  # Example start
            end_color = (
                QColor(UltraModernColors.NEON_PURPLE).lighter(150).name()
            )  # Lighter for pulse effect

            self.pulse_animation.setKeyValueAt(
                0,
                self._get_frame_style(
                    self.current_status_string(), is_pulse=True, pulse_factor=1.0
                ),
            )  # Original brightness
            self.pulse_animation.setKeyValueAt(
                0.5,
                self._get_frame_style(
                    self.current_status_string(), is_pulse=True, pulse_factor=1.5
                ),
            )  # Brighter
            self.pulse_animation.setKeyValueAt(
                1,
                self._get_frame_style(
                    self.current_status_string(), is_pulse=True, pulse_factor=1.0
                ),
            )  # Back to original

        if self.pulse_animation.state() != QPropertyAnimation.State.Running:
            self.pulse_animation.start()
            logger.debug(f"Pulse animation started for {self.title} card.")

    # Modified _get_frame_style to include pulse_factor handling
    def _get_frame_style(
        self,
        status: str,
        is_hover: bool = False,
        is_pulse: bool = False,
        pulse_factor: float = 1.0,
    ) -> str:
        """Generates the QFrame stylesheet based on status, hover, and pulse state."""
        border_colors = {
            "connected": UltraModernColors.SUCCESS_COLOR,
            "disconnected": UltraModernColors.ERROR_COLOR,
            "error": UltraModernColors.ERROR_COLOR,
            "success": UltraModernColors.SUCCESS_COLOR,
            "never": UltraModernColors.GLASS_BORDER,
            "syncing": UltraModernColors.NEON_BLUE,
            "warning": UltraModernColors.WARNING_COLOR,
            "in_progress": UltraModernColors.NEON_PURPLE,
            "connecting": UltraModernColors.NEON_YELLOW,
            "failed": UltraModernColors.ERROR_COLOR,
        }

        current_border_color_name = border_colors.get(
            status, UltraModernColors.GLASS_BORDER
        )
        current_border_color = QColor(current_border_color_name)

        if is_pulse:
            current_border_color = current_border_color.lighter(
                int(pulse_factor * 100)
            )  # Adjust brightness

        if is_hover:
            hover_border_color = (
                QColor(UltraModernColors.NEON_BLUE)
                if status in ["connected", "success"]
                else (
                    QColor(UltraModernColors.NEON_PINK)
                    if status in ["error", "failed", "disconnected"]
                    else QColor(UltraModernColors.NEON_GREEN)
                )
            )
            current_border_color = hover_border_color.lighter(
                120
            )  # Slightly brighter on hover

        frame_style = f"""
            QFrame {{
                background: {UltraModernColors.GLASS_BG_LIGHT if is_hover else UltraModernColors.GLASS_BG_DARK};
                border: 2px solid {current_border_color.name()};
                border-radius: 8px;
                padding: 8px;
                color: {UltraModernColors.TEXT_PRIMARY};
            }}
        """
        return frame_style

    def _stop_pulse_animation(self):
        """Stops the pulsating animation."""
        if (
            self.pulse_animation
            and self.pulse_animation.state() == QPropertyAnimation.State.Running
        ):
            self.pulse_animation.stop()
            self.outer_frame.setStyleSheet(
                self._get_frame_style(self.current_status_string(), is_hover=False)
            )  # Reset style
            logger.debug(f"Pulse animation stopped for {self.title} card.")

    def enterEvent(self, event):
        """Handle mouse hover enter event."""
        super().enterEvent(event)
        self.outer_frame.setStyleSheet(
            self._get_frame_style(self.current_status_string(), is_hover=True)
        )

    def leaveEvent(self, event):
        """Reset hover effect."""
        super().leaveEvent(event)
        self.update_status_display()  # This will re-apply non-hover style and manage pulse

    def cleanup_animations(self):
        """Cleanup animations"""
        self._stop_pulse_animation()
        if self.pulse_animation:
            self.pulse_animation.deleteLater()
            self.pulse_animation = None
            logger.debug("Pulse animation object deleted.")
