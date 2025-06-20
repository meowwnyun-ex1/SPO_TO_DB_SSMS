# controller/connection_manager.py - Enhanced with Caching and Robustness
from PyQt6.QtCore import QObject, pyqtSignal
from connectors.sharepoint_connector import SharePointConnector
from connectors.database_connector import DatabaseConnector
from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity
from utils.config_manager import Config  # Import Config dataclass for type hinting
import logging
import functools

logger = logging.getLogger(__name__)


class ConnectionManager(QObject):
    """
    Manages connections to external services (SharePoint, Database).
    Uses caching for connector instances to improve performance.
    """

    status_changed = pyqtSignal(str, str)  # service_name, status
    log_message = pyqtSignal(str, str)  # message, level

    def __init__(self, parent=None):
        super().__init__(parent)
        # Use functools.lru_cache for memoization of connector instances.
        # This prevents recreating expensive objects like database engines or session objects
        # as long as the config (hashable) is the same.
        self._get_sharepoint_connector_cached = functools.lru_cache(maxsize=1)(
            self._get_sharepoint_connector
        )
        self._get_database_connector_cached = functools.lru_cache(maxsize=1)(
            self._get_database_connector
        )
        logger.info("ConnectionManager initialized.")

    @handle_exceptions(
        ErrorCategory.CONNECTION, ErrorSeverity.HIGH
    )  # Removed user_message
    def _get_sharepoint_connector(
        self, config: Config
    ) -> Optional[SharePointConnector]:
        """Internal method to create and return a SharePointConnector instance."""
        try:
            connector = SharePointConnector(config)
            if connector.test_connection():
                self.status_changed.emit("SharePoint", "connected")
                self.log_message.emit(
                    "✅ SharePoint connection established.", "success"
                )
                logger.info(
                    "SharePoint connector created and connection tested successfully."
                )
                return connector
            else:
                self.status_changed.emit("SharePoint", "disconnected")
                self.log_message.emit("❌ SharePoint connection failed.", "error")
                logger.error(
                    "SharePoint connection test failed after connector creation."
                )
                return None
        except Exception as e:
            self.status_changed.emit("SharePoint", "error")
            self.log_message.emit(
                f"❌ Error creating SharePoint connector: {e}", "critical"
            )
            logger.critical(f"Error creating SharePointConnector: {e}", exc_info=True)
            return None

    @handle_exceptions(
        ErrorCategory.CONNECTION, ErrorSeverity.HIGH
    )  # Removed user_message
    def _get_database_connector(self, config: Config) -> Optional[DatabaseConnector]:
        """Internal method to create and return a DatabaseConnector instance."""
        try:
            connector = DatabaseConnector(config)
            if connector.test_connection():
                self.status_changed.emit("Database", "connected")
                self.log_message.emit("✅ Database connection established.", "success")
                logger.info(
                    "Database connector created and connection tested successfully."
                )
                return connector
            else:
                self.status_changed.emit("Database", "disconnected")
                self.log_message.emit("❌ Database connection failed.", "error")
                logger.error(
                    "Database connection test failed after connector creation."
                )
                return None
        except Exception as e:
            self.status_changed.emit("Database", "error")
            self.log_message.emit(
                f"❌ Error creating database connector: {e}", "critical"
            )
            logger.critical(f"Error creating DatabaseConnector: {e}", exc_info=True)
            return None

    @handle_exceptions(
        ErrorCategory.CONNECTION, ErrorSeverity.HIGH
    )  # Removed user_message
    def get_sharepoint_connector(self, config: Config) -> Optional[SharePointConnector]:
        """Returns a cached or new SharePointConnector instance."""
        return self._get_sharepoint_connector_cached(config)

    @handle_exceptions(
        ErrorCategory.CONNECTION, ErrorSeverity.HIGH
    )  # Removed user_message
    def get_database_connector(self, config: Config) -> Optional[DatabaseConnector]:
        """Returns a cached or new DatabaseConnector instance."""
        return self._get_database_connector_cached(config)

    @handle_exceptions(
        ErrorCategory.CONNECTION, ErrorSeverity.MEDIUM
    )  # Removed user_message
    def check_all_connections_status(self, config: Config) -> Dict[str, str]:
        """Checks the status of all connections without recreating connectors."""
        logger.info("Checking all connection statuses...")
        status = {"sharepoint": "disconnected", "database": "disconnected"}

        # Check SharePoint status
        try:
            sp_connector = self._get_sharepoint_connector_cached(
                config
            )  # Get cached instance
            if sp_connector and sp_connector.test_connection():
                status["sharepoint"] = "connected"
            else:
                status["sharepoint"] = (
                    "error"  # Mark as error if test fails or connector is None
                )
            logger.debug(f"SharePoint status: {status['sharepoint']}")
        except Exception:
            status["sharepoint"] = "error"
            logger.debug("SharePoint connection failed during status check.")

        # Check Database status
        try:
            db_connector = self._get_database_connector_cached(
                config
            )  # Get cached instance
            if db_connector and db_connector.test_connection():
                status["database"] = "connected"
            else:
                status["database"] = (
                    "error"  # Mark as error if test fails or connector is None
                )
            logger.debug(f"Database status: {status['database']}")
        except Exception:
            status["database"] = "error"
            logger.debug("Database connection failed during status check.")

        return status

    def reset_connections(self):
        """
        Clears all cached connector instances and resets connection status.
        This forces new connector instances to be created on next request.
        """
        self._get_sharepoint_connector_cached.cache_clear()
        self._get_database_connector_cached.cache_clear()
        self.status_changed.emit("SharePoint", "disconnected")
        self.status_changed.emit("Database", "disconnected")
        self.log_message.emit("🔄 Connections reset and cache cleared.", "info")
        logger.info("All connection caches cleared and status reset.")

    def cleanup(self):
        """Performs cleanup for ConnectionManager."""
        self.reset_connections()  # Clear all cached connectors
        # Disconnect all signals
        try:
            self.status_changed.disconnect()
            self.log_message.disconnect()
            logger.info("Disconnected ConnectionManager signals.")
        except TypeError as e:
            logger.debug(
                f"Attempted to disconnect non-connected ConnectionManager signal: {e}"
            )
        except Exception as e:
            logger.warning(f"Error during ConnectionManager signal disconnection: {e}")
        logger.info("ConnectionManager cleanup completed.")
