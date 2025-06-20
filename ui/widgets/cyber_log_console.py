from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QFont, QTextCursor, QColor
from PyQt6.QtCore import QTimer
from ..styles.theme import UltraModernColors


class CyberLogConsole(QTextEdit):
    """คอนโซล Log สไตล์ Cyber พร้อมเอฟเฟกต์การพิมพ์"""

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

        # แก้: ใช้ theme colors
        self.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {UltraModernColors.GLASS_BG_DARK};
                border: 1px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 8px;
                color: {UltraModernColors.TEXT_PRIMARY};
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10px;
                line-height: 1.4;
            }}
            QScrollBar:vertical {{
                border: none;
                background: rgba(0, 0, 0, 0.2);
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {UltraModernColors.NEON_PURPLE};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {UltraModernColors.NEON_PINK};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                background: none;
                border: none;
            }}
        """
        )

    def add_message_with_typing(self, message, level="info"):
        """เพิ่มข้อความ Log พร้อมเอฟเฟกต์การพิมพ์"""
        # แก้: เพิ่ม emoji และ timestamp
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")

        # เพิ่ม emoji ตาม level
        level_icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "debug": "🔍",
        }

        icon = level_icons.get(level, "ℹ️")
        self.full_message = f"[{timestamp}] {icon} {message}\n"
        self.current_index = 0
        self.message_level = level

        # Start typing effect
        self.typing_timer.start(15)  # ความเร็วการพิมพ์

    def _add_next_char(self):
        """Add the next character of the message with color."""
        if self.current_index < len(self.full_message):
            char_to_add = self.full_message[self.current_index]

            # แก้: ใช้ colors จาก theme
            colors = {
                "info": UltraModernColors.NEON_BLUE,
                "success": UltraModernColors.SUCCESS_COLOR,
                "warning": UltraModernColors.NEON_YELLOW,
                "error": UltraModernColors.ERROR_COLOR,
                "debug": UltraModernColors.TEXT_SECONDARY,
            }
            color_code = colors.get(self.message_level, colors["info"])

            # Use QTextCursor to insert styled text
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)

            # Create a character format for the color
            char_format = cursor.charFormat()
            text_color = QColor(color_code)
            char_format.setForeground(text_color)
            cursor.setCharFormat(char_format)

            cursor.insertText(char_to_add)

            # Move cursor to the end and apply default format
            cursor.movePosition(QTextCursor.MoveOperation.End)
            default_format = cursor.charFormat()
            default_format.setForeground(QColor(UltraModernColors.TEXT_PRIMARY))
            cursor.setCharFormat(default_format)

            self.setTextCursor(cursor)
            self.current_index += 1
        else:
            self.typing_timer.stop()
            # Scroll to bottom
            self.ensureCursorVisible()

    def clear(self):
        """Clear the text console and stop typing animation."""
        super().clear()
        if self.typing_timer.isActive():
            self.typing_timer.stop()
        self.full_message = ""
        self.current_index = 0
        self.message_level = "info"

    def add_system_message(self, message):
        """เพิ่มข้อความระบบโดยตรงไม่มี typing effect"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        char_format = cursor.charFormat()
        char_format.setForeground(QColor(UltraModernColors.NEON_GREEN))
        cursor.setCharFormat(char_format)

        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        cursor.insertText(f"[{timestamp}] 🖥️ {message}\n")

        self.setTextCursor(cursor)
        self.ensureCursorVisible()
