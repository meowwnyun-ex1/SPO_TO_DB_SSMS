# ui/styles/theme.py - Modern 2025 Design System
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor, QPalette


class ModernColors:
    """2025 Design System Color Palette"""

    # Primary Brand Colors
    PRIMARY = "#6366F1"  # Indigo-500
    PRIMARY_DARK = "#4F46E5"  # Indigo-600
    PRIMARY_LIGHT = "#8B5CF6"  # Violet-500

    # Accent Colors
    ACCENT = "#06B6D4"  # Cyan-500
    ACCENT_BRIGHT = "#0EA5E9"  # Sky-500
    SUCCESS = "#10B981"  # Emerald-500
    WARNING = "#F59E0B"  # Amber-500
    ERROR = "#EF4444"  # Red-500

    # Neutral Palette
    SURFACE_PRIMARY = "#0F172A"  # Slate-900
    SURFACE_SECONDARY = "#1E293B"  # Slate-800
    SURFACE_TERTIARY = "#334155"  # Slate-700
    SURFACE_ELEVATED = "#475569"  # Slate-600

    # Text Colors
    TEXT_PRIMARY = "#F8FAFC"  # Slate-50
    TEXT_SECONDARY = "#CBD5E1"  # Slate-300
    TEXT_MUTED = "#94A3B8"  # Slate-400
    TEXT_DISABLED = "#64748B"  # Slate-500

    # Glass & Blur Effects
    GLASS_BG = "rgba(15, 23, 42, 0.7)"
    GLASS_BORDER = "rgba(148, 163, 184, 0.2)"
    GLASS_SHADOW = "rgba(0, 0, 0, 0.25)"

    # Gradients
    GRADIENT_PRIMARY = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6366F1, stop:1 #8B5CF6)"
    )
    GRADIENT_ACCENT = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #06B6D4, stop:1 #0EA5E9)"
    )
    GRADIENT_SUCCESS = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #10B981, stop:1 #059669)"
    )
    GRADIENT_ERROR = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #EF4444, stop:1 #DC2626)"
    )


class Typography:
    """Modern Typography System"""

    # Font Families
    PRIMARY_FONT = "Inter"
    SECONDARY_FONT = "SF Pro Display"
    MONO_FONT = "JetBrains Mono"

    # Font Sizes
    TEXT_XS = 11
    TEXT_SM = 12
    TEXT_BASE = 14
    TEXT_LG = 16
    TEXT_XL = 18
    TEXT_2XL = 20
    TEXT_3XL = 24

    # Font Weights
    WEIGHT_LIGHT = 300
    WEIGHT_NORMAL = 400
    WEIGHT_MEDIUM = 500
    WEIGHT_SEMIBOLD = 600
    WEIGHT_BOLD = 700


class Spacing:
    """Modern Spacing System"""

    XS = 4
    SM = 8
    BASE = 12
    MD = 16
    LG = 20
    XL = 24
    XXL = 32

    # Component Specific
    BUTTON_PADDING = "8px 16px"
    INPUT_PADDING = "12px 16px"
    CARD_PADDING = "20px"


class BorderRadius:
    """Modern Border Radius System"""

    SM = 6
    BASE = 8
    MD = 12
    LG = 16
    XL = 20
    FULL = 9999


def apply_modern_theme(app: QApplication):
    """Apply 2025 Modern Theme"""
    palette = app.palette()

    # Set palette colors
    palette.setColor(QPalette.ColorRole.Window, QColor(ModernColors.SURFACE_PRIMARY))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(ModernColors.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Base, QColor(ModernColors.SURFACE_SECONDARY))
    palette.setColor(QPalette.ColorRole.Text, QColor(ModernColors.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Button, QColor(ModernColors.PRIMARY))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(ModernColors.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(ModernColors.PRIMARY))
    palette.setColor(
        QPalette.ColorRole.HighlightedText, QColor(ModernColors.TEXT_PRIMARY)
    )

    app.setPalette(palette)
    app.setStyleSheet(get_global_stylesheet())


def get_global_stylesheet():
    """Global Modern Stylesheet"""
    return f"""
        * {{
            font-family: "{Typography.PRIMARY_FONT}", -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
            font-size: {Typography.TEXT_BASE}px;
            line-height: 1.5;
        }}
        
        QMainWindow {{
            background: {ModernColors.SURFACE_PRIMARY};
            color: {ModernColors.TEXT_PRIMARY};
        }}
        
        QWidget {{
            background: transparent;
            color: {ModernColors.TEXT_PRIMARY};
        }}
        
        /* Modern Scrollbars */
        QScrollBar:vertical {{
            background: {ModernColors.SURFACE_SECONDARY};
            width: 8px;
            border-radius: 4px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background: {ModernColors.TEXT_MUTED};
            border-radius: 4px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {ModernColors.TEXT_SECONDARY};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        
        QScrollBar:horizontal {{
            background: {ModernColors.SURFACE_SECONDARY};
            height: 8px;
            border-radius: 4px;
            margin: 0;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {ModernColors.TEXT_MUTED};
            border-radius: 4px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: {ModernColors.TEXT_SECONDARY};
        }}
        
        /* Modern Tooltips */
        QToolTip {{
            background: {ModernColors.SURFACE_TERTIARY};
            color: {ModernColors.TEXT_PRIMARY};
            border: 1px solid {ModernColors.GLASS_BORDER};
            border-radius: {BorderRadius.SM}px;
            padding: 8px 12px;
            font-size: {Typography.TEXT_SM}px;
            box-shadow: 0 10px 25px {ModernColors.GLASS_SHADOW};
        }}
        
        /* Modern Message Boxes */
        QMessageBox {{
            background: {ModernColors.SURFACE_SECONDARY};
            color: {ModernColors.TEXT_PRIMARY};
            border: 1px solid {ModernColors.GLASS_BORDER};
            border-radius: {BorderRadius.MD}px;
        }}
        
        QMessageBox QLabel {{
            color: {ModernColors.TEXT_PRIMARY};
            font-size: {Typography.TEXT_BASE}px;
            font-weight: {Typography.WEIGHT_MEDIUM};
        }}
        
        QMessageBox QPushButton {{
            {get_button_style('primary', 'md')}
        }}
    """


def get_button_style(variant="primary", size="md"):
    """Modern Button Styles"""

    # Size configurations
    sizes = {
        "sm": {
            "padding": "6px 12px",
            "font_size": Typography.TEXT_SM,
            "height": "32px",
            "border_radius": BorderRadius.SM,
        },
        "md": {
            "padding": "8px 16px",
            "font_size": Typography.TEXT_BASE,
            "height": "40px",
            "border_radius": BorderRadius.BASE,
        },
        "lg": {
            "padding": "12px 24px",
            "font_size": Typography.TEXT_LG,
            "height": "48px",
            "border_radius": BorderRadius.MD,
        },
    }

    size_config = sizes.get(size, sizes["md"])

    # Variant configurations
    variants = {
        "primary": {
            "background": ModernColors.GRADIENT_PRIMARY,
            "color": ModernColors.TEXT_PRIMARY,
            "border": f"1px solid {ModernColors.PRIMARY}",
            "hover_bg": ModernColors.PRIMARY_DARK,
            "shadow": "0 4px 12px rgba(99, 102, 241, 0.3)",
        },
        "secondary": {
            "background": ModernColors.SURFACE_TERTIARY,
            "color": ModernColors.TEXT_PRIMARY,
            "border": f"1px solid {ModernColors.GLASS_BORDER}",
            "hover_bg": ModernColors.SURFACE_ELEVATED,
            "shadow": "0 2px 8px rgba(0, 0, 0, 0.1)",
        },
        "accent": {
            "background": ModernColors.GRADIENT_ACCENT,
            "color": ModernColors.TEXT_PRIMARY,
            "border": f"1px solid {ModernColors.ACCENT}",
            "hover_bg": ModernColors.ACCENT_BRIGHT,
            "shadow": "0 4px 12px rgba(6, 182, 212, 0.3)",
        },
        "ghost": {
            "background": "transparent",
            "color": ModernColors.TEXT_SECONDARY,
            "border": f"1px solid {ModernColors.GLASS_BORDER}",
            "hover_bg": ModernColors.SURFACE_SECONDARY,
            "shadow": "none",
        },
        "danger": {
            "background": ModernColors.GRADIENT_ERROR,
            "color": ModernColors.TEXT_PRIMARY,
            "border": f"1px solid {ModernColors.ERROR}",
            "hover_bg": "#DC2626",
            "shadow": "0 4px 12px rgba(239, 68, 68, 0.3)",
        },
    }

    variant_config = variants.get(variant, variants["primary"])

    return f"""
        QPushButton {{
            background: {variant_config["background"]};
            color: {variant_config["color"]};
            border: {variant_config["border"]};
            border-radius: {size_config["border_radius"]}px;
            padding: {size_config["padding"]};
            font-size: {size_config["font_size"]}px;
            font-weight: {Typography.WEIGHT_MEDIUM};
            min-height: {size_config["height"]};
            outline: none;
        }}
        
        QPushButton:hover {{
            background: {variant_config["hover_bg"]};
            transform: translateY(-1px);
            box-shadow: {variant_config["shadow"]};
        }}
        
        QPushButton:pressed {{
            transform: translateY(0px);
            background: {variant_config["background"]};
        }}
        
        QPushButton:disabled {{
            background: {ModernColors.SURFACE_TERTIARY};
            color: {ModernColors.TEXT_DISABLED};
            border: 1px solid {ModernColors.GLASS_BORDER};
            opacity: 0.6;
        }}
    """


def get_input_style():
    """Modern Input Field Styles"""
    return f"""
        QLineEdit, QTextEdit, QComboBox, QSpinBox {{
            background: {ModernColors.SURFACE_SECONDARY};
            color: {ModernColors.TEXT_PRIMARY};
            border: 1px solid {ModernColors.GLASS_BORDER};
            border-radius: {BorderRadius.BASE}px;
            padding: {Spacing.BASE}px {Spacing.MD}px;
            font-size: {Typography.TEXT_BASE}px;
            font-weight: {Typography.WEIGHT_NORMAL};
            selection-background-color: {ModernColors.PRIMARY};
            selection-color: {ModernColors.TEXT_PRIMARY};
        }}
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
            border: 2px solid {ModernColors.PRIMARY};
            background: {ModernColors.SURFACE_PRIMARY};
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }}
        
        QLineEdit:hover, QTextEdit:hover, QComboBox:hover, QSpinBox:hover {{
            border-color: {ModernColors.TEXT_MUTED};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
            background: transparent;
        }}
        
        QComboBox::down-arrow {{
            width: 12px;
            height: 12px;
            background: {ModernColors.TEXT_SECONDARY};
        }}
        
        QComboBox QAbstractItemView {{
            background: {ModernColors.SURFACE_SECONDARY};
            border: 1px solid {ModernColors.GLASS_BORDER};
            border-radius: {BorderRadius.BASE}px;
            selection-background-color: {ModernColors.PRIMARY};
            selection-color: {ModernColors.TEXT_PRIMARY};
            padding: {Spacing.SM}px;
        }}
    """


def get_card_style():
    """Modern Card Component Style"""
    return f"""
        QWidget {{
            background: {ModernColors.GLASS_BG};
            border: 1px solid {ModernColors.GLASS_BORDER};
            border-radius: {BorderRadius.MD}px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px {ModernColors.GLASS_SHADOW};
        }}
        
        QWidget:hover {{
            border-color: {ModernColors.PRIMARY};
            background: rgba(15, 23, 42, 0.8);
            transform: translateY(-2px);
        }}
    """


def get_progress_style():
    """Modern Progress Bar Style"""
    return f"""
        QProgressBar {{
            background: {ModernColors.SURFACE_SECONDARY};
            border: none;
            border-radius: {BorderRadius.SM}px;
            height: 8px;
            text-align: center;
            color: {ModernColors.TEXT_PRIMARY};
            font-weight: {Typography.WEIGHT_MEDIUM};
            font-size: {Typography.TEXT_SM}px;
        }}
        
        QProgressBar::chunk {{
            background: {ModernColors.GRADIENT_PRIMARY};
            border-radius: {BorderRadius.SM}px;
            margin: 1px;
        }}
    """


def get_groupbox_style():
    """Modern Group Box Style"""
    return f"""
        QGroupBox {{
            background: {ModernColors.GLASS_BG};
            border: 1px solid {ModernColors.GLASS_BORDER};
            border-radius: {BorderRadius.MD}px;
            margin-top: 20px;
            padding-top: {Spacing.MD}px;
            font-weight: {Typography.WEIGHT_SEMIBOLD};
            font-size: {Typography.TEXT_LG}px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: {Spacing.SM}px {Spacing.MD}px;
            background: {ModernColors.GRADIENT_PRIMARY};
            border: none;
            border-radius: {BorderRadius.SM}px;
            color: {ModernColors.TEXT_PRIMARY};
            font-weight: {Typography.WEIGHT_SEMIBOLD};
        }}
    """


def get_tab_style():
    """Modern Tab Widget Style"""
    return f"""
        QTabWidget::pane {{
            background: {ModernColors.SURFACE_SECONDARY};
            border: 1px solid {ModernColors.GLASS_BORDER};
            border-radius: {BorderRadius.MD}px;
            margin-top: -1px;
        }}
        
        QTabBar::tab {{
            background: {ModernColors.SURFACE_TERTIARY};
            border: 1px solid {ModernColors.GLASS_BORDER};
            border-bottom: none;
            border-top-left-radius: {BorderRadius.BASE}px;
            border-top-right-radius: {BorderRadius.BASE}px;
            padding: {Spacing.SM}px {Spacing.MD}px;
            margin-right: 2px;
            color: {ModernColors.TEXT_SECONDARY};
            font-weight: {Typography.WEIGHT_MEDIUM};
        }}
        
        QTabBar::tab:selected {{
            background: {ModernColors.GRADIENT_PRIMARY};
            color: {ModernColors.TEXT_PRIMARY};
            border-color: {ModernColors.PRIMARY};
        }}
        
        QTabBar::tab:hover:!selected {{
            background: {ModernColors.SURFACE_ELEVATED};
            color: {ModernColors.TEXT_PRIMARY};
        }}
    """


# Backward compatibility
UltraModernColors = ModernColors
CompactScaling = Spacing
apply_ultra_modern_theme = apply_modern_theme
get_modern_button_style = get_button_style
get_modern_input_style = get_input_style
get_modern_card_style = get_card_style
get_holographic_progress_style = get_progress_style
get_holographic_groupbox_style = get_groupbox_style
get_modern_tab_style = get_tab_style
