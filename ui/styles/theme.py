# ui/styles/theme.py - Ultra Modern Design System (Complete)


class UltraModernColors:

    # Primary holographic gradients
    PRIMARY_GLOW = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a1a1a, stop:0.3 #4a004a, stop:0.6 #8a2be2, stop:1 #d8bfd8)"
    SECONDARY_GLOW = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e0e0e0, stop:0.5 #c8a2c8, stop:1 #4a004a)"

    # Neon accent colors - เพิ่มความสดใส
    NEON_BLUE = "#00BFFF"  # Deep Sky Blue
    NEON_PURPLE = "#8A2BE2"  # Blue Violet
    NEON_PINK = "#FF69B4"  # Hot Pink
    NEON_GREEN = "#00FF00"  # Lime Green
    NEON_YELLOW = "#FFD700"  # Gold

    # Glassmorphism backgrounds - เพิ่ม opacity เพื่อ contrast
    GLASS_BG = "rgba(0, 0, 0, 0.8)"  # เข้มขึ้นจาก 0.05
    GLASS_BG_DARK = "rgba(0, 0, 0, 0.9)"  # เข้มขึ้นจาก 0.4
    GLASS_BORDER = "rgba(255, 255, 255, 0.3)"  # ขาวให้ชัดเจน

    # Neural network gradients
    NEURAL_GRADIENT_DARK = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0a0a0a, stop:0.5 #2a002a, stop:1 #0a0a0a)"
    NEURAL_GRADIENT_LIGHT = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f0f0f0, stop:0.5 #d8bfd8, stop:1 #f0f0f0)"

    # Text colors - เพิ่มความคมชัด
    TEXT_PRIMARY = "#FFFFFF"  # Pure White
    TEXT_SECONDARY = "#E0E0E0"  # Light Gray (เพิ่มจาก C0C0C0)
    TEXT_ACCENT = "#F0E68C"  # Khaki (เปลี่ยนจาก DDA0DD)
    BORDER_COLOR = "rgba(255, 255, 255, 0.2)"
    HIGHLIGHT_COLOR = "#8A2BE2"
    ERROR_COLOR = "#FF4500"  # Orange Red (เพิ่มจาก FF6347)
    SUCCESS_COLOR = "#00FF00"  # Lime (เพิ่มจาก 7CFC00)


def apply_ultra_modern_theme(app):
    """Apply ultra-modern theme with high contrast"""
    app.setStyleSheet(
        f"""
        QMainWindow {{
            background: transparent;
            color: {UltraModernColors.TEXT_PRIMARY};
            font-family: 'Segoe UI', sans-serif;
            font-size: 14px;
            font-weight: 500;
        }}
        QWidget {{
            background: transparent;
            color: {UltraModernColors.TEXT_PRIMARY};
            font-family: 'Segoe UI', sans-serif;
        }}
        QLabel {{
            color: {UltraModernColors.TEXT_PRIMARY};
            font-weight: 500;
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
            background: rgba(0, 0, 0, 0.9);
            color: {UltraModernColors.TEXT_PRIMARY};
            border-top: 1px solid {UltraModernColors.NEON_PURPLE};
            padding: 5px;
            font-weight: bold;
        }}
    """
    )


def get_ultra_modern_card_style(variant="default"):
    """Generate QFrame stylesheet for holographic card effect"""
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
                background: rgba(0, 255, 0, 0.1);
                border: 1px solid {UltraModernColors.SUCCESS_COLOR};
                border-radius: 15px;
                padding: 15px;
                color: {UltraModernColors.TEXT_PRIMARY};
            }}
        """
    elif variant == "error":
        return f"""
            QFrame {{
                background: rgba(255, 69, 0, 0.1);
                border: 1px solid {UltraModernColors.ERROR_COLOR};
                border-radius: 15px;
                padding: 15px;
                color: {UltraModernColors.TEXT_PRIMARY};
            }}
        """
    return ""


def get_ultra_modern_button_style(variant="primary", size="md"):
    """Generate QPushButton stylesheet with futuristic gradient effects"""
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
            color: #FFFFFF;
        }}
    """

    if variant == "primary":
        return (
            base_style
            + f"""
            QPushButton {{
                background: {UltraModernColors.NEON_PURPLE};
                border: 1px solid {UltraModernColors.NEON_PURPLE};
            }}
            QPushButton:hover {{
                background: {UltraModernColors.NEON_PINK};
                border: 1px solid {UltraModernColors.NEON_PINK};
            }}
            QPushButton:pressed {{
                background: {UltraModernColors.NEON_BLUE};
            }}
        """
        )
    elif variant == "secondary":
        return (
            base_style
            + f"""
            QPushButton {{
                background: {UltraModernColors.GLASS_BG};
                border: 1px solid {UltraModernColors.GLASS_BORDER};
            }}
            QPushButton:hover {{
                background: {UltraModernColors.GLASS_BG_DARK};
                border: 1px solid {UltraModernColors.NEON_BLUE};
            }}
        """
        )
    elif variant == "ghost":
        return (
            base_style
            + f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {UltraModernColors.GLASS_BORDER};
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid {UltraModernColors.NEON_PURPLE};
            }}
        """
        )
    return base_style


def get_ultra_modern_input_style():
    """Generate stylesheet for QLineEdit, QTextEdit, QComboBox with modern look"""
    return f"""
        QLineEdit, QTextEdit, QComboBox {{
            background-color: {UltraModernColors.GLASS_BG};
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            border-radius: 8px;
            padding: 8px 12px;
            color: {UltraModernColors.TEXT_PRIMARY};
            font-weight: 500;
            selection-background-color: {UltraModernColors.NEON_PURPLE};
            selection-color: #FFFFFF;
        }}
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border: 1px solid {UltraModernColors.NEON_PURPLE};
            background-color: {UltraModernColors.GLASS_BG_DARK};
        }}
        QComboBox::drop-down {{
            border: 0px;
        }}
        QComboBox::down-arrow {{
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTMgNS41TDYgOC41TDkgNS41IiBzdHJva2U9IiNGRkZGRkYiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
        }}
        QComboBox::on {{
            border: 1px solid {UltraModernColors.NEON_PURPLE};
        }}
        QComboBox QAbstractItemView {{
            background-color: {UltraModernColors.GLASS_BG_DARK};
            border: 1px solid {UltraModernColors.NEON_PURPLE};
            border-radius: 8px;
            selection-background-color: {UltraModernColors.NEON_PURPLE};
            color: {UltraModernColors.TEXT_PRIMARY};
            padding: 5px;
        }}
    """


def get_neon_checkbox_style():
    """Generate stylesheet for QCheckBox with neon, futuristic look"""
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
            background-color: {UltraModernColors.GLASS_BG};
        }}
        QCheckBox::indicator:hover {{
            border: 1px solid {UltraModernColors.NEON_PURPLE};
        }}
        QCheckBox::indicator:checked {{
            background-color: {UltraModernColors.NEON_GREEN};
            border: 1px solid {UltraModernColors.NEON_GREEN};
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0iIzAwMDAwMCIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
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
    """Generate stylesheet for QProgressBar with holographic, glowing effect"""
    return f"""
        QProgressBar {{
            background: {UltraModernColors.GLASS_BG};
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


def get_holographic_tab_style():
    """Generate stylesheet for QTabWidget and QTabBar with modern, glass-like appearance"""
    return f"""
        QTabWidget::pane {{
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            background: {UltraModernColors.GLASS_BG_DARK};
            border-radius: 15px;
            margin-top: -1px;
        }}
        QTabBar::tab {{
            background: {UltraModernColors.GLASS_BG};
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            border-bottom-color: {UltraModernColors.GLASS_BORDER};
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            padding: 8px 15px;
            color: {UltraModernColors.TEXT_SECONDARY};
            font-weight: bold;
            margin-right: 2px;
        }}
        QTabBar::tab:selected {{
            background: {UltraModernColors.GLASS_BG_DARK};
            border-bottom-color: transparent;
            color: {UltraModernColors.TEXT_PRIMARY};
        }}
        QTabBar::tab:hover:!selected {{
            background: rgba(255, 255, 255, 0.1);
            color: {UltraModernColors.NEON_BLUE};
        }}
    """


def get_holographic_groupbox_style():
    """Generate stylesheet for QGroupBox with subtle holographic border and title styling"""
    return f"""
        QGroupBox {{
            background: {UltraModernColors.GLASS_BG_DARK};
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            border-radius: 15px;
            margin-top: 25px;
            padding-top: 15px;
            color: {UltraModernColors.TEXT_PRIMARY};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 10px;
            background-color: {UltraModernColors.GLASS_BG_DARK};
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
    return ""


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
    lambda: f"""
    QTableWidget {{
        background-color: {UltraModernColors.GLASS_BG_DARK};
        border: 1px solid {UltraModernColors.NEON_PURPLE};
        border-radius: 8px;
        gridline-color: rgba(138, 43, 226, 0.1);
        color: {UltraModernColors.TEXT_PRIMARY};
        selection-background-color: {UltraModernColors.NEON_PURPLE};
        selection-color: #FFFFFF;
    }}
    QHeaderView::section {{
        background-color: {UltraModernColors.GLASS_BG_DARK};
        color: {UltraModernColors.NEON_GREEN};
        padding: 5px;
        border: 1px solid {UltraModernColors.GLASS_BORDER};
        border-bottom: none;
    }}
    QTableWidget::item {{
        padding: 5px;
    }}
    QTableWidget::item:selected {{
        background-color: rgba(138, 43, 226, 0.3);
    }}
"""
)
