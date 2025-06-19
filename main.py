"""
SharePoint to SQL Sync by เฮียตอม😎
© 2025 Thammaphon Chittasuwanna (SDM) | Innovation Department
"""

import sys
import os
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor

# Add project root to path
# เพิ่ม path ของ root project เพื่อให้ import โมดูลอื่นๆ ได้
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
from controller.app_controller import AppController
from utils.logger import setup_logging
from ui.styles.theme import (
    apply_ultra_modern_theme,
    UltraModernColors,
)  # Import UltraModernColors

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_app_theme(app):
    """
    Setup modern dark theme with the new color palette and apply global styles.
    ตั้งค่าธีมสมัยใหม่โทนเข้มพร้อมพาเลทสีใหม่และใช้สไตล์ทั่วทั้งแอปพลิเคชัน
    """
    app.setStyle("Fusion")

    # Dark palette - Adjusted for white, purple, black theme
    # พาเลทสีเข้ม - ปรับสำหรับธีมขาว ม่วง ดำ
    dark_palette = QPalette()
    dark_palette.setColor(
        QPalette.ColorRole.Window, QColor(20, 20, 20)
    )  # Dark background for areas not covered by image
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
    )  # Use neon pink for bright text
    dark_palette.setColor(
        QPalette.ColorRole.Link, QColor(UltraModernColors.NEON_BLUE)
    )  # Use neon blue for links
    dark_palette.setColor(
        QPalette.ColorRole.Highlight, QColor(UltraModernColors.NEON_PURPLE)
    )  # Use neon purple for highlights
    dark_palette.setColor(
        QPalette.ColorRole.HighlightedText, QColor(0, 0, 0)
    )  # Black text on highlight

    app.setPalette(dark_palette)

    # Apply global styles defined in theme.py
    # ใช้สไตล์ทั่วทั้งแอปพลิเคชันที่กำหนดไว้ใน theme.py
    apply_ultra_modern_theme(app)


def main():
    """Application entry point"""
    # Setup logging early
    # ตั้งค่าการบันทึกข้อมูลตั้งแต่เริ่มต้น
    setup_logging()

    app = QApplication(sys.argv)
    setup_app_theme(app)

    # Set initial window size (e.g., 1280x720 for 16:9 aspect ratio, smaller than 1920x1080)
    # ตั้งค่าขนาดเริ่มต้นของหน้าต่าง (เช่น 1280x720 สำหรับอัตราส่วน 16:9 ซึ่งเล็กกว่า 1920x1080)
    initial_width = 1280
    initial_height = 720
    screen_rect = app.primaryScreen().availableGeometry()
    x = (screen_rect.width() - initial_width) // 2
    y = (screen_rect.height() - initial_height) // 2

    # Initialize controller before main window
    # เริ่มต้น Controller ก่อน MainWindow
    controller = AppController()

    main_window = MainWindow(controller)
    main_window.setGeometry(
        x, y, initial_width, initial_height
    )  # Set initial position and size

    # Set background image for QMainWindow
    # ตั้งค่ารูปภาพพื้นหลังสำหรับ QMainWindow
    background_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "assets", "background.jpg"
    )
    if os.path.exists(background_path):
        # Using QPalette for background image with scaling and proper tiling
        # ใช้ QPalette สำหรับรูปภาพพื้นหลังพร้อมการปรับขนาดและการจัดเรียงที่เหมาะสม
        # Note: QMainWindow's background can also be set via stylesheet with `background-image: url(...)`
        # but QPalette offers more control over scaling/tiling directly.
        # สำหรับการปรับขนาดและวางภาพให้เต็มพื้นที่ ให้ใช้ stylesheet แทนได้ถ้าต้องการควบคุมด้วย CSS
        # หรือถ้าใช้ QPalette ต้อง setAutoFillBackground(True) ใน MainWindow ด้วย

        # Using stylesheet for background image as it's more flexible with dynamic resizing
        main_window.setStyleSheet(
            f"""
            QMainWindow {{
                background-image: url('{background_path.replace(os.sep, "/")}');
                background-repeat: no-repeat;
                background-position: center;
                background-attachment: fixed; /* Ensures background stays fixed during scroll, though we aim for no scroll */
                background-size: cover; /* This will scale the image to cover the entire window */
                border: 1px solid {UltraModernColors.NEON_PURPLE}; /* Add a subtle border */
                border-radius: 15px; /* Optional: rounded corners for the main window */
            }}
            {main_window.styleSheet()}
        """
        )
        main_window.setAutoFillBackground(
            True
        )  # Important for background to show correctly with QPalette/setStyleSheet
    else:
        logger.warning(
            f"Background image not found at: {background_path}. Using solid color background."
        )
        # Fallback to a solid color if image is not found, adjusted for new theme
        main_window.setStyleSheet(
            f"""
            QMainWindow {{
                background-color: #1a1a1a; /* Dark background */
                border: 1px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 15px;
            }}
            {main_window.styleSheet()}
        """
        )

    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
