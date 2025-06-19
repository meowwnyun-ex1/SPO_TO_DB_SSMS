from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QCheckBox,
    QTextEdit,
    QProgressBar,
    QScrollArea,
    QSizePolicy,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import (
    Qt,
    pyqtSignal,
    pyqtSlot,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    QRect,
)
from PyQt6.QtGui import QFont, QColor
from ..widgets.status_card import UltraModernStatusCard
from ..styles.theme import (
    UltraModernColors,
    get_ultra_modern_card_style,
    get_ultra_modern_button_style,
    get_neon_checkbox_style,
    get_cyber_log_style,
    get_holographic_progress_style,
    get_background_image_style,
)
import logging

logger = logging.getLogger(__name__)


class HolographicFrame(QFrame):
    """เฟรมแบบ holographic พร้อม dimensional effects"""

    def __init__(self, variant="default", parent=None):
        super().__init__(parent)
        self.variant = variant
        self.setup_holographic_style()
        self.setup_hover_effects()

    def setup_holographic_style(self):
        """ตั้งค่าสไตล์ holographic"""
        style = get_ultra_modern_card_style(self.variant)
        self.setStyleSheet(style)

        # เพิ่ม shadow effects
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setBlurRadius(20)
        self.shadow_effect.setColor(QColor(0, 0, 0, 80))
        self.shadow_effect.setOffset(0, 10)
        self.setGraphicsEffect(self.shadow_effect)

    def setup_hover_effects(self):
        """ตั้งค่า hover animations"""
        self.hover_animation = QPropertyAnimation(self, b"geometry")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.OutCubic)

    def enterEvent(self, event):
        """Hover effect"""
        super().enterEvent(event)
        # เพิ่ม glow effect
        self.shadow_effect.setColor(QColor(0, 212, 255, 120))
        self.shadow_effect.setBlurRadius(30)

    def leaveEvent(self, event):
        """Reset hover"""
        super().leaveEvent(event)
        self.shadow_effect.setColor(QColor(0, 0, 0, 80))
        self.shadow_effect.setBlurRadius(20)


class NeonSectionHeader(QFrame):
    """หัวข้อส่วนแบบ neon glow"""

    def __init__(self, title, icon="", parent=None):
        super().__init__(parent)
        self.title = title
        self.icon = icon
        self.setup_neon_ui()

    def setup_neon_ui(self):
        """ตั้งค่า UI แบบ neon"""
        self.setFixedHeight(60)

        # Holographic background
        self.setStyleSheet(
            f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {UltraModernColors.NEON_BLUE}40,
                    stop:0.3 {UltraModernColors.NEON_PURPLE}30,
                    stop:0.7 {UltraModernColors.NEON_PINK}40,
                    stop:1 {UltraModernColors.NEON_BLUE}40
                );
                border: 2px solid {UltraModernColors.NEON_BLUE};
                border-radius: 16px;
                box-shadow: 
                    0 0 20px rgba(0, 212, 255, 0.5),
                    inset 0 0 20px rgba(0, 212, 255, 0.1);
            }}
            QLabel {{
                background: transparent;
                color: {UltraModernColors.TEXT_LUMINOUS};
                font-weight: 700;
                text-shadow: 
                    0 0 10px {UltraModernColors.NEON_BLUE},
                    0 2px 4px rgba(0, 0, 0, 0.5);
            }}
        """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)

        # Icon + Title
        label_text = f"{self.icon} {self.title}" if self.icon else self.title
        label = QLabel(label_text)
        label.setFont(QFont("Inter", 16, QFont.Bold))

        layout.addWidget(label)
        layout.addStretch()

        # เพิ่ม glow effect
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(25)
        glow.setColor(QColor(0, 212, 255, 100))
        glow.setOffset(0, 0)
        self.setGraphicsEffect(glow)


class CyberButton(QPushButton):
    """ปุ่มแบบ cyberpunk พร้อม advanced effects"""

    def __init__(self, text, variant="primary", size="md", parent=None):
        super().__init__(text, parent)
        self.variant = variant
        self.size = size
        self.setup_cyber_style()
        self.setup_animations()

    def setup_cyber_style(self):
        """ตั้งค่าสไตล์ cyberpunk"""
        style = get_ultra_modern_button_style(self.variant, self.size)
        self.setStyleSheet(style)

        # เพิ่ม glow effect
        self.glow_effect = QGraphicsDropShadowEffect()
        self.glow_effect.setBlurRadius(15)
        self.glow_effect.setColor(QColor(102, 126, 234, 80))
        self.glow_effect.setOffset(0, 0)
        self.setGraphicsEffect(self.glow_effect)

    def setup_animations(self):
        """ตั้งค่า hover animations"""
        self.press_animation = QPropertyAnimation(self, b"geometry")
        self.press_animation.setDuration(100)
        self.press_animation.setEasingCurve(QEasingCurve.OutCubic)

    def enterEvent(self, event):
        """Hover glow effect"""
        super().enterEvent(event)
        if self.variant == "primary":
            self.glow_effect.setColor(QColor(0, 212, 255, 150))
        elif self.variant == "success":
            self.glow_effect.setColor(QColor(57, 255, 20, 150))
        elif self.variant == "warning":
            self.glow_effect.setColor(QColor(255, 107, 0, 150))
        self.glow_effect.setBlurRadius(25)

    def leaveEvent(self, event):
        """Reset glow"""
        super().leaveEvent(event)
        self.glow_effect.setColor(QColor(102, 126, 234, 80))
        self.glow_effect.setBlurRadius(15)

    def mousePressEvent(self, event):
        """Press animation"""
        super().mousePressEvent(event)
        # Scale down effect
        current_rect = self.geometry()
        pressed_rect = QRect(
            current_rect.x() + 2,
            current_rect.y() + 2,
            current_rect.width() - 4,
            current_rect.height() - 4,
        )
        self.press_animation.setStartValue(current_rect)
        self.press_animation.setEndValue(pressed_rect)
        self.press_animation.start()


class HolographicProgressBar(QProgressBar):
    """Progress bar แบบ holographic"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_holographic_style()
        self.setup_glow_animation()

    def setup_holographic_style(self):
        """ตั้งค่าสไตล์ holographic"""
        style = get_holographic_progress_style()
        self.setStyleSheet(style)

        # เพิ่ม glow effect
        self.glow_effect = QGraphicsDropShadowEffect()
        self.glow_effect.setBlurRadius(20)
        self.glow_effect.setColor(QColor(102, 126, 234, 100))
        self.glow_effect.setOffset(0, 0)
        self.setGraphicsEffect(self.glow_effect)

    def setup_glow_animation(self):
        """ตั้งค่า glow animation"""
        self.glow_timer = QTimer()
        self.glow_timer.timeout.connect(self.animate_glow)
        self.glow_intensity = 100
        self.glow_direction = 1

    def animate_glow(self):
        """Animation สำหรับ glow effect"""
        self.glow_intensity += self.glow_direction * 20
        if self.glow_intensity >= 200:
            self.glow_direction = -1
        elif self.glow_intensity <= 50:
            self.glow_direction = 1

        self.glow_effect.setColor(QColor(102, 126, 234, self.glow_intensity))

    def setVisible(self, visible):
        """Override setVisible เพื่อควบคุม animation"""
        super().setVisible(visible)
        if visible:
            self.glow_timer.start(100)
        else:
            self.glow_timer.stop()


class CyberLogConsole(QTextEdit):
    """Console แบบ cyberpunk terminal"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_cyber_style()
        self.setup_typing_effect()

    def setup_cyber_style(self):
        """ตั้งค่าสไตล์ cyberpunk terminal"""
        style = get_cyber_log_style()
        self.setStyleSheet(style)

        # เพิ่ม terminal properties
        self.setReadOnly(True)
        self.setPlaceholderText("🔍 Neural network activity monitoring initialized...")

        # เพิ่ม glow effect
        self.glow_effect = QGraphicsDropShadowEffect()
        self.glow_effect.setBlurRadius(25)
        self.glow_effect.setColor(QColor(0, 212, 255, 80))
        self.glow_effect.setOffset(0, 0)
        self.setGraphicsEffect(self.glow_effect)

    def setup_typing_effect(self):
        """ตั้งค่า typing effect"""
        self.typing_timer = QTimer()
        self.current_message = ""
        self.typing_index = 0

    def add_message_with_typing(self, message, level="info"):
        """เพิ่มข้อความแบบ typing effect"""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        # สีตาม level
        colors = {
            "info": UltraModernColors.NEON_BLUE,
            "success": UltraModernColors.NEON_GREEN,
            "warning": UltraModernColors.NEON_YELLOW,
            "error": UltraModernColors.NEON_PINK,
            "debug": UltraModernColors.NEON_PURPLE,
        }

        # ไอคอนตาม level
        icons = {
            "info": "◉",
            "success": "◎",
            "warning": "◈",
            "error": "◆",
            "debug": "◇",
        }

        color = colors.get(level, UltraModernColors.NEON_GREEN)
        icon = icons.get(level, "◉")

        # สร้าง HTML message พร้อม cyber styling
        formatted_message = f"""
        <div style="
            margin: 8px 0; 
            padding: 8px 0; 
            border-left: 3px solid {color}; 
            padding-left: 16px;
            background: linear-gradient(90deg, {color}10, transparent);
        ">
            <span style="
                color: #64748b; 
                font-size: 11px; 
                font-family: 'JetBrains Mono', monospace;
            ">[{timestamp}]</span>
            <span style="
                color: {color}; 
                font-weight: 600; 
                margin-left: 12px;
                text-shadow: 0 0 8px {color}80;
            ">{icon} {message}</span>
        </div>
        """

        self.append(formatted_message)

        # Auto scroll with smooth animation
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


class UltraModernDashboard(QWidget):
    """Dashboard แบบ ultra modern holographic พร้อม dimensional effects"""

    # Signals
    test_connections_requested = pyqtSignal()
    start_sync_requested = pyqtSignal()
    stop_sync_requested = pyqtSignal()
    clear_logs_requested = pyqtSignal()
    auto_sync_toggled = pyqtSignal(bool, int)

    def __init__(self, controller):
        super().__init__(controller)
        self.controller = controller
        self.setup_ultra_modern_ui()
        self.setup_background_effects()

    def setup_ultra_modern_ui(self):
        """ตั้งค่า UI แบบ ultra modern"""
        # Main scroll area สำหรับ responsive design
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet(
            f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: rgba(0, 0, 0, 0.3);
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {UltraModernColors.NEON_BLUE};
                border-radius: 6px;
                min-height: 30px;
                box-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
            }}
            QScrollBar::handle:vertical:hover {{
                background: {UltraModernColors.NEON_PURPLE};
                box-shadow: 0 0 15px rgba(189, 94, 255, 0.7);
            }}
        """
        )

        # Scroll content
        scroll_content = QWidget()
        scroll.setWidget(scroll_content)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # Content layout พร้อม responsive margins
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(30)

        # สร้างส่วนต่างๆ
        self.create_holographic_header(content_layout)
        self.create_neural_connection_section(content_layout)
        self.create_quantum_progress_section(content_layout)
        self.create_cyber_control_section(content_layout)
        self.create_matrix_logs_section(content_layout)

    def setup_background_effects(self):
        """ตั้งค่า background effects"""
        # ใช้ background image หรือ gradient
        bg_style = get_background_image_style()
        self.setStyleSheet(
            f"""
            QWidget {{
                {bg_style}
            }}
        """
        )

    def create_holographic_header(self, layout):
        """สร้าง brand header แบบ holographic"""
        header = HolographicFrame("holographic")
        header.setMinimumHeight(120)
        header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(40, 24, 40, 24)
        header_layout.setSpacing(12)

        # Title แบบ holographic
        title = QLabel("SharePoint ◈ Microsoft SQL")
        title.setFont(QFont("Inter", 26, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"""
            color: {UltraModernColors.TEXT_LUMINOUS};
            text-shadow: 
                0 0 20px {UltraModernColors.NEON_BLUE},
                0 4px 8px rgba(0, 0, 0, 0.5);
            letter-spacing: 1px;
        """
        )

        # Subtitle แบบ neon
        subtitle = QLabel("◦ Neural Data Synchronization Matrix ◦")
        subtitle.setFont(QFont("Inter", 14, QFont.Medium))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(
            f"""
            color: {UltraModernColors.NEON_BLUE};
            text-shadow: 
                0 0 15px {UltraModernColors.NEON_BLUE},
                0 2px 4px rgba(0, 0, 0, 0.3);
            letter-spacing: 0.5px;
            margin-top: 8px;
        """
        )

        # Credit line
        credit = QLabel("Thammaphon Chittasuwanna (SDM) | Innovation Department")
        credit.setFont(QFont("Inter", 10, QFont.Normal))
        credit.setAlignment(Qt.AlignCenter)
        credit.setStyleSheet(
            f"""
            color: rgba(255, 255, 255, 0.7);
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
            margin-top: 4px;
        """
        )

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addWidget(credit)
        layout.addWidget(header)

    def create_neural_connection_section(self, layout):
        """สร้าง connection status section แบบ neural network"""
        conn_frame = HolographicFrame("elevated")

        conn_layout = QVBoxLayout(conn_frame)
        conn_layout.setContentsMargins(28, 28, 28, 28)
        conn_layout.setSpacing(24)

        # Section header แบบ neon
        header = NeonSectionHeader("Neural Network Status", "⬢")
        conn_layout.addWidget(header)

        # Status cards layout
        cards_container = QWidget()
        cards_layout = QHBoxLayout(cards_container)
        cards_layout.setSpacing(20)

        # สร้าง ultra modern status cards
        self.sp_status = UltraModernStatusCard("SharePoint Matrix", "disconnected")
        self.db_status = UltraModernStatusCard("Database Node", "disconnected")
        self.sync_status = UltraModernStatusCard("Sync Protocol", "never")

        # Responsive sizing
        for card in [self.sp_status, self.db_status, self.sync_status]:
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            card.status_clicked.connect(self.on_status_card_clicked)

        cards_layout.addWidget(self.sp_status)
        cards_layout.addWidget(self.db_status)
        cards_layout.addWidget(self.sync_status)

        conn_layout.addWidget(cards_container)
        layout.addWidget(conn_frame)

    def create_quantum_progress_section(self, layout):
        """สร้าง progress section แบบ quantum"""
        progress_frame = HolographicFrame("neon")

        prog_layout = QVBoxLayout(progress_frame)
        prog_layout.setContentsMargins(28, 28, 28, 28)
        prog_layout.setSpacing(24)

        # Section header
        header = NeonSectionHeader("Quantum Data Transfer", "◈")
        prog_layout.addWidget(header)

        # Progress content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(16)

        # Holographic progress bar
        self.progress_bar = HolographicProgressBar()
        self.progress_bar.setVisible(False)

        # Progress message แบบ cyber
        self.progress_message = QLabel("◦ System ready for neural synchronization ◦")
        self.progress_message.setFont(QFont("Inter", 13, QFont.Medium))
        self.progress_message.setStyleSheet(
            f"""
            color: {UltraModernColors.TEXT_GLOW};
            background: transparent;
            padding: 12px 0px;
            text-shadow: 0 0 8px {UltraModernColors.NEON_BLUE}80;
        """
        )
        self.progress_message.setAlignment(Qt.AlignCenter)

        content_layout.addWidget(self.progress_bar)
        content_layout.addWidget(self.progress_message)

        prog_layout.addLayout(content_layout)
        layout.addWidget(progress_frame)

    def create_cyber_control_section(self, layout):
        """สร้าง control panel แบบ cyberpunk"""
        control_frame = HolographicFrame("elevated")

        ctrl_layout = QVBoxLayout(control_frame)
        ctrl_layout.setContentsMargins(28, 28, 28, 28)
        ctrl_layout.setSpacing(24)

        # Section header
        header = NeonSectionHeader("Command Matrix", "⬡")
        ctrl_layout.addWidget(header)

        # Control content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)

        # Main action buttons - responsive
        main_buttons_container = QWidget()
        main_buttons = QHBoxLayout(main_buttons_container)
        main_buttons.setSpacing(16)

        self.test_btn = CyberButton("◉ Neural Probe", "primary", "lg")
        self.test_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.test_btn.clicked.connect(self.test_connections_requested.emit)

        self.sync_btn = CyberButton("◈ Initiate Sync", "success", "lg")
        self.sync_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.sync_btn.clicked.connect(self._toggle_sync)

        main_buttons.addWidget(self.test_btn)
        main_buttons.addWidget(self.sync_btn)

        # Secondary controls - responsive
        secondary_container = QWidget()
        secondary_layout = QHBoxLayout(secondary_container)
        secondary_layout.setSpacing(16)

        self.clear_btn = CyberButton("◇ Purge Logs", "warning", "md")
        self.clear_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.clear_btn.clicked.connect(self.clear_logs_requested.emit)

        # Enhanced auto sync checkbox
        self.auto_sync_check = QCheckBox("◦ Autonomous Neural Sync")
        self.auto_sync_check.setStyleSheet(get_neon_checkbox_style())
        self.auto_sync_check.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.auto_sync_check.toggled.connect(self._toggle_auto_sync)

        secondary_layout.addWidget(self.clear_btn)
        secondary_layout.addWidget(self.auto_sync_check)

        content_layout.addWidget(main_buttons_container)
        content_layout.addWidget(secondary_container)

        ctrl_layout.addLayout(content_layout)
        layout.addWidget(control_frame)

    def create_matrix_logs_section(self, layout):
        """สร้าง logs section แบบ matrix terminal"""
        logs_frame = HolographicFrame("neon")

        logs_layout = QVBoxLayout(logs_frame)
        logs_layout.setContentsMargins(28, 28, 28, 28)
        logs_layout.setSpacing(24)

        # Section header
        header = NeonSectionHeader("Neural Activity Matrix", "◎")
        logs_layout.addWidget(header)

        # Cyber log console
        self.log_console = CyberLogConsole()
        self.log_console.setMinimumHeight(160)
        self.log_console.setMaximumHeight(220)

        logs_layout.addWidget(self.log_console)
        layout.addWidget(logs_frame)

    # Event handlers
    def _toggle_sync(self):
        """Toggle sync operation"""
        if self.controller.get_sync_status()["is_running"]:
            self.stop_sync_requested.emit()
        else:
            self.start_sync_requested.emit()

    def _toggle_auto_sync(self, checked):
        """Toggle auto sync"""
        self.auto_sync_toggled.emit(checked, 3600)

    def on_status_card_clicked(self, status):
        """Handle status card clicks"""
        logger.info(f"Status card clicked: {status}")

    # Public update methods
    @pyqtSlot(str, str)
    def update_connection_status(self, service, status):
        """อัปเดตสถานะการเชื่อมต่อ"""
        if service == "SharePoint":
            self.sp_status.update_status(status)
        elif service == "Database":
            self.db_status.update_status(status)

    @pyqtSlot(str, int, str)
    def update_progress(self, message, progress, level):
        """อัปเดต progress"""
        cyber_message = f"◦ {message} ◦"
        self.progress_message.setText(cyber_message)

        if progress > 0:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(progress)
        else:
            self.progress_bar.setVisible(False)

    @pyqtSlot(bool, str, dict)
    def on_sync_completed(self, success, message, stats):
        """Handle sync completion"""
        self.progress_bar.setVisible(False)

        if success:
            self.sync_btn.setText("◈ Initiate Sync")
            self.sync_status.update_status("success", "Neural sync complete")
            self.progress_message.setText("✓ Quantum data transfer successful")
        else:
            self.sync_btn.setText("◈ Initiate Sync")
            self.sync_status.update_status("error", "Sync protocol failed")
            self.progress_message.setText("✗ Neural network disruption detected")

    def add_log_message(self, message, level):
        """เพิ่มข้อความ log แบบ cyber"""
        self.log_console.add_message_with_typing(message, level)

    def clear_logs(self):
        """ล้าง logs"""
        self.log_console.clear()
        self.add_log_message("Neural matrix purged - system ready", "info")

    def set_auto_sync_enabled(self, enabled):
        """ตั้งค่า auto sync"""
        self.auto_sync_check.setChecked(enabled)

    def resizeEvent(self, event):
        """Handle responsive behavior"""
        super().resizeEvent(event)

        # ปรับ margins ตาม window size
        width = self.width()
        if width < 800:
            margins = (15, 15, 15, 15)
            spacing = 15
        elif width < 1200:
            margins = (25, 25, 25, 25)
            spacing = 20
        else:
            margins = (30, 30, 30, 30)
            spacing = 30

        # อัปเดต layout margins
        scroll_widget = self.findChild(QScrollArea).widget()
        if scroll_widget and scroll_widget.layout():
            scroll_widget.layout().setContentsMargins(*margins)
            scroll_widget.layout().setSpacing(spacing)


# Backward compatibility
class Dashboard(UltraModernDashboard):
    """Alias สำหรับ backward compatibility"""

    pass
