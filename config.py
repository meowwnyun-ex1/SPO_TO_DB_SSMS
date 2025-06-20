# config.py - Enhanced version
import os
import json
from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

CONFIG_FILE = "config.json"


@dataclass
class Config:
    # General Application Settings
    app_name: str = "DENSO Neural Matrix"
    app_version: str = "1.0.0"
    connection_timeout: int = 30  # Default timeout for network operations in seconds
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # UI Settings
    background_image_path: str = (
        "assets/images/bg_denso_matrix.jpg"  # Updated default path
    )
    enable_background_audio: bool = False
    background_audio_path: str = "assets/audio/bg_ambient.mp3"  # Updated default path
    background_audio_volume: float = 0.1  # 0.0 to 1.0

    # SharePoint Configuration
    sharepoint_site: str = os.getenv(
        "SHAREPOINT_SITE", "https://yourdomain.sharepoint.com/sites/YourSite"
    )
    sharepoint_list: str = os.getenv("SHAREPOINT_LIST", "your_list_name")
    sharepoint_client_id: str = os.getenv("SHAREPOINT_CLIENT_ID", "your_client_id")
    sharepoint_client_secret: str = os.getenv("SHAREPOINT_CLIENT_SECRET", "your_secret")
    tenant_id: str = os.getenv("TENANT_ID", "your_tenant")
    use_graph_api: bool = False

    # Database Configuration
    database_type: str = "sqlserver"  # or "sqlite"

    # SQL Server Configuration
    sql_server: str = os.getenv("SQL_SERVER", "your_sql_server.database.windows.net")
    sql_database: str = os.getenv("SQL_DATABASE", "your_db")
    sql_username: str = os.getenv("SQL_USERNAME", "your_user")
    sql_password: str = os.getenv("SQL_PASSWORD", "your_password")
    sql_table_name: str = os.getenv("SQL_TABLE_NAME", "your_table")
    sql_create_table: bool = True

    # SQLite Configuration
    sqlite_file: str = "data.db"
    sqlite_table_name: str = "sharepoint_data"
    sqlite_create_table: bool = True

    # Sync Configuration
    sync_interval: int = 600  # seconds (e.g., 600 for 10 minutes)
    sync_mode: str = "full"  # 'full' or 'incremental'
    auto_sync_enabled: bool = False
    auto_sync_direction: str = "spo_to_sql"  # 'spo_to_sql' or 'sql_to_spo'
    full_sync_on_startup: bool = False
    incremental_sync_field: str = "Modified"  # Field to check for incremental updates

    # Data Mapping (JSON structure for SharePoint to SQL and SQL to SharePoint)
    sharepoint_to_sql_mapping: dict = json.loads(
        os.getenv("SHAREPOINT_TO_SQL_MAPPING", "{}")
    )
    sql_to_sharepoint_mapping: dict = json.loads(
        os.getenv("SQL_TO_SHAREPOINT_MAPPING", "{}")
    )

    # Cache Management
    auto_cache_cleanup_enabled: bool = False
    cache_cleanup_interval_hours: int = 24
    cache_cleanup_types: list = field(
        default_factory=lambda: ["python_cache", "log_files", "temp_files"]
    )

    # Error Handling & Logging
    enable_error_notifications: bool = True
    error_log_retention_days: int = 7


def load_config_from_file(config_path: Path) -> dict:
    """Loads configuration from a JSON file."""
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding config JSON from {config_path}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {e}")
            return {}
    return {}


def save_config_to_file(config_data: dict, config_path: Path):
    """Saves configuration to a JSON file."""
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Configuration saved to {config_path}")
    except Exception as e:
        logger.error(f"Error saving config to {config_path}: {e}")


def initialize_config(config_file: str = CONFIG_FILE) -> Config:
    """
    Initializes the Config object, loading from config.json if it exists,
    otherwise using defaults.
    """
    config_path = Path(config_file)
    file_config = load_config_from_file(config_path)

    # Create an instance with default values from dataclass
    config = Config()

    # Override defaults with values from config file
    for key, value in file_config.items():
        if hasattr(config, key):
            # Handle nested structures if necessary, though direct assignment is fine for now
            # For dicts like mappings, ensure they are loaded correctly
            if isinstance(getattr(config, key), dict) and isinstance(value, dict):
                setattr(config, key, {**getattr(config, key), **value})
            else:
                setattr(config, key, value)
        else:
            logger.warning(f"Unknown configuration key in {config_file}: {key}")

    # Ensure environment variables override file settings if they are set
    # This loop is technically redundant if load_dotenv is called early and
    # default values in Config dataclass use os.getenv, but kept for clarity
    # or if there's a desire to re-evaluate env vars after file load.
    # For this pattern, it's better to let dataclass defaults handle env vars directly.
    # We will remove explicit os.getenv calls here, assuming dataclass handles it.

    return config


# Global instance of configuration
# This ensures that all modules import the same config object
# It's initialized once when the module is first imported
_current_config = initialize_config()


class ConfigManager:
    """
    Singleton-like class to manage application configuration,
    providing access to settings and saving capabilities.
    """

    _config: Optional[Config] = None

    def __new__(cls, *args, **kwargs):
        if cls._config is None:
            cls._config = _current_config  # Use the pre-initialized config
            logger.info("ConfigManager initialized and loaded configuration.")
        return super().__new__(cls)

    def get_config(self) -> Config:
        """Returns the current configuration object."""
        return ConfigManager._config

    def save_config(self):
        """Saves the current configuration to the JSON file."""
        config_data = asdict(ConfigManager._config)
        # Remove fields that are not meant for config.json or are dynamically set
        config_data.pop("app_name", None)
        config_data.pop("app_version", None)
        config_data.pop("log_level", None)

        # Handle specific cases where we might want to flatten or rename for saving
        # Example: if you had 'sql_config' dataclass, you'd merge its dict here
        if (
            "sqlserver" in config_data
        ):  # Example: This block assumes 'sqlserver' was a nested dict in old config
            sql_config = config_data.pop("sqlserver")
            config_data.update(sql_config)

        # Ensure database_type is correctly represented if using old db_type field
        if hasattr(ConfigManager._config, "db_type") and not config_data.get(
            "database_type"
        ):
            config_data["database_type"] = ConfigManager._config.db_type.lower()

        save_config_to_file(config_data, Path(CONFIG_FILE))

    def update_setting(self, key_path: str, value: Any):
        """
        Updates a specific setting in the configuration and saves it.
        Key path can be nested, e.g., "sharepoint.url" or "auto_sync.enabled".
        """
        parts = key_path.split(".")
        current = ConfigManager._config
        for i, part in enumerate(parts):
            if hasattr(current, part):
                if i == len(parts) - 1:
                    setattr(current, part, value)
                    logger.debug(f"Config updated: {key_path} = {value}")
                else:
                    current = getattr(current, part)
            else:
                logger.warning(
                    f"Config key '{key_path}' not found at '{part}'. Update ignored."
                )
                return
        self.save_config()

    def get_setting(self, *key_path) -> Any:
        """
        Retrieves a setting value from the configuration.
        Accepts multiple arguments for nested keys, e.g., get_setting("auto_sync", "enabled").
        """
        current = ConfigManager._config
        for part in key_path:
            if hasattr(current, part):
                current = getattr(current, part)
            else:
                logger.warning(
                    f"Config setting path {'/'.join(key_path)} not found at '{part}'. Returning None."
                )
                return None
        return current

    def reload_config(self):
        """Forces a reload of the configuration from the file."""
        ConfigManager._config = self._load_config()
        logger.info("Configuration reloaded from file.")

    def _load_config(self) -> Config:
        """Internal method to load configuration, used by reload_config."""
        return initialize_config(CONFIG_FILE)
