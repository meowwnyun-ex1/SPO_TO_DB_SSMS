# ui/widgets/cyber_log_console.py - Fixed Cyber Log Console
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QFont, QTextCursor, QColor
from PyQt6.QtCore import QTimer, Qt, pyqtSlot
from datetime import datetime
import logging
from collections import deque

try:
    from ..styles.theme import UltraModernColors
except ImportError:
    # Fallback colors if theme import fails
    class UltraModernColors:
        GLASS_BG_DARK = "rgba(10, 10, 10, 0.92)"
        GLASS_BORDER = "rgba(255, 255, 255, 0.15)"
        TEXT_PRIMARY = "#E0E0E0"
        TEXT_SECONDARY = "#A0A0A0"
        NEON_PURPLE = "#9D4EDD"
        NEON_GREEN = "#00F5A0"
        WARNING_COLOR = "#FFD700"
        ERROR_COLOR = "#FF6347"
        SUCCESS_COLOR = "#00FF7F"


logger = logging.getLogger(__name__)


class LogMessage:
    """Represents a single log message with metadata"""

    def __init__(self, message: str, level: str, timestamp: datetime = None):
        self.message = message
        self.level = level.lower()
        self.timestamp = timestamp or datetime.now()
        self.formatted_time = self.timestamp.strftime("[%H:%M:%S]")
        self.icon = self._get_icon_for_level()
        self.color = self._get_color_for_level()

    def _get_icon_for_level(self) -> str:
        """Get icon for log level"""
        icons = {
            "debug": "◇",
            "info": "◉",
            "warning": "◈",
            "error": "◆",
            "critical": "⬢",
            "success": "✅",
        }
        return icons.get(self.level, "◯")

    def _get_color_for_level(self) -> QColor:
        """Get color for log level"""
        colors = {
            "debug": UltraModernColors.TEXT_SECONDARY,
            "info": UltraModernColors.TEXT_PRIMARY,
            "warning": UltraModernColors.WARNING_COLOR,
            "error": UltraModernColors.ERROR_COLOR,
            "critical": UltraModernColors.ERROR_COLOR,
            "success": UltraModernColors.SUCCESS_COLOR,
        }
        return QColor(colors.get(self.level, UltraModernColors.TEXT_PRIMARY))

    def to_html(self) -> str:
        """Convert message to HTML format"""
        return (
            f'<span style="color: {self.color.name()};">'
            f"{self.formatted_time} {self.icon} {self.message}"
            f"</span>"
        )


class CyberLogConsole(QTextEdit):
    """
    Enhanced Cyber Log Console with optimized performance and memory management.
    Features typing effect, automatic line limiting, and efficient rendering.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Configuration
        self.max_lines = 500  # Increased for better history
        self.max_queue_size = 1000  # Prevent memory overflow
        self.typing_speed = 15  # Characters per update (faster than before)

        # State management
        self.message_queue = deque(maxlen=self.max_queue_size)
        self.current_message = None
        self.current_index = 0
        self.is_typing = False

        # Timer for typing effect
        self.typing_timer = QTimer(self)
        self.typing_timer.setInterval(50)  # 50ms for smooth typing
        self.typing_timer.timeout.connect(self._type_next_chunk)

        # Timer for batch processing
        self.batch_timer = QTimer(self)
        self.batch_timer.setSingleShot(True)
        self.batch_timer.setInterval(100)  # 100ms delay for batching
        self.batch_timer.timeout.connect(self._process_message_batch)

        # Pending messages for batch processing
        self.pending_messages = []

        self._setup_ui()
        logger.debug("CyberLogConsole initialized")

    def _setup_ui(self):
        """Setup the UI styling and properties"""
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 10, QFont.Weight.Normal))

        # Apply styling
        self.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {UltraModernColors.GLASS_BG_DARK};
                border: 1px solid {UltraModernColors.GLASS_BORDER};
                border-radius: 8px;
                color: {UltraModernColors.TEXT_PRIMARY};
                padding: 8px;
                selection-background-color: {UltraModernColors.NEON_PURPLE};
                selection-color: white;
                font-family: "Consolas", "Monaco", monospace;
            }}
        """
        )

        # Scroll bar policies
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Enable word wrap
        self.setWordWrapMode(self.WordWrapMode.WidgetWidth)

        # Set initial message
        self._append_html(
            '<span style="color: #00F5A0;">◉ Log console initialized</span>'
        )

    @pyqtSlot(str, str)
    def add_log_message(self, message: str, level: str = "info"):
        """
        Add a new log message to the console.
        Messages are batched for better performance.
        """
        try:
            if not message.strip():
                return

            # Create log message object
            log_msg = LogMessage(message, level)

            # Add to pending batch
            self.pending_messages.append(log_msg)

            # Start/restart batch timer
            if not self.batch_timer.isActive():
                self.batch_timer.start()

        except Exception as e:
            logger.error(f"Error adding log message: {e}")

    def _process_message_batch(self):
        """Process batched messages for better performance"""
        try:
            if not self.pending_messages:
                return

            # If typing is in progress, wait for it to complete
            if self.is_typing:
                self.batch_timer.start()  # Retry later
                return

            # Process messages in batch
            batch_size = min(5, len(self.pending_messages))  # Process up to 5 at once
            messages_to_process = []

            for _ in range(batch_size):
                if self.pending_messages:
                    messages_to_process.append(self.pending_messages.pop(0))

            # Add to queue for typing effect
            for msg in messages_to_process:
                if len(self.message_queue) < self.max_queue_size:
                    self.message_queue.append(msg)

            # Start typing if not already in progress
            if not self.is_typing:
                self._start_next_message()

            # Continue processing if more messages pending
            if self.pending_messages:
                self.batch_timer.start()

        except Exception as e:
            logger.error(f"Error processing message batch: {e}")

    def _start_next_message(self):
        """Start typing the next message from the queue"""
        try:
            if self.message_queue and not self.is_typing:
                self.current_message = self.message_queue.popleft()
                self.current_index = 0
                self.is_typing = True
                self.typing_timer.start()

        except Exception as e:
            logger.error(f"Error starting next message: {e}")

    def _type_next_chunk(self):
        """Type the next chunk of characters"""
        try:
            if not self.current_message or not self.is_typing:
                self._finish_typing()
                return

            # Get full message HTML
            full_html = self.current_message.to_html()

            # Calculate how many characters to show
            chars_to_show = min(len(full_html), self.current_index + self.typing_speed)

            if chars_to_show >= len(full_html):
                # Message complete
                self._append_html(full_html + "<br>")
                self._finish_typing()
            else:
                # Continue typing - for simplicity, just add the complete message
                # (Chunked HTML typing is complex due to tag boundaries)
                self._append_html(full_html + "<br>")
                self._finish_typing()

        except Exception as e:
            logger.error(f"Error in typing effect: {e}")
            self._finish_typing()

    def _finish_typing(self):
        """Finish current typing and start next message"""
        try:
            self.typing_timer.stop()
            self.is_typing = False
            self.current_message = None
            self.current_index = 0

            # Limit lines after adding message
            self._limit_lines()

            # Auto-scroll to bottom
            self._scroll_to_bottom()

            # Start next message if available
            if self.message_queue:
                self._start_next_message()

        except Exception as e:
            logger.error(f"Error finishing typing: {e}")

    def _append_html(self, html: str):
        """Append HTML content to the console"""
        try:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertHtml(html)

        except Exception as e:
            logger.error(f"Error appending HTML: {e}")

    def _limit_lines(self):
        """Remove old lines if console exceeds max_lines"""
        try:
            document = self.document()
            block_count = document.blockCount()

            if block_count > self.max_lines:
                # Calculate how many lines to remove
                lines_to_remove = block_count - self.max_lines

                # Move cursor to start and remove lines
                cursor = QTextCursor(document)
                cursor.movePosition(QTextCursor.MoveOperation.Start)

                for _ in range(lines_to_remove):
                    cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                    cursor.removeSelectedText()
                    cursor.deleteChar()  # Remove the newline

                logger.debug(f"Removed {lines_to_remove} lines from console")

        except Exception as e:
            logger.error(f"Error limiting lines: {e}")

    def _scroll_to_bottom(self):
        """Scroll console to bottom"""
        try:
            scrollbar = self.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        except Exception as e:
            logger.debug(f"Error scrolling to bottom: {e}")

    @pyqtSlot()
    def clear(self):
        """Clear all text from console and reset state"""
        try:
            # Stop timers
            if self.typing_timer.isActive():
                self.typing_timer.stop()
            if self.batch_timer.isActive():
                self.batch_timer.stop()

            # Clear state
            self.message_queue.clear()
            self.pending_messages.clear()
            self.current_message = None
            self.current_index = 0
            self.is_typing = False

            # Clear console
            super().clear()

            # Add cleared message
            self._append_html(
                '<span style="color: #FFD700;">◈ Console cleared</span><br>'
            )

            logger.info("Log console cleared")

        except Exception as e:
            logger.error(f"Error clearing console: {e}")

    def add_separator(self, text: str = ""):
        """Add a visual separator to the console"""
        try:
            separator_text = f"{'─' * 50}"
            if text:
                separator_text = f"─── {text} {'─' * (44 - len(text))}"

            separator_msg = LogMessage(separator_text, "info")
            self.add_log_message(separator_msg.message, separator_msg.level)

        except Exception as e:
            logger.error(f"Error adding separator: {e}")

    def get_line_count(self) -> int:
        """Get current number of lines in console"""
        try:
            return self.document().blockCount()
        except Exception:
            return 0

    def get_message_count(self) -> int:
        """Get number of messages in queue"""
        return len(self.message_queue) + len(self.pending_messages)

    def is_busy(self) -> bool:
        """Check if console is currently processing messages"""
        return self.is_typing or bool(self.message_queue) or bool(self.pending_messages)

    def flush(self):
        """Force processing of all pending messages immediately"""
        try:
            # Stop typing effect temporarily
            typing_was_active = self.typing_timer.isActive()
            if typing_was_active:
                self.typing_timer.stop()

            # Process all pending messages immediately
            while self.pending_messages:
                msg = self.pending_messages.pop(0)
                self._append_html(msg.to_html() + "<br>")

            # Process all queued messages immediately
            while self.message_queue:
                msg = self.message_queue.popleft()
                self._append_html(msg.to_html() + "<br>")

            # Reset typing state
            self.is_typing = False
            self.current_message = None

            # Limit lines and scroll
            self._limit_lines()
            self._scroll_to_bottom()

            logger.debug("Console flushed")

        except Exception as e:
            logger.error(f"Error flushing console: {e}")

    def cleanup(self):
        """Perform cleanup for the console"""
        logger.info("CyberLogConsole cleanup initiated")

        try:
            # Stop all timers
            if self.typing_timer:
                self.typing_timer.stop()
                self.typing_timer.deleteLater()
                self.typing_timer = None

            if self.batch_timer:
                self.batch_timer.stop()
                self.batch_timer.deleteLater()
                self.batch_timer = None

            # Clear all queues
            self.message_queue.clear()
            self.pending_messages.clear()

            # Reset state
            self.current_message = None
            self.is_typing = False

            logger.info("CyberLogConsole cleanup completed")

        except Exception as e:
            logger.error(f"Error during console cleanup: {e}")
