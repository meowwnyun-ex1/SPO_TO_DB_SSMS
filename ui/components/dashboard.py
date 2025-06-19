from PyQt5.QtWidgets import (
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
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QColor
from ..widgets.status_card import StatusCard
import logging

logger = logging.getLogger(__name__)


class ModernFrame(QFrame):
    """Enhanced frame with glassmorphism effect"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            """
            QFrame {
                background: rgba(45, 55, 72, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 16px;
                backdrop-filter: blur(10px);
            }
        """
        )

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 10)
        self.setGraphicsEffect(shadow)


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


class SectionHeader(QFrame):
    """Modern section header with icon support"""

    def __init__(self, title, icon="", parent=None):
        super().__init__(parent)
        self.title = title
        self.icon = icon
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d4ff, 
                    stop:0.5 #5b73ff, 
                    stop:1 #00d4ff);
                border: none;
                border-radius: 10px;
                min-height: 50px;
                max-height: 50px;
            }
            QLabel {
                background: transparent;
                color: #ffffff;
                font-weight: 700;
                font-size: 14px;
                text-shadow: 0px 2px 4px rgba(0,0,0,0.3);
            }
        """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)

        label_text = f"{self.icon} {self.title}" if self.icon else self.title
        label = QLabel(label_text)
        label.setFont(QFont("Segoe UI", 14, QFont.Bold))

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
        self.setup_ui()

    def setup_ui(self):
        """Responsive layout with modern design"""
        # Main scroll area for responsiveness
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(26, 32, 44, 0.5);
                width: 8px;
                border-radius: 4px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 212, 255, 0.7);
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(0, 212, 255, 0.9);
            }
        """
        )

        # Scroll content
        scroll_content = QWidget()
        scroll.setWidget(scroll_content)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # Content layout with responsive margins
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(25)

        # Create sections
        self.create_brand_header(content_layout)
        self.create_connection_section(content_layout)
        self.create_progress_section(content_layout)
        self.create_control_section(content_layout)
        self.create_logs_section(content_layout)

    def create_brand_header(self, layout):
        """Enhanced brand header with modern typography"""
        header = GradientHeaderFrame()
        header.setMinimumHeight(100)
        header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(30, 20, 30, 20)
        header_layout.setSpacing(8)

        # Main title with enhanced typography
        title = QLabel("SharePoint to Microsoft SQL")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            """
            color: #ffffff;
            text-shadow: 0px 3px 6px rgba(0,0,0,0.4);
            letter-spacing: 0.5px;
        """
        )

        # Enhanced subtitle
        subtitle = QLabel("Thammaphon Chittasuwanna (SDM) | Innovation")
        subtitle.setFont(QFont("Segoe UI", 12, QFont.Normal))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(
            """
            color: rgba(255,255,255,0.9);
            text-shadow: 0px 2px 4px rgba(0,0,0,0.3);
            font-weight: 500;
            letter-spacing: 0.3px;
        """
        )

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addWidget(header)

    def create_connection_section(self, layout):
        """Enhanced connection status section"""
        conn_frame = ModernFrame()

        conn_layout = QVBoxLayout(conn_frame)
        conn_layout.setContentsMargins(25, 25, 25, 25)
        conn_layout.setSpacing(20)

        # Modern section header
        header = SectionHeader("Connection Status", "🔗")
        conn_layout.addWidget(header)

        # Responsive status cards layout
        cards_container = QWidget()
        cards_layout = QHBoxLayout(cards_container)
        cards_layout.setSpacing(15)

        self.sp_status = StatusCard("SharePoint", "disconnected")
        self.db_status = StatusCard("Database", "disconnected")
        self.sync_status = StatusCard("Last Sync", "never")

        # Make cards responsive
        for card in [self.sp_status, self.db_status, self.sync_status]:
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        cards_layout.addWidget(self.sp_status)
        cards_layout.addWidget(self.db_status)
        cards_layout.addWidget(self.sync_status)

        conn_layout.addWidget(cards_container)
        layout.addWidget(conn_frame)

    def create_progress_section(self, layout):
        """Enhanced progress section with animations"""
        progress_frame = ModernFrame()

        prog_layout = QVBoxLayout(progress_frame)
        prog_layout.setContentsMargins(25, 25, 25, 25)
        prog_layout.setSpacing(20)

        # Modern section header
        header = SectionHeader("Sync Progress", "📊")
        prog_layout.addWidget(header)

        # Progress content with better spacing
        content_layout = QVBoxLayout()
        content_layout.setSpacing(15)

        # Enhanced progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: none;
                border-radius: 8px;
                background: rgba(26, 32, 44, 0.8);
                text-align: center;
                font-weight: 600;
                color: #ffffff;
                min-height: 16px;
                max-height: 16px;
                font-size: 12px;
            }
            QProgressBar::chunk {
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #48bb78, 
                    stop:0.5 #38a169, 
                    stop:1 #2f855a);
            }
        """
        )
        self.progress_bar.setVisible(False)

        # Enhanced progress message
        self.progress_message = QLabel("Ready to synchronize data")
        self.progress_message.setFont(QFont("Segoe UI", 12, QFont.Medium))
        self.progress_message.setStyleSheet(
            """
            color: #e2e8f0; 
            background: transparent;
            padding: 8px 0px;
        """
        )
        self.progress_message.setAlignment(Qt.AlignLeft)

        content_layout.addWidget(self.progress_bar)
        content_layout.addWidget(self.progress_message)

        prog_layout.addLayout(content_layout)
        layout.addWidget(progress_frame)

    def create_control_section(self, layout):
        """Enhanced control panel with modern buttons"""
        control_frame = ModernFrame()

        ctrl_layout = QVBoxLayout(control_frame)
        ctrl_layout.setContentsMargins(25, 25, 25, 25)
        ctrl_layout.setSpacing(20)

        # Modern section header
        header = SectionHeader("Control Panel", "⚙️")
        ctrl_layout.addWidget(header)

        # Control content with responsive layout
        content_layout = QVBoxLayout()
        content_layout.setSpacing(18)

        # Main action buttons - responsive
        main_buttons_container = QWidget()
        main_buttons = QHBoxLayout(main_buttons_container)
        main_buttons.setSpacing(15)

        self.test_btn = QPushButton("🔍 Test Connections")
        self.test_btn.setStyleSheet(self.get_modern_primary_button_style())
        self.test_btn.setMinimumHeight(48)
        self.test_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.test_btn.clicked.connect(self.test_connections_requested.emit)

        self.sync_btn = QPushButton("🚀 Start Sync")
        self.sync_btn.setStyleSheet(self.get_modern_success_button_style())
        self.sync_btn.setMinimumHeight(48)
        self.sync_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.sync_btn.clicked.connect(self._toggle_sync)

        main_buttons.addWidget(self.test_btn)
        main_buttons.addWidget(self.sync_btn)

        # Secondary controls - responsive
        secondary_container = QWidget()
        secondary_layout = QHBoxLayout(secondary_container)
        secondary_layout.setSpacing(15)

        self.clear_btn = QPushButton("🧹 Clear Logs")
        self.clear_btn.setStyleSheet(self.get_modern_warning_button_style())
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.clear_btn.clicked.connect(self.clear_logs_requested.emit)

        # Enhanced auto sync checkbox
        self.auto_sync_check = QCheckBox("🔄 Auto Sync Every Hour")
        self.auto_sync_check.setStyleSheet(self.get_modern_checkbox_style())
        self.auto_sync_check.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.auto_sync_check.toggled.connect(self._toggle_auto_sync)

        secondary_layout.addWidget(self.clear_btn)
        secondary_layout.addWidget(self.auto_sync_check)

        content_layout.addWidget(main_buttons_container)
        content_layout.addWidget(secondary_container)

        ctrl_layout.addLayout(content_layout)
        layout.addWidget(control_frame)

    def create_logs_section(self, layout):
        """Enhanced logs section with modern console design"""
        logs_frame = ModernFrame()

        logs_layout = QVBoxLayout(logs_frame)
        logs_layout.setContentsMargins(25, 25, 25, 25)
        logs_layout.setSpacing(20)

        # Modern section header
        header = SectionHeader("System Logs", "📋")
        logs_layout.addWidget(header)

        # Enhanced log console
        self.log_console = QTextEdit()
        self.log_console.setStyleSheet(
            """
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f1419, 
                    stop:1 #1a1f2e);
                border: 2px solid rgba(0, 212, 255, 0.2);
                border-radius: 12px;
                color: #48bb78;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                padding: 16px;
                line-height: 1.4;
                selection-background-color: rgba(0, 212, 255, 0.3);
            }
            QScrollBar:vertical {
                background: rgba(26, 32, 44, 0.8);
                width: 10px;
                border-radius: 5px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 212, 255, 0.6);
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(0, 212, 255, 0.8);
            }
            QScrollBar::add-line:vertical, 
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """
        )
        self.log_console.setMinimumHeight(140)
        self.log_console.setMaximumHeight(200)
        self.log_console.setReadOnly(True)
        self.log_console.setPlaceholderText(
            "🔍 System logs and status messages will appear here..."
        )

        logs_layout.addWidget(self.log_console)
        layout.addWidget(logs_frame)

    def get_modern_primary_button_style(self):
        """Enhanced primary button with gradients and effects"""
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4299e1, 
                    stop:1 #3182ce);
                color: #ffffff;
                border: none;
                border-radius: 12px;
                padding: 14px 24px;
                font-weight: 600;
                font-size: 13px;
                font-family: 'Segoe UI';
                text-shadow: 0px 1px 2px rgba(0,0,0,0.2);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #63b3ed, 
                    stop:1 #4299e1);
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2b77a8, 
                    stop:1 #2c5aa0);
                transform: translateY(0px);
            }
        """

    def get_modern_success_button_style(self):
        """Enhanced success button with gradients"""
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #48bb78, 
                    stop:1 #38a169);
                color: #ffffff;
                border: none;
                border-radius: 12px;
                padding: 14px 24px;
                font-weight: 600;
                font-size: 13px;
                font-family: 'Segoe UI';
                text-shadow: 0px 1px 2px rgba(0,0,0,0.2);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #68d391, 
                    stop:1 #48bb78);
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2f855a, 
                    stop:1 #276749);
                transform: translateY(0px);
            }
        """

    def get_modern_warning_button_style(self):
        """Enhanced warning button with gradients"""
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ed8936, 
                    stop:1 #dd6b20);
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 12px;
                font-family: 'Segoe UI';
                text-shadow: 0px 1px 2px rgba(0,0,0,0.2);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f6ad55, 
                    stop:1 #ed8936);
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c05621, 
                    stop:1 #9c4221);
                transform: translateY(0px);
            }
        """

    def get_modern_checkbox_style(self):
        """Enhanced checkbox with modern styling"""
        return """
            QCheckBox {
                color: #e2e8f0;
                font-size: 13px;
                font-family: 'Segoe UI';
                font-weight: 500;
                spacing: 12px;
                background: transparent;
                padding: 12px 16px;
                border-radius: 8px;
            }
            QCheckBox:hover {
                background: rgba(0, 212, 255, 0.1);
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
            }
            QCheckBox::indicator:unchecked {
                background: rgba(26, 32, 44, 0.8);
                border: 2px solid rgba(74, 85, 104, 0.8);
            }
            QCheckBox::indicator:unchecked:hover {
                background: rgba(45, 55, 72, 0.9);
                border: 2px solid rgba(0, 212, 255, 0.5);
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #48bb78, 
                    stop:1 #38a169);
                border: 2px solid #48bb78;
            }
            QCheckBox::indicator:checked:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #68d391, 
                    stop:1 #48bb78);
            }
        """

    # Event handlers
    def _toggle_sync(self):
        if self.controller.get_sync_status()["is_running"]:
            self.stop_sync_requested.emit()
        else:
            self.start_sync_requested.emit()

    def _toggle_auto_sync(self, checked):
        self.auto_sync_toggled.emit(checked, 3600)

    # Public update methods
    @pyqtSlot(str, str)
    def update_connection_status(self, service, status):
        if service == "SharePoint":
            self.sp_status.update_status(status)
        elif service == "Database":
            self.db_status.update_status(status)

    @pyqtSlot(str, int, str)
    def update_progress(self, message, progress, level):
        self.progress_message.setText(f"📍 {message}")

        if progress > 0:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(progress)
        else:
            self.progress_bar.setVisible(False)

    @pyqtSlot(bool, str, dict)
    def on_sync_completed(self, success, message, stats):
        self.progress_bar.setVisible(False)

        if success:
            self.sync_btn.setText("🚀 Start Sync")
            self.sync_btn.setStyleSheet(self.get_modern_success_button_style())
            self.sync_status.update_status("success", "Completed")
            self.progress_message.setText("✅ Sync completed successfully")
        else:
            self.sync_btn.setText("🚀 Start Sync")
            self.sync_btn.setStyleSheet(self.get_modern_success_button_style())
            self.sync_status.update_status("error", "Failed")
            self.progress_message.setText("❌ Sync failed - Check logs for details")

    def add_log_message(self, message, level):
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")

        # Enhanced color scheme with better contrast
        colors = {
            "info": "#64b5f6",  # Light blue
            "success": "#81c784",  # Light green
            "warning": "#ffb74d",  # Light orange
            "error": "#e57373",  # Light red
            "debug": "#ba68c8",  # Light purple
        }

        # Enhanced formatting with better typography
        color = colors.get(level, "#ffffff")
        level_icon = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "debug": "🔧",
        }.get(level, "📝")

        formatted = f"""
        <div style="margin: 4px 0; padding: 6px 0; border-left: 3px solid {color}; padding-left: 12px;">
            <span style="color: #718096; font-size: 10px;">[{timestamp}]</span>
            <span style="color: {color}; font-weight: 500; margin-left: 8px;">{level_icon} {message}</span>
        </div>
        """

        self.log_console.append(formatted)

        # Auto scroll to bottom
        cursor = self.log_console.textCursor()
        cursor.movePosition(cursor.End)
        self.log_console.setTextCursor(cursor)

    def clear_logs(self):
        self.log_console.clear()
        self.add_log_message("Logs cleared", "info")

    def set_auto_sync_enabled(self, enabled):
        self.auto_sync_check.setChecked(enabled)

    def resizeEvent(self, event):
        """Handle responsive behavior on window resize"""
        super().resizeEvent(event)

        # Adjust margins based on window size
        width = self.width()
        if width < 800:
            # Mobile/small screen
            margins = (15, 15, 15, 15)
            spacing = 15
        elif width < 1200:
            # Tablet/medium screen
            margins = (25, 25, 25, 25)
            spacing = 20
        else:
            # Desktop/large screen
            margins = (30, 30, 30, 30)
            spacing = 25

        # Update layout margins
        if hasattr(self, "content_layout"):
            self.content_layout.setContentsMargins(*margins)
            self.content_layout.setSpacing(spacing)
