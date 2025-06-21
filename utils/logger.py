# utils/logger.py - Modern 2025 Logging System
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Optional
import weakref


class ModernUILogHandler(QObject, logging.Handler):
    """Modern logging handler with proper cleanup"""

    log_record_emitted = pyqtSignal(str, str)  # message, level

    _instances = weakref.WeakSet()

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        logging.Handler.__init__(self)

        # Add to weak reference set for cleanup tracking
        ModernUILogHandler._instances.add(self)

        self.setFormatter(ModernLogFormatter())
        self._is_destroyed = False

    def emit(self, record):
        """Emit log record as signal with safety checks"""
        if self._is_destroyed:
            return

        try:
            message = self.format(record)
            # Only emit if signal is still connected
            if self.log_record_emitted.receivers() > 0:
                self.log_record_emitted.emit(message, record.levelname.lower())
        except (RuntimeError, AttributeError):
            # Object has been deleted or signal disconnected
            self._is_destroyed = True
        except Exception:
            # Fallback to prevent logging errors from breaking the app
            self.handleError(record)

    def cleanup(self):
        """Safe cleanup method"""
        if self._is_destroyed:
            return

        try:
            # Disconnect all signals
            if hasattr(self, "log_record_emitted"):
                self.log_record_emitted.disconnect()
            self._is_destroyed = True
        except (RuntimeError, TypeError):
            pass

    def __del__(self):
        """Destructor with safe cleanup"""
        try:
            self.cleanup()
        except:
            pass

    @classmethod
    def cleanup_all_instances(cls):
        """Cleanup all handler instances"""
        instances_copy = list(cls._instances)
        for handler in instances_copy:
            try:
                if handler and not handler._is_destroyed:
                    handler.cleanup()
            except (ReferenceError, AttributeError):
                pass


class ModernLogFormatter(logging.Formatter):
    """Modern log formatter with clean output"""

    def __init__(self):
        super().__init__()

        # Modern icons
        self.level_icons = {
            "DEBUG": "🔍",
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "CRITICAL": "🚨",
        }

        # Console colors
        self.colors = {
            "DEBUG": "\033[36m",  # Cyan
            "INFO": "\033[32m",  # Green
            "WARNING": "\033[33m",  # Yellow
            "ERROR": "\033[31m",  # Red
            "CRITICAL": "\033[35m",  # Magenta
            "RESET": "\033[0m",  # Reset
        }

    def format(self, record):
        """Format log record with modern styling"""
        icon = self.level_icons.get(record.levelname, "•")
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")

        # For console output (with colors)
        if hasattr(record, "console_output"):
            color_start = self.colors.get(record.levelname, self.colors["RESET"])
            color_end = self.colors["RESET"]
            formatted_msg = (
                f"{color_start}[{timestamp}] {icon} "
                f"{record.name} → {record.getMessage()}{color_end}"
            )
        else:
            # For UI output (no colors)
            formatted_msg = (
                f"[{timestamp}] {icon} {record.name} → {record.getMessage()}"
            )

        # Add exception info if present
        if record.exc_info:
            formatted_msg += f"\n💥 Exception: {self.formatException(record.exc_info)}"

        return formatted_msg


class PerformanceFileHandler(logging.handlers.RotatingFileHandler):
    """High-performance file handler with modern features"""

    def __init__(self, filename, **kwargs):
        # Ensure log directory exists
        log_dir = Path(filename).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # Default parameters for performance
        kwargs.setdefault("maxBytes", 10 * 1024 * 1024)  # 10MB
        kwargs.setdefault("backupCount", 5)
        kwargs.setdefault("encoding", "utf-8")

        super().__init__(filename, **kwargs)
        self.setFormatter(ModernLogFormatter())


class LoggerManager:
    """Centralized logger management"""

    _ui_handler: Optional[ModernUILogHandler] = None
    _is_initialized = False

    @classmethod
    def setup_logging(
        cls,
        log_file: str = "logs/app.log",
        log_level: str = "INFO",
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5,
    ) -> Optional[ModernUILogHandler]:
        """Setup modern logging system"""

        if cls._is_initialized:
            return cls._ui_handler

        # Clean up any existing handlers
        cls.cleanup_logging()

        # Set root logger level
        logging.root.setLevel(logging.DEBUG)

        try:
            # File handler
            file_handler = PerformanceFileHandler(
                log_file, maxBytes=max_bytes, backupCount=backup_count
            )
            file_handler.setLevel(logging.getLevelName(log_level))
            logging.root.addHandler(file_handler)

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.getLevelName(log_level))
            console_handler.setFormatter(ModernLogFormatter())
            # Mark for console coloring
            console_handler.addFilter(
                lambda record: setattr(record, "console_output", True) or True
            )
            logging.root.addHandler(console_handler)

            # UI Handler
            cls._ui_handler = ModernUILogHandler()
            cls._ui_handler.setLevel(logging.INFO)  # UI shows less verbose logs
            logging.root.addHandler(cls._ui_handler)

            cls._is_initialized = True

            logging.info(f"Modern logging system initialized - Level: {log_level}")
            return cls._ui_handler

        except Exception as e:
            print(f"Failed to setup logging: {e}")
            return None

    @classmethod
    def cleanup_logging(cls):
        """Safe cleanup of all logging handlers"""
        if not cls._is_initialized:
            return

        try:
            # Remove all existing handlers
            for handler in logging.root.handlers[:]:
                try:
                    # Special cleanup for UI handlers
                    if isinstance(handler, ModernUILogHandler):
                        handler.cleanup()

                    logging.root.removeHandler(handler)

                    # Close file handlers
                    if hasattr(handler, "close"):
                        handler.close()

                except Exception as e:
                    print(f"Error removing handler: {e}")

            # Cleanup all UI handler instances
            ModernUILogHandler.cleanup_all_instances()

            cls._ui_handler = None
            cls._is_initialized = False

        except Exception as e:
            print(f"Error during logging cleanup: {e}")

    @classmethod
    def get_ui_handler(cls) -> Optional[ModernUILogHandler]:
        """Get current UI handler"""
        return cls._ui_handler

    @classmethod
    def is_initialized(cls) -> bool:
        """Check if logging is initialized"""
        return cls._is_initialized


def get_logger(name: str) -> logging.Logger:
    """Get logger instance with modern configuration"""
    return logging.getLogger(name)


class OperationTimer:
    """Context manager for timing operations"""

    def __init__(self, operation_name: str, logger_name: str = "__main__"):
        self.operation_name = operation_name
        self.logger = get_logger(logger_name)
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"🚀 Starting: {self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()

        if exc_type:
            self.logger.error(
                f"💥 Failed: {self.operation_name} ({duration:.3f}s) - {exc_val}"
            )
        else:
            self.logger.info(f"✅ Completed: {self.operation_name} ({duration:.3f}s)")


class ModernDebugger:
    """Modern debugging utilities"""

    @staticmethod
    def log_function_entry(func):
        """Decorator for logging function entry/exit"""

        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            logger.debug(f"→ Entering: {func.__name__}")

            try:
                result = func(*args, **kwargs)
                logger.debug(f"← Exiting: {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"💥 Exception in {func.__name__}: {e}")
                raise

        return wrapper

    @staticmethod
    def log_data_flow(data, stage_name: str, logger_name: str = "data_flow"):
        """Log data transformation stages"""
        logger = get_logger(logger_name)

        try:
            if hasattr(data, "__len__"):
                count = len(data)
                logger.info(f"📊 {stage_name}: {count} records")
            else:
                logger.info(f"📊 {stage_name}: {type(data).__name__}")

            # Log sample data for debugging
            if isinstance(data, (list, tuple)) and len(data) > 0:
                logger.debug(f"   Sample: {str(data[:2])[:100]}...")
            elif hasattr(data, "head"):  # pandas DataFrame
                logger.debug(f"   Sample:\n{data.head(2)}")

        except Exception as e:
            logger.warning(f"Error logging data flow for {stage_name}: {e}")


# Convenience functions
def setup_neural_logging(*args, **kwargs):
    """Backward compatibility function"""
    return LoggerManager.setup_logging(*args, **kwargs)


def cleanup_neural_logging():
    """Cleanup logging system"""
    LoggerManager.cleanup_logging()


def get_neural_logger(name: str):
    """Backward compatibility function"""
    return get_logger(name)


# Global cleanup function for application shutdown
def shutdown_logging():
    """Safe shutdown of logging system"""
    try:
        LoggerManager.cleanup_logging()
        # Force cleanup of logging module
        logging.shutdown()
    except Exception as e:
        print(f"Error during logging shutdown: {e}")


# Automatic cleanup registration
import atexit

atexit.register(shutdown_logging)
