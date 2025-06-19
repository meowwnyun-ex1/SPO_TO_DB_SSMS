from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QCheckBox,
    QScrollArea,
    QSizePolicy,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import (
    Qt,
    pyqtSignal,
    pyqtSlot,
)
from PyQt6.QtGui import QFont, QColor
from ..widgets.status_card import UltraModernStatusCard
from ..widgets.cyber_log_console import CyberLogConsole
from ..widgets.holographic_progress_bar import HolographicProgressBar
from ..styles.theme import (
    UltraModernColors,
    get_ultra_modern_card_style,
)
import logging
import os
import tempfile
import shutil

logger = logging.getLogger(__name__)


class AppController:
    def __init__(self):
        self.sync_running = False

    def get_sync_status(self):
        return {"is_running": self.sync_running}

    def clear_system_cache(self):
        try:
            temp_dir = tempfile.gettempdir()
            app_cache_dir = os.path.join(temp_dir, "spo_to_db_cache")
            if os.path.exists(app_cache_dir):
                shutil.rmtree(app_cache_dir)
            os.makedirs(app_cache_dir, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False


class HolographicFrame(QFrame):
    """เฟรมแบบ holographic พร้อม dimensional effects"""

    def __init__(self, variant="default", parent=None):
        super().__init__(parent)
        self.variant = variant
        self.setup_holographic_style()
        # If setup_hover_effects is not implemented, comment or remove the next line
        # self.setup_hover_effects()

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


class GradientHeaderFrame(QFrame):
    """Enhanced gradient header with animations"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            """
            QFrame {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #667eea,
            stop:0.3 #764ba2,
            stop:0.6 #f093fb,
            stop:1 #f5576c);
            border: none;
            border-radius: 20px;
            }
            QLabel {
            background: transparent;
            color: #ffffff;
            }
            """
        )

        # Add glow effect
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(30)
        glow.setColor(QColor(102, 126, 234, 100))
        glow.setOffset(0, 0)
        self.setGraphicsEffect(glow)


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
            }}
            QLabel {{
                background: transparent;
                color: {UltraModernColors.TEXT_LUMINOUS};
                font-weight: 700;
            }}
            """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)

        # Icon + Title
        label_text = f"{self.icon} {self.title}" if self.icon else self.title
        label = QLabel(label_text)
        label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))

        layout.addWidget(label)
        layout.addStretch()


class Dashboard(QWidget):
    """Modern Responsive Dashboard with Glassmorphism Design"""

    # Signals
    test_connections_requested = pyqtSignal()
    start_sync_requested = pyqtSignal()
    stop_sync_requested = pyqtSignal()
    clear_logs_requested = pyqtSignal()
    auto_sync_toggled = pyqtSignal(bool, int)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ultra_modern_ui()
        # If setup_background_effects is not implemented, comment or remove the next line
        # self.setup_background_effects()

    def setup_ultra_modern_ui(self):
        """ตั้งค่า UI แบบ ultra modern"""
        # Main scroll area สำหรับ responsive design
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
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

            }}
            QScrollBar::handle:vertical:hover {{
            background: {UltraModernColors.NEON_PURPLE};

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

    def create_holographic_header(self, layout):
        self.create_brand_header(layout)

    def create_brand_header(self, layout):
        """Enhanced brand header with modern typography"""
        header = GradientHeaderFrame()
        header.setMinimumHeight(100)
        header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(40, 24, 40, 24)
        header_layout.setSpacing(12)

        # Main title with enhanced typography
        title = QLabel("SharePoint to Microsoft SQL")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            """
            color: #ffffff;

            letter-spacing: 0.5px;
            """
        )

        # Enhanced subtitle
        subtitle = QLabel("Thammaphon Chittasuwanna (SDM) | Innovation")
        subtitle.setFont(QFont("Segoe UI", 12, QFont.Weight.Normal))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(
            """
            color: rgba(255,255,255,0.9);

            font-weight: 500;
            letter-spacing: 0.3px;
            """
        )

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        # If credit is not defined, comment or remove the next line
        # header_layout.addWidget(credit)

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
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

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

        # Enhanced progress message
        self.progress_message = QLabel("Ready to synchronize data")
        self.progress_message.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        self.progress_message.setStyleSheet(
            f"""
            color: {UltraModernColors.TEXT_GLOW};
            background: transparent;
            padding: 12px 0px;

            """
        )
        self.progress_message.setAlignment(Qt.AlignmentFlag.AlignLeft)

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

        self.test_btn = QPushButton("🔍 Test Connections")
        self.test_btn.setStyleSheet(self.get_modern_primary_button_style())
        self.test_btn.setMinimumHeight(48)
        self.test_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.test_btn.clicked.connect(self.test_connections_requested.emit)

        self.sync_btn = QPushButton("🚀 Start Sync")
        self.sync_btn.setStyleSheet(self.get_modern_success_button_style())
        self.sync_btn.setMinimumHeight(48)
        self.sync_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.sync_btn.clicked.connect(self._toggle_sync)

        main_buttons.addWidget(self.test_btn)
        main_buttons.addWidget(self.sync_btn)

        # Secondary controls - responsive
        secondary_container = QWidget()
        secondary_layout = QHBoxLayout(secondary_container)
        secondary_layout.setSpacing(16)

        self.clear_btn = QPushButton("🧹 Clear Logs")
        self.clear_btn.setStyleSheet(self.get_modern_warning_button_style())
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.clear_btn.clicked.connect(self.clear_logs_requested.emit)

        # Enhanced auto sync checkbox
        self.auto_sync_check = QCheckBox("🔄 Auto Sync Every Hour")
        self.auto_sync_check.setStyleSheet(self.get_modern_checkbox_style())
        self.auto_sync_check.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
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

    def get_modern_primary_button_style(self):
        return """
            QPushButton {
                background: #2196F3;
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1976D2;
            }
        """

    def get_modern_success_button_style(self):
        return """
            QPushButton {
                background: #4CAF50;
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #388E3C;
            }
        """

    def get_modern_warning_button_style(self):
        return """
            QPushButton {
                background: #FF9800;
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #F57C00;
            }
        """

    def get_modern_checkbox_style(self):
        return """
            QCheckBox {
                color: white;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #2196F3;
            }
            QCheckBox::indicator:unchecked {
                background: transparent;
            }
            QCheckBox::indicator:checked {
                background: #2196F3;
            }
        """

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
class UltraModernDashboard(Dashboard):
    """Alias สำหรับ backward compatibility"""

    pass
    pass
