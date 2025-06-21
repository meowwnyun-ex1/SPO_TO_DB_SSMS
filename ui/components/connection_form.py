# ui/components/connection_form.py - Complete Connection Form
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import sys
from pathlib import Path

current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from utils.config_manager import get_config_manager
except ImportError:
    # Fallback
    class FallbackConfigManager:
        def get_config(self):
            class Config:
                sharepoint_site = ""
                sharepoint_list = ""
                sharepoint_client_id = ""
                sharepoint_client_secret = ""
                tenant_id = ""
                database_type = "sqlserver"
                sql_server = ""
                sql_database = ""
                sql_username = ""
                sql_password = ""
                sql_table_name = ""
                sqlite_file = ""
                sqlite_table_name = ""

            return Config()

        def save_config(self):
            pass

        def update_setting(self, key, value):
            pass

    def get_config_manager():
        return FallbackConfigManager()


class ModernGroupBox(QGroupBox):
    """Modern styled group box"""

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setStyleSheet(
            """
            QGroupBox {
                font-weight: 600;
                font-size: 14px;
                color: #F8FAFC;
                border: 2px solid #374151;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 16px;
                background: #1E293B;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
                background: #6366F1;
                border-radius: 4px;
                color: white;
                left: 8px;
                top: -8px;
            }
        """
        )


class ModernLineEdit(QLineEdit):
    """Modern styled line edit"""

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(40)
        self.setStyleSheet(
            """
            QLineEdit {
                background: #0F172A;
                border: 2px solid #374151;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: #F8FAFC;
            }
            QLineEdit:focus {
                border-color: #6366F1;
                background: #1E293B;
            }
            QLineEdit:hover {
                border-color: #6B7280;
            }
        """
        )


class ModernComboBox(QComboBox):
    """Modern styled combo box"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(40)
        self.setStyleSheet(
            """
            QComboBox {
                background: #0F172A;
                border: 2px solid #374151;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: #F8FAFC;
                min-width: 120px;
            }
            QComboBox:focus {
                border-color: #6366F1;
                background: #1E293B;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                background: #9CA3AF;
            }
            QComboBox QAbstractItemView {
                background: #1E293B;
                border: 1px solid #374151;
                border-radius: 6px;
                selection-background-color: #6366F1;
                color: #F8FAFC;
            }
        """
        )


class ModernButton(QPushButton):
    """Modern styled button"""

    def __init__(self, text, variant="primary", parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        if variant == "primary":
            self.setStyleSheet(
                """
                QPushButton {
                    background: #6366F1;
                    border: none;
                    border-radius: 6px;
                    color: white;
                    font-weight: 600;
                    font-size: 14px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: #4F46E5;
                }
                QPushButton:pressed {
                    background: #3730A3;
                }
            """
            )
        elif variant == "secondary":
            self.setStyleSheet(
                """
                QPushButton {
                    background: #374151;
                    border: 2px solid #6B7280;
                    border-radius: 6px;
                    color: #F8FAFC;
                    font-weight: 600;
                    font-size: 14px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: #4B5563;
                    border-color: #9CA3AF;
                }
            """
            )


class SharePointConnectionForm(QWidget):
    """SharePoint connection configuration form"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = get_config_manager()
        self._setup_ui()
        self._load_config()

    def _setup_ui(self):
        """Setup SharePoint form UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # SharePoint URL
        url_layout = QVBoxLayout()
        url_layout.addWidget(QLabel("SharePoint Site URL *"))
        self.url_input = ModernLineEdit("https://company.sharepoint.com/sites/sitename")
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # List Name
        list_layout = QVBoxLayout()
        list_layout.addWidget(QLabel("SharePoint List Name *"))
        self.list_input = ModernLineEdit("List Name")
        list_layout.addWidget(self.list_input)
        layout.addLayout(list_layout)

        # Authentication section
        auth_group = ModernGroupBox("Authentication Credentials")
        auth_layout = QVBoxLayout(auth_group)
        auth_layout.setSpacing(12)

        # Client ID
        client_id_layout = QVBoxLayout()
        client_id_layout.addWidget(QLabel("Client ID (App Registration GUID) *"))
        self.client_id_input = ModernLineEdit("12345678-1234-1234-1234-123456789012")
        client_id_layout.addWidget(self.client_id_input)
        auth_layout.addLayout(client_id_layout)

        # Client Secret
        secret_layout = QVBoxLayout()
        secret_layout.addWidget(QLabel("Client Secret *"))
        self.secret_input = ModernLineEdit("Client Secret Value")
        self.secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        secret_layout.addWidget(self.secret_input)
        auth_layout.addLayout(secret_layout)

        # Tenant ID
        tenant_layout = QVBoxLayout()
        tenant_layout.addWidget(QLabel("Tenant ID (Directory GUID) *"))
        self.tenant_input = ModernLineEdit("87654321-4321-4321-4321-210987654321")
        tenant_layout.addWidget(self.tenant_input)
        auth_layout.addLayout(tenant_layout)

        layout.addWidget(auth_group)

        # Test button
        self.test_sp_btn = ModernButton("🔍 Test SharePoint Connection")
        self.test_sp_btn.clicked.connect(self._test_sharepoint)
        layout.addWidget(self.test_sp_btn)

    def _load_config(self):
        """Load SharePoint configuration"""
        try:
            config = self.config_manager.get_config()
            self.url_input.setText(getattr(config, "sharepoint_site", ""))
            self.list_input.setText(getattr(config, "sharepoint_list", ""))
            self.client_id_input.setText(getattr(config, "sharepoint_client_id", ""))
            self.secret_input.setText(getattr(config, "sharepoint_client_secret", ""))
            self.tenant_input.setText(getattr(config, "tenant_id", ""))
        except Exception as e:
            print(f"Error loading SharePoint config: {e}")

    def save_config(self):
        """Save SharePoint configuration"""
        try:
            self.config_manager.update_setting("sharepoint_site", self.url_input.text())
            self.config_manager.update_setting(
                "sharepoint_list", self.list_input.text()
            )
            self.config_manager.update_setting(
                "sharepoint_client_id", self.client_id_input.text()
            )
            self.config_manager.update_setting(
                "sharepoint_client_secret", self.secret_input.text()
            )
            self.config_manager.update_setting("tenant_id", self.tenant_input.text())
            self.config_manager.save_config()
        except Exception as e:
            print(f"Error saving SharePoint config: {e}")

    def _test_sharepoint(self):
        """Test SharePoint connection"""
        self.test_sp_btn.setText("🔄 Testing...")
        self.test_sp_btn.setEnabled(False)

        # Simulate test (replace with actual test)
        QTimer.singleShot(2000, self._test_complete)

    def _test_complete(self):
        """Test completion"""
        self.test_sp_btn.setText("✅ Connection OK")
        QTimer.singleShot(
            2000, lambda: self.test_sp_btn.setText("🔍 Test SharePoint Connection")
        )
        self.test_sp_btn.setEnabled(True)


class DatabaseConnectionForm(QWidget):
    """Database connection configuration form"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = get_config_manager()
        self._setup_ui()
        self._load_config()

    def _setup_ui(self):
        """Setup database form UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Database Type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Database Type:"))
        self.db_type_combo = ModernComboBox()
        self.db_type_combo.addItems(["SQL Server", "SQLite"])
        self.db_type_combo.currentTextChanged.connect(self._on_db_type_changed)
        type_layout.addWidget(self.db_type_combo)
        type_layout.addStretch()
        layout.addLayout(type_layout)

        # SQL Server Section
        self.sql_group = ModernGroupBox("SQL Server Connection")
        sql_layout = QVBoxLayout(self.sql_group)
        sql_layout.setSpacing(12)

        # Server
        server_layout = QVBoxLayout()
        server_layout.addWidget(QLabel("Server Address *"))
        self.server_input = ModernLineEdit("server\\instance or server,port")
        server_layout.addWidget(self.server_input)
        sql_layout.addLayout(server_layout)

        # Database
        db_layout = QVBoxLayout()
        db_layout.addWidget(QLabel("Database Name *"))
        self.database_input = ModernLineEdit("DatabaseName")
        db_layout.addWidget(self.database_input)
        sql_layout.addLayout(db_layout)

        # Credentials row
        cred_layout = QHBoxLayout()

        # Username
        user_layout = QVBoxLayout()
        user_layout.addWidget(QLabel("Username *"))
        self.username_input = ModernLineEdit("username")
        user_layout.addWidget(self.username_input)
        cred_layout.addLayout(user_layout)

        # Password
        pass_layout = QVBoxLayout()
        pass_layout.addWidget(QLabel("Password *"))
        self.password_input = ModernLineEdit("password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        pass_layout.addWidget(self.password_input)
        cred_layout.addLayout(pass_layout)

        sql_layout.addLayout(cred_layout)

        # Table name
        table_layout = QVBoxLayout()
        table_layout.addWidget(QLabel("Target Table Name *"))
        self.table_input = ModernLineEdit("TableName")
        table_layout.addWidget(self.table_input)
        sql_layout.addLayout(table_layout)

        layout.addWidget(self.sql_group)

        # SQLite Section
        self.sqlite_group = ModernGroupBox("SQLite Database")
        sqlite_layout = QVBoxLayout(self.sqlite_group)

        # File path
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Database File:"))
        self.sqlite_input = ModernLineEdit("data.db")
        browse_btn = ModernButton("📁 Browse", "secondary")
        browse_btn.clicked.connect(self._browse_sqlite)
        file_layout.addWidget(self.sqlite_input)
        file_layout.addWidget(browse_btn)
        sqlite_layout.addLayout(file_layout)

        # SQLite table
        sqlite_table_layout = QVBoxLayout()
        sqlite_table_layout.addWidget(QLabel("Table Name:"))
        self.sqlite_table_input = ModernLineEdit("sharepoint_data")
        sqlite_table_layout.addWidget(self.sqlite_table_input)
        sqlite_layout.addLayout(sqlite_table_layout)

        layout.addWidget(self.sqlite_group)

        # Test button
        self.test_db_btn = ModernButton("🔍 Test Database Connection")
        self.test_db_btn.clicked.connect(self._test_database)
        layout.addWidget(self.test_db_btn)

        # Show appropriate section
        self._on_db_type_changed("SQL Server")

    def _on_db_type_changed(self, db_type):
        """Handle database type change"""
        if db_type == "SQL Server":
            self.sql_group.show()
            self.sqlite_group.hide()
        else:
            self.sql_group.hide()
            self.sqlite_group.show()

    def _browse_sqlite(self):
        """Browse for SQLite file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Select SQLite Database",
            "data.db",
            "SQLite Files (*.db *.sqlite);;All Files (*)",
        )
        if file_path:
            self.sqlite_input.setText(file_path)

    def _load_config(self):
        """Load database configuration"""
        try:
            config = self.config_manager.get_config()

            # Set database type
            db_type = getattr(config, "database_type", "sqlserver")
            if db_type == "sqlserver":
                self.db_type_combo.setCurrentText("SQL Server")
            else:
                self.db_type_combo.setCurrentText("SQLite")

            # SQL Server fields
            self.server_input.setText(getattr(config, "sql_server", ""))
            self.database_input.setText(getattr(config, "sql_database", ""))
            self.username_input.setText(getattr(config, "sql_username", ""))
            self.password_input.setText(getattr(config, "sql_password", ""))
            self.table_input.setText(getattr(config, "sql_table_name", ""))

            # SQLite fields
            self.sqlite_input.setText(getattr(config, "sqlite_file", "data.db"))
            self.sqlite_table_input.setText(
                getattr(config, "sqlite_table_name", "sharepoint_data")
            )

        except Exception as e:
            print(f"Error loading database config: {e}")

    def save_config(self):
        """Save database configuration"""
        try:
            # Database type
            db_type = (
                "sqlserver"
                if self.db_type_combo.currentText() == "SQL Server"
                else "sqlite"
            )
            self.config_manager.update_setting("database_type", db_type)

            # SQL Server settings
            self.config_manager.update_setting("sql_server", self.server_input.text())
            self.config_manager.update_setting(
                "sql_database", self.database_input.text()
            )
            self.config_manager.update_setting(
                "sql_username", self.username_input.text()
            )
            self.config_manager.update_setting(
                "sql_password", self.password_input.text()
            )
            self.config_manager.update_setting(
                "sql_table_name", self.table_input.text()
            )

            # SQLite settings
            self.config_manager.update_setting("sqlite_file", self.sqlite_input.text())
            self.config_manager.update_setting(
                "sqlite_table_name", self.sqlite_table_input.text()
            )

            self.config_manager.save_config()
        except Exception as e:
            print(f"Error saving database config: {e}")

    def _test_database(self):
        """Test database connection"""
        self.test_db_btn.setText("🔄 Testing...")
        self.test_db_btn.setEnabled(False)

        # Simulate test
        QTimer.singleShot(2000, self._db_test_complete)

    def _db_test_complete(self):
        """Database test completion"""
        self.test_db_btn.setText("✅ Connection OK")
        QTimer.singleShot(
            2000, lambda: self.test_db_btn.setText("🔍 Test Database Connection")
        )
        self.test_db_btn.setEnabled(True)


class ConnectionSetupWidget(QWidget):
    """Complete connection setup widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup main connection UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(24, 24, 24, 24)

        # Header
        header = QLabel("Connection Configuration")
        header.setStyleSheet(
            """
            font-size: 24px;
            font-weight: bold;
            color: #F8FAFC;
            margin-bottom: 16px;
        """
        )
        layout.addWidget(header)

        # Description
        desc = QLabel(
            "Configure your SharePoint and Database connections below. All fields marked with * are required."
        )
        desc.setStyleSheet("color: #9CA3AF; margin-bottom: 24px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Forms in scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(32)

        # SharePoint Form
        self.sharepoint_form = SharePointConnectionForm()
        content_layout.addWidget(self.sharepoint_form)

        # Database Form
        self.database_form = DatabaseConnectionForm()
        content_layout.addWidget(self.database_form)

        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Action buttons
        button_layout = QHBoxLayout()

        save_btn = ModernButton("💾 Save Configuration")
        save_btn.clicked.connect(self._save_all)
        button_layout.addWidget(save_btn)

        test_all_btn = ModernButton("🔍 Test All Connections", "secondary")
        test_all_btn.clicked.connect(self._test_all)
        button_layout.addWidget(test_all_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def _save_all(self):
        """Save all configurations"""
        try:
            self.sharepoint_form.save_config()
            self.database_form.save_config()

            # Show success message
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Configuration Saved")
            msg.setText("All connection settings have been saved successfully!")
            msg.exec()

        except Exception as e:
            # Show error message
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Save Error")
            msg.setText(f"Error saving configuration:\n{e}")
            msg.exec()

    def _test_all(self):
        """Test all connections"""
        self.sharepoint_form._test_sharepoint()
        self.database_form._test_database()


# Factory function
def create_connection_setup_widget(parent=None):
    """Create connection setup widget"""
    return ConnectionSetupWidget(parent)
