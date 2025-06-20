from PyQt6.QtWidgets import (
    QLineEdit,
    QTextEdit,
    QComboBox,
    QSpinBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from ..styles.theme import get_modern_input_style, UltraModernColors


class ModernLineEdit(QLineEdit):
    """Modern line edit with enhanced styling"""

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self.setStyleSheet(get_modern_input_style())
        self.setFont(QFont("Segoe UI", 14, QFont.Weight.Normal))

    def set_error(self, has_error=True):
        """Set error state"""
        if has_error:
            self.setStyleSheet(
                get_modern_input_style().replace(
                    UltraModernColors.GLASS_BORDER, UltraModernColors.ERROR_COLOR
                )
            )
        else:
            self.setStyleSheet(get_modern_input_style())

    def set_success(self, has_success=True):
        """Set success state"""
        if has_success:
            self.setStyleSheet(
                get_modern_input_style().replace(
                    UltraModernColors.GLASS_BORDER, UltraModernColors.SUCCESS_COLOR
                )
            )
        else:
            self.setStyleSheet(get_modern_input_style())


class ModernTextEdit(QTextEdit):
    """Modern text edit with enhanced styling"""

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self.setStyleSheet(get_modern_input_style())
        self.setFont(QFont("Segoe UI", 14, QFont.Weight.Normal))


class ModernComboBox(QComboBox):
    """Modern combo box with enhanced styling"""

    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        if items:
            self.addItems(items)
        self.setStyleSheet(get_modern_input_style())
        self.setFont(QFont("Segoe UI", 14, QFont.Weight.Normal))


class ModernSpinBox(QSpinBox):
    """Modern spin box with enhanced styling"""

    def __init__(self, min_val=0, max_val=100, value=0, suffix="", parent=None):
        super().__init__(parent)
        self.setRange(min_val, max_val)
        self.setValue(value)
        if suffix:
            self.setSuffix(f" {suffix}")
        self.setStyleSheet(get_modern_input_style())
        self.setFont(QFont("Segoe UI", 14, QFont.Weight.Normal))


class FormField(QWidget):
    """Complete form field with label and input"""

    def __init__(
        self, label_text, input_widget, required=False, help_text="", parent=None
    ):
        super().__init__(parent)
        self.input_widget = input_widget
        self.setup_ui(label_text, required, help_text)

    def setup_ui(self, label_text, required, help_text):
        """Setup form field UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Label
        label = QLabel(label_text)
        if required:
            label.setText(f"{label_text} *")

        label.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        label.setStyleSheet(
            f"color: {UltraModernColors.TEXT_ACCENT}; margin-bottom: 4px;"
        )
        layout.addWidget(label)

        # Input widget
        layout.addWidget(self.input_widget)

        # Help text
        if help_text:
            help_label = QLabel(help_text)
            help_label.setFont(QFont("Segoe UI", 10))
            help_label.setStyleSheet(
                f"color: {UltraModernColors.TEXT_SECONDARY}; margin-top: 4px;"
            )
            help_label.setWordWrap(True)
            layout.addWidget(help_label)

    def get_value(self):
        """Get input value"""
        if isinstance(self.input_widget, (QLineEdit, QTextEdit)):
            return (
                self.input_widget.text()
                if isinstance(self.input_widget, QLineEdit)
                else self.input_widget.toPlainText()
            )
        elif isinstance(self.input_widget, QComboBox):
            return self.input_widget.currentText()
        elif isinstance(self.input_widget, QSpinBox):
            return self.input_widget.value()
        return None

    def set_value(self, value):
        """Set input value"""
        if isinstance(self.input_widget, QLineEdit):
            self.input_widget.setText(str(value))
        elif isinstance(self.input_widget, QTextEdit):
            self.input_widget.setPlainText(str(value))
        elif isinstance(self.input_widget, QComboBox):
            index = self.input_widget.findText(str(value))
            if index >= 0:
                self.input_widget.setCurrentIndex(index)
        elif isinstance(self.input_widget, QSpinBox):
            self.input_widget.setValue(int(value))

    def set_error(self, has_error=True, message=""):
        """Set error state"""
        if hasattr(self.input_widget, "set_error"):
            self.input_widget.set_error(has_error)


class PasswordField(ModernLineEdit):
    """Password field แบบธรรมดา"""

    def __init__(self, placeholder="Enter password", parent=None):
        super().__init__(placeholder, parent)
        self.setEchoMode(QLineEdit.EchoMode.Password)


class SearchField(ModernLineEdit):
    """Search field แบบธรรมดา"""

    search_triggered = pyqtSignal(str)

    def __init__(self, placeholder="Search...", parent=None):
        super().__init__(placeholder, parent)

        # Connect signals
        self.textChanged.connect(self._on_text_changed)
        self.returnPressed.connect(self._on_search)

    def _on_text_changed(self, text):
        """Handle text change for live search"""
        if len(text) >= 2:  # Start searching after 2 characters
            self.search_triggered.emit(text)

    def _on_search(self):
        """Handle return press"""
        self.search_triggered.emit(self.text())


class ModernLineEdit(QLineEdit):
    """Modern line edit with enhanced styling"""

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self.setStyleSheet(get_modern_input_style())
        self.setFont(QFont("Segoe UI", 14, QFont.Weight.Normal))

    def set_error(self, has_error=True):
        """Set error state"""
        if has_error:
            self.setStyleSheet(
                get_modern_input_style().replace(
                    UltraModernColors.GLASS_BORDER, UltraModernColors.ERROR_COLOR
                )
            )
        else:
            self.setStyleSheet(get_modern_input_style())

    def set_success(self, has_success=True):
        """Set success state"""
        if has_success:
            self.setStyleSheet(
                get_modern_input_style().replace(
                    UltraModernColors.GLASS_BORDER, UltraModernColors.SUCCESS_COLOR
                )
            )
        else:
            self.setStyleSheet(get_modern_input_style())


class ModernTextEdit(QTextEdit):
    """Modern text edit with enhanced styling"""

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self.setStyleSheet(get_modern_input_style())
        self.setFont(QFont("Segoe UI", 14, QFont.Weight.Normal))


class ModernComboBox(QComboBox):
    """Modern combo box with enhanced styling"""

    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        if items:
            self.addItems(items)
        self.setStyleSheet(get_modern_input_style())
        self.setFont(QFont("Segoe UI", 14, QFont.Weight.Normal))


class ModernSpinBox(QSpinBox):
    """Modern spin box with enhanced styling"""

    def __init__(self, min_val=0, max_val=100, value=0, suffix="", parent=None):
        super().__init__(parent)
        self.setRange(min_val, max_val)
        self.setValue(value)
        if suffix:
            self.setSuffix(f" {suffix}")
        self.setStyleSheet(get_modern_input_style())
        self.setFont(QFont("Segoe UI", 14, QFont.Weight.Normal))


class FormField(QWidget):
    """Complete form field with label and input"""

    def __init__(
        self, label_text, input_widget, required=False, help_text="", parent=None
    ):
        super().__init__(parent)
        self.input_widget = input_widget
        self.setup_ui(label_text, required, help_text)

    def setup_ui(self, label_text, required, help_text):
        """Setup form field UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Label
        label = QLabel(label_text)
        if required:
            label.setText(f"{label_text} *")

        label.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
        label.setStyleSheet(
            f"color: {UltraModernColors.TEXT_ACCENT}; margin-bottom: 4px;"
        )
        layout.addWidget(label)

        # Input widget
        layout.addWidget(self.input_widget)

        # Help text
        if help_text:
            help_label = QLabel(help_text)
            help_label.setFont(QFont("Segoe UI", 10))
            help_label.setStyleSheet(
                f"color: {UltraModernColors.TEXT_SECONDARY}; margin-top: 4px;"
            )
            help_label.setWordWrap(True)
            layout.addWidget(help_label)

    def get_value(self):
        """Get input value"""
        if isinstance(self.input_widget, (QLineEdit, QTextEdit)):
            return (
                self.input_widget.text()
                if isinstance(self.input_widget, QLineEdit)
                else self.input_widget.toPlainText()
            )
        elif isinstance(self.input_widget, QComboBox):
            return self.input_widget.currentText()
        elif isinstance(self.input_widget, QSpinBox):
            return self.input_widget.value()
        return None

    def set_value(self, value):
        """Set input value"""
        if isinstance(self.input_widget, QLineEdit):
            self.input_widget.setText(str(value))
        elif isinstance(self.input_widget, QTextEdit):
            self.input_widget.setPlainText(str(value))
        elif isinstance(self.input_widget, QComboBox):
            index = self.input_widget.findText(str(value))
            if index >= 0:
                self.input_widget.setCurrentIndex(index)
        elif isinstance(self.input_widget, QSpinBox):
            self.input_widget.setValue(int(value))

    def set_error(self, has_error=True, message=""):
        """Set error state"""
        if hasattr(self.input_widget, "set_error"):
            self.input_widget.set_error(has_error)


class PasswordField(ModernLineEdit):
    """Password field with show/hide toggle"""

    def __init__(self, placeholder="Enter password", parent=None):
        super().__init__(placeholder, parent)
        self.setEchoMode(QLineEdit.EchoMode.Password)

        # Add show/hide action
        self.show_action = self.addAction(
            "👁️", QLineEdit.ActionPosition.TrailingPosition
        )
        self.show_action.triggered.connect(self.toggle_password_visibility)
        self.password_visible = False

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.password_visible:
            self.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_action.setText("👁️")
        else:
            self.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_action.setText("🙈")
        self.password_visible = not self.password_visible


class SearchField(ModernLineEdit):
    """Search field with search icon"""

    search_triggered = pyqtSignal(str)

    def __init__(self, placeholder="Search...", parent=None):
        super().__init__(placeholder, parent)

        # Add search icon
        self.search_action = self.addAction(
            "🔍", QLineEdit.ActionPosition.LeadingPosition
        )

        # Connect signals
        self.textChanged.connect(self._on_text_changed)
        self.returnPressed.connect(self._on_search)

    def _on_text_changed(self, text):
        """Handle text change for live search"""
        if len(text) >= 2:  # Start searching after 2 characters
            self.search_triggered.emit(text)

    def _on_search(self):
        """Handle return press"""
        self.search_triggered.emit(self.text())
