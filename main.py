#!/usr/bin/env python3
"""
DENSO Neural Matrix - SharePoint to SQL Sync System
© Thammaphon Chittasuwanna (SDM) | Innovation Department
"""

import sys
import atexit
import signal
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

# Add project root to path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Global variables for cleanup
app_instance = None
controller_instance = None
main_window_instance = None
player = None
audio_output = None


def setup_imports():
    """Setup imports with proper error handling"""
    try:
        global MainWindow, AppController, setup_neural_logging
        global apply_ultra_modern_theme, get_config_manager

        from ui.main_window import MainWindow
        from controller.app_controller import AppController
        from utils.logger import setup_neural_logging
        from ui.styles.theme import apply_ultra_modern_theme
        from utils.config_manager import get_config_manager

        return True
    except ImportError as e:
        print(f"CRITICAL IMPORT ERROR: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        return False


def setup_logging():
    """Initialize logging system"""
    try:
        log_dir = project_root / "logs"
        log_dir.mkdir(exist_ok=True)

        ui_handler = setup_neural_logging(
            log_file=str(log_dir / "app.log"), log_level="INFO"
        )

        logger = logging.getLogger(__name__)
        logger.info("Logging system initialized")
        return ui_handler
    except Exception as e:
        print(f"Failed to setup logging: {e}")
        return None


def setup_background_image(main_window):
    """Setup background image for main window"""
    try:
        config_manager = get_config_manager()
        background_path = config_manager.get_setting("background_image_path")

        if background_path:
            full_path = project_root / background_path
            if full_path.exists():
                qt_path = QUrl.fromLocalFile(str(full_path)).toString()
                main_window.setStyleSheet(
                    f"""
                    QMainWindow {{
                        background-image: url("{qt_path}");
                        background-repeat: no-repeat;
                        background-position: center;
                        background-attachment: fixed;
                    }}
                """
                )
                logging.info(f"Background image applied: {full_path}")
            else:
                logging.warning(f"Background image not found: {full_path}")
    except Exception as e:
        logging.error(f"Failed to setup background image: {e}")


def setup_background_audio():
    """Setup background audio if enabled"""
    global player, audio_output

    try:
        config_manager = get_config_manager()

        if not config_manager.get_setting("enable_background_audio"):
            return

        audio_path = config_manager.get_setting("background_audio_path")
        volume = config_manager.get_setting("background_audio_volume")

        if audio_path:
            full_path = project_root / audio_path
            if full_path.exists():
                player = QMediaPlayer()
                audio_output = QAudioOutput()

                player.setAudioOutput(audio_output)
                player.setSource(QUrl.fromLocalFile(str(full_path)))

                audio_output.setVolume(volume)
                player.setLoops(QMediaPlayer.Loops.Infinite)
                player.play()

                logging.info(f"Background audio started: {full_path}")
            else:
                logging.warning(f"Audio file not found: {full_path}")
    except Exception as e:
        logging.error(f"Failed to setup background audio: {e}")


def cleanup_resources():
    """Perform graceful cleanup of application resources"""
    global controller_instance, main_window_instance, player, audio_output

    logging.info("Starting application cleanup...")

    try:
        # Stop background audio
        if player and player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            player.stop()
            player.deleteLater()

        if audio_output:
            audio_output.deleteLater()

        # Cleanup main window
        if main_window_instance:
            main_window_instance.cleanup()
            main_window_instance.deleteLater()

        # Cleanup controller
        if controller_instance:
            controller_instance.cleanup()
            controller_instance.deleteLater()

        logging.info("Application cleanup completed")

    except Exception as e:
        logging.error(f"Error during cleanup: {e}")


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.critical(
        "Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback)
    )

    # Show critical error dialog
    if app_instance:
        QMessageBox.critical(
            None,
            "Critical Error",
            f"An unhandled error occurred:\n{exc_value}\n\nThe application will close.",
            QMessageBox.StandardButton.Ok,
        )

    cleanup_resources()


def handle_signal(signum, frame):
    """Signal handler for graceful shutdown"""
    logging.info(f"Received signal {signum}, shutting down...")
    cleanup_resources()
    if app_instance:
        app_instance.quit()


def create_missing_directories():
    """Create required directories if they don't exist"""
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
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)


def main():
    """Main application entry point"""
    global app_instance, controller_instance, main_window_instance

    # Setup exception handling
    sys.excepthook = handle_exception
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    atexit.register(cleanup_resources)

    exit_code = 1

    try:
        # Check imports
        if not setup_imports():
            return exit_code

        # Create required directories
        create_missing_directories()

        # Setup logging
        ui_handler = setup_logging()

        # Create QApplication
        app_instance = QApplication(sys.argv)
        app_instance.setApplicationName("DENSO Neural Matrix")
        app_instance.setApplicationVersion("1.0.0")

        # Apply theme
        apply_ultra_modern_theme(app_instance)
        logging.info("Ultra Modern Theme applied")

        # Initialize core components
        controller_instance = AppController()
        main_window_instance = MainWindow(controller_instance)

        # Connect UI logging if available
        if ui_handler and hasattr(main_window_instance, "dashboard"):
            ui_handler.log_record_emitted.connect(
                main_window_instance.dashboard.log_console.add_log_message
            )

        # Setup UI enhancements
        setup_background_image(main_window_instance)
        setup_background_audio()

        # Show main window
        main_window_instance.show()

        # Create timer for Qt event processing
        timer = QTimer()
        timer.timeout.connect(lambda: None)
        timer.start(100)

        logging.info("DENSO Neural Matrix started successfully")

        # Run application
        exit_code = app_instance.exec()

    except Exception as e:
        logging.critical(f"Critical error in main: {e}", exc_info=True)
        if app_instance:
            QMessageBox.critical(
                None,
                "Startup Error",
                f"Failed to start application:\n{e}",
                QMessageBox.StandardButton.Ok,
            )
    finally:
        cleanup_resources()
        logging.info(f"Application finished with exit code: {exit_code}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
