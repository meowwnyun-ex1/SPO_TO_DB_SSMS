# ui/styles/theme.py - Optimized for 900x500 displays
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor, QPalette


class UltraModernColors:
    # Enhanced glassmorphism colors
    GLASS_BG = "rgba(15, 15, 15, 0.85)"
    GLASS_BG_DARK = "rgba(10, 10, 10, 0.92)"
    GLASS_BG_LIGHT = "rgba(25, 25, 25, 0.75)"
    GLASS_BORDER = "rgba(255, 255, 255, 0.15)"
    GLASS_BORDER_BRIGHT = "rgba(255, 255, 255, 0.25)"

    # Enhanced neon colors
    NEON_BLUE = "#00D4FF"
    NEON_PURPLE = "#9D4EDD"
    NEON_PINK = "#FF006E"
    NEON_GREEN = "#00F5A0"
    NEON_YELLOW = "#FFD23F"

    # Text colors
    TEXT_PRIMARY = "#E0E0E0"
    TEXT_SECONDARY = "#A0A0A0"
    TEXT_SECONDARY_ALT = "#707070"

    # Status colors
    SUCCESS_COLOR = "#00FF7F"
    ERROR_COLOR = "#FF6347"
    WARNING_COLOR = "#FFD700"

    # Gradients
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


class CompactScaling:
    """Scaling values optimized for 900x500 displays"""

    # Font sizes (significantly reduced)
    FONT_SIZE_TINY = 7
    FONT_SIZE_SMALL = 8
    FONT_SIZE_NORMAL = 9
    FONT_SIZE_MEDIUM = 10
    FONT_SIZE_LARGE = 11
    FONT_SIZE_XLARGE = 12

    # Spacing (minimal for compact layout)
    SPACING_TINY = 1
    SPACING_SMALL = 2
    SPACING_NORMAL = 3
    SPACING_MEDIUM = 4
    SPACING_LARGE = 5

    # Margins (minimal)
    MARGIN_TINY = 2
    MARGIN_SMALL = 3
    MARGIN_NORMAL = 4
    MARGIN_MEDIUM = 5
    MARGIN_LARGE = 6

    # Widget dimensions (reduced)
    BUTTON_HEIGHT_SMALL = 20
    BUTTON_HEIGHT_NORMAL = 24
    BUTTON_HEIGHT_LARGE = 28

    STATUS_CARD_HEIGHT = 40
    PROGRESS_BAR_HEIGHT = 12
    TAB_HEIGHT = 24
    NAVBAR_HEIGHT = 32


def apply_ultra_modern_theme(app: QApplication):
    """Apply ultra-modern theme optimized for compact displays"""
    palette = app.palette()

    palette.setColor(QPalette.ColorRole.Window, QColor(UltraModernColors.GLASS_BG_DARK))
    palette.setColor(
        QPalette.ColorRole.WindowText, QColor(UltraModernColors.TEXT_PRIMARY)
    )
    palette.setColor(QPalette.ColorRole.Base, QColor(UltraModernColors.GLASS_BG_DARK))
    palette.setColor(QPalette.ColorRole.Text, QColor(UltraModernColors.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Button, QColor(UltraModernColors.NEON_BLUE))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#FFFFFF"))
    palette.setColor(
        QPalette.ColorRole.Highlight, QColor(UltraModernColors.NEON_PURPLE)
    )
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))

    app.setPalette(palette)
    app.setStyleSheet(get_global_stylesheet())


def get_global_stylesheet():
    """Global stylesheet optimized for compact displays"""
    return f"""
        * {{
            font-family: "Segoe UI", sans-serif;
            color: {UltraModernColors.TEXT_PRIMARY};
            border-radius: 2px;
        }}
        QMainWindow {{
            background: transparent;
        }}
        QWidget {{
            background-color: transparent;
        }}
        QMessageBox {{
            background-color: {UltraModernColors.GLASS_BG_DARK};
            color: {UltraModernColors.TEXT_PRIMARY};
            border: 1px solid {UltraModernColors.NEON_PURPLE};
            border-radius: 4px;
        }}
        QMessageBox QLabel {{
            color: {UltraModernColors.TEXT_PRIMARY};
            font-size: {CompactScaling.FONT_SIZE_NORMAL}px;
        }}
        QMessageBox QPushButton {{
            {get_modern_button_style('primary', 'sm')}
            padding: 2px 8px;
            margin: 1px;
        }}
        QToolTip {{
            background-color: {UltraModernColors.GLASS_BG_DARK};
            color: {UltraModernColors.TEXT_PRIMARY};
            border: 1px solid {UltraModernColors.NEON_BLUE};
            border-radius: 2px;
            padding: 2px;
            font-size: {CompactScaling.FONT_SIZE_SMALL}px;
        }}
        QScrollArea {{
            border: none;
        }}
        QScrollBar:vertical {{
            border: 1px solid {UltraModernColors.GLASS_BORDER_BRIGHT};
            background: {UltraModernColors.GLASS_BG_DARK};
            width: 6px;
            margin: 6px 0 6px 0;
            border-radius: 3px;
        }}
        QScrollBar::handle:vertical {{
            background: {UltraModernColors.NEON_PURPLE};
            border-radius: 3px;
            min-height: 12px;
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
            height: 6px;
            margin: 0 6px 0 6px;
            border-radius: 3px;
        }}
        QScrollBar::handle:horizontal {{
            background: {UltraModernColors.NEON_BLUE};
            border-radius: 3px;
            min-width: 12px;
        }}
    """


def get_modern_button_style(variant="primary", size="md"):
    """Modern button styles optimized for compact displays"""
    # Base dimensions for compact display
    if size == "sm":
        padding = "2px 6px"
        font_size = f"{CompactScaling.FONT_SIZE_SMALL}px"
        border_radius = "3px"
    elif size == "lg":
        padding = "4px 12px"
        font_size = f"{CompactScaling.FONT_SIZE_MEDIUM}px"
        border_radius = "4px"
    else:  # md
        padding = "3px 8px"
        font_size = f"{CompactScaling.FONT_SIZE_NORMAL}px"
        border_radius = "3px"

    base_style = f"""
        QPushButton {{
            border: 1px solid {UltraModernColors.GLASS_BORDER_BRIGHT};
            border-radius: {border_radius};
            padding: {padding};
            color: {UltraModernColors.TEXT_PRIMARY};
            font-weight: 600;
            font-size: {font_size};
            min-height: {CompactScaling.BUTTON_HEIGHT_SMALL if size == 'sm' else CompactScaling.BUTTON_HEIGHT_NORMAL}px;
        }}
        QPushButton:hover {{
            border-color: {UltraModernColors.NEON_BLUE};
            box-shadow: 0 0 6px {UltraModernColors.NEON_BLUE};
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

    # Variant styles
    if variant == "primary":
        variant_style = f"""
            QPushButton {{
                background: {UltraModernColors.PRIMARY_GRADIENT};
                color: #FFFFFF;
                border: 1px solid {UltraModernColors.NEON_PURPLE};
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 {UltraModernColors.NEON_BLUE}E0, 
                    stop:1 {UltraModernColors.NEON_PURPLE}C0);
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
    elif variant == "danger":
        variant_style = f"""
            QPushButton {{
                background: {UltraModernColors.ERROR_GRADIENT};
                color: #FFFFFF;
                border: 1px solid {UltraModernColors.ERROR_COLOR};
            }}
            QPushButton:hover {{
                background: {UltraModernColors.ERROR_COLOR};
            }}
        """
    else:  # ghost
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

    return f"{base_style} {variant_style}"


def get_modern_input_style():
    """Input field styles optimized for compact displays"""
    return f"""
        QLineEdit, QTextEdit, QComboBox, QSpinBox {{
            background-color: {UltraModernColors.GLASS_BG_DARK};
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            border-radius: 3px;
            padding: 2px 6px;
            color: {UltraModernColors.TEXT_PRIMARY};
            font-size: {CompactScaling.FONT_SIZE_NORMAL}px;
            min-height: 16px;
            selection-background-color: {UltraModernColors.NEON_PURPLE};
            selection-color: white;
        }}
        QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {{
            border: 1px solid {UltraModernColors.NEON_BLUE};
        }}
        QComboBox::drop-down {{
            border: 0px;
            width: 16px;
        }}
        QComboBox::down-arrow {{
            width: 10px;
            height: 10px;
        }}
        QComboBox QAbstractItemView {{
            border: 1px solid {UltraModernColors.NEON_BLUE};
            background-color: {UltraModernColors.GLASS_BG_DARK};
            selection-background-color: {UltraModernColors.NEON_PURPLE};
            color: {UltraModernColors.TEXT_PRIMARY};
            font-size: {CompactScaling.FONT_SIZE_NORMAL}px;
            outline: 0;
        }}
        QSpinBox::up-button, QSpinBox::down-button {{
            width: 12px;
            border-left: 1px solid {UltraModernColors.GLASS_BORDER};
            background: {UltraModernColors.GLASS_BG_LIGHT};
        }}
        QSpinBox::up-arrow, QSpinBox::down-arrow {{
            width: 6px;
            height: 6px;
        }}
    """


def get_modern_checkbox_style():
    """Checkbox style optimized for compact displays"""
    return f"""
        QCheckBox {{
            spacing: 3px;
            color: {UltraModernColors.TEXT_PRIMARY};
            font-size: {CompactScaling.FONT_SIZE_NORMAL}px;
            padding: 1px;
        }}
        QCheckBox::indicator {{
            width: 12px;
            height: 12px;
            border-radius: 2px;
            border: 1px solid {UltraModernColors.GLASS_BORDER_BRIGHT};
            background-color: {UltraModernColors.GLASS_BG_DARK};
        }}
        QCheckBox::indicator:checked {{
            background-color: {UltraModernColors.NEON_GREEN};
            border: 1px solid {UltraModernColors.NEON_GREEN};
        }}
        QCheckBox::indicator:hover {{
            border-color: {UltraModernColors.NEON_BLUE};
        }}
    """


def get_modern_tab_style():
    """Tab widget style optimized for compact displays"""
    return f"""
        QTabWidget::pane {{
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            border-radius: 4px;
            background-color: {UltraModernColors.GLASS_BG};
            margin-top: -1px;
        }}
        QTabWidget::tab-bar {{
            left: 2px;
        }}
        QTabBar::tab {{
            background: {UltraModernColors.GLASS_BG_DARK};
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            border-top-left-radius: 3px;
            border-top-right-radius: 3px;
            padding: 2px 6px;
            min-width: 50px;
            max-height: {CompactScaling.TAB_HEIGHT}px;
            color: {UltraModernColors.TEXT_SECONDARY};
            margin-right: 1px;
            font-size: {CompactScaling.FONT_SIZE_SMALL}px;
        }}
        QTabBar::tab:selected {{
            background: {UltraModernColors.PRIMARY_GRADIENT};
            border-color: {UltraModernColors.NEON_PURPLE};
            border-bottom-color: transparent;
            color: white;
            font-weight: bold;
        }}
        QTabBar::tab:hover {{
            background: {UltraModernColors.GLASS_BG_LIGHT};
            border-color: {UltraModernColors.NEON_BLUE};
        }}
    """


def get_modern_card_style():
    """Card style optimized for compact displays"""
    return f"""
        QWidget {{
            background: {UltraModernColors.GLASS_BG_DARK};
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            border-radius: 4px;
            padding: 2px;
        }}
        QWidget:hover {{
            border-color: {UltraModernColors.NEON_BLUE};
        }}
    """


def get_modern_groupbox_style():
    """Group box style optimized for compact displays"""
    return f"""
        QGroupBox {{
            background: {UltraModernColors.GLASS_BG_DARK};
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            border-radius: 5px;
            margin-top: 12px;
            padding-top: 8px;
            color: {UltraModernColors.TEXT_PRIMARY};
            font-weight: 500;
            font-size: {CompactScaling.FONT_SIZE_NORMAL}px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 2px 6px;
            background: {UltraModernColors.PRIMARY_GRADIENT};
            border: 1px solid {UltraModernColors.NEON_PURPLE};
            border-radius: 4px;
            color: #FFFFFF;
            font-weight: 600;
            font-size: {CompactScaling.FONT_SIZE_SMALL}px;
        }}
    """


def get_holographic_progress_style():
    """Progress bar style optimized for compact displays"""
    return f"""
        QProgressBar {{
            background: {UltraModernColors.GLASS_BG_DARK};
            border: 1px solid {UltraModernColors.NEON_PURPLE};
            border-radius: 3px;
            height: {CompactScaling.PROGRESS_BAR_HEIGHT}px;
            text-align: center;
            color: {UltraModernColors.TEXT_PRIMARY};
            font-weight: bold;
            font-size: {CompactScaling.FONT_SIZE_SMALL}px;
        }}
        QProgressBar::chunk {{
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {UltraModernColors.NEON_PURPLE},
                stop:1 {UltraModernColors.NEON_PINK}
            );
            border-radius: 3px;
        }}
    """


def get_navbar_style():
    """Navigation bar style for compact layout"""
    return f"""
        QWidget {{
            background: {UltraModernColors.GLASS_BG_DARK};
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            border-radius: 4px;
            min-height: {CompactScaling.NAVBAR_HEIGHT}px;
            max-height: {CompactScaling.NAVBAR_HEIGHT}px;
        }}
        QPushButton {{
            background: transparent;
            border: none;
            color: {UltraModernColors.TEXT_SECONDARY};
            font-size: {CompactScaling.FONT_SIZE_SMALL}px;
            padding: 4px 8px;
            margin: 1px;
            border-radius: 2px;
        }}
        QPushButton:hover {{
            background: {UltraModernColors.GLASS_BG_LIGHT};
            color: {UltraModernColors.TEXT_PRIMARY};
        }}
        QPushButton:checked {{
            background: {UltraModernColors.NEON_PURPLE};
            color: white;
            font-weight: bold;
        }}
    """


# Compatibility aliases
get_ultra_modern_card_style = get_modern_card_style
get_ultra_modern_button_style = get_modern_button_style
get_ultra_modern_input_style = get_modern_input_style
get_holographic_groupbox_style = get_modern_groupbox_style
