# ui/styles/theme.py - Updated Modern Design System


class ModernColors:
    # Primary palette
    PRIMARY_50 = "#eff6ff"
    PRIMARY_500 = "#3b82f6"
    PRIMARY_600 = "#2563eb"
    PRIMARY_700 = "#1d4ed8"

    # Semantic colors
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    ERROR = "#ef4444"
    INFO = "#06b6d4"

    # Neutral backgrounds
    BG_PRIMARY = "#0f172a"
    BG_SECONDARY = "#1e293b"
    BG_TERTIARY = "#334155"
    BG_ELEVATED = "rgba(30, 41, 59, 0.95)"

    # Text hierarchy
    TEXT_PRIMARY = "#f8fafc"
    TEXT_SECONDARY = "#cbd5e1"
    TEXT_MUTED = "#64748b"

    # Borders & dividers
    BORDER = "#374151"
    BORDER_FOCUS = "#3b82f6"
    BORDER_SUBTLE = "rgba(55, 65, 81, 0.3)"


class Spacing:
    XS, SM, MD, LG, XL, XXL = 4, 8, 12, 16, 20, 24
    SECTION_GAP = 32
    CARD_PADDING = 20


class Typography:
    FONT_PRIMARY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    FONT_MONO = "'JetBrains Mono', 'SF Mono', Consolas, monospace"

    # Font sizes
    TEXT_XS, TEXT_SM, TEXT_BASE, TEXT_LG, TEXT_XL, TEXT_2XL = 12, 14, 16, 18, 20, 24

    # Weights
    WEIGHT_NORMAL, WEIGHT_MEDIUM, WEIGHT_SEMIBOLD, WEIGHT_BOLD = 400, 500, 600, 700


class BorderRadius:
    SM, MD, LG, XL = 6, 8, 12, 16


def get_modern_card_style(variant="default"):
    """Modern glassmorphism card styles"""
    base = f"""
        QFrame {{
            background: {ModernColors.BG_ELEVATED};
            border: 1px solid {ModernColors.BORDER_SUBTLE};
            border-radius: {BorderRadius.LG}px;
            padding: {Spacing.CARD_PADDING}px;
        }}
        QLabel {{
            background: transparent;
            color: {ModernColors.TEXT_PRIMARY};
            font-family: {Typography.FONT_PRIMARY};
        }}
    """

    if variant == "elevated":
        base += f"""
            QFrame {{
                border: 1px solid rgba(59, 130, 246, 0.2);
            }}
        """
    elif variant == "interactive":
        base += f"""
            QFrame:hover {{
                background: rgba(30, 41, 59, 0.98);
                border: 1px solid rgba(59, 130, 246, 0.4);
            }}
        """

    return base


def get_modern_button_style(variant="primary", size="md"):
    """Modern button styling"""

    # Size variants
    sizes = {
        "sm": {
            "height": 32,
            "padding": f"{Spacing.SM}px {Spacing.MD}px",
            "font_size": Typography.TEXT_SM,
        },
        "md": {
            "height": 40,
            "padding": f"{Spacing.MD}px {Spacing.LG}px",
            "font_size": Typography.TEXT_BASE,
        },
        "lg": {
            "height": 48,
            "padding": f"{Spacing.LG}px {Spacing.XL}px",
            "font_size": Typography.TEXT_LG,
        },
    }

    size_config = sizes[size]

    base = f"""
        QPushButton {{
            border: none;
            border-radius: {BorderRadius.MD}px;
            padding: {size_config['padding']};
            font-family: {Typography.FONT_PRIMARY};
            font-size: {size_config['font_size']}px;
            font-weight: {Typography.WEIGHT_SEMIBOLD};
            min-height: {size_config['height']}px;
        }}
        QPushButton:disabled {{
            opacity: 0.5;
        }}
    """

    variants = {
        "primary": f"""
            QPushButton {{
                background: {ModernColors.PRIMARY_500};
                color: white;
            }}
            QPushButton:hover {{
                background: {ModernColors.PRIMARY_600};
            }}
        """,
        "success": f"""
            QPushButton {{
                background: {ModernColors.SUCCESS};
                color: white;
            }}
            QPushButton:hover {{
                background: #059669;
            }}
        """,
        "warning": f"""
            QPushButton {{
                background: {ModernColors.WARNING};
                color: white;
            }}
            QPushButton:hover {{
                background: #d97706;
            }}
        """,
        "secondary": f"""
            QPushButton {{
                background: {ModernColors.BG_TERTIARY};
                color: {ModernColors.TEXT_PRIMARY};
                border: 1px solid {ModernColors.BORDER};
            }}
            QPushButton:hover {{
                background: #475569;
                border: 1px solid {ModernColors.BORDER_FOCUS};
            }}
        """,
    }

    return base + variants.get(variant, variants["primary"])


def get_modern_input_style():
    """Modern form inputs with focus states"""
    return f"""
        QLineEdit, QComboBox {{
            background: {ModernColors.BG_SECONDARY};
            border: 2px solid {ModernColors.BORDER};
            border-radius: {BorderRadius.MD}px;
            padding: {Spacing.MD}px {Spacing.LG}px;
            color: {ModernColors.TEXT_PRIMARY};
            font-family: {Typography.FONT_PRIMARY};
            font-size: {Typography.TEXT_BASE}px;
            min-height: 40px;
        }}
        QLineEdit:focus, QComboBox:focus {{
            border: 2px solid {ModernColors.BORDER_FOCUS};
            background: rgba(30, 41, 59, 0.9);
        }}
        QLineEdit:disabled, QComboBox:disabled {{
            background: {ModernColors.BG_PRIMARY};
            color: {ModernColors.TEXT_MUTED};
            border: 2px solid {ModernColors.BG_PRIMARY};
        }}
        QLineEdit::placeholder {{
            color: {ModernColors.TEXT_MUTED};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border: 4px solid transparent;
            border-top: 6px solid {ModernColors.TEXT_SECONDARY};
            margin-right: 8px;
        }}
        QComboBox QAbstractItemView {{
            background: {ModernColors.BG_SECONDARY};
            border: 1px solid {ModernColors.BORDER};
            border-radius: {BorderRadius.MD}px;
            color: {ModernColors.TEXT_PRIMARY};
            selection-background-color: {ModernColors.PRIMARY_500};
        }}
    """


def get_modern_progress_style():
    """Modern progress bar with gradient"""
    return f"""
        QProgressBar {{
            border: none;
            border-radius: {BorderRadius.MD}px;
            background: {ModernColors.BG_PRIMARY};
            text-align: center;
            font-family: {Typography.FONT_PRIMARY};
            font-size: {Typography.TEXT_SM}px;
            font-weight: {Typography.WEIGHT_SEMIBOLD};
            color: {ModernColors.TEXT_PRIMARY};
            min-height: 20px;
        }}
        QProgressBar::chunk {{
            border-radius: {BorderRadius.MD}px;
            background: qlineargradient(90deg, {ModernColors.PRIMARY_500}, {ModernColors.PRIMARY_600});
        }}
    """


def get_modern_log_style():
    """Modern terminal-style log console"""
    return f"""
        QTextEdit {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {ModernColors.BG_PRIMARY}, stop:1 #0a0f1a);
            border: 2px solid {ModernColors.BORDER};
            border-radius: {BorderRadius.LG}px;
            color: {ModernColors.SUCCESS};
            font-family: {Typography.FONT_MONO};
            font-size: {Typography.TEXT_SM}px;
            padding: {Spacing.LG}px;
            line-height: 1.5;
            selection-background-color: rgba(59, 130, 246, 0.3);
        }}
        QScrollBar:vertical {{
            background: {ModernColors.BG_SECONDARY};
            width: 12px;
            border-radius: 6px;
            margin: 2px;
        }}
        QScrollBar::handle:vertical {{
            background: {ModernColors.PRIMARY_500};
            border-radius: 6px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {ModernColors.PRIMARY_600};
        }}
    """


def get_modern_tab_style():
    """Modern tab widget"""
    return f"""
        QTabWidget::pane {{
            border: 1px solid {ModernColors.BORDER};
            border-radius: {BorderRadius.MD}px;
            background: {ModernColors.BG_SECONDARY};
            margin-top: 5px;
        }}
        QTabBar::tab {{
            background: {ModernColors.BG_PRIMARY};
            color: {ModernColors.TEXT_MUTED};
            padding: 14px 24px;
            margin-right: 2px;
            border-top-left-radius: {BorderRadius.MD}px;
            border-top-right-radius: {BorderRadius.MD}px;
            font-weight: {Typography.WEIGHT_SEMIBOLD};
            font-size: {Typography.TEXT_SM}px;
            font-family: {Typography.FONT_PRIMARY};
            min-width: 120px;
        }}
        QTabBar::tab:selected {{
            background: {ModernColors.PRIMARY_500};
            color: white;
        }}
        QTabBar::tab:hover:!selected {{
            background: {ModernColors.BG_TERTIARY};
            color: {ModernColors.TEXT_PRIMARY};
        }}
    """


def get_modern_checkbox_style():
    """Modern checkbox with animations"""
    return f"""
        QCheckBox {{
            color: {ModernColors.TEXT_PRIMARY};
            font-size: {Typography.TEXT_BASE}px;
            font-family: {Typography.FONT_PRIMARY};
            font-weight: {Typography.WEIGHT_MEDIUM};
            spacing: 12px;
            background: transparent;
            padding: 12px 16px;
            border-radius: {BorderRadius.MD}px;
        }}
        QCheckBox:hover {{
            background: rgba(59, 130, 246, 0.1);
        }}
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}
        QCheckBox::indicator:unchecked {{
            background: {ModernColors.BG_PRIMARY};
            border: 2px solid {ModernColors.BORDER};
        }}
        QCheckBox::indicator:unchecked:hover {{
            background: {ModernColors.BG_SECONDARY};
            border: 2px solid {ModernColors.BORDER_FOCUS};
        }}
        QCheckBox::indicator:checked {{
            background: {ModernColors.PRIMARY_500};
            border: 2px solid {ModernColors.PRIMARY_500};
        }}
        QCheckBox::indicator:checked:hover {{
            background: {ModernColors.PRIMARY_600};
            border: 2px solid {ModernColors.PRIMARY_600};
        }}
    """


def get_modern_groupbox_style():
    """Modern group container"""
    return f"""
        QGroupBox {{
            border: 1px solid {ModernColors.BORDER};
            border-radius: {BorderRadius.MD}px;
            margin-top: 20px;
            padding-top: 20px;
            font-family: {Typography.FONT_PRIMARY};
            font-size: {Typography.TEXT_LG}px;
            font-weight: {Typography.WEIGHT_SEMIBOLD};
            color: {ModernColors.TEXT_PRIMARY};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 16px;
            padding: 4px 12px;
            background: {ModernColors.PRIMARY_500};
            color: white;
            border-radius: 4px;
        }}
    """


# Legacy function aliases for backward compatibility
def apply_gradient_theme(widget):
    """Apply modern theme to main window"""
    widget.setStyleSheet(
        f"""
        QMainWindow {{
            background: {ModernColors.BG_PRIMARY};
            color: {ModernColors.TEXT_PRIMARY};
        }}
        QStatusBar {{
            background: {ModernColors.BG_SECONDARY};
            color: {ModernColors.TEXT_PRIMARY};
            border-top: 1px solid {ModernColors.BORDER};
            padding: 8px 15px;
            font-size: 12px;
        }}
    """
    )


def get_card_style():
    return get_modern_card_style()


def get_header_card_style():
    return get_modern_card_style("elevated")


def get_gradient_button_style(color1=None, color2=None, size="normal"):
    size_map = {"normal": "md", "large": "lg", "small": "sm"}
    return get_modern_button_style("primary", size_map.get(size, "md"))


def get_input_style():
    return get_modern_input_style()


def get_combobox_style():
    return get_modern_input_style()


def get_checkbox_style():
    return get_modern_checkbox_style()


def get_progress_bar_style():
    return get_modern_progress_style()


def get_textedit_style():
    return get_modern_log_style()


def get_tab_style():
    return get_modern_tab_style()


def get_groupbox_style():
    return get_modern_groupbox_style()


def get_modern_tab_style():
    """Modern tab widget"""
    return get_tab_style()


def get_modern_input_style():
    """Modern input styling"""
    return get_modern_input_style()


def get_modern_groupbox_style():
    """Modern group container"""
    return get_groupbox_style()


def get_modern_checkbox_style():
    """Modern checkbox with animations"""
    return get_checkbox_style()
