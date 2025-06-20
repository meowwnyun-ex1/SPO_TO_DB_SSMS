# controller/app_controller.py - Debug App Controller
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, pyqtSlot
from typing import Any
import logging

logger = logging.getLogger(__name__)


class AppController(QObject):
    """
    Enhanced App Controller for DENSO Neural Matrix.
    Manages application logic, orchestrates data sync, connection tests,
    and interacts with UI components via signals.
    """

    # Core signals
    status_changed = pyqtSignal(str, str)  # service_name, status
    progress_updated = pyqtSignal(str, int, str)  # task_name, percentage, message
    sync_completed = pyqtSignal(bool, str, dict)  # success, message, stats
    log_message = pyqtSignal(str, str)  # message, level

    # UI update signals
    sharepoint_sites_updated = pyqtSignal(list)
    sharepoint_lists_updated = pyqtSignal(list)
    database_names_updated = pyqtSignal(list)
    database_tables_updated = pyqtSignal(list)
    ui_enable_request = pyqtSignal(bool)
    sharepoint_status_update = pyqtSignal(str)
    database_status_update = pyqtSignal(str)
    last_sync_status_update = pyqtSignal(str)
    auto_sync_status_update = pyqtSignal(bool)
    progress_update = pyqtSignal(int)
    current_task_update = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        logger.info("Initializing AppController...")

        try:
            print("AppController: Getting config manager...")
            from utils.config_manager import get_config_manager

            self.config_manager = get_config_manager()
            print("AppController: Config manager obtained")

            self.config = self.config_manager.get_config()
            print("AppController: Config obtained")

            print("AppController: Creating connection manager...")
            from .connection_manager import ConnectionManager

            self.connection_manager = ConnectionManager()
            print("AppController: Connection manager created")

            print("AppController: Creating sync engine...")
            from .sync_engine import SyncEngine

            self.sync_engine = SyncEngine(self.config)
            print("AppController: Sync engine created")

            print("AppController: Creating excel import handler...")
            from utils.excel_import_handler import ExcelImportHandler

            self.excel_import_handler = ExcelImportHandler(self.config)
            print("AppController: Excel import handler created")

            print("AppController: Creating auto cache manager...")
            from utils.cache_cleaner import AutoCacheManager

            self.auto_cache_manager = AutoCacheManager(self.config_manager)
            print("AppController: Auto cache manager created")

            print("AppController: Connecting signals...")
            self._connect_signals()
            print("AppController: Signals connected")

            print("AppController: Initializing data...")
            self._initialize_data()
            print("AppController: Data initialized")

            print("AppController: Setting up auto sync timer...")
            self.auto_sync_timer = QTimer(self)
            self.auto_sync_timer.timeout.connect(self._on_auto_sync_timeout)
            self.toggle_auto_sync(self.config.auto_sync_enabled)
            print("AppController: Auto sync timer setup complete")

            logger.info("AppController initialized.")
            print("AppController: Initialization complete!")

        except Exception as e:
            print(f"AppController initialization error: {e}")
            logger.error(f"AppController initialization error: {e}", exc_info=True)
            raise

    def _connect_signals(self):
        """Connect signals between components"""
        try:
            print("AppController: Connecting ConnectionManager signals...")
            # ConnectionManager signals
            self.connection_manager.status_changed.connect(
                self._handle_service_status_change
            )
            self.connection_manager.log_message.connect(
                lambda msg, level: self.log_message.emit(f"[CONN] {msg}", level)
            )
            print("AppController: ConnectionManager signals connected")

            print("AppController: Connecting SyncEngine signals...")
            # SyncEngine signals
            self.sync_engine.progress_updated.connect(self.progress_updated.emit)
            self.sync_engine.sync_completed.connect(self._handle_sync_completed)
            self.sync_engine.log_message.connect(
                lambda msg, level: self.log_message.emit(f"[SYNC] {msg}", level)
            )
            print("AppController: SyncEngine signals connected")

            print("AppController: Connecting CacheManager signals...")
            # CacheManager signals
            self.auto_cache_manager.log_message.connect(
                lambda msg, level: self.log_message.emit(f"[CACHE] {msg}", level)
            )
            print("AppController: CacheManager signals connected")

            print("AppController: Connecting ConfigManager signals...")
            # ConfigManager signals
            self.config_manager.config_updated.connect(self._handle_config_update)
            print("AppController: ConfigManager signals connected")

            print("AppController: Connecting ExcelImportHandler signals...")
            # ExcelImportHandler signals
            self.excel_import_handler.log_message.connect(
                lambda msg, level: self.log_message.emit(f"[EXCEL] {msg}", level)
            )
            self.excel_import_handler.import_progress.connect(
                lambda p, msg: self.progress_update.emit(p)
            )
            self.excel_import_handler.import_completed.connect(
                self._handle_excel_import_completed
            )
            print("AppController: ExcelImportHandler signals connected")

            logger.debug("AppController signals connected successfully")

        except Exception as e:
            print(f"AppController signal connection error: {e}")
            logger.error(f"Error connecting AppController signals: {e}")
            raise

    def _initialize_data(self):
        """Initialize data for UI components"""
        try:
            print("AppController: Updating UI with config...")
            self.update_ui_with_config()
            print("AppController: Testing all connections...")
            self.test_all_connections()
            print("AppController: Data initialization complete")
            logger.debug("AppController data initialized")
        except Exception as e:
            print(f"AppController data initialization error: {e}")
            logger.error(f"Error initializing AppController data: {e}")
            # Don't raise here, continue with partially initialized state

    @pyqtSlot(str, str)
    def _handle_service_status_change(self, service_name: str, status: str):
        """Handle status updates from ConnectionManager"""
        logger.info(f"Service status changed: {service_name} - {status}")
        if service_name == "SharePoint":
            self.sharepoint_status_update.emit(status)
        elif service_name == "Database":
            self.database_status_update.emit(status)

    @pyqtSlot(bool, str, dict)
    def _handle_sync_completed(self, success: bool, message: str, stats: dict):
        """Handle synchronization completion"""
        logger.info(f"Sync completed: Success={success}, Message='{message}'")
        sync_status = "success" if success else "failed"
        self.last_sync_status_update.emit(sync_status)
        self.sync_completed.emit(success, message, stats)
        self.ui_enable_request.emit(True)
        self.progress_update.emit(0)
        self.current_task_update.emit("Idle")

        if success:
            self.log_message.emit(
                "Data synchronization completed successfully.", "info"
            )
        else:
            self.log_message.emit(f"Data synchronization failed: {message}", "error")

    @pyqtSlot()
    def _handle_config_update(self):
        """Handle configuration update"""
        logger.info("Configuration updated, reloading...")
        self.config = self.config_manager.get_config()
        self.update_ui_with_config()
        self.test_all_connections()
        self.toggle_auto_sync(self.config.auto_sync_enabled)

    @pyqtSlot()
    def test_all_connections(self):
        """Test connections to SharePoint and Database"""
        logger.info("Testing all connections...")
        self.ui_enable_request.emit(False)
        self.current_task_update.emit("Testing connections...")

        sp_status = "disconnected"
        db_status = "disconnected"

        try:
            sp_connector = self.connection_manager.get_sharepoint_connector(self.config)
            sp_connected = sp_connector.test_connection() if sp_connector else False
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

        try:
            db_connector = self.connection_manager.get_database_connector(self.config)
            db_connected = db_connector.test_connection() if db_connector else False
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

        self.ui_enable_request.emit(True)
        self.current_task_update.emit("Idle")
        logger.info(
            f"Connection test completed. SharePoint: {sp_status}, Database: {db_status}"
        )

    @pyqtSlot(str)
    def run_full_sync(self, direction: str = "spo_to_sql"):
        """Initiate a full data synchronization"""
        logger.info(f"Initiating full sync in direction: {direction}")
        self.ui_enable_request.emit(False)
        self.current_task_update.emit(f"Running full sync ({direction})...")
        self.log_message.emit(f"Starting full sync: {direction}", "info")
        self.progress_update.emit(0)

        self.sync_engine.start_sync(direction)
        self.last_sync_status_update.emit("in_progress")

    @pyqtSlot(str, str, dict)
    def import_excel_data(self, file_path: str, table_name: str, column_mapping: dict):
        """Initiate Excel data import"""
        logger.info(f"Initiating Excel import from {file_path} to {table_name}")
        self.ui_enable_request.emit(False)
        self.current_task_update.emit("Importing Excel data...")
        self.log_message.emit(f"Starting Excel import: {file_path}", "info")
        self.progress_update.emit(0)
        self.excel_import_handler.start_import(file_path, table_name, column_mapping)

    @pyqtSlot(object)
    def _handle_excel_import_completed(self, result):
        """Handle Excel import completion"""
        success = getattr(result, "success", False)
        message = getattr(result, "message", "Import completed")

        logger.info(f"Excel import completed: Success={success}, Message='{message}'")
        self.ui_enable_request.emit(True)
        self.progress_update.emit(0)
        self.current_task_update.emit("Idle")

        if success:
            self.log_message.emit("Excel import completed successfully.", "info")
        else:
            self.log_message.emit(f"Excel import failed: {message}", "error")

    @pyqtSlot(str, object, str)
    def update_setting(self, key_path: str, value: Any, value_type: str):
        """Update a configuration setting"""
        logger.info(f"Updating setting: {key_path} = {value} ({value_type})")

        try:
            if value_type == "bool":
                converted_value = str(value).lower() in ("true", "1", "yes", "on")
            elif value_type == "int":
                converted_value = int(value)
            elif value_type == "float":
                converted_value = float(value)
            elif value_type == "json_str":
                import json

                converted_value = json.loads(value) if value else {}
            elif value_type == "dict":
                converted_value = value if isinstance(value, dict) else {}
            else:
                converted_value = value

            self.config_manager.update_setting(key_path, converted_value)
            self.log_message.emit(f"Setting '{key_path}' updated.", "info")

        except (ValueError, TypeError, json.JSONDecodeError) as e:
            self.log_message.emit(
                f"Failed to update setting '{key_path}': {e}", "error"
            )

    @pyqtSlot()
    def run_cache_cleanup(self):
        """Manually trigger cache cleanup"""
        logger.info("Manual cache cleanup initiated")
        self.auto_cache_manager.run_manual_cleanup()

    @pyqtSlot(bool)
    def toggle_auto_sync(self, enabled: bool):
        """Toggle automatic synchronization"""
        self.config_manager.update_setting("auto_sync_enabled", enabled)
        self.config.auto_sync_enabled = enabled
        self.auto_sync_status_update.emit(enabled)

        if enabled:
            interval_ms = self.config.sync_interval * 1000
            self.auto_sync_timer.start(interval_ms)
            logger.info(
                f"Auto-sync enabled with interval: {self.config.sync_interval} seconds"
            )
            self.log_message.emit(
                f"Auto-sync enabled. Next sync in {self.config.sync_interval} seconds.",
                "info",
            )
        else:
            self.auto_sync_timer.stop()
            logger.info("Auto-sync disabled")
            self.log_message.emit("Auto-sync disabled.", "info")

    @pyqtSlot()
    def _on_auto_sync_timeout(self):
        """Triggered by the auto-sync timer"""
        logger.info("Auto-sync triggered")
        direction = getattr(self.config, "auto_sync_direction", "spo_to_sql")
        self.run_full_sync(direction)

    @pyqtSlot()
    def update_ui_with_config(self):
        """Update UI elements with current configuration"""
        logger.debug("Updating UI with current configuration")
        self.sharepoint_status_update.emit("disconnected")
        self.database_status_update.emit("disconnected")
        self.last_sync_status_update.emit(
            getattr(self.config, "last_sync_status", "never")
        )
        self.auto_sync_status_update.emit(self.config.auto_sync_enabled)
        self.progress_update.emit(0)
        self.current_task_update.emit("Idle")

    def cleanup(self):
        """Perform comprehensive cleanup"""
        logger.info("Initiating AppController cleanup...")

        try:
            # Stop auto-sync timer
            if hasattr(self, "auto_sync_timer") and self.auto_sync_timer.isActive():
                self.auto_sync_timer.stop()
                self.auto_sync_timer.deleteLater()

            # Cleanup components
            if hasattr(self, "sync_engine"):
                self.sync_engine.cleanup()
            if hasattr(self, "connection_manager"):
                self.connection_manager.cleanup()
            if hasattr(self, "excel_import_handler"):
                self.excel_import_handler.cleanup()
            if hasattr(self, "auto_cache_manager"):
                self.auto_cache_manager.cleanup()

            logger.info("AppController cleanup completed")

        except Exception as e:
            logger.error(f"Error during AppController cleanup: {e}")
