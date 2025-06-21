# ui/widgets/modern_input.py - Modern 2025 Input System
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import sys
from pathlib import Path

current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from ui.styles.theme import ModernColors, Typography, BorderRadius, get_input_style
except ImportError:

    class ModernColors:
        SURFACE_SECONDARY = "#1E293B"
        PRIMARY = "#6366F1"
        TEXT_PRIMARY = "#F8FAFC"


class ModernLineEdit(QLineEdit):
    """Modern line edit with enhanced UX"""

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self._setup_style()
        self._setup_animations()

    def _setup_style(self):
        self.setStyleSheet(get_input_style())
        self.setFont(QFont(Typography.PRIMARY_FONT, Typography.TEXT_BASE))
        self.setMinimumHeight(40)

    def _setup_animations(self):
        self.focus_animation = QPropertyAnimation(self, b"styleSheet")
        self.focus_animation.setDuration(200)
        self.focus_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def set_error(self, has_error=True):
        if has_error:
            self.setStyleSheet(
                get_input_style().replace(ModernColors.GLASS_BORDER, ModernColors.ERROR)
            )
        else:
            self.setStyleSheet(get_input_style())


class ModernTextEdit(QTextEdit):
    """Modern multi-line text input"""

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet(get_input_style())
        self.setFont(QFont(Typography.PRIMARY_FONT, Typography.TEXT_BASE))
        self.setMinimumHeight(80)


class ModernComboBox(QComboBox):
    """Modern dropdown with search"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(get_input_style())
        self.setFont(QFont(Typography.PRIMARY_FONT, Typography.TEXT_BASE))
        self.setMinimumHeight(40)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)


class ModernSpinBox(QSpinBox):
    """Modern number input"""

    def __init__(self, min_val=0, max_val=100, parent=None):
        super().__init__(parent)
        self.setRange(min_val, max_val)
        self.setStyleSheet(get_input_style())
        self.setFont(QFont(Typography.PRIMARY_FONT, Typography.TEXT_BASE))
        self.setMinimumHeight(40)


class SearchField(ModernLineEdit):
    """Search input with instant feedback"""

    search_triggered = pyqtSignal(str)

    def __init__(self, placeholder="Search...", parent=None):
        super().__init__(placeholder, parent)
        self.textChanged.connect(self._on_text_changed)
        self.returnPressed.connect(self._on_search)

        # Add search icon
        self.setText("🔍 " + self.text())

    def _on_text_changed(self, text):
        if len(text) > 2 or not text:
            self.search_triggered.emit(text)

    def _on_search(self):
        self.search_triggered.emit(self.text())


class PasswordField(ModernLineEdit):
    """Password input with toggle visibility"""

    def __init__(self, placeholder="Password", parent=None):
        super().__init__(placeholder, parent)
        self.setEchoMode(QLineEdit.EchoMode.Password)
        self._setup_toggle_button()

    def _setup_toggle_button(self):
        self.toggle_btn = QPushButton("👁")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setFixedSize(30, 30)
        self.toggle_btn.setStyleSheet(
            """
            QPushButton {
                border: none;
                background: transparent;
                font-size: 14px;
            }
        """
        )
        self.toggle_btn.clicked.connect(self._toggle_visibility)

        layout = QHBoxLayout(self)
        layout.addStretch()
        layout.addWidget(self.toggle_btn)
        layout.setContentsMargins(0, 0, 8, 0)

    def _toggle_visibility(self, checked):
        if checked:
            self.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_btn.setText("🙈")
        else:
            self.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_btn.setText("👁")


class FormField(QWidget):
    """Complete form field with label and validation"""

    def __init__(self, input_widget, label_text="", required=False, parent=None):
        super().__init__(parent)
        self.input_widget = input_widget
        self.label_text = label_text
        self.required = required
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        if self.label_text:
            label_layout = QHBoxLayout()

            self.label = QLabel(self.label_text)
            self.label.setFont(
                QFont(
                    Typography.PRIMARY_FONT,
                    Typography.TEXT_SM,
                    Typography.WEIGHT_MEDIUM,
                )
            )
            self.label.setStyleSheet(f"color: {ModernColors.TEXT_PRIMARY};")
            label_layout.addWidget(self.label)

            if self.required:
                required_label = QLabel("*")
                required_label.setStyleSheet(f"color: {ModernColors.ERROR};")
                label_layout.addWidget(required_label)

            label_layout.addStretch()
            layout.addLayout(label_layout)

        layout.addWidget(self.input_widget)

        # Error message label
        self.error_label = QLabel()
        self.error_label.setStyleSheet(
            f"""
            color: {ModernColors.ERROR};
            font-size: {Typography.TEXT_SM}px;
        """
        )
        self.error_label.hide()
        layout.addWidget(self.error_label)

    def get_value(self):
        if isinstance(self.input_widget, QLineEdit):
            return self.input_widget.text()
        elif isinstance(self.input_widget, QTextEdit):
            return self.input_widget.toPlainText()
        elif isinstance(self.input_widget, QComboBox):
            return self.input_widget.currentText()
        elif isinstance(self.input_widget, QSpinBox):
            return self.input_widget.value()
        return None

    def set_value(self, value):
        if isinstance(self.input_widget, QLineEdit):
            self.input_widget.setText(str(value))
        elif isinstance(self.input_widget, QTextEdit):
            self.input_widget.setText(str(value))
        elif isinstance(self.input_widget, QComboBox):
            index = self.input_widget.findText(str(value))
            if index >= 0:
                self.input_widget.setCurrentIndex(index)
        elif isinstance(self.input_widget, QSpinBox):
            self.input_widget.setValue(int(value))

    def set_error(self, message=""):
        if message:
            self.error_label.setText(message)
            self.error_label.show()
            if hasattr(self.input_widget, "set_error"):
                self.input_widget.set_error(True)
        else:
            self.error_label.hide()
            if hasattr(self.input_widget, "set_error"):
                self.input_widget.set_error(False)

    def validate(self):
        """Basic validation"""
        if self.required and not self.get_value():
            self.set_error("This field is required")
            return False

        self.set_error()
        return True


class ModernCheckBox(QCheckBox):
    """Modern checkbox with animations"""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._setup_style()

    def _setup_style(self):
        self.setStyleSheet(
            f"""
            QCheckBox {{
                font-size: {Typography.TEXT_BASE}px;
                color: {ModernColors.TEXT_PRIMARY};
                spacing: 8px;
                font-family: "{Typography.PRIMARY_FONT}";
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {ModernColors.GLASS_BORDER};
                background: {ModernColors.SURFACE_SECONDARY};
            }}
            QCheckBox::indicator:checked {{
                background: {ModernColors.PRIMARY};
                border-color: {ModernColors.PRIMARY};
            }}
            QCheckBox::indicator:hover {{
                border-color: {ModernColors.PRIMARY};
            }}
        """
        )


class ModernSlider(QSlider):
    """Modern slider with value display"""

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self._setup_style()
        self._setup_value_display()

    def _setup_style(self):
        self.setStyleSheet(
            f"""
            QSlider::groove:horizontal {{
                border: none;
                height: 6px;
                background: {ModernColors.SURFACE_TERTIARY};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {ModernColors.PRIMARY};
                border: none;
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }}
            QSlider::sub-page:horizontal {{
                background: {ModernColors.PRIMARY};
                border-radius: 3px;
            }}
        """
        )

    def _setup_value_display(self):
        self.value_label = QLabel(str(self.value()))
        self.value_label.setStyleSheet(
            f"""
            background: {ModernColors.SURFACE_TERTIARY};
            color: {ModernColors.TEXT_PRIMARY};
            padding: 4px 8px;
            border-radius: 4px;
            font-size: {Typography.TEXT_SM}px;
        """
        )
        self.valueChanged.connect(lambda v: self.value_label.setText(str(v)))


class FileUploadField(QWidget):
    """Modern file upload with drag & drop"""

    file_selected = pyqtSignal(str)

    def __init__(self, accept_types="All Files (*)", parent=None):
        super().__init__(parent)
        self.accept_types = accept_types
        self._setup_ui()
        self.setAcceptDrops(True)

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet(
            f"""
            background: {ModernColors.SURFACE_SECONDARY};
            border: 1px solid {ModernColors.GLASS_BORDER};
            border-radius: {BorderRadius.BASE}px;
            padding: 8px 12px;
            color: {ModernColors.TEXT_SECONDARY};
        """
        )
        layout.addWidget(self.file_label, 1)

        self.browse_btn = QPushButton("📁 Browse")
        self.browse_btn.clicked.connect(self._browse_file)
        self.browse_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {ModernColors.PRIMARY};
                color: {ModernColors.TEXT_PRIMARY};
                border: none;
                border-radius: {BorderRadius.BASE}px;
                padding: 8px 16px;
                font-weight: {Typography.WEIGHT_MEDIUM};
            }}
        """
        )
        layout.addWidget(self.browse_btn)

    def _browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", self.accept_types
        )
        if file_path:
            self._set_file(file_path)

    def _set_file(self, file_path):
        file_name = Path(file_path).name
        self.file_label.setText(file_name)
        self.file_label.setStyleSheet(
            self.file_label.styleSheet().replace(
                ModernColors.TEXT_SECONDARY, ModernColors.TEXT_PRIMARY
            )
        )
        self.file_selected.emit(file_path)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self._set_file(files[0])


# Factory functions
def create_text_field(placeholder="", label="", required=False, parent=None):
    input_widget = ModernLineEdit(placeholder, parent)
    return FormField(input_widget, label, required, parent)


def create_password_field(label="Password", required=True, parent=None):
    input_widget = PasswordField("Enter password", parent)
    return FormField(input_widget, label, required, parent)


def create_dropdown_field(items=None, label="", required=False, parent=None):
    input_widget = ModernComboBox(parent)
    if items:
        input_widget.addItems(items)
    return FormField(input_widget, label, required, parent)


def create_number_field(min_val=0, max_val=100, label="", required=False, parent=None):
    input_widget = ModernSpinBox(min_val, max_val, parent)
    return FormField(input_widget, label, required, parent)
