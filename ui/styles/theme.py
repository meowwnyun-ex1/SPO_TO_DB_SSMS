# ui/styles/theme.py - Ultra Modern Design System (Enhanced)


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

    # Gradient definitions
    PRIMARY_GRADIENT = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #9D4EDD, stop:1 #00D4FF)"
    )
    SECONDARY_GRADIENT = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FF006E, stop:1 #FFD23F)"
    )
    SUCCESS_GRADIENT = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00F5A0, stop:1 #00D4FF)"
    )
    ERROR_GRADIENT = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FF006E, stop:1 #FF4081)"
    )

    # Text colors
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#E0E0E0"
    TEXT_ACCENT = "#FFD23F"

    # Status colors
    SUCCESS_COLOR = "#00F5A0"
    ERROR_COLOR = "#FF4757"
    WARNING_COLOR = "#FFD23F"


def apply_ultra_modern_theme(app):
    """Apply enhanced ultra-modern theme"""
    app.setStyleSheet(
        f"""
        QMainWindow {{
            background: transparent;
            color: {UltraModernColors.TEXT_PRIMARY};
            font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', sans-serif;
            font-size: 14px;
            font-weight: 400;
        }}
        QWidget {{
            background: transparent;
            color: {UltraModernColors.TEXT_PRIMARY};
            font-family: 'Segoe UI', 'SF Pro Display', sans-serif;
        }}
        QLabel {{
            color: {UltraModernColors.TEXT_PRIMARY};
            font-weight: 500;
        }}
        QScrollArea {{
            border: none;
            background: transparent;
        }}
        QScrollBar:vertical {{
            border: none;
            background: {UltraModernColors.GLASS_BG};
            width: 8px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical {{
            background: {UltraModernColors.NEON_PURPLE};
            border-radius: 4px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {UltraModernColors.NEON_PINK};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            background: none;
            border: none;
        }}
        QStatusBar {{
            background: {UltraModernColors.GLASS_BG_DARK};
            color: {UltraModernColors.TEXT_PRIMARY};
            border-top: 1px solid {UltraModernColors.GLASS_BORDER};
            padding: 5px;
            font-weight: 500;
        }}
    """
    )


def get_modern_card_style(variant="default"):
    """Generate modern glassmorphism card style"""
    base_style = f"""
        QFrame {{
            background: {UltraModernColors.GLASS_BG};
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            border-radius: 16px;
            padding: 20px;
            color: {UltraModernColors.TEXT_PRIMARY};
        }}
        QFrame:hover {{
            background: {UltraModernColors.GLASS_BG_LIGHT};
            border: 1px solid {UltraModernColors.GLASS_BORDER_BRIGHT};
        }}
    """

    if variant == "highlight":
        return f"""
            QFrame {{
                background: {UltraModernColors.GLASS_BG_DARK};
                border: 2px solid {UltraModernColors.NEON_PURPLE};
                border-radius: 16px;
                padding: 20px;
                color: {UltraModernColors.TEXT_PRIMARY};
            }}
            QFrame:hover {{
                border: 2px solid {UltraModernColors.NEON_PINK};
                background: rgba(157, 78, 221, 0.1);
            }}
        """
    elif variant == "success":
        return f"""
            QFrame {{
                background: rgba(0, 245, 160, 0.1);
                border: 1px solid {UltraModernColors.SUCCESS_COLOR};
                border-radius: 16px;
                padding: 20px;
                color: {UltraModernColors.TEXT_PRIMARY};
            }}
        """
    elif variant == "error":
        return f"""
            QFrame {{
                background: rgba(255, 71, 87, 0.1);
                border: 1px solid {UltraModernColors.ERROR_COLOR};
                border-radius: 16px;
                padding: 20px;
                color: {UltraModernColors.TEXT_PRIMARY};
            }}
        """

    return base_style


def get_modern_button_style(variant="primary", size="md"):
    """Generate modern button style with enhanced gradients"""
    padding_map = {"sm": "8px 16px", "md": "12px 24px", "lg": "16px 32px"}

    font_size_map = {"sm": "12px", "md": "14px", "lg": "16px"}

    padding = padding_map.get(size, padding_map["md"])
    font_size = font_size_map.get(size, font_size_map["md"])

    base_style = f"""
        QPushButton {{
            border: none;
            border-radius: 12px;
            padding: {padding};
            font-size: {font_size};
            font-weight: 600;
            color: #FFFFFF;
        }}
        QPushButton:hover {{
            /* Qt doesn't support transform, use margin instead */
            margin-top: 1px;
        }}
        QPushButton:pressed {{
            margin-top: 0px;
        }}
        QPushButton:disabled {{
            /* Qt doesn't support opacity in stylesheets */
            color: #888888;
        }}
    """

    if variant == "primary":
        return (
            base_style
            + f"""
            QPushButton {{
                background: {UltraModernColors.PRIMARY_GRADIENT};
                border: 1px solid {UltraModernColors.NEON_PURPLE};
            }}
            QPushButton:hover {{
                background: {UltraModernColors.SECONDARY_GRADIENT};
                border: 1px solid {UltraModernColors.NEON_PINK};
            }}
        """
        )
    elif variant == "secondary":
        return (
            base_style
            + f"""
            QPushButton {{
                background: {UltraModernColors.GLASS_BG};
                border: 1px solid {UltraModernColors.GLASS_BORDER_BRIGHT};
            }}
            QPushButton:hover {{
                background: {UltraModernColors.GLASS_BG_LIGHT};
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
                background: {UltraModernColors.GLASS_BG};
                border: 1px solid {UltraModernColors.NEON_PURPLE};
            }}
        """
        )

    return base_style


def get_modern_input_style():
    """Generate modern input field style"""
    return f"""
        QLineEdit, QTextEdit, QComboBox, QSpinBox {{
            background: {UltraModernColors.GLASS_BG};
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            border-radius: 10px;
            padding: 12px 16px;
            color: {UltraModernColors.TEXT_PRIMARY};
            font-weight: 500;
            font-size: 14px;
            selection-background-color: {UltraModernColors.NEON_PURPLE};
            selection-color: #FFFFFF;
        }}
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
            border: 2px solid {UltraModernColors.NEON_PURPLE};
            background: {UltraModernColors.GLASS_BG_LIGHT};
        }}
        QLineEdit:hover, QTextEdit:hover, QComboBox:hover, QSpinBox:hover {{
            border: 1px solid {UltraModernColors.GLASS_BORDER_BRIGHT};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QComboBox::down-arrow {{
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTMgNS41TDYgOC41TDkgNS41IiBzdHJva2U9IiNGRkZGRkYiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
        }}
        QComboBox QAbstractItemView {{
            background: {UltraModernColors.GLASS_BG_DARK};
            border: 1px solid {UltraModernColors.NEON_PURPLE};
            border-radius: 10px;
            selection-background-color: {UltraModernColors.NEON_PURPLE};
            color: {UltraModernColors.TEXT_PRIMARY};
            padding: 8px;
        }}
        QSpinBox::up-button, QSpinBox::down-button {{
            width: 20px;
            border: none;
            background: {UltraModernColors.GLASS_BG};
        }}
        QSpinBox::up-arrow {{
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iMTAiIHZpZXdCb3g9IjAgMCAxMCAxMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTIuNSA2LjI1TDUgMy43NUw3LjUgNi4yNSIgc3Ryb2tlPSIjRkZGRkZGIiBzdHJva2Utd2lkdGg9IjEuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPg==);
        }}
        QSpinBox::down-arrow {{
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iMTAiIHZpZXdCb3g9IjAgMCAxMCAxMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTcuNSAzLjc1TDUgNi4yNUwyLjUgMy43NSIgc3Ryb2tlPSIjRkZGRkZGIiBzdHJva2Utd2lkdGg9IjEuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPg==);
        }}
    """


def get_modern_checkbox_style():
    """Generate modern checkbox style"""
    return f"""
        QCheckBox {{
            spacing: 12px;
            color: {UltraModernColors.TEXT_PRIMARY};
            font-weight: 500;
            font-size: 14px;
        }}
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border-radius: 6px;
            border: 2px solid {UltraModernColors.GLASS_BORDER_BRIGHT};
            background: {UltraModernColors.GLASS_BG};
        }}
        QCheckBox::indicator:hover {{
            border: 2px solid {UltraModernColors.NEON_PURPLE};
            background: {UltraModernColors.GLASS_BG_LIGHT};
        }}
        QCheckBox::indicator:checked {{
            background: {UltraModernColors.PRIMARY_GRADIENT};
            border: 2px solid {UltraModernColors.NEON_PURPLE};
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0iI0ZGRkZGRiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
        }}
    """


def get_modern_progress_style():
    """Generate modern progress bar style"""
    return f"""
        QProgressBar {{
            background: {UltraModernColors.GLASS_BG};
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            border-radius: 10px;
            height: 20px;
            text-align: center;
            color: {UltraModernColors.TEXT_PRIMARY};
            font-weight: 600;
        }}
        QProgressBar::chunk {{
            background: {UltraModernColors.PRIMARY_GRADIENT};
            border-radius: 10px;
        }}
    """


def get_modern_tab_style():
    """Generate modern tab widget style"""
    return f"""
        QTabWidget::pane {{
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            background: {UltraModernColors.GLASS_BG_DARK};
            border-radius: 16px;
            margin-top: -1px;
        }}
        QTabBar::tab {{
            background: {UltraModernColors.GLASS_BG};
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            border-bottom: none;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            padding: 12px 20px;
            color: {UltraModernColors.TEXT_SECONDARY};
            font-weight: 500;
            margin-right: 4px;
            min-width: 80px;
        }}
        QTabBar::tab:selected {{
            background: {UltraModernColors.GLASS_BG_DARK};
            border: 1px solid {UltraModernColors.NEON_PURPLE};
            border-bottom: none;
            color: {UltraModernColors.TEXT_PRIMARY};
        }}
        QTabBar::tab:hover:!selected {{
            background: {UltraModernColors.GLASS_BG_LIGHT};
            border: 1px solid {UltraModernColors.GLASS_BORDER_BRIGHT};
            color: {UltraModernColors.NEON_BLUE};
        }}
    """


def get_modern_groupbox_style():
    """Generate modern group box style"""
    return f"""
        QGroupBox {{
            background: {UltraModernColors.GLASS_BG_DARK};
            border: 1px solid {UltraModernColors.GLASS_BORDER};
            border-radius: 16px;
            margin-top: 30px;
            padding-top: 20px;
            color: {UltraModernColors.TEXT_PRIMARY};
            font-weight: 500;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 8px 16px;
            background: {UltraModernColors.PRIMARY_GRADIENT};
            border: 1px solid {UltraModernColors.NEON_PURPLE};
            border-radius: 12px;
            color: #FFFFFF;
            font-weight: 600;
            font-size: 14px;
        }}
    """


# Compatibility aliases
get_ultra_modern_card_style = get_modern_card_style
get_ultra_modern_button_style = get_modern_button_style
get_ultra_modern_input_style = get_modern_input_style
get_neon_checkbox_style = get_modern_checkbox_style
get_holographic_progress_style = get_modern_progress_style
get_holographic_tab_style = get_modern_tab_style
get_holographic_groupbox_style = get_modern_groupbox_style
get_gradient_button_style = get_modern_button_style
