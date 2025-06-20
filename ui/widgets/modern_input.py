from PyQt6.QtWidgets import (
    QLineEdit,
    QTextEdit,
    QComboBox,
    QSpinBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import pyqtSignal, Qt  # Added Qt for alignment
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
    """Modern text edit with enhanced styling for multi-line input."""

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self.setStyleSheet(
            get_modern_input_style()
        )  # Reusing input style for consistency
        self.setFont(QFont("Segoe UI", 14, QFont.Weight.Normal))
        self.setMinimumHeight(80)  # Ensure enough height for multi-line text

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


class ModernSpinBox(QSpinBox):
    """Modern SpinBox for integer or decimal values."""

    def __init__(self, min_val=0, max_val=100, step=1, decimal=False, parent=None):
        super().__init__(parent)
        self.is_decimal = decimal
        if decimal:
            self.setDecimals(2)  # Default to 2 decimal places
            self.setSingleStep(step)
            self.setRange(min_val, max_val)
        else:
            self.setSingleStep(step)
            self.setRange(min_val, max_val)
        self.setStyleSheet(get_modern_input_style())
        self.setFont(QFont("Segoe UI", 14, QFont.Weight.Normal))


class FormField(QWidget):
    """
    A reusable widget combining a label and an input widget.
    Can wrap QLineEdit, QTextEdit, QComboBox, QSpinBox, QCheckBox.
    """

    def __init__(self, input_widget, label_text="", parent=None):
        super().__init__(parent)
        self.input_widget = input_widget
        self.label_text = label_text
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        if self.label_text:
            self.label = QLabel(self.label_text)
            self.label.setFont(QFont("Segoe UI", 12, QFont.Weight.SemiBold))
            self.label.setStyleSheet(f"color: {UltraModernColors.TEXT_PRIMARY};")
            layout.addWidget(self.label)
        else:
            self.label = None  # No label if text is empty

        # For QCheckBox, we might not want to put it inside FormField's layout
        # as it often comes with its own label. Handle this directly in ConfigPanel.
        if isinstance(self.input_widget, QCheckBox):
            # If it's a checkbox, assume the input_widget itself provides the label/text
            layout.addWidget(self.input_widget)
            if self.label:
                self.label.hide()  # Hide the FormField's label if it's a checkbox
        else:
            layout.addWidget(self.input_widget)

    def get_value(self):
        """Retrieves the current value from the wrapped input widget."""
        if isinstance(self.input_widget, QLineEdit):
            return self.input_widget.text()
        elif isinstance(self.input_widget, QTextEdit):
            return self.input_widget.toPlainText()
        elif isinstance(self.input_widget, QComboBox):
            return self.input_widget.currentText()
        elif isinstance(self.input_widget, QSpinBox):
            return self.input_widget.value()
        elif isinstance(self.input_widget, QCheckBox):
            return self.input_widget.isChecked()
        return None

    def set_value(self, value):
        """Sets the value of the wrapped input widget."""
        if isinstance(self.input_widget, QLineEdit):
            self.input_widget.setText(str(value))
        elif isinstance(self.input_widget, QTextEdit):
            self.input_widget.setText(str(value))
        elif isinstance(self.input_widget, QComboBox):
            index = self.input_widget.findText(str(value), Qt.MatchFlag.MatchExactly)
            if index >= 0:
                self.input_widget.setCurrentIndex(index)
            else:
                self.input_widget.setCurrentText(
                    str(value)
                )  # Fallback if text not in list
        elif isinstance(self.input_widget, QSpinBox):
            # QSpinBox needs value to be within range, so convert to int/float first
            if self.input_widget.is_decimal:
                self.input_widget.setValue(float(value))
            else:
                self.input_widget.setValue(int(value))
        elif isinstance(self.input_widget, QCheckBox):
            self.input_widget.setChecked(bool(value))

    def set_error(self, has_error=True, message=""):
        """Set error state for the input widget."""
        if hasattr(self.input_widget, "set_error"):
            self.input_widget.set_error(has_error)
        if self.label:
            if has_error:
                self.label.setStyleSheet(
                    f"color: {UltraModernColors.ERROR_COLOR}; font-weight: bold;"
                )
                if message:
                    self.label.setText(
                        f"{self.label_text} <span style='color:{UltraModernColors.ERROR_COLOR}; font-size:10px;'>({message})</span>"
                    )
            else:
                self.label.setStyleSheet(
                    f"color: {UltraModernColors.TEXT_PRIMARY}; font-weight: semi-bold;"
                )
                self.label.setText(self.label_text)


class PasswordField(ModernLineEdit):
    """แก้แล้ว: Password field แบบธรรมดาไม่มี show/hide toggle"""

    def __init__(self, placeholder="Enter password", parent=None):
        super().__init__(placeholder, parent)
        self.setEchoMode(QLineEdit.EchoMode.Password)


class SearchField(ModernLineEdit):
    """แก้แล้ว: Search field แบบธรรมดาไม่มี search icon"""

    search_triggered = pyqtSignal(str)

    def __init__(self, placeholder="Search...", parent=None):
        super().__init__(placeholder, parent)

        # Connect signals
        self.textChanged.connect(self._on_text_changed)
        self.returnPressed.connect(self._on_search)

    def _on_text_changed(self, text):
        """Handle text change for live search"""
        # Example: if text length > 3, trigger a soft search
        # This could be debounced with a QTimer if performance is an issue
        if len(text) > 3 or not text:  # Trigger on 3+ chars or when clearing
            self.search_triggered.emit(text)

    def _on_search(self):
        """Handle Enter key pressed for explicit search"""
        self.search_triggered.emit(self.text())
