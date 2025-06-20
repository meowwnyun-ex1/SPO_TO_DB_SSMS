# ui/components/dashboard.py - Compact Dashboard Component
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFileDialog,
    QMessageBox,
    QLabel,
)
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt6.QtGui import QFont
import logging
import sys
from pathlib import Path

# Add project root to path for imports
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from ui.widgets.status_card import ModernStatusCard
    from ui.widgets.holographic_progress_bar import HolographicProgressBar
    from ui.widgets.modern_button import ActionButton
    from ui.styles.theme import UltraModernColors, CompactScaling
    from ui.widgets.neon_groupbox import NeonGroupBox
    from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity
    from utils.config_manager import get_simple_config

except ImportError as e:
    print(f"Import error in dashboard.py: {e}")
    sys.exit(1)

logger = logging.getLogger(__name__)


class CompactStatusGrid(QWidget):
    """Compact status display grid for 900x500"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup compact status grid"""
        layout = QGridLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(3)

        # Create compact status cards
        self.sp_status_card = ModernStatusCard("SharePoint", "disconnected")
        self.db_status_card = ModernStatusCard("Database", "disconnected")
        self.sync_status_card = ModernStatusCard("Last Sync", "never")
        self.auto_sync_card = ModernStatusCard(
            "Auto-Sync", False, is_boolean_status=True
        )

        # Arrange in 2x2 grid for compact layout
        layout.addWidget(self.sp_status_card, 0, 0)
        layout.addWidget(self.db_status_card, 0, 1)
        layout.addWidget(self.sync_status_card, 1, 0)
        layout.addWidget(self.auto_sync_card, 1, 1)

        # Reduce card heights for compact display
        for card in [
            self.sp_status_card,
            self.db_status_card,
            self.sync_status_card,
            self.auto_sync_card,
        ]:
            card.setMaximumHeight(CompactScaling.STATUS_CARD_HEIGHT)

    def cleanup(self):
        """Cleanup status cards"""
        cards = [
            self.sp_status_card,
            self.db_status_card,
            self.sync_status_card,
            self.auto_sync_card,
        ]
        for card in cards:
            if hasattr(card, "cleanup_animations"):
                card.cleanup_animations()


class CompactControlPanel(QWidget):
    """Compact control panel with essential buttons"""

    # Signals
    run_sync_requested = pyqtSignal(str)
    clear_cache_requested = pyqtSignal()
    test_connections_requested = pyqtSignal()
    import_excel_requested = pyqtSignal(str, str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = get_simple_config()  # Use simple config access
        self._setup_ui()

    def _setup_ui(self):
        """Setup compact control panel"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Essential action buttons in horizontal layout
        self.sync_button = ActionButton("🚀 Sync", "primary", "sm")
        self.test_button = ActionButton("🌐 Test", "secondary", "sm")
        self.excel_button = ActionButton("📊 Excel", "ghost", "sm")
        self.cache_button = ActionButton("🧹 Clean", "ghost", "sm")

        # Add buttons to layout
        layout.addWidget(self.sync_button)
        layout.addWidget(self.test_button)
        layout.addWidget(self.excel_button)
        layout.addWidget(self.cache_button)
        layout.addStretch(1)  # Push buttons to left

        # Connect signals
        self.sync_button.clicked.connect(self._on_sync_clicked)
        self.test_button.clicked.connect(self.test_connections_requested.emit)
        self.excel_button.clicked.connect(self._on_excel_clicked)
        self.cache_button.clicked.connect(self.clear_cache_requested.emit)

    @pyqtSlot()
    def _on_sync_clicked(self):
        """Handle sync button click"""
        try:
            config = get_simple_config()
            direction = getattr(config, "auto_sync_direction", "spo_to_sql")
            self.run_sync_requested.emit(direction)
        except Exception as e:
            logger.error(f"Error handling sync click: {e}")

    @pyqtSlot()
    def _on_excel_clicked(self):
        """Handle Excel import button click"""
        try:
            file_dialog = QFileDialog(self)
            file_dialog.setWindowTitle("Select Excel File")
            file_dialog.setNameFilter("Excel Files (*.xlsx *.xls)")
            file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

            if file_dialog.exec():
                selected_files = file_dialog.selectedFiles()
                if selected_files:
                    file_path = selected_files[0]

                    config = get_simple_config()
                    table_name = getattr(config, "sql_table_name", "imported_data")
                    column_mapping = getattr(config, "excel_import_mapping", {})

                    if not column_mapping:
                        QMessageBox.warning(
                            self,
                            "Missing Config",
                            "Excel import mapping not configured.\nPlease configure in Config panel.",
                            QMessageBox.StandardButton.Ok,
                        )
                        return

                    self.import_excel_requested.emit(
                        file_path, table_name, column_mapping
                    )

        except Exception as e:
            logger.error(f"Error handling Excel import: {e}")


class CompactProgressPanel(QWidget):
    """Compact progress display panel"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup compact progress panel"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        # Current task label - smaller font
        self.task_label = QLabel("Idle")
        self.task_label.setFont(
            QFont("Segoe UI", CompactScaling.FONT_SIZE_NORMAL, QFont.Weight.Bold)
        )
        self.task_label.setStyleSheet(f"color: {UltraModernColors.NEON_GREEN};")
        self.task_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.task_label)

        # Compact progress bar
        self.progress_bar = HolographicProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximumHeight(CompactScaling.PROGRESS_BAR_HEIGHT)
        layout.addWidget(self.progress_bar)

    def update_progress(self, task_name: str, percentage: int, message: str):
        """Update progress display"""
        try:
            # Truncate long messages for compact display
            display_message = message[:30] + "..." if len(message) > 30 else message
            self.task_label.setText(f"{task_name}: {display_message}")
            self.progress_bar.setValue(max(0, min(100, percentage)))
        except Exception as e:
            logger.debug(f"Error updating progress: {e}")

    def update_current_task(self, task_description: str):
        """Update current task description"""
        try:
            # Truncate for compact display
            display_task = (
                task_description[:40] + "..."
                if len(task_description) > 40
                else task_description
            )
            self.task_label.setText(display_task)
        except Exception as e:
            logger.debug(f"Error updating task: {e}")


class Dashboard(QWidget):
    """
    Compact dashboard optimized for 900x500 display.
    Consolidates all essential information in minimal space.
    """

    # Signals to communicate with AppController
    run_sync_requested = pyqtSignal(str)
    clear_cache_requested = pyqtSignal()
    test_connections_requested = pyqtSignal()
    import_excel_requested = pyqtSignal(str, str, dict)

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.cleanup_done = False

        self._setup_ui()
        self._connect_signals()

        logger.info("Compact Dashboard initialized")

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.HIGH)
    def _setup_ui(self):
        """Setup compact dashboard layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        main_layout.setSpacing(4)

        # 1. Status section - most important info at top
        status_group = NeonGroupBox("System Status")
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(4, 8, 4, 4)
        status_layout.setSpacing(4)

        self.status_grid = CompactStatusGrid()
        status_layout.addWidget(self.status_grid)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)

        # 2. Progress section - show current operations
        progress_group = NeonGroupBox("Current Operation")
        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(4, 8, 4, 4)
        progress_layout.setSpacing(2)

        self.progress_panel = CompactProgressPanel()
        progress_layout.addWidget(self.progress_panel)
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)

        # 3. Quick actions - essential controls
        actions_group = NeonGroupBox("Quick Actions")
        actions_layout = QVBoxLayout()
        actions_layout.setContentsMargins(4, 8, 4, 4)
        actions_layout.setSpacing(4)

        self.control_panel = CompactControlPanel()
        actions_layout.addWidget(self.control_panel)
        actions_group.setLayout(actions_layout)
        main_layout.addWidget(actions_group)

        # 4. System info - compact footer
        self._create_system_info_footer(main_layout)

        main_layout.addStretch(1)  # Push content to top

    def _create_system_info_footer(self, main_layout):
        """Create compact system information footer"""
        try:
            footer_layout = QHBoxLayout()
            footer_layout.setContentsMargins(0, 0, 0, 0)
            footer_layout.setSpacing(8)

            # System status indicators
            config = self.config_manager.get_config()

            version_label = QLabel(f"v{config.app_version}")
            version_label.setFont(QFont("Segoe UI", CompactScaling.FONT_SIZE_TINY))
            version_label.setStyleSheet(f"color: {UltraModernColors.TEXT_SECONDARY};")

            db_type_label = QLabel(f"DB: {config.database_type.upper()}")
            db_type_label.setFont(QFont("Segoe UI", CompactScaling.FONT_SIZE_TINY))
            db_type_label.setStyleSheet(f"color: {UltraModernColors.TEXT_SECONDARY};")

            footer_layout.addWidget(version_label)
            footer_layout.addWidget(db_type_label)
            footer_layout.addStretch(1)

            main_layout.addLayout(footer_layout)

        except Exception as e:
            logger.error(f"Error creating system info footer: {e}")

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.HIGH)
    def _connect_signals(self):
        """Connect UI elements to controller actions"""
        try:
            # Connect control panel signals
            self.control_panel.run_sync_requested.connect(self.run_sync_requested.emit)
            self.control_panel.clear_cache_requested.connect(
                self.clear_cache_requested.emit
            )
            self.control_panel.test_connections_requested.connect(
                self.test_connections_requested.emit
            )
            self.control_panel.import_excel_requested.connect(
                self.import_excel_requested.emit
            )

            logger.debug("Compact dashboard signals connected successfully")

        except Exception as e:
            logger.error(f"Error connecting dashboard signals: {e}")

    # Methods called by MainWindow to update dashboard state

    @pyqtSlot(str, int, str)
    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.LOW)
    def update_progress(self, task_name: str, percentage: int, message: str):
        """Update progress bar and current task label"""
        if self.progress_panel:
            self.progress_panel.update_progress(task_name, percentage, message)

    @pyqtSlot(str)
    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.LOW)
    def update_current_task(self, task_description: str):
        """Update current task description label"""
        if self.progress_panel:
            self.progress_panel.update_current_task(task_description)

    @pyqtSlot(str, str)
    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.LOW)
    def update_status(self, service_name: str, status: str):
        """Update specific status cards"""
        try:
            if not self.status_grid:
                return

            if service_name == "SharePoint" and hasattr(
                self.status_grid, "sp_status_card"
            ):
                self.status_grid.sp_status_card.set_status(status)
            elif service_name == "Database" and hasattr(
                self.status_grid, "db_status_card"
            ):
                self.status_grid.db_status_card.set_status(status)

            logger.debug(f"Status updated: {service_name} → {status}")

        except Exception as e:
            logger.debug(f"Error updating status: {e}")

    # Properties for backward compatibility with MainWindow

    @property
    def sp_status_card(self):
        """Access to SharePoint status card"""
        return self.status_grid.sp_status_card if self.status_grid else None

    @property
    def db_status_card(self):
        """Access to database status card"""
        return self.status_grid.db_status_card if self.status_grid else None

    @property
    def last_sync_status_card(self):
        """Access to last sync status card"""
        return self.status_grid.sync_status_card if self.status_grid else None

    @property
    def auto_sync_status_card(self):
        """Access to auto-sync status card"""
        return self.status_grid.auto_sync_card if self.status_grid else None

    # Backward compatibility methods

    def update_connection_status(self, service_name: str, status: str):
        """Backward compatibility method"""
        self.update_status(service_name, status)

    def set_progress(self, percentage: int, message: str = ""):
        """Backward compatibility method"""
        self.update_progress("Operation", percentage, message)

    def cleanup(self):
        """Perform cleanup for the Dashboard"""
        if self.cleanup_done:
            logger.debug("Dashboard cleanup already performed")
            return

        logger.info("Initiating Dashboard cleanup...")

        try:
            # Clean up status grid
            if hasattr(self, "status_grid") and self.status_grid:
                self.status_grid.cleanup()
                self.status_grid.deleteLater()
                self.status_grid = None

            # Clean up other components
            components = ["progress_panel", "control_panel"]
            for comp_name in components:
                comp = getattr(self, comp_name, None)
                if comp:
                    if hasattr(comp, "cleanup"):
                        comp.cleanup()
                    comp.deleteLater()
                    setattr(self, comp_name, None)

            # Disconnect control panel signals
            try:
                if hasattr(self, "control_panel") and self.control_panel:
                    self.control_panel.run_sync_requested.disconnect()
                    self.control_panel.clear_cache_requested.disconnect()
                    self.control_panel.test_connections_requested.disconnect()
                    self.control_panel.import_excel_requested.disconnect()
            except (TypeError, RuntimeError):
                pass

            # Clean up remaining child widgets
            for child in self.findChildren(QWidget):
                if child and child != self:
                    child.deleteLater()

            self.cleanup_done = True
            logger.info("Dashboard cleanup completed successfully")

        except Exception as e:
            logger.error(f"Error during Dashboard cleanup: {e}")
            self.cleanup_done = True
