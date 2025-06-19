# ui/styles/theme.py - Ultra Modern Design System with Dimensional Effects (Updated for White, Purple, Black Theme)


class UltraModernColors:
    """Advanced color palette with luminous effects (White, Purple, Black Theme)"""

    # Primary holographic gradients - Adjusted for purple/white/black
    # เน้นสีม่วง, ขาว, ดำ
    PRIMARY_GLOW = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a1a1a, stop:0.3 #4a004a, stop:0.6 #8a2be2, stop:1 #d8bfd8)"
    SECONDARY_GLOW = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e0e0e0, stop:0.5 #c8a2c8, stop:1 #4a004a)"

    # Neon accent colors - Adjusted for new theme
    NEON_BLUE = "#9370DB"  # Medium Purple
    NEON_PURPLE = "#8A2BE2"  # Blue Violet
    NEON_PINK = "#DA70D6"  # Orchid
    NEON_GREEN = "#A0EEA0"  # Light Green (can be adjusted if too bright)
    NEON_YELLOW = "#FFFF99"  # Pale Yellow

    # Glassmorphism backgrounds - Adjusted for new theme and background image transparency
    GLASS_BG = "rgba(255, 255, 255, 0.05)"  # Very subtle white
    GLASS_BG_DARK = "rgba(0, 0, 0, 0.4)"  # Darker background for contrast
    GLASS_BORDER = "rgba(200, 200, 200, 0.3)"  # Lighter border for definition

    # Neural network inspired gradients - Adjusted for new theme
    NEURAL_GRADIENT_DARK = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0a0a0a, stop:0.5 #2a002a, stop:1 #0a0a0a)"
    NEURAL_GRADIENT_LIGHT = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f0f0f0, stop:0.5 #d8bfd8, stop:1 #f0f0f0)"

    # Text and general colors
    TEXT_PRIMARY = "#FFFFFF"  # White text
    TEXT_SECONDARY = "#C0C0C0"  # Light gray for secondary text
    TEXT_ACCENT = "#DDA0DD"  # Plum for accents
    BORDER_COLOR = "rgba(150, 150, 150, 0.2)"  # Subtle border
    HIGHLIGHT_COLOR = "#8A2BE2"  # Blue Violet for highlights
    ERROR_COLOR = "#FF6347"  # Tomato Red for errors
    SUCCESS_COLOR = "#7CFC00"  # Lawn Green for success


def apply_ultra_modern_theme(app):
    """Apply a sophisticated ultra-modern theme to the QApplication with the new color palette."""
    app.setStyleSheet(
        f"""
        QMainWindow {{
            background: transparent; /* Handled by main.py for image background */
            color: {UltraModernColors.TEXT_PRIMARY};
            font-family: 'Inter', 'Segoe UI', sans-serif;
            font-size: 14px;
        }}
        QWidget {{
            background: transparent;
            color: {UltraModernColors.TEXT_PRIMARY};
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }}
        QLabel {{
            color: {UltraModernColors.TEXT_PRIMARY};
        }}
        QPushButton {{
            {get_ultra_modern_button_style('primary')}
        }}
        QLineEdit, QTextEdit, QComboBox {{
            {get_ultra_modern_input_style()}
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
        }}
        QToolTip {{
            background-color: {UltraModernColors.NEURAL_GRADIENT_DARK};
            color: {UltraModernColors.TEXT_PRIMARY};
            border: 1px solid {UltraModernColors.NEON_PURPLE};
            border-radius: 5px;
            padding: 5px;
        }}
        QScrollArea {{
            border: none;
            background: transparent;
        }}
        QScrollBar:vertical {{
            border: none;
            background: {UltraModernColors.GLASS_BG_DARK};
            width: 10px;
            margin: 0px 0px 0px 0px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical {{
            background: {UltraModernColors.NEON_PURPLE};
            min-height: 20px;
            border-radius: 5px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            background: none;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
        QStatusBar {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 rgba(0, 0, 0, 0.6),
                                        stop:0.5 {UltraModernColors.NEON_PURPLE},
                                        stop:1 rgba(0, 0, 0, 0.6));
            color: {UltraModernColors.TEXT_PRIMARY};
            border-top: 1px solid {UltraModernColors.NEON_PURPLE};
            padding: 5px;
            font-weight: bold;
        }}
        """
    )


def get_ultra_modern_card_style(variant="default"):
    """
    Generates a QFrame stylesheet for a futuristic, holographic card effect.
    Uses glassmorphism for background with subtle border and shadow.
    """
    if variant == "default":
        return f"""
            QFrame {{
                background: {UltraModernColors.GLASS_BG};
                border: 1px solid {UltraModernColors.GLASS_BORDER};
                border-radius: 15px;
                padding: 15px;
                color: {UltraModernColors.TEXT_PRIMARY};
            }}
        """
    elif variant == "highlight":
        return f"""
            QFrame {{
                background: {UltraModernColors.GLASS_BG_DARK};
                border: 2px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 15px;
                padding: 15px;
                color: {UltraModernColors.TEXT_PRIMARY};
            }}
        """
    elif variant == "success":
        return f"""
            QFrame {{
                background: rgba(124, 252, 0, 0.1); /* Lawn Green transparent */
                border: 1px solid {UltraModernColors.SUCCESS_COLOR};
                border-radius: 15px;
                padding: 15px;
                color: {UltraModernColors.TEXT_PRIMARY};
            }}
        """
    elif variant == "error":
        return f"""
            QFrame {{
                background: rgba(255, 99, 71, 0.1); /* Tomato Red transparent */
                border: 1px solid {UltraModernColors.ERROR_COLOR};
                border-radius: 15px;
                padding: 15px;
                color: {UltraModernColors.TEXT_PRIMARY};
            }}
        """
    return ""


def get_ultra_modern_button_style(variant="primary", size="md"):
    """
    Generates a QPushButton stylesheet with futuristic gradient effects.
    """
    padding = "10px 20px"
    font_size = "14px"
    if size == "lg":
        padding = "12px 24px"
        font_size = "16px"
    elif size == "sm":
        padding = "8px 16px"
        font_size = "12px"

    base_style = f"""
        QPushButton {{
            border-radius: 10px;
            padding: {padding};
            font-size: {font_size};
            font-weight: bold;
        }}
        QPushButton:hover {{
            /* We handle hover effects using QPropertyAnimation or QGraphicsEffect where possible */
        }}
        QPushButton:pressed {{
            /* We handle pressed effects using QPropertyAnimation or QGraphicsEffect where possible */
        }}
    """
    if variant == "primary":
        return (
            base_style
            + f"""
            QPushButton {{
                background: {UltraModernColors.PRIMARY_GLOW};
                color: {UltraModernColors.TEXT_PRIMARY};
                border: 1px solid {UltraModernColors.NEON_PURPLE};
            }}
            QPushButton:hover {{
                background: {UltraModernColors.SECONDARY_GLOW};
                border: 1px solid {UltraModernColors.NEON_PINK};
            }}
        """
        )
    elif variant == "secondary":
        return (
            base_style
            + f"""
            QPushButton {{
                background: {UltraModernColors.NEURAL_GRADIENT_DARK};
                color: {UltraModernColors.TEXT_SECONDARY};
                border: 1px solid {UltraModernColors.GLASS_BORDER};
            }}
            QPushButton:hover {{
                background: {UltraModernColors.GLASS_BG_DARK};
                border: 1px solid {UltraModernColors.NEON_BLUE};
                color: {UltraModernColors.TEXT_PRIMARY};
            }}
        """
        )
    elif variant == "ghost":
        return (
            base_style
            + f"""
            QPushButton {{
                background: transparent;
                color: {UltraModernColors.TEXT_ACCENT};
                border: 1px solid {UltraModernColors.GLASS_BORDER};
            }}
            QPushButton:hover {{
                background: {UltraModernColors.GLASS_BG};
                color: {UltraModernColors.NEON_PURPLE};
                border: 1px solid {UltraModernColors.NEON_PURPLE};
            }}
        """
        )
    return base_style


def get_ultra_modern_input_style():
    """
    Generates a stylesheet for QLineEdit, QTextEdit, QComboBox with a modern, clean look.
    """
    return f"""
        QLineEdit, QTextEdit, QComboBox {{
            background-color: {UltraModernColors.GLASS_BG_DARK};
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            border-radius: 8px;
            padding: 8px 12px;
            color: {UltraModernColors.TEXT_PRIMARY};
            selection-background-color: {UltraModernColors.HIGHLIGHT_COLOR};
            selection-color: {UltraModernColors.TEXT_PRIMARY};
        }}
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border: 1px solid {UltraModernColors.NEON_PURPLE};
            background-color: rgba(0, 0, 0, 0.5); /* Slightly darker on focus */
        }}
        QComboBox::drop-down {{
            border: 0px; /* No border for the arrow button */
        }}
        QComboBox::down-arrow {{
            /* Simple white down arrow SVG as base64 */
            image: url(data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeD0iMHB4IiB5PSIwcHgiIHdpZHRoPSIxMnB4IiBoZWlnaHQ9IjEycHgiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZW5hYmxlLWJhY2tncm91bmQ9Im5ldyAwIDAgMTIgMTIiIHhtbDpzcGFjZT0icHJlc2VydmUiPjxwYXRoIGZpbGw9IiNGRkZGRkYiIGQ9Ik02IDguNkwxLjUgNC4xTDIuNSA0bDYuNSA2LjVsMS41LTIuMkw2IDguNkwxLjUgNC4xTDIuNSA0bDYuNS02LjVjLTEuMS0xLjEtMi43LTIuNC01LTJjLTIuMy0wLjQtMy45IDAuOC01IDJjLTEuMSAxLjItMC41IDIuNyAxIDQuMWwxLjUgNC4yTDYuNSA2LjVsLTQuNi00LjYgNi40IDYuNFoiLz48L3N2Zz4=);
        }}
        QComboBox::on {{ /* When combobox is open */
            border: 1px solid {UltraModernColors.NEON_PURPLE};
        }}
        QComboBox QAbstractItemView {{
            background-color: {UltraModernColors.GLASS_BG_DARK};
            border: 1px solid {UltraModernColors.NEON_PURPLE};
            border-radius: 8px;
            selection-background-color: {UltraModernColors.HIGHLIGHT_COLOR};
            color: {UltraModernColors.TEXT_PRIMARY};
            padding: 5px;
        }}
    """


def get_neon_checkbox_style():
    """
    Generates a stylesheet for QCheckBox with a neon, futuristic look.
    """
    return f"""
        QCheckBox {{
            spacing: 8px;
            color: {UltraModernColors.TEXT_PRIMARY};
            font-weight: bold;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 1px solid {UltraModernColors.NEON_BLUE};
            background-color: rgba(0, 0, 0, 0.2);
        }}
        QCheckBox::indicator:hover {{
            border: 1px solid {UltraModernColors.NEON_PURPLE};
        }}
        QCheckBox::indicator:checked {{
            background-color: {UltraModernColors.NEON_GREEN};
            border: 1px solid {UltraModernColors.NEON_GREEN};
            image: url(data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJMYXllcl8xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB4PSIwcHgiIHk9IjBweCIKCSB2aWV3Qm94PSIwIDAgNTAgNTAiIGVuYWJsZS1iYWNrZ3JvdW5kPSJuZXcgMCAwIDUwIDUwIiB4bWw6c3BhY2U9InByZXNlcnZlIj4KPHN0eWxlIHR5cGU9InRleHQvY3NzIj4KCS5zdDB7ZmlsbDojZmZmZmZmO30KPC9zdHlsZT4KPHBhdGggY2xhc3M9InN0MCIgZD0iTTIxLjMsMzkuMkwxMC4yLDI3LjlsNC4zLTQuMmw2LjgsNi44TDQ0LjcsMTAuM2w0LjMsNC4zTDIxLjMsMzkuMnoiLz4KPC9zdmc+); /* White checkmark */
        }}
        QCheckBox::indicator:disabled {{
            border: 1px solid rgba(150, 150, 150, 0.3);
            background-color: rgba(0, 0, 0, 0.1);
        }}
        QCheckBox:disabled {{
            color: rgba(150, 150, 150, 0.5);
        }}
    """


def get_holographic_progress_style():
    """
    Generates a stylesheet for QProgressBar with a holographic, glowing effect.
    """
    return f"""
        QProgressBar {{
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid {UltraModernColors.GLASS_BORDER};
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
                stop:1 {UltraModernColors.NEON_BLUE}
            );
            border-radius: 8px;
            /* Removed transition here */
        }}
    """


def get_holographic_tab_style():
    """
    Generates a stylesheet for QTabWidget and QTabBar with a modern, glass-like appearance.
    """
    return f"""
        QTabWidget::pane {{
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            background: {UltraModernColors.GLASS_BG_DARK};
            border-radius: 15px;
            margin-top: -1px; /* Overlap with tab bar border */
        }}
        QTabBar::tab {{
            background: {UltraModernColors.GLASS_BG};
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            border-bottom-color: {UltraModernColors.GLASS_BORDER}; /* Same as pane border */
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            padding: 8px 15px;
            color: {UltraModernColors.TEXT_SECONDARY};
            font-weight: bold;
            margin-right: 2px;
            /* Removed transition here */
        }}
        QTabBar::tab:selected {{
            background: {UltraModernColors.GLASS_BG_DARK};
            border-bottom-color: transparent; /* Makes selected tab look connected to pane */
            color: {UltraModernColors.TEXT_PRIMARY};
        }}
        QTabBar::tab:hover:!selected {{
            background: rgba(255, 255, 255, 0.1);
            color: {UltraModernColors.NEON_BLUE};
        }}
    """


def get_holographic_groupbox_style():
    """
    Generates a stylesheet for QGroupBox with a subtle holographic border and title styling.
    """
    return f"""
        QGroupBox {{
            background: {UltraModernColors.GLASS_BG_DARK};
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            border-radius: 15px;
            margin-top: 25px; /* Space for the title */
            padding-top: 15px;
            color: {UltraModernColors.TEXT_PRIMARY};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center; /* Position the title at the top center */
            padding: 0 10px;
            background-color: {UltraModernColors.NEURAL_GRADIENT_DARK};
            border: 1px solid {UltraModernColors.NEON_PURPLE};
            border-radius: 8px;
            color: {UltraModernColors.TEXT_ACCENT};
            font-weight: bold;
            font-size: 13px;
        }}
    """


# Legacy compatibility functions
def get_modern_card_style(variant="default"):
    return get_ultra_modern_card_style(variant)


def get_modern_button_style(variant="primary", size="md"):
    return get_ultra_modern_button_style(variant, size)


def get_modern_input_style():
    return get_ultra_modern_input_style()


def get_modern_progress_style():
    return get_holographic_progress_style()


def get_modern_log_style():
    # CyberLogConsole has its own style defined internally
    # This function can return a generic style or empty string if not needed
    return ""  # No specific modern log style needed here, CyberLogConsole has its own.


def get_modern_tab_style():
    return get_holographic_tab_style()


def get_modern_checkbox_style():
    return get_neon_checkbox_style()


def get_modern_groupbox_style():
    return get_holographic_groupbox_style()


# Additional compatibility aliases
get_card_style = get_ultra_modern_card_style
get_gradient_button_style = get_ultra_modern_button_style
get_input_style = get_ultra_modern_input_style
get_combobox_style = get_ultra_modern_input_style  # ComboBox uses input style
get_checkbox_style = get_neon_checkbox_style
get_progress_bar_style = get_holographic_progress_style
get_textedit_style = get_ultra_modern_input_style  # QTextEdit uses input style
get_table_widget_style = (
    lambda: """
    QTableWidget {
        background-color: rgba(0, 0, 0, 0.4);
        border: 1px solid #00d4ff;
        border-radius: 8px;
        gridline-color: rgba(0, 212, 255, 0.1);
        color: #E0E0E0;
        selection-background-color: #00d4ff;
        selection-color: #FFFFFF;
    }
    QHeaderView::section {
        background-color: rgba(0, 0, 0, 0.6);
        color: #00ff9d;
        padding: 5px;
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-bottom: none;
    }
    QTableWidget::item {
        padding: 5px;
    }
    QTableWidget::item:selected {
        background-color: rgba(0, 212, 255, 0.3);
    }
"""
)
