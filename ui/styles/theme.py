def apply_gradient_theme(widget):
    """Clean modern theme without unsupported properties"""
    widget.setStyleSheet(
        """
        QMainWindow {
            background: #1a1a2e;
            color: #ffffff;
        }
        QStatusBar {
            background: #16213e;
            color: #ffffff;
            border-top: 1px solid #333;
            padding: 5px;
        }
    """
    )


def get_card_style():
    """Clean card styling"""
    return """
        QFrame {
            background: #2d3748;
            border: 1px solid #4a5568;
            border-radius: 12px;
            padding: 15px;
            margin: 8px;
        }
        QLabel {
            color: #ffffff;
            background: transparent;
            font-family: 'Segoe UI';
        }
    """


def get_header_card_style():
    """Header card with accent border"""
    return """
        QFrame {
            background: #2d3748;
            border: 2px solid #00d4ff;
            border-radius: 15px;
            padding: 20px;
            margin: 10px;
        }
        QLabel {
            color: #ffffff;
            background: transparent;
            font-family: 'Segoe UI';
        }
    """


def get_gradient_button_style(color1="#4CAF50", color2="#45a049", size="normal"):
    """Modern button without transform/box-shadow"""
    if size == "large":
        padding = "16px 32px"
        font_size = "14px"
        height = "48px"
    elif size == "small":
        padding = "8px 16px"
        font_size = "12px"
        height = "32px"
    else:
        padding = "12px 24px"
        font_size = "13px"
        height = "40px"

    return f"""
        QPushButton {{
            background: {color1};
            color: white;
            border: none;
            border-radius: 8px;
            padding: {padding};
            font-weight: 600;
            font-size: {font_size};
            font-family: 'Segoe UI';
            min-height: {height};
        }}
        QPushButton:hover {{
            background: {color2};
        }}
        QPushButton:pressed {{
            background: {adjust_color(color2, -20)};
        }}
        QPushButton:disabled {{
            background: #718096;
            color: #a0aec0;
        }}
    """


def get_input_style():
    """Clean input styling"""
    return """
        QLineEdit {
            background: #1a202c;
            border: 2px solid #4a5568;
            border-radius: 6px;
            padding: 12px 16px;
            color: #ffffff;
            font-size: 13px;
            font-family: 'Segoe UI';
        }
        QLineEdit:focus {
            border: 2px solid #00d4ff;
            background: #2d3748;
        }
        QLineEdit:disabled {
            background: #2d3748;
            border: 2px solid #718096;
            color: #a0aec0;
        }
        QLineEdit::placeholder {
            color: #a0aec0;
        }
    """


def get_combobox_style():
    """Modern combobox"""
    return """
        QComboBox {
            background: #1a202c;
            border: 2px solid #4a5568;
            border-radius: 6px;
            padding: 12px 16px;
            color: #ffffff;
            font-size: 13px;
            font-family: 'Segoe UI';
            min-width: 200px;
        }
        QComboBox:focus {
            border: 2px solid #00d4ff;
            background: #2d3748;
        }
        QComboBox::drop-down {
            border: none;
            width: 30px;
        }
        QComboBox::down-arrow {
            image: none;
            border: 4px solid transparent;
            border-top: 6px solid #ffffff;
            margin-right: 8px;
        }
        QComboBox::down-arrow:hover {
            border-top: 6px solid #00d4ff;
        }
        QComboBox QAbstractItemView {
            background: #2d3748;
            border: 1px solid #4a5568;
            border-radius: 6px;
            color: #ffffff;
            selection-background-color: #00d4ff;
            outline: none;
        }
        QComboBox QAbstractItemView::item {
            padding: 10px 16px;
            border-bottom: 1px solid #4a5568;
        }
        QComboBox QAbstractItemView::item:hover {
            background: #4a5568;
        }
        QComboBox QAbstractItemView::item:selected {
            background: #00d4ff;
            color: #1a202c;
        }
    """


def get_checkbox_style():
    """Clean checkbox"""
    return """
        QCheckBox {
            color: #ffffff;
            font-size: 13px;
            font-family: 'Segoe UI';
            spacing: 10px;
        }
        QCheckBox::indicator {
            width: 20px;
            height: 20px;
        }
        QCheckBox::indicator:unchecked {
            background: #1a202c;
            border: 2px solid #4a5568;
            border-radius: 4px;
        }
        QCheckBox::indicator:unchecked:hover {
            background: #2d3748;
            border: 2px solid #00d4ff;
        }
        QCheckBox::indicator:checked {
            background: #00d4ff;
            border: 2px solid #00d4ff;
            border-radius: 4px;
        }
        QCheckBox::indicator:checked:hover {
            background: #0099cc;
            border: 2px solid #0099cc;
        }
    """


def get_progress_bar_style():
    """Simple progress bar"""
    return """
        QProgressBar {
            border: none;
            border-radius: 8px;
            background: #1a202c;
            text-align: center;
            font-weight: bold;
            font-size: 12px;
            color: #ffffff;
            min-height: 20px;
        }
        QProgressBar::chunk {
            border-radius: 8px;
            background: #00d4ff;
        }
    """


def get_textedit_style():
    """Terminal-style log console"""
    return """
        QTextEdit {
            background: #0f1419;
            border: 1px solid #4a5568;
            border-radius: 8px;
            color: #00ff88;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 12px;
            padding: 12px;
            line-height: 1.5;
        }
        QTextEdit:focus {
            border: 1px solid #00d4ff;
        }
        QScrollBar:vertical {
            background: #1a202c;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background: #4a5568;
            border-radius: 6px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background: #718096;
        }
        QScrollBar::add-line:vertical, 
        QScrollBar::sub-line:vertical {
            height: 0px;
        }
    """


def get_tab_style():
    """Clean tab design"""
    return """
        QTabWidget::pane {
            border: 1px solid #4a5568;
            border-radius: 8px;
            background: #2d3748;
            margin-top: 5px;
        }
        QTabBar::tab {
            background: #1a202c;
            color: #a0aec0;
            padding: 14px 24px;
            margin-right: 2px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 600;
            font-size: 13px;
            font-family: 'Segoe UI';
            min-width: 120px;
        }
        QTabBar::tab:selected {
            background: #00d4ff;
            color: #1a202c;
        }
        QTabBar::tab:hover:!selected {
            background: #4a5568;
            color: #ffffff;
        }
    """


def get_groupbox_style():
    """Modern group container"""
    return """
        QGroupBox {
            border: 1px solid #4a5568;
            border-radius: 8px;
            margin-top: 20px;
            padding-top: 20px;
            font-family: 'Segoe UI';
            font-size: 14px;
            font-weight: 600;
            color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 16px;
            padding: 4px 12px;
            background: #00d4ff;
            color: #1a202c;
            border-radius: 4px;
        }
    """


def adjust_color(color_hex, amount):
    """Darken/lighten color"""
    try:
        if color_hex.startswith("#"):
            color_hex = color_hex[1:]

        r = max(0, min(255, int(color_hex[0:2], 16) + amount))
        g = max(0, min(255, int(color_hex[2:4], 16) + amount))
        b = max(0, min(255, int(color_hex[4:6], 16) + amount))

        return f"#{r:02x}{g:02x}{b:02x}"
    except:
        return color_hex
