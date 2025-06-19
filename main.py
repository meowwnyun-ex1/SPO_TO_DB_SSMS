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
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
from controller.app_controller import AppController
from utils.logger import setup_logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_app_theme(app):
    """Setup modern dark theme"""
    app.setStyle("Fusion")

    # Dark palette
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(0, 0, 0))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
    app.setPalette(dark_palette)


def main():
    """Application entry point"""
    # Setup logging
    setup_logging()

    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("SharePoint to SQL by เฮียตอม😎")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Thammaphon Chittasuwanna (SDM) | Innovation")

    # Apply theme
    setup_app_theme(app)

    # Initialize controller และ main window
    controller = AppController()
    window = MainWindow(controller)

    # Show window
    window.show()

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
