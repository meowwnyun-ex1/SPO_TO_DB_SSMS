import json
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class AppConfig:
    """Application configuration data class"""

    # SharePoint Configuration
    tenant_id: str = ""
    client_id: str = ""
    client_secret: str = ""
    site_url: str = ""
    list_name: str = ""
    use_graph_api: bool = False

    # Database Configuration
    database_type: str = "sqlserver"  # or "sqlite"

    # SQL Server Configuration
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
    sqlite_backup: bool = False

    # Sync Configuration
    sync_interval: int = 3600  # seconds
    sync_mode: str = "full"  # or "incremental"
    auto_sync_enabled: bool = False
    batch_size: int = 1000
    parallel_processing: bool = False

    # Notification Settings
    email_notifications: bool = False
    success_notifications: bool = True
    error_notifications: bool = True

    # Advanced Settings
    connection_timeout: int = 30
    max_retries: int = 3
    log_level: str = "INFO"

    # UI Preferences
    theme: str = "dark"
    language: str = "th"
    window_geometry: dict = field(
        default_factory=lambda: {"width": 1400, "height": 900}
    )

    def to_dict(self):
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        # Filter out unknown fields
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)


class ConfigManager:
    """Configuration manager class"""

    def __init__(self, config_file="config.json"):
        self.config_file = Path(config_file)
        self.config = None
        self._load_config()

    def _load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Handle legacy config format
                if self._is_legacy_format(data):
                    data = self._convert_legacy_config(data)

                self.config = AppConfig.from_dict(data)
                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                self.config = AppConfig()
                logger.info("Created default configuration")

        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            self.config = AppConfig()

    def _is_legacy_format(self, data):
        """Check if config is in legacy format"""
        return "sharepoint" in data or "database" in data

    def _convert_legacy_config(self, legacy_data):
        """Convert legacy config format to new format"""
        converted = {}

        # SharePoint section
        if "sharepoint" in legacy_data:
            sp = legacy_data["sharepoint"]
            converted.update(
                {
                    "tenant_id": sp.get("tenant_id", ""),
                    "client_id": sp.get("client_id", ""),
                    "client_secret": sp.get("client_secret", ""),
                    "site_url": sp.get("site", ""),
                    "list_name": sp.get("list", ""),
                    "use_graph_api": sp.get("use_graph_api", False),
                }
            )

        # Database section
        if "database" in legacy_data:
            db = legacy_data["database"]
            converted["database_type"] = db.get("type", "sqlserver")

            if "sqlserver" in db:
                sql = db["sqlserver"]
                converted.update(
                    {
                        "sql_server": sql.get("server", ""),
                        "sql_database": sql.get("database", ""),
                        "sql_username": sql.get("username", ""),
                        "sql_password": sql.get("password", ""),
                        "sql_table_name": sql.get("table_name", ""),
                        "sql_create_table": sql.get("create_table", True),
                    }
                )

            if "sqlite" in db:
                sqlite = db["sqlite"]
                converted.update(
                    {
                        "sqlite_file": sqlite.get("file", "data.db"),
                        "sqlite_table_name": sqlite.get("table_name", "data"),
                        "sqlite_create_table": sqlite.get("create_table", True),
                    }
                )

        # Sync section
        if "sync" in legacy_data:
            sync = legacy_data["sync"]
            converted.update(
                {
                    "sync_interval": sync.get("interval", 3600),
                    "sync_mode": sync.get("mode", "full"),
                }
            )

        return converted

    def save_config(self, config: AppConfig):
        """Save configuration to file"""
        try:
            # Create directory if it doesn't exist
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)

            self.config = config
            logger.info(f"Configuration saved to {self.config_file}")

        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
            raise

    def get_config(self) -> AppConfig:
        """Get current configuration"""
        return self.config

    def update_config(self, **kwargs):
        """Update specific configuration values"""
        if self.config is None:
            self.config = AppConfig()

        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                logger.warning(f"Unknown config key: {key}")

        self.save_config(self.config)

    def reset_config(self):
        """Reset configuration to defaults"""
        self.config = AppConfig()
        self.save_config(self.config)
        logger.info("Configuration reset to defaults")

    def backup_config(self, backup_path: Optional[str] = None):
        """Create a backup of current configuration"""
        if backup_path is None:
            backup_path = f"{self.config_file}.backup"

        try:
            if self.config_file.exists():
                import shutil

                shutil.copy2(self.config_file, backup_path)
                logger.info(f"Configuration backed up to {backup_path}")
                return True
        except Exception as e:
            logger.error(f"Failed to backup configuration: {str(e)}")
            return False

    def restore_config(self, backup_path: str):
        """Restore configuration from backup"""
        try:
            backup_file = Path(backup_path)
            if backup_file.exists():
                import shutil

                shutil.copy2(backup_file, self.config_file)
                self._load_config()
                logger.info(f"Configuration restored from {backup_path}")
                return True
            else:
                logger.error(f"Backup file not found: {backup_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to restore configuration: {str(e)}")
            return False

    def validate_config(self) -> dict:
        """Validate current configuration"""
        if self.config is None:
            return {"valid": False, "errors": ["No configuration loaded"]}

        errors = []
        warnings = []

        # SharePoint validation
        if not self.config.tenant_id.strip():
            errors.append("Tenant ID is required")
        if not self.config.client_id.strip():
            errors.append("Client ID is required")
        if not self.config.client_secret.strip():
            errors.append("Client Secret is required")
        if not self.config.site_url.strip():
            errors.append("Site URL is required")

        # Database validation
        if self.config.database_type == "sqlserver":
            if not self.config.sql_server.strip():
                errors.append("SQL Server is required")
            if not self.config.sql_database.strip():
                errors.append("SQL Database is required")
            if not self.config.sql_username.strip():
                warnings.append("SQL Username is empty")
        elif self.config.database_type == "sqlite":
            if not self.config.sqlite_file.strip():
                errors.append("SQLite file path is required")

        # Sync validation
        if self.config.sync_interval < 60:
            warnings.append("Sync interval is very short (< 1 minute)")
        if self.config.batch_size < 1:
            errors.append("Batch size must be greater than 0")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def export_config(self, export_path: str, include_secrets: bool = False):
        """Export configuration to another file"""
        try:
            config_dict = self.config.to_dict()

            if not include_secrets:
                # Remove sensitive information
                config_dict["client_secret"] = "***"
                config_dict["sql_password"] = "***"

            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"Configuration exported to {export_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export configuration: {str(e)}")
            return False

    def import_config(self, import_path: str):
        """Import configuration from another file"""
        try:
            with open(import_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle legacy format
            if self._is_legacy_format(data):
                data = self._convert_legacy_config(data)

            imported_config = AppConfig.from_dict(data)
            self.save_config(imported_config)
            logger.info(f"Configuration imported from {import_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to import configuration: {str(e)}")
            return False
