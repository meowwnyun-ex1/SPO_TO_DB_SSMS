from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from .sync_engine import SyncEngine
from .connection_manager import ConnectionManager
from utils.config_manager import ConfigManager
from utils.cache_cleaner import AutoCacheManager
from utils.excel_import_handler import ExcelImportHandler
from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity
import logging

logger = logging.getLogger(__name__)


class AppController(QObject):
    """
    Enhanced App Controller for DENSO Neural Matrix.
    Manages application logic, orchestrates data sync, connection tests,
    and interacts with UI components via signals.
    """

    # Core signals (emitted from controller to UI/other modules)
    status_changed = pyqtSignal(
        str, str
    )  # service_name, status (e.g., "SharePoint", "connected")
    progress_updated = pyqtSignal(str, int, str)  # task_name, percentage, message
    sync_completed = pyqtSignal(bool, str, dict)  # success, message, stats
    log_message = pyqtSignal(str, str)  # message, level (e.g., "Data synced", "info")

    # UI specific update signals (emitted to update UI dropdowns/labels)
    sharepoint_sites_updated = pyqtSignal(list)
    sharepoint_lists_updated = pyqtSignal(list)
    database_names_updated = pyqtSignal(list)
    database_tables_updated = pyqtSignal(list)
    ui_enable_request = pyqtSignal(bool)  # Request to enable/disable UI
    sharepoint_status_update = pyqtSignal(str)  # "connected", "disconnected", "error"
    database_status_update = pyqtSignal(str)  # "connected", "disconnected", "error"
    last_sync_status_update = pyqtSignal(str)  # success, failed, never
    auto_sync_status_update = pyqtSignal(bool)  # True if auto sync is enabled
    progress_update = pyqtSignal(int)  # For main progress bar (0-100)
    current_task_update = pyqtSignal(str)  # Current task description

    def __init__(self, parent=None):
        super().__init__(parent)
        logger.info("Initializing AppController...")
        self.config_manager = ConfigManager()
        self.config = self.config_manager.get_config()

        self.connection_manager = ConnectionManager()
        self.sync_engine = SyncEngine()
        self.excel_import_handler = ExcelImportHandler()
        self.auto_cache_manager = AutoCacheManager(
            cleanup_interval_hours=self.config.cache_cleanup_interval_hours,
            auto_cleanup_enabled=self.config.auto_cache_cleanup_enabled,
        )

        self._connect_signals()
        self._initialize_data()
        self.auto_sync_timer = QTimer(self)
        self.auto_sync_timer.timeout.connect(self._on_auto_sync_timeout)
        self.toggle_auto_sync(self.config.auto_sync_enabled)

        logger.info("AppController initialized.")

    def _connect_signals(self):
        """Connects signals between components and to UI update methods."""
        # Connect ConnectionManager signals
        self.connection_manager.status_changed.connect(
            self._handle_service_status_change
        )
        self.connection_manager.log_message.connect(
            lambda msg, level: self.log_message.emit(f"[CONN] {msg}", level)
        )

        # Connect SyncEngine signals
        self.sync_engine.progress_updated.connect(self.progress_updated.emit)
        self.sync_engine.sync_completed.connect(self._handle_sync_completed)
        self.sync_engine.log_message.connect(
            lambda msg, level: self.log_message.emit(f"[SYNC] {msg}", level)
        )

        # Connect CacheCleaner signals
        self.auto_cache_manager.log_message.connect(
            lambda msg, level: self.log_message.emit(f"[CACHE] {msg}", level)
        )

        # Connect ConfigManager signals (if any, for config reload notifications)
        self.config_manager.config_updated.connect(self._handle_config_update)

        # Connect ExcelImportHandler signals
        self.excel_import_handler.log_message.connect(
            lambda msg, level: self.log_message.emit(f"[EXCEL] {msg}", level)
        )
        self.excel_import_handler.import_progress.connect(
            lambda p: self.progress_update.emit(p)
        )
        self.excel_import_handler.import_completed.connect(
            self._handle_excel_import_completed
        )

    def _initialize_data(self):
        """Initializes data for UI components."""
        self.config_manager.load_config()
        self.update_ui_with_config()
        self.test_all_connections()
        self.get_available_sharepoint_sites()  # Populate sites dropdown
        self.get_available_sharepoint_lists()  # Populate lists dropdown
        self.get_available_databases()
        self.get_available_tables()

    @pyqtSlot(str, str)
    def _handle_service_status_change(self, service_name: str, status: str):
        """Handle status updates from ConnectionManager."""
        logger.info(f"Service status changed: {service_name} - {status}")
        if service_name == "SharePoint":
            self.sharepoint_status_update.emit(status)
        elif service_name == "Database":
            self.database_status_update.emit(status)

    @pyqtSlot(bool, str, dict)
    @handle_exceptions(ErrorCategory.SYNC, ErrorSeverity.HIGH)
    def _handle_sync_completed(self, success: bool, message: str, stats: dict):
        """Handle synchronization completion."""
        logger.info(f"Sync completed: Success={success}, Message='{message}'")
        sync_status = "success" if success else "failed"
        self.last_sync_status_update.emit(sync_status)
        self.sync_completed.emit(success, message, stats)
        self.ui_enable_request.emit(True)  # Re-enable UI after sync
        self.progress_update.emit(0)  # Reset progress bar
        self.current_task_update.emit("Idle")
        if success:
            self.log_message.emit(
                "Data synchronization completed successfully.", "info"
            )
        else:
            self.log_message.emit(f"Data synchronization failed: {message}", "error")

    @pyqtSlot()
    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.MEDIUM)
    def _handle_config_update(self):
        """Handle configuration update. Reloads config and updates UI."""
        logger.info("Configuration updated, reloading and applying to UI.")
        self.config = self.config_manager.get_config()  # Get the latest config
        self.update_ui_with_config()
        # Potentially re-test connections if relevant config changed
        self.test_all_connections()
        self.toggle_auto_sync(
            self.config.auto_sync_enabled
        )  # Re-evaluate auto-sync based on new config

    @pyqtSlot()
    @handle_exceptions(ErrorCategory.CONNECTION, ErrorSeverity.HIGH)
    def test_all_connections(self):
        """Tests connections to SharePoint and Database and updates UI."""
        logger.info("Testing all connections...")
        self.ui_enable_request.emit(False)  # Disable UI during connection test
        self.current_task_update.emit("Testing connections...")

        sp_status = "disconnected"
        db_status = "disconnected"

        try:
            sp_connected = self.connection_manager.test_sharepoint_connection(
                self.config
            )
            sp_status = "connected" if sp_connected else "error"
            self.sharepoint_status_update.emit(sp_status)
            self.log_message.emit(
                f"SharePoint connection: {'Connected' if sp_connected else 'Failed'}",
                "info" if sp_connected else "error",
            )
        except Exception as e:
            sp_status = "error"
            self.sharepoint_status_update.emit(sp_status)
            self.log_message.emit(f"SharePoint connection error: {e}", "critical")
            logger.exception("SharePoint connection test failed.")

        try:
            db_connected = self.connection_manager.test_database_connection(self.config)
            db_status = "connected" if db_connected else "error"
            self.database_status_update.emit(db_status)
            self.log_message.emit(
                f"Database connection: {'Connected' if db_connected else 'Failed'}",
                "info" if db_connected else "error",
            )
        except Exception as e:
            db_status = "error"
            self.database_status_update.emit(db_status)
            self.log_message.emit(f"Database connection error: {e}", "critical")
            logger.exception("Database connection test failed.")

        self.ui_enable_request.emit(True)  # Re-enable UI
        self.current_task_update.emit("Idle")
        logger.info(
            f"Connection test completed. SharePoint: {sp_status}, Database: {db_status}"
        )
        self.log_message.emit(
            f"Connection tests complete. SharePoint: {sp_status.capitalize()}, Database: {db_status.capitalize()}",
            "info",
        )

    @pyqtSlot(str)
    @handle_exceptions(ErrorCategory.SYNC, ErrorSeverity.HIGH)
    def run_full_sync(self, direction: str = "spo_to_sql"):
        """Initiates a full data synchronization."""
        logger.info(f"Initiating full sync in direction: {direction}...")
        self.ui_enable_request.emit(False)  # Disable UI during sync
        self.current_task_update.emit(f"Running full sync ({direction})...")
        self.log_message.emit(f"Starting full sync: {direction}", "info")
        self.progress_update.emit(0)

        # Validate config before starting sync
        if not self.sync_engine.validate_config_for_sync(self.config, direction):
            self.log_message.emit(
                "Sync configuration validation failed. Aborting sync.", "error"
            )
            self.ui_enable_request.emit(True)
            self.current_task_update.emit("Idle")
            return

        self.sync_engine.start_sync(self.config, direction)
        self.last_sync_status_update.emit("in_progress")

    @pyqtSlot(str, str, dict)
    @handle_exceptions(ErrorCategory.DATA, ErrorSeverity.HIGH)
    def import_excel_data(self, file_path: str, table_name: str, column_mapping: dict):
        """Initiates Excel data import."""
        logger.info(f"Initiating Excel import from {file_path} to {table_name}...")
        self.ui_enable_request.emit(False)
        self.current_task_update.emit("Importing Excel data...")
        self.log_message.emit(f"Starting Excel import: {file_path}", "info")
        self.progress_update.emit(0)
        self.excel_import_handler.start_import(
            file_path, table_name, column_mapping, self.config
        )

    @pyqtSlot(bool, str)
    @handle_exceptions(ErrorCategory.DATA, ErrorSeverity.HIGH)
    def _handle_excel_import_completed(self, success: bool, message: str):
        """Handles Excel import completion."""
        logger.info(f"Excel import completed: Success={success}, Message='{message}'")
        self.ui_enable_request.emit(True)
        self.progress_update.emit(0)
        self.current_task_update.emit("Idle")
        if success:
            self.log_message.emit("Excel import completed successfully.", "info")
        else:
            self.log_message.emit(f"Excel import failed: {message}", "error")

    @pyqtSlot(str, str, str)
    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.MEDIUM)
    def update_setting(self, key_path: str, value: Any, value_type: str):
        """Updates a configuration setting and saves it."""
        logger.info(
            f"Attempting to update setting: {key_path} with value '{value}' (type: {value_type})"
        )
        # Convert value to appropriate type
        if value_type == "bool":
            converted_value = value.lower() == "true"
        elif value_type == "int":
            converted_value = int(value)
        elif value_type == "float":
            converted_value = float(value)
        else:  # string or other types
            converted_value = value

        self.config_manager.update_setting(key_path, converted_value)
        self.log_message.emit(f"Setting '{key_path}' updated.", "info")
        # ConfigManager's config_updated signal will trigger _handle_config_update

    @pyqtSlot()
    @handle_exceptions(ErrorCategory.SYSTEM, ErrorSeverity.LOW)
    def run_cache_cleanup(self):
        """Manually triggers cache cleanup."""
        logger.info("Manual cache cleanup initiated.")
        self.auto_cache_manager.run_cleanup()

    @pyqtSlot(bool)
    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.MEDIUM)
    def toggle_auto_sync(self, enabled: bool):
        """Toggles automatic synchronization."""
        self.config_manager.update_setting("auto_sync_enabled", enabled)
        self.config.auto_sync_enabled = enabled  # Update local config immediately
        self.auto_sync_status_update.emit(enabled)
        if enabled:
            interval = self.config.sync_interval * 60 * 1000  # Convert minutes to ms
            self.auto_sync_timer.start(interval)
            logger.info(
                f"Auto-sync enabled with interval: {self.config.sync_interval} minutes."
            )
            self.log_message.emit(
                f"Auto-sync enabled. Next sync in {self.config.sync_interval} minutes.",
                "info",
            )
        else:
            self.auto_sync_timer.stop()
            logger.info("Auto-sync disabled.")
            self.log_message.emit("Auto-sync disabled.", "info")

    @pyqtSlot()
    def _on_auto_sync_timeout(self):
        """Triggered by the auto-sync timer."""
        logger.info("Auto-sync triggered.")
        self.run_full_sync(self.config.auto_sync_direction)

    @pyqtSlot()
    def get_available_sharepoint_sites(self):
        """Fetches and emits available SharePoint sites."""
        try:
            sites = self.connection_manager.get_sharepoint_available_sites(self.config)
            self.sharepoint_sites_updated.emit(sites)
            logger.debug(f"SharePoint sites fetched: {sites}")
        except Exception as e:
            logger.error(f"Failed to fetch SharePoint sites: {e}")
            self.log_message.emit(f"Failed to load SharePoint sites: {e}", "error")
            self.sharepoint_sites_updated.emit([])

    @pyqtSlot()
    def get_available_sharepoint_lists(self):
        """Fetches and emits available SharePoint lists for the configured site."""
        try:
            lists = self.connection_manager.get_sharepoint_available_lists(self.config)
            self.sharepoint_lists_updated.emit(lists)
            logger.debug(f"SharePoint lists fetched: {lists}")
        except Exception as e:
            logger.error(f"Failed to fetch SharePoint lists: {e}")
            self.log_message.emit(f"Failed to load SharePoint lists: {e}", "error")
            self.sharepoint_lists_updated.emit([])

    @pyqtSlot()
    def get_available_databases(self):
        """Fetches and emits available databases for the configured connection."""
        try:
            databases = self.connection_manager.get_database_available_databases(
                self.config
            )
            self.database_names_updated.emit(databases)
            logger.debug(f"Available databases fetched: {databases}")
        except Exception as e:
            logger.error(f"Failed to fetch available databases: {e}")
            self.log_message.emit(f"Failed to load databases: {e}", "error")
            self.database_names_updated.emit([])

    @pyqtSlot()
    def get_available_tables(self):
        """Fetches and emits available tables for the configured database."""
        try:
            tables = self.connection_manager.get_database_available_tables(self.config)
            self.database_tables_updated.emit(tables)
            logger.debug(f"Available tables fetched: {tables}")
        except Exception as e:
            logger.error(f"Failed to fetch available tables: {e}")
            self.log_message.emit(f"Failed to load tables: {e}", "error")
            self.database_tables_updated.emit([])

    @pyqtSlot()
    def update_ui_with_config(self):
        """Emits signals to update various UI elements based on current config."""
        logger.debug("Updating UI with current configuration...")
        self.sharepoint_status_update.emit(
            "disconnected"
        )  # Reset to disconnected until tested
        self.database_status_update.emit(
            "disconnected"
        )  # Reset to disconnected until tested
        self.last_sync_status_update.emit(self.config.last_sync_status)
        self.auto_sync_status_update.emit(self.config.auto_sync_enabled)
        self.progress_update.emit(0)
        self.current_task_update.emit("Idle")

    def _cleanup_signals(self):
        """Centralized method to disconnect all signals."""
        logger.info("Disconnecting AppController signals...")
        signals_to_disconnect = [
            self.connection_manager.status_changed,
            self.connection_manager.log_message,
            self.sync_engine.progress_updated,
            self.sync_engine.sync_completed,
            self.sync_engine.log_message,
            self.auto_cache_manager.log_message,
            self.config_manager.config_updated,
            self.excel_import_handler.log_message,
            self.excel_import_handler.import_progress,
            self.excel_import_handler.import_completed,
            self.auto_sync_timer.timeout,
        ]

        for signal in signals_to_disconnect:
            try:
                signal.disconnect()
            except TypeError as e:
                logger.debug(
                    f"Attempted to disconnect non-connected signal {signal.name}: {e}"
                )
            except Exception as e:
                logger.warning(f"Error during signal {signal.name} disconnection: {e}")
        logger.info("All AppController signals disconnected.")

    def cleanup(self):
        """
        Performs comprehensive cleanup for the AppController and its managed components.
        Ensures all threads, timers, and connections are properly terminated.
        """
        logger.info("Initiating AppController cleanup...")

        # Stop auto-sync timer
        if self.auto_sync_timer.isActive():
            self.auto_sync_timer.stop()
            self.auto_sync_timer.deleteLater()
            logger.info("Auto-sync timer stopped.")

        # Clean up SyncEngine
        if self.sync_engine:
            self.sync_engine.cleanup()
            logger.info("SyncEngine cleanup completed.")

        # Clean up ConnectionManager
        if self.connection_manager:
            self.connection_manager.cleanup()
            logger.info("ConnectionManager cleanup completed.")

        # Clean up ExcelImportHandler
        if self.excel_import_handler:
            self.excel_import_handler.cleanup()
            logger.info("ExcelImportHandler cleanup completed.")

        # Clean up cache manager (e.g., stop its timer if any)
        if hasattr(self.auto_cache_manager, "cleanup"):
            self.auto_cache_manager.cleanup()
            logger.info("AutoCacheManager cleanup completed.")

        # Disconnect all signals to prevent dangling connections
        self._cleanup_signals()

        logger.info("AppController cleanup completed successfully.")
