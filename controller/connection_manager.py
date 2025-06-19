from PyQt6.QtCore import QObject, pyqtSignal
from connectors.sharepoint_connector import SharePointConnector
from connectors.database_connector import DatabaseConnector
import logging

logger = logging.getLogger(__name__)


class ConnectionManager(QObject):
    """Manages connections to external services"""

    status_changed = pyqtSignal(str, str)  # service_name, status
    log_message = pyqtSignal(str, str)  # message, level

    def __init__(self):
        super().__init__()
        self._sharepoint_connector = None
        self._database_connector = None

    # SharePoint Connection Management
    def test_sharepoint_connection(self, config):
        """Test SharePoint connection"""
        try:
            self.status_changed.emit("SharePoint", "connecting")

            connector = SharePointConnector(config)
            success = connector.test_connection()

            if success:
                self.status_changed.emit("SharePoint", "connected")
                self._sharepoint_connector = connector
            else:
                self.status_changed.emit("SharePoint", "error")

            return success

        except Exception as e:
            self.status_changed.emit("SharePoint", "error")
            self.log_message.emit(
                f"SharePoint connection test failed: {str(e)}", "error"
            )
            logger.exception("SharePoint connection test failed")
            return False

    def get_sharepoint_sites(self, config):
        """Get available SharePoint sites"""
        try:
            connector = SharePointConnector(config)
            sites = connector.get_sites()
            return sites

        except Exception as e:
            self.log_message.emit(f"Failed to get SharePoint sites: {str(e)}", "error")
            logger.exception("Failed to get SharePoint sites")
            return []

    def get_sharepoint_lists(self, config, site_url=None):
        """Get SharePoint lists for a site"""
        try:
            connector = SharePointConnector(config)
            if site_url:
                lists = connector.get_lists(site_url)
            else:
                lists = connector.get_lists()
            return lists

        except Exception as e:
            self.log_message.emit(f"Failed to get SharePoint lists: {str(e)}", "error")
            logger.exception("Failed to get SharePoint lists")
            return []

    # Database Connection Management
    def test_database_connection(self, config):
        """Test database connection"""
        try:
            self.status_changed.emit("Database", "connecting")

            connector = DatabaseConnector(config)
            success = connector.test_connection()

            if success:
                self.status_changed.emit("Database", "connected")
                self._database_connector = connector
            else:
                self.status_changed.emit("Database", "error")

            return success

        except Exception as e:
            self.status_changed.emit("Database", "error")
            self.log_message.emit(f"Database connection test failed: {str(e)}", "error")
            logger.exception("Database connection test failed")
            return False

    def get_databases(self, config):
        """Get available databases (SQL Server only)"""
        try:
            if config.database_type != "sqlserver":
                return []

            connector = DatabaseConnector(config)
            databases = connector.get_databases()
            return databases

        except Exception as e:
            self.log_message.emit(f"Failed to get databases: {str(e)}", "error")
            logger.exception("Failed to get databases")
            return []

    def get_tables(self, config):
        """Get available tables"""
        try:
            connector = DatabaseConnector(config)
            tables = connector.get_tables()
            return tables

        except Exception as e:
            self.log_message.emit(f"Failed to get tables: {str(e)}", "error")
            logger.exception("Failed to get tables")
            return []

    # Connection Status
    def get_connection_status(self, config):
        """Get status of all connections"""
        status = {"sharepoint": "disconnected", "database": "disconnected"}

        # Test SharePoint
        try:
            sp_connector = SharePointConnector(config)
            if sp_connector.test_connection():
                status["sharepoint"] = "connected"
        except:
            pass

        # Test Database
        try:
            db_connector = DatabaseConnector(config)
            if db_connector.test_connection():
                status["database"] = "connected"
        except:
            pass

        return status

    def reset_connections(self):
        """Reset all connections"""
        self._sharepoint_connector = None
        self._database_connector = None
        self.status_changed.emit("SharePoint", "disconnected")
        self.status_changed.emit("Database", "disconnected")
        self.log_message.emit("🔄 รีเซ็ตการเชื่อมต่อทั้งหมด", "info")
