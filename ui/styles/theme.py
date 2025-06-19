# ui/styles/theme.py - Modern theme system
"""
Modern gradient theme system with Thai design elements
"""


def apply_gradient_theme(widget):
    """Apply modern gradient theme to main widget"""
    widget.setStyleSheet(
        """
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #0f3460),
                stop:1 qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #533483, stop:0.5 #7b2cbf, stop:1 #9d4edd));
        }
        
        QStatusBar {
            background: rgba(0,0,0,0.3);
            color: rgba(255,255,255,0.9);
            border-top: 1px solid rgba(255,255,255,0.1);
            font-size: 11px;
            padding: 5px;
        }
    """
    )


def get_card_style():
    """Get modern card styling"""
    return """
        QFrame {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(255,255,255,0.12), 
                stop:1 rgba(255,255,255,0.08));
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 15px;
            margin: 5px;
        }
        
        QLabel {
            color: rgba(255,255,255,0.9);
            background: transparent;
        }
    """


def get_header_card_style():
    """Get header card styling with logo area"""
    return """
        QFrame {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(255,255,255,0.15), 
                stop:1 rgba(255,255,255,0.10));
            border: 2px solid rgba(0,212,255,0.3);
            border-radius: 20px;
            margin: 5px;
        }
        
        QLabel {
            color: rgba(255,255,255,0.95);
            background: transparent;
        }
    """


def get_gradient_button_style(color1="#4CAF50", color2="#45a049", size="normal"):
    """Get gradient button styling"""
    if size == "large":
        padding = "15px 25px"
        font_size = "12px"
        height = "50px"
    elif size == "small":
        padding = "8px 15px"
        font_size = "10px"
        height = "35px"
    else:  # normal
        padding = "12px 20px"
        font_size = "11px"
        height = "42px"

    return f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {color1}, stop:1 {color2});
            color: white;
            border: none;
            border-radius: 12px;
            padding: {padding};
            font-weight: bold;
            font-size: {font_size};
            font-family: 'Segoe UI';
            min-height: {height};
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {color2}, stop:1 {color1});
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            transform: translateY(-1px);
        }}
        QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {adjust_color(color2, -20)}, stop:1 {adjust_color(color1, -20)});
            transform: translateY(1px);
        }}
        QPushButton:disabled {{
            background: rgba(100,100,100,0.5);
            color: rgba(255,255,255,0.5);
        }}
    """


def get_input_style():
    """Get modern input field styling"""
    return """
        QLineEdit {
            background: rgba(255,255,255,0.1);
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            padding: 12px 15px;
            color: white;
            font-size: 11px;
            font-family: 'Segoe UI';
            selection-background-color: rgba(0,212,255,0.3);
        }
        QLineEdit:focus {
            border: 2px solid #00d4ff;
            background: rgba(255,255,255,0.15);
            box-shadow: 0 0 10px rgba(0,212,255,0.3);
        }
        QLineEdit:disabled {
            background: rgba(255,255,255,0.05);
            border: 2px solid rgba(255,255,255,0.1);
            color: rgba(255,255,255,0.5);
        }
        QLineEdit::placeholder {
            color: rgba(255,255,255,0.5);
        }
    """


def get_combobox_style():
    """Get modern combobox styling"""
    return """
        QComboBox {
            background: rgba(255,255,255,0.1);
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            padding: 12px 15px;
            color: white;
            font-size: 11px;
            font-family: 'Segoe UI';
            min-width: 150px;
        }
        QComboBox:focus {
            border: 2px solid #00d4ff;
            background: rgba(255,255,255,0.15);
        }
        QComboBox::drop-down {
            border: none;
            width: 30px;
            margin-right: 5px;
        }
        QComboBox::down-arrow {
            image: none;
            border: 5px solid transparent;
            border-top: 8px solid rgba(255,255,255,0.7);
            margin-right: 5px;
        }
        QComboBox::down-arrow:hover {
            border-top: 8px solid #00d4ff;
        }
        QComboBox QAbstractItemView {
            background: rgba(40,40,60,0.95);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            color: white;
            selection-background-color: #00d4ff;
            outline: none;
        }
        QComboBox QAbstractItemView::item {
            padding: 8px 15px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        QComboBox QAbstractItemView::item:hover {
            background: rgba(0,212,255,0.2);
        }
    """


def get_checkbox_style():
    """Get modern checkbox styling"""
    return """
        QCheckBox {
            color: rgba(255,255,255,0.9);
            font-size: 11px;
            font-family: 'Segoe UI';
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        QCheckBox::indicator:unchecked {
            background: rgba(255,255,255,0.1);
            border: 2px solid rgba(255,255,255,0.3);
            border-radius: 4px;
        }
        QCheckBox::indicator:unchecked:hover {
            background: rgba(255,255,255,0.15);
            border: 2px solid rgba(0,212,255,0.5);
        }
        QCheckBox::indicator:checked {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #00d4ff, stop:1 #0099ff);
            border: 2px solid #0099ff;
            border-radius: 4px;
        }
        QCheckBox::indicator:checked:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #00b8e6, stop:1 #0088dd);
        }
    """


def get_listwidget_style():
    """Get modern list widget styling"""
    return """
        QListWidget {
            background: rgba(255,255,255,0.08);
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            color: white;
            font-size: 11px;
            font-family: 'Segoe UI';
            padding: 5px;
            outline: none;
        }
        QListWidget:focus {
            border: 2px solid #00d4ff;
        }
        QListWidget::item {
            padding: 8px 12px;
            border-radius: 6px;
            margin: 2px;
            border: 1px solid transparent;
        }
        QListWidget::item:hover {
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
        }
        QListWidget::item:selected {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #00d4ff, stop:1 #0099ff);
            color: white;
            border: 1px solid #0099ff;
        }
        QListWidget::item:selected:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #00b8e6, stop:1 #0088dd);
        }
    """


def get_progress_bar_style():
    """Get modern progress bar styling"""
    return """
        QProgressBar {
            border: none;
            border-radius: 8px;
            background: rgba(255,255,255,0.1);
            text-align: center;
            font-weight: bold;
            font-size: 11px;
            color: white;
            min-height: 16px;
        }
        QProgressBar::chunk {
            border-radius: 8px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #00d4ff, 
                stop:0.3 #0099ff, 
                stop:0.7 #0066cc,
                stop:1 #004499);
        }
    """


def get_textedit_style():
    """Get modern text edit (log console) styling"""
    return """
        QTextEdit {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(20,20,30,0.95), 
                stop:1 rgba(30,30,45,0.95));
            border: 2px solid rgba(255,255,255,0.1);
            border-radius: 10px;
            color: #00ff88;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 11px;
            padding: 10px;
            line-height: 1.4;
            selection-background-color: rgba(0,212,255,0.3);
        }
        QTextEdit:focus {
            border: 2px solid rgba(0,212,255,0.3);
        }
        QScrollBar:vertical {
            background: rgba(255,255,255,0.1);
            width: 12px;
            border-radius: 6px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: rgba(255,255,255,0.3);
            border-radius: 6px;
            min-height: 20px;
            margin: 2px;
        }
        QScrollBar::handle:vertical:hover {
            background: rgba(255,255,255,0.5);
        }
        QScrollBar::handle:vertical:pressed {
            background: rgba(0,212,255,0.7);
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: transparent;
        }
    """


def get_tab_style():
    """Get modern tab widget styling"""
    return """
        QTabWidget::pane {
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 10px;
            background: rgba(255,255,255,0.05);
            margin-top: 5px;
        }
        QTabBar::tab {
            background: rgba(255,255,255,0.1);
            color: rgba(255,255,255,0.8);
            padding: 12px 20px;
            margin-right: 3px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: bold;
            font-size: 11px;
            font-family: 'Segoe UI';
            min-width: 120px;
        }
        QTabBar::tab:selected {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #00d4ff, stop:1 #0099ff);
            color: white;
        }
        QTabBar::tab:hover:!selected {
            background: rgba(255,255,255,0.2);
            color: rgba(255,255,255,0.95);
        }
    """


def get_groupbox_style():
    """Get modern group box styling"""
    return """
        QGroupBox {
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 10px;
            margin-top: 15px;
            padding-top: 20px;
            font-family: 'Segoe UI';
            font-size: 12px;
            font-weight: bold;
            color: rgba(255,255,255,0.9);
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 10px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #00d4ff, stop:1 #0099ff);
            color: white;
            border-radius: 4px;
        }
    """


def get_splitter_style():
    """Get modern splitter styling"""
    return """
        QSplitter::handle {
            background: rgba(255,255,255,0.1);
            width: 3px;
            margin: 2px;
            border-radius: 1px;
        }
        QSplitter::handle:hover {
            background: rgba(0,212,255,0.5);
        }
        QSplitter::handle:pressed {
            background: #00d4ff;
        }
    """


def adjust_color(color_hex, amount):
    """Adjust color brightness"""
    try:
        # Remove # if present
        if color_hex.startswith("#"):
            color_hex = color_hex[1:]

        # Convert hex to RGB
        r = int(color_hex[0:2], 16)
        g = int(color_hex[2:4], 16)
        b = int(color_hex[4:6], 16)

        # Adjust brightness
        r = max(0, min(255, r + amount))
        g = max(0, min(255, g + amount))
        b = max(0, min(255, b + amount))

        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
    except:
        return color_hex  # Return original if conversion fails


def get_thai_fonts():
    """Get Thai-compatible font family list"""
    return ["Segoe UI", "Tahoma", "Leelawadee UI", "Arial Unicode MS", "sans-serif"]


def get_connection_status_style():
    """Get connection status indicator styling"""
    return """
        QLabel {
            font-size: 16px;
            font-weight: bold;
            padding: 5px;
            border-radius: 8px;
            background: rgba(255,255,255,0.1);
            margin: 2px;
        }
    """


# Theme presets
THEME_PRESETS = {
    "default": {
        "primary": "#00d4ff",
        "secondary": "#0099ff",
        "success": "#00ff88",
        "warning": "#ffaa00",
        "error": "#ff4444",
        "info": "#00d4ff",
    },
    "sunset": {
        "primary": "#ff6b35",
        "secondary": "#ff8e53",
        "success": "#00c851",
        "warning": "#ffbb33",
        "error": "#ff4444",
        "info": "#33b5e5",
    },
    "ocean": {
        "primary": "#0077be",
        "secondary": "#004d7a",
        "success": "#00c851",
        "warning": "#ffbb33",
        "error": "#ff4444",
        "info": "#33b5e5",
    },
}


def apply_theme_preset(preset_name="default"):
    """Apply a theme preset"""
    if preset_name not in THEME_PRESETS:
        preset_name = "default"

    return THEME_PRESETS[preset_name]
