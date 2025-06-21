# ui/widgets/cyber_log_console.py - Modern 2025 Log Console
from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSlot, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QColor, QTextCharFormat
from datetime import datetime
from collections import deque
import sys
from pathlib import Path

current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from ui.styles.theme import ModernColors, Typography, BorderRadius
    from ui.widgets.modern_button import IconButton
except ImportError:

    class ModernColors:
        SURFACE_PRIMARY = "#0F172A"
        TEXT_PRIMARY = "#F8FAFC"
        SUCCESS = "#10B981"
        ERROR = "#EF4444"
        WARNING = "#F59E0B"


class LogEntry:
    """Structured log entry"""

    def __init__(self, message, level="info", timestamp=None):
        self.message = message
        self.level = level.lower()
        self.timestamp = timestamp or datetime.now()
        self.formatted_time = self.timestamp.strftime("%H:%M:%S.%f")[:-3]

    def to_html(self):
        """Convert to HTML with styling"""
        icons = {
            "debug": "🔍",
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "critical": "🚨",
            "success": "✅",
        }

        colors = {
            "debug": ModernColors.TEXT_SECONDARY,
            "info": ModernColors.TEXT_PRIMARY,
            "warning": ModernColors.WARNING,
            "error": ModernColors.ERROR,
            "critical": ModernColors.ERROR,
            "success": ModernColors.SUCCESS,
        }

        icon = icons.get(self.level, "•")
        color = colors.get(self.level, ModernColors.TEXT_PRIMARY)

        return f"""
        <div style="margin: 2px 0; padding: 4px 8px; border-left: 2px solid {color}20; background: rgba(255,255,255,0.02);">
            <span style="color: {ModernColors.TEXT_SECONDARY}; font-size: 11px;">{self.formatted_time}</span>
            <span style="color: {color}; margin: 0 8px;">{icon}</span>
            <span style="color: {color};">{self.message}</span>
        </div>
        """


class ModernLogConsole(QTextEdit):
    """2025 Modern Log Console with performance optimization"""

    log_cleared = pyqtSignal()

    def __init__(self, max_entries=500, parent=None):
        super().__init__(parent)
        self.max_entries = max_entries
        self.entry_queue = deque(maxlen=1000)
        self.batch_timer = QTimer(self)
        self.batch_timer.setSingleShot(True)
        self.batch_timer.timeout.connect(self._process_batch)
        self.pending_entries = []

        self._setup_ui()
        self._add_welcome_message()

    def _setup_ui(self):
        """Setup console styling and properties"""
        self.setReadOnly(True)
        self.setFont(QFont(Typography.MONO_FONT, Typography.TEXT_SM))

        # Modern styling
        self.setStyleSheet(
            f"""
            QTextEdit {{
                background: {ModernColors.SURFACE_PRIMARY};
                color: {ModernColors.TEXT_PRIMARY};
                border: 1px solid {ModernColors.GLASS_BORDER};
                border-radius: {BorderRadius.MD}px;
                padding: 12px;
                font-family: "{Typography.MONO_FONT}", "Consolas", monospace;
                font-size: {Typography.TEXT_SM}px;
                line-height: 1.4;
                selection-background-color: {ModernColors.PRIMARY};
            }}
        """
        )

        # Performance optimizations
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setWordWrapMode(self.WordWrapMode.WidgetWidth)

        # Enable rich text
        self.setHtml("")

    def _add_welcome_message(self):
        """Add initial welcome message"""
        welcome_html = f"""
        <div style="text-align: center; padding: 20px; color: {ModernColors.TEXT_SECONDARY};">
            <h3 style="color: {ModernColors.PRIMARY}; margin: 0;">🚀 DENSO Neural Matrix</h3>
            <p style="margin: 8px 0 0 0; font-size: 12px;">Log Console Initialized</p>
            <hr style="border: 1px solid {ModernColors.GLASS_BORDER}; margin: 16px 0;">
        </div>
        """
        self.setHtml(welcome_html)

    @pyqtSlot(str, str)
    def add_log_message(self, message, level="info"):
        """Add log message with batching for performance"""
        if not message.strip():
            return

        entry = LogEntry(message, level)
        self.pending_entries.append(entry)

        # Start batch timer if not active
        if not self.batch_timer.isActive():
            self.batch_timer.start(100)  # 100ms batch delay

    def _process_batch(self):
        """Process batched log entries"""
        if not self.pending_entries:
            return

        # Process up to 10 entries at once
        batch_size = min(10, len(self.pending_entries))
        entries_to_process = []

        for _ in range(batch_size):
            if self.pending_entries:
                entries_to_process.append(self.pending_entries.pop(0))

        # Add entries to console
        for entry in entries_to_process:
            self._append_entry(entry)
            self.entry_queue.append(entry)

        # Limit total entries
        self._limit_entries()

        # Auto-scroll to bottom
        self._scroll_to_bottom()

        # Continue processing if more entries pending
        if self.pending_entries:
            self.batch_timer.start(50)

    def _append_entry(self, entry):
        """Append single entry to console"""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(entry.to_html())

    def _limit_entries(self):
        """Limit number of entries for performance"""
        if len(self.entry_queue) > self.max_entries:
            # Remove old entries from display
            excess = len(self.entry_queue) - self.max_entries
            self._remove_old_entries(excess)

    def _remove_old_entries(self, count):
        """Remove old entries from top of console"""
        try:
            document = self.document()
            cursor = QTextCursor(document)
            cursor.movePosition(QTextCursor.MoveOperation.Start)

            # Remove blocks from top
            for _ in range(min(count, document.blockCount() - 1)):
                cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()

        except Exception:
            pass  # Fail silently to prevent console errors

    def _scroll_to_bottom(self):
        """Auto-scroll to show latest entries"""
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    @pyqtSlot()
    def clear(self):
        """Clear console and reset state"""
        self.entry_queue.clear()
        self.pending_entries.clear()

        if self.batch_timer.isActive():
            self.batch_timer.stop()

        super().clear()
        self._add_welcome_message()
        self.log_cleared.emit()

    def export_logs(self, file_path):
        """Export logs to file"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("DENSO Neural Matrix - Log Export\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write("=" * 50 + "\n\n")

                for entry in self.entry_queue:
                    f.write(
                        f"[{entry.formatted_time}] {entry.level.upper()}: {entry.message}\n"
                    )

            return True
        except Exception:
            return False

    def get_stats(self):
        """Get console statistics"""
        level_counts = {}
        for entry in self.entry_queue:
            level_counts[entry.level] = level_counts.get(entry.level, 0) + 1

        return {
            "total_entries": len(self.entry_queue),
            "pending_entries": len(self.pending_entries),
            "level_distribution": level_counts,
            "is_processing": self.batch_timer.isActive(),
        }

    def filter_by_level(self, levels):
        """Filter display by log levels"""
        if not levels:
            levels = ["debug", "info", "warning", "error", "critical", "success"]

        filtered_html = f"""
        <div style="text-align: center; padding: 20px; color: {ModernColors.TEXT_SECONDARY};">
            <h3 style="color: {ModernColors.PRIMARY}; margin: 0;">🚀 DENSO Neural Matrix</h3>
            <p style="margin: 8px 0 0 0; font-size: 12px;">Filtered Log View</p>
            <hr style="border: 1px solid {ModernColors.GLASS_BORDER}; margin: 16px 0;">
        </div>
        """

        for entry in self.entry_queue:
            if entry.level in levels:
                filtered_html += entry.to_html()

        self.setHtml(filtered_html)
        self._scroll_to_bottom()

    def search_logs(self, query):
        """Search logs and highlight results"""
        if not query:
            return

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)

        # Clear previous highlights
        self.setExtraSelections([])

        # Find and highlight all occurrences
        selections = []
        while True:
            cursor = self.document().find(query, cursor)
            if cursor.isNull():
                break

            # Create highlight format
            format = QTextCharFormat()
            format.setBackground(QColor(ModernColors.WARNING))
            format.setForeground(QColor(ModernColors.SURFACE_PRIMARY))

            # Add to selections
            selection = self.ExtraSelection()
            selection.cursor = cursor
            selection.format = format
            selections.append(selection)

        self.setExtraSelections(selections)

        # Move to first result
        if selections:
            self.setTextCursor(selections[0].cursor)


class LogConsoleWithControls(QWidget):
    """Log console with control buttons"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Control bar
        controls = QHBoxLayout()
        controls.setSpacing(8)

        self.clear_btn = IconButton("🗑", tooltip="Clear logs", size="sm")
        self.export_btn = IconButton("💾", tooltip="Export logs", size="sm")
        self.filter_btn = IconButton("🔍", tooltip="Filter logs", size="sm")
        self.stats_btn = IconButton("📊", tooltip="Show stats", size="sm")

        controls.addWidget(self.clear_btn)
        controls.addWidget(self.export_btn)
        controls.addWidget(self.filter_btn)
        controls.addWidget(self.stats_btn)
        controls.addStretch()

        # Log level indicators
        level_layout = QHBoxLayout()
        level_layout.setSpacing(4)

        levels = [
            ("🔍", "DEBUG", ModernColors.TEXT_SECONDARY),
            ("ℹ️", "INFO", ModernColors.TEXT_PRIMARY),
            ("⚠️", "WARN", ModernColors.WARNING),
            ("❌", "ERROR", ModernColors.ERROR),
        ]

        for icon, name, color in levels:
            indicator = QPushButton(f"{icon} {name}")
            indicator.setCheckable(True)
            indicator.setChecked(True)
            indicator.setStyleSheet(
                f"""
                QPushButton {{
                    background: transparent;
                    border: 1px solid {color}40;
                    border-radius: 4px;
                    padding: 2px 6px;
                    color: {color};
                    font-size: 10px;
                }}
                QPushButton:checked {{
                    background: {color}20;
                    border-color: {color};
                }}
            """
            )
            level_layout.addWidget(indicator)

        level_layout.addStretch()

        # Combine control bars
        control_widget = QWidget()
        control_widget.setStyleSheet(
            f"""
            QWidget {{
                background: {ModernColors.SURFACE_SECONDARY};
                border: 1px solid {ModernColors.GLASS_BORDER};
                border-radius: {BorderRadius.SM}px;
                padding: 4px 8px;
            }}
        """
        )
        control_layout = QVBoxLayout(control_widget)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(4)
        control_layout.addLayout(controls)
        control_layout.addLayout(level_layout)

        layout.addWidget(control_widget)

        # Console
        self.console = ModernLogConsole()
        layout.addWidget(self.console)

        # Connect signals
        self.clear_btn.clicked.connect(self.console.clear)
        self.export_btn.clicked.connect(self._export_logs)

    def _export_logs(self):
        """Export logs to file"""
        from PyQt6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs",
            f"denso_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)",
        )
        if file_path:
            success = self.console.export_logs(file_path)
            if success:
                self.console.add_log_message(
                    f"Logs exported to: {file_path}", "success"
                )
            else:
                self.console.add_log_message("Failed to export logs", "error")


# Backward compatibility
CyberLogConsole = ModernLogConsole
