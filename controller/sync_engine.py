# controller/sync_engine.py - Fixed Sync Engine
from PyQt6.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import pandas as pd
from datetime import datetime, timezone
from typing import Tuple, Optional
import logging

from connectors.sharepoint_connector import SharePointConnector
from connectors.database_connector import DatabaseConnector
from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity
from utils.config_manager import Config

logger = logging.getLogger(__name__)


class SyncWorker(QThread):
    """
    Dedicated QThread for performing data synchronization.
    Supports SharePoint to SQL and SQL to SharePoint synchronization.
    """

    progress_updated = pyqtSignal(str, int, str)  # task_name, percentage, message
    sync_completed = pyqtSignal(bool, str, dict)  # success, message, stats
    log_message = pyqtSignal(str, str)  # message, level

    def __init__(self, config: Config, direction: str = "spo_to_sql", parent=None):
        super().__init__(parent)
        self.config = config
        self.direction = direction
        self._should_stop = False
        self.sync_stats = self._init_stats()
        self.sharepoint_connector = None
        self.database_connector = None
        logger.debug(f"SyncWorker initialized for direction: {self.direction}")

    def _init_stats(self) -> dict:
        """Initialize synchronization statistics"""
        return {
            "total_records": 0,
            "records_added": 0,
            "records_updated": 0,
            "errors": 0,
            "duration_seconds": 0.0,
            "start_time": None,
            "end_time": None,
            "sync_direction": self.direction,
        }

    def run(self):
        """Main execution loop for the sync worker"""
        self.sync_stats = self._init_stats()
        self.sync_stats["start_time"] = datetime.now(timezone.utc)
        self.log_message.emit(
            f"🚀 Starting {self.direction} synchronization...", "info"
        )
        logger.info(f"SyncWorker started: {self.direction}")

        success = False
        message = ""

        try:
            # Initialize connectors
            self.sharepoint_connector = SharePointConnector(self.config)
            self.database_connector = DatabaseConnector(self.config)

            if self.direction == "spo_to_sql":
                success, message = self._sync_sharepoint_to_sql()
            elif self.direction == "sql_to_spo":
                success, message = self._sync_sql_to_sharepoint()
            else:
                message = f"Invalid sync direction: {self.direction}"
                self.log_message.emit(f"❌ Error: {message}", "error")
                logger.error(message)

        except Exception as e:
            message = f"Critical error during sync: {e}"
            self.log_message.emit(f"❌ Critical Sync Error: {e}", "critical")
            logger.critical(message, exc_info=True)
            success = False
        finally:
            self.sync_stats["end_time"] = datetime.now(timezone.utc)
            if self.sync_stats["start_time"] and self.sync_stats["end_time"]:
                self.sync_stats["duration_seconds"] = (
                    self.sync_stats["end_time"] - self.sync_stats["start_time"]
                ).total_seconds()

            # Cleanup connectors
            if self.sharepoint_connector:
                self.sharepoint_connector.close()
            if self.database_connector:
                self.database_connector.close()

            self.sync_completed.emit(success, message, self.sync_stats)
            logger.info(f"SyncWorker finished. Success: {success}")

    @handle_exceptions(ErrorCategory.SYNC, ErrorSeverity.HIGH)
    def _sync_sharepoint_to_sql(self) -> Tuple[bool, str]:
        """Synchronize data from SharePoint to SQL Server"""
        self.log_message.emit("📥 Fetching data from SharePoint...", "info")
        logger.info("Starting SharePoint to SQL sync")

        if self._should_stop:
            return False, "Sync cancelled by user"

        # Progress update
        self.progress_updated.emit(
            "SharePoint to SQL", 10, "Connecting to SharePoint..."
        )

        # Get SharePoint data
        sharepoint_data = self.sharepoint_connector.read_list_items(
            self.config.sharepoint_list
        )
        if sharepoint_data is None:
            return False, "Failed to retrieve data from SharePoint"

        df_spo = pd.DataFrame(sharepoint_data)
        self.sync_stats["total_records"] = len(df_spo)
        self.log_message.emit(f"📊 Found {len(df_spo)} items in SharePoint", "info")
        logger.info(f"Retrieved {len(df_spo)} items from SharePoint")

        if df_spo.empty:
            return True, "No data to synchronize from SharePoint"

        self.progress_updated.emit(
            "SharePoint to SQL", 30, "Applying column mapping..."
        )

        # Apply column mapping
        spo_to_sql_mapping = self.config.sharepoint_to_sql_mapping
        if not spo_to_sql_mapping:
            return False, "SharePoint to SQL mapping is not configured"

        df_spo_mapped = pd.DataFrame()
        for spo_col, sql_col in spo_to_sql_mapping.items():
            if spo_col in df_spo.columns:
                df_spo_mapped[sql_col] = df_spo[spo_col]
            else:
                self.log_message.emit(
                    f"⚠️ Warning: SharePoint column '{spo_col}' not found", "warning"
                )

        if df_spo_mapped.empty:
            return False, "No valid columns after applying mapping"

        self.progress_updated.emit("SharePoint to SQL", 60, "Writing to database...")
        self.log_message.emit("💾 Writing data to SQL Database...", "info")

        try:
            # Determine write mode
            if_exists_mode = "replace" if self.config.sql_truncate_before else "append"

            rows_written = self.database_connector.write_dataframe(
                df_spo_mapped,
                table_name=self.config.sql_table_name,
                if_exists=if_exists_mode,
                index=False,
                create_table=self.config.sql_create_table,
            )

            self.sync_stats["records_added"] = rows_written
            self.progress_updated.emit("SharePoint to SQL", 100, "Sync completed!")

            message = (
                f"Successfully synced {rows_written} records from SharePoint to SQL"
            )
            self.log_message.emit(f"✅ {message}", "success")
            logger.info(message)
            return True, message

        except Exception as e:
            message = f"Failed to write data to SQL database: {e}"
            self.log_message.emit(f"❌ {message}", "error")
            logger.error(message, exc_info=True)
            return False, message

    @handle_exceptions(ErrorCategory.SYNC, ErrorSeverity.HIGH)
    def _sync_sql_to_sharepoint(self) -> Tuple[bool, str]:
        """Synchronize data from SQL Server to SharePoint"""
        self.log_message.emit("📤 Fetching data from SQL Database...", "info")
        logger.info("Starting SQL to SharePoint sync")

        if self._should_stop:
            return False, "Sync cancelled by user"

        self.progress_updated.emit("SQL to SharePoint", 10, "Reading from database...")

        # Get SQL data
        sql_data = self.database_connector.read_table(self.config.sql_table_name)
        if sql_data is None:
            return False, "Failed to retrieve data from SQL database"

        df_sql = pd.DataFrame(sql_data)
        self.sync_stats["total_records"] = len(df_sql)
        self.log_message.emit(f"📊 Found {len(df_sql)} records in SQL", "info")

        if df_sql.empty:
            return True, "No data to synchronize from SQL"

        self.progress_updated.emit(
            "SQL to SharePoint", 30, "Applying column mapping..."
        )

        # Apply column mapping
        sql_to_spo_mapping = self.config.sql_to_sharepoint_mapping
        if not sql_to_spo_mapping:
            return False, "SQL to SharePoint mapping is not configured"

        df_sql_mapped = pd.DataFrame()
        for sql_col, spo_col in sql_to_spo_mapping.items():
            if sql_col in df_sql.columns:
                df_sql_mapped[spo_col] = df_sql[sql_col]
            else:
                self.log_message.emit(
                    f"⚠️ Warning: SQL column '{sql_col}' not found", "warning"
                )

        if df_sql_mapped.empty:
            return False, "No valid columns after applying mapping"

        self.progress_updated.emit("SQL to SharePoint", 60, "Writing to SharePoint...")
        self.log_message.emit("📤 Writing data to SharePoint...", "info")

        try:
            # Convert to records for SharePoint
            records_to_upload = df_sql_mapped.to_dict(orient="records")
            added_count = 0
            error_count = 0

            # Get existing SharePoint items for update logic
            existing_items = self.sharepoint_connector.read_list_items(
                self.config.sharepoint_list, select_fields=["Id"]
            )
            existing_ids = (
                {item["Id"] for item in existing_items} if existing_items else set()
            )

            total_records = len(records_to_upload)
            for i, record in enumerate(records_to_upload):
                if self._should_stop:
                    return False, "Sync cancelled by user"

                progress = 60 + int((i / total_records) * 30)  # 60% to 90%
                self.progress_updated.emit(
                    "SQL to SharePoint",
                    progress,
                    f"Processing record {i+1}/{total_records}",
                )

                # For simplicity, always add new items (no update logic for now)
                if self.sharepoint_connector.add_list_item(
                    self.config.sharepoint_list, record
                ):
                    added_count += 1
                else:
                    error_count += 1

            self.sync_stats["records_added"] = added_count
            self.sync_stats["errors"] = error_count
            self.progress_updated.emit("SQL to SharePoint", 100, "Sync completed!")

            message = f"Successfully synced to SharePoint: Added {added_count}, Errors {error_count}"
            self.log_message.emit(f"✅ {message}", "success")
            logger.info(message)
            return True, message

        except Exception as e:
            message = f"Failed to write data to SharePoint: {e}"
            self.log_message.emit(f"❌ {message}", "error")
            logger.error(message, exc_info=True)
            return False, message

    def stop(self):
        """Set flag to stop sync process gracefully"""
        self._should_stop = True
        logger.info("SyncWorker received stop signal")


class SyncEngine(QObject):
    """
    Orchestrates data synchronization between SharePoint and SQL Database.
    Manages SyncWorker threads and emits signals for UI updates.
    """

    progress_updated = pyqtSignal(str, int, str)  # task_name, percentage, message
    sync_completed = pyqtSignal(bool, str, dict)  # success, message, stats
    log_message = pyqtSignal(str, str)  # message, level
    current_task_update = pyqtSignal(str)  # task description

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.sync_worker: Optional[SyncWorker] = None
        logger.info("SyncEngine initialized")

    @pyqtSlot(str)
    @handle_exceptions(ErrorCategory.SYNC, ErrorSeverity.HIGH)
    def start_sync(self, direction: str):
        """Start synchronization process in a new thread"""
        if self.sync_worker and self.sync_worker.isRunning():
            self.log_message.emit("Sync is already in progress", "warning")
            logger.warning("Attempted to start sync while another is running")
            return

        # Validate configuration
        if not self._validate_sync_config(direction):
            self.sync_completed.emit(False, "Sync configuration is invalid", {})
            return

        self.current_task_update.emit(
            f"Starting {direction.replace('_', ' ').title()} Sync..."
        )
        self.log_message.emit(f"Initiating data sync: {direction}", "info")
        self.progress_updated.emit(
            f"{direction.replace('_', ' ').title()} Sync", 0, "Initializing..."
        )

        self.sync_worker = SyncWorker(self.config, direction)

        # Connect worker signals
        self.sync_worker.progress_updated.connect(self.progress_updated.emit)
        self.sync_worker.sync_completed.connect(self.sync_completed.emit)
        self.sync_worker.log_message.connect(self.log_message.emit)

        self.sync_worker.start()
        logger.info(f"SyncWorker thread started for direction: {direction}")

    @pyqtSlot()
    @handle_exceptions(ErrorCategory.SYNC, ErrorSeverity.MEDIUM)
    def stop_sync(self):
        """Stop currently running synchronization"""
        if self.sync_worker and self.sync_worker.isRunning():
            self.log_message.emit("Stopping synchronization...", "warning")
            self.current_task_update.emit("Stopping Sync...")
            self.sync_worker.stop()
            logger.info("SyncWorker stop method called")
        else:
            self.log_message.emit("No active synchronization to stop", "info")

    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.HIGH)
    def _validate_sync_config(self, direction: str) -> bool:
        """Validate configuration settings required for synchronization"""
        errors = []

        # General checks
        if not self.config.sharepoint_site or not self.config.sharepoint_list:
            errors.append("SharePoint site URL or list name is missing")

        if not (
            self.config.sharepoint_client_id
            and self.config.sharepoint_client_secret
            and self.config.tenant_id
        ):
            errors.append("SharePoint authentication credentials are missing")

        # Database checks
        db_type = self.config.database_type.lower()
        if db_type == "sqlserver":
            if not (
                self.config.sql_server
                and self.config.sql_database
                and self.config.sql_username
                and self.config.sql_password
            ):
                errors.append("SQL Server connection details are incomplete")
            if not self.config.sql_table_name:
                errors.append("SQL table name is not specified")
        elif db_type == "sqlite":
            if not self.config.sqlite_file:
                errors.append("SQLite database file path is not specified")
            if not self.config.sqlite_table_name:
                errors.append("SQLite table name is not specified")
        else:
            errors.append(f"Unsupported database type: {self.config.database_type}")

        # Direction-specific mapping checks
        if direction == "spo_to_sql":
            if not self.config.sharepoint_to_sql_mapping:
                errors.append("SharePoint to SQL field mapping is empty")
            elif not isinstance(self.config.sharepoint_to_sql_mapping, dict):
                errors.append("SharePoint to SQL field mapping is not valid")

        elif direction == "sql_to_spo":
            if not self.config.sql_to_sharepoint_mapping:
                errors.append("SQL to SharePoint field mapping is empty")
            elif not isinstance(self.config.sql_to_sharepoint_mapping, dict):
                errors.append("SQL to SharePoint field mapping is not valid")
        else:
            errors.append(f"Unknown sync direction: {direction}")

        if errors:
            for error_msg in errors:
                self.log_message.emit(f"⚠️ Config Error: {error_msg}", "error")
                logger.error(f"Config validation error: {error_msg}")
            return False

        logger.info(f"Configuration for '{direction}' sync validated successfully")
        return True

    def cleanup(self):
        """Perform cleanup for SyncEngine"""
        logger.info("SyncEngine cleanup initiated")

        if self.sync_worker and self.sync_worker.isRunning():
            self.sync_worker.stop()
            self.sync_worker.wait(5000)  # Wait up to 5 seconds
            if self.sync_worker.isRunning():
                logger.warning("SyncWorker did not terminate within timeout")
                self.sync_worker.terminate()

        # Disconnect signals
        try:
            self.progress_updated.disconnect()
            self.sync_completed.disconnect()
            self.log_message.disconnect()
            self.current_task_update.disconnect()
            logger.info("SyncEngine signals disconnected")
        except (TypeError, RuntimeError):
            pass  # Signals already disconnected

        logger.info("SyncEngine cleanup completed")
