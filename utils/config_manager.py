import json
from pathlib import Path
from dataclasses import dataclass, asdict
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
    database_type: str = "sqlserver"

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

    # Sync Configuration
    sync_interval: int = 3600
    sync_mode: str = "full"
    auto_sync_enabled: bool = False
    batch_size: int = 1000

    # Advanced Settings
    connection_timeout: int = 30
    max_retries: int = 3
    log_level: str = "INFO"
    parallel_processing: bool = False
    success_notifications: bool = True
    error_notifications: bool = True

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)


class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = Path(config_file)
        self.config = None
        self._load_config()

    def _load_config(self):
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.config = AppConfig.from_dict(data)
            else:
                self.config = AppConfig()
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            self.config = AppConfig()

    def save_config(self, config: AppConfig):
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            self.config = config
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
            raise

    def get_config(self) -> AppConfig:
        return self.config
