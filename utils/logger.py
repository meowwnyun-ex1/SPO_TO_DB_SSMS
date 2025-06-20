import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal


# This QObject class can be used to emit log messages to the UI thread
class NeuraUILogHandler(QObject, logging.Handler):
    """
    A custom logging handler that emits log records as signals,
    allowing PyQt UI elements to display them in real-time.
    """

    log_record_emitted = pyqtSignal(str, str)  # message, level

    def __init__(self, parent=None):
        super().__init__(parent)
        logging.Handler.__init__(self)
        self.setFormatter(NeuralLogFormatter())

    def emit(self, record):
        """Emits the formatted log record as a signal."""
        try:
            message = self.format(record)
            self.log_record_emitted.emit(message, record.levelname.lower())
        except Exception:
            self.handleError(record)


class NeuralLogFormatter(logging.Formatter):
    """Custom formatter สำหรับ neural logging system"""

    def __init__(self):
        super().__init__()
        self.neural_symbols = {
            "DEBUG": "◇",
            "INFO": "◉",
            "WARNING": "◈",
            "ERROR": "◆",
            "CRITICAL": "⬢",
        }
        self.colors = {
            "DEBUG": "\033[90m",  # Gray
            "INFO": "\033[96m",  # Cyan
            "WARNING": "\033[93m",  # Yellow
            "ERROR": "\033[91m",  # Red
            "CRITICAL": "\033[95m",  # Magenta
            "RESET": "\033[0m",  # Reset color
        }

    def format(self, record):
        """Format log record with neural styling"""
        symbol = self.neural_symbols.get(record.levelname, "◯")
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S.%f")[:-3]

        # Get color for console output
        color_start = self.colors.get(record.levelname, self.colors["RESET"])
        color_end = self.colors["RESET"]

        # Neural log format
        neural_format = (
            f"{color_start}[{timestamp}] {symbol} {record.name} "
            f"→ {record.getMessage()}{color_end}"
        )

        # Add exception info if present
        if record.exc_info:
            neural_format += f"\n⚠️ Exception: {self.formatException(record.exc_info)}"

        return neural_format


class QuantumFileHandler(logging.handlers.RotatingFileHandler):
    """Enhanced file handler with quantum data organization"""

    def __init__(self, filename, **kwargs):
        # Ensure log directory exists
        log_dir = Path(filename).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        super().__init__(filename, **kwargs)
        self.setFormatter(NeuralLogFormatter())  # Use custom formatter


def setup_neural_logging(
    log_file: str = "logs/app.log",
    log_level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
):
    """
    Sets up the global neural logging configuration.
    Configures file logging with rotation and console logging.
    Returns the UI log handler for connecting to a QTextEdit.
    """
    # Remove all existing handlers to prevent duplicate logs
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
        handler.close()

    logging.root.setLevel(logging.DEBUG)  # Set root to DEBUG to capture all messages

    # File handler with rotation
    file_handler = QuantumFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    file_handler.setLevel(logging.getLevelName(log_level))
    file_handler.setFormatter(NeuralLogFormatter())
    logging.root.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.getLevelName(log_level))
    console_handler.setFormatter(NeuralLogFormatter())
    logging.root.addHandler(console_handler)

    # UI Log Handler
    ui_log_handler = NeuraUILogHandler()
    ui_log_handler.setLevel(logging.INFO)  # UI might show less verbose logs
    logging.root.addHandler(ui_log_handler)

    logging.info(f"Neural logging system initialized. Log level: {log_level}")
    return ui_log_handler


def get_neural_logger(name: str):
    """Returns a logger instance with the neural logging configuration."""
    return logging.getLogger(name)


class OperationTimer:
    """Context manager for timing operations."""

    def __init__(self, operation_name: str, logger_name: str = "__main__"):
        self.operation_name = operation_name
        self.logger = get_neural_logger(logger_name)
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"▶ Starting: {self.operation_name}...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()

        if exc_type:
            self.logger.error(
                f"◆ Failed: {self.operation_name} ({duration:.3f}s) - {exc_val}"
            )
        else:
            self.logger.info(f"◎ Completed: {self.operation_name} ({duration:.3f}s)")


class NeuralDebugger:
    """Advanced debugging utilities for neural operations"""

    @staticmethod
    def log_function_entry(func):
        """Decorator for logging function entry/exit"""

        def wrapper(*args, **kwargs):
            logger = get_neural_logger(func.__module__)
            logger.info(f"◉ Entering: {func.__name__}")

            try:
                result = func(*args, **kwargs)
                logger.info(f"◎ Exiting: {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"◆ Exception in {func.__name__}: {e}")
                raise

        return wrapper

    @staticmethod
    def log_data_flow(data, stage_name):
        """Log data transformation stages"""
        logger = get_neural_logger("data_flow")

        if hasattr(data, "__len__"):
            logger.info(f"Data Flow: {stage_name} - Records: {len(data)}")
        else:
            logger.info(f"Data Flow: {stage_name} - Data Type: {type(data).__name__}")

        # Optionally, log a snippet of data for debugging purposes
        if isinstance(data, (list, pd.DataFrame)) and len(data) > 0:
            if isinstance(data, pd.DataFrame):
                logger.debug(f"  Snippet:\n{data.head(2).to_string()}")
            else:
                logger.debug(f"  Snippet: {data[:2]}...")


if __name__ == "__main__":
    # Example usage for testing
    ui_handler = setup_neural_logging(log_level="DEBUG")

    # You would connect ui_handler.log_record_emitted to your UI's log display
    # For testing, we can print it
    # ui_handler.log_record_emitted.connect(lambda msg, level: print(f"[UI_SIGNAL] {level.upper()}: {msg}"))

    my_logger = get_neural_logger("test_module")

    my_logger.debug("This is a debug message.")
    my_logger.info("This is an info message.")
    my_logger.warning("This is a warning message.")

    try:
        raise ValueError("Something went wrong!")
    except ValueError:
        my_logger.error("An error occurred.", exc_info=True)

    my_logger.critical("This is a critical message.")

    with OperationTimer("ComplexCalculation"):
        time.sleep(0.5)  # Simulate work
        my_logger.info("Intermediate step completed.")

    @NeuralDebugger.log_function_entry
    def example_function(a, b):
        my_logger.info(f"Calculating {a} + {b}")
        return a + b

    result = example_function(5, 3)
    my_logger.info(f"Result: {result}")

    import pandas as pd

    sample_df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["A", "B", "C"]})
    NeuralDebugger.log_data_flow(sample_df, "Initial Data Load")

    # To see UI messages if not connected to a real UI
    # for msg, level in ui_handler.log_record_emitted: # This won't work directly outside of Qt loop
    #     print(f"UI Logged: [{level}] {msg}")
