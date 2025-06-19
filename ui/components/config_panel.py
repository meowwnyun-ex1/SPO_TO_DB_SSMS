from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QPushButton,
    QSpinBox,
    QFrame,
    QLabel,
    QGraphicsDropShadowEffect,
    QScrollArea,
    QFileDialog,
    QMessageBox,
)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QColor
from ..styles.theme import (
    UltraModernColors,
    get_holographic_tab_style,
    get_ultra_modern_input_style,
    get_ultra_modern_button_style,
    get_neon_checkbox_style,
    get_holographic_groupbox_style,
    get_ultra_modern_card_style,
)
from utils.config_manager import AppConfig
import logging

logger = logging.getLogger(__name__)


class HolographicTab(QWidget):
    """Tab แบบ holographic พร้อม dimensional effects"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_holographic_background()

    def setup_holographic_background(self):
        """ตั้งค่า background แบบ holographic"""
        self.setStyleSheet(
            f"""
            QWidget {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.02),
                    stop:0.5 rgba(0, 212, 255, 0.03),
                    stop:1 rgba(189, 94, 255, 0.02)
                );
                backdrop-filter: blur(15px);
            }}
        """
        )


class NeonGroupBox(QGroupBox):
    """GroupBox แบบ neon glow พร้อม advanced effects"""

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setup_neon_style()
        self.setup_glow_animation()

    def setup_neon_style(self):
        """ตั้งค่าสไตล์ neon"""
        style = get_holographic_groupbox_style()
        self.setStyleSheet(style)

        # เพิ่ม glow effect
        self.glow_effect = QGraphicsDropShadowEffect()
        self.glow_effect.setBlurRadius(20)
        self.glow_effect.setColor(QColor(0, 212, 255, 60))
        self.glow_effect.setOffset(0, 0)
        self.setGraphicsEffect(self.glow_effect)

    def setup_glow_animation(self):
        """ตั้งค่า glow animation"""
        self.glow_timer = QTimer()
        self.glow_timer.timeout.connect(self.animate_glow)
        self.glow_intensity = 60
        self.glow_direction = 1
        self.glow_timer.start(2000)  # Subtle breathing effect

    def animate_glow(self):
        """Animate glow effect"""
        self.glow_intensity += self.glow_direction * 20
        if self.glow_intensity >= 120:
            self.glow_direction = -1
        elif self.glow_intensity <= 40:
            self.glow_direction = 1

        self.glow_effect.setColor(QColor(0, 212, 255, self.glow_intensity))


class CyberInput(QLineEdit):
    """Input field แบบ cyberpunk พร้อม holographic effects"""

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setup_cyber_style()
        self.setup_focus_animations()

    def setup_cyber_style(self):
        """ตั้งค่าสไตล์ cyberpunk"""
        style = get_ultra_modern_input_style()
        self.setStyleSheet(style)

        # เพิ่ม subtle glow
        self.glow_effect = QGraphicsDropShadowEffect()
        self.glow_effect.setBlurRadius(10)
        self.glow_effect.setColor(QColor(255, 255, 255, 30))
        self.glow_effect.setOffset(0, 0)
        self.setGraphicsEffect(self.glow_effect)

    def setup_focus_animations(self):
        """ตั้งค่า focus animations"""
        self.focus_animation = QPropertyAnimation(self, b"geometry")
        self.focus_animation.setDuration(200)
        self.focus_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def focusInEvent(self, event):
        """Enhanced focus in effect"""
        super().focusInEvent(event)
        # เพิ่ม neon glow
        self.glow_effect.setColor(QColor(0, 212, 255, 80))
        self.glow_effect.setBlurRadius(15)

    def focusOutEvent(self, event):
        """Reset focus effect"""
        super().focusOutEvent(event)
        self.glow_effect.setColor(QColor(255, 255, 255, 30))
        self.glow_effect.setBlurRadius(10)


class HolographicComboBox(QComboBox):
    """ComboBox แบบ holographic พร้อม dimensional dropdown"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_holographic_style()
        self.setup_hover_effects()

    def setup_holographic_style(self):
        """ตั้งค่าสไตล์ holographic"""
        style = get_ultra_modern_input_style()
        self.setStyleSheet(style)

        # เพิ่ม glow effect
        self.glow_effect = QGraphicsDropShadowEffect()
        self.glow_effect.setBlurRadius(10)
        self.glow_effect.setColor(QColor(255, 255, 255, 30))
        self.glow_effect.setOffset(0, 0)
        self.setGraphicsEffect(self.glow_effect)

    def setup_hover_effects(self):
        """ตั้งค่า hover effects"""
        pass

    def enterEvent(self, event):
        """Hover glow effect"""
        super().enterEvent(event)
        self.glow_effect.setColor(QColor(189, 94, 255, 60))
        self.glow_effect.setBlurRadius(15)

    def leaveEvent(self, event):
        """Reset hover"""
        super().leaveEvent(event)
        self.glow_effect.setColor(QColor(255, 255, 255, 30))
        self.glow_effect.setBlurRadius(10)


class CyberButton(QPushButton):
    """Button แบบ cyberpunk พร้อม advanced animations"""

    def __init__(self, text, variant="primary", size="md", parent=None):
        super().__init__(text, parent)
        self.variant = variant
        self.size = size
        self.setup_cyber_style()
        self.setup_press_animations()

    def setup_cyber_style(self):
        """ตั้งค่าสไตล์ cyberpunk"""
        style = get_ultra_modern_button_style(self.variant, self.size)
        self.setStyleSheet(style)

        # เพิ่ม glow effect
        self.glow_effect = QGraphicsDropShadowEffect()
        self.glow_effect.setBlurRadius(15)

        if self.variant == "primary":
            self.glow_effect.setColor(QColor(102, 126, 234, 80))
        elif self.variant == "success":
            self.glow_effect.setColor(QColor(86, 171, 47, 80))
        elif self.variant == "warning":
            self.glow_effect.setColor(QColor(237, 137, 54, 80))
        else:
            self.glow_effect.setColor(QColor(100, 100, 100, 60))

        self.glow_effect.setOffset(0, 0)
        self.setGraphicsEffect(self.glow_effect)

    def setup_press_animations(self):
        """ตั้งค่า press animations"""
        self.press_animation = QPropertyAnimation(self, b"geometry")
        self.press_animation.setDuration(100)
        self.press_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def enterEvent(self, event):
        """Enhanced hover effect"""
        super().enterEvent(event)
        # เพิ่ม glow intensity
        current_color = self.glow_effect.color()
        enhanced_color = QColor(
            current_color.red(), current_color.green(), current_color.blue(), 150
        )
        self.glow_effect.setColor(enhanced_color)
        self.glow_effect.setBlurRadius(25)

    def leaveEvent(self, event):
        """Reset hover effect"""
        super().leaveEvent(event)
        current_color = self.glow_effect.color()
        normal_color = QColor(
            current_color.red(), current_color.green(), current_color.blue(), 80
        )
        self.glow_effect.setColor(normal_color)
        self.glow_effect.setBlurRadius(15)

    def mousePressEvent(self, event):
        """Press animation with scale effect"""
        super().mousePressEvent(event)
        current_rect = self.geometry()
        pressed_rect = QRect(
            current_rect.x() + 2,
            current_rect.y() + 2,
            current_rect.width() - 4,
            current_rect.height() - 4,
        )
        self.press_animation.setStartValue(current_rect)
        self.press_animation.setEndValue(pressed_rect)
        self.press_animation.start()

    def mouseReleaseEvent(self, event):
        """Release animation"""
        super().mouseReleaseEvent(event)
        # Implement release animation if needed


class UltraModernConfigPanel(QWidget):
    """Ultra modern configuration panel พร้อม holographic interface"""

    # Signals
    config_changed = pyqtSignal(object)
    test_sharepoint_requested = pyqtSignal()
    test_database_requested = pyqtSignal()
    refresh_sites_requested = pyqtSignal()
    refresh_lists_requested = pyqtSignal()
    refresh_databases_requested = pyqtSignal()
    refresh_tables_requested = pyqtSignal()

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.config = AppConfig()
        self.setup_ultra_modern_ui()
        self.setup_background_effects()

    def setup_ultra_modern_ui(self):
        """ตั้งค่า UI แบบ ultra modern"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Ultra modern tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(get_holographic_tab_style())

        # สร้าง tabs
        self.create_neural_sharepoint_tab()
        self.create_quantum_database_tab()
        self.create_matrix_advanced_tab()

        # เพิ่ม tabs พร้อม cyber icons
        self.tab_widget.addTab(self.sharepoint_tab, "◈ Neural SharePoint")
        self.tab_widget.addTab(self.database_tab, "◎ Quantum Database")
        self.tab_widget.addTab(self.advanced_tab, "⬢ Matrix Advanced")

        layout.addWidget(self.tab_widget)

        # Action buttons แบบ cyberpunk
        self.create_cyber_action_buttons(layout)

    def setup_background_effects(self):
        """ตั้งค่า background effects"""
        self.setStyleSheet(
            f"""
            QWidget {{
                background: transparent;
            }}
        """
        )

    def create_neural_sharepoint_tab(self):
        """สร้าง SharePoint tab แบบ neural network"""
        self.sharepoint_tab = HolographicTab()

        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        scroll_content = QWidget()
        scroll.setWidget(scroll_content)

        layout = QVBoxLayout(self.sharepoint_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(24)

        # Neural Authentication Group
        auth_group = NeonGroupBox("◈ Neural Authentication Matrix")
        auth_layout = QFormLayout(auth_group)
        auth_layout.setSpacing(16)

        # Tenant ID
        self.tenant_id_input = CyberInput("xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
        auth_layout.addRow(
            self.create_neon_label("Tenant Neural ID:"), self.tenant_id_input
        )

        # Client ID
        self.client_id_input = CyberInput("Application (client) neural identifier")
        auth_layout.addRow(
            self.create_neon_label("Client Neural ID:"), self.client_id_input
        )

        # Client Secret - แก้ไข EchoMode
        self.client_secret_input = CyberInput("Neural security token")
        self.client_secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        auth_layout.addRow(
            self.create_neon_label("Neural Secret:"), self.client_secret_input
        )

        content_layout.addWidget(auth_group)

        # Matrix Connection Group
        connection_group = NeonGroupBox("◎ Matrix Connection Protocol")
        connection_layout = QFormLayout(connection_group)
        connection_layout.setSpacing(16)

        # Site URL with refresh
        site_url_layout = QHBoxLayout()
        self.site_url_input = CyberInput(
            "https://yourcompany.sharepoint.com/sites/matrix"
        )

        self.refresh_sites_btn = CyberButton("◉", "primary", "sm")
        self.refresh_sites_btn.setMaximumWidth(44)
        self.refresh_sites_btn.clicked.connect(self.refresh_sites_requested.emit)

        site_url_layout.addWidget(self.site_url_input)
        site_url_layout.addWidget(self.refresh_sites_btn)
        connection_layout.addRow(
            self.create_neon_label("Matrix Site URL:"), site_url_layout
        )

        # List Name with refresh
        list_layout = QHBoxLayout()
        self.list_name_combo = HolographicComboBox()
        self.list_name_combo.setEditable(True)

        self.refresh_lists_btn = CyberButton("◈", "primary", "sm")
        self.refresh_lists_btn.setMaximumWidth(44)
        self.refresh_lists_btn.clicked.connect(self.refresh_lists_requested.emit)

        list_layout.addWidget(self.list_name_combo)
        list_layout.addWidget(self.refresh_lists_btn)
        connection_layout.addRow(
            self.create_neon_label("Data Stream List:"), list_layout
        )

        content_layout.addWidget(connection_group)

        # Protocol Options Group
        options_group = NeonGroupBox("⬢ Neural Protocol Options")
        options_layout = QFormLayout(options_group)

        self.use_graph_api_check = QCheckBox("◦ Enable Microsoft Graph Neural API")
        self.use_graph_api_check.setStyleSheet(get_neon_checkbox_style())
        options_layout.addRow("", self.use_graph_api_check)

        content_layout.addWidget(options_group)

        # Test Neural Connection
        test_layout = QHBoxLayout()
        self.test_sp_btn = CyberButton("◉ Initiate Neural Probe", "success", "lg")
        self.test_sp_btn.clicked.connect(self.test_sharepoint_requested.emit)
        test_layout.addWidget(self.test_sp_btn)
        test_layout.addStretch()

        content_layout.addLayout(test_layout)
        content_layout.addStretch()

    def create_quantum_database_tab(self):
        """สร้าง Database tab แบบ quantum computing"""
        self.database_tab = HolographicTab()

        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        scroll_content = QWidget()
        scroll.setWidget(scroll_content)

        layout = QVBoxLayout(self.database_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(24)

        # Quantum Engine Selection
        type_group = NeonGroupBox("◎ Quantum Storage Engine")
        type_layout = QVBoxLayout(type_group)

        self.db_type_combo = HolographicComboBox()
        self.db_type_combo.addItems(["sqlserver", "sqlite", "mysql", "postgresql"])
        self.db_type_combo.currentTextChanged.connect(self._on_db_type_changed)
        type_layout.addWidget(self.db_type_combo)

        content_layout.addWidget(type_group)

        # SQL Server Quantum Configuration
        self.sqlserver_group = NeonGroupBox("◈ SQL Server Quantum Matrix")
        sqlserver_layout = QFormLayout(self.sqlserver_group)
        sqlserver_layout.setSpacing(16)

        # Server
        self.sql_server_input = CyberInput("quantum-server.database.matrix.net")
        sqlserver_layout.addRow(
            self.create_neon_label("Quantum Server:"), self.sql_server_input
        )

        # Database with refresh
        db_layout = QHBoxLayout()
        self.sql_database_combo = HolographicComboBox()
        self.sql_database_combo.setEditable(True)

        self.refresh_db_btn = CyberButton("◎", "primary", "sm")
        self.refresh_db_btn.setMaximumWidth(44)
        self.refresh_db_btn.clicked.connect(self.refresh_databases_requested.emit)

        db_layout.addWidget(self.sql_database_combo)
        db_layout.addWidget(self.refresh_db_btn)
        sqlserver_layout.addRow(self.create_neon_label("Quantum Database:"), db_layout)

        # Username
        self.sql_username_input = CyberInput("quantum_user")
        sqlserver_layout.addRow(
            self.create_neon_label("Neural Username:"), self.sql_username_input
        )

        # Password - แก้ไข EchoMode
        self.sql_password_input = CyberInput("quantum_access_key")
        self.sql_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        sqlserver_layout.addRow(
            self.create_neon_label("Neural Password:"), self.sql_password_input
        )

        # Table with refresh
        table_layout = QHBoxLayout()
        self.sql_table_combo = HolographicComboBox()
        self.sql_table_combo.setEditable(True)

        self.refresh_tables_btn = CyberButton("⬢", "primary", "sm")
        self.refresh_tables_btn.setMaximumWidth(44)
        self.refresh_tables_btn.clicked.connect(self.refresh_tables_requested.emit)

        table_layout.addWidget(self.sql_table_combo)
        table_layout.addWidget(self.refresh_tables_btn)
        sqlserver_layout.addRow(
            self.create_neon_label("Data Matrix Table:"), table_layout
        )

        # Quantum Options
        self.sql_create_table_check = QCheckBox(
            "◦ Auto-generate quantum table structure"
        )
        self.sql_create_table_check.setStyleSheet(get_neon_checkbox_style())
        self.sql_create_table_check.setChecked(True)
        sqlserver_layout.addRow("", self.sql_create_table_check)

        self.sql_truncate_check = QCheckBox("◦ Purge existing quantum data before sync")
        self.sql_truncate_check.setStyleSheet(get_neon_checkbox_style())
        sqlserver_layout.addRow("", self.sql_truncate_check)

        content_layout.addWidget(self.sqlserver_group)

        # Test Quantum Connection
        test_layout = QHBoxLayout()
        self.test_db_btn = CyberButton("◎ Quantum Connection Probe", "success", "lg")
        self.test_db_btn.clicked.connect(self.test_database_requested.emit)
        test_layout.addWidget(self.test_db_btn)
        test_layout.addStretch()

        content_layout.addLayout(test_layout)
        content_layout.addStretch()

        # Initially show SQL Server
        self._on_db_type_changed("sqlserver")

    def create_matrix_advanced_tab(self):
        """สร้าง Advanced tab แบบ matrix system"""
        self.advanced_tab = HolographicTab()

        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        scroll_content = QWidget()
        scroll.setWidget(scroll_content)

        layout = QVBoxLayout(self.advanced_tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(24)

        # Neural Sync Settings
        sync_group = NeonGroupBox("◈ Neural Synchronization Protocol")
        sync_layout = QFormLayout(sync_group)
        sync_layout.setSpacing(16)

        # Sync Interval
        self.sync_interval_spin = QSpinBox()
        self.sync_interval_spin.setMinimum(60)
        self.sync_interval_spin.setMaximum(86400)
        self.sync_interval_spin.setValue(3600)
        self.sync_interval_spin.setSuffix(" neural cycles")
        self.sync_interval_spin.setStyleSheet(get_ultra_modern_input_style())
        sync_layout.addRow(
            self.create_neon_label("Sync Frequency:"), self.sync_interval_spin
        )

        # Sync Mode
        self.sync_mode_combo = HolographicComboBox()
        self.sync_mode_combo.addItems(["full", "incremental", "quantum"])
        sync_layout.addRow(
            self.create_neon_label("Sync Protocol:"), self.sync_mode_combo
        )

        # Batch Size
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setMinimum(100)
        self.batch_size_spin.setMaximum(10000)
        self.batch_size_spin.setValue(1000)
        self.batch_size_spin.setSuffix(" data packets")
        self.batch_size_spin.setStyleSheet(get_ultra_modern_input_style())
        sync_layout.addRow(
            self.create_neon_label("Neural Batch Size:"), self.batch_size_spin
        )

        content_layout.addWidget(sync_group)

        # Quantum Performance Settings
        perf_group = NeonGroupBox("⬢ Quantum Performance Matrix")
        perf_layout = QFormLayout(perf_group)
        perf_layout.setSpacing(16)

        # Connection Timeout
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setMinimum(10)
        self.timeout_spin.setMaximum(300)
        self.timeout_spin.setValue(30)
        self.timeout_spin.setSuffix(" quantum seconds")
        self.timeout_spin.setStyleSheet(get_ultra_modern_input_style())
        perf_layout.addRow(self.create_neon_label("Neural Timeout:"), self.timeout_spin)

        # Max Retries
        self.retries_spin = QSpinBox()
        self.retries_spin.setMinimum(1)
        self.retries_spin.setMaximum(10)
        self.retries_spin.setValue(3)
        self.retries_spin.setStyleSheet(get_ultra_modern_input_style())
        perf_layout.addRow(self.create_neon_label("Retry Attempts:"), self.retries_spin)

        # Parallel Processing
        self.parallel_check = QCheckBox("◦ Enable parallel quantum processing")
        self.parallel_check.setStyleSheet(get_neon_checkbox_style())
        perf_layout.addRow("", self.parallel_check)

        content_layout.addWidget(perf_group)

        # Matrix Monitoring Settings
        log_group = NeonGroupBox("◎ Neural Activity Monitoring")
        log_layout = QFormLayout(log_group)
        log_layout.setSpacing(16)

        # Log Level
        self.log_level_combo = HolographicComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level_combo.setCurrentText("INFO")
        log_layout.addRow(
            self.create_neon_label("Monitor Level:"), self.log_level_combo
        )

        content_layout.addWidget(log_group)

        # Notification Matrix
        notif_group = NeonGroupBox("◈ Alert Transmission Protocol")
        notif_layout = QFormLayout(notif_group)

        self.success_notif_check = QCheckBox("◦ Success neural transmissions")
        self.success_notif_check.setStyleSheet(get_neon_checkbox_style())
        self.success_notif_check.setChecked(True)
        notif_layout.addRow("", self.success_notif_check)

        self.error_notif_check = QCheckBox("◦ Error neural alerts")
        self.error_notif_check.setStyleSheet(get_neon_checkbox_style())
        self.error_notif_check.setChecked(True)
        notif_layout.addRow("", self.error_notif_check)

        content_layout.addWidget(notif_group)
        content_layout.addStretch()

    def create_cyber_action_buttons(self, layout):
        """สร้าง action buttons แบบ cyberpunk"""
        button_frame = QFrame()
        button_frame.setStyleSheet(get_ultra_modern_card_style())

        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(24, 16, 24, 16)
        button_layout.setSpacing(16)

        # Save Config Button
        self.save_btn = CyberButton("◉ Save Neural Configuration", "success", "lg")
        self.save_btn.clicked.connect(self._save_config)
        button_layout.addWidget(self.save_btn)

        # Load Config Button
        self.load_btn = CyberButton("◎ Load Configuration Matrix", "primary", "lg")
        self.load_btn.clicked.connect(self._load_config_file)
        button_layout.addWidget(self.load_btn)

        # Reset Button
        self.reset_btn = CyberButton("⬢ Reset to Quantum Defaults", "warning", "lg")
        self.reset_btn.clicked.connect(self._reset_config)
        button_layout.addWidget(self.reset_btn)

        button_layout.addStretch()
        layout.addWidget(button_frame)

    def create_neon_label(self, text):
        """สร้าง label แบบ neon glow"""
        label = QLabel(text)
        label.setFont(QFont("Inter", 12, QFont.Weight.Medium))
        label.setStyleSheet(
            f"""
            QLabel {{
                color: {UltraModernColors.TEXT_GLOW};
                background: transparent;
                padding: 4px 0px;
                text-shadow: 0 0 8px {UltraModernColors.NEON_BLUE}60;
            }}
        """
        )
        return label

    # Public Methods
    def load_config(self, config: AppConfig):
        """โหลด Configuration ลง UI"""
        self.config = config

        # SharePoint Tab
        self.tenant_id_input.setText(config.tenant_id)
        self.client_id_input.setText(config.client_id)
        self.client_secret_input.setText(config.client_secret)
        self.site_url_input.setText(config.site_url)
        self.list_name_combo.setCurrentText(config.list_name)
        self.use_graph_api_check.setChecked(config.use_graph_api)

        # Database Tab
        self.db_type_combo.setCurrentText(config.database_type)

        # SQL Server
        self.sql_server_input.setText(config.sql_server)
        self.sql_database_combo.setCurrentText(config.sql_database)
        self.sql_username_input.setText(config.sql_username)
        self.sql_password_input.setText(config.sql_password)
        self.sql_table_combo.setCurrentText(config.sql_table_name)
        self.sql_create_table_check.setChecked(config.sql_create_table)
        self.sql_truncate_check.setChecked(config.sql_truncate_before)

        # Advanced Tab
        self.sync_interval_spin.setValue(config.sync_interval)
        self.sync_mode_combo.setCurrentText(config.sync_mode)
        self.batch_size_spin.setValue(config.batch_size)
        self.timeout_spin.setValue(config.connection_timeout)
        self.retries_spin.setValue(config.max_retries)
        self.parallel_check.setChecked(config.parallel_processing)
        self.log_level_combo.setCurrentText(config.log_level)
        self.success_notif_check.setChecked(config.success_notifications)
        self.error_notif_check.setChecked(config.error_notifications)

        # Update database visibility
        self._on_db_type_changed(config.database_type)

    def get_config(self) -> AppConfig:
        """ดึง Configuration จาก UI"""
        config = AppConfig()

        # SharePoint
        config.tenant_id = self.tenant_id_input.text().strip()
        config.client_id = self.client_id_input.text().strip()
        config.client_secret = self.client_secret_input.text().strip()
        config.site_url = self.site_url_input.text().strip()
        config.list_name = self.list_name_combo.currentText().strip()
        config.use_graph_api = self.use_graph_api_check.isChecked()

        # Database
        config.database_type = self.db_type_combo.currentText()

        # SQL Server
        config.sql_server = self.sql_server_input.text().strip()
        config.sql_database = self.sql_database_combo.currentText().strip()
        config.sql_username = self.sql_username_input.text().strip()
        config.sql_password = self.sql_password_input.text().strip()
        config.sql_table_name = self.sql_table_combo.currentText().strip()
        config.sql_create_table = self.sql_create_table_check.isChecked()
        config.sql_truncate_before = self.sql_truncate_check.isChecked()

        # Advanced
        config.sync_interval = self.sync_interval_spin.value()
        config.sync_mode = self.sync_mode_combo.currentText()
        config.batch_size = self.batch_size_spin.value()
        config.connection_timeout = self.timeout_spin.value()
        config.max_retries = self.retries_spin.value()
        config.parallel_processing = self.parallel_check.isChecked()
        config.log_level = self.log_level_combo.currentText()
        config.success_notifications = self.success_notif_check.isChecked()
        config.error_notifications = self.error_notif_check.isChecked()

        return config

    def update_sharepoint_lists(self, lists):
        """อัพเดทรายการ SharePoint Lists"""
        self.list_name_combo.clear()
        for list_item in lists:
            title = list_item.get("Title", "")
            if title:
                self.list_name_combo.addItem(f"◦ {title}")

    def update_databases(self, databases):
        """อัพเดทรายการ Databases"""
        current_text = self.sql_database_combo.currentText()
        self.sql_database_combo.clear()
        for db in databases:
            self.sql_database_combo.addItem(f"◎ {db}")
        self.sql_database_combo.setCurrentText(current_text)

    def update_tables(self, tables):
        """อัพเดทรายการ Tables"""
        current_text = self.sql_table_combo.currentText()
        self.sql_table_combo.clear()
        for table in tables:
            self.sql_table_combo.addItem(f"⬢ {table}")
        self.sql_table_combo.setCurrentText(current_text)

    # Private Methods
    def _on_db_type_changed(self, db_type):
        """จัดการเมื่อเปลี่ยน Database Type"""
        if db_type == "sqlserver":
            self.sqlserver_group.setVisible(True)
        else:
            # For other types, could add more groups
            self.sqlserver_group.setVisible(True)  # Keep visible for now

    def _save_config(self):
        """บันทึก Configuration พร้อม cyber effects"""
        try:
            config = self.get_config()
            self.config_changed.emit(config)

            # Visual feedback
            self.save_btn.setText("◉ Neural Config Saved!")
            QTimer.singleShot(
                2000, lambda: self.save_btn.setText("◉ Save Neural Configuration")
            )

            logger.info("Configuration saved from cyber UI")
        except Exception as e:
            logger.error(f"Failed to save config from cyber UI: {str(e)}")

    def _load_config_file(self):
        """โหลด Configuration จากไฟล์"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Neural Configuration Matrix",
            "",
            "JSON Files (*.json);;All Files (*)",
        )

        if file_path:
            try:
                import json

                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                config = AppConfig.from_dict(data)
                self.load_config(config)
                self.config_changed.emit(config)

                # Visual feedback
                self.load_btn.setText("◎ Matrix Loaded!")
                QTimer.singleShot(
                    2000, lambda: self.load_btn.setText("◎ Load Configuration Matrix")
                )

                logger.info(f"Configuration loaded from neural matrix: {file_path}")

            except Exception as e:
                logger.error(f"Failed to load config from {file_path}: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Neural Matrix Error",
                    f"Failed to load configuration matrix:\n{str(e)}",
                )

    def _reset_config(self):
        """รีเซ็ต Configuration เป็นค่าเริ่มต้น"""
        reply = QMessageBox.question(
            self,
            "Reset Neural Configuration",
            "Are you sure you want to reset all neural pathways to quantum defaults?\n\n"
            + "This will purge all current configuration data.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            default_config = AppConfig()
            self.load_config(default_config)
            self.config_changed.emit(default_config)

            # Visual feedback
            self.reset_btn.setText("⬢ Quantum Reset Complete!")
            QTimer.singleShot(
                2000, lambda: self.reset_btn.setText("⬢ Reset to Quantum Defaults")
            )

            logger.info("Configuration reset to quantum defaults")

    def showEvent(self, event):
        """เมื่อ panel ถูกแสดง"""
        super().showEvent(event)
        # Start any ongoing animations
        for child in self.findChildren(NeonGroupBox):
            if hasattr(child, "glow_timer"):
                child.glow_timer.start(2000)

    def hideEvent(self, event):
        """เมื่อ panel ถูกซ่อน"""
        super().hideEvent(event)
        # Stop animations to save resources
        for child in self.findChildren(NeonGroupBox):
            if hasattr(child, "glow_timer"):
                child.glow_timer.stop()


# Backward compatibility
class ConfigPanel(UltraModernConfigPanel):
    """Alias สำหรับ backward compatibility"""

    pass
