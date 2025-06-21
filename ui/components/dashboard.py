# ui/components/dashboard.py - Modern 2025 Dashboard
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import sys
from pathlib import Path

current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from ui.styles.theme import ModernColors, Typography, BorderRadius, Spacing
    from ui.widgets.modern_button import ActionButton, IconButton
except ImportError:

    class ModernColors:
        SURFACE_SECONDARY = "#1E293B"
        PRIMARY = "#6366F1"
        SUCCESS = "#10B981"
        ERROR = "#EF4444"
        WARNING = "#F59E0B"
        TEXT_PRIMARY = "#F8FAFC"
        TEXT_SECONDARY = "#CBD5E1"


class StatusIndicator(QWidget):
    """Modern status indicator with pulse animation"""

    def __init__(self, size=12, parent=None):
        super().__init__(parent)
        self.status = "disconnected"
        self.size = size
        self.setFixedSize(size, size)

        # Pulse animation
        self.pulse_animation = QPropertyAnimation(self, b"opacity")
        self.pulse_animation.setDuration(1500)
        self.pulse_animation.setStartValue(0.3)
        self.pulse_animation.setEndValue(1.0)
        self.pulse_animation.setLoopCount(-1)
        self.pulse_animation.setEasingCurve(QEasingCurve.Type.InOutSine)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        colors = {
            "connected": ModernColors.SUCCESS,
            "disconnected": ModernColors.ERROR,
            "connecting": ModernColors.WARNING,
            "syncing": ModernColors.PRIMARY,
        }

        color = QColor(colors.get(self.status, ModernColors.ERROR))
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, self.size, self.size)

    def set_status(self, status):
        self.status = status
        if status in ["connecting", "syncing"]:
            self.pulse_animation.start()
        else:
            self.pulse_animation.stop()
            self.setProperty("opacity", 1.0)
        self.update()


class MetricCard(QWidget):
    """Modern metric display card"""

    def __init__(self, title, value="—", unit="", trend=None, parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.unit = unit
        self.trend = trend
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        # Header with title and indicator
        header_layout = QHBoxLayout()

        title_label = QLabel(self.title)
        title_label.setStyleSheet(
            f"""
            font-size: {Typography.TEXT_SM}px;
            font-weight: {Typography.WEIGHT_MEDIUM};
            color: {ModernColors.TEXT_SECONDARY};
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """
        )
        header_layout.addWidget(title_label)

        self.status_indicator = StatusIndicator(8)
        header_layout.addWidget(self.status_indicator)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Value display
        value_layout = QHBoxLayout()

        self.value_label = QLabel(self.value)
        self.value_label.setStyleSheet(
            f"""
            font-size: {Typography.TEXT_2XL}px;
            font-weight: {Typography.WEIGHT_BOLD};
            color: {ModernColors.TEXT_PRIMARY};
        """
        )
        value_layout.addWidget(self.value_label)

        if self.unit:
            unit_label = QLabel(self.unit)
            unit_label.setStyleSheet(
                f"""
                font-size: {Typography.TEXT_BASE}px;
                color: {ModernColors.TEXT_SECONDARY};
                margin-left: 4px;
            """
            )
            value_layout.addWidget(unit_label)

        value_layout.addStretch()
        layout.addLayout(value_layout)

        # Trend indicator
        if self.trend:
            self.trend_label = QLabel(self.trend)
            self.trend_label.setStyleSheet(
                f"""
                font-size: {Typography.TEXT_SM}px;
                color: {ModernColors.SUCCESS};
            """
            )
            layout.addWidget(self.trend_label)

        # Card styling
        self.setStyleSheet(
            f"""
            QWidget {{
                background: {ModernColors.SURFACE_SECONDARY};
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: {BorderRadius.MD}px;
            }}
            QWidget:hover {{
                border-color: {ModernColors.PRIMARY};
                background: rgba(30, 41, 59, 0.8);
            }}
        """
        )
        self.setMinimumHeight(100)

    def update_value(self, value, status="neutral", trend=None):
        colors = {
            "success": ModernColors.SUCCESS,
            "error": ModernColors.ERROR,
            "warning": ModernColors.WARNING,
            "neutral": ModernColors.TEXT_PRIMARY,
        }

        color = colors.get(status, ModernColors.TEXT_PRIMARY)
        self.value_label.setText(str(value))
        self.value_label.setStyleSheet(
            f"""
            font-size: {Typography.TEXT_2XL}px;
            font-weight: {Typography.WEIGHT_BOLD};
            color: {color};
        """
        )

        self.status_indicator.set_status(status)

        if trend and hasattr(self, "trend_label"):
            self.trend_label.setText(trend)


class QuickActionsPanel(QWidget):
    """Quick action buttons panel"""

    sync_requested = pyqtSignal()
    test_requested = pyqtSignal()
    import_requested = pyqtSignal()
    clean_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Section title
        title = QLabel("Quick Actions")
        title.setStyleSheet(
            f"""
            font-size: {Typography.TEXT_LG}px;
            font-weight: {Typography.WEIGHT_SEMIBOLD};
            color: {ModernColors.TEXT_PRIMARY};
            margin-bottom: 8px;
        """
        )
        layout.addWidget(title)

        # Action buttons grid
        grid = QGridLayout()
        grid.setSpacing(8)

        # Primary actions
        self.sync_btn = ActionButton.primary("🚀 Run Sync", size="md")
        self.sync_btn.clicked.connect(self.sync_requested.emit)

        self.test_btn = ActionButton.secondary("🔗 Test Connections", size="md")
        self.test_btn.clicked.connect(self.test_requested.emit)

        # Secondary actions
        self.import_btn = ActionButton.accent("📊 Import Excel", size="md")
        self.import_btn.clicked.connect(self.import_requested.emit)

        self.clean_btn = ActionButton.ghost("🧹 Clean Cache", size="md")
        self.clean_btn.clicked.connect(self.clean_requested.emit)

        grid.addWidget(self.sync_btn, 0, 0)
        grid.addWidget(self.test_btn, 0, 1)
        grid.addWidget(self.import_btn, 1, 0)
        grid.addWidget(self.clean_btn, 1, 1)

        layout.addLayout(grid)


class ProgressPanel(QWidget):
    """Modern progress display panel"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Current Operation")
        title.setStyleSheet(
            f"""
            font-size: {Typography.TEXT_LG}px;
            font-weight: {Typography.WEIGHT_SEMIBOLD};
            color: {ModernColors.TEXT_PRIMARY};
        """
        )
        header_layout.addWidget(title)

        self.status_indicator = StatusIndicator(10)
        header_layout.addWidget(self.status_indicator)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Task description
        self.task_label = QLabel("Ready")
        self.task_label.setStyleSheet(
            f"""
            font-size: {Typography.TEXT_BASE}px;
            color: {ModernColors.TEXT_SECONDARY};
        """
        )
        layout.addWidget(self.task_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(
            f"""
            QProgressBar {{
                background: rgba(51, 65, 85, 0.5);
                border: none;
                border-radius: 6px;
                height: 12px;
                text-align: center;
                color: {ModernColors.TEXT_PRIMARY};
                font-weight: {Typography.WEIGHT_MEDIUM};
                font-size: {Typography.TEXT_SM}px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ModernColors.PRIMARY},
                    stop:1 #8B5CF6
                );
                border-radius: 6px;
            }}
        """
        )
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Card styling
        self.setStyleSheet(
            f"""
            QWidget {{
                background: {ModernColors.SURFACE_SECONDARY};
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: {BorderRadius.MD}px;
            }}
        """
        )

    def update_progress(self, task, percentage, message=""):
        display_text = f"{task}: {message}" if message else task
        self.task_label.setText(display_text)
        self.progress_bar.setValue(percentage)

        if percentage > 0 and percentage < 100:
            self.status_indicator.set_status("syncing")
        elif percentage == 100:
            self.status_indicator.set_status("connected")
        else:
            self.status_indicator.set_status("disconnected")


class SystemOverview(QWidget):
    """System overview with key metrics"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Section title
        title = QLabel("System Overview")
        title.setStyleSheet(
            f"""
            font-size: {Typography.TEXT_LG}px;
            font-weight: {Typography.WEIGHT_SEMIBOLD};
            color: {ModernColors.TEXT_PRIMARY};
        """
        )
        layout.addWidget(title)

        # Metrics grid
        grid = QGridLayout()
        grid.setSpacing(12)

        # Create metric cards
        self.sp_card = MetricCard("SharePoint", "Disconnected")
        self.db_card = MetricCard("Database", "Disconnected")
        self.sync_card = MetricCard("Last Sync", "Never")
        self.auto_sync_card = MetricCard("Auto Sync", "Disabled")

        grid.addWidget(self.sp_card, 0, 0)
        grid.addWidget(self.db_card, 0, 1)
        grid.addWidget(self.sync_card, 1, 0)
        grid.addWidget(self.auto_sync_card, 1, 1)

        layout.addLayout(grid)

        # Store cards for easy access
        self.cards = {
            "sharepoint": self.sp_card,
            "database": self.db_card,
            "sync": self.sync_card,
            "auto_sync": self.auto_sync_card,
        }

    def update_metric(self, metric_type, value, status="neutral", trend=None):
        if metric_type in self.cards:
            self.cards[metric_type].update_value(value, status, trend)


class RecentActivity(QWidget):
    """Recent activity log display"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.activities = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Recent Activity")
        title.setStyleSheet(
            f"""
            font-size: {Typography.TEXT_LG}px;
            font-weight: {Typography.WEIGHT_SEMIBOLD};
            color: {ModernColors.TEXT_PRIMARY};
        """
        )
        header_layout.addWidget(title)
        header_layout.addStretch()

        clear_btn = IconButton("🗑", tooltip="Clear activity", size="sm")
        clear_btn.clicked.connect(self.clear_activities)
        header_layout.addWidget(clear_btn)

        layout.addLayout(header_layout)

        # Activity list
        self.activity_list = QListWidget()
        self.activity_list.setStyleSheet(
            f"""
            QListWidget {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                background: rgba(51, 65, 85, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 6px;
                padding: 8px;
                margin: 2px 0;
                color: {ModernColors.TEXT_PRIMARY};
                font-size: {Typography.TEXT_SM}px;
            }}
            QListWidget::item:hover {{
                background: rgba(51, 65, 85, 0.5);
                border-color: {ModernColors.PRIMARY};
            }}
        """
        )
        self.activity_list.setMaximumHeight(200)
        layout.addWidget(self.activity_list)

        # Card styling
        self.setStyleSheet(
            f"""
            QWidget {{
                background: {ModernColors.SURFACE_SECONDARY};
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: {BorderRadius.MD}px;
            }}
        """
        )

    def add_activity(self, message, activity_type="info"):
        from datetime import datetime

        icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}

        icon = icons.get(activity_type, "ℹ️")
        timestamp = datetime.now().strftime("%H:%M:%S")

        item_text = f"{icon} {timestamp} - {message}"
        self.activity_list.insertItem(0, item_text)

        # Limit to 50 items
        if self.activity_list.count() > 50:
            self.activity_list.takeItem(self.activity_list.count() - 1)

    def clear_activities(self):
        self.activity_list.clear()
        self.add_activity("Activity log cleared", "info")


class Dashboard(QWidget):
    """Main 2025 Modern Dashboard"""

    # Signals
    sync_requested = pyqtSignal()
    test_connections_requested = pyqtSignal()
    import_excel_requested = pyqtSignal()
    clear_cache_requested = pyqtSignal()

    def __init__(self, controller=None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.cleanup_done = False
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        # Top section - Overview and Progress
        top_section = QHBoxLayout()
        top_section.setSpacing(24)

        # System overview (left side)
        self.overview = SystemOverview()
        top_section.addWidget(self.overview, 2)

        # Progress panel (right side)
        self.progress_panel = ProgressPanel()
        top_section.addWidget(self.progress_panel, 1)

        layout.addLayout(top_section)

        # Middle section - Actions and Activity
        middle_section = QHBoxLayout()
        middle_section.setSpacing(24)

        # Quick actions (left side)
        self.actions_panel = QuickActionsPanel()
        middle_section.addWidget(self.actions_panel, 1)

        # Recent activity (right side)
        self.activity_panel = RecentActivity()
        middle_section.addWidget(self.activity_panel, 1)

        layout.addLayout(middle_section)

        layout.addStretch()

    def _connect_signals(self):
        """Connect internal signals"""
        self.actions_panel.sync_requested.connect(self.sync_requested.emit)
        self.actions_panel.test_requested.connect(self.test_connections_requested.emit)
        self.actions_panel.import_requested.connect(self.import_excel_requested.emit)
        self.actions_panel.clean_requested.connect(self.clear_cache_requested.emit)

    # Public interface methods for MainWindow
    def update_sharepoint_status(self, status):
        status_map = {
            "connected": ("Connected", "success"),
            "disconnected": ("Disconnected", "error"),
            "connecting": ("Connecting...", "connecting"),
            "error": ("Error", "error"),
        }
        display, status_type = status_map.get(status, (status, "neutral"))
        self.overview.update_metric("sharepoint", display, status_type)
        self.activity_panel.add_activity(f"SharePoint: {display}", status_type)

    def update_database_status(self, status):
        status_map = {
            "connected": ("Connected", "success"),
            "disconnected": ("Disconnected", "error"),
            "connecting": ("Connecting...", "connecting"),
            "error": ("Error", "error"),
        }
        display, status_type = status_map.get(status, (status, "neutral"))
        self.overview.update_metric("database", display, status_type)
        self.activity_panel.add_activity(f"Database: {display}", status_type)

    def update_sync_status(self, status):
        self.overview.update_metric(
            "sync", status, "success" if status != "Never" else "neutral"
        )
        if status != "Never":
            self.activity_panel.add_activity(f"Sync completed: {status}", "success")

    def update_auto_sync_status(self, enabled):
        status = "Enabled" if enabled else "Disabled"
        status_type = "success" if enabled else "neutral"
        self.overview.update_metric("auto_sync", status, status_type)
        self.activity_panel.add_activity(f"Auto-sync {status.lower()}", "info")

    def update_progress(self, task, percentage, message=""):
        self.progress_panel.update_progress(task, percentage, message)
        if percentage == 100:
            self.activity_panel.add_activity(f"Completed: {task}", "success")
        elif percentage == 0:
            self.activity_panel.add_activity(f"Started: {task}", "info")

    def update_current_task(self, task):
        self.progress_panel.task_label.setText(task)
        if task != "Ready" and task != "Idle":
            self.activity_panel.add_activity(f"Task: {task}", "info")

    def add_activity_log(self, message, level="info"):
        self.activity_panel.add_activity(message, level)

    # Backward compatibility properties
    @property
    def sp_status_card(self):
        return self.overview.sp_card

    @property
    def db_status_card(self):
        return self.overview.db_card

    @property
    def last_sync_status_card(self):
        return self.overview.sync_card

    @property
    def auto_sync_status_card(self):
        return self.overview.auto_sync_card

    def cleanup(self):
        """Cleanup dashboard resources"""
        if self.cleanup_done:
            return

        try:
            # Cleanup panels
            if hasattr(self, "activity_panel"):
                self.activity_panel.clear_activities()

            # Cleanup animations
            for card in self.overview.cards.values():
                if hasattr(card, "status_indicator"):
                    card.status_indicator.pulse_animation.stop()

            if hasattr(self.progress_panel, "status_indicator"):
                self.progress_panel.status_indicator.pulse_animation.stop()

            self.cleanup_done = True

        except Exception as e:
            print(f"Dashboard cleanup error: {e}")


# Factory function for easy creation
def create_modern_dashboard(controller=None, parent=None):
    """Create a modern dashboard instance"""
    return Dashboard(controller, parent)
