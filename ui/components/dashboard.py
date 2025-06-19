from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QCheckBox,
    QTextEdit,
    QProgressBar,
    QGridLayout,
)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QTimer
from PyQt5.QtGui import QFont
from ..widgets.status_card import StatusCard
from ..styles.theme import (
    get_card_style,
    get_header_card_style,
    get_gradient_button_style,
    get_textedit_style,
)
import logging

logger = logging.getLogger(__name__)


class Dashboard(QWidget):
    """Dashboard component สำหรับแสดงสถานะและควบคุมการซิงค์"""

    # Signals สำหรับการสื่อสารกับ Controller
    test_connections_requested = pyqtSignal()
    start_sync_requested = pyqtSignal()
    stop_sync_requested = pyqtSignal()
    clear_logs_requested = pyqtSignal()
    auto_sync_toggled = pyqtSignal(bool, int)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()
        self.setup_auto_refresh()

    def setup_ui(self):
        """ตั้งค่า UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header Card
        self.create_header_card(layout)

        # Connection Status Cards
        self.create_connection_status(layout)

        # Progress Tracking
        self.create_progress_section(layout)

        # Control Panel
        self.create_control_panel(layout)

        # Log Console
        self.create_log_console(layout)

        layout.addStretch()

    def create_header_card(self, layout):
        """สร้าง Header Card พร้อมโลโก้"""
        self.header_card = QFrame()
        self.header_card.setStyleSheet(get_header_card_style())
        self.header_card.setFixedHeight(100)

        header_layout = QVBoxLayout(self.header_card)

        # Title
        title_label = QLabel("SharePoint to SQL")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))

        # Subtitle
        subtitle_label = QLabel("by เฮียตอม😎")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Segoe UI", 12))
        subtitle_label.setStyleSheet("color: rgba(255,255,255,0.8);")

        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)

        layout.addWidget(self.header_card)

    def create_connection_status(self, layout):
        """สร้าง Connection Status Cards"""
        status_frame = QFrame()
        status_frame.setStyleSheet(get_card_style())
        status_layout = QGridLayout(status_frame)

        # SharePoint Status
        self.sp_status_card = StatusCard("SharePoint", "disconnected")
        status_layout.addWidget(self.sp_status_card, 0, 0)

        # Database Status
        self.db_status_card = StatusCard("Database", "disconnected")
        status_layout.addWidget(self.db_status_card, 0, 1)

        # Last Sync Status
        self.sync_status_card = StatusCard("Last Sync", "never")
        status_layout.addWidget(self.sync_status_card, 1, 0, 1, 2)

        layout.addWidget(status_frame)

    def create_progress_section(self, layout):
        """สร้าง Progress Tracking Section"""
        progress_frame = QFrame()
        progress_frame.setStyleSheet(get_card_style())
        progress_layout = QVBoxLayout(progress_frame)

        # Progress Title
        progress_title = QLabel("Progress Tracking")
        progress_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        progress_layout.addWidget(progress_title)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        # Progress Message
        self.progress_message = QLabel("Ready")
        self.progress_message.setStyleSheet("color: rgba(255,255,255,0.8);")
        progress_layout.addWidget(self.progress_message)

        layout.addWidget(progress_frame)

    def create_control_panel(self, layout):
        """สร้าง Control Panel"""
        control_frame = QFrame()
        control_frame.setStyleSheet(get_card_style())
        control_layout = QVBoxLayout(control_frame)

        # Control Title
        control_title = QLabel("Control Panel")
        control_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        control_layout.addWidget(control_title)

        # Button Layout
        button_layout = QGridLayout()

        # Test Connections Button
        self.test_btn = QPushButton("🔍 ทดสอบการเชื่อมต่อ")
        self.test_btn.setStyleSheet(get_gradient_button_style("#2196F3", "#1976D2"))
        self.test_btn.clicked.connect(self.test_connections_requested.emit)
        button_layout.addWidget(self.test_btn, 0, 0)

        # Start Sync Button
        self.sync_btn = QPushButton("🚀 เริ่มซิงค์")
        self.sync_btn.setStyleSheet(get_gradient_button_style("#4CAF50", "#388E3C"))
        self.sync_btn.clicked.connect(self._toggle_sync)
        button_layout.addWidget(self.sync_btn, 0, 1)

        # Clear Logs Button
        self.clear_btn = QPushButton("🧹 ล้างล็อก")
        self.clear_btn.setStyleSheet(
            get_gradient_button_style("#FF9800", "#F57C00", "small")
        )
        self.clear_btn.clicked.connect(self.clear_logs_requested.emit)
        button_layout.addWidget(self.clear_btn, 1, 0)

        # Auto Sync Toggle
        self.auto_sync_checkbox = QCheckBox("🔄 ซิงค์อัตโนมัติ")
        self.auto_sync_checkbox.toggled.connect(self._toggle_auto_sync)
        button_layout.addWidget(self.auto_sync_checkbox, 1, 1)

        control_layout.addLayout(button_layout)
        layout.addWidget(control_frame)

    def create_log_console(self, layout):
        """สร้าง Log Console"""
        log_frame = QFrame()
        log_frame.setStyleSheet(get_card_style())
        log_layout = QVBoxLayout(log_frame)

        # Log Title
        log_title = QLabel("System Logs")
        log_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        log_layout.addWidget(log_title)

        # Log Console
        self.log_console = QTextEdit()
        self.log_console.setStyleSheet(get_textedit_style())
        self.log_console.setMaximumHeight(200)
        self.log_console.setReadOnly(True)
        log_layout.addWidget(self.log_console)

        layout.addWidget(log_frame)

    def setup_auto_refresh(self):
        """ตั้งค่า Auto Refresh Timer"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_status)
        self.refresh_timer.start(5000)  # Refresh ทุก 5 วินาที

    # Slot Methods
    @pyqtSlot(str, str)
    def update_connection_status(self, service, status):
        """อัพเดทสถานะการเชื่อมต่อ"""
        if service == "SharePoint":
            self.sp_status_card.update_status(status)
        elif service == "Database":
            self.db_status_card.update_status(status)

    @pyqtSlot(str, int, str)
    def update_progress(self, message, progress, level):
        """อัพเดทความคืบหนา"""
        self.progress_message.setText(message)

        if progress > 0:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(progress)
        else:
            self.progress_bar.setVisible(False)

        # Update progress bar color based on level
        if level == "error":
            self.progress_bar.setStyleSheet(
                "QProgressBar::chunk { background: #f44336; }"
            )
        elif level == "warning":
            self.progress_bar.setStyleSheet(
                "QProgressBar::chunk { background: #ff9800; }"
            )
        else:
            self.progress_bar.setStyleSheet(
                "QProgressBar::chunk { background: #4caf50; }"
            )

    @pyqtSlot(bool, str, dict)
    def on_sync_completed(self, success, message, stats):
        """จัดการเมื่อซิงค์เสร็จสิ้น"""
        self.progress_bar.setVisible(False)
        self.progress_message.setText("Ready")

        # Update sync button
        self.sync_btn.setText("🚀 เริ่มซิงค์")
        self.sync_btn.setEnabled(True)

        # Update last sync status
        if success and stats:
            records = stats.get("records_inserted", 0)
            duration = stats.get("duration", 0)
            sync_text = f"Success: {records} records in {duration:.1f}s"
            self.sync_status_card.update_status("success", sync_text)
        else:
            self.sync_status_card.update_status("error", "Failed")

    def add_log_message(self, message, level):
        """เพิ่มข้อความลง Log Console"""
        # Add timestamp
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")

        # Color coding based on level
        color_map = {
            "info": "#00ff88",
            "warning": "#ffaa00",
            "error": "#ff4444",
            "success": "#00d4ff",
        }

        color = color_map.get(level, "#ffffff")
        formatted_message = (
            f'<span style="color: {color}">[{timestamp}] {message}</span>'
        )

        self.log_console.append(formatted_message)

        # Auto scroll to bottom
        cursor = self.log_console.textCursor()
        cursor.movePosition(cursor.End)
        self.log_console.setTextCursor(cursor)

    def clear_logs(self):
        """ล้าง Log Console"""
        self.log_console.clear()

    def set_auto_sync_enabled(self, enabled):
        """ตั้งค่า Auto Sync Checkbox"""
        self.auto_sync_checkbox.setChecked(enabled)

    # Private Methods
    def _toggle_sync(self):
        """Toggle การซิงค์"""
        if self.controller.get_sync_status()["is_running"]:
            self.stop_sync_requested.emit()
            self.sync_btn.setText("🚀 เริ่มซิงค์")
        else:
            self.start_sync_requested.emit()
            self.sync_btn.setText("⏹️ หยุดซิงค์")

    def _toggle_auto_sync(self, checked):
        """Toggle Auto Sync"""
        interval = 3600  # 1 hour default
        self.auto_sync_toggled.emit(checked, interval)

    def _refresh_status(self):
        """Refresh สถานะต่างๆ"""
        try:
            # Update sync button state
            sync_status = self.controller.get_sync_status()
            if sync_status["is_running"]:
                self.sync_btn.setText("⏹️ หยุดซิงค์")
                self.sync_btn.setStyleSheet(
                    get_gradient_button_style("#f44336", "#d32f2f")
                )
            else:
                self.sync_btn.setText("🚀 เริ่มซิงค์")
                self.sync_btn.setStyleSheet(
                    get_gradient_button_style("#4CAF50", "#388E3C")
                )

        except Exception as e:
            logger.warning(f"Failed to refresh dashboard status: {str(e)}")
