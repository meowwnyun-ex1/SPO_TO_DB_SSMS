# ui/styles/theme.py - Ultra Modern Design System (Enhanced)
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor, QPalette


class UltraModernColors:
    # Enhanced glassmorphism colors
    GLASS_BG = "rgba(15, 15, 15, 0.85)"  # เข้มขึ้น แต่ยังโปร่งใส
    GLASS_BG_DARK = "rgba(10, 10, 10, 0.92)"  # เข้มขึ้นเล็กน้อย
    GLASS_BG_LIGHT = "rgba(25, 25, 25, 0.75)"  # สำหรับ hover
    GLASS_BORDER = "rgba(255, 255, 255, 0.15)"  # border นุ่มขึ้น
    GLASS_BORDER_BRIGHT = "rgba(255, 255, 255, 0.25)"  # สำหรับ focus

    # Enhanced neon colors
    NEON_BLUE = "#00D4FF"  # สีฟ้าสดใส
    NEON_PURPLE = "#9D4EDD"  # ม่วงนุ่มขึ้น
    NEON_PINK = "#FF006E"  # ชมพูสดใส
    NEON_GREEN = "#00F5A0"  # เขียวสดใส
    NEON_YELLOW = "#FFD23F"  # เหลืองอบอุ่น

    # Text colors
    TEXT_PRIMARY = "#E0E0E0"  # สีเทาอ่อนสำหรับข้อความหลัก
    TEXT_SECONDARY = "#A0A0A0"  # สีเทาสำหรับข้อความรอง
    TEXT_SECONDARY_ALT = "#707070"  # สีเทาเข้มขึ้นสำหรับข้อความรองอื่นๆ

    # Status colors
    SUCCESS_COLOR = "#00FF7F"  # Spring Green
    ERROR_COLOR = "#FF6347"  # Tomato
    WARNING_COLOR = "#FFD700"  # Gold

    # Gradient definitions
    PRIMARY_GRADIENT = (
        f"qlineargradient(x1:0, y1:0, x2:1, y2:1, "
        f"stop:0 {NEON_BLUE}, stop:1 {NEON_PURPLE})"
    )
    SECONDARY_GRADIENT = (
        f"qlineargradient(x1:0, y1:0, x2:1, y2:1, "
        f"stop:0 {NEON_GREEN}, stop:1 {NEON_YELLOW})"
    )
    ERROR_GRADIENT = (
        f"qlineargradient(x1:0, y1:0, x2:1, y2:1, "
        f"stop:0 {ERROR_COLOR}, stop:1 {NEON_PINK})"
    )
    SUCCESS_GRADIENT = (
        f"qlineargradient(x1:0, y1:0, x2:1, y2:1, "
        f"stop:0 {SUCCESS_COLOR}, stop:1 {NEON_GREEN})"
    )

    # Hover/Press effects (defined in CSS for simplicity)
    # No direct colors here, but rather patterns for use in styles.


def apply_ultra_modern_theme(app: QApplication):
    """Applies the ultra-modern theme globally to the QApplication."""
    palette = app.palette()

    # Set overall background and foreground colors
    palette.setColor(QPalette.ColorRole.Window, QColor(UltraModernColors.GLASS_BG_DARK))
    palette.setColor(
        QPalette.ColorRole.WindowText, QColor(UltraModernColors.TEXT_PRIMARY)
    )
    palette.setColor(
        QPalette.ColorRole.Base, QColor(UltraModernColors.GLASS_BG_DARK)
    )  # For input fields background
    palette.setColor(
        QPalette.ColorRole.Text, QColor(UltraModernColors.TEXT_PRIMARY)
    )  # For text in input fields
    palette.setColor(
        QPalette.ColorRole.Button, QColor(UltraModernColors.NEON_BLUE)
    )  # Default button color
    palette.setColor(
        QPalette.ColorRole.ButtonText, QColor("#FFFFFF")
    )  # Button text color
    palette.setColor(
        QPalette.ColorRole.Highlight, QColor(UltraModernColors.NEON_PURPLE)
    )  # Selection highlight
    palette.setColor(
        QPalette.ColorRole.HighlightedText, QColor("#FFFFFF")
    )  # Selected text color

    app.setPalette(palette)

    # Apply global stylesheet for consistent looks
    app.setStyleSheet(get_global_stylesheet())


def get_global_stylesheet():
    """Returns the global stylesheet for the application."""
    return f"""
        * {{
            font-family: "Segoe UI", sans-serif;
            color: {UltraModernColors.TEXT_PRIMARY};
            border-radius: 8px; /* Global rounded corners */
        }}
        QMainWindow {{
            background: transparent; /* Handled by main.py for image */
        }}
        QWidget {{
            background-color: transparent; /* Default transparent for layering */
        }}
        QMessageBox {{
            background-color: {UltraModernColors.GLASS_BG_DARK};
            color: {UltraModernColors.TEXT_PRIMARY};
            border: 1px solid {UltraModernColors.NEON_PURPLE};
            border-radius: 10px;
        }}
        QMessageBox QLabel {{
            color: {UltraModernColors.TEXT_PRIMARY};
        }}
        QMessageBox QPushButton {{
            {get_modern_button_style('primary', 'md')}
            padding: 8px 20px;
            margin: 5px;
        }}
        QToolTip {{
            background-color: {UltraModernColors.GLASS_BG_DARK};
            color: {UltraModernColors.TEXT_PRIMARY};
            border: 1px solid {UltraModernColors.NEON_BLUE};
            border-radius: 5px;
            padding: 5px;
            opacity: 200; /* Fully opaque */
        }}
        QScrollArea {{
            border: none;
        }}
        QScrollBar:vertical {{
            border: 1px solid {UltraModernColors.GLASS_BORDER_BRIGHT};
            background: {UltraModernColors.GLASS_BG_DARK};
            width: 10px;
            margin: 15px 0 15px 0;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical {{
            background: {UltraModernColors.NEON_PURPLE};
            border-radius: 5px;
            min-height: 20px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            background: none;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
        QScrollBar:horizontal {{
            border: 1px solid {UltraModernColors.GLASS_BORDER_BRIGHT};
            background: {UltraModernColors.GLASS_BG_DARK};
            height: 10px;
            margin: 0 15px 0 15px;
            border-radius: 5px;
        }}
        QScrollBar::handle:horizontal {{
            background: {UltraModernColors.NEON_BLUE};
            border-radius: 5px;
            min-width: 20px;
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            background: none;
        }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: none;
    }}
    """


def get_modern_button_style(variant="primary", size="md"):
    """Generates modern button styles based on variant and size."""
    base_style = f"""
        QPushButton {{
            border: 1px solid {UltraModernColors.GLASS_BORDER_BRIGHT};
            border-radius: 12px;
            padding: 10px 20px;
            transition: all 0.2s ease-in-out;
            color: {UltraModernColors.TEXT_PRIMARY};
            font-weight: 600;
        }}
        QPushButton:hover {{
            border-color: {UltraModernColors.NEON_BLUE};
            box-shadow: 0 0 15px {UltraModernColors.NEON_BLUE};
        }}
        QPushButton:pressed {{
            transform: translateY(1px);
        }}
        QPushButton:disabled {{
            background-color: {UltraModernColors.GLASS_BG_DARK};
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            color: {UltraModernColors.TEXT_SECONDARY_ALT};
            opacity: 0.6;
        }}
    """

    # Variant specific styles
    if variant == "primary":
        variant_style = f"""
            QPushButton {{
                background: {UltraModernColors.PRIMARY_GRADIENT};
                color: #FFFFFF;
                border: 1px solid {UltraModernColors.NEON_PURPLE};
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {UltraModernColors.NEON_BLUE.replace('FF', 'E0')}, stop:1 {UltraModernColors.NEON_PURPLE.replace('DD', 'C0')}); /* Slightly desaturated hover */
                border-color: {UltraModernColors.NEON_BLUE};
            }}
        """
    elif variant == "secondary":
        variant_style = f"""
            QPushButton {{
                background: {UltraModernColors.GLASS_BG_LIGHT};
                border: 1px solid {UltraModernColors.NEON_GREEN};
                color: {UltraModernColors.NEON_GREEN};
            }}
            QPushButton:hover {{
                background-color: {UltraModernColors.NEON_GREEN};
                color: {UltraModernColors.GLASS_BG_DARK};
            }}
        """
    elif variant == "ghost":
        variant_style = f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {UltraModernColors.GLASS_BORDER};
                color: {UltraModernColors.TEXT_PRIMARY};
            }}
            QPushButton:hover {{
                background-color: {UltraModernColors.GLASS_BG_LIGHT};
                border-color: {UltraModernColors.TEXT_PRIMARY};
            }}
        """
    else:  # Default to primary
        variant_style = ""

    # Size specific styles
    size_style = ""
    if size == "sm":
        size_style = "padding: 6px 12px; font-size: 12px;"
    elif size == "lg":
        size_style = "padding: 14px 28px; font-size: 16px;"

    return f"{base_style} {variant_style} QPushButton {{ {size_style} }}"


def get_modern_input_style():
    """Generates modern input field (QLineEdit, QTextEdit, QComboBox) styles."""
    return f"""
        QLineEdit, QTextEdit, QComboBox, QSpinBox {{
            background-color: {UltraModernColors.GLASS_BG_DARK};
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            border-radius: 8px;
            padding: 8px 12px;
            color: {UltraModernColors.TEXT_PRIMARY};
            selection-background-color: {UltraModernColors.NEON_PURPLE};
            selection-color: white;
        }}
        QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {{
            border: 1px solid {UltraModernColors.NEON_BLUE};
        }}
        QComboBox::drop-down {{
            border: 0px; /* No border for dropdown */
        }}
        QComboBox::down-arrow {{
            image: url(resources/icons/arrow_down.png); /* Placeholder for custom arrow */
            /* Or use a font icon like FontAwesome or Phosphor icons */
        }}
        QComboBox QAbstractItemView {{
            border: 1px solid {UltraModernColors.NEON_BLUE};
            background-color: {UltraModernColors.GLASS_BG_DARK};
            selection-background-color: {UltraModernColors.NEON_PURPLE};
            color: {UltraModernColors.TEXT_PRIMARY};
            outline: 0; /* Remove dotted outline on focus */
        }}
        QSpinBox::up-button, QSpinBox::down-button {{
            subcontrol-origin: border;
            width: 20px;
            border-left: 1px solid {UltraModernColors.GLASS_BORDER};
            background: {UltraModernColors.GLASS_BG_LIGHT};
            border-top-right-radius: 8px;
            border-bottom-right-radius: 8px;
        }}
        QSpinBox::up-arrow, QSpinBox::down-arrow {{
            width: 12px;
            height: 12px;
            color: {UltraModernColors.TEXT_PRIMARY};
        }}
        QSpinBox::up-arrow {{
            image: url(resources/icons/arrow_up.png); /* Placeholder */
        }}
        QSpinBox::down-arrow {{
            image: url(resources/icons/arrow_down.png); /* Placeholder */
        }}
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
            background-color: {UltraModernColors.NEON_BLUE};
        }}
    """


def get_modern_checkbox_style():
    """Generates modern checkbox style."""
    return f"""
        QCheckBox {{
            spacing: 5px;
            color: {UltraModernColors.TEXT_PRIMARY};
            font-size: 14px;
            padding: 5px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 1px solid {UltraModernColors.GLASS_BORDER_BRIGHT};
            background-color: {UltraModernColors.GLASS_BG_DARK};
        }}
        QCheckBox::indicator:unchecked {{
            background-color: {UltraModernColors.GLASS_BG_DARK};
        }}
        QCheckBox::indicator:checked {{
            background-color: {UltraModernColors.NEON_GREEN}; /* Use a vibrant color when checked */
            border: 1px solid {UltraModernColors.NEON_GREEN};
            image: url(resources/icons/check_mark.png); /* Placeholder for checkmark icon */
            /* Or use unicode character: content: "\\2713"; */
        }}
        QCheckBox::indicator:hover {{
            border-color: {UltraModernColors.NEON_BLUE};
        }}
        QCheckBox::indicator:disabled {{
            background-color: {UltraModernColors.GLASS_BG_DARK};
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            opacity: 0.5;
        }}
    """


def get_modern_tab_style():
    """Generates modern tab widget style."""
    return f"""
        QTabWidget::pane {{ /* The tab widget frame */
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            border-radius: 10px;
            background-color: {UltraModernColors.GLASS_BG};
            margin-top: -1px; /* Overlap with tabs */
        }}
        QTabWidget::tab-bar {{
            left: 5px; /* Move tabs a bit to the right */
        }}
        QTabBar::tab {{
            background: {UltraModernColors.GLASS_BG_DARK};
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            border-bottom-color: {UltraModernColors.GLASS_BORDER}; /* same as pane */
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            padding: 8px 15px;
            min-width: 80px;
            color: {UltraModernColors.TEXT_SECONDARY};
            margin-right: 2px;
        }}
        QTabBar::tab:selected {{
            background: {UltraModernColors.PRIMARY_GRADIENT};
            border-color: {UltraModernColors.NEON_PURPLE};
            border-bottom-color: transparent; /* Make bottom transparent to blend with pane */
            color: white;
            font-weight: bold;
        }}
        QTabBar::tab:hover {{
            background: {UltraModernColors.GLASS_BG_LIGHT};
            border-color: {UltraModernColors.NEON_BLUE};
        }}
        QTabBar::tab:!selected {{
            margin-top: 2px; /* make non-selected tabs look sunken */
        }}
    """


def get_modern_card_style():
    """Generates modern card/frame style."""
    return f"""
        QWidget {{ /* Applied to QWidget acting as a card */
            background: {UltraModernColors.GLASS_BG_DARK};
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* Soft shadow */
            padding: 5px; /* Inner padding for content */
            transition: all 0.2s ease-in-out;
        }}
        QWidget:hover {{
            border-color: {UltraModernColors.NEON_BLUE};
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3); /* Enhanced shadow on hover */
            transform: translateY(-2px); /* Slight lift effect */
        }}
    """


def get_modern_groupbox_style():  # This function is present
    """Generates modern group box style."""
    return f"""
        QGroupBox {{
            background: {UltraModernColors.GLASS_BG_DARK};
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            border-radius: 16px;
            margin-top: 30px; /* Space for title */
            padding-top: 20px; /* Padding below title */
            color: {UltraModernColors.TEXT_PRIMARY};
            font-weight: 500;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center; /* Center the title */
            padding: 8px 16px;
            background: {UltraModernColors.PRIMARY_GRADIENT};
            border: 1px solid {UltraModernColors.NEON_PURPLE};
            border-radius: 12px;
            color: #FFFFFF;
            font-weight: 600;
            font-size: 14px;
        }}
    """


def get_holographic_progress_style():
    """Generates holographic progress bar style."""
    return f"""
        QProgressBar {{
            background: {UltraModernColors.GLASS_BG_DARK};
            border: 1px solid {UltraModernColors.NEON_PURPLE};
            border-radius: 8px;
            height: 20px;
            text-align: center;
            color: {UltraModernColors.TEXT_PRIMARY};
            font-weight: bold;
        }}
        QProgressBar::chunk {{
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {UltraModernColors.NEON_PURPLE},
                stop:1 {UltraModernColors.NEON_PINK}
            );
            border-radius: 8px;
        }}
    """


# Compatibility aliases
get_ultra_modern_card_style = get_modern_card_style
get_ultra_modern_button_style = get_modern_button_style
get_ultra_modern_input_style = get_modern_input_style
get_holographic_groupbox_style = get_modern_groupbox_style  # Ensure this alias exists and points to the correct function
