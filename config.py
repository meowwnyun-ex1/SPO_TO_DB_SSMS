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
    sqlite_table_name: str = "data"
    sqlite_create_table: bool = True

    # Sync Configuration
    sync_interval: int = int(os.getenv("SYNC_INTERVAL", "3600"))  # Default: 1 hour
    sync_mode: str = "full"  # or "incremental"


def save_config(config: Config):
    """Save configuration to JSON file"""
    config_dict = {
        "sharepoint": {
            "site": config.sharepoint_site,
            "list": config.sharepoint_list,
            "client_id": config.sharepoint_client_id,
            "client_secret": config.sharepoint_client_secret,
            "tenant_id": config.tenant_id,
            "use_graph_api": config.use_graph_api,
        },
        "database": {
            "type": config.database_type,
            "sqlserver": {
                "server": config.sql_server,
                "database": config.sql_database,
                "username": config.sql_username,
                "password": config.sql_password,
                "table_name": config.sql_table_name,
                "create_table": config.sql_create_table,
            },
            "sqlite": {
                "file": config.sqlite_file,
                "table_name": config.sqlite_table_name,
                "create_table": config.sqlite_create_table,
            },
        },
        "sync": {
            "interval": config.sync_interval,
            "mode": config.sync_mode,
        },
    }

    with open(CONFIG_FILE, "w") as f:
        json.dump(config_dict, f, indent=4)


def load_config() -> Config:
    """Load configuration from JSON file or create default"""
    if not Path(CONFIG_FILE).exists():
        return Config()

    try:
        with open(CONFIG_FILE, "r") as f:
            config_dict = json.load(f)

        config = Config()

        # SharePoint
        sp = config_dict.get("sharepoint", {})
        config.sharepoint_site = sp.get("site", config.sharepoint_site)
        config.sharepoint_list = sp.get("list", config.sharepoint_list)
        config.sharepoint_client_id = sp.get("client_id", config.sharepoint_client_id)
        config.sharepoint_client_secret = sp.get(
            "client_secret", config.sharepoint_client_secret
        )
        config.tenant_id = sp.get("tenant_id", config.tenant_id)
        config.use_graph_api = sp.get("use_graph_api", config.use_graph_api)

        # Database
        db = config_dict.get("database", {})
        config.database_type = db.get("type", config.database_type)

        sqls = db.get("sqlserver", {})
        config.sql_server = sqls.get("server", config.sql_server)
        config.sql_database = sqls.get("database", config.sql_database)
        config.sql_username = sqls.get("username", config.sql_username)
        config.sql_password = sqls.get("password", config.sql_password)
        config.sql_table_name = sqls.get("table_name", config.sql_table_name)
        config.sql_create_table = sqls.get("create_table", config.sql_create_table)

        sqlite = db.get("sqlite", {})
        config.sqlite_file = sqlite.get("file", config.sqlite_file)
        config.sqlite_table_name = sqlite.get("table_name", config.sqlite_table_name)
        config.sqlite_create_table = sqlite.get(
            "create_table", config.sqlite_create_table
        )

        # Sync
        sync = config_dict.get("sync", {})
        config.sync_interval = sync.get("interval", config.sync_interval)
        config.sync_mode = sync.get("mode", config.sync_mode)

        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        return Config()
