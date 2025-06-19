# ui/styles/theme.py - Ultra Modern Design System with Dimensional Effects

import os


class UltraModernColors:
    """Advanced color palette with luminous effects"""

    # Primary holographic gradients
    PRIMARY_GLOW = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:0.3 #764ba2, stop:0.6 #f093fb, stop:1 #f5576c)"
    SECONDARY_GLOW = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #a8edea, stop:0.5 #fed6e3, stop:1 #667eea)"

    # Neon accent colors
    NEON_BLUE = "#00d4ff"
    NEON_PURPLE = "#bd5eff"
    NEON_PINK = "#ff6b9d"
    NEON_GREEN = "#39ff14"
    NEON_YELLOW = "#ffff00"

    # Glassmorphism backgrounds
    GLASS_BG = "rgba(255, 255, 255, 0.1)"
    GLASS_BG_DARK = "rgba(0, 0, 0, 0.2)"
    GLASS_BORDER = "rgba(255, 255, 255, 0.2)"

    # Neural network inspired gradients
    NEURAL_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #141E30, stop:0.3 #243B55, stop:0.7 #667eea, stop:1 #764ba2)"
    CYBER_GRADIENT = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0f3460, stop:0.5 #0f3460, stop:1 #16537e)"

    # Status colors with glow
    SUCCESS_GLOW = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #56ab2f, stop:1 #a8e6cf)"
    )
    ERROR_GLOW = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff416c, stop:1 #ff4b2b)"
    )
    WARNING_GLOW = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f093fb, stop:1 #f5576c)"
    )

    # Text with luminosity
    TEXT_LUMINOUS = "#ffffff"
    TEXT_GLOW = "#e6f7ff"
    TEXT_NEON = "#00ffff"


class DimensionalEffects:
    """3D and dimensional visual effects"""

    # Shadow configurations
    LARGE_SHADOW = """
        QGraphicsDropShadowEffect {
            blur-radius: 25px;
            color: rgba(0, 0, 0, 0.4);
            offset: 0px 15px;
        }
    """

    GLOW_SHADOW = """
        QGraphicsDropShadowEffect {
            blur-radius: 20px;
            color: rgba(102, 126, 234, 0.6);
            offset: 0px 0px;
        }
    """

    NEON_GLOW = """
        QGraphicsDropShadowEffect {
            blur-radius: 30px;
            color: rgba(0, 212, 255, 0.8);
            offset: 0px 0px;
        }
    """


def get_background_image_style():
    """Get background image style if exists"""
    bg_paths = [
        "assets/background.jpg",
        "assets/bg.png",
        "assets/background.png",
        "ui/assets/background.jpg",
        "resources/bg.jpg",
    ]

    for path in bg_paths:
        if os.path.exists(path):
            return f"""
                background-image: url({path});
                background-repeat: no-repeat;
                background-position: center;
                background-attachment: fixed;
            """

    # Fallback to advanced gradient if no image found
    return f"""
        background: {UltraModernColors.NEURAL_GRADIENT};
        background-attachment: fixed;
    """


def get_ultra_modern_card_style(variant="default"):
    """Ultra modern glassmorphism cards with dimensional effects"""
    base = f"""
        QFrame {{
            background: rgba(255, 255, 255, 0.05);
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 24px;
        }}
        QFrame:hover {{
            background: rgba(255, 255, 255, 0.08);
            border: 2px solid rgba(0, 212, 255, 0.4);
            transform: translateY(-3px) scale(1.02);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        QLabel {{
            background: transparent;
            color: {UltraModernColors.TEXT_LUMINOUS};
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }}
    """

    variants = {
        "elevated": f"""
            QFrame {{
                background: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(102, 126, 234, 0.3);
                box-shadow: 
                    0 25px 50px rgba(0, 0, 0, 0.25),
                    0 0 30px rgba(102, 126, 234, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
            }}
        """,
        "neon": f"""
            QFrame {{
                border: 2px solid {UltraModernColors.NEON_BLUE};
                box-shadow: 
                    0 0 20px rgba(0, 212, 255, 0.4),
                    0 0 40px rgba(0, 212, 255, 0.2),
                    inset 0 0 20px rgba(0, 212, 255, 0.1);
            }}
        """,
        "holographic": f"""
            QFrame {{
                background: {UltraModernColors.PRIMARY_GLOW};
                opacity: 0.9;
                border: none;
                box-shadow: 
                    0 20px 40px rgba(102, 126, 234, 0.3),
                    0 0 50px rgba(245, 87, 108, 0.2);
            }}
        """,
    }

    return base + variants.get(variant, "")


def get_ultra_modern_button_style(variant="primary", size="md"):
    """Ultra modern holographic buttons with dimensional effects"""

    sizes = {
        "sm": {
            "height": 36,
            "padding": "10px 18px",
            "font_size": 13,
            "border_radius": 12,
        },
        "md": {
            "height": 44,
            "padding": "14px 28px",
            "font_size": 15,
            "border_radius": 16,
        },
        "lg": {
            "height": 52,
            "padding": "18px 36px",
            "font_size": 17,
            "border_radius": 20,
        },
    }

    size_config = sizes[size]

    base = f"""
        QPushButton {{
            border: none;
            border-radius: {size_config['border_radius']}px;
            padding: {size_config['padding']};
            font-family: 'Inter', 'Segoe UI', sans-serif;
            font-size: {size_config['font_size']}px;
            font-weight: 600;
            min-height: {size_config['height']}px;
            color: {UltraModernColors.TEXT_LUMINOUS};
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        QPushButton:hover {{
            transform: translateY(-2px) scale(1.05);
            filter: brightness(1.2);
        }}
        QPushButton:pressed {{
            transform: translateY(0px) scale(0.98);
            filter: brightness(0.9);
        }}
        QPushButton:disabled {{
            opacity: 0.4;
            transform: none;
        }}
    """

    variants = {
        "primary": f"""
            QPushButton {{
                background: {UltraModernColors.PRIMARY_GLOW};
                box-shadow: 
                    0 8px 32px rgba(102, 126, 234, 0.4),
                    0 0 20px rgba(118, 75, 162, 0.3),
                    inset 0 1px 0 rgba(255, 255, 255, 0.2);
            }}
            QPushButton:hover {{
                box-shadow: 
                    0 12px 40px rgba(102, 126, 234, 0.6),
                    0 0 30px rgba(118, 75, 162, 0.5),
                    inset 0 1px 0 rgba(255, 255, 255, 0.3);
            }}
        """,
        "success": f"""
            QPushButton {{
                background: {UltraModernColors.SUCCESS_GLOW};
                box-shadow: 
                    0 8px 32px rgba(86, 171, 47, 0.4),
                    0 0 20px rgba(168, 230, 207, 0.3);
            }}
            QPushButton:hover {{
                box-shadow: 
                    0 12px 40px rgba(86, 171, 47, 0.6),
                    0 0 30px rgba(168, 230, 207, 0.5);
            }}
        """,
        "warning": f"""
            QPushButton {{
                background: {UltraModernColors.WARNING_GLOW};
                box-shadow: 
                    0 8px 32px rgba(240, 147, 251, 0.4),
                    0 0 20px rgba(245, 87, 108, 0.3);
            }}
        """,
        "neon": f"""
            QPushButton {{
                background: rgba(0, 212, 255, 0.1);
                border: 2px solid {UltraModernColors.NEON_BLUE};
                box-shadow: 
                    0 0 20px rgba(0, 212, 255, 0.5),
                    inset 0 0 20px rgba(0, 212, 255, 0.1);
            }}
            QPushButton:hover {{
                background: rgba(0, 212, 255, 0.2);
                box-shadow: 
                    0 0 30px rgba(0, 212, 255, 0.8),
                    inset 0 0 30px rgba(0, 212, 255, 0.2);
            }}
        """,
        "glass": f"""
            QPushButton {{
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 
                    0 8px 32px rgba(0, 0, 0, 0.1),
                    inset 0 1px 0 rgba(255, 255, 255, 0.2);
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }}
        """,
    }

    return base + variants.get(variant, variants["primary"])


def get_ultra_modern_input_style():
    """Ultra modern holographic inputs with glow effects"""
    return f"""
        QLineEdit, QComboBox {{
            background: rgba(255, 255, 255, 0.05);
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 16px 20px;
            color: {UltraModernColors.TEXT_LUMINOUS};
            font-family: 'Inter', 'Segoe UI', sans-serif;
            font-size: 15px;
            font-weight: 500;
            min-height: 24px;
            selection-background-color: rgba(0, 212, 255, 0.3);
        }}
        QLineEdit:focus, QComboBox:focus {{
            border: 2px solid {UltraModernColors.NEON_BLUE};
            background: rgba(255, 255, 255, 0.08);
            box-shadow: 
                0 0 20px rgba(0, 212, 255, 0.4),
                inset 0 0 20px rgba(0, 212, 255, 0.1);
        }}
        QLineEdit:hover, QComboBox:hover {{
            border: 2px solid rgba(255, 255, 255, 0.2);
            background: rgba(255, 255, 255, 0.07);
        }}
        QLineEdit::placeholder {{
            color: rgba(255, 255, 255, 0.5);
        }}
        QComboBox::drop-down {{
            border: none;
            width: 40px;
            background: transparent;
        }}
        QComboBox::down-arrow {{
            image: none;
            border: 6px solid transparent;
            border-top: 8px solid {UltraModernColors.NEON_BLUE};
            margin-right: 12px;
        }}
        QComboBox QAbstractItemView {{
            background: rgba(255, 255, 255, 0.05);
            border: 2px solid rgba(0, 212, 255, 0.3);
            border-radius: 12px;
            color: {UltraModernColors.TEXT_LUMINOUS};
            selection-background-color: rgba(0, 212, 255, 0.3);
            padding: 8px;
        }}
        QComboBox QAbstractItemView::item {{
            padding: 12px 16px;
            border-radius: 8px;
            margin: 2px;
        }}
        QComboBox QAbstractItemView::item:hover {{
            background: rgba(0, 212, 255, 0.2);
        }}
    """


def get_holographic_progress_style():
    """Holographic progress bar with dimensional effects"""
    return f"""
        QProgressBar {{
            border: none;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.05);
            text-align: center;
            font-family: 'Inter', 'Segoe UI', sans-serif;
            font-size: 13px;
            font-weight: 600;
            color: {UltraModernColors.TEXT_LUMINOUS};
            min-height: 24px;
        }}
        QProgressBar::chunk {{
            border-radius: 12px;
            background: {UltraModernColors.PRIMARY_GLOW};
            box-shadow: 
                0 0 20px rgba(102, 126, 234, 0.6),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
        }}
    """


def get_cyber_log_style():
    """Cyberpunk terminal-style log console"""
    return f"""
        QTextEdit {{
            background: {UltraModernColors.CYBER_GRADIENT};
            border: 2px solid {UltraModernColors.NEON_BLUE};
            border-radius: 16px;
            color: {UltraModernColors.NEON_GREEN};
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 13px;
            font-weight: 500;
            padding: 20px;
            line-height: 1.6;
            selection-background-color: rgba(0, 212, 255, 0.3);
            box-shadow: 
                0 0 30px rgba(0, 212, 255, 0.3),
                inset 0 0 30px rgba(0, 0, 0, 0.2);
        }}
        QScrollBar:vertical {{
            background: rgba(0, 0, 0, 0.3);
            width: 14px;
            border-radius: 7px;
            margin: 3px;
        }}
        QScrollBar::handle:vertical {{
            background: {UltraModernColors.NEON_BLUE};
            border-radius: 7px;
            min-height: 30px;
            box-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        }}
        QScrollBar::handle:vertical:hover {{
            background: {UltraModernColors.NEON_PURPLE};
            box-shadow: 0 0 15px rgba(189, 94, 255, 0.7);
        }}
        QScrollBar::add-line:vertical, 
        QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
    """


def get_holographic_tab_style():
    """Holographic tab widget with dimensional effects"""
    return f"""
        QTabWidget::pane {{
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.03);
            margin-top: 8px;
        }}
        QTabBar::tab {{
            background: rgba(255, 255, 255, 0.05);
            color: rgba(255, 255, 255, 0.7);
            padding: 16px 32px;
            margin-right: 4px;
            border-top-left-radius: 16px;
            border-top-right-radius: 16px;
            font-weight: 600;
            font-size: 14px;
            font-family: 'Inter', 'Segoe UI', sans-serif;
            min-width: 140px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }}
        QTabBar::tab:selected {{
            background: {UltraModernColors.PRIMARY_GLOW};
            color: {UltraModernColors.TEXT_LUMINOUS};
            border: 2px solid rgba(102, 126, 234, 0.5);
            box-shadow: 
                0 8px 32px rgba(102, 126, 234, 0.4),
                0 0 20px rgba(118, 75, 162, 0.3);
            transform: translateY(-2px);
        }}
        QTabBar::tab:hover:!selected {{
            background: rgba(255, 255, 255, 0.1);
            color: {UltraModernColors.TEXT_LUMINOUS};
            border: 2px solid rgba(0, 212, 255, 0.3);
            box-shadow: 0 0 15px rgba(0, 212, 255, 0.2);
        }}
    """


def get_neon_checkbox_style():
    """Neon checkbox with holographic effects"""
    return f"""
        QCheckBox {{
            color: {UltraModernColors.TEXT_LUMINOUS};
            font-size: 15px;
            font-family: 'Inter', 'Segoe UI', sans-serif;
            font-weight: 500;
            spacing: 16px;
            background: transparent;
            padding: 16px 20px;
            border-radius: 12px;
        }}
        QCheckBox:hover {{
            background: rgba(0, 212, 255, 0.1);
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
        }}
        QCheckBox::indicator {{
            width: 24px;
            height: 24px;
            border-radius: 6px;
        }}
        QCheckBox::indicator:unchecked {{
            background: rgba(255, 255, 255, 0.05);
            border: 2px solid rgba(255, 255, 255, 0.2);
        }}
        QCheckBox::indicator:unchecked:hover {{
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid {UltraModernColors.NEON_BLUE};
            box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
        }}
        QCheckBox::indicator:checked {{
            background: {UltraModernColors.SUCCESS_GLOW};
            border: 2px solid {UltraModernColors.NEON_GREEN};
            box-shadow: 
                0 0 20px rgba(57, 255, 20, 0.5),
                inset 0 0 10px rgba(255, 255, 255, 0.2);
        }}
        QCheckBox::indicator:checked:hover {{
            box-shadow: 
                0 0 25px rgba(57, 255, 20, 0.7),
                inset 0 0 15px rgba(255, 255, 255, 0.3);
        }}
    """


def get_holographic_groupbox_style():
    """Holographic group container with dimensional borders"""
    return f"""
        QGroupBox {{
            background: rgba(255, 255, 255, 0.03);
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            margin-top: 32px;
            padding-top: 32px;
            font-family: 'Inter', 'Segoe UI', sans-serif;
            font-size: 16px;
            font-weight: 700;
            color: {UltraModernColors.TEXT_LUMINOUS};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 24px;
            padding: 8px 20px;
            background: {UltraModernColors.PRIMARY_GLOW};
            color: {UltraModernColors.TEXT_LUMINOUS};
            border-radius: 12px;
            border: 2px solid rgba(102, 126, 234, 0.3);
            box-shadow: 
                0 8px 32px rgba(102, 126, 234, 0.4),
                0 0 20px rgba(118, 75, 162, 0.3);
        }}
    """


def apply_ultra_modern_theme(widget):
    """Apply ultra modern holographic theme"""
    bg_style = get_background_image_style()

    widget.setStyleSheet(
        f"""
        QMainWindow {{
            {bg_style}
            color: {UltraModernColors.TEXT_LUMINOUS};
        }}
        QMainWindow::separator {{
            background: rgba(0, 212, 255, 0.3);
            width: 2px;
            height: 2px;
            border-radius: 1px;
        }}
        QSplitter {{
            background: transparent;
            border: none;
        }}
        QSplitter::handle {{
            background: {UltraModernColors.NEON_BLUE};
            width: 3px;
            margin: 15px;
            border-radius: 2px;
            box-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        }}
        QSplitter::handle:hover {{
            background: {UltraModernColors.NEON_PURPLE};
            box-shadow: 0 0 15px rgba(189, 94, 255, 0.7);
        }}
        QStatusBar {{
            background: rgba(0, 0, 0, 0.4);
            color: {UltraModernColors.TEXT_LUMINOUS};
            border-top: 2px solid rgba(0, 212, 255, 0.3);
            padding: 12px 20px;
            font-size: 13px;
            font-weight: 500;
        }}
    """
    )


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
    return get_cyber_log_style()


def get_modern_tab_style():
    return get_holographic_tab_style()


def get_modern_checkbox_style():
    return get_neon_checkbox_style()


def get_modern_groupbox_style():
    return get_holographic_groupbox_style()


# Additional compatibility
get_card_style = get_ultra_modern_card_style
get_gradient_button_style = get_ultra_modern_button_style
get_input_style = get_ultra_modern_input_style
get_combobox_style = get_ultra_modern_input_style
get_checkbox_style = get_neon_checkbox_style
get_progress_bar_style = get_holographic_progress_style
get_textedit_style = get_cyber_log_style
get_tab_style = get_holographic_tab_style
get_groupbox_style = get_holographic_groupbox_style
apply_gradient_theme = apply_ultra_modern_theme
