from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QFont, QTextCursor, QColor
from PyQt6.QtCore import QTimer  # Import QTimer for typing effect


class CyberLogConsole(QTextEdit):
    """
    คอนโซล Log สไตล์ Cyber พร้อมเอฟเฟกต์การพิมพ์ตัวอักษรทีละตัว
    และรองรับสีตามระดับของ Log
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.typing_timer = QTimer(self)
        self.typing_timer.timeout.connect(self._add_next_char)
        self.full_message = ""
        self.current_index = 0
        self.message_level = "info"

    def setup_ui(self):
        """ตั้งค่า UI สำหรับคอนโซล"""
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 10))
        # Stylesheet is now loaded from theme.py, ensuring consistency
        # สไตล์ชีทจะถูกโหลดจาก theme.py เพื่อให้สอดคล้องกัน
        # self.setStyleSheet(...) will be set by apply_ultra_modern_theme or get_cyber_log_style

    def add_message_with_typing(self, message, level="info"):
        """
        เพิ่มข้อความ Log พร้อมเอฟเฟกต์การพิมพ์
        Args:
            message (str): ข้อความที่จะแสดง
            level (str): ระดับ Log ('info', 'warning', 'error')
        """
        self.full_message = message + "\n"  # Add newline at the end
        self.current_index = 0
        self.message_level = level

        # Clear current line if not empty before starting new message for typing effect
        # if not self.toPlainText().endswith('\n') and self.toPlainText():
        #     self.append("") # Ensure a fresh line

        # Start typing effect
        self.typing_timer.start(25)  # Typing speed (milliseconds per character)

    def _add_next_char(self):
        """Add the next character of the message with color."""
        if self.current_index < len(self.full_message):
            char_to_add = self.full_message[self.current_index]

            # Get color based on level (same logic as before)
            colors = {"info": "#00ff9d", "warning": "#ffff00", "error": "#ff0055"}
            color_code = colors.get(self.message_level, colors["info"])

            # Use QTextCursor to insert styled text
            cursor = self.textCursor()
            cursor.movePosition(
                QTextCursor.MoveOperation.End
            )  # Move to end of document

            # Create a character format for the color
            char_format = cursor.charFormat()
            text_color = QColor(color_code)
            char_format.setForeground(text_color)
            cursor.setCharFormat(char_format)  # Apply format

            cursor.insertText(char_to_add)  # Insert character

            # Move cursor to the end again and apply default format for next text
            cursor.movePosition(QTextCursor.MoveOperation.End)
            default_format = cursor.charFormat()
            default_format.setForeground(
                QColor("#00ff9d")
            )  # Reset to default info color
            cursor.setCharFormat(default_format)

            self.setTextCursor(cursor)  # Update cursor position

            self.current_index += 1
        else:
            self.typing_timer.stop()
            # Ensure the last line is properly terminated if it's not already
            if not self.toPlainText().endswith("\n"):
                self.append("")
            # After typing is complete, reset to default font/color for subsequent messages
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            default_format = cursor.charFormat()
            default_format.setForeground(
                QColor("#00ff9d")
            )  # Reset to default info color
            cursor.setCharFormat(default_format)
            self.setTextCursor(cursor)

    def clear(self):
        """Clear the text console and stop typing animation if active."""
        super().clear()
        if self.typing_timer.isActive():
            self.typing_timer.stop()
        self.full_message = ""
        self.current_index = 0
        self.message_level = "info"
