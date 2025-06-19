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


def cleanup_resources():
    """ทำความสะอาดทรัพยากรก่อนปิดโปรแกรม"""
    try:
        if controller_instance:
            controller_instance.cleanup()
        if main_window_instance:
            main_window_instance.close()
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
    """Setup modern dark theme with the new color palette"""
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


def main():
    """Application entry point with proper cleanup"""
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
        app_instance.setQuitOnLastWindowClosed(True)  # ให้แอปปิดเมื่อหน้าต่างสุดท้ายปิด

        setup_app_theme(app_instance)

        # Set initial window size
        initial_width = 1280
        initial_height = 720
        screen_rect = app_instance.primaryScreen().availableGeometry()
        x = (screen_rect.width() - initial_width) // 2
        y = (screen_rect.height() - initial_height) // 2

        # Initialize controller before main window
        controller_instance = AppController()

        main_window_instance = MainWindow(controller_instance)
        main_window_instance.setGeometry(x, y, initial_width, initial_height)

        # Set background image
        background_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "assets", "background.jpg"
        )
        if os.path.exists(background_path):
            main_window_instance.setStyleSheet(
                f"""
                QMainWindow {{
                    background-image: url('{background_path.replace(os.sep, "/")}');
                    background-repeat: no-repeat;
                    background-position: center;
                    background-attachment: fixed;
                    background-size: cover;
                    border: 1px solid {UltraModernColors.NEON_PURPLE};
                    border-radius: 15px;
                }}
                {main_window_instance.styleSheet()}
            """
            )
            main_window_instance.setAutoFillBackground(True)
        else:
            logger.warning(f"Background image not found at: {background_path}")
            main_window_instance.setStyleSheet(
                f"""
                QMainWindow {{
                    background-color: #1a1a1a;
                    border: 1px solid {UltraModernColors.NEON_PURPLE};
                    border-radius: 15px;
                }}
                {main_window_instance.styleSheet()}
            """
            )

        main_window_instance.show()

        # เพิ่ม timer เพื่อให้แอปตอบสนอง signal ได้ดีขึ้น
        timer = QTimer()
        timer.timeout.connect(lambda: None)
        timer.start(100)

        exit_code = app_instance.exec()

    except Exception as e:
        logger.error(f"Critical error in main: {e}")
        exit_code = 1
    finally:
        cleanup_resources()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
