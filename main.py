"""
SharePoint to SQL Sync by เฮียตอม😎
© 2025 Thammaphon Chittasuwanna (SDM) | Innovation Department
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
from core.app_controller import AppController
from utils.logger import setup_logging


def setup_app_theme(app):
    """Setup modern dark theme"""
    app.setStyle("Fusion")

    # Dark palette
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
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
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
