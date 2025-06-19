from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPainter


class StatusIndicator(QWidget):
    def __init__(self, status="disconnected", parent=None):
        super().__init__(parent)
        self.status = status
        self.setFixedSize(12, 12)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        colors = {
            "connected": QColor("#4CAF50"),
            "disconnected": QColor("#F44336"),
            "error": QColor("#FF9800"),
            "success": QColor("#4CAF50"),
            "never": QColor("#9E9E9E"),
        }

        color = colors.get(self.status, colors["disconnected"])
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(self.rect())


class StatusCard(QWidget):
    def __init__(self, title, status="disconnected", parent=None):
        super().__init__(parent)
        self.title = title
        self.status = status
        self.description = ""
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Title row with status indicator
        title_row = QHBoxLayout()

        self.status_indicator = StatusIndicator(self.status)
        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))

        title_row.addWidget(self.status_indicator)
        title_row.addWidget(self.title_label)
        title_row.addStretch()

        # Status label
        self.status_label = QLabel(self.status.capitalize())
        self.status_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))

        # Description
        self.description_label = QLabel(self.description)
        self.description_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Normal))
        self.description_label.setWordWrap(True)
        self.description_label.setVisible(False)

        layout.addLayout(title_row)
        layout.addWidget(self.status_label)
        layout.addWidget(self.description_label)

    def update_status(self, status, description=""):
        self.status = status
        self.status_indicator.status = status
        self.status_label.setText(status.capitalize())
        if description:
            self.description_label.setText(description)
            self.description_label.setVisible(True)
        self.status_indicator.update()


class UltraModernStatusCard(StatusCard):
    def __init__(self, title, status="disconnected", parent=None):
        super().__init__(title, status, parent)
        self.setStyleSheet(
            """
            QWidget {
                background-color: rgba(20, 20, 30, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                color: white;
            }
            QLabel {
                background-color: transparent;
            }
        """
        )
        self.status_label.setStyleSheet(
            """
            QLabel {
                color: #cbd5e1;
                background: transparent;
                padding: 6px 0px;
                text-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
            }
        """
        )

        # Enhanced details section
        self.details_label = QLabel("")
        self.details_label.setFont(QFont("Segoe UI", 9))
        self.details_label.setStyleSheet(
            """
            QLabel {
                color: #94a3b8;
                background: transparent;
                line-height: 1.4;
            }
        """
        )
        self.details_label.setWordWrap(True)

        layout.addLayout(title_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(self.details_label)
        layout.addStretch()
        layout.addWidget(self.metrics_widget)

        # Set initial holographic card style
        self.update_card_style("disconnected")

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
        """Get enhanced status text with emojis"""
        status_texts = {
            "connected": "🟢 Online & Ready",
            "disconnected": "⚫ Offline",
            "connecting": "🔵 Connecting...",
            "error": "🔴 Connection Failed",
            "warning": "🟡 Warning State",
            "success": "✅ Operation Complete",
            "syncing": "🟣 Synchronizing...",
            "processing": "⚙️ Processing...",
            "never": "⏸️ Never Connected",
        }
        return status_texts.get(status, "❓ Unknown Status")

    def update_card_style(self, status):
        """Update card with holographic styling based on status"""
        colors = self.get_status_colors(status)

        # Advanced glassmorphism with status-specific accents
        style = f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.08),
                    stop:0.5 {colors['bg']},
                    stop:1 rgba(255, 255, 255, 0.04)
                );
                backdrop-filter: blur(20px);
                border: 2px solid {colors['border']};
                border-radius: 20px;
                box-shadow: 
                    0 8px 32px rgba(0, 0, 0, 0.2),
                    0 0 20px {colors['glow']},
                    inset 0 1px 0 rgba(255, 255, 255, 0.1),
                    inset 0 -1px 0 rgba(0, 0, 0, 0.1);
            }}
            QFrame:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.12),
                    stop:0.5 {colors['bg'].replace('0.05', '0.08')},
                    stop:1 rgba(255, 255, 255, 0.06)
                );
                border: 2px solid {colors['border'].replace('0.5', '0.8')};
                box-shadow: 
                    0 12px 40px rgba(0, 0, 0, 0.3),
                    0 0 30px {colors['glow'].replace('0.3', '0.6')},
                    inset 0 1px 0 rgba(255, 255, 255, 0.2);
            }}
        """

        self.setStyleSheet(style)

    def pulse_glow(self):
        """Create pulsing glow effect for active states"""
        if self.current_status in ["connecting", "syncing", "processing"]:
            # Implement glow pulsing logic here
            pass

    def update_status(self, status, details="", metrics=None):
        """Update card status with advanced animations"""
        self.current_status = status

        # Update indicator
        self.status_indicator.update_status(status)

        # Update status text with enhanced styling
        status_text = self.get_status_text(status)
        colors = self.get_status_colors(status)

        self.status_label.setText(status_text)
        self.status_label.setStyleSheet(
            f"""
            QLabel {{
                color: {colors['text']};
                background: transparent;
                padding: 6px 0px;
                text-shadow: 
                    0 1px 3px rgba(0, 0, 0, 0.4),
                    0 0 10px {colors['text']}40;
                font-weight: 600;
            }}
        """
        )

        # Update details if provided
        if details:
            self.details_label.setText(details)
            self.details_label.setVisible(True)
        else:
            self.details_label.setVisible(False)

        # Update metrics if provided
        if metrics:
            self.metric1_label.setText(metrics.get("metric1", ""))
            self.metric2_label.setText(metrics.get("metric2", ""))
            self.metrics_widget.setVisible(True)
        else:
            self.metrics_widget.setVisible(False)

        # Update card styling
        self.update_card_style(status)

        # Start/stop glow animations
        if status in ["connecting", "syncing", "processing"]:
            self.glow_timer.start(1000)
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


# UltraModernStatusCard สำหรับ UI แบบ ultra modern
class UltraModernStatusCard(AnimatedStatusCard):
    def __init__(self, title, status="disconnected", parent=None):
        super().__init__(title, status, parent)
        self.setStyleSheet(
            """
            QWidget {
                background-color: rgba(20, 20, 30, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                color: white;
            }
            QLabel {
                background-color: transparent;
            }
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

        # Create hover transform
        hover_rect = QRect(
            self.original_geometry.x() - 4,
            self.original_geometry.y() - 6,
            self.original_geometry.width() + 8,
            self.original_geometry.height() + 8,
        )

        self.transform_animation.setStartValue(self.geometry())
        self.transform_animation.setEndValue(hover_rect)
        self.transform_animation.start()

    def leaveEvent(self, event):
        """Enhanced hover leave effect"""
        super().leaveEvent(event)

        # Return to base shadow
        self.setGraphicsEffect(self.base_shadow)

        # Return to original geometry
        if self.original_geometry:
            self.transform_animation.setStartValue(self.geometry())
            self.transform_animation.setEndValue(self.original_geometry)
            self.transform_animation.start()


# Backward compatibility aliases


# UltraModernStatusCard สำหรับ UI แบบ ultra modern
class UltraModernStatusCard(AnimatedStatusCard):
    def __init__(self, title, status="disconnected", parent=None):
        super().__init__(title, status, parent)


class StatusCard(UltraModernStatusCard):
    """Main status card alias for backward compatibility"""

    pass


class AnimatedStatusCard(UltraModernStatusCard):
    """Animated status card alias"""

    pass


class CompactStatusCard(QFrame):
    """Ultra compact holographic status indicator"""

    def __init__(self, title, status="disconnected", parent=None):
        super().__init__(parent)
        self.title = title
        self.current_status = status
        self.setup_compact_ui()
        self.update_status(status)

    def setup_compact_ui(self):
        """Setup ultra compact holographic UI"""
        self.setFixedHeight(48)
        self.setMinimumWidth(100)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)

        # Status indicator
        self.status_indicator = QLabel("●")
        self.status_indicator.setFont(QFont("Segoe UI", 12))
        self.status_indicator.setFixedSize(16, 16)

        # Compact text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(1)

        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #e2e8f0; background: transparent;")

        self.status_label = QLabel("...")
        self.status_label.setFont(QFont("Inter", 7))
        self.status_label.setStyleSheet("color: #94a3b8; background: transparent;")

        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.status_label)

        layout.addWidget(self.indicator)
        layout.addLayout(text_layout)

        # Compact holographic style
        self.setStyleSheet(
            """
            QFrame {
                background: rgba(255, 255, 255, 0.06);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            }
            QFrame:hover {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(0, 212, 255, 0.3);
                box-shadow: 0 0 15px rgba(0, 212, 255, 0.2);
            }
        """
        )

    def update_status(self, status, details=""):
        """Update compact status"""
        colors = {
            "connected": "#39ff14",
            "disconnected": "#64748b",
            "connecting": "#00d4ff",
            "error": "#ff073a",
            "warning": "#ff6b00",
        }

        texts = {
            "connected": "Online",
            "disconnected": "Offline",
            "connecting": "Connecting...",
            "error": "Error",
            "warning": "Warning",
        }

        color = colors.get(status, "#64748b")
        text = texts.get(status, "Unknown")

        self.indicator.setStyleSheet(
            f"""
            color: {color};
            background: transparent;
            text-shadow: 0 0 8px {color};
        """
        )

        self.status_label.setText(text)
