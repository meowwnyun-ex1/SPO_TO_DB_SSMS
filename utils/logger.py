import logging
import logging.handlers
from pathlib import Path


def setup_logging(log_level="INFO", log_dir="logs"):
    """Setup application logging"""

    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # Configure log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    simple_formatter = logging.Formatter("%(levelname)s: %(message)s")

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # File handler - detailed logs
    file_handler = logging.handlers.RotatingFileHandler(
        log_path / "sharepoint_sync.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)

    # Error file handler - errors only
    error_handler = logging.handlers.RotatingFileHandler(
        log_path / "errors.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)

    # Console handler - for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)

    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - Level: {log_level}")
    logger.info(f"Log directory: {log_path.absolute()}")

    return root_logger


def get_logger(name):
    """Get a logger for a specific module"""
    return logging.getLogger(name)


class UILogHandler(logging.Handler):
    """Custom log handler for UI display"""

    def __init__(self, callback=None):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        if self.callback:
            msg = self.format(record)
            level = record.levelname.lower()

            # Map log levels to UI levels
            level_map = {
                "debug": "info",
                "info": "info",
                "warning": "warning",
                "error": "error",
                "critical": "error",
            }

            ui_level = level_map.get(level, "info")
            self.callback(msg, ui_level)
