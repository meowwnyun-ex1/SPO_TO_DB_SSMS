"""
SharePoint to SQL Sync by เฮียตอม😎
© 2025 Thammaphon Chittasuwanna (SDM) | Innovation Department
"""

import sys
import os
import atexit
import signal
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPalette, QColor

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
from controller.app_controller import AppController
from utils.logger import setup_neural_logging
from ui.styles.theme import apply_ultra_modern_theme, UltraModernColors

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global references for cleanup
app_instance = None
main_window_instance = None
controller_instance = None
cleanup_in_progress = False


def cleanup_resources():
    """แก้บัค: ทำความสะอาดทรัพยากรโดยป้องกัน double cleanup"""
    global cleanup_in_progress

    if cleanup_in_progress:
        return

    cleanup_in_progress = True

    try:
        if controller_instance and hasattr(controller_instance, "cleanup"):
            controller_instance.cleanup()

        if main_window_instance and not main_window_instance.cleanup_done:
            main_window_instance._safe_cleanup()

        logger.info("🧹 Resources cleaned up successfully")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


def signal_handler(signum, frame):
    """จัดการ signal เมื่อถูกบังคับปิด"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    cleanup_resources()
    if app_instance:
        app_instance.quit()
    sys.exit(0)


def setup_app_theme(app):
    """Setup modern dark theme"""
    app.setStyle("Fusion")

    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(20, 20, 20))
    dark_palette.setColor(
        QPalette.ColorRole.WindowText, QColor(UltraModernColors.TEXT_PRIMARY)
    )
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(40, 40, 40))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(0, 0, 0))
    dark_palette.setColor(
        QPalette.ColorRole.ToolTipText, QColor(UltraModernColors.TEXT_PRIMARY)
    )
    dark_palette.setColor(
        QPalette.ColorRole.Text, QColor(UltraModernColors.TEXT_PRIMARY)
    )
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(50, 50, 50))
    dark_palette.setColor(
        QPalette.ColorRole.ButtonText, QColor(UltraModernColors.TEXT_PRIMARY)
    )
    dark_palette.setColor(
        QPalette.ColorRole.BrightText, QColor(UltraModernColors.NEON_PINK)
    )
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(UltraModernColors.NEON_BLUE))
    dark_palette.setColor(
        QPalette.ColorRole.Highlight, QColor(UltraModernColors.NEON_PURPLE)
    )
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))

    app.setPalette(dark_palette)
    apply_ultra_modern_theme(app)


def setup_background_image(main_window):
    """ตั้งค่ารูปพื้นหลัง"""
    # ลองหาไฟล์รูพื้นหลังในหลายรูปแบบ
    background_files = [
        "assets/background.jpg",
        "assets/background.png",
        "assets/bg.jpg",
        "assets/bg.png",
        "background.jpg",
        "background.png",
    ]

    background_path = None
    project_root = os.path.dirname(os.path.abspath(__file__))

    for bg_file in background_files:
        full_path = os.path.join(project_root, bg_file)
        if os.path.exists(full_path):
            background_path = full_path
            logger.info(f"Found background image: {bg_file}")
            break

    if background_path:
        # แปลง path เป็น format ที่ Qt รองรับ
        bg_path_qt = background_path.replace(os.sep, "/")

        main_window.setStyleSheet(
            f"""
            QMainWindow {{
                background-image: url('{bg_path_qt}');
                background-repeat: no-repeat;
                background-position: center;
                border: 2px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 15px;
            }}
            {main_window.styleSheet()}
            """
        )
        main_window.setAutoFillBackground(True)
        logger.info(f"Background image set: {background_path}")
    else:
        # ถ้าไม่มีรูป ใช้ gradient
        logger.warning("Background image not found, using gradient")
        main_window.setStyleSheet(
            f"""
            QMainWindow {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a,
                    stop:0.3 #1a0a1a,
                    stop:0.7 #0a1a1a,
                    stop:1 #0a0a0a
                );
                border: 2px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 15px;
            }}
            {main_window.styleSheet()}
            """
        )


def main():
    """Application entry point แก้บัค cleanup"""
    global app_instance, main_window_instance, controller_instance

    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Register cleanup function
    atexit.register(cleanup_resources)

    try:
        # Setup logging early
        setup_neural_logging()

        app_instance = QApplication(sys.argv)
        app_instance.setQuitOnLastWindowClosed(True)

        setup_app_theme(app_instance)

        # Initialize controller before main window
        controller_instance = AppController()
        main_window_instance = MainWindow(controller_instance)

        # ตั้งค่ารูปพื้นหลัง
        setup_background_image(main_window_instance)

        main_window_instance.show()

        # Timer เพื่อให้แอปตอบสนอง signal ได้ดี
        timer = QTimer()
        timer.timeout.connect(lambda: None)
        timer.start(100)

        exit_code = app_instance.exec()

    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        exit_code = 1
    finally:
        if not cleanup_in_progress:
            cleanup_resources()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
