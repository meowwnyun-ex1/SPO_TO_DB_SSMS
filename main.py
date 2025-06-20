#!/usr/bin/env python3
"""
DENSO Neural Matrix - SharePoint to SQL Sync System
© Thammaphon Chittasuwanna (SDM) | Innovation Department
"""

import sys
import os
import atexit
import signal
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

# Add project root to path
# This ensures absolute imports work correctly regardless of execution context
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Attempt to import core components with fallbacks for robustness
try:
    from ui.main_window import MainWindow
    from controller.app_controller import AppController
    from utils.logger import setup_neural_logging
    from ui.styles.theme import apply_ultra_modern_theme, UltraModernColors
    from utils.config_manager import ConfigManager
except ImportError as e:
    print(
        f"CRITICAL IMPORT ERROR: {e}. Please ensure all dependencies are installed and project structure is correct."
    )
    sys.exit(1)  # Exit if essential components cannot be imported

# Configure logging early
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_background_image(main_window):
    """
    Sets up the background image for the main window based on config.
    Applies it as a stylesheet to the central widget or main window.
    """
    config_manager = ConfigManager()
    background_image_path = config_manager.get_setting("background_image_path")

    if background_image_path:
        # Use Pathlib for robust path handling
        full_path = Path(project_root) / background_image_path
        if full_path.exists():
            try:
                # Set background using stylesheet for better resizing and layering
                # We need to make sure main_window.central_widget exists and is accessible
                # Or apply directly to main_window if no specific central widget handles it
                # For simplicity, we apply to the main_window itself.
                # Ensure the path uses forward slashes for Qt stylesheet compatibility
                qt_path = (
                    QUrl.fromLocalFile(str(full_path)).toLocalFile().replace("\\", "/")
                )

                # The background will stretch to fill the window and be behind other widgets
                main_window.setStyleSheet(
                    f"""
                    QMainWindow {{
                        background-image: url("{qt_path}");
                        background-repeat: no-repeat;
                        background-position: center;
                        background-size: cover; /* This makes the image cover the entire window */
                    }}
                """
                )
                logger.info(f"Background image applied from: {full_path}")
            except Exception as e:
                logger.error(f"Error setting up background image: {e}")
        else:
            logger.warning(f"Background image file not found: {full_path}")
    else:
        logger.info("No background image path configured.")


def setup_background_audio():
    """
    Sets up background audio based on config.
    """
    config_manager = ConfigManager()
    enable_audio = config_manager.get_setting("enable_background_audio")
    audio_path = config_manager.get_setting("background_audio_path")
    audio_volume = config_manager.get_setting("background_audio_volume")

    if enable_audio and audio_path:
        full_path = os.path.join(project_root, audio_path)
        if os.path.exists(full_path):
            try:
                global player, audio_output  # Keep references to prevent garbage collection
                player = QMediaPlayer()
                audio_output = QAudioOutput()
                player.setAudioOutput(audio_output)

                media_content = QUrl.fromLocalFile(full_path)
                player.setSource(media_content)

                audio_output.setVolume(audio_volume)
                player.setLoops(-1)  # Loop indefinitely
                player.play()
                logger.info(f"Background audio started from: {full_path}")
            except Exception as e:
                logger.error(f"Error setting up background audio: {e}")
        else:
            logger.warning(f"Background audio file not found: {full_path}")
    else:
        logger.info("Background audio disabled or not configured.")


def cleanup_resources():
    """
    Performs graceful cleanup of application resources.
    """
    logger.info("Initiating application resource cleanup...")
    try:
        if "controller_instance" in globals() and controller_instance:
            controller_instance.cleanup()
            logger.info("AppController cleanup requested.")

        if "main_window_instance" in globals() and main_window_instance:
            main_window_instance.cleanup()  # Call cleanup method on MainWindow
            logger.info("MainWindow cleanup requested.")

        if (
            "player" in globals()
            and player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
        ):
            player.stop()
            player.deleteLater()
            audio_output.deleteLater()
            logger.info("Background audio stopped and cleaned up.")

    except Exception as e:
        logger.critical(f"Error during cleanup_resources: {e}", exc_info=True)


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    Global exception handler.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical(
        "Unhandled exception caught by global handler",
        exc_info=(exc_type, exc_value, exc_traceback),
    )
    cleanup_resources()
    # Optionally, display a message box for critical errors
    # QMessageBox.critical(None, "Critical Error", "An unhandled critical error occurred. The application will close.")


def handle_signal(signum, frame):
    """
    Signal handler for graceful shutdown (e.g., Ctrl+C).
    """
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    cleanup_resources()
    QApplication.quit()


if __name__ == "__main__":
    sys.excepthook = handle_exception
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    atexit.register(cleanup_resources)

    logger.info("Starting DENSO Neural Matrix Application...")

    app_instance = None
    exit_code = 0

    try:
        app_instance = QApplication(sys.argv)
        app_instance.setApplicationName("DENSO Neural Matrix")
        app_instance.setApplicationVersion(ConfigManager().get_setting("app_version"))

        apply_ultra_modern_theme(app_instance)
        logger.info("Ultra Modern Theme applied.")

        controller_instance = AppController()
        main_window_instance = MainWindow(controller_instance)

        # Apply background image via stylesheet directly to main_window_instance
        setup_background_image(main_window_instance)

        setup_background_audio()

        main_window_instance.show()

        timer = QTimer()
        timer.timeout.connect(lambda: None)
        timer.start(100)

        exit_code = app_instance.exec()

    except Exception as e:
        logger.critical(
            f"Unhandled critical error in main application loop: {e}", exc_info=True
        )
        cleanup_resources()
        exit_code = 1

    finally:
        logger.info(f"Application finished with exit code: {exit_code}")
