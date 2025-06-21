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
ui_handler = None


def setup_imports():
    """Setup imports with proper error handling"""
    try:
        global OptimizedMainWindow, AppController, setup_neural_logging
        global apply_ultra_modern_theme, get_config_manager

        print("Importing main window...")
        from ui.main_window import OptimizedMainWindow

        print("Main window imported successfully")

        print("Importing app controller...")
        from controller.app_controller import AppController

        print("App controller imported successfully")

        print("Importing utilities...")
        from utils.logger import setup_neural_logging
        from ui.styles.theme import apply_ultra_modern_theme
        from utils.config_manager import get_config_manager

        print("All utilities imported successfully")

        return True
    except ImportError as e:
        print(f"CRITICAL IMPORT ERROR: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        return False


def setup_logging():
    """Initialize logging system"""
    global ui_handler
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


def create_main_window_with_timeout():
    """Create main window with timeout protection"""
    global main_window_instance, controller_instance

    try:
        print("Creating MainWindow with timeout protection...")

        # Set a timeout for window creation
        creation_timer = QTimer()
        creation_timer.setSingleShot(True)
        creation_completed = False

        def on_timeout():
            nonlocal creation_completed
            if not creation_completed:
                print("MainWindow creation timed out!")
                logging.error("MainWindow creation timed out after 10 seconds")
                raise TimeoutError("MainWindow creation timed out")

        creation_timer.timeout.connect(on_timeout)
        creation_timer.start(10000)  # 10 second timeout

        # Create the main window
        print("Instantiating OptimizedMainWindow...")
        try:
            main_window_instance = OptimizedMainWindow(controller_instance)
            creation_completed = True
            creation_timer.stop()
        except Exception as e:
            print(f"OptimizedMainWindow failed: {e}")
            # Create minimal working window
            from PyQt6.QtWidgets import (
                QMainWindow,
                QWidget,
                QVBoxLayout,
                QTextEdit,
                QPushButton,
            )

            main_window_instance = QMainWindow()
            central = QWidget()
            layout = QVBoxLayout(central)

            # Simple UI
            layout.addWidget(QLabel("DENSO Neural Matrix - Minimal Mode"))

            log_area = QTextEdit()
            log_area.setReadOnly(True)
            layout.addWidget(log_area)

            # Connect controller logs
            if hasattr(controller_instance, "log_message"):
                controller_instance.log_message.connect(
                    lambda msg, level: log_area.append(f"[{level}] {msg}")
                )

            test_btn = QPushButton("Test Connections")
            test_btn.clicked.connect(
                lambda: (
                    controller_instance.test_all_connections()
                    if hasattr(controller_instance, "test_all_connections")
                    else None
                )
            )
            layout.addWidget(test_btn)

            main_window_instance.setCentralWidget(central)
            main_window_instance.setWindowTitle("DENSO Neural Matrix - Safe Mode")
            main_window_instance.setGeometry(100, 100, 600, 400)

            creation_completed = True
            creation_timer.stop()

        print("MainWindow created successfully")
        return True

    except Exception as e:
        print(f"Error creating MainWindow: {e}")
        logging.error(f"Error creating MainWindow: {e}")
        return False


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
    global controller_instance, main_window_instance, player, audio_output, ui_handler

    print("Starting application cleanup...")
    logging.info("Starting application cleanup...")

    try:
        # Stop background audio
        if player and player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            player.stop()
            if hasattr(player, "deleteLater"):
                player.deleteLater()

        if audio_output and hasattr(audio_output, "deleteLater"):
            audio_output.deleteLater()

        # Cleanup main window
        if main_window_instance:
            try:
                main_window_instance.cleanup()
                if hasattr(main_window_instance, "deleteLater"):
                    main_window_instance.deleteLater()
            except Exception as e:
                print(f"Error cleaning up main window: {e}")

        # Cleanup controller
        if controller_instance:
            try:
                controller_instance.cleanup()
                if hasattr(controller_instance, "deleteLater"):
                    controller_instance.deleteLater()
            except Exception as e:
                print(f"Error cleaning up controller: {e}")

        # Cleanup UI handler
        if ui_handler:
            try:
                if hasattr(ui_handler, "log_record_emitted"):
                    ui_handler.log_record_emitted.disconnect()
                if hasattr(ui_handler, "deleteLater"):
                    ui_handler.deleteLater()
            except Exception as e:
                print(f"Error cleaning up UI handler: {e}")

        print("Application cleanup completed")
        logging.info("Application cleanup completed")

    except Exception as e:
        print(f"Error during cleanup: {e}")
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
        try:
            QMessageBox.critical(
                None,
                "Critical Error",
                f"An unhandled error occurred:\n{exc_value}\n\nThe application will close.",
                QMessageBox.StandardButton.Ok,
            )
        except:
            pass

    cleanup_resources()


def handle_signal(signum, frame):
    """Signal handler for graceful shutdown"""
    print(f"Received signal {signum}, shutting down...")
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
        print("Starting DENSO Neural Matrix...")

        # Check imports
        if not setup_imports():
            return exit_code

        print("Imports successful...")

        # Create required directories
        create_missing_directories()

        # Setup logging
        ui_handler = setup_logging()
        print("Logging setup complete...")

        # Create QApplication
        app_instance = QApplication(sys.argv)
        app_instance.setApplicationName("DENSO Neural Matrix")
        app_instance.setApplicationVersion("1.0.0")
        print("QApplication created...")

        # Apply theme
        apply_ultra_modern_theme(app_instance)
        logging.info("Ultra Modern Theme applied")
        print("Theme applied...")

        # Initialize core components
        print("Creating AppController...")
        controller_instance = AppController()
        print("AppController created successfully")

        # Create MainWindow with timeout protection
        print("Creating MainWindow...")
        if not create_main_window_with_timeout():
            print("Failed to create MainWindow - switching to minimal mode")
            # Create a minimal fallback window
            from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget

            main_window_instance = QMainWindow()
            central_widget = QWidget()
            layout = QVBoxLayout(central_widget)
            label = QLabel(
                "DENSO Neural Matrix - Minimal Mode\n\nMain UI failed to load."
            )
            layout.addWidget(label)
            main_window_instance.setCentralWidget(central_widget)
            main_window_instance.setWindowTitle("DENSO Neural Matrix - Minimal")
            main_window_instance.setGeometry(100, 100, 400, 200)

        print("MainWindow created successfully")

        # Connect UI logging if available
        if ui_handler and hasattr(main_window_instance, "log_panel"):
            try:
                ui_handler.log_record_emitted.connect(
                    main_window_instance.log_panel.log_console.add_log_message
                )
                print("UI logging connected...")
            except Exception as e:
                print(f"UI logging connection failed: {e}")

        # Setup UI enhancements (skip if in minimal mode)
        if hasattr(main_window_instance, "config_manager"):
            setup_background_image(main_window_instance)
            setup_background_audio()

        # Show main window
        print("Showing main window...")
        main_window_instance.show()
        print("Main window should be visible now")

        # Create timer for Qt event processing
        timer = QTimer()
        timer.timeout.connect(lambda: None)
        timer.start(100)

        logging.info("DENSO Neural Matrix started successfully")
        print("Application started successfully - entering event loop...")

        # Run application
        exit_code = app_instance.exec()
        print(f"Application exited with code: {exit_code}")

    except Exception as e:
        print(f"Critical error in main: {e}")
        logging.critical(f"Critical error in main: {e}", exc_info=True)
        if app_instance:
            try:
                QMessageBox.critical(
                    None,
                    "Startup Error",
                    f"Failed to start application:\n{e}",
                    QMessageBox.StandardButton.Ok,
                )
            except:
                pass
    finally:
        cleanup_resources()
        try:
            logging.info(f"Application finished with exit code: {exit_code}")
        except:
            pass

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
