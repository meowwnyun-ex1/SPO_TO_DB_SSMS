"""
◈ SharePoint to SQL Neural Matrix by เฮียตอม😎 ◈
© 2025 Thammaphon Chittasuwanna (SDM) | Innovation Department

Ultra Modern Holographic Interface with Quantum Data Synchronization
Neural Network Architecture for Enterprise Data Management
"""

import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt6.QtGui import QPalette, QColor, QPixmap, QPainter, QFont, QLinearGradient
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import UltraModernMainWindow
from core.app_controller import AppController
from utils.logger import setup_logging
from ui.styles.theme import UltraModernColors


class NeuralInitializationThread(QThread):
    """Background thread สำหรับ initialize neural systems"""

    progress_updated = pyqtSignal(str, int)
    initialization_completed = pyqtSignal(object)
    initialization_failed = pyqtSignal(str)

    def run(self):
        """Initialize neural matrix components"""
        try:
            # Phase 1: Neural Network Initialization
            self.progress_updated.emit("◈ Initializing Neural Network Core...", 20)
            self.msleep(300)

            # Phase 2: Quantum Controller Setup
            self.progress_updated.emit("◎ Loading Quantum Controller Matrix...", 40)
            controller = AppController()
            self.msleep(400)

            # Phase 3: Holographic Interface Preparation
            self.progress_updated.emit("⬢ Preparing Holographic Interface...", 60)
            self.msleep(300)

            # Phase 4: Neural Pathways Optimization
            self.progress_updated.emit("◉ Optimizing Neural Pathways...", 80)
            self.msleep(200)

            # Phase 5: Matrix Synchronization
            self.progress_updated.emit("◦ Neural Matrix Ready ◦", 100)
            self.msleep(200)

            self.initialization_completed.emit(controller)

        except Exception as e:
            error_msg = f"Neural initialization failed: {str(e)}"
            self.initialization_failed.emit(error_msg)


class HolographicSplashScreen(QSplashScreen):
    """Splash screen แบบ holographic พร้อม neural loading effects"""

    def __init__(self):
        # สร้าง holographic background
        pixmap = self.create_holographic_background()
        super().__init__(pixmap)

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | Qt.SplashScreen | Qt.FramelessWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Setup neural loading animation
        self.loading_symbols = ["◈", "◉", "◎", "⬢", "◆", "◇", "⬡", "⬟"]
        self.symbol_index = 0

        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_neural_symbol)
        self.animation_timer.start(150)

    def create_holographic_background(self):
        """สร้าง holographic background สำหรับ splash screen"""
        width, height = 600, 400
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Holographic gradient background
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0.0, QColor(20, 30, 48, 200))
        gradient.setColorAt(0.3, QColor(0, 212, 255, 80))
        gradient.setColorAt(0.7, QColor(189, 94, 255, 80))
        gradient.setColorAt(1.0, QColor(20, 30, 48, 200))

        painter.fillRect(0, 0, width, height, gradient)

        # Neural network grid pattern
        painter.setPen(QColor(0, 212, 255, 30))
        grid_size = 40
        for x in range(0, width, grid_size):
            painter.drawLine(x, 0, x, height)
        for y in range(0, height, grid_size):
            painter.drawLine(0, y, width, y)

        # Central holographic frame
        frame_rect = pixmap.rect().adjusted(40, 40, -40, -40)
        painter.setPen(QColor(0, 212, 255, 150))
        painter.drawRoundedRect(frame_rect, 20, 20)

        # Neon glow effect
        for i in range(3):
            painter.setPen(QColor(0, 212, 255, 50 - i * 15))
            painter.drawRoundedRect(frame_rect.adjusted(-i, -i, i, i), 20 + i, 20 + i)

        # Title text
        painter.setPen(QColor(255, 255, 255, 255))
        painter.setFont(QFont("Inter", 24, QFont.Bold))
        title_rect = pixmap.rect().adjusted(0, 80, 0, -200)
        painter.drawText(title_rect, Qt.AlignCenter, "◈ Neural Matrix Initialization ◈")

        # Subtitle
        painter.setFont(QFont("Inter", 14, QFont.Medium))
        painter.setPen(QColor(0, 212, 255, 200))
        subtitle_rect = pixmap.rect().adjusted(0, 130, 0, -150)
        painter.drawText(
            subtitle_rect, Qt.AlignCenter, "SharePoint to SQL Quantum Sync System"
        )

        # Credit line
        painter.setFont(QFont("Inter", 10))
        painter.setPen(QColor(255, 255, 255, 150))
        credit_rect = pixmap.rect().adjusted(0, 300, 0, -50)
        painter.drawText(
            credit_rect, Qt.AlignCenter, "Powered by เฮียตอม😎 | Innovation Department"
        )

        painter.end()
        return pixmap

    def animate_neural_symbol(self):
        """Animate neural loading symbol"""
        self.symbol_index = (self.symbol_index + 1) % len(self.loading_symbols)

    def show_neural_message(self, message, progress=0):
        """แสดงข้อความแบบ neural พร้อม progress"""
        neural_symbol = self.loading_symbols[self.symbol_index]

        # Enhanced message with neural styling
        neural_message = f"{neural_symbol} {message}"

        if progress > 0:
            neural_message += f" [{progress}%]"

        # แสดงข้อความด้วยสี neon
        self.showMessage(
            neural_message,
            Qt.AlignCenter | Qt.AlignBottom,
            QColor(0, 255, 255),  # Cyan neon color
        )

    def finish_neural_loading(self):
        """เสร็จสิ้นการโหลด neural matrix"""
        self.animation_timer.stop()
        self.show_neural_message("◎ Neural Matrix Online ◎", 100)


def setup_ultra_modern_app_theme(app):
    """ตั้งค่า ultra modern theme สำหรับ application"""
    app.setStyle("Fusion")

    # Ultra modern dark palette พร้อม holographic accents
    dark_palette = QPalette()

    # Base colors
    dark_palette.setColor(QPalette.Window, QColor(26, 32, 44))
    dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Base, QColor(15, 20, 26))
    dark_palette.setColor(QPalette.AlternateBase, QColor(45, 55, 72))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Button, QColor(45, 55, 72))
    dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.BrightText, QColor(0, 212, 255))
    dark_palette.setColor(QPalette.Link, QColor(0, 212, 255))
    dark_palette.setColor(QPalette.Highlight, QColor(0, 212, 255))
    dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))

    # Disabled colors
    dark_palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))

    app.setPalette(dark_palette)

    # Global application stylesheet
    app.setStyleSheet(
        f"""
        QApplication {{
            background: {UltraModernColors.NEURAL_GRADIENT};
        }}
        QToolTip {{
            background: rgba(0, 212, 255, 0.9);
            color: white;
            border: 1px solid rgba(0, 212, 255, 0.5);
            border-radius: 8px;
            padding: 8px;
            font-family: 'Inter', 'Segoe UI', sans-serif;
            font-size: 12px;
            font-weight: 500;
        }}
        QMessageBox {{
            background: rgba(26, 32, 44, 0.95);
            backdrop-filter: blur(15px);
        }}
    """
    )


def handle_neural_exception(exc_type, exc_value, exc_traceback):
    """จัดการ exception แบบ neural system"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # Log neural system error
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

    # Create neural error dialog
    app = QApplication.instance()
    if app:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("◆ Neural Matrix Critical Error")
        msg_box.setText(
            "◆ Fatal neural network disruption detected\n\n"
            "The neural matrix has encountered a critical error and needs to restart.\n"
            "All data will be preserved in the quantum backup systems."
        )
        msg_box.setDetailedText(error_msg)
        msg_box.setStandardButtons(QMessageBox.Ok)

        # Apply neural styling
        msg_box.setStyleSheet(
            f"""
            QMessageBox {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 7, 58, 0.1),
                    stop:1 rgba(20, 30, 48, 0.9)
                );
                color: {UltraModernColors.TEXT_LUMINOUS};
                border: 2px solid rgba(255, 7, 58, 0.5);
                border-radius: 16px;
            }}
            QMessageBox QPushButton {{
                background: {UltraModernColors.ERROR_GLOW};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 13px;
            }}
        """
        )

        msg_box.exec_()


def initialize_neural_environment():
    """Initialize neural computing environment"""
    # Setup neural logging system
    try:
        setup_logging("INFO", "logs")
        print("◉ Neural logging system initialized")
    except Exception as e:
        print(f"◆ Warning: Could not initialize logging: {e}")

    # Setup neural exception handling
    sys.excepthook = handle_neural_exception
    print("◎ Neural exception handler activated")

    # Optimize neural performance
    if hasattr(sys, "setrecursionlimit"):
        sys.setrecursionlimit(5000)

    print("⬢ Neural environment optimization complete")


def main():
    """Neural Matrix Application Entry Point"""
    print("=" * 60)
    print("◈ SharePoint to SQL Neural Matrix v2.0")
    print("◦ Ultra Modern Holographic Interface")
    print("◦ Quantum Data Synchronization Engine")
    print("◦ Powered by เฮียตอม😎 | Innovation Department")
    print("=" * 60)

    # Initialize neural environment
    initialize_neural_environment()

    # Create QApplication with neural optimization
    app = QApplication(sys.argv)
    app.setApplicationName("SharePoint to SQL Neural Matrix by เฮียตอม😎")
    app.setApplicationVersion("2.0 - Holographic Edition")
    app.setOrganizationName("Thammaphon Chittasuwanna (SDM) | Innovation Department")
    app.setOrganizationDomain("neural-matrix.innovation.local")

    # Apply ultra modern theme
    setup_ultra_modern_app_theme(app)

    try:
        # Show holographic splash screen
        splash = HolographicSplashScreen()
        splash.show()
        app.processEvents()

        # Initialize neural components in background
        init_thread = NeuralInitializationThread()
        controller = None
        main_window = None

        def on_progress_update(message, progress):
            splash.show_neural_message(message, progress)
            app.processEvents()

        def on_initialization_complete(ctrl):
            nonlocal controller, main_window
            controller = ctrl

            # Create main neural interface
            splash.show_neural_message("◈ Launching Holographic Interface...", 100)
            app.processEvents()

            main_window = UltraModernMainWindow(controller)

            # Finish splash and show main window
            splash.finish_neural_loading()
            QTimer.singleShot(
                800, lambda: [splash.finish(main_window), main_window.show()]
            )

        def on_initialization_failed(error_msg):
            splash.hide()

            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("◆ Neural Matrix Initialization Failed")
            msg_box.setText(
                "◆ Failed to initialize neural matrix\n\n"
                "The neural network could not be established.\n"
                "Please check system requirements and try again."
            )
            msg_box.setDetailedText(error_msg)
            msg_box.exec_()

            sys.exit(1)

        # Connect neural initialization signals
        init_thread.progress_updated.connect(on_progress_update)
        init_thread.initialization_completed.connect(on_initialization_complete)
        init_thread.initialization_failed.connect(on_initialization_failed)

        # Start neural initialization
        init_thread.start()

        print("◉ Neural matrix startup sequence initiated")
        print("◦ Holographic interface loading...")

        # Start quantum event loop
        exit_code = app.exec_()

        print("◎ Neural matrix shutdown complete")
        print("◦ Quantum systems offline")
        print("◦ Thank you for using Neural Matrix v2.0")

        sys.exit(exit_code)

    except Exception as e:
        print(f"◆ Critical neural matrix failure: {e}")

        # Show emergency error dialog
        if "app" in locals():
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("◆ Critical Neural Matrix Failure")
            msg_box.setText(
                "◆ Catastrophic neural network failure\n\n"
                "The neural matrix has suffered a critical system failure.\n"
                "Emergency shutdown protocols have been activated."
            )
            msg_box.setDetailedText(str(e))
            msg_box.exec_()

        sys.exit(1)


if __name__ == "__main__":
    main()
