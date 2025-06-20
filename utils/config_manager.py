# utils/config_manager.py - Comprehensive Configuration Management
import os
import json
from dataclasses import dataclass, field, asdict
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, Any, Optional
import logging

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
    Data class to hold all application configuration settings.
    Default values are provided, some from environment variables.
    """

    # General Application Settings
    app_name: str = "DENSO Neural Matrix"
    app_version: str = "1.0.0"
    connection_timeout: int = 30  # Default timeout for network operations in seconds
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    max_retries: int = 3  # Added max_retries for network operations

    # UI Settings
    background_image_path: str = "resources/images/bg_denso_matrix.jpg"
    enable_background_audio: bool = False
    background_audio_path: str = "resources/audio/bg_ambient.mp3"
    background_audio_volume: float = 0.1  # 0.0 to 1.0

    # SharePoint Configuration
    sharepoint_url: str = os.getenv(
        "SHAREPOINT_URL", ""
    )  # Use SHAREPOINT_URL if available
    sharepoint_site: str = os.getenv(
        "SHAREPOINT_SITE", "https://yourdomain.sharepoint.com/sites/YourSite"
    )
    sharepoint_list: str = os.getenv("SHAREPOINT_LIST", "your_list_name")
    sharepoint_client_id: str = os.getenv("SHAREPOINT_CLIENT_ID", "")
    sharepoint_client_secret: str = os.getenv("SHAREPOINT_CLIENT_SECRET", "")
    tenant_id: str = os.getenv("TENANT_ID", "")
    use_graph_api: bool = False  # Set to True to use Microsoft Graph API

    # Database Configuration
    database_type: str = "sqlserver"  # or "sqlite"
    db_type: str = "SQL Server"  # Alias for display in UI

    # SQL Server Configuration
    sql_server: str = os.getenv("SQL_SERVER", "your_sql_server.database.windows.net")
    sql_database: str = os.getenv("SQL_DATABASE", "your_db")
    sql_username: str = os.getenv("SQL_USERNAME", "your_user")
    sql_password: str = os.getenv("SQL_PASSWORD", "your_password")
    sql_table_name: str = os.getenv("SQL_TABLE_NAME", "your_table")
    sql_create_table: bool = True  # Automatically create table if not exists
    sql_truncate_before: bool = True  # Truncate table before sync for SPO to SQL

    # SQLite Configuration
    sqlite_file: str = os.getenv("SQLITE_FILE", "data.db")
    sqlite_table_name: str = os.getenv("SQLITE_TABLE_NAME", "sharepoint_data")
    sqlite_create_table: bool = True  # Automatically create table if not exists

    # Synchronization Settings
    sync_interval: int = 600  # seconds (e.g., 600s = 10 minutes)
    sync_mode: str = "full"  # "full", "incremental", "bidirectional"
    auto_sync_enabled: bool = False
    last_sync_timestamp: Optional[str] = None  # Store as ISO format string

    # Field Mappings (example structures, should be loaded from config.json)
    sharepoint_to_sql_mapping: Dict[str, str] = field(default_factory=dict)
    sql_to_sharepoint_mapping: Dict[str, str] = field(default_factory=dict)

    # Excel Import Settings
    excel_import_mapping: Dict[str, str] = field(
        default_factory=dict
    )  # New field for Excel mapping


class ConfigManager:
    """
    Manages application configuration, loading from config.json and .env,
    and providing methods to get and set settings dynamically.
    """

    _config: Config = None  # Singleton instance of Config

    def __init__(self):
        if ConfigManager._config is None:
            ConfigManager._config = self._load_config()
        logger.debug("ConfigManager initialized.")

    def _load_config(self) -> Config:
        """Loads configuration from config.json and environment variables."""
        config_data = {}
        # Ensure default config directory exists
        DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        if DEFAULT_CONFIG_PATH.exists():
            try:
                with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                logger.info(f"Loaded configuration from {DEFAULT_CONFIG_PATH}.")
            except json.JSONDecodeError as e:
                logger.error(
                    f"Error decoding config.json: {e}. Using default settings.",
                    exc_info=True,
                )
            except Exception as e:
                logger.error(
                    f"An unexpected error occurred while reading config.json: {e}. Using default settings.",
                    exc_info=True,
                )
        else:
            logger.warning(
                f"Configuration file not found at {DEFAULT_CONFIG_PATH}. Creating with default settings."
            )
            # Save default config if file doesn't exist
            self._save_default_config()

        # Create a Config instance with default values
        config = Config()

        # Override with values from config.json (nested support)
        for key, value in config_data.items():
            if hasattr(config, key):
                if isinstance(getattr(config, key), dict) and isinstance(value, dict):
                    # Merge dictionaries for nested settings
                    getattr(config, key).update(value)
                else:
                    try:
                        # Attempt type conversion if necessary
                        target_type = type(getattr(config, key))
                        if target_type == Path:  # Handle Path objects
                            setattr(config, key, Path(value))
                        elif target_type == bool and isinstance(value, str):
                            setattr(
                                config,
                                key,
                                value.lower() in ("true", "1", "t", "y", "yes"),
                            )
                        elif value is not None:
                            setattr(config, key, target_type(value))
                    except (ValueError, TypeError):
                        logger.warning(
                            f"Type mismatch for config key '{key}'. Using default value for now."
                        )
            else:
                logger.warning(
                    f"Unknown configuration key '{key}' found in config.json. Skipping."
                )

        # Override with environment variables (higher precedence)
        # Environment variables are already loaded by load_dotenv() at module level
        # We can iterate through Config fields and check os.getenv
        for field_name, field_type in config.__annotations__.items():
            env_var_name = field_name.upper()
            env_value = os.getenv(env_var_name)
            if env_value is not None:
                try:
                    # Basic type conversion for environment variables
                    if field_type == int:
                        setattr(config, field_name, int(env_value))
                    elif field_type == float:
                        setattr(config, field_name, float(env_value))
                    elif field_type == bool:
                        setattr(
                            config,
                            field_name,
                            env_value.lower() in ("true", "1", "t", "y", "yes"),
                        )
                    elif field_type == str:
                        setattr(config, field_name, env_value)
                    # For Dict, List, Optional, etc., more complex parsing might be needed
                    # but for now, simple string assignment for env vars is common.
                except (ValueError, TypeError):
                    logger.warning(
                        f"Could not convert environment variable '{env_var_name}' value '{env_value}' to type {field_type}. Using config file/default value."
                    )

        logger.debug("Configuration loaded successfully into Config object.")
        return config

    def _save_default_config(self):
        """Saves the current default configuration to config.json."""
        default_config_dict = asdict(Config())
        try:
            with open(DEFAULT_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(default_config_dict, f, indent=2, ensure_ascii=False)
            logger.info(f"Default configuration saved to {DEFAULT_CONFIG_PATH}.")
        except Exception as e:
            logger.error(f"Failed to save default config.json: {e}", exc_info=True)

    def save_config(self):
        """Saves the current configuration instance back to config.json."""
        if ConfigManager._config:
            try:
                # Convert dataclass to dict, excluding fields that are default_factory (e.g., dicts)
                # and merge current dict values.
                current_config_dict = asdict(ConfigManager._config)

                # Re-read existing config to preserve keys not managed by Config dataclass
                # This prevents unintended data loss if config.json has extra keys
                existing_config_data = {}
                if DEFAULT_CONFIG_PATH.exists():
                    try:
                        with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
                            existing_config_data = json.load(f)
                    except json.JSONDecodeError:
                        logger.warning(
                            "Existing config.json is invalid JSON. Overwriting."
                        )
                    except Exception as e:
                        logger.warning(
                            f"Could not read existing config.json: {e}. Overwriting."
                        )

                # Update only the known keys from the Config dataclass
                for key, value in current_config_dict.items():
                    existing_config_data[key] = value

                with open(DEFAULT_CONFIG_PATH, "w", encoding="utf-8") as f:
                    json.dump(existing_config_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Configuration saved to {DEFAULT_CONFIG_PATH}.")
            except Exception as e:
                logger.error(
                    f"Failed to save configuration to config.json: {e}", exc_info=True
                )
        else:
            logger.warning("No configuration instance to save.")

    def set_setting(self, key_path: str, value: Any):
        """
        Sets a configuration setting.
        Supports nested settings by using dot notation, e.g., "sharepoint.url" or "auto_sync.enabled".
        """
        parts = key_path.split(".")
        current = ConfigManager._config
        for i, part in enumerate(parts):
            if hasattr(current, part):
                if i == len(parts) - 1:
                    # Attempt type conversion based on the dataclass field's type
                    target_type = type(getattr(current, part))
                    try:
                        if target_type == bool and isinstance(value, str):
                            converted_value = value.lower() in (
                                "true",
                                "1",
                                "t",
                                "y",
                                "yes",
                            )
                        else:
                            converted_value = target_type(value)
                        setattr(current, part, converted_value)
                        logger.debug(f"Config updated: {key_path} = {converted_value}")
                    except (ValueError, TypeError):
                        logger.warning(
                            f"Cannot convert value '{value}' to type {target_type} for config key '{key_path}'. Update ignored."
                        )
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


# Ensure a ConfigManager instance is created at startup to load the config
# This makes sure ConfigManager._config is populated when other modules import it.
ConfigManager()
