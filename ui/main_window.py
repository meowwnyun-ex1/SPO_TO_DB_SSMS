from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QSplitter,
    QMessageBox,
    QStatusBar,
    QLabel,
    QApplication,
    QVBoxLayout,
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QCloseEvent
from .styles.theme import UltraModernColors
from utils.logger import NeuraUILogHandler
from utils.error_handling import (
    handle_exceptions,
    ErrorCategory,
    ErrorSeverity,
    get_error_handler,
)
import logging

logger = logging.getLogger(__name__)


class CompactStatusBar(QStatusBar):
    """Compact status bar สำหรับหน้าจอขนาด 900x500"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_status = "ready"
        self.setFixedHeight(25)

        self.status_label = QLabel("DENSO Neural matrix online...")
        self.status_label.setStyleSheet(
            f"""
            QLabel {{
                color: {UltraModernColors.TEXT_PRIMARY};
                font-weight: 600;
                font-size: 10px;
                padding: 2px 8px;
                background: {UltraModernColors.GLASS_BG_DARK};
                border: 1px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 3px;
                margin: 1px;
            }}
            """
        )
        self.addPermanentWidget(self.status_label)

        self.progress_label = QLabel("●")
        self.progress_label.setStyleSheet(
            f"""
            QLabel {{
                color: {UltraModernColors.NEON_BLUE};
                font-weight: bold;
                font-size: 10px;
                padding: 2px 4px;
            }}
            """
        )
        self.addWidget(self.progress_label)

    @pyqtSlot(str, str)
    def set_status(self, message, status_type="info"):
        """อัปเดตสถานะ - ข้อความสั้นๆ"""
        self.current_status = status_type

        icon_map = {
            "info": "◉",
            "warning": "◈",
            "error": "◆",
            "ready": "◎",
            "syncing": "⟳",
            "success": "✓",
        }

        status_icon = icon_map.get(status_type, "◉")
        # ตัดข้อความให้สั้น
        short_message = message[:30] + "..." if len(message) > 30 else message
        self.status_label.setText(f"{status_icon} {short_message}")


class MainWindow(QMainWindow):
    """Enhanced Main Window - ขนาดคงที่ 900x500 พร้อม UX/UI ที่ดีขึ้น"""

    def __init__(self, controller):
        super().__init__(parent=None)
        self.controller = controller
        self.ui_log_handler = None
        self.is_closing = False
        self.cleanup_done = False

        # Initialize UI components as None first
        self.dashboard = None
        self.config_panel = None
        self.status_bar = None

        # Error handler
        self.error_handler = get_error_handler()
        self.error_handler.error_occurred.connect(self._handle_application_error)

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        self.setup_compact_ui()
        self._connect_signals()
        self._setup_logging()

        if hasattr(self, "status_bar") and self.status_bar:
            self.status_bar.set_status(
                "© Thammaphon Chittasuwanna (SDM) | Innovation", "ready"
            )

    def setup_compact_ui(self):
        """Setup UI สำหรับขนาด 900x500"""
        self.setWindowTitle("DENSO Neural Matrix | SPO ↔ SQL Sync")

        # ขนาดคงที่
        self.setFixedSize(900, 500)
        self.setMinimumSize(900, 500)
        self.setMaximumSize(900, 500)

        # จัดหน้าต่างให้อยู่กลางจอ
        self._center_window()

    def _create_fallback_ui(self):
        """สร้าง fallback UI แบบง่ายๆ"""
        try:
            central_widget = self.centralWidget()
            if not central_widget:
                central_widget = QWidget()
                self.setCentralWidget(central_widget)

            if central_widget.layout():
                QWidget().setLayout(central_widget.layout())

            layout = QVBoxLayout(central_widget)
            layout.setContentsMargins(50, 50, 50, 50)

            error_label = QLabel("⚠️ Main UI Failed to Load")
            error_label.setStyleSheet(
                "color: #FF6B6B; font-size: 18px; font-weight: bold;"
            )
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(error_label)

            details_label = QLabel("Check console and restart")
            details_label.setStyleSheet("color: #CCCCCC; font-size: 14px;")
            details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(details_label)

            logger.info("Basic fallback UI created")
        except Exception as e:
            logger.error(f"Fallback UI failed: {e}")

    def _rebuild_layout(self):
        """Rebuild layout ตามที่มี components"""
        try:
            central_widget = self.centralWidget()
            if not central_widget:
                central_widget = QWidget()
                self.setCentralWidget(central_widget)

            if central_widget.layout():
                QWidget().setLayout(central_widget.layout())

            main_layout = QHBoxLayout(central_widget)
            main_layout.setContentsMargins(5, 5, 5, 5)
            main_layout.setSpacing(10)

            if self.dashboard and self.config_panel:
                self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
                self.main_splitter.setChildrenCollapsible(False)
                self.main_splitter.addWidget(self.dashboard)
                self.main_splitter.addWidget(self.config_panel)
                self.main_splitter.setSizes([540, 360])
                main_layout.addWidget(self.main_splitter)
            elif self.dashboard:
                main_layout.addWidget(self.dashboard)
            elif self.config_panel:
                main_layout.addWidget(self.config_panel)

            logger.info("Layout rebuilt")
        except Exception as e:
            logger.error(f"Layout rebuild failed: {e}")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout แบบ compact
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)

        try:
            # Import ที่นี่เพื่อตรวจสอบว่ามีหรือไม่
            from .components.dashboard import ModernDashboard
            from .components.config_panel import ModernConfigPanel

            self.dashboard = ModernDashboard(self.controller)
            self.config_panel = ModernConfigPanel(self.controller)

            if not self.dashboard or not self.config_panel:
                logger.error("Failed to initialize UI components")
                self.dashboard = None
                self.config_panel = None
                return

        except ImportError as e:
            logger.error(f"Failed to import UI components: {e}")
            self.dashboard = None
            self.config_panel = None
            self._create_fallback_ui()
            return
        except Exception as e:
            logger.error(f"Failed to create UI components: {e}")
            # Create minimal fallback UI
            self.dashboard = None
            self.config_panel = None
            self._create_fallback_ui()
            return

        # Splitter แบบ compact
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setChildrenCollapsible(False)

        if self.dashboard:
            self.main_splitter.addWidget(self.dashboard)
        if self.config_panel:
            self.main_splitter.addWidget(self.config_panel)

        # การแบ่งพื้นที่ 60:40
        self.main_splitter.setSizes([540, 360])
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 0)

        main_layout.addWidget(self.main_splitter)

        # Compact status bar
        self.status_bar = CompactStatusBar(self)
        self.setStatusBar(self.status_bar)

        # Modern splitter styling
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a,
                    stop:0.5 #1a0a2a,
                    stop:1 #0a0a0a
                );
                border: 2px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 12px;
            }}
            QSplitter::handle {{
                background: {UltraModernColors.NEON_PURPLE};
                width: 3px;
                border-radius: 1px;
            }}
            QSplitter::handle:hover {{
                background: {UltraModernColors.NEON_PINK};
                width: 4px;
            }}
            """
        )

    def _center_window(self):
        """จัดหน้าต่างให้อยู่กลางจอ"""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = self.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())

    @handle_exceptions(ErrorCategory.UI, ErrorSeverity.MEDIUM)
    def _connect_signals(self):
        """เชื่อมต่อ signals - ปลอดภัยขึ้น"""
        if not self.controller:
            logger.error("Cannot connect signals - missing controller")
            return

        # ตรวจสอบว่ามี config_panel หรือไม่
        config_panel = getattr(self, "config_panel", None)
        if not config_panel:
            logger.warning("Config panel not available - skipping config signals")
        else:
            try:
                # Config panel signals
                config_panel.config_changed.connect(self.controller.update_config)
                config_panel.test_sharepoint_requested.connect(
                    self.controller.test_sharepoint_connection
                )
                config_panel.test_database_requested.connect(
                    self.controller.test_database_connection
                )

                # Refresh signals
                config_panel.refresh_sites_requested.connect(
                    self.controller.refresh_sharepoint_sites
                )
                config_panel.refresh_lists_requested.connect(
                    self.controller.refresh_sharepoint_lists
                )
                config_panel.refresh_databases_requested.connect(
                    self.controller.refresh_database_names
                )
                config_panel.refresh_tables_requested.connect(
                    self.controller.refresh_database_tables
                )

                config_panel.auto_sync_toggled.connect(self.controller.toggle_auto_sync)

                # Excel import signal
                if hasattr(config_panel, "excel_import_requested"):
                    config_panel.excel_import_requested.connect(
                        self.controller.run_excel_import
                    )

                logger.info("Config panel signals connected")
            except Exception as e:
                logger.error(f"Config panel signals failed: {e}")

        # ตรวจสอบว่ามี dashboard หรือไม่
        dashboard = getattr(self, "dashboard", None)
        if not dashboard:
            logger.warning("Dashboard not available - skipping dashboard signals")
        else:
            try:
                # Controller to dashboard signals
                self.controller.log_message.connect(dashboard.add_log_message)

                # Connect to status bar if available
                status_bar = getattr(self, "status_bar", None)
                if status_bar:
                    self.controller.log_message.connect(status_bar.set_status)

                self.controller.progress_update.connect(
                    dashboard.update_overall_progress
                )
                self.controller.current_task_update.connect(
                    dashboard.update_current_task
                )

                # Status updates
                self.controller.sharepoint_status_update.connect(
                    dashboard.update_sharepoint_status
                )
                self.controller.database_status_update.connect(
                    dashboard.update_database_status
                )
                self.controller.last_sync_status_update.connect(
                    dashboard.update_last_sync_status
                )
                self.controller.auto_sync_status_update.connect(
                    dashboard.set_auto_sync_enabled
                )

                # Sync direction signal
                if hasattr(dashboard, "sync_direction_changed"):
                    dashboard.sync_direction_changed.connect(
                        self.controller.set_sync_direction
                    )

                logger.info("Dashboard signals connected")
            except Exception as e:
                logger.error(f"Dashboard signals failed: {e}")

        # Cross-component signals - only if both exist
        if config_panel and dashboard:
            try:
                # Data population
                self.controller.sharepoint_sites_updated.connect(
                    config_panel.populate_sharepoint_sites
                )
                self.controller.sharepoint_lists_updated.connect(
                    config_panel.populate_sharepoint_lists
                )
                self.controller.database_names_updated.connect(
                    config_panel.populate_database_names
                )
                self.controller.database_tables_updated.connect(
                    config_panel.populate_database_tables
                )

                # UI control
                self.controller.ui_enable_request.connect(config_panel.set_ui_enabled)

                logger.info("Cross-component signals connected")
            except Exception as e:
                logger.error(f"Cross-component signals failed: {e}")

        logger.info("Signal connections completed")

    def _setup_logging(self):
        """Setup logging handler"""
        if self.dashboard and hasattr(self.dashboard, "add_log_message"):
            try:
                self.ui_log_handler = NeuraUILogHandler(self.dashboard.add_log_message)
                logging.getLogger().addHandler(self.ui_log_handler)
                logger.info("UI log handler initialized")
            except Exception as e:
                logger.error(f"Failed to setup UI logging: {e}")

    @pyqtSlot(object)
    def _handle_application_error(self, error_info):
        """จัดการ application errors"""
        error_msg = f"Application Error: {error_info.message}"
        if hasattr(self, "status_bar"):
            self.status_bar.set_status(error_msg, "error")
        logger.error(error_msg)

    def closeEvent(self, event: QCloseEvent):
        """Enhanced close event"""
        if self.is_closing:
            event.accept()
            return

        self.is_closing = True

        try:
            reply = QMessageBox.question(
                self,
                "Neural Matrix Shutdown",
                "ปิดระบบ Neural Matrix?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Safe status bar update
                status_bar = getattr(self, "status_bar", None)
                if status_bar:
                    try:
                        status_bar.set_status("Shutting down...", "warning")
                    except Exception as e:
                        logger.warning(f"Status bar update failed: {e}")

                QApplication.processEvents()

                if not self.cleanup_done:
                    self._safe_cleanup()

                event.accept()
                QApplication.quit()
            else:
                self.is_closing = False
                event.ignore()

        except Exception as e:
            logger.error(f"Close event error: {e}")
            if not self.cleanup_done:
                self._safe_cleanup()
            event.accept()
            QApplication.quit()

    @handle_exceptions(ErrorCategory.SYSTEM, ErrorSeverity.LOW)
    def _safe_cleanup(self):
        """Safe cleanup"""
        if self.cleanup_done:
            return

        try:
            # Controller cleanup
            controller = getattr(self, "controller", None)
            if controller and hasattr(controller, "cleanup"):
                controller.cleanup()

            # UI log handler cleanup
            if self.ui_log_handler:
                try:
                    logging.getLogger().removeHandler(self.ui_log_handler)
                except:
                    pass
                self.ui_log_handler = None

            # Status bar cleanup
            status_bar = getattr(self, "status_bar", None)
            if status_bar and hasattr(status_bar, "cleanup"):
                try:
                    status_bar.cleanup()
                except Exception as e:
                    logger.warning(f"Status bar cleanup failed: {e}")

            # Dashboard cleanup
            dashboard = getattr(self, "dashboard", None)
            if dashboard and hasattr(dashboard, "cleanup"):
                try:
                    dashboard.cleanup()
                except Exception as e:
                    logger.warning(f"Dashboard cleanup failed: {e}")

            # Config panel cleanup
            config_panel = getattr(self, "config_panel", None)
            if config_panel and hasattr(config_panel, "cleanup"):
                try:
                    config_panel.cleanup()
                except Exception as e:
                    logger.warning(f"Config panel cleanup failed: {e}")

            self.cleanup_done = True
            logger.info("Safe cleanup completed")

        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            self.cleanup_done = True

    def keyPressEvent(self, event):
        """Key shortcuts"""
        try:
            if event.key() == Qt.Key.Key_Escape:
                self.close()
            elif event.key() == Qt.Key.Key_F5 and self.controller:
                self.controller.run_full_sync()
            elif event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                if event.key() == Qt.Key.Key_Q:
                    self.close()
                elif event.key() == Qt.Key.Key_R and self.controller:
                    self.controller.test_all_connections()
            else:
                super().keyPressEvent(event)
        except Exception as e:
            logger.error(f"Key press error: {e}")
            super().keyPressEvent(event)
