from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QSplitter,
    QMessageBox,
    QStatusBar,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QFrame,
    QLabel,
    QVBoxLayout,
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer, QPropertyAnimation
from PyQt6.QtGui import QCloseEvent, QFont, QColor
from .components.dashboard import UltraModernDashboard
from .components.config_panel import UltraModernConfigPanel
from .styles.theme import (
    UltraModernColors,
    apply_ultra_modern_theme,
    get_ultra_modern_card_style,
)
from utils.logger import UILogHandler
import logging

logger = logging.getLogger(__name__)


class HolographicStatusBar(QStatusBar):
    """Status bar แบบ holographic พร้อม neural network effects"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_holographic_style()
        self.setup_status_animations()
        self.current_status = "ready"

    def setup_holographic_style(self):
        """ตั้งค่าสไตล์ holographic"""
        self.setStyleSheet(
            f"""
            QStatusBar {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 0, 0, 0.6),
                    stop:0.5 rgba(0, 212, 255, 0.1),
                    stop:1 rgba(0, 0, 0, 0.6)
                );

                color: {UltraModernColors.TEXT_LUMINOUS};
                border-top: 2px solid rgba(0, 212, 255, 0.4);
                padding: 12px 24px;
                font-size: 13px;
                font-weight: 500;
                font-family: 'Inter', 'Segoe UI', sans-serif;

            }}
            QStatusBar::item {{
                border: none;
                background: transparent;
            }}
        """
        )

        # เพิ่ม glow effect
        self.glow_effect = QGraphicsDropShadowEffect()
        self.glow_effect.setBlurRadius(15)
        self.glow_effect.setColor(QColor(0, 212, 255, 60))
        self.glow_effect.setOffset(0, 0)
        self.setGraphicsEffect(self.glow_effect)

    def setup_status_animations(self):
        """ตั้งค่า status animations"""
        self.glow_timer = QTimer()
        self.glow_timer.timeout.connect(self.animate_status_glow)
        self.glow_intensity = 60
        self.glow_direction = 1

    def animate_status_glow(self):
        """Animate status glow effect"""
        if self.current_status in ["syncing", "connecting", "processing"]:
            self.glow_intensity += self.glow_direction * 15
            if self.glow_intensity >= 120:
                self.glow_direction = -1
            elif self.glow_intensity <= 40:
                self.glow_direction = 1

            self.glow_effect.setColor(QColor(0, 212, 255, self.glow_intensity))

    def set_neural_status(self, message, status_type="info"):
        """ตั้งค่าสถานะแบบ neural network"""
        self.current_status = status_type

        # Status icons และสี
        status_configs = {
            "ready": {"icon": "◉", "color": UltraModernColors.NEON_GREEN},
            "connecting": {"icon": "◐", "color": UltraModernColors.NEON_BLUE},
            "syncing": {"icon": "◑", "color": UltraModernColors.NEON_PURPLE},
            "success": {"icon": "◎", "color": UltraModernColors.NEON_GREEN},
            "error": {"icon": "◆", "color": UltraModernColors.NEON_PINK},
            "warning": {"icon": "◈", "color": UltraModernColors.NEON_YELLOW},
        }

        config = status_configs.get(status_type, status_configs["ready"])

        # อัปเดตข้อความพร้อม neural styling
        neural_message = f"{config['icon']} Neural Status: {message}"
        self.showMessage(neural_message)

        # อัปเดต glow color
        if status_type in ["connecting", "syncing", "processing"]:
            self.glow_timer.start(200)
        else:
            self.glow_timer.stop()
            self.glow_effect.setColor(QColor(0, 212, 255, 60))


class HolographicSplitter(QSplitter):
    """Splitter แบบ holographic พร้อม dimensional effects"""

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setup_holographic_style()
        self.setup_hover_animations()

    def setup_holographic_style(self):
        """ตั้งค่าสไตล์ holographic"""
        self.setStyleSheet(
            f"""
            QSplitter {{
                background: transparent;
                border: none;
            }}
            QSplitter::handle {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {UltraModernColors.NEON_BLUE},
                    stop:0.5 {UltraModernColors.NEON_PURPLE},
                    stop:1 {UltraModernColors.NEON_BLUE}
                );
                width: 4px;
                margin: 20px 0px;
                border-radius: 2px;
                box-shadow: 
                    0 0 15px rgba(0, 212, 255, 0.5),
                    inset 0 0 10px rgba(255, 255, 255, 0.1);
            }}
            QSplitter::handle:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 {UltraModernColors.NEON_PURPLE},
                    stop:0.5 {UltraModernColors.NEON_PINK},
                    stop:1 {UltraModernColors.NEON_PURPLE}
                );
                width: 6px;
                box-shadow: 
                    0 0 25px rgba(189, 94, 255, 0.8),
                    inset 0 0 15px rgba(255, 255, 255, 0.2);
            }}
            QSplitter::handle:pressed {{
                background: {UltraModernColors.NEON_PINK};
                box-shadow: 
                    0 0 30px rgba(255, 107, 156, 0.9),
                    inset 0 0 20px rgba(255, 255, 255, 0.3);
            }}
        """
        )

    def setup_hover_animations(self):
        """ตั้งค่า hover animations"""
        self.setChildrenCollapsible(False)


class QuantumLoadingOverlay(QWidget):
    """Loading overlay แบบ quantum พร้อม holographic effects"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_quantum_ui()
        self.setup_quantum_animations()
        self.hide()

    def setup_quantum_ui(self):
        """ตั้งค่า UI แบบ quantum"""
        self.setStyleSheet(
            f"""
            QWidget {{
                background: rgba(0, 0, 0, 0.8);

            }}
        """
        )

        # Loading content
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Quantum loading frame
        loading_frame = QFrame()
        loading_frame.setFixedSize(300, 120)
        loading_frame.setStyleSheet(get_ultra_modern_card_style("neon"))

        frame_layout = QVBoxLayout(loading_frame)
        frame_layout.setAlignment(Qt.AlignCenter)
        frame_layout.setSpacing(16)

        # Loading icon
        self.loading_icon = QLabel("◈")
        self.loading_icon.setFont(QFont("Inter", 32, QFont.Bold))
        self.loading_icon.setAlignment(Qt.AlignCenter)
        self.loading_icon.setStyleSheet(
            f"""
            color: {UltraModernColors.NEON_BLUE};
            text-shadow: 
                0 0 20px {UltraModernColors.NEON_BLUE},
                0 0 40px {UltraModernColors.NEON_BLUE};
        """
        )

        # Loading text
        self.loading_text = QLabel("Initializing Neural Matrix...")
        self.loading_text.setFont(QFont("Inter", 14, QFont.Medium))
        self.loading_text.setAlignment(Qt.AlignCenter)
        self.loading_text.setStyleSheet(
            f"""
            color: {UltraModernColors.TEXT_LUMINOUS};

        """
        )

        frame_layout.addWidget(self.loading_icon)
        frame_layout.addWidget(self.loading_text)
        layout.addWidget(loading_frame)

    def setup_quantum_animations(self):
        """ตั้งค่า quantum animations"""
        # Rotation animation
        self.rotation_timer = QTimer()
        self.rotation_timer.timeout.connect(self.rotate_quantum_icon)
        self.rotation_angle = 0

        # Fade animation
        self.fade_effect = QGraphicsOpacityEffect()
        self.loading_icon.setGraphicsEffect(self.fade_effect)

        self.fade_animation = QPropertyAnimation(self.fade_effect, b"opacity")
        self.fade_animation.setDuration(1000)
        self.fade_animation.setStartValue(0.3)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setLoopCount(-1)

    def rotate_quantum_icon(self):
        """หมุน quantum icon"""
        symbols = ["◈", "◉", "◎", "⬢", "◆", "◇"]
        self.rotation_angle = (self.rotation_angle + 1) % len(symbols)
        self.loading_icon.setText(symbols[self.rotation_angle])

    def show_quantum_loading(self, message="Processing..."):
        """แสดง quantum loading"""
        self.loading_text.setText(message)
        self.rotation_timer.start(200)
        self.fade_animation.start()
        self.show()
        self.raise_()

    def hide_quantum_loading(self):
        """ซ่อน quantum loading"""
        self.rotation_timer.stop()
        self.fade_animation.stop()
        self.hide()


class UltraModernMainWindow(QMainWindow):
    """Main window แบบ ultra modern holographic พร้อม neural network interface"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.ui_log_handler = None
        self.loading_overlay = None
        self.setup_quantum_window()
        self.setup_holographic_ui()
        self.setup_neural_connections()
        self.setup_quantum_logging()
        self.load_neural_state()

    def setup_quantum_window(self):
        """ตั้งค่าหน้าต่างแบบ quantum"""
        self.setWindowTitle("◈ SharePoint to SQL Neural Matrix by เฮียตอม😎 ◈")
        self.setGeometry(100, 100, 1800, 1100)
        self.setMinimumSize(1600, 1000)

        # Apply ultra modern theme
        apply_ultra_modern_theme(self)

        # Holographic status bar
        self.neural_status_bar = HolographicStatusBar()
        self.setStatusBar(self.neural_status_bar)
        self.neural_status_bar.set_neural_status("Neural matrix initialized", "ready")

    def setup_holographic_ui(self):
        """ตั้งค่า UI แบบ holographic"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Holographic splitter
        splitter = HolographicSplitter(Qt.Orientation.Horizontal)

        # Create ultra modern components
        self.neural_dashboard = UltraModernDashboard(self.controller)
        self.quantum_config_panel = UltraModernConfigPanel(self.controller)

        # Add to splitter with quantum proportions
        splitter.addWidget(self.neural_dashboard)
        splitter.addWidget(self.quantum_config_panel)

        # Set neural proportions (dashboard: config = 1:2.2)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([600, 1200])

        main_layout.addWidget(splitter)

        # Quantum loading overlay
        self.loading_overlay = QuantumLoadingOverlay(central_widget)
        self.loading_overlay.resize(central_widget.size())

    def setup_neural_connections(self):
        """ตั้งค่า neural signal connections"""
        # Controller → UI signals
        self.controller.status_changed.connect(self.on_neural_status_changed)
        self.controller.progress_updated.connect(self.on_quantum_progress_updated)
        self.controller.sync_completed.connect(self.on_neural_sync_completed)
        self.controller.log_message.connect(self.on_matrix_log_message)

        # Neural Dashboard → Controller signals
        self.neural_dashboard.test_connections_requested.connect(
            lambda: self.execute_with_quantum_feedback(
                self.controller.test_all_connections, "Testing neural connections..."
            )
        )
        self.neural_dashboard.start_sync_requested.connect(
            lambda: self.execute_with_quantum_feedback(
                self.controller.start_sync, "Initiating quantum sync..."
            )
        )
        self.neural_dashboard.stop_sync_requested.connect(self.controller.stop_sync)
        self.neural_dashboard.clear_logs_requested.connect(self.clear_matrix_logs)
        self.neural_dashboard.auto_sync_toggled.connect(
            self.controller.toggle_auto_sync
        )

        # Quantum Config Panel → Controller signals
        self.quantum_config_panel.config_changed.connect(
            lambda config: self.execute_with_quantum_feedback(
                lambda: self.controller.save_config(config),
                "Saving neural configuration...",
            )
        )
        self.quantum_config_panel.test_sharepoint_requested.connect(
            lambda: self.execute_with_quantum_feedback(
                self.controller.test_sharepoint_connection,
                "Probing SharePoint neural network...",
            )
        )
        self.quantum_config_panel.test_database_requested.connect(
            lambda: self.execute_with_quantum_feedback(
                self.controller.test_database_connection,
                "Testing quantum database link...",
            )
        )
        self.quantum_config_panel.refresh_sites_requested.connect(
            self._handle_neural_refresh_sites
        )
        self.quantum_config_panel.refresh_lists_requested.connect(
            self._handle_neural_refresh_lists
        )
        self.quantum_config_panel.refresh_databases_requested.connect(
            self._handle_neural_refresh_databases
        )
        self.quantum_config_panel.refresh_tables_requested.connect(
            self._handle_neural_refresh_tables
        )

    def setup_quantum_logging(self):
        """ตั้งค่า quantum logging system"""
        self.ui_log_handler = UILogHandler(self.on_matrix_log_message)
        self.ui_log_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(self.ui_log_handler)

    def load_neural_state(self):
        """โหลดสถานะเริ่มต้นของ neural network"""
        try:
            self.loading_overlay.show_quantum_loading("Loading neural configuration...")

            # Load configuration
            config = self.controller.get_config()
            self.quantum_config_panel.load_config(config)

            # Test connections with delay for visual effect
            QTimer.singleShot(1000, self._test_initial_connections)
            QTimer.singleShot(2000, self.loading_overlay.hide_quantum_loading)

        except Exception as e:
            logger.error(f"Failed to load neural state: {str(e)}")
            self.loading_overlay.hide_quantum_loading()

    def _test_initial_connections(self):
        """ทดสอบการเชื่อมต่อเริ่มต้น"""
        QTimer.singleShot(100, self.controller.test_sharepoint_connection)
        QTimer.singleShot(300, self.controller.test_database_connection)

    def execute_with_quantum_feedback(self, func, loading_message):
        """Execute function with quantum visual feedback"""
        self.loading_overlay.show_quantum_loading(loading_message)

        def execute_and_hide():
            try:
                result = func()
                QTimer.singleShot(500, self.loading_overlay.hide_quantum_loading)
                return result
            except Exception as e:
                logger.error(f"Quantum operation failed: {str(e)}")
                QTimer.singleShot(500, self.loading_overlay.hide_quantum_loading)
                self.show_neural_error("Quantum Operation Failed", str(e))

        QTimer.singleShot(100, execute_and_hide)

    # Neural Signal Handlers
    @pyqtSlot(str, str)
    def on_neural_status_changed(self, service, status):
        """Handle neural status changes"""
        self.neural_dashboard.update_connection_status(service, status)

        # Update neural status bar
        status_messages = {
            ("SharePoint", "connected"): (
                "SharePoint neural link established",
                "success",
            ),
            ("Database", "connected"): ("Quantum database synchronized", "success"),
            ("SharePoint", "error"): ("SharePoint neural disruption detected", "error"),
            ("Database", "error"): ("Quantum database link failure", "error"),
            ("SharePoint", "connecting"): (
                "Establishing SharePoint neural link...",
                "connecting",
            ),
            ("Database", "connecting"): (
                "Synchronizing quantum database...",
                "connecting",
            ),
        }

        message_data = status_messages.get(
            (service, status), (f"{service}: {status}", "info")
        )
        self.neural_status_bar.set_neural_status(message_data[0], message_data[1])

    @pyqtSlot(str, int, str)
    def on_quantum_progress_updated(self, message, progress, level):
        """Handle quantum progress updates"""
        self.neural_dashboard.update_progress(message, progress, level)

        if progress > 0:
            self.neural_status_bar.set_neural_status(
                f"Quantum transfer: {message} ({progress}%)", "syncing"
            )

    @pyqtSlot(bool, str)
    def on_neural_sync_completed(self, success, message):
        """Handle neural sync completion"""
        stats = (
            self.controller.get_sync_status()
            if hasattr(self.controller, "get_sync_status")
            else {}
        )
        self.neural_dashboard.on_sync_completed(success, message, stats)

        if success:
            self.neural_status_bar.set_neural_status(
                f"Neural sync complete: {message}", "success"
            )
            self.show_neural_success("Quantum Sync Complete", message)
        else:
            self.neural_status_bar.set_neural_status(
                f"Neural sync failed: {message}", "error"
            )
            self.show_neural_error("Neural Sync Failure", message)

    @pyqtSlot(str, str)
    def on_matrix_log_message(self, message, level):
        """Handle matrix log messages"""
        self.neural_dashboard.add_log_message(message, level)

    # Neural Refresh Handlers
    def _handle_neural_refresh_sites(self):
        """Handle neural site refresh"""
        try:
            self.neural_status_bar.set_neural_status(
                "Scanning neural sites...", "connecting"
            )
            sites = self.controller.get_sharepoint_sites()
            self.neural_status_bar.set_neural_status(
                f"Found {len(sites)} neural sites", "success"
            )
        except Exception as e:
            self.show_neural_error("Neural Site Scan Failed", str(e))

    def _handle_neural_refresh_lists(self):
        """Handle neural list refresh"""
        try:
            self.neural_status_bar.set_neural_status(
                "Analyzing neural data streams...", "connecting"
            )
            config = self.quantum_config_panel.get_config()
            lists = self.controller.get_sharepoint_lists(config.site_url)
            self.quantum_config_panel.update_sharepoint_lists(lists)
            self.neural_status_bar.set_neural_status(
                f"Found {len(lists)} data streams", "success"
            )
        except Exception as e:
            self.show_neural_error("Neural Stream Analysis Failed", str(e))

    def _handle_neural_refresh_databases(self):
        """Handle neural database refresh"""
        try:
            self.neural_status_bar.set_neural_status(
                "Scanning quantum databases...", "connecting"
            )
            databases = self.controller.get_databases()
            self.quantum_config_panel.update_databases(databases)
            self.neural_status_bar.set_neural_status(
                f"Found {len(databases)} quantum databases", "success"
            )
        except Exception as e:
            self.show_neural_error("Quantum Database Scan Failed", str(e))

    def _handle_neural_refresh_tables(self):
        """Handle neural table refresh"""
        try:
            self.neural_status_bar.set_neural_status(
                "Mapping quantum data structures...", "connecting"
            )
            tables = self.controller.get_tables()
            self.quantum_config_panel.update_tables(tables)
            self.neural_status_bar.set_neural_status(
                f"Mapped {len(tables)} data structures", "success"
            )
        except Exception as e:
            self.show_neural_error("Quantum Structure Mapping Failed", str(e))

    # Utility Methods
    def clear_matrix_logs(self):
        """ล้าง matrix logs"""
        self.neural_dashboard.clear_logs()
        self.neural_status_bar.set_neural_status(
            "Neural activity matrix purged", "info"
        )

    def show_neural_success(self, title, message):
        """แสดงข้อความสำเร็จแบบ neural"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(f"◎ {title}")
        msg_box.setText(f"◉ {message}")
        msg_box.setStyleSheet(
            f"""
            QMessageBox {{
                background: {get_ultra_modern_card_style()};
                color: {UltraModernColors.TEXT_LUMINOUS};
            }}
            QMessageBox QPushButton {{
                background: {UltraModernColors.SUCCESS_GLOW};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
            }}
        """
        )
        msg_box.exec_()

    def show_neural_error(self, title, message):
        """แสดงข้อความผิดพลาดแบบ neural"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(f"◆ {title}")
        msg_box.setText(f"✗ {message}")
        msg_box.setStyleSheet(
            f"""
            QMessageBox {{
                background: {get_ultra_modern_card_style()};
                color: {UltraModernColors.TEXT_LUMINOUS};
            }}
            QMessageBox QPushButton {{
                background: {UltraModernColors.ERROR_GLOW};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
            }}
        """
        )
        msg_box.exec_()

    def resizeEvent(self, event):
        """Handle window resize for quantum overlay"""
        super().resizeEvent(event)
        if self.loading_overlay:
            self.loading_overlay.resize(self.centralWidget().size())

    def closeEvent(self, event: QCloseEvent):
        """Handle neural matrix shutdown"""
        try:
            if self.controller.get_sync_status()["is_running"]:
                reply = QMessageBox.question(
                    self,
                    "◈ Neural Matrix Shutdown Confirmation",
                    "Neural synchronization is active.\n\n"
                    + "◦ Force shutdown may cause data corruption\n"
                    + "◦ Recommend graceful termination\n\n"
                    + "Proceed with neural matrix shutdown?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )

                if reply == QMessageBox.No:
                    event.ignore()
                    return

                self.loading_overlay.show_quantum_loading(
                    "Terminating neural processes..."
                )
                self.controller.stop_sync()
                QTimer.singleShot(1000, lambda: self._complete_shutdown(event))
            else:
                self._complete_shutdown(event)

        except Exception as e:
            logger.error(f"Error during neural shutdown: {str(e)}")
            event.accept()

    def _complete_shutdown(self, event):
        """Complete neural matrix shutdown"""
        try:
            self.controller.cleanup()
            if self.ui_log_handler:
                logging.getLogger().removeHandler(self.ui_log_handler)

            self.neural_status_bar.set_neural_status(
                "Neural matrix shutdown complete", "ready"
            )
            event.accept()

        except Exception as e:
            logger.error(f"Error completing neural shutdown: {str(e)}")
            event.accept()


class MainWindow(QMainWindow):
    """Main window สำหรับโปรเจคนี้ ใช้แสดงผล Dashboard"""

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_holographic_ui()

    def setup_holographic_ui(self):
        """ตั้งค่า UI แบบ holographic สำหรับ MainWindow"""
        self.setWindowTitle("SharePoint to SQL Sync")
        self.setMinimumSize(1000, 700)

        # Central widget setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Initialize and add dashboard
        self.neural_dashboard = UltraModernDashboard(self.controller)
        main_layout.addWidget(self.neural_dashboard)
