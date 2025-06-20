# controller/connection_manager.py - Fixed Connection Manager
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Optional, Dict
import logging
import hashlib
import time

from connectors.sharepoint_connector import SharePointConnector
from connectors.database_connector import DatabaseConnector
from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity
from utils.config_manager import Config

logger = logging.getLogger(__name__)


class ConnectionCache:
    """Simple cache for connector instances with TTL"""

    def __init__(self, ttl_seconds: int = 300):  # 5 minutes default TTL
        self.cache = {}
        self.ttl = ttl_seconds

    def _generate_key(self, config: Config, connector_type: str) -> str:
        """Generate cache key based on configuration"""
        if connector_type == "sharepoint":
            config_str = f"{config.sharepoint_site}_{config.sharepoint_client_id}_{config.tenant_id}"
        elif connector_type == "database":
            if config.database_type == "sqlserver":
                config_str = (
                    f"{config.sql_server}_{config.sql_database}_{config.sql_username}"
                )
            else:
                config_str = f"{config.sqlite_file}"
        else:
            config_str = str(config)

        return hashlib.md5(config_str.encode()).hexdigest()

    def get(self, config: Config, connector_type: str):
        """Get cached connector if valid"""
        key = self._generate_key(config, connector_type)

        if key in self.cache:
            connector, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                logger.debug(f"Cache hit for {connector_type} connector")
                return connector
            else:
                logger.debug(f"Cache expired for {connector_type} connector")
                del self.cache[key]

        return None

    def set(self, config: Config, connector_type: str, connector):
        """Cache connector instance"""
        key = self._generate_key(config, connector_type)
        self.cache[key] = (connector, time.time())
        logger.debug(f"Cached {connector_type} connector")

    def clear(self):
        """Clear all cached connectors"""
        for key, (connector, _) in self.cache.items():
            try:
                if hasattr(connector, "close"):
                    connector.close()
            except Exception as e:
                logger.debug(f"Error closing cached connector: {e}")

        self.cache.clear()
        logger.debug("Connection cache cleared")


class ConnectionManager(QObject):
    """
    Manages connections to external services (SharePoint, Database).
    Enhanced with caching, health monitoring, and robust error handling.
    """

    status_changed = pyqtSignal(str, str)  # service_name, status
    log_message = pyqtSignal(str, str)  # message, level

    def __init__(self, parent=None):
        super().__init__(parent)

        # Connection cache with 5-minute TTL
        self.cache = ConnectionCache(ttl_seconds=300)

        # Connection status tracking
        self.connection_status = {
            "sharepoint": "disconnected",
            "database": "disconnected",
        }

        # Last connection test times
        self.last_test_time = {}

        logger.info("ConnectionManager initialized")

    @handle_exceptions(ErrorCategory.CONNECTION, ErrorSeverity.HIGH)
    def get_sharepoint_connector(self, config: Config) -> Optional[SharePointConnector]:
        """Get SharePoint connector instance with caching"""
        try:
            # Try to get from cache first
            connector = self.cache.get(config, "sharepoint")
            if connector:
                # Test if cached connector still works
                if self._test_sharepoint_connector(connector):
                    return connector
                else:
                    logger.warning(
                        "Cached SharePoint connector failed test, creating new one"
                    )

            # Create new connector
            logger.info("Creating new SharePoint connector")
            connector = SharePointConnector(config)

            # Test connection before caching
            if self._test_sharepoint_connector(connector):
                self.cache.set(config, "sharepoint", connector)
                self._update_connection_status("sharepoint", "connected")
                self.log_message.emit("✅ SharePoint connection established", "success")
                return connector
            else:
                self._update_connection_status("sharepoint", "error")
                self.log_message.emit("❌ SharePoint connection failed", "error")
                return None

        except Exception as e:
            self._update_connection_status("sharepoint", "error")
            self.log_message.emit(f"❌ SharePoint connector error: {e}", "critical")
            logger.error(f"Error creating SharePoint connector: {e}", exc_info=True)
            return None

    @handle_exceptions(ErrorCategory.CONNECTION, ErrorSeverity.HIGH)
    def get_database_connector(self, config: Config) -> Optional[DatabaseConnector]:
        """Get database connector instance with caching"""
        try:
            # Try to get from cache first
            connector = self.cache.get(config, "database")
            if connector:
                # Test if cached connector still works
                if self._test_database_connector(connector):
                    return connector
                else:
                    logger.warning(
                        "Cached database connector failed test, creating new one"
                    )

            # Create new connector
            logger.info(f"Creating new {config.database_type} database connector")
            connector = DatabaseConnector(config)

            # Test connection before caching
            if self._test_database_connector(connector):
                self.cache.set(config, "database", connector)
                self._update_connection_status("database", "connected")
                self.log_message.emit("✅ Database connection established", "success")
                return connector
            else:
                self._update_connection_status("database", "error")
                self.log_message.emit("❌ Database connection failed", "error")
                return None

        except Exception as e:
            self._update_connection_status("database", "error")
            self.log_message.emit(f"❌ Database connector error: {e}", "critical")
            logger.error(f"Error creating database connector: {e}", exc_info=True)
            return None

    def _test_sharepoint_connector(self, connector: SharePointConnector) -> bool:
        """Test SharePoint connector functionality"""
        try:
            return connector.test_connection()
        except Exception as e:
            logger.debug(f"SharePoint connector test failed: {e}")
            return False

    def _test_database_connector(self, connector: DatabaseConnector) -> bool:
        """Test database connector functionality"""
        try:
            return connector.test_connection()
        except Exception as e:
            logger.debug(f"Database connector test failed: {e}")
            return False

    def _update_connection_status(self, service_name: str, status: str):
        """Update connection status and emit signal"""
        old_status = self.connection_status.get(service_name, "unknown")
        if old_status != status:
            self.connection_status[service_name] = status
            self.status_changed.emit(service_name.title(), status)
            self.last_test_time[service_name] = time.time()
            logger.info(
                f"{service_name.title()} status changed: {old_status} → {status}"
            )

    @handle_exceptions(ErrorCategory.CONNECTION, ErrorSeverity.MEDIUM)
    def test_sharepoint_connection(self, config: Config) -> bool:
        """Test SharePoint connection without caching"""
        try:
            logger.info("Testing SharePoint connection")
            self._update_connection_status("sharepoint", "connecting")

            connector = SharePointConnector(config)
            result = connector.test_connection()

            if result:
                self._update_connection_status("sharepoint", "connected")
                logger.info("SharePoint connection test successful")
            else:
                self._update_connection_status("sharepoint", "error")
                logger.warning("SharePoint connection test failed")

            # Clean up test connector
            connector.close()
            return result

        except Exception as e:
            self._update_connection_status("sharepoint", "error")
            logger.error(f"SharePoint connection test error: {e}")
            return False

    @handle_exceptions(ErrorCategory.CONNECTION, ErrorSeverity.MEDIUM)
    def test_database_connection(self, config: Config) -> bool:
        """Test database connection without caching"""
        try:
            logger.info(f"Testing {config.database_type} database connection")
            self._update_connection_status("database", "connecting")

            connector = DatabaseConnector(config)
            result = connector.test_connection()

            if result:
                self._update_connection_status("database", "connected")
                logger.info("Database connection test successful")
            else:
                self._update_connection_status("database", "error")
                logger.warning("Database connection test failed")

            # Clean up test connector
            connector.close()
            return result

        except Exception as e:
            self._update_connection_status("database", "error")
            logger.error(f"Database connection test error: {e}")
            return False

    @handle_exceptions(ErrorCategory.CONNECTION, ErrorSeverity.MEDIUM)
    def test_all_connections(self, config: Config) -> Dict[str, bool]:
        """Test all connections and return results"""
        results = {}

        logger.info("Testing all connections")

        # Test SharePoint
        try:
            results["sharepoint"] = self.test_sharepoint_connection(config)
        except Exception as e:
            logger.error(f"SharePoint test failed: {e}")
            results["sharepoint"] = False

        # Test Database
        try:
            results["database"] = self.test_database_connection(config)
        except Exception as e:
            logger.error(f"Database test failed: {e}")
            results["database"] = False

        # Log summary
        success_count = sum(results.values())
        total_count = len(results)

        if success_count == total_count:
            self.log_message.emit(
                f"✅ All {total_count} connections successful", "success"
            )
        elif success_count > 0:
            self.log_message.emit(
                f"⚠️ {success_count}/{total_count} connections successful", "warning"
            )
        else:
            self.log_message.emit("❌ All connection tests failed", "error")

        return results

    def get_connection_status(self) -> Dict[str, str]:
        """Get current connection status for all services"""
        return self.connection_status.copy()

    def get_connection_health(self) -> Dict[str, dict]:
        """Get detailed connection health information"""
        health = {}

        for service, status in self.connection_status.items():
            last_test = self.last_test_time.get(service)
            health[service] = {
                "status": status,
                "last_test": last_test,
                "last_test_age": time.time() - last_test if last_test else None,
                "is_stale": (
                    (time.time() - last_test > 300) if last_test else True
                ),  # 5 minutes
            }

        return health

    def refresh_connections(self):
        """Force refresh of all cached connections"""
        logger.info("Refreshing all connections")
        self.cache.clear()

        # Reset status
        for service in self.connection_status:
            self._update_connection_status(service, "disconnected")

        self.log_message.emit("🔄 Connection cache cleared", "info")

    def cleanup(self):
        """Perform cleanup for ConnectionManager"""
        logger.info("ConnectionManager cleanup initiated")

        try:
            # Clear cache (this will also close cached connectors)
            self.cache.clear()

            # Reset status
            for service in self.connection_status:
                self.connection_status[service] = "disconnected"

            # Disconnect signals
            try:
                self.status_changed.disconnect()
                self.log_message.disconnect()
                logger.info("ConnectionManager signals disconnected")
            except (TypeError, RuntimeError):
                pass  # Signals already disconnected

        except Exception as e:
            logger.error(f"Error during ConnectionManager cleanup: {e}")

        logger.info("ConnectionManager cleanup completed")

    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            self.cleanup()
        except Exception:
            pass  # Ignore errors during destruction
