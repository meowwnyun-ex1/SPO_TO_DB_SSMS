from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QFont, QTextCursor


class CyberLogConsole(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 10))
        self.setStyleSheet(
            """
            QTextEdit {
                background-color: rgba(0, 0, 0, 0.3);
                color: #00ff9d;
                border: 1px solid rgba(0, 212, 255, 0.3);
                border-radius: 8px;
                padding: 8px;
            }
        """
        )

    def add_message_with_typing(self, message, level="info"):
        colors = {"info": "#00ff9d", "warning": "#ffff00", "error": "#ff0055"}
        color = colors.get(level, colors["info"])
        self.append(f'<span style="color: {color};">{message}</span>')
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
