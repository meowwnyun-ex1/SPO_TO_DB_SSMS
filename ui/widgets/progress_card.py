from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QWidget,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtGui import QFont, QColor, QPainter
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtSignal
from ..styles.theme import (
    UltraModernColors,
    get_ultra_modern_card_style,
)


class QuantumProgressBar(QProgressBar):
    """Enhanced progress bar with quantum effects"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_quantum_style()
        self.setup_neural_animations()

    def setup_quantum_style(self):
        """Setup quantum holographic styling"""
        self.setStyleSheet(
            f"""
            QProgressBar {{
                border: none;
                border-radius: 12px;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 0, 0, 0.4),
                    stop:1 rgba(0, 212, 255, 0.1)
                );
                text-align: center;
                font-family: 'Inter', 'Segoe UI', sans-serif;
                font-size: 12px;
                font-weight: 600;
                color: {UltraModernColors.TEXT_LUMINOUS};
                min-height: 20px;
                text-shadow: 0 0 8px {UltraModernColors.NEON_BLUE}60;
                backdrop-filter: blur(10px);
            }}
            QProgressBar::chunk {{
                border-radius: 12px;
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {UltraModernColors.NEON_BLUE},
                    stop:0.5 {UltraModernColors.NEON_PURPLE},
                    stop:1 {UltraModernColors.NEON_PINK}
                );
                box-shadow: 
                    0 0 15px rgba(0, 212, 255, 0.6),
                    inset 0 1px 0 rgba(255, 255, 255, 0.2);
            }}
        """
        )

        # Quantum glow effect
        self.glow_effect = QGraphicsDropShadowEffect()
        self.glow_effect.setBlurRadius(20)
        self.glow_effect.setColor(QColor(0, 212, 255, 100))
        self.glow_effect.setOffset(0, 0)
        self.setGraphicsEffect(self.glow_effect)

    def setup_neural_animations(self):
        """Setup neural animation system"""
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self.pulse_quantum_glow)
        self.glow_intensity = 100
        self.glow_direction = 1

    def pulse_quantum_glow(self):
        """Animate quantum glow pulsing"""
        self.glow_intensity += self.glow_direction * 20
        if self.glow_intensity >= 200:
            self.glow_direction = -1
        elif self.glow_intensity <= 60:
            self.glow_direction = 1

        self.glow_effect.setColor(QColor(0, 212, 255, self.glow_intensity))

    def setVisible(self, visible):
        """Override setVisible to control animations"""
        super().setVisible(visible)
        if visible:
            self.pulse_timer.start(150)
        else:
            self.pulse_timer.stop()


class NeuralStatusIndicator(QLabel):
    """Neural network status indicator with dynamic effects"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(24, 24)
        self.current_status = "idle"
        self.setup_neural_style()
        self.setup_status_animations()

    def setup_neural_style(self):
        """Setup neural indicator styling"""
        self.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        self.setAlignment(Qt.AlignCenter)
        self.setText("◯")

    def setup_status_animations(self):
        """Setup status animation system"""
        self.rotation_timer = QTimer()
        self.rotation_timer.timeout.connect(self.rotate_neural_symbol)
        self.symbol_index = 0
        self.neural_symbols = ["◯", "◉", "◎", "◈", "◆", "⬢"]

    def rotate_neural_symbol(self):
        """Rotate through neural symbols"""
        self.symbol_index = (self.symbol_index + 1) % len(self.neural_symbols)
        self.setText(self.neural_symbols[self.symbol_index])

    def update_neural_status(self, status):
        """Update neural status with appropriate styling"""
        self.current_status = status

        status_configs = {
            "idle": {
                "symbol": "◯",
                "color": UltraModernColors.TEXT_MUTED,
                "animate": False,
            },
            "processing": {
                "symbol": "◉",
                "color": UltraModernColors.NEON_BLUE,
                "animate": True,
            },
            "success": {
                "symbol": "◎",
                "color": UltraModernColors.NEON_GREEN,
                "animate": False,
            },
            "error": {
                "symbol": "◆",
                "color": UltraModernColors.NEON_PINK,
                "animate": False,
            },
            "warning": {
                "symbol": "◈",
                "color": UltraModernColors.NEON_YELLOW,
                "animate": False,
            },
        }

        config = status_configs.get(status, status_configs["idle"])

        # Apply styling
        self.setStyleSheet(
            f"""
            QLabel {{
                color: {config['color']};
                background: transparent;
                text-shadow: 
                    0 0 10px {config['color']},
                    0 0 20px {config['color']};
            }}
        """
        )

        # Control animation
        if config["animate"]:
            self.rotation_timer.start(300)
        else:
            self.rotation_timer.stop()
            self.setText(config["symbol"])


class QuantumMetricDisplay(QWidget):
    """Display quantum metrics with holographic styling"""

    def __init__(self, label_text, parent=None):
        super().__init__(parent)
        self.label_text = label_text
        self.setup_quantum_ui()

    def setup_quantum_ui(self):
        """Setup quantum metric UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Metric label
        self.label = QLabel(self.label_text)
        self.label.setFont(QFont("Inter", 9, QFont.Weight.Medium))
        self.label.setStyleSheet(
            f"""
            color: {UltraModernColors.TEXT_MUTED};
            background: transparent;
        """
        )

        # Metric value
        self.value = QLabel("--")
        self.value.setFont(QFont("Inter", 11, QFont.Weight.Bold))
        self.value.setStyleSheet(
            f"""
            color: {UltraModernColors.NEON_BLUE};
            background: transparent;
            text-shadow: 0 0 8px {UltraModernColors.NEON_BLUE}60;
        """
        )

        layout.addWidget(self.label)
        layout.addWidget(self.value)

    def update_quantum_value(self, value, status="normal"):
        """Update metric value with status coloring"""
        self.value.setText(str(value))

        colors = {
            "normal": UltraModernColors.NEON_BLUE,
            "success": UltraModernColors.NEON_GREEN,
            "warning": UltraModernColors.NEON_YELLOW,
            "error": UltraModernColors.NEON_PINK,
        }

        color = colors.get(status, UltraModernColors.NEON_BLUE)
        self.value.setStyleSheet(
            f"""
            color: {color};
            background: transparent;
            text-shadow: 0 0 8px {color}60;
        """
        )


class UltraModernProgressCard(QFrame):
    """Ultra modern progress card with quantum visualization"""

    # Signals
    progress_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_progress = 0
        self.current_status = "idle"
        self.setup_holographic_ui()
        self.setup_dimensional_effects()

    def setup_holographic_ui(self):
        """Setup holographic progress interface"""
        self.setMinimumHeight(160)
        self.setMaximumHeight(200)

        # Apply ultra modern card styling
        self.setStyleSheet(get_ultra_modern_card_style("elevated"))

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header section
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        # Neural status indicator
        self.neural_indicator = NeuralStatusIndicator()

        # Title
        self.title_label = QLabel("Quantum Progress Tracking")
        self.title_label.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        self.title_label.setStyleSheet(
            f"""
            QLabel {{
                color: {UltraModernColors.TEXT_LUMINOUS};
                background: transparent;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
            }}
        """
        )

        header_layout.addWidget(self.neural_indicator)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        # Progress section
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(12)

        # Quantum progress bar
        self.quantum_progress = QuantumProgressBar()
        self.quantum_progress.setVisible(False)

        # Progress message
        self.progress_message = QLabel("◦ Neural matrix ready for quantum operations ◦")
        self.progress_message.setFont(QFont("Inter", 12, QFont.Weight.Medium))
        self.progress_message.setStyleSheet(
            f"""
            QLabel {{
                color: {UltraModernColors.TEXT_GLOW};
                background: transparent;
                padding: 8px 0px;
                text-shadow: 0 0 8px {UltraModernColors.NEON_BLUE}40;
            }}
        """
        )
        self.progress_message.setAlignment(Qt.AlignCenter)
        self.progress_message.setWordWrap(True)

        progress_layout.addWidget(self.quantum_progress)
        progress_layout.addWidget(self.progress_message)

        # Metrics section
        metrics_container = QWidget()
        metrics_layout = QHBoxLayout(metrics_container)
        metrics_layout.setContentsMargins(0, 0, 0, 0)
        metrics_layout.setSpacing(20)

        # Quantum metrics
        self.speed_metric = QuantumMetricDisplay("Transfer Rate")
        self.records_metric = QuantumMetricDisplay("Data Packets")
        self.time_metric = QuantumMetricDisplay("Quantum Time")

        metrics_layout.addWidget(self.speed_metric)
        metrics_layout.addWidget(self.records_metric)
        metrics_layout.addWidget(self.time_metric)
        metrics_layout.addStretch()

        # Add all sections
        layout.addLayout(header_layout)
        layout.addLayout(progress_layout)
        layout.addWidget(metrics_container)

        # Make clickable
        self.setCursor(Qt.PointingHandCursor)

    def setup_dimensional_effects(self):
        """Setup dimensional shadow effects"""
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setBlurRadius(15)
        self.shadow_effect.setColor(QColor(0, 0, 0, 60))
        self.shadow_effect.setOffset(0, 8)
        self.setGraphicsEffect(self.shadow_effect)

        # Hover animation
        self.hover_animation = QPropertyAnimation(self, b"geometry")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.OutCubic)

    def update_quantum_progress(self, message, progress, level="info"):
        """Update quantum progress with neural styling"""
        self.current_progress = progress

        # Update neural indicator
        if progress > 0:
            self.neural_indicator.update_neural_status("processing")
        else:
            self.neural_indicator.update_neural_status("idle")

        # Update progress message with quantum styling
        level_symbols = {"info": "◉", "success": "◎", "warning": "◈", "error": "◆"}

        symbol = level_symbols.get(level, "◉")
        quantum_message = f"{symbol} {message}"

        self.progress_message.setText(quantum_message)

        # Update progress bar
        if progress > 0:
            self.quantum_progress.setVisible(True)
            self.quantum_progress.setValue(progress)

            # Update message color based on level
            level_colors = {
                "info": UltraModernColors.NEON_BLUE,
                "success": UltraModernColors.NEON_GREEN,
                "warning": UltraModernColors.NEON_YELLOW,
                "error": UltraModernColors.NEON_PINK,
            }

            color = level_colors.get(level, UltraModernColors.NEON_BLUE)
            self.progress_message.setStyleSheet(
                f"""
                QLabel {{
                    color: {color};
                    background: transparent;
                    padding: 8px 0px;
                    text-shadow: 0 0 12px {color}80;
                }}
            """
            )
        else:
            self.quantum_progress.setVisible(False)
            # Reset to default styling
            self.progress_message.setStyleSheet(
                f"""
                QLabel {{
                    color: {UltraModernColors.TEXT_GLOW};
                    background: transparent;
                    padding: 8px 0px;
                    text-shadow: 0 0 8px {UltraModernColors.NEON_BLUE}40;
                }}
            """
            )

    def update_quantum_metrics(self, speed="--", records="--", time="--"):
        """Update quantum operation metrics"""
        self.speed_metric.update_quantum_value(speed)
        self.records_metric.update_quantum_value(records)
        self.time_metric.update_quantum_value(time)

    def set_quantum_complete(self, success=True, message="Operation complete"):
        """Set completion state with appropriate neural styling"""
        if success:
            self.neural_indicator.update_neural_status("success")
            self.update_quantum_progress(f"✓ {message}", 0, "success")
        else:
            self.neural_indicator.update_neural_status("error")
            self.update_quantum_progress(f"✗ {message}", 0, "error")

    def reset_quantum_state(self):
        """Reset to initial quantum state"""
        self.neural_indicator.update_neural_status("idle")
        self.quantum_progress.setVisible(False)
        self.progress_message.setText("◦ Neural matrix ready for quantum operations ◦")
        self.update_quantum_metrics()

        # Reset styling
        self.progress_message.setStyleSheet(
            f"""
            QLabel {{
                color: {UltraModernColors.TEXT_GLOW};
                background: transparent;
                padding: 8px 0px;
                text-shadow: 0 0 8px {UltraModernColors.NEON_BLUE}40;
            }}
        """
        )

    def mousePressEvent(self, event):
        """Handle click events with quantum feedback"""
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.progress_clicked.emit()

    def enterEvent(self, event):
        """Enhanced hover effect"""
        super().enterEvent(event)

        # Enhance glow effect
        self.shadow_effect.setColor(QColor(0, 212, 255, 120))
        self.shadow_effect.setBlurRadius(25)

        # Subtle lift animation
        current_rect = self.geometry()
        hover_rect = QRect(
            current_rect.x(),
            current_rect.y() - 3,
            current_rect.width(),
            current_rect.height(),
        )

        self.hover_animation.setStartValue(current_rect)
        self.hover_animation.setEndValue(hover_rect)
        self.hover_animation.start()

    def leaveEvent(self, event):
        """Reset hover effect"""
        super().leaveEvent(event)

        # Reset glow
        self.shadow_effect.setColor(QColor(0, 0, 0, 60))
        self.shadow_effect.setBlurRadius(15)

        # Return to original position
        current_rect = self.geometry()
        normal_rect = QRect(
            current_rect.x(),
            current_rect.y() + 3,
            current_rect.width(),
            current_rect.height(),
        )

        self.hover_animation.setStartValue(current_rect)
        self.hover_animation.setEndValue(normal_rect)
        self.hover_animation.start()


# Backward compatibility
class ProgressCard(UltraModernProgressCard):
    """Alias สำหรับ backward compatibility"""

    pass


class CompactProgressIndicator(QWidget):
    """Compact progress indicator สำหรับ status bar หรือ small spaces"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)
        self.setMinimumWidth(120)
        self.setup_compact_ui()

    def setup_compact_ui(self):
        """Setup compact holographic UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)

        # Compact neural indicator
        self.indicator = QLabel("◯")
        self.indicator.setFont(QFont("Inter", 10, QFont.Weight.Bold))
        self.indicator.setFixedSize(16, 16)
        self.indicator.setAlignment(Qt.AlignCenter)

        # Compact text
        self.text_label = QLabel("Ready")
        self.text_label.setFont(QFont("Inter", 9, QFont.Weight.Medium))
        self.text_label.setStyleSheet(
            f"""
            color: {UltraModernColors.TEXT_LUMINOUS};
            background: transparent;
        """
        )

        layout.addWidget(self.indicator)
        layout.addWidget(self.text_label)
        layout.addStretch()

        # Compact holographic styling
        self.setStyleSheet(
            f"""
            QWidget {{
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(8px);
                border: 1px solid rgba(0, 212, 255, 0.2);
                border-radius: 8px;
            }}
            QWidget:hover {{
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(0, 212, 255, 0.4);
            }}
        """
        )

    def update_compact_status(self, message, status="info"):
        """Update compact status display"""
        self.text_label.setText(message)

        status_configs = {
            "info": {"symbol": "◉", "color": UltraModernColors.NEON_BLUE},
            "success": {"symbol": "◎", "color": UltraModernColors.NEON_GREEN},
            "warning": {"symbol": "◈", "color": UltraModernColors.NEON_YELLOW},
            "error": {"symbol": "◆", "color": UltraModernColors.NEON_PINK},
            "processing": {"symbol": "◐", "color": UltraModernColors.NEON_PURPLE},
        }

        config = status_configs.get(status, status_configs["info"])

        self.indicator.setText(config["symbol"])
        self.indicator.setStyleSheet(
            f"""
            color: {config['color']};
            background: transparent;
            text-shadow: 0 0 8px {config['color']};
        """
        )


class QuantumDataFlowVisualizer(QWidget):
    """Advanced data flow visualizer with quantum effects"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self.data_points = []
        self.setup_visualizer()
        self.setup_flow_animation()

    def setup_visualizer(self):
        """Setup quantum flow visualizer"""
        self.setStyleSheet(
            f"""
            QWidget {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 0, 0, 0.3),
                    stop:0.5 rgba(0, 212, 255, 0.1),
                    stop:1 rgba(0, 0, 0, 0.3)
                );
                border: 1px solid rgba(0, 212, 255, 0.2);
                border-radius: 12px;
            }}
        """
        )

    def setup_flow_animation(self):
        """Setup data flow animation"""
        self.flow_timer = QTimer()
        self.flow_timer.timeout.connect(self.animate_data_flow)
        self.flow_position = 0

    def start_quantum_flow(self):
        """Start quantum data flow animation"""
        self.flow_timer.start(100)

    def stop_quantum_flow(self):
        """Stop quantum data flow animation"""
        self.flow_timer.stop()

    def animate_data_flow(self):
        """Animate flowing data particles"""
        self.flow_position = (self.flow_position + 1) % 100
        self.update()  # Trigger repaint

    def paintEvent(self, event):
        """Custom paint for quantum data flow visualization"""
        super().paintEvent(event)

        if not self.flow_timer.isActive():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw flowing particles
        width = self.width()
        height = self.height()

        # Neural data particles
        particles = 8
        for i in range(particles):
            x = ((self.flow_position + i * 12) % (width + 20)) - 10
            y = height // 2 + (i % 3 - 1) * 15

            # Particle glow
            for radius in range(3, 0, -1):
                alpha = 100 - radius * 20
                painter.setBrush(QColor(0, 212, 255, alpha))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)

    def add_data_packet(self, size, type_name="data"):
        """Add data packet to flow visualization"""
        self.data_points.append(
            {"size": size, "type": type_name, "timestamp": datetime.now()}
        )

        # Keep only recent packets
        if len(self.data_points) > 50:
            self.data_points = self.data_points[-50:]


class NeuralSyncProgressWidget(QFrame):
    """Specialized widget for neural sync progress visualization"""

    sync_interrupted = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sync_stages = []
        self.current_stage = 0
        self.setup_neural_sync_ui()

    def setup_neural_sync_ui(self):
        """Setup neural synchronization UI"""
        self.setStyleSheet(get_ultra_modern_card_style("neon"))
        self.setMinimumHeight(200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Sync header
        header = QLabel("◈ Neural Synchronization Protocol")
        header.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        header.setStyleSheet(
            f"""
            color: {UltraModernColors.TEXT_LUMINOUS};
            text-shadow: 0 0 10px {UltraModernColors.NEON_BLUE};
        """
        )
        layout.addWidget(header)

        # Stage progress
        self.stage_progress = QuantumProgressBar()
        layout.addWidget(self.stage_progress)

        # Current stage display
        self.stage_label = QLabel("Initializing neural pathways...")
        self.stage_label.setFont(QFont("Inter", 11, QFont.Weight.Medium))
        self.stage_label.setStyleSheet(
            f"""
            color: {UltraModernColors.TEXT_GLOW};
            background: transparent;
        """
        )
        layout.addWidget(self.stage_label)

        # Data flow visualizer
        self.flow_viz = QuantumDataFlowVisualizer()
        layout.addWidget(self.flow_viz)

        # Stage list
        self.stages_widget = QWidget()
        self.stages_layout = QVBoxLayout(self.stages_widget)
        self.stages_layout.setContentsMargins(0, 0, 0, 0)
        self.stages_layout.setSpacing(4)
        layout.addWidget(self.stages_widget)

        # Control buttons
        control_layout = QHBoxLayout()

        self.pause_btn = QPushButton("⏸️ Pause Neural Sync")
        self.pause_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: rgba(255, 193, 7, 0.2);
                color: {UltraModernColors.NEON_YELLOW};
                border: 1px solid rgba(255, 193, 7, 0.3);
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }}
        """
        )

        self.abort_btn = QPushButton("⏹️ Abort Sync")
        self.abort_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: rgba(220, 53, 69, 0.2);
                color: {UltraModernColors.NEON_PINK};
                border: 1px solid rgba(220, 53, 69, 0.3);
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }}
        """
        )
        self.abort_btn.clicked.connect(self.sync_interrupted.emit)

        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.abort_btn)
        control_layout.addStretch()

        layout.addLayout(control_layout)

    def initialize_neural_sync(self, stages):
        """Initialize neural sync with defined stages"""
        self.sync_stages = stages
        self.current_stage = 0

        # Clear previous stage indicators
        for i in reversed(range(self.stages_layout.count())):
            self.stages_layout.itemAt(i).widget().setParent(None)

        # Create stage indicators
        for i, stage in enumerate(stages):
            stage_indicator = self.create_stage_indicator(stage, i)
            self.stages_layout.addWidget(stage_indicator)

        # Start flow visualization
        self.flow_viz.start_quantum_flow()

    def create_stage_indicator(self, stage_name, index):
        """Create individual stage indicator"""
        indicator = QWidget()
        indicator.setFixedHeight(24)

        layout = QHBoxLayout(indicator)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        # Stage symbol
        symbol = QLabel("◯")
        symbol.setFont(QFont("Inter", 10))
        symbol.setFixedSize(16, 16)

        # Stage name
        name = QLabel(stage_name)
        name.setFont(QFont("Inter", 9))

        layout.addWidget(symbol)
        layout.addWidget(name)
        layout.addStretch()

        # Store references for updates
        indicator.symbol = symbol
        indicator.name = name
        indicator.stage_index = index

        return indicator

    def update_neural_stage(self, stage_index, progress, message=""):
        """Update current neural sync stage"""
        if stage_index < len(self.sync_stages):
            self.current_stage = stage_index

            # Update stage progress
            self.stage_progress.setValue(progress)

            # Update stage message
            stage_name = self.sync_stages[stage_index]
            if message:
                self.stage_label.setText(f"{stage_name}: {message}")
            else:
                self.stage_label.setText(stage_name)

            # Update stage indicators
            for i in range(self.stages_layout.count()):
                widget = self.stages_layout.itemAt(i).widget()
                if hasattr(widget, "stage_index"):
                    if widget.stage_index < stage_index:
                        # Completed stage
                        widget.symbol.setText("◎")
                        widget.symbol.setStyleSheet(
                            f"color: {UltraModernColors.NEON_GREEN};"
                        )
                    elif widget.stage_index == stage_index:
                        # Current stage
                        widget.symbol.setText("◉")
                        widget.symbol.setStyleSheet(
                            f"color: {UltraModernColors.NEON_BLUE};"
                        )
                    else:
                        # Pending stage
                        widget.symbol.setText("◯")
                        widget.symbol.setStyleSheet(
                            f"color: {UltraModernColors.TEXT_MUTED};"
                        )

    def complete_neural_sync(self, success=True):
        """Complete neural synchronization"""
        self.flow_viz.stop_quantum_flow()

        if success:
            self.stage_progress.setValue(100)
            self.stage_label.setText("◎ Neural synchronization complete")

            # Mark all stages as complete
            for i in range(self.stages_layout.count()):
                widget = self.stages_layout.itemAt(i).widget()
                if hasattr(widget, "symbol"):
                    widget.symbol.setText("◎")
                    widget.symbol.setStyleSheet(
                        f"color: {UltraModernColors.NEON_GREEN};"
                    )
        else:
            self.stage_label.setText("◆ Neural synchronization failed")

            # Mark current stage as failed
            if self.current_stage < self.stages_layout.count():
                widget = self.stages_layout.itemAt(self.current_stage).widget()
                if hasattr(widget, "symbol"):
                    widget.symbol.setText("◆")
                    widget.symbol.setStyleSheet(
                        f"color: {UltraModernColors.NEON_PINK};"
                    )
