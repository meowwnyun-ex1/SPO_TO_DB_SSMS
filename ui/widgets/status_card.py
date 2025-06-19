from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QFont, QColor


class AnimatedStatusCard(QFrame):
    """Modern animated status card with glassmorphism effect"""

    def __init__(self, title, status="disconnected", parent=None):
        super().__init__(parent)
        self.title = title
        self.current_status = status
        self.setup_ui()
        self.setup_animations()
        self.update_status(status)

    def setup_ui(self):
        """Setup modern card UI"""
        self.setMinimumHeight(120)
        self.setMaximumHeight(140)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        # Title section
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)

        # Status indicator (animated dot)
        self.status_indicator = QLabel("●")
        self.status_indicator.setFont(QFont("Segoe UI", 16))
        self.status_indicator.setAlignment(Qt.AlignCenter)
        self.status_indicator.setFixedSize(24, 24)

        # Title label
        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.title_label.setStyleSheet(
            """
            color: #e2e8f0;
            background: transparent;
        """
        )

        title_layout.addWidget(self.status_indicator)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        # Status text
        self.status_label = QLabel("Checking...")
        self.status_label.setFont(QFont("Segoe UI", 11, QFont.Medium))
        self.status_label.setAlignment(Qt.AlignLeft)
        self.status_label.setStyleSheet(
            """
            color: #a0aec0;
            background: transparent;
            padding: 4px 0px;
        """
        )

        # Details text (optional)
        self.details_label = QLabel("")
        self.details_label.setFont(QFont("Segoe UI", 9))
        self.details_label.setStyleSheet(
            """
            color: #718096;
            background: transparent;
        """
        )
        self.details_label.setWordWrap(True)

        layout.addLayout(title_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(self.details_label)
        layout.addStretch()

        # Set initial card style
        self.update_card_style("disconnected")

        # Add shadow effect
        self.setup_shadow_effect()

    def setup_shadow_effect(self):
        """Add modern shadow effect"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)

    def setup_animations(self):
        """Setup status indicator animations"""
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self.pulse_indicator)

        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)

    def pulse_indicator(self):
        """Animate status indicator for active states"""
        if self.current_status in ["connecting", "syncing", "processing"]:
            current_color = self.status_indicator.styleSheet()
            if "opacity: 0.3" in current_color:
                opacity = "opacity: 1.0"
            else:
                opacity = "opacity: 0.3"

            # Update indicator with pulse effect
            color = self.get_status_color(self.current_status)
            self.status_indicator.setStyleSheet(
                f"""
                color: {color};
                background: transparent;
                {opacity};
            """
            )

    def get_status_color(self, status):
        """Get color for status"""
        colors = {
            "connected": "#48bb78",  # Green
            "disconnected": "#718096",  # Gray
            "connecting": "#4299e1",  # Blue
            "error": "#f56565",  # Red
            "warning": "#ed8936",  # Orange
            "success": "#38a169",  # Dark Green
            "syncing": "#9f7aea",  # Purple
            "processing": "#4299e1",  # Blue
            "never": "#a0aec0",  # Light Gray
        }
        return colors.get(status, "#718096")

    def get_status_text(self, status):
        """Get display text for status"""
        texts = {
            "connected": "✅ Connected",
            "disconnected": "❌ Disconnected",
            "connecting": "🔄 Connecting...",
            "error": "❌ Connection Error",
            "warning": "⚠️ Warning",
            "success": "✅ Success",
            "syncing": "🔄 Syncing...",
            "processing": "⚙️ Processing...",
            "never": "⏸️ Never Synced",
        }
        return texts.get(status, "❓ Unknown")

    def update_card_style(self, status):
        """Update card appearance based on status"""
        # Base card style with glassmorphism
        base_style = """
            QFrame {
                background: rgba(45, 55, 72, 0.95);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
            }
        """

        # Status-specific accent colors
        accent_colors = {
            "connected": "rgba(72, 187, 120, 0.2)",
            "disconnected": "rgba(113, 128, 150, 0.2)",
            "connecting": "rgba(66, 153, 225, 0.2)",
            "error": "rgba(245, 101, 101, 0.2)",
            "warning": "rgba(237, 137, 54, 0.2)",
            "success": "rgba(56, 161, 105, 0.2)",
            "syncing": "rgba(159, 122, 234, 0.2)",
            "processing": "rgba(66, 153, 225, 0.2)",
            "never": "rgba(160, 174, 192, 0.2)",
        }

        accent = accent_colors.get(status, "rgba(113, 128, 150, 0.2)")

        # Enhanced style with accent border
        enhanced_style = f"""
            QFrame {{
                background: rgba(45, 55, 72, 0.95);
                border-radius: 16px;
                border: 2px solid {accent};
                backdrop-filter: blur(10px);
            }}
            QFrame:hover {{
                background: rgba(45, 55, 72, 0.98);
                border: 2px solid {accent.replace('0.2', '0.4')};
                transform: translateY(-2px);
            }}
        """

        self.setStyleSheet(enhanced_style)

    def update_status(self, status, details=""):
        """Update card status with animation"""
        self.current_status = status

        # Update indicator color
        color = self.get_status_color(status)
        self.status_indicator.setStyleSheet(
            f"""
            color: {color};
            background: transparent;
        """
        )

        # Update status text
        self.status_label.setText(self.get_status_text(status))

        # Update details if provided
        if details:
            self.details_label.setText(details)
            self.details_label.setVisible(True)
        else:
            self.details_label.setVisible(False)

        # Update card style
        self.update_card_style(status)

        # Start/stop pulse animation
        if status in ["connecting", "syncing", "processing"]:
            self.pulse_timer.start(800)  # Pulse every 800ms
        else:
            self.pulse_timer.stop()
            # Reset indicator opacity
            self.status_indicator.setStyleSheet(
                f"""
                color: {color};
                background: transparent;
                opacity: 1.0;
            """
            )


class StatusCard(AnimatedStatusCard):
    """Alias for backward compatibility"""

    def __init__(self, title, status="disconnected", parent=None):
        super().__init__(title, status, parent)


# Enhanced Status Card with additional features
class DetailedStatusCard(AnimatedStatusCard):
    """Extended status card with more details and metrics"""

    def __init__(self, title, status="disconnected", parent=None):
        super().__init__(title, status, parent)
        self.setup_metrics()

    def setup_metrics(self):
        """Add metrics display"""
        # Add metrics section
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(12)

        # Uptime metric
        self.uptime_label = QLabel("Uptime: --")
        self.uptime_label.setFont(QFont("Segoe UI", 8))
        self.uptime_label.setStyleSheet(
            """
            color: #4a5568;
            background: transparent;
        """
        )

        # Response time metric
        self.response_label = QLabel("Response: --")
        self.response_label.setFont(QFont("Segoe UI", 8))
        self.response_label.setStyleSheet(
            """
            color: #4a5568;
            background: transparent;
        """
        )

        metrics_layout.addWidget(self.uptime_label)
        metrics_layout.addWidget(self.response_label)
        metrics_layout.addStretch()

        # Add to main layout
        self.layout().addLayout(metrics_layout)

    def update_metrics(self, uptime=None, response_time=None):
        """Update metrics display"""
        if uptime:
            self.uptime_label.setText(f"Uptime: {uptime}")
        if response_time:
            self.response_label.setText(f"Response: {response_time}ms")


# Compact Status Card for smaller spaces
class CompactStatusCard(QFrame):
    """Compact version of status card for toolbars or small spaces"""

    def __init__(self, title, status="disconnected", parent=None):
        super().__init__(parent)
        self.title = title
        self.current_status = status
        self.setup_ui()
        self.update_status(status)

    def setup_ui(self):
        """Setup compact UI"""
        self.setFixedHeight(60)
        self.setMinimumWidth(120)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)

        # Status indicator
        self.status_indicator = QLabel("●")
        self.status_indicator.setFont(QFont("Segoe UI", 12))
        self.status_indicator.setFixedSize(16, 16)

        # Title and status
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.title_label.setStyleSheet("color: #e2e8f0; background: transparent;")

        self.status_label = QLabel("Checking...")
        self.status_label.setFont(QFont("Segoe UI", 8))
        self.status_label.setStyleSheet("color: #a0aec0; background: transparent;")

        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.status_label)

        layout.addWidget(self.status_indicator)
        layout.addLayout(text_layout)

        # Base style
        self.setStyleSheet(
            """
            QFrame {
                background: rgba(45, 55, 72, 0.9);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """
        )

    def update_status(self, status, details=""):
        """Update compact status"""
        self.current_status = status

        # Status colors (same as main card)
        colors = {
            "connected": "#48bb78",
            "disconnected": "#718096",
            "connecting": "#4299e1",
            "error": "#f56565",
            "warning": "#ed8936",
            "success": "#38a169",
            "syncing": "#9f7aea",
            "processing": "#4299e1",
            "never": "#a0aec0",
        }

        # Status texts (shorter for compact)
        texts = {
            "connected": "Connected",
            "disconnected": "Offline",
            "connecting": "Connecting...",
            "error": "Error",
            "warning": "Warning",
            "success": "Success",
            "syncing": "Syncing...",
            "processing": "Processing...",
            "never": "Never",
        }

        color = colors.get(status, "#718096")
        text = texts.get(status, "Unknown")

        self.status_indicator.setStyleSheet(
            f"""
            color: {color};
            background: transparent;
        """
        )

        self.status_label.setText(text)
