# ui/main_window.py - Fixed Modern 2025 Main Window
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import logging
import sys
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from ui.styles.theme import ModernColors, Typography, BorderRadius
    from ui.components.dashboard import create_modern_dashboard
    from ui.components.config_panel import create_config_panel
    from ui.components.connection_form import create_connection_setup_widget
    from ui.widgets.cyber_log_console import LogConsoleWithControls
    from ui.widgets.modern_button import ActionButton
except ImportError as e:
    print(f"Import error in main_window: {e}")

    # Fallback minimal colors
    class ModernColors:
        SURFACE_PRIMARY = "#0F172A"
        SURFACE_SECONDARY = "#1E293B"
        TEXT_PRIMARY = "#F8FAFC"
        PRIMARY = "#6366F1"
        GLASS_BORDER = "rgba(255, 255, 255, 0.1)"

    class Typography:
        PRIMARY_FONT = "Inter"
        TEXT_2XL = 20
        TEXT_BASE = 14
        WEIGHT_BOLD = 700


logger = logging.getLogger(__name__)


class ModernTabWidget(QTabWidget):
    """Enhanced tab widget with modern styling"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_styling()
        self.setMovable(True)
        self.setTabsClosable(False)

    def _setup_styling(self):
        """Apply tab styling without unsupported properties"""
        self.setStyleSheet(
            f"""
            QTabWidget::pane {{
                background: {ModernColors.SURFACE_SECONDARY};
                border: 1px solid {ModernColors.GLASS_BORDER};
                border-radius: 8px;
                margin-top: -1px;
            }}
            QTabBar::tab {{
                background: rgba(51, 65, 85, 0.5);
                border: 1px solid {ModernColors.GLASS_BORDER};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 12px 20px;
                margin-right: 2px;
                color: #CBD5E1;
                font-weight: 500;
                min-width: 100px;
                font-size: 14px;
            }}
            QTabBar::tab:selected {{
                background: {ModernColors.PRIMARY};
                color: white;
                border-color: {ModernColors.PRIMARY};
                font-weight: 600;
            }}
            QTabBar::tab:hover:!selected {{
                background: rgba(99, 102, 241, 0.3);
                color: {ModernColors.TEXT_PRIMARY};
            }}
        """
        )


class OptimizedMainWindow(QMainWindow):
    """Fixed 2025 Main Window with proper error handling and cleanup"""

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.cleanup_done = False
        self.dashboard = None
        self.config_panel = None
        self.log_console = None

        # Initialize window safely
        self._safe_init()

    def _safe_init(self):
        """Safe initialization with error handling"""
        try:
            self._setup_window()
            self._setup_ui()
            self._connect_signals()
            logger.info("Modern MainWindow initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing MainWindow: {e}", exc_info=True)
            self._create_fallback_ui()

    def _setup_window(self):
        """Setup window properties"""
        self.setWindowTitle("DENSO Neural Matrix - SharePoint ↔ SQL Sync")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # Center on screen
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

        # Apply global styling
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background: {ModernColors.SURFACE_PRIMARY};
                color: {ModernColors.TEXT_PRIMARY};
            }}
        """
        )

    def _setup_ui(self):
        """Setup modern UI with proper error handling"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = self._create_header()
        main_layout.addWidget(header)

        # Main content with tabs
        self.tab_widget = ModernTabWidget()

        try:
            # Dashboard tab
            self.dashboard = create_modern_dashboard(self.controller)
            self.tab_widget.addTab(self.dashboard, "📊 Dashboard")

            # Connection Setup tab (แยกออกจาก Config)
            self.connection_setup = create_connection_setup_widget()
            self.tab_widget.addTab(self.connection_setup, "🔗 Connections")

            # Config tab (สำหรับ sync settings)
            self.config_panel = create_config_panel(self.controller)
            self.tab_widget.addTab(self.config_panel, "⚙️ Sync Settings")

            # Logs tab
            logs_widget = self._create_logs_tab()
            self.tab_widget.addTab(logs_widget, "📝 Logs")

        except Exception as e:
            logger.error(f"Error creating tabs: {e}")
            self._create_simple_tabs()

        main_layout.addWidget(self.tab_widget)

        # Status bar
        self._setup_status_bar()

    def _create_header(self):
        """Create modern header bar"""
        header = QWidget()
        header.setFixedHeight(70)
        header.setStyleSheet(
            f"""
            QWidget {{
                background: {ModernColors.SURFACE_SECONDARY};
                border-bottom: 1px solid {ModernColors.GLASS_BORDER};
            }}
        """
        )

        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 16, 24, 16)

        # Branding
        brand_layout = QHBoxLayout()

        logo = QLabel("🚀")
        logo.setStyleSheet(f"font-size: 24px; color: {ModernColors.PRIMARY};")
        brand_layout.addWidget(logo)

        title = QLabel("DENSO Neural Matrix")
        title.setStyleSheet(
            f"""
            font-size: {Typography.TEXT_2XL}px;
            font-weight: {Typography.WEIGHT_BOLD};
            color: {ModernColors.TEXT_PRIMARY};
            font-family: "{Typography.PRIMARY_FONT}";
        """
        )
        brand_layout.addWidget(title)

        subtitle = QLabel("SharePoint ↔ SQL Sync System")
        subtitle.setStyleSheet(
            f"""
            font-size: {Typography.TEXT_BASE}px;
            color: {ModernColors.TEXT_SECONDARY};
            margin-left: 8px;
        """
        )
        brand_layout.addWidget(subtitle)

        layout.addLayout(brand_layout)
        layout.addStretch()

        # Connection status
        self.connection_status = QLabel("●")
        self.connection_status.setStyleSheet(
            f"""
            font-size: 16px;
            color: {ModernColors.ERROR};
        """
        )
        self.connection_status.setToolTip("Connection Status")
        layout.addWidget(self.connection_status)

        return header

    def _create_logs_tab(self):
        """Create logs tab with console"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Log controls
        controls_layout = QHBoxLayout()

        clear_btn = ActionButton.ghost("🗑 Clear", size="sm")
        export_btn = ActionButton.secondary("💾 Export", size="sm")

        controls_layout.addWidget(clear_btn)
        controls_layout.addWidget(export_btn)
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        # Log console
        self.log_console = LogConsoleWithControls()
        layout.addWidget(self.log_console)

        # Connect clear button
        clear_btn.clicked.connect(self.log_console.console.clear)
        export_btn.clicked.connect(self._export_logs)

        return widget

    def _create_simple_tabs(self):
        """Fallback simple tabs if main creation fails"""
        # Simple dashboard
        dashboard_widget = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_widget)
        dashboard_layout.addWidget(QLabel("Dashboard - Simplified Mode"))

        # Simple connection form
        connection_widget = QWidget()
        connection_layout = QVBoxLayout(connection_widget)
        connection_layout.addWidget(QLabel("Connection Setup - Simplified Mode"))

        # Simple config
        config_widget = QWidget()
        config_layout = QVBoxLayout(config_widget)
        config_layout.addWidget(QLabel("Sync Settings - Simplified Mode"))

        self.tab_widget.addTab(dashboard_widget, "📊 Dashboard")
        self.tab_widget.addTab(connection_widget, "🔗 Connections")
        self.tab_widget.addTab(config_widget, "⚙️ Sync")

    def _create_fallback_ui(self):
        """Create minimal fallback UI if main UI fails"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Header
        header = QLabel("🚀 DENSO Neural Matrix - Safe Mode")
        header.setStyleSheet(
            f"""
            font-size: 18px;
            font-weight: bold;
            color: {ModernColors.PRIMARY};
            padding: 16px;
            text-align: center;
        """
        )
        layout.addWidget(header)

        # Message
        message = QLabel("Running in safe mode. Some features may be limited.")
        message.setStyleSheet(
            f"color: {ModernColors.TEXT_SECONDARY}; text-align: center;"
        )
        layout.addWidget(message)

        # Basic controls
        controls = QHBoxLayout()

        test_btn = QPushButton("Test Connections")
        test_btn.clicked.connect(self._test_connections)
        controls.addWidget(test_btn)

        sync_btn = QPushButton("Run Sync")
        sync_btn.clicked.connect(self._run_sync)
        controls.addWidget(sync_btn)

        layout.addLayout(controls)
        layout.addStretch()

    def _setup_status_bar(self):
        """Setup status bar"""
        status_bar = self.statusBar()
        status_bar.setStyleSheet(
            f"""
            QStatusBar {{
                background: {ModernColors.SURFACE_SECONDARY};
                border-top: 1px solid {ModernColors.GLASS_BORDER};
                color: {ModernColors.TEXT_SECONDARY};
                font-size: 12px;
            }}
        """
        )

        self.status_label = QLabel("Ready")
        status_bar.addWidget(self.status_label)

        self.sync_label = QLabel("Idle")
        status_bar.addPermanentWidget(self.sync_label)

    def _connect_signals(self):
        """Connect controller signals with error handling"""
        if not self.controller:
            return

        try:
            # Connect available signals
            signal_connections = [
                ("log_message", self._handle_log_message),
                ("sharepoint_status_update", self._update_sharepoint_status),
                ("database_status_update", self._update_database_status),
                ("progress_updated", self._handle_progress),
                ("current_task_update", self._update_current_task),
                ("sync_completed", self._handle_sync_completed),
            ]

            for signal_name, handler in signal_connections:
                if hasattr(self.controller, signal_name):
                    signal = getattr(self.controller, signal_name)
                    signal.connect(handler)
                    logger.debug(f"Connected signal: {signal_name}")

            # Connect dashboard signals if available
            if self.dashboard:
                if hasattr(self.dashboard, "sync_requested"):
                    self.dashboard.sync_requested.connect(self._run_sync)
                if hasattr(self.dashboard, "test_connections_requested"):
                    self.dashboard.test_connections_requested.connect(
                        self._test_connections
                    )
                if hasattr(self.dashboard, "import_excel_requested"):
                    self.dashboard.import_excel_requested.connect(self._import_excel)
                if hasattr(self.dashboard, "clear_cache_requested"):
                    self.dashboard.clear_cache_requested.connect(self._clear_cache)

        except Exception as e:
            logger.error(f"Error connecting signals: {e}")

    # Signal handlers
    @pyqtSlot(str, str)
    def _handle_log_message(self, message: str, level: str):
        """Handle log messages"""
        try:
            if self.log_console and hasattr(self.log_console, "console"):
                self.log_console.console.add_log_message(message, level)
        except Exception as e:
            logger.debug(f"Error handling log message: {e}")

    @pyqtSlot(str)
    def _update_sharepoint_status(self, status: str):
        """Update SharePoint status"""
        try:
            if self.dashboard and hasattr(self.dashboard, "update_sharepoint_status"):
                self.dashboard.update_sharepoint_status(status)

            # Update header connection status
            connected = status == "connected"
            color = ModernColors.SUCCESS if connected else ModernColors.ERROR
            self.connection_status.setStyleSheet(f"font-size: 16px; color: {color};")

        except Exception as e:
            logger.debug(f"Error updating SharePoint status: {e}")

    @pyqtSlot(str)
    def _update_database_status(self, status: str):
        """Update database status"""
        try:
            if self.dashboard and hasattr(self.dashboard, "update_database_status"):
                self.dashboard.update_database_status(status)
        except Exception as e:
            logger.debug(f"Error updating database status: {e}")

    @pyqtSlot(str, int, str)
    def _handle_progress(self, task: str, percent: int, message: str):
        """Handle progress updates"""
        try:
            if self.dashboard and hasattr(self.dashboard, "update_progress"):
                self.dashboard.update_progress(task, percent, message)
        except Exception as e:
            logger.debug(f"Error handling progress: {e}")

    @pyqtSlot(str)
    def _update_current_task(self, task: str):
        """Update current task"""
        try:
            self.sync_label.setText(task)
            if self.dashboard and hasattr(self.dashboard, "update_current_task"):
                self.dashboard.update_current_task(task)
        except Exception as e:
            logger.debug(f"Error updating current task: {e}")

    @pyqtSlot(bool, str, dict)
    def _handle_sync_completed(self, success: bool, message: str, stats: dict):
        """Handle sync completion"""
        try:
            status = "success" if success else "failed"
            if self.dashboard and hasattr(self.dashboard, "update_sync_status"):
                self.dashboard.update_sync_status(status)
        except Exception as e:
            logger.debug(f"Error handling sync completion: {e}")

    # Action handlers
    def _test_connections(self):
        """Test all connections"""
        try:
            if self.controller and hasattr(self.controller, "test_all_connections"):
                self.controller.test_all_connections()
        except Exception as e:
            logger.error(f"Error testing connections: {e}")

    def _run_sync(self):
        """Run synchronization"""
        try:
            if self.controller and hasattr(self.controller, "run_full_sync"):
                self.controller.run_full_sync("spo_to_sql")
        except Exception as e:
            logger.error(f"Error running sync: {e}")

    def _import_excel(self):
        """Import Excel file"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)"
            )
            if (
                file_path
                and self.controller
                and hasattr(self.controller, "import_excel_data")
            ):
                self.controller.import_excel_data(file_path, "imported_data", {})
        except Exception as e:
            logger.error(f"Error importing Excel: {e}")

    def _clear_cache(self):
        """Clear system cache"""
        try:
            if self.controller and hasattr(self.controller, "run_cache_cleanup"):
                self.controller.run_cache_cleanup()
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

    def _export_logs(self):
        """Export logs to file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Logs", "denso_logs.txt", "Text Files (*.txt)"
            )
            if file_path and self.log_console:
                success = self.log_console.console.export_logs(file_path)
                if success:
                    self.status_label.setText(f"Logs exported to: {file_path}")
        except Exception as e:
            logger.error(f"Error exporting logs: {e}")

    def closeEvent(self, event):
        """Handle window close with confirmation"""
        reply = QMessageBox.question(
            self,
            "Exit Application",
            "Are you sure you want to exit DENSO Neural Matrix?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.cleanup()
            event.accept()
        else:
            event.ignore()

    def cleanup(self):
        """Comprehensive cleanup with error handling"""
        if self.cleanup_done:
            return

        logger.info("Starting MainWindow cleanup")

        try:
            # Cleanup dashboard
            if self.dashboard and hasattr(self.dashboard, "cleanup"):
                self.dashboard.cleanup()

            # Cleanup config panel
            if self.config_panel and hasattr(self.config_panel, "cleanup"):
                self.config_panel.cleanup()

            # Cleanup log console
            if self.log_console:
                self.log_console.console.clear()

            # Cleanup controller
            if self.controller and hasattr(self.controller, "cleanup"):
                self.controller.cleanup()

            self.cleanup_done = True
            logger.info("MainWindow cleanup completed")

        except Exception as e:
            logger.error(f"Error during MainWindow cleanup: {e}")


# Backward compatibility
MainWindow = OptimizedMainWindow
