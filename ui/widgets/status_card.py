from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QWidget,
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QRect, pyqtSignal
from PyQt6.QtGui import QFont, QColor


class PulsingIndicator(QLabel):
    """Advanced pulsing indicator with holographic effects"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(32, 32)
        self.current_status = "disconnected"
        self.setup_animations()

    def setup_animations(self):
        """Setup sophisticated pulse and glow animations"""
        # Primary pulse animation
        self.pulse_animation = QPropertyAnimation(self, b"geometry")
        self.pulse_animation.setDuration(1200)
        self.pulse_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.pulse_animation.setLoopCount(-1)

        # Opacity animation for breathing effect
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)

        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(2000)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.opacity_animation.setLoopCount(-1)
        self.opacity_animation.setStartValue(0.4)
        self.opacity_animation.setEndValue(1.0)

        # Glow effect
        self.glow_effect = QGraphicsDropShadowEffect()
        self.glow_effect.setBlurRadius(25)
        self.glow_effect.setOffset(0, 0)

    def start_animations(self, status):
        """Start status-specific animations"""
        self.current_status = status

        # Stop existing animations
        self.pulse_animation.stop()
        self.opacity_animation.stop()

        # Configure glow based on status
        colors = {
            "connected": QColor(72, 187, 120, 180),  # Green glow
            "connecting": QColor(0, 212, 255, 200),  # Blue glow
            "syncing": QColor(159, 122, 234, 200),  # Purple glow
            "error": QColor(245, 101, 101, 180),  # Red glow
            "warning": QColor(237, 137, 54, 180),  # Orange glow
            "success": QColor(57, 255, 20, 200),  # Neon green glow
            "disconnected": QColor(113, 128, 150, 100),  # Gray glow
        }

        glow_color = colors.get(status, colors["disconnected"])
        self.glow_effect.setColor(glow_color)

        # Apply glow effect
        if hasattr(self, "opacity_effect"):
            self.opacity_effect.deleteLater()
        self.setGraphicsEffect(self.glow_effect)

        # Start animations for active states
        if status in ["connecting", "syncing", "processing"]:
            # Pulse geometry animation
            base_rect = QRect(0, 0, 32, 32)
            expanded_rect = QRect(-2, -2, 36, 36)

            self.pulse_animation.setStartValue(base_rect)
            self.pulse_animation.setEndValue(expanded_rect)
            self.pulse_animation.start()

            # Breathing opacity effect
            self.opacity_effect = QGraphicsOpacityEffect()
            self.setGraphicsEffect(self.opacity_effect)

            self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.opacity_animation.setDuration(2000)
            self.opacity_animation.setStartValue(0.6)
            self.opacity_animation.setEndValue(1.0)
            self.opacity_animation.setLoopCount(-1)
            self.opacity_animation.start()

    def stop_animations(self):
        """Stop all animations"""
        self.pulse_animation.stop()
        self.opacity_animation.stop()

    def update_status(self, status):
        """Update indicator status with animations"""
        # Status symbols with enhanced Unicode
        symbols = {
            "connected": "●",
            "disconnected": "○",
            "connecting": "◐",
            "error": "✖",
            "warning": "⚠",
            "success": "✓",
            "syncing": "◑",
            "processing": "◒",
            "never": "◯",
        }

        # Status colors with enhanced luminosity
        colors = {
            "connected": "#39ff14",  # Neon green
            "disconnected": "#64748b",  # Cool gray
            "connecting": "#00d4ff",  # Neon blue
            "error": "#ff073a",  # Neon red
            "warning": "#ff6b00",  # Neon orange
            "success": "#00ff41",  # Bright green
            "syncing": "#bd5eff",  # Neon purple
            "processing": "#00d4ff",  # Neon blue
            "never": "#9ca3af",  # Light gray
        }

        symbol = symbols.get(status, "◯")
        color = colors.get(status, "#64748b")

        # Apply holographic text style
        self.setText(symbol)
        self.setStyleSheet(
            f"""
            QLabel {{
                color: {color};
                background: transparent;
                font-size: 20px;
                font-weight: 900;
                text-align: center;
                text-shadow: 
                    0 0 10px {color},
                    0 0 20px {color},
                    0 0 30px {color};
            }}
        """
        )

        self.start_animations(status)


class HolographicFrame(QFrame):
    """Ultra modern frame with advanced glassmorphism and dimensional effects"""

    hover_started = pyqtSignal()
    hover_ended = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_effects()
        self.setup_hover_animations()

    def setup_effects(self):
        """Setup advanced visual effects"""
        # Multi-layered shadow system
        self.primary_shadow = QGraphicsDropShadowEffect()
        self.primary_shadow.setBlurRadius(20)
        self.primary_shadow.setColor(QColor(0, 0, 0, 80))
        self.primary_shadow.setOffset(0, 10)

        self.glow_shadow = QGraphicsDropShadowEffect()
        self.glow_shadow.setBlurRadius(30)
        self.glow_shadow.setColor(QColor(102, 126, 234, 60))
        self.glow_shadow.setOffset(0, 0)

        # Start with primary shadow
        self.setGraphicsEffect(self.primary_shadow)

    def setup_hover_animations(self):
        """Setup hover transform animations"""
        self.hover_animation = QPropertyAnimation(self, b"geometry")
        self.hover_animation.setDuration(300)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.shadow_timer = QTimer()
        self.shadow_timer.setSingleShot(True)
        self.shadow_timer.timeout.connect(self.switch_to_glow)

    def switch_to_glow(self):
        """Switch to glow effect on hover"""
        self.setGraphicsEffect(self.glow_shadow)

    def enterEvent(self, event):
        """Enhanced hover enter effect"""
        super().enterEvent(event)

        # Start glow transition
        self.shadow_timer.start(100)

        # Emit hover signal
        self.hover_started.emit()

        # Slight scale and lift effect
        current_rect = self.geometry()
        hover_rect = QRect(
            current_rect.x() - 3,
            current_rect.y() - 5,
            current_rect.width() + 6,
            current_rect.height() + 6,
        )

        self.hover_animation.setStartValue(current_rect)
        self.hover_animation.setEndValue(hover_rect)
        self.hover_animation.start()

    def leaveEvent(self, event):
        """Enhanced hover leave effect"""
        super().leaveEvent(event)

        # Reset to primary shadow
        self.shadow_timer.stop()
        self.setGraphicsEffect(self.primary_shadow)

        # Emit hover end signal
        self.hover_ended.emit()

        # Return to original position
        self.hover_animation.finished.connect(self.reset_geometry)

    def reset_geometry(self):
        """Reset to original geometry"""
        # This would need the original geometry stored
        pass


class UltraModernStatusCard(QFrame):
    """Ultra modern holographic status card with advanced dimensional effects"""

    status_clicked = pyqtSignal(str)

    def __init__(self, title, status="disconnected", parent=None):
        super().__init__(parent)
        self.title = title
        self.current_status = status
        self.original_geometry = None
        self.setup_ui()
        self.setup_animations()
        self.update_status(status)

    def setup_ui(self):
        """Setup ultra modern holographic UI"""
        self.setMinimumHeight(140)
        self.setMaximumHeight(180)
        self.setMinimumWidth(180)

        # Make clickable
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Main layout with enhanced spacing
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # Header section with holographic indicator
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        # Advanced pulsing indicator
        self.status_indicator = PulsingIndicator()

        # Title with enhanced typography
        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        self.title_label.setStyleSheet(
            """
            QLabel {
                color: #ffffff;
                background: transparent;
                text-shadow: 
                    0 2px 4px rgba(0, 0, 0, 0.5),
                    0 0 10px rgba(255, 255, 255, 0.3);
                letter-spacing: 0.5px;
            }
        """
        )

        header_layout.addWidget(self.status_indicator)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        # Status text with dynamic styling
        self.status_label = QLabel("Initializing...")
        self.status_label.setFont(QFont("Inter", 12, QFont.Weight.Medium))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
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
        self.details_label.setFont(QFont("Inter", 10, QFont.Weight.Normal))
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

        # Metrics section (optional)
        self.metrics_widget = QWidget()
        metrics_layout = QHBoxLayout(self.metrics_widget)
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(16)

        self.metric1_label = QLabel("")
        self.metric1_label.setFont(QFont("Inter", 8, QFont.Weight.Medium))
        self.metric1_label.setStyleSheet("color: #64748b; background: transparent;")

        self.metric2_label = QLabel("")
        self.metric2_label.setFont(QFont("Inter", 8, QFont.Weight.Medium))
        self.metric2_label.setStyleSheet("color: #64748b; background: transparent;")

        metrics_layout.addWidget(self.metric1_label)
        metrics_layout.addWidget(self.metric2_label)
        metrics_layout.addStretch()

        self.metrics_widget.setVisible(False)

        # Add all sections to main layout
        layout.addLayout(header_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(self.details_label)
        layout.addStretch()
        layout.addWidget(self.metrics_widget)

        # Set initial holographic card style
        self.update_card_style("disconnected")

    def setup_animations(self):
        """Setup advanced card animations"""
        # Hover transform animation
        self.transform_animation = QPropertyAnimation(self, b"geometry")
        self.transform_animation.setDuration(250)
        self.transform_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Glow pulse animation for active states
        self.glow_timer = QTimer()
        self.glow_timer.timeout.connect(self.pulse_glow)

        # Setup advanced shadow effects
        self.setup_shadow_effects()

    def setup_shadow_effects(self):
        """Setup multi-layered shadow system"""
        self.base_shadow = QGraphicsDropShadowEffect()
        self.base_shadow.setBlurRadius(15)
        self.base_shadow.setColor(QColor(0, 0, 0, 60))
        self.base_shadow.setOffset(0, 8)

        self.hover_shadow = QGraphicsDropShadowEffect()
        self.hover_shadow.setBlurRadius(25)
        self.hover_shadow.setColor(QColor(0, 212, 255, 80))
        self.hover_shadow.setOffset(0, 12)

        # Start with base shadow
        self.setGraphicsEffect(self.base_shadow)

    def get_status_colors(self, status):
        """Get enhanced color scheme for status"""
        color_schemes = {
            "connected": {
                "border": "rgba(57, 255, 20, 0.5)",
                "glow": "rgba(57, 255, 20, 0.3)",
                "bg": "rgba(57, 255, 20, 0.05)",
                "text": "#39ff14",
            },
            "disconnected": {
                "border": "rgba(100, 116, 139, 0.3)",
                "glow": "rgba(100, 116, 139, 0.2)",
                "bg": "rgba(100, 116, 139, 0.03)",
                "text": "#64748b",
            },
            "connecting": {
                "border": "rgba(0, 212, 255, 0.5)",
                "glow": "rgba(0, 212, 255, 0.4)",
                "bg": "rgba(0, 212, 255, 0.05)",
                "text": "#00d4ff",
            },
            "error": {
                "border": "rgba(255, 7, 58, 0.5)",
                "glow": "rgba(255, 7, 58, 0.4)",
                "bg": "rgba(255, 7, 58, 0.05)",
                "text": "#ff073a",
            },
            "warning": {
                "border": "rgba(255, 107, 0, 0.5)",
                "glow": "rgba(255, 107, 0, 0.4)",
                "bg": "rgba(255, 107, 0, 0.05)",
                "text": "#ff6b00",
            },
            "success": {
                "border": "rgba(0, 255, 65, 0.5)",
                "glow": "rgba(0, 255, 65, 0.4)",
                "bg": "rgba(0, 255, 65, 0.05)",
                "text": "#00ff41",
            },
            "syncing": {
                "border": "rgba(189, 94, 255, 0.5)",
                "glow": "rgba(189, 94, 255, 0.4)",
                "bg": "rgba(189, 94, 255, 0.05)",
                "text": "#bd5eff",
            },
        }

        return color_schemes.get(status, color_schemes["disconnected"])

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
                transform: translateY(-4px) scale(1.02);
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
            self.glow_timer.stop()

    def mousePressEvent(self, event):
        """Handle card click with ripple effect"""
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.status_clicked.emit(self.current_status)
            # Add ripple effect here if needed

    def enterEvent(self, event):
        """Enhanced hover enter effect"""
        super().enterEvent(event)

        # Switch to hover shadow
        self.setGraphicsEffect(self.hover_shadow)

        # Store original geometry for animation
        if self.original_geometry is None:
            self.original_geometry = self.geometry()

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

        # Compact indicator
        self.indicator = QLabel("●")
        self.indicator.setFont(QFont("Inter", 10, QFont.Weight.Bold))
        self.indicator.setFixedSize(16, 16)

        # Compact text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(1)

        self.title_label = QLabel(self.title)
        self.title_label.setFont(QFont("Inter", 9, QFont.Weight.Bold))
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
