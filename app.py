# app.py - Modern UI version
import sys
import os
import logging
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QProgressBar,
    QTextEdit,
    QFrame,
    QTabWidget,
    QLineEdit,
    QComboBox,
    QGroupBox,
    QFormLayout,
    QMessageBox,
    QCheckBox,
    QFileDialog,
    QStackedWidget,
    QListWidget,
    QListWidgetItem,
)
from PyQt5.QtCore import QTimer, Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import (
    QPixmap,
    QFont,
    QPalette,
    QBrush,
    QColor,
    QFontDatabase,
    QLinearGradient,
)

from config import save_config, load_config
from sharepoint_sync import SharePointConnector, test_sharepoint_connection
from db import DatabaseConnector


class SyncThread(QThread):
    update_signal = pyqtSignal(str, int)
    finished_signal = pyqtSignal(bool)

    def __init__(self, config):
        super().__init__()
        self.config = config

    def run(self):
        try:
            self.update_signal.emit("🔄 Connecting to SharePoint...", 10)
            sp_connector = SharePointConnector(
                self.config.sharepoint_site,
                self.config.sharepoint_client_id,
                self.config.sharepoint_client_secret,
                self.config.tenant_id,
            )

            self.update_signal.emit("⬇️ Downloading data...", 30)
            df = sp_connector.fetch_data(self.config.sharepoint_list)

            if df is None or df.empty:
                self.update_signal.emit("⚠️ No data to sync", 50)
                self.finished_signal.emit(False)
                return

            self.update_signal.emit("💾 Preparing database...", 60)
            db_connector = DatabaseConnector(self.config)

            if self.config.database_type == "sqlserver":
                table_name = self.config.sql_table_name
            else:
                table_name = self.config.sqlite_table_name

            if (
                self.config.database_type == "sqlserver"
                and self.config.sql_create_table
            ) or (
                self.config.database_type == "sqlite"
                and self.config.sqlite_create_table
            ):
                self.update_signal.emit("🛠️ Creating table if needed...", 70)
                db_connector.create_table(df, table_name)

            self.update_signal.emit("📤 Inserting data...", 80)
            db_connector.insert_data(df, table_name)

            self.update_signal.emit("✅ Sync completed!", 100)
            self.finished_signal.emit(True)
        except Exception as e:
            self.update_signal.emit(f"❌ Error: {str(e)}", 0)
            self.finished_signal.emit(False)


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SharePoint to Database Sync")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(QSize(1000, 700))

        # Load fonts
        self.load_fonts()

        # Setup logging and UI
        self.setup_logging()
        self.setup_ui()

        # Load saved configuration
        self.config = load_config()
        self.load_config_to_ui()

        # Setup sync timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.start_sync)
        self.timer.start(self.config.sync_interval * 1000)

        # Current sync thread
        self.sync_thread = None

    def load_fonts(self):
        """Load custom fonts"""
        font_dir = "assets/fonts/"
        if not os.path.exists(font_dir):
            os.makedirs(font_dir)

        # Try to load modern fonts
        try:
            QFontDatabase.addApplicationFont(font_dir + "Roboto-Regular.ttf")
            QFontDatabase.addApplicationFont(font_dir + "Roboto-Medium.ttf")
            QFontDatabase.addApplicationFont(font_dir + "Roboto-Bold.ttf")
            QFontDatabase.addApplicationFont(font_dir + "Montserrat-Regular.ttf")
            QFontDatabase.addApplicationFont(font_dir + "Montserrat-Bold.ttf")
        except:
            pass  # Use system fonts if custom fonts not available

    def setup_logging(self):
        """Setup logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("system.log"), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def setup_ui(self):
        """Setup main UI components with modern design"""
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # Left panel (Dashboard) - Modern card style
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, stretch=1)

        # Right panel (Tabs) - Modern card style
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, stretch=3)

        # Set modern background
        self.set_background()

        # Redirect logging to console
        self.log_handler = LogHandler(self.log_console)
        logging.getLogger().addHandler(self.log_handler)

    def create_left_panel(self):
        """Create the left dashboard panel with modern design"""
        panel = QFrame()
        panel.setObjectName("leftPanel")
        panel.setStyleSheet(
            """
            #leftPanel {
                background-color: rgba(40, 44, 52, 0.95);
                border-radius: 12px;
                border: 1px solid #444;
            }
            QLabel#appHeader {
                color: #61afef;
                font-size: 24px;
                font-weight: bold;
            }
            QLabel#statusLabel {
                color: #abb2bf;
                font-size: 14px;
            }
            #progressBar {
                height: 8px;
                border-radius: 4px;
                background: #3e4451;
            }
            #progressBar::chunk {
                background: #61afef;
                border-radius: 4px;
            }
        """
        )
        panel.setFixedWidth(320)

        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header with modern font
        header = QLabel("Data Sync Dashboard")
        header.setObjectName("appHeader")
        header.setFont(QFont("Montserrat", 18, QFont.Bold))
        layout.addWidget(header, alignment=Qt.AlignCenter)

        # Logo
        logo = QLabel()
        logo_pixmap = QPixmap("assets/logo.png")
        if not logo_pixmap.isNull():
            logo.setPixmap(logo_pixmap.scaled(180, 180, Qt.KeepAspectRatio))
        else:
            # Create a placeholder if logo is missing
            logo.setText("LOGO")
            logo.setAlignment(Qt.AlignCenter)
            logo.setStyleSheet("font-size: 24px; font-weight: bold; color: #61afef;")
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        # Status
        self.status_label = QLabel("🟢 System Ready")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setFont(QFont("Roboto", 11))
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setObjectName("progressBar")
        layout.addWidget(self.progress)

        # Sync buttons with modern style
        btn_container = QWidget()
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setSpacing(12)

        self.btn_test = self.create_modern_button("🔍 Test Connections", "#4b6eaf")
        self.btn_test.clicked.connect(self.test_connections)

        self.btn_start = self.create_modern_button("🚀 Start Sync", "#2e7d32")
        self.btn_start.clicked.connect(self.start_sync)

        self.btn_clear = self.create_modern_button("🧹 Clear Logs", "#c62828")
        self.btn_clear.clicked.connect(self.clear_logs)

        btn_layout.addWidget(self.btn_test)
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_clear)
        layout.addWidget(btn_container)

        # Copyright with smaller font
        copyright = QLabel("© 2023 SharePoint Sync Tool")
        copyright.setFont(QFont("Roboto", 8))
        copyright.setStyleSheet("color: #666;")
        layout.addWidget(copyright, alignment=Qt.AlignCenter)

        return panel

    def create_modern_button(self, text, color):
        """Create a modern styled button"""
        btn = QPushButton(text)
        btn.setFont(QFont("Roboto", 11, QFont.Medium))
        btn.setFixedHeight(42)
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
                border: none;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {self.adjust_color(color, 20)};
            }}
            QPushButton:pressed {{
                background-color: {self.adjust_color(color, -20)};
            }}
        """
        )
        return btn

    def adjust_color(self, color, amount):
        """Adjust color brightness"""
        # Convert hex to RGB
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)

        # Adjust brightness
        r = max(0, min(255, r + amount))
        g = max(0, min(255, g + amount))
        b = max(0, min(255, b + amount))

        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"

    def create_right_panel(self):
        """Create the right configuration panel with modern tabs"""
        panel = QTabWidget()
        panel.setObjectName("rightPanel")
        panel.setStyleSheet(
            """
            #rightPanel {
                background-color: rgba(40, 44, 52, 0.9);
                border-radius: 12px;
                border: 1px solid #444;
            }
            QTabBar::tab {
                background: #3e4451;
                color: #abb2bf;
                padding: 8px 16px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
                font-family: 'Roboto';
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background: #61afef;
                color: #282c34;
                font-weight: bold;
            }
            QGroupBox {
                border: 1px solid #3e4451;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-family: 'Roboto';
                font-size: 14px;
                font-weight: bold;
                color: #abb2bf;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit, QComboBox {
                background: #3e4451;
                border: 1px solid #3e4451;
                border-radius: 4px;
                padding: 6px;
                color: #abb2bf;
                font-family: 'Roboto';
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #61afef;
            }
            QPushButton {
                background-color: #61afef;
                color: #282c34;
                border-radius: 4px;
                padding: 6px 12px;
                font-family: 'Roboto';
                font-size: 12px;
                font-weight: medium;
            }
            QPushButton:hover {
                background-color: #528bcc;
            }
            QListWidget {
                background: #3e4451;
                border: 1px solid #3e4451;
                border-radius: 4px;
                color: #abb2bf;
                font-family: 'Roboto';
                font-size: 12px;
            }
        """
        )

        # SharePoint Tab
        sp_tab = self.create_sharepoint_tab()
        panel.addTab(sp_tab, "SharePoint")

        # Database Tab
        db_tab = self.create_database_tab()
        panel.addTab(db_tab, "Database")

        # Log Console
        log_tab = self.create_log_tab()
        panel.addTab(log_tab, "Logs")

        return panel

    def create_sharepoint_tab(self):
        """Create SharePoint configuration tab with modern design"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Connection Group
        conn_group = QGroupBox("SharePoint Connection")
        conn_layout = QFormLayout(conn_group)
        conn_layout.setVerticalSpacing(12)
        conn_layout.setHorizontalSpacing(15)

        # Tenant ID
        self.sp_tenant_id = QLineEdit()
        self.sp_tenant_id.setPlaceholderText("Tenant ID")
        conn_layout.addRow("Tenant ID:", self.sp_tenant_id)

        # Client ID
        self.sp_client_id = QLineEdit()
        self.sp_client_id.setPlaceholderText("Client ID")
        conn_layout.addRow("Client ID:", self.sp_client_id)

        # Client Secret
        self.sp_client_secret = QLineEdit()
        self.sp_client_secret.setPlaceholderText("Client Secret")
        self.sp_client_secret.setEchoMode(QLineEdit.Password)
        conn_layout.addRow("Client Secret:", self.sp_client_secret)

        # Site selection
        self.sp_site_list = QListWidget()
        self.sp_site_list.setFixedHeight(100)
        self.btn_refresh_sites = QPushButton("Refresh Sites")
        self.btn_refresh_sites.clicked.connect(self.refresh_sharepoint_sites)

        site_layout = QHBoxLayout()
        site_layout.addWidget(self.sp_site_list)
        site_layout.addWidget(self.btn_refresh_sites)
        conn_layout.addRow("Available Sites:", site_layout)

        # List selection
        self.sp_list_list = QListWidget()
        self.sp_list_list.setFixedHeight(100)
        self.btn_refresh_lists = QPushButton("Refresh Lists")
        self.btn_refresh_lists.clicked.connect(self.refresh_sharepoint_lists)

        list_layout = QHBoxLayout()
        list_layout.addWidget(self.sp_list_list)
        list_layout.addWidget(self.btn_refresh_lists)
        conn_layout.addRow("Available Lists:", list_layout)

        # Test button
        btn_test_sp = QPushButton("Test SharePoint Connection")
        btn_test_sp.clicked.connect(lambda: self.test_connection("sharepoint"))
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)

        # Advanced Options
        adv_group = QGroupBox("Advanced Options")
        adv_layout = QVBoxLayout(adv_group)

        self.sp_use_graph = QCheckBox("Use Microsoft Graph API")
        self.sp_use_graph.setToolTip("Use Graph API instead of SharePoint REST API")
        adv_layout.addWidget(self.sp_use_graph)

        layout.addWidget(adv_group)
        layout.addStretch()
        return tab

    def refresh_sharepoint_sites(self):
        """Refresh list of SharePoint sites"""
        try:
            tenant_id = self.sp_tenant_id.text()
            client_id = self.sp_client_id.text()
            client_secret = self.sp_client_secret.text()

            if not all([tenant_id, client_id, client_secret]):
                QMessageBox.warning(
                    self,
                    "Warning",
                    "Please enter Tenant ID, Client ID and Client Secret first",
                )
                return

            self.sp_site_list.clear()
            self.sp_list_list.clear()

            connector = SharePointConnector(
                "https://dummy.sharepoint.com",  # Dummy URL just to initialize
                client_id,
                client_secret,
                tenant_id,
            )

            sites = connector.get_sites()
            for site in sites:
                item = QListWidgetItem(
                    site.get("Title", "") + " (" + site.get("Url", "") + ")"
                )
                item.setData(Qt.UserRole, site.get("Url"))
                self.sp_site_list.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch sites: {str(e)}")

    def refresh_sharepoint_lists(self):
        """Refresh lists for selected SharePoint site"""
        try:
            selected_items = self.sp_site_list.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Warning", "Please select a site first")
                return

            site_url = selected_items[0].data(Qt.UserRole)
            tenant_id = self.sp_tenant_id.text()
            client_id = self.sp_client_id.text()
            client_secret = self.sp_client_secret.text()

            connector = SharePointConnector(
                site_url, client_id, client_secret, tenant_id
            )

            self.sp_list_list.clear()
            lists = connector.get_lists(site_url)
            for list_item in lists:
                item = QListWidgetItem(list_item.get("Title", ""))
                item.setData(Qt.UserRole, list_item.get("Title"))
                self.sp_list_list.addItem(item)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch lists: {str(e)}")

    def create_database_tab(self):
        """Create database configuration tab with modern design"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Database Type Selection
        db_type_group = QGroupBox("Database Type")
        db_type_layout = QHBoxLayout(db_type_group)

        self.db_type = QComboBox()
        self.db_type.addItems(["SQL Server", "SQLite"])
        self.db_type.currentTextChanged.connect(self.toggle_db_type)

        db_type_layout.addWidget(QLabel("Select:"))
        db_type_layout.addWidget(self.db_type)
        db_type_layout.addStretch()
        layout.addWidget(db_type_group)

        # Stacked widget for different DB types
        self.db_stack = QStackedWidget()

        # SQL Server Panel
        sql_panel = QWidget()
        sql_layout = QFormLayout(sql_panel)
        sql_layout.setVerticalSpacing(12)
        sql_layout.setHorizontalSpacing(15)

        self.sql_server = QLineEdit()
        self.sql_server.setPlaceholderText("server.database.windows.net")

        self.sql_db = QLineEdit()
        self.sql_db.setPlaceholderText("Database Name")

        self.sql_user = QLineEdit()
        self.sql_user.setPlaceholderText("Username")

        self.sql_pass = QLineEdit()
        self.sql_pass.setPlaceholderText("Password")
        self.sql_pass.setEchoMode(QLineEdit.Password)

        self.sql_table = QLineEdit()
        self.sql_table.setPlaceholderText("Table Name")

        self.btn_refresh_db = QPushButton("Refresh Databases")
        self.btn_refresh_db.clicked.connect(self.refresh_databases)

        self.sql_db_list = QListWidget()
        self.sql_db_list.setFixedHeight(80)

        self.btn_refresh_tables = QPushButton("Refresh Tables")
        self.btn_refresh_tables.clicked.connect(self.refresh_tables)

        self.sql_table_list = QListWidget()
        self.sql_table_list.setFixedHeight(80)

        self.sql_create_new = QCheckBox("Create new table if not exists")
        self.sql_create_new.setChecked(True)

        sql_layout.addRow("Server:", self.sql_server)
        sql_layout.addRow("Database:", self.sql_db)
        sql_layout.addRow("Username:", self.sql_user)
        sql_layout.addRow("Password:", self.sql_pass)
        sql_layout.addRow("Available Databases:", self.sql_db_list)
        sql_layout.addRow(self.btn_refresh_db)
        sql_layout.addRow("Table Name:", self.sql_table)
        sql_layout.addRow("Available Tables:", self.sql_table_list)
        sql_layout.addRow(self.btn_refresh_tables)
        sql_layout.addRow(self.sql_create_new)

        self.db_stack.addWidget(sql_panel)

        # SQLite Panel
        sqlite_panel = QWidget()
        sqlite_layout = QFormLayout(sqlite_panel)
        sqlite_layout.setVerticalSpacing(12)
        sqlite_layout.setHorizontalSpacing(15)

        self.sqlite_file = QLineEdit()
        self.sqlite_file.setPlaceholderText("database.db")
        self.btn_browse = QPushButton("Browse...")
        self.btn_browse.clicked.connect(self.browse_sqlite_file)

        file_layout = QHBoxLayout()
        file_layout.addWidget(self.sqlite_file)
        file_layout.addWidget(self.btn_browse)

        self.sqlite_table = QLineEdit()
        self.sqlite_table.setPlaceholderText("Table Name")

        self.btn_refresh_sqlite_tables = QPushButton("Refresh Tables")
        self.btn_refresh_sqlite_tables.clicked.connect(self.refresh_sqlite_tables)

        self.sqlite_table_list = QListWidget()
        self.sqlite_table_list.setFixedHeight(80)

        self.sqlite_create_new = QCheckBox("Create new table if not exists")
        self.sqlite_create_new.setChecked(True)

        sqlite_layout.addRow("Database File:", file_layout)
        sqlite_layout.addRow("Table Name:", self.sqlite_table)
        sqlite_layout.addRow("Available Tables:", self.sqlite_table_list)
        sqlite_layout.addRow(self.btn_refresh_sqlite_tables)
        sqlite_layout.addRow(self.sqlite_create_new)

        self.db_stack.addWidget(sqlite_panel)
        layout.addWidget(self.db_stack)

        # Test button
        btn_test_db = QPushButton("Test Database Connection")
        btn_test_db.clicked.connect(lambda: self.test_connection("database"))
        layout.addWidget(btn_test_db)

        layout.addStretch()
        return tab

    def toggle_db_type(self, db_type):
        """Switch between SQL Server and SQLite panels"""
        if db_type == "SQL Server":
            self.db_stack.setCurrentIndex(0)
        else:
            self.db_stack.setCurrentIndex(1)

    def browse_sqlite_file(self):
        """Open file dialog to select SQLite database"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select SQLite Database", "", "SQLite Databases (*.db *.sqlite)"
        )
        if filename:
            self.sqlite_file.setText(filename)
            self.refresh_sqlite_tables()

    def refresh_databases(self):
        """Refresh list of available SQL Server databases"""
        try:
            server = self.sql_server.text()
            username = self.sql_user.text()
            password = self.sql_pass.text()

            if not server:
                QMessageBox.warning(
                    self, "Warning", "Please enter server address first"
                )
                return

            self.sql_db_list.clear()

            # Create temp config for testing
            temp_config = load_config()
            temp_config.sql_server = server
            temp_config.sql_username = username
            temp_config.sql_password = password

            db_connector = DatabaseConnector(temp_config)
            databases = db_connector.get_databases()

            for db in databases:
                self.sql_db_list.addItem(db)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch databases: {str(e)}")

    def refresh_tables(self):
        """Refresh list of available tables in SQL Server database"""
        try:
            server = self.sql_server.text()
            username = self.sql_user.text()
            password = self.sql_pass.text()
            database = self.sql_db.text()

            if not all([server, database]):
                QMessageBox.warning(
                    self, "Warning", "Please enter server and database first"
                )
                return

            self.sql_table_list.clear()

            # Create temp config for testing
            temp_config = load_config()
            temp_config.sql_server = server
            temp_config.sql_username = username
            temp_config.sql_password = password
            temp_config.sql_database = database

            db_connector = DatabaseConnector(temp_config)
            tables = db_connector.get_tables()

            for table in tables:
                self.sql_table_list.addItem(table)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch tables: {str(e)}")

    def refresh_sqlite_tables(self):
        """Refresh list of available tables in SQLite database"""
        try:
            db_file = self.sqlite_file.text()

            if not db_file:
                QMessageBox.warning(self, "Warning", "Please select SQLite file first")
                return

            self.sqlite_table_list.clear()

            # Create temp config for testing
            temp_config = load_config()
            temp_config.database_type = "sqlite"
            temp_config.sqlite_file = db_file

            db_connector = DatabaseConnector(temp_config)
            tables = db_connector.get_tables()

            for table in tables:
                self.sqlite_table_list.addItem(table)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch tables: {str(e)}")

    def create_log_tab(self):
        """Create log console tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)

        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet(
            """
            QTextEdit {
                background-color: #282c34;
                color: #abb2bf;
                font-family: 'Roboto Mono';
                font-size: 11px;
                border-radius: 4px;
                padding: 8px;
            }
        """
        )

        layout.addWidget(self.log_console)
        return tab

    def set_background(self):
        """Set modern background with gradient"""
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(40, 44, 52))
        gradient.setColorAt(1, QColor(30, 34, 42))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

    def load_config_to_ui(self):
        """Load configuration into UI elements"""
        # SharePoint
        self.sp_tenant_id.setText(self.config.tenant_id)
        self.sp_client_id.setText(self.config.sharepoint_client_id)
        self.sp_client_secret.setText(self.config.sharepoint_client_secret)
        self.sp_use_graph.setChecked(self.config.use_graph_api)

        # Database
        if self.config.database_type == "sqlserver":
            self.db_type.setCurrentIndex(0)
            self.sql_server.setText(self.config.sql_server)
            self.sql_db.setText(self.config.sql_database)
            self.sql_user.setText(self.config.sql_username)
            self.sql_pass.setText(self.config.sql_password)
            self.sql_table.setText(self.config.sql_table_name)
            self.sql_create_new.setChecked(self.config.sql_create_table)
        else:
            self.db_type.setCurrentIndex(1)
            self.sqlite_file.setText(self.config.sqlite_file)
            self.sqlite_table.setText(self.config.sqlite_table_name)
            self.sqlite_create_new.setChecked(self.config.sqlite_create_table)

    def save_ui_to_config(self):
        """Save UI values to configuration"""
        # SharePoint
        self.config.tenant_id = self.sp_tenant_id.text()
        self.config.sharepoint_client_id = self.sp_client_id.text()
        self.config.sharepoint_client_secret = self.sp_client_secret.text()
        self.config.use_graph_api = self.sp_use_graph.isChecked()

        # Database
        if self.db_type.currentText() == "SQL Server":
            self.config.database_type = "sqlserver"
            self.config.sql_server = self.sql_server.text()
            self.config.sql_database = self.sql_db.text()
            self.config.sql_username = self.sql_user.text()
            self.config.sql_password = self.sql_pass.text()
            self.config.sql_table_name = self.sql_table.text()
            self.config.sql_create_table = self.sql_create_new.isChecked()
        else:
            self.config.database_type = "sqlite"
            self.config.sqlite_file = self.sqlite_file.text()
            self.config.sqlite_table_name = self.sqlite_table.text()
            self.config.sqlite_create_table = self.sqlite_create_new.isChecked()

        save_config(self.config)

    def test_connection(self, connection_type):
        """Test either SharePoint or database connection"""
        try:
            self.save_ui_to_config()

            if connection_type == "sharepoint":
                success = test_sharepoint_connection(
                    self.config.sharepoint_site,
                    self.config.sharepoint_client_id,
                    self.config.sharepoint_client_secret,
                    self.config.tenant_id,
                )
                if success:
                    QMessageBox.information(
                        self, "Success", "SharePoint connection successful!"
                    )
                else:
                    QMessageBox.warning(self, "Warning", "SharePoint connection failed")
            else:
                db_connector = DatabaseConnector(self.config)
                success = db_connector.test_connection()
                if success:
                    QMessageBox.information(
                        self, "Success", "Database connection successful!"
                    )
                else:
                    QMessageBox.warning(self, "Warning", "Database connection failed")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection test failed: {str(e)}")

    def test_connections(self):
        """Test both SharePoint and database connections"""
        self.test_connection("sharepoint")
        self.test_connection("database")

    def start_sync(self):
        """Start the sync process in a separate thread"""
        if self.sync_thread and self.sync_thread.isRunning():
            QMessageBox.warning(self, "Warning", "Sync is already in progress")
            return

        self.save_ui_to_config()

        # Validate SharePoint selection
        selected_site = self.sp_site_list.currentItem()
        if not selected_site:
            QMessageBox.warning(
                self, "Warning", "Please select a SharePoint site first"
            )
            return

        selected_list = self.sp_list_list.currentItem()
        if not selected_list:
            QMessageBox.warning(
                self, "Warning", "Please select a SharePoint list first"
            )
            return

        # Update config with selected site and list
        self.config.sharepoint_site = selected_site.data(Qt.UserRole)
        self.config.sharepoint_list = selected_list.data(Qt.UserRole)

        # Validate database selection
        if self.db_type.currentText() == "SQL Server":
            if not self.sql_db.text():
                QMessageBox.warning(self, "Warning", "Please select a database first")
                return
            if not self.sql_table.text():
                QMessageBox.warning(
                    self, "Warning", "Please enter or select a table name"
                )
                return
        else:
            if not self.sqlite_file.text():
                QMessageBox.warning(self, "Warning", "Please select SQLite file first")
                return
            if not self.sqlite_table.text():
                QMessageBox.warning(
                    self, "Warning", "Please enter or select a table name"
                )
                return

        # Start sync thread
        self.sync_thread = SyncThread(self.config)
        self.sync_thread.update_signal.connect(self.update_status)
        self.sync_thread.finished_signal.connect(self.sync_finished)
        self.sync_thread.start()

        # Disable buttons during sync
        self.btn_test.setEnabled(False)
        self.btn_start.setEnabled(False)

    def update_status(self, message, progress):
        """Update status message and progress bar"""
        self.status_label.setText(message)
        self.progress.setValue(progress)
        self.log_console.append(message)

    def sync_finished(self, success):
        """Handle sync completion"""
        self.btn_test.setEnabled(True)
        self.btn_start.setEnabled(True)

        if success:
            self.update_status("✅ Sync completed successfully", 100)
        else:
            self.update_status("❌ Sync failed", 0)

    def clear_logs(self):
        """Clear the log console"""
        self.log_console.clear()


class LogHandler(logging.Handler):
    """Custom logging handler to output to QTextEdit"""

    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit

    def emit(self, record):
        msg = self.format(record)
        self.text_edit.append(msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    # Create and show main window
    window = MainApp()
    window.show()

    sys.exit(app.exec_())
