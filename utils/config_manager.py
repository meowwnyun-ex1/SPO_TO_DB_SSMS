# utils/config_manager.py - Fixed Configuration Management with Proper Singleton
import os
import json
from dataclasses import dataclass, field, asdict
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from PyQt6.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Define the default configuration file path
CONFIG_FILE = "config.json"
DEFAULT_CONFIG_DIR = Path("config")
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / CONFIG_FILE


@dataclass
class Config:
    """
    Unified configuration data class.
    Removes conflicts between old and new field names.
    """

    # General Application Settings
    app_name: str = "DENSO Neural Matrix"
    app_version: str = "1.0.0"
    connection_timeout: int = 30
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    max_retries: int = 3

    # UI Settings
    background_image_path: str = "resources/images/bg_denso_matrix.jpg"
    enable_background_audio: bool = False
    background_audio_path: str = "resources/audio/bg_ambient.mp3"
    background_audio_volume: float = 0.1

    # SharePoint Configuration (unified fields)
    sharepoint_site: str = os.getenv("SHAREPOINT_SITE", "")
    sharepoint_list: str = os.getenv("SHAREPOINT_LIST", "")
    sharepoint_client_id: str = os.getenv("SHAREPOINT_CLIENT_ID", "")
    sharepoint_client_secret: str = os.getenv("SHAREPOINT_CLIENT_SECRET", "")
    tenant_id: str = os.getenv("TENANT_ID", "")
    use_graph_api: bool = False

    # Database Configuration (unified)
    database_type: str = "sqlserver"  # "sqlserver" or "sqlite"

    # SQL Server Configuration
    sql_server: str = os.getenv("SQL_SERVER", "")
    sql_database: str = os.getenv("SQL_DATABASE", "")
    sql_username: str = os.getenv("SQL_USERNAME", "")
    sql_password: str = os.getenv("SQL_PASSWORD", "")
    sql_table_name: str = os.getenv("SQL_TABLE_NAME", "")
    sql_create_table: bool = True
    sql_truncate_before: bool = True

    # SQLite Configuration
    sqlite_file: str = os.getenv("SQLITE_FILE", "data.db")
    sqlite_table_name: str = os.getenv("SQLITE_TABLE_NAME", "sharepoint_data")
    sqlite_create_table: bool = True

    # Synchronization Settings
    sync_interval: int = 600  # seconds
    sync_mode: str = "full"
    auto_sync_enabled: bool = False
    auto_sync_direction: str = "spo_to_sql"
    last_sync_timestamp: Optional[str] = None
    last_sync_status: str = "never"

    # Field Mappings
    sharepoint_to_sql_mapping: Dict[str, str] = field(default_factory=dict)
    sql_to_sharepoint_mapping: Dict[str, str] = field(default_factory=dict)
    excel_import_mapping: Dict[str, str] = field(default_factory=dict)

    # Performance Settings
    batch_size: int = 1000
    enable_parallel_processing: bool = False

    # Notification Settings
    enable_success_notifications: bool = True
    enable_error_notifications: bool = True

    # Cache Management
    auto_cache_cleanup_enabled: bool = False
    cache_cleanup_interval_hours: int = 24

    def __post_init__(self):
        """Post-initialization to handle legacy field mapping"""
        # Handle sharepoint_url legacy field
        if hasattr(self, "sharepoint_url") and not self.sharepoint_site:
            self.sharepoint_site = getattr(self, "sharepoint_url", "")

        # Handle db_type legacy field
        if hasattr(self, "db_type"):
            if getattr(self, "db_type", "").lower() == "sql server":
                self.database_type = "sqlserver"
            elif getattr(self, "db_type", "").lower() == "sqlite":
                self.database_type = "sqlite"

    @property
    def sharepoint_url(self) -> str:
        """Backward compatibility property"""
        return self.sharepoint_site

    @property
    def db_type(self) -> str:
        """Backward compatibility property"""
        return "SQL Server" if self.database_type == "sqlserver" else "SQLite"


class ConfigManager(QObject):
    """
    Fixed configuration manager with proper singleton pattern.
    """

    # Signals
    config_updated = pyqtSignal()

    _instance = None
    _config = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            # Initialize QObject properly
            QObject.__init__(cls._instance)
        return cls._instance

    def __init__(self):
        # Only initialize once for singleton
        if not ConfigManager._initialized:
            ConfigManager._initialized = True

            try:
                # Load config on first initialization
                ConfigManager._config = self._load_config()
                logger.debug("ConfigManager initialized as singleton.")
            except Exception as e:
                logger.error(f"Error initializing ConfigManager: {e}")
                # Create default config if loading fails
                ConfigManager._config = Config()

    def _load_config(self) -> Config:
        """Load configuration from file and environment variables"""
        config_data = {}

        # Ensure config directory exists
        DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        # Load from config.json if exists
        if DEFAULT_CONFIG_PATH.exists():
            try:
                with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                logger.info(f"Loaded configuration from {DEFAULT_CONFIG_PATH}")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading config.json: {e}. Using defaults.")
                config_data = {}
        else:
            logger.warning(
                f"Config file not found. Creating default at {DEFAULT_CONFIG_PATH}"
            )
            self._save_default_config()

        # Create Config instance with defaults
        config = Config()

        # Apply config.json values safely
        for key, value in config_data.items():
            if hasattr(config, key):
                current_value = getattr(config, key)
                try:
                    if isinstance(current_value, dict) and isinstance(value, dict):
                        getattr(config, key).update(value)
                    elif isinstance(current_value, bool) and isinstance(value, str):
                        setattr(
                            config, key, value.lower() in ("true", "1", "yes", "on")
                        )
                    elif value is not None:
                        # Type-safe conversion
                        if isinstance(current_value, (int, float)) and isinstance(
                            value, str
                        ):
                            try:
                                converted_value = type(current_value)(value)
                                setattr(config, key, converted_value)
                            except ValueError:
                                logger.warning(
                                    f"Cannot convert '{value}' to {type(current_value)} for key '{key}'"
                                )
                        else:
                            setattr(config, key, value)
                except Exception as e:
                    logger.warning(f"Failed to set config key '{key}': {e}")
            else:
                logger.warning(f"Unknown config key '{key}' in config.json")

        # Environment variables override file settings
        self._apply_env_overrides(config)

        logger.info("Configuration loaded successfully")
        return config

    def _apply_env_overrides(self, config: Config):
        """Apply environment variable overrides"""
        env_mappings = {
            "SHAREPOINT_SITE": "sharepoint_site",
            "SHAREPOINT_LIST": "sharepoint_list",
            "SHAREPOINT_CLIENT_ID": "sharepoint_client_id",
            "SHAREPOINT_CLIENT_SECRET": "sharepoint_client_secret",
            "TENANT_ID": "tenant_id",
            "SQL_SERVER": "sql_server",
            "SQL_DATABASE": "sql_database",
            "SQL_USERNAME": "sql_username",
            "SQL_PASSWORD": "sql_password",
            "SQL_TABLE_NAME": "sql_table_name",
            "LOG_LEVEL": "log_level",
        }

        for env_var, config_attr in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                try:
                    current_type = type(getattr(config, config_attr))
                    if current_type == bool:
                        setattr(
                            config,
                            config_attr,
                            env_value.lower() in ("true", "1", "yes"),
                        )
                    elif current_type == int:
                        setattr(config, config_attr, int(env_value))
                    elif current_type == float:
                        setattr(config, config_attr, float(env_value))
                    else:
                        setattr(config, config_attr, env_value)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to convert env var {env_var}: {e}")

    def _save_default_config(self):
        """Save default configuration to file"""
        try:
            default_config = asdict(Config())
            with open(DEFAULT_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            logger.info(f"Default configuration saved to {DEFAULT_CONFIG_PATH}")
        except IOError as e:
            logger.error(f"Failed to save default config: {e}")

    def get_config(self) -> Config:
        """Get current configuration instance"""
        if ConfigManager._config is None:
            ConfigManager._config = Config()
        return ConfigManager._config

    def save_config(self):
        """Save current configuration to file"""
        if ConfigManager._config:
            try:
                # Convert to dict and save
                config_dict = asdict(ConfigManager._config)

                # Read existing config to preserve unknown keys
                existing_data = {}
                if DEFAULT_CONFIG_PATH.exists():
                    try:
                        with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
                            existing_data = json.load(f)
                    except (json.JSONDecodeError, IOError):
                        pass

                # Update with current config
                existing_data.update(config_dict)

                with open(DEFAULT_CONFIG_PATH, "w", encoding="utf-8") as f:
                    json.dump(existing_data, f, indent=2, ensure_ascii=False)

                logger.info("Configuration saved successfully")
                self.config_updated.emit()  # Emit signal

            except Exception as e:
                logger.error(f"Failed to save configuration: {e}")

    def update_setting(self, key_path: str, value: Any):
        """Update a configuration setting"""
        if not ConfigManager._config:
            logger.error("No config instance to update")
            return

        parts = key_path.split(".")
        current = ConfigManager._config

        # Navigate to the setting
        for i, part in enumerate(parts[:-1]):
            if hasattr(current, part):
                current = getattr(current, part)
            else:
                logger.warning(f"Config path '{key_path}' not found at '{part}'")
                return

        # Set the final value
        final_key = parts[-1]
        if hasattr(current, final_key):
            try:
                # Type conversion
                current_value = getattr(current, final_key)
                target_type = type(current_value)

                if target_type == bool and isinstance(value, str):
                    converted_value = value.lower() in ("true", "1", "yes", "on")
                elif target_type in (int, float, str) and value is not None:
                    converted_value = target_type(value)
                else:
                    converted_value = value

                setattr(current, final_key, converted_value)
                logger.debug(f"Config updated: {key_path} = {converted_value}")
                self.save_config()

            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to convert value for '{key_path}': {e}")
        else:
            logger.warning(f"Config key '{final_key}' not found")

    def get_setting(self, *key_path) -> Any:
        """Get a configuration setting value"""
        if not ConfigManager._config:
            return None

        current = ConfigManager._config
        for part in key_path:
            if hasattr(current, part):
                current = getattr(current, part)
            else:
                logger.warning(
                    f"Config path {'/'.join(key_path)} not found at '{part}'"
                )
                return None
        return current

    def reload_config(self):
        """Reload configuration from file"""
        try:
            ConfigManager._config = self._load_config()
            self.config_updated.emit()  # Emit signal
            logger.info("Configuration reloaded")
        except Exception as e:
            logger.error(f"Failed to reload config: {e}")


# Create singleton instance functions with better error handling
_config_manager_instance = None


def get_config_manager() -> ConfigManager:
    """Get singleton ConfigManager instance with error handling"""
    global _config_manager_instance
    try:
        if _config_manager_instance is None:
            _config_manager_instance = ConfigManager()
        return _config_manager_instance
    except Exception as e:
        logger.error(f"Error getting config manager: {e}")
        # Return a minimal working instance
        return _create_fallback_manager()


def _create_fallback_manager():
    """Create a fallback config manager if normal initialization fails"""

    class FallbackConfigManager:
        def __init__(self):
            self._config = Config()

        def get_config(self):
            return self._config

        def update_setting(self, key, value):
            pass

        def save_config(self):
            pass

        def reload_config(self):
            pass

    return FallbackConfigManager()


def get_simple_config():
    """Simple config access without manager dependency"""
    try:
        if ConfigManager._config:
            return ConfigManager._config
        return Config()
    except Exception:
        return Config()


def get_simple_config_manager():
    """Simple config manager access with fallback"""
    try:
        return get_config_manager()
    except Exception:
        return _create_fallback_manager()
