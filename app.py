# app.py - Enhanced version
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
)
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QPixmap, QFont, QPalette, QBrush, QColor, QIcon, QFontDatabase

from config import save_config, load_config
from db import test_sql_connection, test_sqlite_connection
from sharepoint_sync import test_sharepoint_connection


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SharePoint to SQL/SQLite Sync")
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

    def load_fonts(self):
        """Load custom fonts"""
        QFontDatabase.addApplicationFont("assets/fonts/Roboto-Regular.ttf")
        QFontDatabase.addApplicationFont("assets/fonts/Roboto-Bold.ttf")
        QFontDatabase.addApplicationFont("assets/fonts/SegoeUI.ttf")

    def setup_logging(self):
        """Setup logging system"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("system.log"), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def setup_ui(self):
        """Setup main UI components"""
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Left panel (Dashboard)
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, stretch=1)

        # Right panel (Tabs)
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, stretch=3)

        # Set background
        self.set_background()

        # Redirect logging to console
        self.log_handler = LogHandler(self.log_console)
        logging.getLogger().addHandler(self.log_handler)

    def create_left_panel(self):
        """Create the left dashboard panel"""
        panel = QFrame()
        panel.setObjectName("leftPanel")
        panel.setStyleSheet(
            """
            #leftPanel {
                background-color: rgba(30, 30, 60, 180);
                border-radius: 15px;
                border: 2px solid #4A4A8F;
            }
        """
        )
        panel.setFixedWidth(350)

        layout = QVBoxLayout(panel)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("Data Sync")
        header.setObjectName("appHeader")
        header.setFont(QFont("Roboto", 24, QFont.Bold))
        layout.addWidget(header, alignment=Qt.AlignCenter)

        # Logo
        logo = QLabel()
        logo.setPixmap(QPixmap("assets/logo.png").scaled(200, 200, Qt.KeepAspectRatio))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        # Status
        self.status_label = QLabel("🟢 System Ready")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setFont(QFont("Roboto", 12))
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setObjectName("progressBar")
        layout.addWidget(self.progress)

        # Sync buttons
        btn_container = QWidget()
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setSpacing(15)

        self.btn_test = self.create_button("🔍 TEST CONNECTIONS", "#6A5ACD", "#9370DB")
        self.btn_test.clicked.connect(self.test_connections)

        self.btn_start = self.create_button("🚀 START SYNC", "#0066FF", "#00BFFF")
        self.btn_start.clicked.connect(self.start_sync)

        self.btn_clear = self.create_button("🧹 CLEAR LOGS", "#FF5555", "#FF0000")
        self.btn_clear.clicked.connect(self.clear_logs)

        btn_layout.addWidget(self.btn_test)
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_clear)
        layout.addWidget(btn_container)

        # Copyright
        copyright = QLabel("© Thammaphon Chittasuwanna (SDM) | Innovation")
        copyright.setFont(QFont("Segoe UI", 8))
        copyright.setStyleSheet("color: #AAAAAA;")
        layout.addWidget(copyright, alignment=Qt.AlignCenter)

        return panel

    def create_right_panel(self):
        """Create the right configuration panel"""
        panel = QTabWidget()
        panel.setObjectName("rightPanel")
        panel.setStyleSheet(
            """
            #rightPanel {
                background-color: rgba(20, 20, 40, 200);
                border-radius: 15px;
                border: 2px solid #4A4A8F;
            }
            QTabBar::tab {
                background: rgba(40, 40, 80, 200);
                color: white;
                padding: 8px 15px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: rgba(60, 60, 120, 200);
                border-bottom: 2px solid #00BFFF;
            }
        """
        )

        # SharePoint Tab
        sp_tab = self.create_sharepoint_tab()
        panel.addTab(sp_tab, QIcon("assets/icons/sharepoint.png"), "SharePoint")

        # Database Tab
        db_tab = self.create_database_tab()
        panel.addTab(db_tab, QIcon("assets/icons/database.png"), "Database")

        # Log Console
        log_tab = self.create_log_tab()
        panel.addTab(log_tab, QIcon("assets/icons/logs.png"), "Logs")

        return panel

    def create_sharepoint_tab(self):
        """Create SharePoint configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)

        # Connection Group
        conn_group = QGroupBox("SharePoint Connection")
        conn_group.setFont(QFont("Roboto", 10, QFont.Bold))
        conn_layout = QFormLayout(conn_group)

        self.sp_site = QLineEdit()
        self.sp_site.setPlaceholderText(
            "https://yourdomain.sharepoint.com/sites/yoursite"
        )

        self.sp_list = QLineEdit()
        self.sp_list.setPlaceholderText("List Name")

        self.sp_client_id = QLineEdit()
        self.sp_client_id.setPlaceholderText("Client ID")

        self.sp_client_secret = QLineEdit()
        self.sp_client_secret.setPlaceholderText("Client Secret")
        self.sp_client_secret.setEchoMode(QLineEdit.Password)

        self.sp_tenant_id = QLineEdit()
        self.sp_tenant_id.setPlaceholderText("Tenant ID")

        conn_layout.addRow("Site URL:", self.sp_site)
        conn_layout.addRow("List Name:", self.sp_list)
        conn_layout.addRow("Client ID:", self.sp_client_id)
        conn_layout.addRow("Client Secret:", self.sp_client_secret)
        conn_layout.addRow("Tenant ID:", self.sp_tenant_id)

        # Test button
        btn_test_sp = QPushButton("Test SharePoint Connection")
        btn_test_sp.clicked.connect(lambda: self.test_connection("sharepoint"))
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)

        # Advanced Options
        adv_group = QGroupBox("Advanced Options")
        adv_layout = QVBoxLayout(adv_group)

        self.sp_use_graph = QCheckBox("Use Microsoft Graph API")
        self.sp_use_graph.setToolTip(
            "Check if you want to use Graph API instead of SharePoint REST API"
        )

        adv_layout.addWidget(self.sp_use_graph)
        layout.addWidget(adv_group)

        layout.addStretch()
        return tab

    def create_database_tab(self):
        """Create database configuration tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(15, 15, 15, 15)

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

        self.sql_create_new = QCheckBox("Create new table if not exists")
        self.sql_create_new.setChecked(True)

        sql_layout.addRow("Server:", self.sql_server)
        sql_layout.addRow("Database:", self.sql_db)
        sql_layout.addRow("Username:", self.sql_user)
        sql_layout.addRow("Password:", self.sql_pass)
        sql_layout.addRow("Table Name:", self.sql_table)
        sql_layout.addRow(self.sql_create_new)

        self.db_stack.addWidget(sql_panel)

        # SQLite Panel
        sqlite_panel = QWidget()
        sqlite_layout = QFormLayout(sqlite_panel)

        self.sqlite_file = QLineEdit()
        self.sqlite_file.setPlaceholderText("Path to SQLite file")

        self.btn_browse = QPushButton("Browse...")
        self.btn_browse.clicked.connect(self.browse_sqlite_file)

        self.sqlite_table = QLineEdit()
        self.sqlite_table.setPlaceholderText("Table Name")

        self.sqlite_create_new = QCheckBox("Create new table if not exists")
        self.sqlite_create_new.setChecked(True)

        file_layout = QHBoxLayout()
        file_layout.addWidget(self.sqlite_file)
        file_layout.addWidget(self.btn_browse)

        sqlite_layout.addRow("Database File:", file_layout)
        sqlite_layout.addRow("Table Name:", self.sqlite_table)
        sqlite_layout.addRow(self.sqlite_create_new)

        self.db_stack.addWidget(sqlite_panel)
        layout.addWidget(self.db_stack)

        # Test button
        btn_test_db = QPushButton("Test Database Connection")
        btn_test_db.clicked.connect(lambda: self.test_connection("database"))
        layout.addWidget(btn_test_db)

        # Sync Options
        sync_group = QGroupBox("Sync Options")
        sync_layout = QFormLayout(sync_group)

        self.sync_interval = QLineEdit()
        self.sync_interval.setPlaceholderText("Seconds between syncs")
        self.sync_interval.setValidator(QtGui.QIntValidator(60, 86400))

        self.sync_mode = QComboBox()
        self.sync_mode.addItems(["Full Sync", "Incremental Sync"])

        sync_layout.addRow("Sync Interval (sec):", self.sync_interval)
        sync_layout.addRow("Sync Mode:", self.sync_mode)
        layout.addWidget(sync_group)

        # Save button
        btn_save = QPushButton("💾 Save Configuration")
        btn_save.clicked.connect(self.save_configuration)
        layout.addWidget(btn_save)

        layout.addStretch()
        return tab

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
                background-color: rgba(10, 10, 20, 200);
                color: #E0E0E0;
                border: none;
                font-family: 'Consolas';
                font-size: 12px;
            }
        """
        )

        layout.addWidget(self.log_console)
        return tab

    def toggle_db_type(self, db_type):
        """Toggle between SQL Server and SQLite panels"""
        self.db_stack.setCurrentIndex(0 if db_type == "SQL Server" else 1)

    def browse_sqlite_file(self):
        """Open file dialog to select SQLite database"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select SQLite Database", "", "SQLite Databases (*.db *.sqlite)"
        )
        if file_path:
            self.sqlite_file.setText(file_path)

    def create_button(self, text, color1, color2):
        """Create a styled button"""
        btn = QPushButton(text)
        btn.setFont(QFont("Roboto", 11))
        btn.setFixedHeight(45)
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color1}, stop:1 {color2}
                );
                color: white;
                border-radius: 10px;
                border: 2px solid {color2};
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {color2}, stop:1 {color1}
                );
            }}
            QPushButton:pressed {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #555555, stop:1 #777777
                );
            }}
        """
        )
        return btn

    def set_background(self):
        """Set window background"""
        palette = self.palette()
        bg_path = "assets/background.jpg"

        if os.path.exists(bg_path):
            bg = QPixmap(bg_path)
            if not bg.isNull():
                palette.setBrush(
                    QPalette.Window,
                    QBrush(
                        bg.scaled(
                            self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation
                        )
                    ),
                )
        else:
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0, QColor(10, 10, 30))
            gradient.setColorAt(1, QColor(30, 10, 50))
            palette.setBrush(QPalette.Window, QBrush(gradient))

        self.setPalette(palette)

    def load_config_to_ui(self):
        """Load configuration into UI elements"""
        # SharePoint
        self.sp_site.setText(self.config.sharepoint_site)
        self.sp_list.setText(self.config.sharepoint_list)
        self.sp_client_id.setText(self.config.sharepoint_client_id)
        self.sp_client_secret.setText(self.config.sharepoint_client_secret)
        self.sp_tenant_id.setText(self.config.tenant_id)
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

        # Sync options
        self.sync_interval.setText(str(self.config.sync_interval))
        self.sync_mode.setCurrentIndex(0 if self.config.sync_mode == "full" else 1)

    def save_configuration(self):
        """Save configuration from UI to config file"""
        try:
            self.config.sharepoint_site = self.sp_site.text()
            self.config.sharepoint_list = self.sp_list.text()
            self.config.sharepoint_client_id = self.sp_client_id.text()
            self.config.sharepoint_client_secret = self.sp_client_secret.text()
            self.config.tenant_id = self.sp_tenant_id.text()
            self.config.use_graph_api = self.sp_use_graph.isChecked()

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

            self.config.sync_interval = int(self.sync_interval.text())
            self.config.sync_mode = (
                "full" if self.sync_mode.currentIndex() == 0 else "incremental"
            )

            save_config(self.config)
            self.logger.info("Configuration saved successfully")
            QMessageBox.information(
                self, "Success", "Configuration saved successfully!"
            )
        except Exception as e:
            self.logger.error(f"Error saving configuration: {str(e)}")
            QMessageBox.critical(
                self, "Error", f"Failed to save configuration: {str(e)}"
            )

    def test_connections(self):
        """Test both SharePoint and database connections"""
        self.test_connection("sharepoint")
        self.test_connection("database")

    def test_connection(self, connection_type):
        """Test specific connection"""
        try:
            if connection_type == "sharepoint":
                self.update_status("🔍 Testing SharePoint connection...", 10)
                test_sharepoint_connection(
                    self.sp_site.text(),
                    self.sp_list.text(),
                    self.sp_client_id.text(),
                    self.sp_client_secret.text(),
                    self.sp_tenant_id.text(),
                )
                self.update_status("✅ SharePoint connection successful!", 50)
                QMessageBox.information(
                    self, "Success", "SharePoint connection successful!"
                )
            else:
                self.update_status("🔍 Testing database connection...", 60)
                if self.db_type.currentText() == "SQL Server":
                    test_sql_connection(
                        self.sql_server.text(),
                        self.sql_db.text(),
                        self.sql_user.text(),
                        self.sql_pass.text(),
                    )
                    self.update_status("✅ SQL Server connection successful!", 100)
                    QMessageBox.information(
                        self, "Success", "SQL Server connection successful!"
                    )
                else:
                    test_sqlite_connection(self.sqlite_file.text())
                    self.update_status("✅ SQLite connection successful!", 100)
                    QMessageBox.information(
                        self, "Success", "SQLite connection successful!"
                    )
        except Exception as e:
            self.update_status(
                f"❌ {connection_type.capitalize()} connection failed", 0
            )
            self.logger.error(
                f"{connection_type.capitalize()} connection test failed: {str(e)}"
            )
            QMessageBox.critical(
                self,
                "Error",
                f"{connection_type.capitalize()} connection failed:\n{str(e)}",
            )
        finally:
            QTimer.singleShot(5000, self.reset_status)

    def start_sync(self):
        """Start the synchronization process"""
        self.btn_start.setEnabled(False)
        self.logger.info("Starting synchronization process...")
        self.update_status("🔄 Connecting to SharePoint...", 25)

        try:
            # TODO: Implement actual sync logic
            self.update_status("⬇️ Downloading data...", 50)
            # sync_data()  # This would be the actual sync function

            # Simulate success
            self.update_status("✅ Sync completed!", 100)
            self.logger.info("Synchronization completed successfully")
        except Exception as e:
            self.update_status(f"❌ Error: {str(e)}", 0)
            self.logger.error(f"Synchronization failed: {str(e)}")
        finally:
            self.btn_start.setEnabled(True)
            QTimer.singleShot(5000, self.reset_status)

    def clear_logs(self):
        """Clear log console"""
        self.log_console.clear()
        self.logger.info("Log console cleared")

    def update_status(self, message, progress):
        """Update status label and progress bar"""
        self.status_label.setText(message)
        self.progress.setValue(progress)
        QApplication.processEvents()

    def reset_status(self):
        """Reset status to ready"""
        self.update_status("🟢 System Ready", 0)

    def resizeEvent(self, event):
        """Handle window resize"""
        self.set_background()
        super().resizeEvent(event)


class LogHandler(logging.Handler):
    """Custom handler to display logs in UI"""

    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.append(msg)
        self.text_widget.verticalScrollBar().setValue(
            self.text_widget.verticalScrollBar().maximum()
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application style and font
    app.setStyle("Fusion")
    font = QFont("Roboto", 10)
    app.setFont(font)

    window = MainApp()
    window.show()
    sys.exit(app.exec_())
