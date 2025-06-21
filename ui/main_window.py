# ui/main_window.py - Modern 2025 Design
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
    from ui.styles.theme import (
        ModernColors,
        Typography,
        Spacing,
        BorderRadius,
        get_button_style,
        get_input_style,
        get_card_style,
        get_progress_style,
        get_tab_style,
    )
except ImportError as e:
    print(f"Theme import error: {e}")

    # Fallback minimal styling
    class ModernColors:
        SURFACE_PRIMARY = "#0F172A"
        TEXT_PRIMARY = "#F8FAFC"
        PRIMARY = "#6366F1"


logger = logging.getLogger(__name__)


class ModernHeaderBar(QWidget):
    """Modern application header with branding and controls"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(16)

        # App branding
        brand_layout = QHBoxLayout()

        # Logo/Icon (placeholder)
        logo_label = QLabel("🚀")
        logo_label.setStyleSheet(
            f"""
            font-size: 24px;
            color: {ModernColors.PRIMARY};
        """
        )
        brand_layout.addWidget(logo_label)

        # App title
        title_label = QLabel("DENSO Neural Matrix")
        title_label.setStyleSheet(
            f"""
            font-size: 20px;
            font-weight: 700;
            color: {ModernColors.TEXT_PRIMARY};
            font-family: "{Typography.PRIMARY_FONT}";
        """
        )
        brand_layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel("SharePoint ↔ SQL Sync")
        subtitle_label.setStyleSheet(
            f"""
            font-size: 14px;
            color: {ModernColors.TEXT_SECONDARY};
            margin-left: 8px;
        """
        )
        brand_layout.addWidget(subtitle_label)

        layout.addLayout(brand_layout)
        layout.addStretch()

        # Status indicators
        self.connection_status = QLabel("●")
        self.connection_status.setStyleSheet(
            f"""
            font-size: 16px;
            color: {ModernColors.ERROR};
        """
        )
        self.connection_status.setToolTip("Connection Status")
        layout.addWidget(self.connection_status)

        # Style the header
        self.setStyleSheet(
            f"""
            QWidget {{
                background: {ModernColors.SURFACE_SECONDARY};
                border-bottom: 1px solid {ModernColors.GLASS_BORDER};
            }}
        """
        )
        self.setFixedHeight(80)

    def update_connection_status(self, connected: bool):
        """Update connection status indicator"""
        color = ModernColors.SUCCESS if connected else ModernColors.ERROR
        self.connection_status.setStyleSheet(
            f"""
            font-size: 16px;
            color: {color};
        """
        )


class ModernStatusCard(QWidget):
    """Modern status card component"""

    def __init__(self, title: str, value: str = "—", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        # Title
        title_label = QLabel(self.title)
        title_label.setStyleSheet(
            f"""
            font-size: 12px;
            font-weight: 500;
            color: {ModernColors.TEXT_SECONDARY};
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """
        )
        layout.addWidget(title_label)

        # Value
        self.value_label = QLabel(self.value)
        self.value_label.setStyleSheet(
            f"""
            font-size: 18px;
            font-weight: 600;
            color: {ModernColors.TEXT_PRIMARY};
        """
        )
        layout.addWidget(self.value_label)

        # Card styling
        self.setStyleSheet(
            f"""
            QWidget {{
                background: {ModernColors.SURFACE_SECONDARY};
                border: 1px solid {ModernColors.GLASS_BORDER};
                border-radius: {BorderRadius.MD}px;
            }}
            QWidget:hover {{
                border-color: {ModernColors.PRIMARY};
                background: {ModernColors.SURFACE_TERTIARY};
            }}
        """
        )
        self.setMinimumHeight(80)

    def update_value(self, value: str, status: str = "neutral"):
        """Update card value with status color"""
        colors = {
            "success": ModernColors.SUCCESS,
            "error": ModernColors.ERROR,
            "warning": ModernColors.WARNING,
            "neutral": ModernColors.TEXT_PRIMARY,
        }

        color = colors.get(status, ModernColors.TEXT_PRIMARY)
        self.value_label.setText(value)
        self.value_label.setStyleSheet(
            f"""
            font-size: 18px;
            font-weight: 600;
            color: {color};
        """
        )


class ModernProgressSection(QWidget):
    """Modern progress display section"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Section title
        title = QLabel("Current Operation")
        title.setStyleSheet(
            f"""
            font-size: 16px;
            font-weight: 600;
            color: {ModernColors.TEXT_PRIMARY};
            margin-bottom: 8px;
        """
        )
        layout.addWidget(title)

        # Task description
        self.task_label = QLabel("Ready")
        self.task_label.setStyleSheet(
            f"""
            font-size: 14px;
            color: {ModernColors.TEXT_SECONDARY};
            margin-bottom: 12px;
        """
        )
        layout.addWidget(self.task_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(get_progress_style())
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        # Card styling
        self.setStyleSheet(
            f"""
            QWidget {{
                background: {ModernColors.SURFACE_SECONDARY};
                border: 1px solid {ModernColors.GLASS_BORDER};
                border-radius: {BorderRadius.MD}px;
            }}
        """
        )

    def update_progress(self, task: str, percent: int, message: str = ""):
        """Update progress display"""
        self.task_label.setText(f"{task}: {message}" if message else task)
        self.progress_bar.setValue(percent)


class ModernActionButton(QPushButton):
    """Modern action button with icon and text"""

    def __init__(
        self, text: str, icon: str = "", variant: str = "primary", parent=None
    ):
        super().__init__(parent)
        self.setText(f"{icon} {text}" if icon else text)
        self.setStyleSheet(get_button_style(variant, "md"))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(44)


class ModernDashboard(QWidget):
    """Modern dashboard with status cards and controls"""

    # Signals
    sync_requested = pyqtSignal()
    test_connections_requested = pyqtSignal()
    import_excel_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        # Status cards grid
        status_section = self._create_status_section()
        layout.addWidget(status_section)

        # Progress section
        self.progress_section = ModernProgressSection()
        layout.addWidget(self.progress_section)

        # Action buttons
        actions_section = self._create_actions_section()
        layout.addWidget(actions_section)

        layout.addStretch()

    def _create_status_section(self):
        """Create status cards section"""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setSpacing(16)

        # Section title
        title = QLabel("System Status")
        title.setStyleSheet(
            f"""
            font-size: 16px;
            font-weight: 600;
            color: {ModernColors.TEXT_PRIMARY};
        """
        )
        layout.addWidget(title)

        # Status cards grid
        cards_grid = QGridLayout()
        cards_grid.setSpacing(16)

        self.sp_status_card = ModernStatusCard("SharePoint", "Disconnected")
        self.db_status_card = ModernStatusCard("Database", "Disconnected")
        self.sync_status_card = ModernStatusCard("Last Sync", "Never")
        self.auto_sync_card = ModernStatusCard("Auto Sync", "Disabled")

        cards_grid.addWidget(self.sp_status_card, 0, 0)
        cards_grid.addWidget(self.db_status_card, 0, 1)
        cards_grid.addWidget(self.sync_status_card, 1, 0)
        cards_grid.addWidget(self.auto_sync_card, 1, 1)

        layout.addLayout(cards_grid)
        return section

    def _create_actions_section(self):
        """Create action buttons section"""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setSpacing(16)

        # Section title
        title = QLabel("Quick Actions")
        title.setStyleSheet(
            f"""
            font-size: 16px;
            font-weight: 600;
            color: {ModernColors.TEXT_PRIMARY};
        """
        )
        layout.addWidget(title)

        # Action buttons grid
        buttons_grid = QGridLayout()
        buttons_grid.setSpacing(12)

        # Primary actions
        sync_btn = ModernActionButton("Run Sync", "🚀", "primary")
        sync_btn.clicked.connect(self.sync_requested.emit)

        test_btn = ModernActionButton("Test Connections", "🔗", "secondary")
        test_btn.clicked.connect(self.test_connections_requested.emit)

        excel_btn = ModernActionButton("Import Excel", "📊", "accent")
        excel_btn.clicked.connect(self.import_excel_requested.emit)

        clean_btn = ModernActionButton("Clean Cache", "🧹", "ghost")

        buttons_grid.addWidget(sync_btn, 0, 0)
        buttons_grid.addWidget(test_btn, 0, 1)
        buttons_grid.addWidget(excel_btn, 1, 0)
        buttons_grid.addWidget(clean_btn, 1, 1)

        layout.addLayout(buttons_grid)
        return section

    def update_status_card(self, card_type: str, value: str, status: str = "neutral"):
        """Update specific status card"""
        cards = {
            "sharepoint": self.sp_status_card,
            "database": self.db_status_card,
            "sync": self.sync_status_card,
            "auto_sync": self.auto_sync_card,
        }

        if card_type in cards:
            cards[card_type].update_value(value, status)


class ModernLogConsole(QTextEdit):
    """Modern log console with syntax highlighting"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setReadOnly(True)
        self.setFont(QFont(Typography.MONO_FONT, Typography.TEXT_SM))

        self.setStyleSheet(
            f"""
            QTextEdit {{
                background: {ModernColors.SURFACE_PRIMARY};
                color: {ModernColors.TEXT_PRIMARY};
                border: 1px solid {ModernColors.GLASS_BORDER};
                border-radius: {BorderRadius.MD}px;
                padding: 16px;
                font-family: "{Typography.MONO_FONT}";
                font-size: {Typography.TEXT_SM}px;
                line-height: 1.6;
            }}
        """
        )

        # Add welcome message
        self.append_log("System initialized", "info")

    def append_log(self, message: str, level: str = "info"):
        """Append formatted log message"""
        colors = {
            "info": ModernColors.TEXT_PRIMARY,
            "success": ModernColors.SUCCESS,
            "warning": ModernColors.WARNING,
            "error": ModernColors.ERROR,
            "debug": ModernColors.TEXT_MUTED,
        }

        icons = {
            "info": "ℹ",
            "success": "✓",
            "warning": "⚠",
            "error": "✗",
            "debug": "◇",
        }

        color = colors.get(level, ModernColors.TEXT_PRIMARY)
        icon = icons.get(level, "●")

        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")

        self.append(
            f'<span style="color: {ModernColors.TEXT_MUTED};">[{timestamp}]</span> '
            f'<span style="color: {color};">{icon} {message}</span>'
        )


class ModernTabWidget(QTabWidget):
    """Modern tab widget with custom styling"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(get_tab_style())
        self.setMovable(True)
        self.setTabsClosable(False)


class OptimizedMainWindow(QMainWindow):
    """Modern 2025 Main Window with optimized performance"""

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.cleanup_done = False

        self._setup_window()
        self._setup_ui()
        self._connect_signals()

        logger.info("Modern MainWindow initialized")

    def _setup_window(self):
        """Setup window properties"""
        self.setWindowTitle("DENSO Neural Matrix")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # Center window on screen
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

        # Set window icon (if available)
        try:
            icon_path = project_root / "assets" / "icons" / "app.ico"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except Exception:
            pass

    def _setup_ui(self):
        """Setup modern UI layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header bar
        self.header_bar = ModernHeaderBar()
        main_layout.addWidget(self.header_bar)

        # Main content area
        content_area = self._create_content_area()
        main_layout.addWidget(content_area)

        # Status bar
        self._setup_status_bar()

        # Apply global styling
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background: {ModernColors.SURFACE_PRIMARY};
                color: {ModernColors.TEXT_PRIMARY};
            }}
        """
        )

    def _create_content_area(self):
        """Create main content area with tabs"""
        self.tab_widget = ModernTabWidget()

        # Dashboard tab
        self.dashboard = ModernDashboard()
        self.tab_widget.addTab(self.dashboard, "📊 Dashboard")

        # Configuration tab
        config_widget = self._create_config_tab()
        self.tab_widget.addTab(config_widget, "⚙️ Configuration")

        # Logs tab
        logs_widget = self._create_logs_tab()
        self.tab_widget.addTab(logs_widget, "📝 Logs")

        return self.tab_widget

    def _create_config_tab(self):
        """Create configuration tab content"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        # Configuration sections
        sections = [
            self._create_sharepoint_config(),
            self._create_database_config(),
            self._create_sync_config(),
        ]

        for section in sections:
            layout.addWidget(section)

        layout.addStretch()
        return widget

    def _create_sharepoint_config(self):
        """Create SharePoint configuration section"""
        group = QGroupBox("SharePoint Configuration")
        group.setStyleSheet(
            f"""
            QGroupBox {{
                font-size: 16px;
                font-weight: 600;
                color: {ModernColors.TEXT_PRIMARY};
                border: 1px solid {ModernColors.GLASS_BORDER};
                border-radius: {BorderRadius.MD}px;
                margin-top: 12px;
                padding-top: 16px;
                background: {ModernColors.SURFACE_SECONDARY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 8px 16px;
                background: {ModernColors.PRIMARY};
                border-radius: {BorderRadius.SM}px;
                color: {ModernColors.TEXT_PRIMARY};
            }}
        """
        )

        layout = QFormLayout(group)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 30, 20, 20)

        # SharePoint fields
        self.sp_site_input = QLineEdit()
        self.sp_site_input.setPlaceholderText(
            "https://company.sharepoint.com/sites/site"
        )
        self.sp_site_input.setStyleSheet(get_input_style())

        self.sp_list_input = QLineEdit()
        self.sp_list_input.setPlaceholderText("List name")
        self.sp_list_input.setStyleSheet(get_input_style())

        layout.addRow("Site URL:", self.sp_site_input)
        layout.addRow("List Name:", self.sp_list_input)

        return group

    def _create_database_config(self):
        """Create database configuration section"""
        group = QGroupBox("Database Configuration")
        group.setStyleSheet(
            f"""
            QGroupBox {{
                font-size: 16px;
                font-weight: 600;
                color: {ModernColors.TEXT_PRIMARY};
                border: 1px solid {ModernColors.GLASS_BORDER};
                border-radius: {BorderRadius.MD}px;
                margin-top: 12px;
                padding-top: 16px;
                background: {ModernColors.SURFACE_SECONDARY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 8px 16px;
                background: {ModernColors.ACCENT};
                border-radius: {BorderRadius.SM}px;
                color: {ModernColors.TEXT_PRIMARY};
            }}
        """
        )

        layout = QFormLayout(group)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 30, 20, 20)

        # Database fields
        self.db_server_input = QLineEdit()
        self.db_server_input.setPlaceholderText("Server\\Instance")
        self.db_server_input.setStyleSheet(get_input_style())

        self.db_name_input = QLineEdit()
        self.db_name_input.setPlaceholderText("Database name")
        self.db_name_input.setStyleSheet(get_input_style())

        layout.addRow("Server:", self.db_server_input)
        layout.addRow("Database:", self.db_name_input)

        return group

    def _create_sync_config(self):
        """Create sync configuration section"""
        group = QGroupBox("Synchronization Settings")
        group.setStyleSheet(
            f"""
            QGroupBox {{
                font-size: 16px;
                font-weight: 600;
                color: {ModernColors.TEXT_PRIMARY};
                border: 1px solid {ModernColors.GLASS_BORDER};
                border-radius: {BorderRadius.MD}px;
                margin-top: 12px;
                padding-top: 16px;
                background: {ModernColors.SURFACE_SECONDARY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 8px 16px;
                background: {ModernColors.SUCCESS};
                border-radius: {BorderRadius.SM}px;
                color: {ModernColors.TEXT_PRIMARY};
            }}
        """
        )

        layout = QVBoxLayout(group)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 30, 20, 20)

        # Auto sync checkbox
        self.auto_sync_checkbox = QCheckBox("Enable automatic synchronization")
        self.auto_sync_checkbox.setStyleSheet(
            f"""
            QCheckBox {{
                font-size: 14px;
                color: {ModernColors.TEXT_PRIMARY};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {ModernColors.GLASS_BORDER};
                background: {ModernColors.SURFACE_PRIMARY};
            }}
            QCheckBox::indicator:checked {{
                background: {ModernColors.PRIMARY};
                border-color: {ModernColors.PRIMARY};
            }}
        """
        )
        layout.addWidget(self.auto_sync_checkbox)

        # Sync interval
        interval_layout = QHBoxLayout()
        interval_label = QLabel("Sync interval (minutes):")
        interval_label.setStyleSheet(f"color: {ModernColors.TEXT_PRIMARY};")

        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, 1440)
        self.interval_spinbox.setValue(10)
        self.interval_spinbox.setStyleSheet(get_input_style())

        interval_layout.addWidget(interval_label)
        interval_layout.addWidget(self.interval_spinbox)
        interval_layout.addStretch()

        layout.addLayout(interval_layout)

        return group

    def _create_logs_tab(self):
        """Create logs tab content"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Log controls
        controls_layout = QHBoxLayout()

        clear_btn = ModernActionButton("Clear Logs", "🗑", "ghost")
        export_btn = ModernActionButton("Export Logs", "💾", "secondary")

        controls_layout.addWidget(clear_btn)
        controls_layout.addWidget(export_btn)
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        # Log console
        self.log_console = ModernLogConsole()
        layout.addWidget(self.log_console)

        # Connect clear button
        clear_btn.clicked.connect(self.log_console.clear)

        return widget

    def _setup_status_bar(self):
        """Setup modern status bar"""
        status_bar = self.statusBar()
        status_bar.setStyleSheet(
            f"""
            QStatusBar {{
                background: {ModernColors.SURFACE_SECONDARY};
                border-top: 1px solid {ModernColors.GLASS_BORDER};
                color: {ModernColors.TEXT_SECONDARY};
                font-size: 12px;
                padding: 4px 16px;
            }}
        """
        )

        # Status labels
        self.connection_label = QLabel("Disconnected")
        self.sync_label = QLabel("Ready")

        status_bar.addWidget(self.connection_label)
        status_bar.addPermanentWidget(self.sync_label)

    def _connect_signals(self):
        """Connect controller signals to UI updates"""
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

            # Connect dashboard signals
            self.dashboard.sync_requested.connect(self._run_sync)
            self.dashboard.test_connections_requested.connect(self._test_connections)
            self.dashboard.import_excel_requested.connect(self._import_excel)

        except Exception as e:
            logger.error(f"Signal connection error: {e}")

    @pyqtSlot(str, str)
    def _add_log(self, message: str, level: str):
        """Add log message to console"""
        self.log_console.append_log(message, level)

    @pyqtSlot(str)
    def _update_sp_status(self, status: str):
        """Update SharePoint status"""
        status_map = {
            "connected": ("Connected", "success"),
            "disconnected": ("Disconnected", "error"),
            "connecting": ("Connecting...", "warning"),
            "error": ("Error", "error"),
        }

        display_text, status_type = status_map.get(status, (status.title(), "neutral"))
        self.dashboard.update_status_card("sharepoint", display_text, status_type)
        self.header_bar.update_connection_status(status == "connected")

    @pyqtSlot(str)
    def _update_db_status(self, status: str):
        """Update database status"""
        status_map = {
            "connected": ("Connected", "success"),
            "disconnected": ("Disconnected", "error"),
            "connecting": ("Connecting...", "warning"),
            "error": ("Error", "error"),
        }

        display_text, status_type = status_map.get(status, (status.title(), "neutral"))
        self.dashboard.update_status_card("database", display_text, status_type)

    @pyqtSlot(str, int, str)
    def _update_progress(self, task: str, percent: int, message: str):
        """Update progress display"""
        self.dashboard.progress_section.update_progress(task, percent, message)

    @pyqtSlot(str)
    def _update_task(self, task: str):
        """Update current task display"""
        self.sync_label.setText(task)

    def _test_connections(self):
        """Test all connections"""
        if hasattr(self.controller, "test_all_connections"):
            self.controller.test_all_connections()

    def _run_sync(self):
        """Run synchronization"""
        if hasattr(self.controller, "run_full_sync"):
            self.controller.run_full_sync("spo_to_sql")

    def _import_excel(self):
        """Import Excel file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Excel File", "", "Excel Files (*.xlsx *.xls)"
        )
        if file_path and hasattr(self.controller, "import_excel_data"):
            self.controller.import_excel_data(file_path, "imported_data", {})

    def closeEvent(self, event):
        """Handle window close event"""
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
        """Cleanup resources before closing"""
        if self.cleanup_done:
            return

        logger.info("Cleaning up Modern MainWindow")

        try:
            # Cleanup controller
            if self.controller and hasattr(self.controller, "cleanup"):
                self.controller.cleanup()

            # Cleanup UI components
            if hasattr(self, "log_console"):
                self.log_console.clear()

            self.cleanup_done = True
            logger.info("Modern MainWindow cleanup completed")

        except Exception as e:
            logger.error(f"Error during MainWindow cleanup: {e}")


# Backward compatibility
MainWindow = OptimizedMainWindow
