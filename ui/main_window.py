from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import logging

logger = logging.getLogger(__name__)


class OptimizedMainWindow(QMainWindow):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("DENSO Neural Matrix")
        self.setGeometry(100, 100, 1000, 700)
        self._setup_ui()
        self._connect_signals()
        logger.info("OptimizedMainWindow initialized")

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Header
        header = QLabel("🚀 DENSO Neural Matrix - SharePoint ↔ SQL Sync")
        header.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #00D4FF; padding: 10px;"
        )
        layout.addWidget(header)

        # Tabs
        self.tabs = QTabWidget()

        # Dashboard
        dash = QWidget()
        dash_layout = QVBoxLayout(dash)

        # Status
        status_widget = QWidget()
        status_layout = QGridLayout(status_widget)

        status_layout.addWidget(QLabel("SharePoint:"), 0, 0)
        self.sp_status = QLabel("🔴 Disconnected")
        status_layout.addWidget(self.sp_status, 0, 1)

        status_layout.addWidget(QLabel("Database:"), 0, 2)
        self.db_status = QLabel("🔴 Disconnected")
        status_layout.addWidget(self.db_status, 0, 3)

        dash_layout.addWidget(status_widget)

        # Progress
        self.current_task = QLabel("Idle")
        self.current_task.setStyleSheet("color: #00F5A0; font-weight: bold;")
        dash_layout.addWidget(self.current_task)

        self.progress_bar = QProgressBar()
        dash_layout.addWidget(self.progress_bar)

        # Buttons
        btn_layout = QHBoxLayout()

        test_btn = QPushButton("🌐 Test Connections")
        test_btn.clicked.connect(self._test_connections)
        btn_layout.addWidget(test_btn)

        sync_btn = QPushButton("🚀 Run Sync")
        sync_btn.clicked.connect(self._run_sync)
        btn_layout.addWidget(sync_btn)

        excel_btn = QPushButton("📊 Import Excel")
        excel_btn.clicked.connect(self._import_excel)
        btn_layout.addWidget(excel_btn)

        dash_layout.addLayout(btn_layout)
        dash_layout.addStretch()

        self.tabs.addTab(dash, "📊 Dashboard")

        # Logs
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet(
            """
            QTextEdit {
                background-color: #0a0a0a;
                color: #E0E0E0;
                font-family: Consolas;
                font-size: 9px;
            }
        """
        )
        log_layout.addWidget(self.log_display)

        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.clicked.connect(self.log_display.clear)
        log_layout.addWidget(clear_btn)

        self.tabs.addTab(log_widget, "📝 Logs")

        layout.addWidget(self.tabs)

    def _connect_signals(self):
        try:
            if hasattr(self.controller, "log_message"):
                self.controller.log_message.connect(self._add_log)
            if hasattr(self.controller, "sharepoint_status_update"):
                self.controller.sharepoint_status_update.connect(self._update_sp_status)
            if hasattr(self.controller, "database_status_update"):
                self.controller.database_status_update.connect(self._update_db_status)
            if hasattr(self.controller, "progress_updated"):
                self.controller.progress_updated.connect(self._update_progress)
            if hasattr(self.controller, "current_task_update"):
                self.controller.current_task_update.connect(self._update_task)
        except Exception as e:
            logger.error(f"Signal connection error: {e}")

    @pyqtSlot(str, str)
    def _add_log(self, message, level):
        colors = {"info": "#00F5A0", "warning": "#FFD700", "error": "#FF6347"}
        color = colors.get(level, "#E0E0E0")
        self.log_display.append(
            f'<span style="color: {color};">[{level.upper()}] {message}</span>'
        )

    @pyqtSlot(str)
    def _update_sp_status(self, status):
        colors = {"connected": "#00FF7F", "error": "#FF6347", "disconnected": "#FFD700"}
        icons = {"connected": "🟢", "error": "🔴", "disconnected": "🟡"}
        self.sp_status.setText(f"{icons.get(status, '🔴')} {status.title()}")
        self.sp_status.setStyleSheet(f"color: {colors.get(status, '#FF6347')};")

    @pyqtSlot(str)
    def _update_db_status(self, status):
        colors = {"connected": "#00FF7F", "error": "#FF6347", "disconnected": "#FFD700"}
        icons = {"connected": "🟢", "error": "🔴", "disconnected": "🟡"}
        self.db_status.setText(f"{icons.get(status, '🔴')} {status.title()}")
        self.db_status.setStyleSheet(f"color: {colors.get(status, '#FF6347')};")

    @pyqtSlot(str, int, str)
    def _update_progress(self, task, percent, message):
        self.progress_bar.setValue(percent)
        self.current_task.setText(f"{task}: {message}")

    @pyqtSlot(str)
    def _update_task(self, task):
        self.current_task.setText(task)

    def _test_connections(self):
        if hasattr(self.controller, "test_all_connections"):
            self.controller.test_all_connections()

    def _run_sync(self):
        if hasattr(self.controller, "run_full_sync"):
            self.controller.run_full_sync("spo_to_sql")

    def _import_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Excel File", "", "Excel (*.xlsx *.xls)"
        )
        if file_path and hasattr(self.controller, "import_excel_data"):
            self.controller.import_excel_data(file_path, "imported_data", {})

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Exit",
            "Exit application?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def cleanup(self):
        logger.info("Cleaning up OptimizedMainWindow")


# Compatibility
MainWindow = OptimizedMainWindow
