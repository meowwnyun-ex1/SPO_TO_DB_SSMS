from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QFont, QTextCursor, QColor
from PyQt6.QtCore import QTimer
from ..styles.theme import UltraModernColors


class CyberLogConsole(QTextEdit):
    """Compact Cyber Log Console สำหรับ 900x500"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_compact_ui()
        self.typing_timer = QTimer(self)
        self.typing_timer.timeout.connect(self._add_next_char)
        self.full_message = ""
        self.current_index = 0
        self.message_level = "info"
        self.max_lines = 200  # จำกัดจำนวนบรรทัด

    def setup_compact_ui(self):
        """ตั้งค่า UI สำหรับคอนโซลแบบ compact"""
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 8))  # ลดขนาดฟอนต์

        # Compact styling
        self.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {UltraModernColors.GLASS_BG_DARK};
                border: 1px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 6px;
                color: {UltraModernColors.TEXT_PRIMARY};
                padding: 4px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 8px;
                line-height: 1.3;
            }}
            QScrollBar:vertical {{
                border: none;
                background: rgba(0, 0, 0, 0.2);
                width: 6px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {UltraModernColors.NEON_PURPLE};
                border-radius: 3px;
                min-height: 15px;
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
        """เพิ่มข้อความ Log พร้อมเอฟเฟกต์การพิมพ์ - compact version"""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")

        # เพิ่ม emoji ตาม level - compact
        level_icons = {
            "info": "ℹ",
            "success": "✓",
            "warning": "⚠",
            "error": "✗",
            "debug": "◦",
        }

        icon = level_icons.get(level, "ℹ")

        # Compact message format - ตัดข้อความยาวๆ
        short_message = message[:60] + "..." if len(message) > 60 else message
        self.full_message = f"[{timestamp}] {icon} {short_message}\n"
        self.current_index = 0
        self.message_level = level

        # Start typing effect - เร็วขึ้น
        self.typing_timer.start(10)

    def _add_next_char(self):
        """Add the next character - optimized for compact display"""
        if self.current_index < len(self.full_message):
            char_to_add = self.full_message[self.current_index]

            # Compact colors
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
            self._limit_lines()  # จำกัดจำนวนบรรทัด
            self.ensureCursorVisible()

    def _limit_lines(self):
        """จำกัดจำนวนบรรทัดเพื่อประสิทธิภาพ"""
        document = self.document()
        if document.lineCount() > self.max_lines:
            cursor = QTextCursor(document)
            cursor.movePosition(QTextCursor.MoveOperation.Start)

            # ลบบรรทัดแรกๆ ออก
            lines_to_remove = document.lineCount() - self.max_lines + 10
            for _ in range(lines_to_remove):
                cursor.select(QTextCursor.SelectionType.LineUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()  # ลบ newline

    def clear(self):
        """Clear the text console and stop typing animation"""
        super().clear()
        if self.typing_timer.isActive():
            self.typing_timer.stop()
        self.full_message = ""
        self.current_index = 0
        self.message_level = "info"

    def add_system_message(self, message):
        """เพิ่มข้อความระบบโดยตรง - compact version"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        char_format = cursor.charFormat()
        char_format.setForeground(QColor(UltraModernColors.NEON_GREEN))
        cursor.setCharFormat(char_format)

        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        short_message = message[:50] + "..." if len(message) > 50 else message
        cursor.insertText(f"[{timestamp}] ⚙ {short_message}\n")

        self.setTextCursor(cursor)
        self._limit_lines()
        self.ensureCursorVisible()

    def add_compact_message(self, message, level="info"):
        """เพิ่มข้อความแบบไม่มี typing effect สำหรับประสิทธิภาพ"""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")

        level_icons = {
            "info": "ℹ",
            "success": "✓",
            "warning": "⚠",
            "error": "✗",
            "debug": "◦",
        }

        colors = {
            "info": UltraModernColors.NEON_BLUE,
            "success": UltraModernColors.SUCCESS_COLOR,
            "warning": UltraModernColors.NEON_YELLOW,
            "error": UltraModernColors.ERROR_COLOR,
            "debug": UltraModernColors.TEXT_SECONDARY,
        }

        icon = level_icons.get(level, "ℹ")
        color = colors.get(level, colors["info"])

        # Compact message
        short_message = message[:50] + "..." if len(message) > 50 else message

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        char_format = cursor.charFormat()
        char_format.setForeground(QColor(color))
        cursor.setCharFormat(char_format)

        cursor.insertText(f"[{timestamp}] {icon} {short_message}\n")

        self.setTextCursor(cursor)
        self._limit_lines()
        self.ensureCursorVisible()

    def cleanup(self):
        """Cleanup สำหรับปิดโปรแกรม"""
        if hasattr(self, "typing_timer") and self.typing_timer.isActive():
            self.typing_timer.stop()
