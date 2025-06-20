"""
Centralized Error Handling System - ระบบจัดการ Error แบบรวมศูนย์
"""

import logging
import traceback
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
    DATA_IMPORT = "data_import"  # Added new category for data import errors


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
        self.recovery_handlers: Dict[ErrorCategory, Callable] = {}
        self.error_occurred.connect(
            self._show_message_box
        )  # Connect to default UI display
        self.last_error_info: Optional[ErrorInfo] = None
        self.logger.info("ErrorHandler initialized.")

    def handle_error(self, error_info: ErrorInfo):
        """
        Handles an error by logging it, calling registered callbacks,
        and triggering a UI message.
        """
        self.last_error_info = error_info
        log_method = {
            ErrorSeverity.LOW: self.logger.info,
            ErrorSeverity.MEDIUM: self.logger.warning,
            ErrorSeverity.HIGH: self.logger.error,
            ErrorSeverity.CRITICAL: self.logger.critical,
        }.get(error_info.severity, self.logger.error)

        log_method(
            f"Error [{error_info.category.value.upper()}/{error_info.severity.value.upper()}]: {error_info.message}",
            exc_info=error_info.exception,
        )

        # Call category-specific callbacks
        for callback in self.error_callbacks.get(error_info.category, []):
            try:
                callback(error_info)
            except Exception as e:
                self.logger.error(
                    f"Error in error callback for {error_info.category.value}: {e}",
                    exc_info=True,
                )

        # Attempt recovery action
        recovery_func = self.recovery_handlers.get(error_info.category)
        if recovery_func:
            self.logger.info(
                f"Attempting recovery for {error_info.category.value} error."
            )
            try:
                recovery_func(error_info)
            except Exception as e:
                self.logger.error(
                    f"Recovery failed for {error_info.category.value}: {e}",
                    exc_info=True,
                )

        self.error_occurred.emit(error_info)  # Emit signal for UI display

    def _show_message_box(self, error_info: ErrorInfo):
        """Default UI handler to display an error message box."""
        # Avoid showing too many popups, especially for low severity or repeated errors
        if (
            error_info.severity in [ErrorSeverity.LOW, ErrorSeverity.MEDIUM]
            and not error_info.user_message
        ):
            return  # Don't show popups for minor issues unless explicitly requested

        msg_box = QMessageBox()
        msg_box.setWindowTitle(
            f"Error: {error_info.category.value.replace('_', ' ').title()}"
        )

        icon_map = {
            ErrorSeverity.LOW: QMessageBox.Icon.Information,
            ErrorSeverity.MEDIUM: QMessageBox.Icon.Warning,
            ErrorSeverity.HIGH: QMessageBox.Icon.Critical,
            ErrorSeverity.CRITICAL: QMessageBox.Icon.Critical,
        }
        msg_box.setIcon(icon_map.get(error_info.severity, QMessageBox.Icon.Critical))

        display_message = error_info.user_message or "An unexpected error occurred."
        if error_info.severity == ErrorSeverity.CRITICAL:
            display_message += "\nThe application may not function correctly and might need to be restarted."

        msg_box.setText(f"<b>{display_message}</b>")

        details = f"Category: {error_info.category.value}\nSeverity: {error_info.severity.value}\n"
        details += f"Message: {error_info.message}\n"
        if error_info.context:
            details += f"Context: {error_info.context}\n"
        if error_info.exception:
            details += f"Exception Type: {type(error_info.exception).__name__}\n"
            details += "Traceback:\n" + "".join(
                traceback.format_exception(
                    type(error_info.exception),
                    error_info.exception,
                    error_info.exception.__traceback__,
                )
            )

        msg_box.setDetailedText(details)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def register_callback(
        self, category: ErrorCategory, callback: Callable[[ErrorInfo], None]
    ):
        """Registers a callback function for a specific error category."""
        if category not in self.error_callbacks:
            self.error_callbacks[category] = []
        self.error_callbacks[category].append(callback)
        self.logger.debug(f"Registered callback for category: {category.value}")

    def register_recovery(
        self, category: ErrorCategory, recovery_func: Callable[[ErrorInfo], None]
    ):
        """Registers a recovery function for a specific error category."""
        self.recovery_handlers[category] = recovery_func
        self.logger.debug(f"Registered recovery handler for category: {category.value}")

    def get_last_error_info(self) -> Optional[ErrorInfo]:
        """Returns the information of the last handled error."""
        return self.last_error_info

    def cleanup(self):
        """Cleans up the error handler by disconnecting signals."""
        try:
            self.error_occurred.disconnect(self._show_message_box)
            self.logger.info("ErrorHandler signals disconnected.")
        except TypeError as e:
            self.logger.debug(
                f"Attempted to disconnect non-connected ErrorHandler signal: {e}"
            )
        except Exception as e:
            self.logger.warning(f"Error during ErrorHandler signal disconnection: {e}")
        self.error_callbacks.clear()
        self.recovery_handlers.clear()
        self.logger.info("ErrorHandler cleanup completed.")


# Global instance of ErrorHandler (Singleton pattern)
_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Returns the singleton instance of the ErrorHandler."""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


def handle_exceptions(
    category: ErrorCategory, severity: ErrorSeverity = ErrorSeverity.HIGH
):
    """
    Decorator for handling exceptions in functions.
    Catches exceptions, logs them, and triggers the central error handler.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_info = ErrorInfo(
                    category=category,
                    severity=severity,
                    message=f"An error occurred in {func.__name__}: {e}",
                    exception=e,
                    context={"function": func.__name__},
                )
                get_error_handler().handle_error(error_info)
                # Depending on severity, you might re-raise or return a default value
                if severity == ErrorSeverity.CRITICAL:
                    raise  # Re-raise critical errors to stop execution
                return None  # Return None for non-critical errors or specific default_return if defined

        return wrapper

    return decorator


# Example recovery functions (can be expanded)
def connection_recovery(error_info: ErrorInfo):
    """Attempts to recover from connection errors."""
    logger = logging.getLogger("recovery")
    logger.info("Attempting to reset connections for recovery...")
    # In a real app, this might involve:
    # - Retrying connection attempts
    # - Clearing cached connection objects
    # - Prompting user to check network
    pass


def config_recovery(error_info: ErrorInfo):
    """Attempts to recover from configuration errors."""
    logger = logging.getLogger("recovery")
    logger.warning(
        "Configuration error detected. Suggesting manual review of config files."
    )
    # In a real app, this might involve:
    # - Reloading config
    # - Prompting user to fix invalid entries
    pass


def sync_recovery(error_info: ErrorInfo):
    """Attempts to recover from synchronization errors."""
    logger = logging.getLogger("recovery")
    logger.warning(
        "Sync error detected. Consider running a full sync or checking data integrity."
    )
    # In a real app, this might involve:
    # - Retrying specific failed items
    # - Rolling back partial changes
    pass


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
    handler = get_error_handler()
    # Register default recovery handlers (can be overridden or extended)
    handler.register_recovery(ErrorCategory.CONNECTION, connection_recovery)
    handler.register_recovery(ErrorCategory.CONFIG, config_recovery)
    handler.register_recovery(ErrorCategory.SYNC, sync_recovery)
    # Register new DATA_IMPORT recovery if needed
    # handler.register_recovery(ErrorCategory.DATA_IMPORT, data_import_recovery)
