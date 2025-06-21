# controller/app_controller.py - Fixed App Controller without debug prints
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
            # Import here to avoid circular imports
            import sys
            from pathlib import Path

            current_dir = Path(__file__).parent.absolute()
            project_root = current_dir.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))

            # Simple config access without complex manager
            try:
                from utils.config_manager import Config

                self.config = Config()  # Direct instantiation
                logger.info("Config created directly")
            except Exception as e:
                logger.error(f"Config creation failed: {e}")

                # Fallback config
                class FallbackConfig:
                    auto_sync_enabled = False
                    sync_interval = 600
                    auto_sync_direction = "spo_to_sql"

                self.config = FallbackConfig()

            # Create other components with error handling
            try:
                from .connection_manager import ConnectionManager

                self.connection_manager = ConnectionManager()
                logger.info("Connection manager created")
            except Exception as e:
                logger.error(f"Connection manager creation failed: {e}")
                self.connection_manager = None

            try:
                from .sync_engine import SyncEngine

                self.sync_engine = SyncEngine(self.config)
                logger.info("Sync engine created")
            except Exception as e:
                logger.error(f"Sync engine creation failed: {e}")
                self.sync_engine = None

            try:
                from utils.excel_import_handler import ExcelImportHandler

                self.excel_import_handler = ExcelImportHandler(self.config)
                logger.info("Excel import handler created")
            except Exception as e:
                logger.error(f"Excel import handler creation failed: {e}")
                self.excel_import_handler = None

            # Simple auto cache manager
            self.auto_cache_manager = None
            try:
                from utils.cache_cleaner import AutoCacheManager

                # Skip auto cache manager for now to avoid issues
                logger.info("Auto cache manager skipped")
            except Exception as e:
                logger.error(f"Auto cache manager creation failed: {e}")

            # Connect signals with error handling
            self._connect_signals()

            # Initialize data
            self._initialize_data()

            # Setup auto sync timer
            self.auto_sync_timer = QTimer(self)
            self.auto_sync_timer.timeout.connect(self._on_auto_sync_timeout)
            self.toggle_auto_sync(getattr(self.config, "auto_sync_enabled", False))

            logger.info("AppController initialized successfully.")

        except Exception as e:
            logger.error(f"AppController initialization error: {e}", exc_info=True)
            # Don't raise - continue with partial initialization

    def _connect_signals(self):
        """Connect signals between components"""
        try:
            # ConnectionManager signals
            if self.connection_manager and hasattr(
                self.connection_manager, "status_changed"
            ):
                self.connection_manager.status_changed.connect(
                    self._handle_service_status_change
                )
                self.connection_manager.log_message.connect(
                    lambda msg, level: self.log_message.emit(f"[CONN] {msg}", level)
                )

            # SyncEngine signals
            if self.sync_engine:
                if hasattr(self.sync_engine, "progress_updated"):
                    self.sync_engine.progress_updated.connect(
                        self.progress_updated.emit
                    )
                if hasattr(self.sync_engine, "sync_completed"):
                    self.sync_engine.sync_completed.connect(self._handle_sync_completed)
                if hasattr(self.sync_engine, "log_message"):
                    self.sync_engine.log_message.connect(
                        lambda msg, level: self.log_message.emit(f"[SYNC] {msg}", level)
                    )

            # ExcelImportHandler signals
            if self.excel_import_handler:
                if hasattr(self.excel_import_handler, "log_message"):
                    self.excel_import_handler.log_message.connect(
                        lambda msg, level: self.log_message.emit(
                            f"[EXCEL] {msg}", level
                        )
                    )
                if hasattr(self.excel_import_handler, "import_progress"):
                    self.excel_import_handler.import_progress.connect(
                        lambda p, msg: self.progress_update.emit(p)
                    )
                if hasattr(self.excel_import_handler, "import_completed"):
                    self.excel_import_handler.import_completed.connect(
                        self._handle_excel_import_completed
                    )

            logger.debug("AppController signals connected successfully")

        except Exception as e:
            logger.error(f"Error connecting AppController signals: {e}")

    def _initialize_data(self):
        """Initialize data for UI components"""
        try:
            self.update_ui_with_config()
            # Skip automatic connection testing to speed up startup
            logger.debug("AppController data initialized")
        except Exception as e:
            logger.error(f"Error initializing AppController data: {e}")

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
    def test_all_connections(self):
        """Test connections to SharePoint and Database"""
        logger.info("Testing all connections...")
        self.ui_enable_request.emit(False)
        self.current_task_update.emit("Testing connections...")

        sp_status = "disconnected"
        db_status = "disconnected"

        try:
            if self.connection_manager:
                sp_connector = self.connection_manager.get_sharepoint_connector(
                    self.config
                )
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
            if self.connection_manager:
                db_connector = self.connection_manager.get_database_connector(
                    self.config
                )
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
        if not self.sync_engine:
            self.log_message.emit("Sync engine not available", "error")
            return

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
        if not self.excel_import_handler:
            self.log_message.emit("Excel import handler not available", "error")
            return

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

            # Simple setting update without complex manager
            if hasattr(self.config, key_path):
                setattr(self.config, key_path, converted_value)

            self.log_message.emit(f"Setting '{key_path}' updated.", "info")

        except (ValueError, TypeError) as e:
            self.log_message.emit(
                f"Failed to update setting '{key_path}': {e}", "error"
            )

    @pyqtSlot()
    def run_cache_cleanup(self):
        """Manually trigger cache cleanup"""
        logger.info("Manual cache cleanup initiated")
        if self.auto_cache_manager:
            self.auto_cache_manager.run_manual_cleanup()
        else:
            self.log_message.emit("Cache cleanup not available", "warning")

    @pyqtSlot(bool)
    def toggle_auto_sync(self, enabled: bool):
        """Toggle automatic synchronization"""
        if hasattr(self.config, "auto_sync_enabled"):
            self.config.auto_sync_enabled = enabled
        self.auto_sync_status_update.emit(enabled)

        if enabled and hasattr(self.config, "sync_interval"):
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
        last_sync_status = getattr(self.config, "last_sync_status", "never")
        self.last_sync_status_update.emit(last_sync_status)
        auto_sync_enabled = getattr(self.config, "auto_sync_enabled", False)
        self.auto_sync_status_update.emit(auto_sync_enabled)
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
            if hasattr(self, "sync_engine") and self.sync_engine:
                self.sync_engine.cleanup()
            if hasattr(self, "connection_manager") and self.connection_manager:
                self.connection_manager.cleanup()
            if hasattr(self, "excel_import_handler") and self.excel_import_handler:
                self.excel_import_handler.cleanup()
            if hasattr(self, "auto_cache_manager") and self.auto_cache_manager:
                self.auto_cache_manager.cleanup()

            logger.info("AppController cleanup completed")

        except Exception as e:
            logger.error(f"Error during AppController cleanup: {e}")
