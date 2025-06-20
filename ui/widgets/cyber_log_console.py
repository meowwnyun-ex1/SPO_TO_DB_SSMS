# ui/widgets/cyber_log_console.py - Enhanced Cyber Log Console
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QFont, QTextCursor, QColor
from PyQt6.QtCore import QTimer, Qt  # Added Qt for text alignment
from ..styles.theme import UltraModernColors  # Relative import
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CyberLogConsole(QTextEdit):
    """
    Compact Cyber Log Console with dynamic text rendering (typing effect)
    and optimized for large log volumes by limiting lines.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_compact_ui()

        self.typing_timer = QTimer(self)
        self.typing_timer.setInterval(10)  # Faster typing speed (milliseconds per char)
        self.typing_timer.timeout.connect(self._add_next_char)

        self.full_message_queue = []  # Queue for messages awaiting typing effect
        self.current_message_info = (
            None  # (full_message, current_index, message_level, color, icon)
        )

        self.max_lines = 200  # Limit the number of lines to prevent memory overflow
        logger.debug("CyberLogConsole initialized.")

    def setup_compact_ui(self):
        """Sets up the UI for the compact log console."""
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 10))  # Monospaced font for logs
        self.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {UltraModernColors.GLASS_BG_DARK};
                border: 1px solid {UltraModernColors.GLASS_BORDER};
                border-radius: 8px;
                color: {UltraModernColors.TEXT_PRIMARY};
                padding: 5px;
                selection-background-color: {UltraModernColors.NEON_PURPLE};
                selection-color: white;
            }}
        """
        )
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def add_log_message(self, message: str, level: str = "info"):
        """
        Adds a new log message to the console with a typing effect.
        :param message: The log message string.
        :param level: The log level ("info", "warning", "error", "success", "debug", "critical").
        """
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        color = self._get_color_for_level(level)
        icon = self._get_icon_for_level(level)
        full_message = f"{timestamp} {icon} {message}"

        self.full_message_queue.append((full_message, 0, level, color, icon))
        if not self.typing_timer.isActive():
            self._start_typing_next_message()

    def _get_color_for_level(self, level: str) -> QColor:
        """Returns the appropriate QColor for a given log level."""
        colors = {
            "debug": UltraModernColors.TEXT_SECONDARY,
            "info": UltraModernColors.TEXT_PRIMARY,
            "warning": UltraModernColors.WARNING_COLOR,
            "error": UltraModernColors.ERROR_COLOR,
            "critical": UltraModernColors.ERROR_COLOR,
            "success": UltraModernColors.SUCCESS_COLOR,
        }
        return QColor(colors.get(level.lower(), UltraModernColors.TEXT_PRIMARY))

    def _get_icon_for_level(self, level: str) -> str:
        """Returns an icon string for a given log level."""
        icons = {
            "debug": "◇",
            "info": "◉",
            "warning": "◈",
            "error": "◆",
            "critical": "⬢",
            "success": "✅",
        }
        return icons.get(level.lower(), "◯")

    def _start_typing_next_message(self):
        """Starts the typing effect for the next message in the queue."""
        if self.full_message_queue:
            self.current_message_info = self.full_message_queue.pop(0)
            self.typing_timer.start()
        else:
            self.typing_timer.stop()
            self.current_message_info = None

    def _add_next_char(self):
        """Adds the next character of the current message to the display."""
        if not self.current_message_info:
            return

        full_message, current_index, level, color, icon = self.current_message_info

        if current_index < len(full_message):
            char_to_add = full_message[current_index]

            # Move cursor to the end, insert character
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertHtml(
                f"<span style='color: {color.name()};'>{char_to_add}</span>"
            )

            # Check if this is the end of a line
            if char_to_add == "\n":
                self._limit_lines()

            self.current_message_info = (
                full_message,
                current_index + 1,
                level,
                color,
                icon,
            )
        else:
            # Message finished, add newline and start next
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertHtml("<br>")  # Use <br> for HTML newline
            self._limit_lines()
            self._start_typing_next_message()

        self.verticalScrollBar().setValue(
            self.verticalScrollBar().maximum()
        )  # Keep scroll at bottom

    def _limit_lines(self):
        """Limits the number of lines in the console to max_lines."""
        doc = self.document()
        if doc.blockCount() > self.max_lines:
            cursor = QTextCursor(doc)
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            # Remove lines from the beginning until max_lines is reached
            for _ in range(doc.blockCount() - self.max_lines):
                cursor.select(QTextCursor.SelectionType.LineUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()  # Delete newline character
                cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.setTextCursor(cursor)
            # Ensure scroll bar stays at bottom if it was there before trimming
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
            logger.debug(f"Trimmed log console to {self.max_lines} lines.")

    def clear(self):
        """Clears all text from the console and resets state."""
        self.full_message_queue.clear()
        if self.typing_timer and self.typing_timer.isActive():
            self.typing_timer.stop()
        self.current_message_info = None
        super().clear()
        logger.info("CyberLogConsole cleared.")

    def cleanup(self):
        """Performs cleanup for the CyberLogConsole."""
        logger.info("CyberLogConsole cleanup initiated.")
        if self.typing_timer and self.typing_timer.isActive():
            self.typing_timer.stop()
            self.typing_timer.deleteLater()
            self.typing_timer = None
            logger.debug("Typing timer stopped and deleted.")
        self.full_message_queue.clear()
        self.current_message_info = None
        logger.info("CyberLogConsole cleanup completed.")
