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
            background: #232946;
            border: 1.5px solid #4a5568;
            border-radius: 18px;
            padding: 2em 1.5em;
            margin: 1.2em 0.7em;
            box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        }
        QLabel {
            color: #f4f4f4;
            background: transparent;
            font-family: 'Segoe UI', 'Arial', sans-serif;
            font-size: 1.15em;
            font-weight: 500;
            line-height: 1.5;
        }
    """


def get_header_card_style():
    """Header card with accent border"""
    return """
        QFrame {
            background: #232946;
            border: 2.5px solid #00d4ff;
            border-radius: 22px;
            padding: 2.5em 2em;
            margin: 1.5em 1em;
            box-shadow: 0 4px 18px rgba(0,0,0,0.10);
        }
        QLabel {
            color: #ffffff;
            background: transparent;
            font-family: 'Segoe UI', 'Arial', sans-serif;
            font-size: 2em;
            font-weight: bold;
            letter-spacing: 0.5px;
        }
    """


def get_gradient_button_style(color1="#00d4ff", color2="#4f8cff", size="normal"):
    """Modern button without transform/box-shadow"""
    if size == "large":
        padding = "18px 36px"
        font_size = "1.15em"
        height = "54px"
    elif size == "small":
        padding = "10px 18px"
        font_size = "0.95em"
        height = "36px"
    else:
        padding = "14px 28px"
        font_size = "1.05em"
        height = "44px"

    return f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {color1}, stop:1 {color2});
            color: #fff;
            border: none;
            border-radius: 12px;
            padding: {padding};
            font-weight: 600;
            font-size: {font_size};
            font-family: 'Segoe UI', 'Arial', sans-serif;
            min-height: {height};
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: background 0.2s;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {color2}, stop:1 {color1});
        }}
        QPushButton:pressed {{
            background: #232946;
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
            border-radius: 8px;
            padding: 16px 20px;
            color: #f4f4f4;
            font-size: 1.08em;
            font-family: 'Segoe UI', 'Arial', sans-serif;
        }
        QLineEdit:focus {
            border: 2px solid #00d4ff;
            background: #232946;
        }
        QLineEdit:disabled {
            background: #232946;
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
            border-radius: 8px;
            padding: 16px 20px;
            color: #f4f4f4;
            font-size: 1.08em;
            font-family: 'Segoe UI', 'Arial', sans-serif;
            min-width: 220px;
        }
        QComboBox:focus {
            border: 2px solid #00d4ff;
            background: #232946;
        }
        QComboBox::drop-down {
            border: none;
            width: 34px;
        }
        QComboBox::down-arrow {
            image: none;
            border: 4px solid transparent;
            border-top: 8px solid #ffffff;
            margin-right: 10px;
        }
        QComboBox::down-arrow:hover {
            border-top: 8px solid #00d4ff;
        }
        QComboBox QAbstractItemView {
            background: #232946;
            border: 1.5px solid #4a5568;
            border-radius: 8px;
            color: #f4f4f4;
            selection-background-color: #00d4ff;
            outline: none;
        }
        QComboBox QAbstractItemView::item {
            padding: 12px 20px;
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
            color: #f4f4f4;
            font-size: 1.08em;
            font-family: 'Segoe UI', 'Arial', sans-serif;
            spacing: 12px;
        }
        QCheckBox::indicator {
            width: 22px;
            height: 22px;
        }
        QCheckBox::indicator:unchecked {
            background: #1a202c;
            border: 2px solid #4a5568;
            border-radius: 6px;
        }
        QCheckBox::indicator:unchecked:hover {
            background: #232946;
            border: 2px solid #00d4ff;
        }
        QCheckBox::indicator:checked {
            background: #00d4ff;
            border: 2px solid #00d4ff;
            border-radius: 6px;
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
            border-radius: 10px;
            background: #1a202c;
            text-align: center;
            font-weight: bold;
            font-size: 1.05em;
            color: #f4f4f4;
            min-height: 24px;
        }
        QProgressBar::chunk {
            border-radius: 10px;
            background: #00d4ff;
        }
    """


def get_textedit_style():
    """Terminal-style log console"""
    return """
        QTextEdit {
            background: #0f1419;
            border: 1.5px solid #4a5568;
            border-radius: 10px;
            color: #00ff88;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 1.05em;
            padding: 16px;
            line-height: 1.6;
        }
        QTextEdit:focus {
            border: 1.5px solid #00d4ff;
        }
        QScrollBar:vertical {
            background: #1a202c;
            width: 14px;
            border-radius: 7px;
        }
        QScrollBar::handle:vertical {
            background: #4a5568;
            border-radius: 7px;
            min-height: 24px;
        }
        QScrollBar::handle:vertical:hover {
            background: #00d4ff;
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
            border: 1.5px solid #4a5568;
            border-radius: 12px;
            background: #232946;
            margin-top: 8px;
        }
        QTabBar::tab {
            background: #1a202c;
            color: #a0aec0;
            padding: 18px 32px;
            margin-right: 4px;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
            font-weight: 600;
            font-size: 1.08em;
            font-family: 'Segoe UI', 'Arial', sans-serif;
            min-width: 140px;
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
            border: 1.5px solid #4a5568;
            border-radius: 12px;
            margin-top: 28px;
            padding-top: 28px;
            font-family: 'Segoe UI', 'Arial', sans-serif;
            font-size: 1.15em;
            font-weight: 600;
            color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 24px;
            padding: 8px 18px;
            background: #00d4ff;
            color: #1a202c;
            border-radius: 8px;
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
