#!/usr/bin/env python3
"""
DENSO Neural Matrix 2025 - Modern SharePoint to SQL Sync System
© Thammaphon Chittasuwanna (SDM) | Innovation Department
"""

import sys
import signal
import atexit
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap, QFont

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.absolute()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Global instances
app_instance = None
controller_instance = None
main_window_instance = None
logger_ui_handler = None


def setup_environment():
    """Setup application environment"""
    try:
        # Create required directories
        directories = [
            "logs",
            "config",
            "data",
            "reports",
            "resources/images",
            "resources/audio",
            "assets/icons",
            "assets/images",
        ]

        for dir_path in directories:
            (PROJECT_ROOT / dir_path).mkdir(parents=True, exist_ok=True)

        return True
    except Exception as e:
        print(f"Environment setup failed: {e}")
        return False


def setup_logging():
    """Initialize modern logging system"""
    global logger_ui_handler

    try:
        from utils.logger import LoggerManager

        log_file = str(PROJECT_ROOT / "logs" / "app.log")
        logger_ui_handler = LoggerManager.setup_logging(
            log_file=log_file, log_level="INFO"
        )

        if logger_ui_handler:
            print("✅ Modern logging system initialized")
            return True
        else:
            print("⚠️ Logging system initialized with fallback")
            return True

    except Exception as e:
        print(f"❌ Logging setup failed: {e}")
        return False


def create_splash_screen():
    """Create modern splash screen"""
    try:
        # Create splash pixmap
        splash_pixmap = QPixmap(400, 200)
        splash_pixmap.fill(Qt.GlobalColor.transparent)

        splash = QSplashScreen(splash_pixmap)
        splash.setStyleSheet(
            """
            QSplashScreen {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0F172A,
                    stop:1 #1E293B
                );
                border: 2px solid #6366F1;
                border-radius: 12px;
                color: #F8FAFC;
                font-family: "Inter", sans-serif;
                font-size: 14px;
                font-weight: 600;
            }
        """
        )

        splash.showMessage(
            "🚀 DENSO Neural Matrix\nInitializing Modern System...",
            Qt.AlignmentFlag.AlignCenter,
            Qt.GlobalColor.white,
        )

        splash.show()
        return splash

    except Exception:
        return None


def import_components():
    """Import all required components with error handling"""
    components = {}

    try:
        # Core imports
        from ui.styles.theme import apply_modern_theme
        from controller.app_controller import AppController
        from ui.main_window import OptimizedMainWindow

        components.update(
            {
                "theme": apply_modern_theme,
                "controller": AppController,
                "main_window": OptimizedMainWindow,
            }
        )

        print("✅ Core components imported")
        return components

    except ImportError as e:
        print(f"❌ Component import failed: {e}")
        return None


def create_application():
    """Create and configure QApplication"""
    global app_instance

    try:
        app_instance = QApplication(sys.argv)
        app_instance.setApplicationName("DENSO Neural Matrix")
        app_instance.setApplicationVersion("2025.1.0")
        app_instance.setOrganizationName("DENSO Corporation")

        # Set modern font
        font = QFont("Inter", 10)
        font.setStyleHint(QFont.StyleHint.SansSerif)
        app_instance.setFont(font)

        print("✅ QApplication created")
        return True

    except Exception as e:
        print(f"❌ QApplication creation failed: {e}")
        return False


def create_controller():
    """Create application controller"""
    global controller_instance

    try:
        from controller.app_controller import AppController

        controller_instance = AppController()
        print("✅ Controller created")
        return True

    except Exception as e:
        print(f"❌ Controller creation failed: {e}")
        return False


def create_main_window():
    """Create main window with fallback"""
    global main_window_instance

    try:
        from ui.main_window import OptimizedMainWindow

        main_window_instance = OptimizedMainWindow(controller_instance)
        print("✅ Modern main window created")
        return True

    except Exception as e:
        print(f"⚠️ Modern window failed, creating fallback: {e}")
        return create_fallback_window()


def create_fallback_window():
    """Create minimal fallback window"""
    global main_window_instance

    try:
        from PyQt6.QtWidgets import (
            QMainWindow,
            QWidget,
            QVBoxLayout,
            QLabel,
            QPushButton,
            QTextEdit,
        )

        main_window_instance = QMainWindow()
        main_window_instance.setWindowTitle("DENSO Neural Matrix - Safe Mode")
        main_window_instance.setGeometry(100, 100, 800, 600)

        central = QWidget()
        layout = QVBoxLayout(central)

        # Header
        header = QLabel("🚀 DENSO Neural Matrix - Safe Mode")
        header.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            color: #6366F1;
            padding: 16px;
            text-align: center;
        """
        )
        layout.addWidget(header)

        # Log area
        log_area = QTextEdit()
        log_area.setReadOnly(True)
        log_area.setStyleSheet(
            """
            background: #0F172A;
            color: #F8FAFC;
            border: 1px solid #6366F1;
            border-radius: 8px;
            font-family: "Consolas", monospace;
            font-size: 12px;
            padding: 8px;
        """
        )
        layout.addWidget(log_area)

        # Connect controller logs if available
        if controller_instance and hasattr(controller_instance, "log_message"):
            controller_instance.log_message.connect(
                lambda msg, level: log_area.append(f"[{level.upper()}] {msg}")
            )

        # Control buttons
        btn_layout = QVBoxLayout()

        test_btn = QPushButton("🔗 Test Connections")
        test_btn.setStyleSheet(
            """
            QPushButton {
                background: #6366F1;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #4F46E5;
            }
        """
        )
        if controller_instance and hasattr(controller_instance, "test_all_connections"):
            test_btn.clicked.connect(controller_instance.test_all_connections)
        btn_layout.addWidget(test_btn)

        sync_btn = QPushButton("🚀 Run Sync")
        sync_btn.setStyleSheet(test_btn.styleSheet())
        if controller_instance and hasattr(controller_instance, "run_full_sync"):
            sync_btn.clicked.connect(
                lambda: controller_instance.run_full_sync("spo_to_sql")
            )
        btn_layout.addWidget(sync_btn)

        layout.addLayout(btn_layout)
        main_window_instance.setCentralWidget(central)

        print("✅ Fallback window created")
        return True

    except Exception as e:
        print(f"❌ Fallback window creation failed: {e}")
        return False


def connect_ui_logging():
    """Connect UI logging handler to main window"""
    try:
        if (
            logger_ui_handler
            and main_window_instance
            and hasattr(main_window_instance, "log_console")
        ):

            logger_ui_handler.log_record_emitted.connect(
                main_window_instance.log_console.add_log_message
            )
            print("✅ UI logging connected")

    except Exception as e:
        print(f"⚠️ UI logging connection failed: {e}")


def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""

    def signal_handler(signum, frame):
        print(f"\n🔄 Received signal {signum}, shutting down gracefully...")
        cleanup_application()
        if app_instance:
            app_instance.quit()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def cleanup_application():
    """Comprehensive application cleanup"""
    global controller_instance, main_window_instance, logger_ui_handler

    print("🧹 Starting application cleanup...")

    try:
        # Cleanup main window
        if main_window_instance:
            try:
                if hasattr(main_window_instance, "cleanup"):
                    main_window_instance.cleanup()
                main_window_instance.close()
            except Exception as e:
                print(f"Window cleanup error: {e}")

        # Cleanup controller
        if controller_instance:
            try:
                if hasattr(controller_instance, "cleanup"):
                    controller_instance.cleanup()
            except Exception as e:
                print(f"Controller cleanup error: {e}")

        # Cleanup logging
        if logger_ui_handler:
            try:
                logger_ui_handler.cleanup()
            except Exception as e:
                print(f"Logger cleanup error: {e}")

        # Final logging cleanup
        try:
            from utils.logger import LoggerManager

            LoggerManager.cleanup_logging()
        except Exception as e:
            print(f"Final logging cleanup error: {e}")

        print("✅ Application cleanup completed")

    except Exception as e:
        print(f"❌ Cleanup error: {e}")


def run_application():
    """Run the main application event loop"""
    try:
        if not main_window_instance:
            return 1

        # Show main window
        main_window_instance.show()
        print("🚀 Application started successfully")

        # Process events timer
        timer = QTimer()
        timer.timeout.connect(lambda: None)
        timer.start(100)

        # Run event loop
        exit_code = app_instance.exec()
        print(f"📊 Application exited with code: {exit_code}")
        return exit_code

    except Exception as e:
        print(f"❌ Application runtime error: {e}")
        return 1


def handle_startup_error(error_msg):
    """Handle startup errors with user notification"""
    try:
        if app_instance:
            QMessageBox.critical(
                None,
                "DENSO Neural Matrix - Startup Error",
                f"Failed to start application:\n\n{error_msg}\n\nPlease check the logs for details.",
                QMessageBox.StandardButton.Ok,
            )
    except Exception:
        pass

    print(f"💥 CRITICAL ERROR: {error_msg}")


def main():
    """Main application entry point"""
    exit_code = 1
    splash = None

    try:
        print("🚀 Starting DENSO Neural Matrix 2025...")

        # Setup environment
        if not setup_environment():
            handle_startup_error("Environment setup failed")
            return exit_code

        # Create QApplication
        if not create_application():
            handle_startup_error("QApplication creation failed")
            return exit_code

        # Apply modern theme
        try:
            from ui.styles.theme import apply_modern_theme

            apply_modern_theme(app_instance)
            print("✅ Modern theme applied")
        except Exception as e:
            print(f"⚠️ Theme application failed: {e}")

        # Show splash screen
        splash = create_splash_screen()
        if splash:
            QApplication.processEvents()

        # Setup logging
        if not setup_logging():
            handle_startup_error("Logging system failed")
            return exit_code

        # Create controller
        if not create_controller():
            handle_startup_error("Controller creation failed")
            return exit_code

        # Create main window
        if not create_main_window():
            handle_startup_error("Main window creation failed")
            return exit_code

        # Connect UI logging
        connect_ui_logging()

        # Setup signal handlers
        setup_signal_handlers()
        atexit.register(cleanup_application)

        # Hide splash screen
        if splash:
            splash.close()

        # Run application
        exit_code = run_application()

    except KeyboardInterrupt:
        print("\n⚡ Interrupted by user")
        exit_code = 130

    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        handle_startup_error(error_msg)

    finally:
        # Final cleanup
        try:
            if splash:
                splash.close()
            cleanup_application()
        except Exception as e:
            print(f"Final cleanup error: {e}")

    print(f"🏁 Application finished with exit code: {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
