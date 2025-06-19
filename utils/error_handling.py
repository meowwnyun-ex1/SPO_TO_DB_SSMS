"""
Centralized Error Handling System - ระบบจัดการ Error แบบรวมศูนย์
"""

import logging
import traceback
import sys
from functools import wraps
from typing import Optional, Dict, Callable, Any
from enum import Enum
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox


class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    CONNECTION = "connection"
    CONFIG = "configuration"
    DATA = "data_processing"
    UI = "user_interface"
    SYNC = "synchronization"
    SYSTEM = "system"


@dataclass
class ErrorInfo:
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    exception: Optional[Exception] = None
    context: Optional[Dict] = None
    user_message: Optional[str] = None
    recovery_actions: Optional[list] = None


class ErrorHandler(QObject):
    """Central error handler with UI integration"""

    error_occurred = pyqtSignal(object)  # ErrorInfo

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("error_handler")
        self.error_callbacks: Dict[ErrorCategory, list] = {}
        self.recovery_strategies = {}

    def register_callback(self, category: ErrorCategory, callback: Callable):
        """Register error callback for specific category"""
        if category not in self.error_callbacks:
            self.error_callbacks[category] = []
        self.error_callbacks[category].append(callback)

    def register_recovery(self, category: ErrorCategory, strategy: Callable):
        """Register recovery strategy"""
        self.recovery_strategies[category] = strategy

    def handle_error(self, error_info: ErrorInfo):
        """Handle error with appropriate response"""
        # Log error
        self._log_error(error_info)

        # Emit signal
        self.error_occurred.emit(error_info)

        # Execute callbacks
        if error_info.category in self.error_callbacks:
            for callback in self.error_callbacks[error_info.category]:
                try:
                    callback(error_info)
                except Exception as e:
                    self.logger.error(f"Error callback failed: {e}")

        # Show user notification if needed
        if error_info.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self._show_user_notification(error_info)

        # Attempt recovery
        self._attempt_recovery(error_info)

    def _log_error(self, error_info: ErrorInfo):
        """Log error with appropriate level"""
        context_str = f" Context: {error_info.context}" if error_info.context else ""
        log_msg = f"[{error_info.category.value}] {error_info.message}{context_str}"

        if error_info.exception:
            log_msg += f"\nException: {str(error_info.exception)}"
            log_msg += f"\nTraceback: {traceback.format_exc()}"

        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_msg)
        elif error_info.severity == ErrorSeverity.HIGH:
            self.logger.error(log_msg)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_msg)
        else:
            self.logger.info(log_msg)

    def _show_user_notification(self, error_info: ErrorInfo):
        """Show notification to user"""
        title = f"{error_info.category.value.title()} Error"
        message = error_info.user_message or error_info.message

        if error_info.severity == ErrorSeverity.CRITICAL:
            icon = QMessageBox.Icon.Critical
        else:
            icon = QMessageBox.Icon.Warning

        msg_box = QMessageBox()
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        if error_info.recovery_actions:
            actions_text = "\n".join(
                [f"• {action}" for action in error_info.recovery_actions]
            )
            msg_box.setDetailedText(f"Suggested Actions:\n{actions_text}")

        msg_box.exec()

    def _attempt_recovery(self, error_info: ErrorInfo):
        """Attempt automatic recovery"""
        if error_info.category in self.recovery_strategies:
            try:
                strategy = self.recovery_strategies[error_info.category]
                strategy(error_info)
                self.logger.info(f"Recovery attempted for {error_info.category.value}")
            except Exception as e:
                self.logger.error(f"Recovery failed: {e}")


# Global error handler instance
_error_handler = None


def get_error_handler() -> ErrorHandler:
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


def handle_exceptions(
    category: ErrorCategory,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    user_message: str = None,
    recovery_actions: list = None,
):
    """Decorator for automatic exception handling"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_info = ErrorInfo(
                    category=category,
                    severity=severity,
                    message=f"Error in {func.__name__}: {str(e)}",
                    exception=e,
                    context={"function": func.__name__, "args": str(args)[:100]},
                    user_message=user_message,
                    recovery_actions=recovery_actions,
                )
                get_error_handler().handle_error(error_info)

                # Return appropriate default value based on function name/return type
                if func.__name__.startswith("test_"):
                    return False
                elif func.__name__.startswith("get_") or func.__name__.startswith(
                    "fetch_"
                ):
                    return []
                return None

        return wrapper

    return decorator


class ConnectionErrorHandler:
    """Specialized handler for connection errors"""

    @staticmethod
    @handle_exceptions(
        ErrorCategory.CONNECTION,
        ErrorSeverity.HIGH,
        "Connection failed. Please check your network settings.",
        ["Check internet connection", "Verify server settings", "Try again later"],
    )
    def handle_sharepoint_error(func):
        return func

    @staticmethod
    @handle_exceptions(
        ErrorCategory.CONNECTION,
        ErrorSeverity.HIGH,
        "Database connection failed. Please check configuration.",
        [
            "Verify database settings",
            "Check server availability",
            "Test network connectivity",
        ],
    )
    def handle_database_error(func):
        return func


class ConfigErrorHandler:
    """Specialized handler for configuration errors"""

    @staticmethod
    @handle_exceptions(
        ErrorCategory.CONFIG,
        ErrorSeverity.MEDIUM,
        "Configuration error. Please check your settings.",
        [
            "Review configuration values",
            "Check required fields",
            "Reset to defaults if needed",
        ],
    )
    def handle_config_error(func):
        return func


class SyncErrorHandler:
    """Specialized handler for sync errors"""

    @staticmethod
    @handle_exceptions(
        ErrorCategory.SYNC,
        ErrorSeverity.HIGH,
        "Synchronization failed. Data may be incomplete.",
        [
            "Check source and target connections",
            "Verify data integrity",
            "Retry synchronization",
        ],
    )
    def handle_sync_error(func):
        return func


def setup_global_exception_handler():
    """Setup global exception handler for unhandled exceptions"""

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        error_info = ErrorInfo(
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.CRITICAL,
            message=f"Unhandled exception: {exc_type.__name__}: {str(exc_value)}",
            exception=exc_value,
            user_message="An unexpected error occurred. The application may need to restart.",
            recovery_actions=[
                "Save your work",
                "Restart the application",
                "Report this issue",
            ],
        )

        get_error_handler().handle_error(error_info)

    sys.excepthook = handle_exception


def create_error_recovery_strategies():
    """Create default recovery strategies"""
    handler = get_error_handler()

    def connection_recovery(error_info: ErrorInfo):
        """Recovery for connection errors"""
        logging.info("Attempting connection recovery...")
        # Could implement reconnection logic here

    def config_recovery(error_info: ErrorInfo):
        """Recovery for config errors"""
        logging.info("Attempting config recovery...")
        # Could implement config reset/reload here

    def sync_recovery(error_info: ErrorInfo):
        """Recovery for sync errors"""
        logging.info("Attempting sync recovery...")
        # Could implement partial sync retry here

    handler.register_recovery(ErrorCategory.CONNECTION, connection_recovery)
    handler.register_recovery(ErrorCategory.CONFIG, config_recovery)
    handler.register_recovery(ErrorCategory.SYNC, sync_recovery)


# Convenience functions for common error patterns
def log_and_show_error(
    message: str,
    category: ErrorCategory = ErrorCategory.SYSTEM,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    exception: Exception = None,
):
    """Quick error logging and display"""
    error_info = ErrorInfo(
        category=category,
        severity=severity,
        message=message,
        exception=exception,
        user_message=message,
    )
    get_error_handler().handle_error(error_info)


def safe_execute(
    func: Callable, default_return=None, category: ErrorCategory = ErrorCategory.SYSTEM
) -> Any:
    """Execute function safely with error handling"""
    try:
        return func()
    except Exception as e:
        error_info = ErrorInfo(
            category=category,
            severity=ErrorSeverity.MEDIUM,
            message=f"Safe execution failed: {str(e)}",
            exception=e,
        )
        get_error_handler().handle_error(error_info)
        return default_return


# Initialize error handling system
def init_error_handling():
    """Initialize the error handling system"""
    setup_global_exception_handler()
    create_error_recovery_strategies()
    logging.info("Error handling system initialized")
