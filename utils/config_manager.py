import json
from pathlib import Path
from dataclasses import dataclass, asdict
from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity
import logging

logger = logging.getLogger(__name__)


@dataclass
class AppConfig:
    """แก้แล้ว: field mapping ครบถ้วน รองรับทั้ง SharePoint และ SQLite"""

    # SharePoint Configuration
    sharepoint_url: str = ""
    sharepoint_site: str = ""
    sharepoint_list: str = ""
    sharepoint_client_id: str = ""
    sharepoint_client_secret: str = ""
    tenant_id: str = ""
    use_graph_api: bool = False

    # Database Configuration
    database_type: str = "sqlserver"
    db_type: str = "SQL Server"

    # SQL Server Configuration
    db_host: str = ""
    db_port: int = 1433
    db_name: str = ""
    db_table: str = ""
    db_username: str = ""
    db_password: str = ""

    # Legacy SQL Server fields (backward compatibility)
    sql_server: str = ""
    sql_database: str = ""
    sql_username: str = ""
    sql_password: str = ""
    sql_table_name: str = ""
    sql_create_table: bool = True
    sql_truncate_before: bool = False

    # SQLite Configuration
    sqlite_file: str = "data.db"
    sqlite_table_name: str = "sharepoint_data"
    sqlite_create_table: bool = True

    # Sync Configuration
    sync_interval: int = 60
    sync_mode: str = "full"
    auto_sync_enabled: bool = False
    batch_size: int = 1000

    # Advanced Settings
    connection_timeout: int = 30
    max_retries: int = 3
    log_level: str = "INFO"
    enable_parallel_processing: bool = False
    enable_success_notifications: bool = True
    enable_error_notifications: bool = True

    def __post_init__(self):
        """แก้แล้ว: sync field mappings หลัง initialization"""
        # Sync SharePoint fields
        if not self.sharepoint_url and self.sharepoint_site:
            self.sharepoint_url = self.sharepoint_site
        elif not self.sharepoint_site and self.sharepoint_url:
            self.sharepoint_site = self.sharepoint_url

        # Sync SQL Server fields (new <-> legacy)
        if self.db_host and not self.sql_server:
            self.sql_server = self.db_host
        elif self.sql_server and not self.db_host:
            self.db_host = self.sql_server

        if self.db_name and not self.sql_database:
            self.sql_database = self.db_name
        elif self.sql_database and not self.db_name:
            self.db_name = self.sql_database

        if self.db_username and not self.sql_username:
            self.sql_username = self.db_username
        elif self.sql_username and not self.db_username:
            self.db_username = self.sql_username

        if self.db_password and not self.sql_password:
            self.sql_password = self.db_password
        elif self.sql_password and not self.db_password:
            self.db_password = self.sql_password

        if self.db_table and not self.sql_table_name:
            self.sql_table_name = self.db_table
        elif self.sql_table_name and not self.db_table:
            self.db_table = self.sql_table_name

        # Sync database type fields
        if self.db_type == "SQLite":
            self.database_type = "sqlite"
        elif self.db_type == "SQL Server":
            self.database_type = "sqlserver"

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        """Create from dictionary with field validation"""
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)

    def validate(self):
        """Validate configuration"""
        errors = []

        # SharePoint validation
        if self.sharepoint_url and not self.sharepoint_url.startswith("https://"):
            errors.append("SharePoint URL must start with https://")

        # Database validation
        if self.database_type == "sqlserver" or self.db_type == "SQL Server":
            if not (self.db_host or self.sql_server):
                errors.append("Database host is required")
            if not (self.db_name or self.sql_database):
                errors.append("Database name is required")
        elif self.database_type == "sqlite" or self.db_type == "SQLite":
            if not self.sqlite_file:
                errors.append("SQLite file path is required")

        # Sync validation
        if self.sync_interval < 1:
            errors.append("Sync interval must be at least 1 minute")
        if self.batch_size < 1:
            errors.append("Batch size must be positive")

        return errors


class ConfigManager:
    """แก้แล้ว: field mapping และ error handling"""

    def __init__(self, config_file="config.json"):
        self.config_file = Path(config_file)
        self.config = None
        self._load_config()

    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.MEDIUM)
    def _load_config(self):
        """Load configuration with error handling"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.config = AppConfig.from_dict(data)
                logger.info("Configuration loaded successfully")
            else:
                self.config = AppConfig()
                logger.info("Created default configuration")
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
            self.config = AppConfig()

    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.MEDIUM)
    def save_config(self, config: AppConfig):
        """Save configuration with validation"""
        # Validate before saving
        errors = config.validate()
        if errors:
            logger.warning(f"Config validation warnings: {errors}")

        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            self.config = config
            logger.info("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Failed to save config: {str(e)}")
            raise

    def get_config(self) -> AppConfig:
        """Get current configuration"""
        if self.config is None:
            self._load_config()
        return self.config

    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.LOW)
    def reset_config(self):
        """Reset to default configuration"""
        self.config = AppConfig()
        self.save_config(self.config)
        logger.info("Configuration reset to defaults")

    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.LOW)
    def backup_config(self, backup_path: str = None):
        """Create backup of current configuration"""
        if not backup_path:
            backup_path = f"{self.config_file}.backup"

        try:
            if self.config_file.exists():
                import shutil

                shutil.copy2(self.config_file, backup_path)
                logger.info(f"Config backed up to {backup_path}")
                return True
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            return False

    def get_connection_string(self):
        """Generate connection string สำหรับ database"""
        db_type = self.config.database_type or self.config.db_type

        if db_type and db_type.lower() == "sqlite":
            return f"sqlite:///{Path(self.config.sqlite_file).absolute()}"
        else:  # SQL Server
            server = self.config.db_host or self.config.sql_server
            database = self.config.db_name or self.config.sql_database
            username = self.config.db_username or self.config.sql_username
            password = self.config.db_password or self.config.sql_password

            return (
                f"mssql+pyodbc://{username}:{password}@{server}/"
                f"{database}?driver=ODBC+Driver+17+for+SQL+Server&"
                f"timeout={self.config.connection_timeout}"
            )

    def is_sharepoint_configured(self):
        """ตรวจสอบว่า SharePoint ถูก config แล้วหรือไม่"""
        return all(
            [
                self.config.sharepoint_url or self.config.sharepoint_site,
                self.config.sharepoint_client_id,
                self.config.sharepoint_client_secret,
                self.config.tenant_id,
            ]
        )

    def is_database_configured(self):
        """ตรวจสอบว่า Database ถูก config แล้วหรือไม่"""
        db_type = self.config.database_type or self.config.db_type

        if db_type and db_type.lower() == "sqlite":
            return bool(self.config.sqlite_file)
        else:  # SQL Server
            return all(
                [
                    self.config.db_host or self.config.sql_server,
                    self.config.db_name or self.config.sql_database,
                    self.config.db_username or self.config.sql_username,
                ]
            )

    def get_database_type(self):
        """ดึงประเภทฐานข้อมูลที่ใช้"""
        db_type = self.config.database_type or self.config.db_type
        if db_type and db_type.lower() in ["sqlite"]:
            return "sqlite"
        else:
            return "sqlserver"

    def update_field(self, field_name: str, value):
        """อัปเดตฟิลด์เดียว"""
        if hasattr(self.config, field_name):
            setattr(self.config, field_name, value)
            self.save_config(self.config)
            return True
        return False
