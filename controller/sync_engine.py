# controller/sync_engine.py - Enhanced with Robust Bidirectional Sync and Error Handling
from PyQt6.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from connectors.sharepoint_connector import SharePointConnector
from connectors.database_connector import DatabaseConnector
from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity
from utils.config_manager import Config  # Import Config for type hinting
import logging
import pandas as pd
from datetime import datetime, timezone  # Use timezone aware datetime for consistency
from typing import Tuple  # Added for Tuple type hint

logger = logging.getLogger(__name__)


class SyncWorker(QThread):
    """
    Dedicated QThread for performing data synchronization to prevent UI freezing.
    Supports SharePoint to SQL and SQL to SharePoint synchronization.
    """

    progress_updated = pyqtSignal(str, int, str)  # task_name, percentage, message
    sync_completed = pyqtSignal(bool, str, dict)  # success, message, stats
    log_message = pyqtSignal(str, str)  # message, level

    def __init__(self, config: Config, direction: str = "spo_to_sql", parent=None):
        super().__init__(parent)
        self.config = config
        self.direction = direction
        self._should_stop = False  # Internal flag for graceful stopping
        self.sync_stats = self._init_stats()
        self.sharepoint_connector = None
        self.database_connector = None
        logger.debug(f"SyncWorker initialized for direction: {self.direction}.")

    def _init_stats(self) -> dict:
        """Initializes synchronization statistics."""
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
        """
        Main execution loop for the sync worker.
        Performs synchronization based on the configured direction.
        """
        self.sync_stats = self._init_stats()
        self.sync_stats["start_time"] = datetime.now(timezone.utc)
        self.log_message.emit(
            f"🚀 Starting {self.direction} synchronization...", "info"
        )
        logger.info(f"SyncWorker started: {self.direction}")
        success = False
        message = ""

        try:
            # Initialize connectors outside the loop if they haven't been
            # This ensures they are available for the entire sync process
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
            message = f"A critical error occurred during sync: {e}"
            self.log_message.emit(f"❌ Critical Sync Error: {e}", "critical")
            logger.critical(message, exc_info=True)
            success = False
        finally:
            self.sync_stats["end_time"] = datetime.now(timezone.utc)
            if self.sync_stats["start_time"] and self.sync_stats["end_time"]:
                self.sync_stats["duration_seconds"] = (
                    self.sync_stats["end_time"] - self.sync_stats["start_time"]
                ).total_seconds()

            # Ensure connectors are closed
            if self.sharepoint_connector:
                self.sharepoint_connector.close()
            if self.database_connector:
                self.database_connector.close()

            self.sync_completed.emit(success, message, self.sync_stats)
            logger.info(f"SyncWorker finished. Success: {success}, Message: {message}")

    @handle_exceptions(ErrorCategory.SYNC, ErrorSeverity.HIGH)
    def _sync_sharepoint_to_sql(self) -> Tuple[bool, str]:  # Corrected type hint
        """Synchronizes data from SharePoint to SQL Server."""
        self.log_message.emit("Fetching data from SharePoint...", "info")
        logger.info("Starting SharePoint to SQL sync.")

        if self._should_stop:
            return False, "Sync cancelled by user."

        sharepoint_data = self.sharepoint_connector.read_list_items(
            self.config.sharepoint_list
        )
        if sharepoint_data is None:
            return False, "Failed to retrieve data from SharePoint."

        df_spo = pd.DataFrame(sharepoint_data)
        self.sync_stats["total_records"] = len(df_spo)
        self.log_message.emit(f"Found {len(df_spo)} items in SharePoint.", "info")
        logger.info(f"Retrieved {len(df_spo)} items from SharePoint.")

        if df_spo.empty:
            return True, "No new data to synchronize from SharePoint."

        # Apply column mapping
        spo_to_sql_mapping = self.config.sharepoint_to_sql_mapping
        df_spo_mapped = pd.DataFrame()

        # Validate mapping and apply
        for spo_col, sql_col in spo_to_sql_mapping.items():
            if spo_col in df_spo.columns:
                df_spo_mapped[sql_col] = df_spo[spo_col]
            else:
                self.log_message.emit(
                    f"⚠️ Warning: SharePoint column '{spo_col}' not found. Skipping.",
                    "warning",
                )
                logger.warning(
                    f"SharePoint column '{spo_col}' not found in data. Skipping mapping."
                )

        if df_spo_mapped.empty:
            return False, "No valid columns after applying SharePoint to SQL mapping."

        # Handle potential type conversions if necessary, especially for datetime or specific number formats
        # For example: df_spo_mapped['DateColumn'] = pd.to_datetime(df_spo_mapped['DateColumn'], errors='coerce')

        self.log_message.emit("Writing data to SQL Database...", "info")
        logger.info("Writing mapped data to SQL Database.")

        try:
            # Decide on insert/replace based on config
            if_exists_mode = "replace" if self.config.sql_truncate_before else "append"

            # Use self.database_connector.write_dataframe
            rows_written = self.database_connector.write_dataframe(
                df_spo_mapped,
                table_name=self.config.sql_table_name,
                if_exists=if_exists_mode,
                index=False,  # Do not write DataFrame index as a column
                create_table=self.config.sql_create_table,  # Pass create_table flag
            )

            self.sync_stats["records_added"] = (
                rows_written  # Assuming 'replace' or 'append' means added
            )
            message = (
                f"Successfully synced {rows_written} records from SharePoint to SQL."
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
    def _sync_sql_to_sharepoint(self) -> Tuple[bool, str]:  # Corrected type hint
        """Synchronizes data from SQL Server to SharePoint."""
        self.log_message.emit("Fetching data from SQL Database...", "info")
        logger.info("Starting SQL to SharePoint sync.")

        if self._should_stop:
            return False, "Sync cancelled by user."

        sql_data = self.database_connector.read_table(self.config.sql_table_name)
        if sql_data is None:
            return False, "Failed to retrieve data from SQL database."

        df_sql = pd.DataFrame(sql_data)
        self.sync_stats["total_records"] = len(df_sql)
        self.log_message.emit(f"Found {len(df_sql)} records in SQL.", "info")
        logger.info(f"Retrieved {len(df_sql)} records from SQL.")

        if df_sql.empty:
            return True, "No new data to synchronize from SQL."

        # Apply column mapping
        sql_to_spo_mapping = self.config.sql_to_sharepoint_mapping
        df_sql_mapped = pd.DataFrame()

        for sql_col, spo_col in sql_to_spo_mapping.items():
            if sql_col in df_sql.columns:
                df_sql_mapped[spo_col] = df_sql[
                    sql_col
                ]  # Map SQL column to SharePoint column
            else:
                self.log_message.emit(
                    f"⚠️ Warning: SQL column '{sql_col}' not found. Skipping.", "warning"
                )
                logger.warning(
                    f"SQL column '{sql_col}' not found in data. Skipping mapping."
                )

        if df_sql_mapped.empty:
            return False, "No valid columns after applying SQL to SharePoint mapping."

        self.log_message.emit("Writing data to SharePoint...", "info")
        logger.info("Writing mapped data to SharePoint.")

        try:
            # SharePoint update requires a list of dictionaries, not a DataFrame
            records_to_upload = df_sql_mapped.to_dict(orient="records")

            # Placeholder for actual update/add logic
            added_count, updated_count, error_count = 0, 0, 0

            # Assuming primary key for update is 'ID' for SharePoint or configurable
            sharepoint_list_items = self.sharepoint_connector.read_list_items(
                self.config.sharepoint_list, select_fields=["Id"]
            )
            existing_spo_ids = (
                {item["Id"] for item in sharepoint_list_items}
                if sharepoint_list_items
                else set()
            )

            for i, record in enumerate(records_to_upload):
                if self._should_stop:
                    return False, "Sync cancelled by user."

                self.progress_updated.emit(
                    "SQL to SharePoint",
                    int((i / len(records_to_upload)) * 100),
                    f"Processing record {i+1}/{len(records_to_upload)}",
                )

                spo_id = record.get(
                    "ID"
                )  # Assuming 'ID' is the SharePoint item ID after mapping

                if spo_id and spo_id in existing_spo_ids:
                    # Update existing item
                    if self.sharepoint_connector.update_list_item(
                        self.config.sharepoint_list, spo_id, record
                    ):
                        updated_count += 1
                    else:
                        error_count += 1
                else:
                    # Add new item
                    if self.sharepoint_connector.add_list_item(
                        self.config.sharepoint_list, record
                    ):
                        added_count += 1
                    else:
                        error_count += 1

            self.sync_stats["records_added"] = added_count
            self.sync_stats["records_updated"] = updated_count
            self.sync_stats["errors"] = error_count

            message = f"Successfully synced from SQL to SharePoint: Added {added_count}, Updated {updated_count}, Errors {error_count}."
            self.log_message.emit(f"✅ {message}", "success")
            logger.info(message)
            return True, message
        except Exception as e:
            message = f"Failed to write data to SharePoint: {e}"
            self.log_message.emit(f"❌ {message}", "error")
            logger.error(message, exc_info=True)
            return False, message

    def stop(self):
        """Sets the internal flag to stop the sync process gracefully."""
        self._should_stop = True
        logger.info("SyncWorker received stop signal. Will terminate gracefully.")


class SyncEngine(QObject):
    """
    Orchestrates data synchronization between SharePoint and SQL Database.
    Manages SyncWorker threads and emits signals for UI updates.
    """

    # Signals for UI updates
    progress_updated = pyqtSignal(str, int, str)  # task_name, percentage, message
    sync_completed = pyqtSignal(bool, str, dict)  # success, message, stats
    log_message = pyqtSignal(str, str)  # message, level
    current_task_update = pyqtSignal(str)  # To update a simple task description label

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.sync_worker = None
        logger.info("SyncEngine initialized.")

    @pyqtSlot(str)
    @handle_exceptions(ErrorCategory.SYNC, ErrorSeverity.HIGH)
    def start_sync(self, direction: str):
        """Starts the synchronization process in a new thread."""
        if self.sync_worker and self.sync_worker.isRunning():
            self.log_message.emit("Sync is already in progress.", "warning")
            logger.warning("Attempted to start sync while another is running.")
            return

        # Validate configuration before starting sync
        if not self._validate_sync_config(direction):
            self.sync_completed.emit(False, "Sync configuration is invalid.", {})
            return

        self.current_task_update.emit(
            f"Starting {direction.replace('_', ' ').title()} Sync..."
        )
        self.log_message.emit(f"Initiating data sync: {direction}", "info")

        self.progress_updated.emit(
            f"{direction.replace('_', ' ').title()} Sync", 0, "Initializing..."
        )

        self.sync_worker = SyncWorker(self.config, direction)

        # Connect worker signals to SyncEngine signals to pass them to AppController
        self.sync_worker.progress_updated.connect(self.progress_updated.emit)
        self.sync_worker.sync_completed.connect(self.sync_completed.emit)
        self.sync_worker.log_message.connect(self.log_message.emit)

        self.sync_worker.start()
        logger.info(f"SyncWorker thread started for direction: {direction}.")

    @pyqtSlot()
    @handle_exceptions(ErrorCategory.SYNC, ErrorSeverity.MEDIUM)
    def stop_sync(self):
        """Stops the currently running synchronization process."""
        if self.sync_worker and self.sync_worker.isRunning():
            self.log_message.emit("Stopping synchronization...", "warning")
            self.current_task_update.emit("Stopping Sync...")
            self.sync_worker.stop()
            # It's generally good practice to wait for the thread to finish
            # but for UI responsiveness, we might not block here.
            # The worker's run() method will handle its own graceful exit.
            logger.info("SyncWorker stop method called.")
        else:
            self.log_message.emit("No active synchronization to stop.", "info")
            logger.info("No active sync to stop.")

    @handle_exceptions(ErrorCategory.CONFIG, ErrorSeverity.HIGH)
    def _validate_sync_config(self, direction: str) -> bool:
        """
        Validates the configuration settings required for synchronization.
        Emits log messages for errors.
        """
        errors = []

        # General checks
        if not self.config.sharepoint_site or not self.config.sharepoint_list:
            errors.append("SharePoint site URL or list name is missing.")
        if not (
            self.config.sharepoint_client_id
            and self.config.sharepoint_client_secret
            and self.config.tenant_id
        ):
            errors.append(
                "SharePoint client ID, client secret, or tenant ID is missing for authentication."
            )

        db_type = self.config.database_type.lower()
        if db_type == "sqlserver":
            if not (
                self.config.sql_server
                and self.config.sql_database
                and self.config.sql_username
                and self.config.sql_password
            ):
                errors.append(
                    "SQL Server connection details (server, database, username, password) are incomplete."
                )
            if not self.config.sql_table_name:
                errors.append("SQL table name is not specified.")
        elif db_type == "sqlite":
            if not self.config.sqlite_file:
                errors.append("SQLite database file path is not specified.")
            if not self.config.sqlite_table_name:
                errors.append("SQLite table name is not specified.")
        else:
            errors.append(
                f"Unsupported database type configured: {self.config.database_type}"
            )

        # Direction-specific mapping checks
        if direction == "spo_to_sql":
            if not self.config.sharepoint_to_sql_mapping:
                errors.append("SharePoint to SQL field mapping is empty or invalid.")
            elif not isinstance(self.config.sharepoint_to_sql_mapping, dict) or not all(
                isinstance(k, str) and isinstance(v, str)
                for k, v in self.config.sharepoint_to_sql_mapping.items()
            ):
                errors.append(
                    "SharePoint to SQL field mapping is not a valid dictionary."
                )

        elif direction == "sql_to_spo":
            if not self.config.sql_to_sharepoint_mapping:
                errors.append("SQL to SharePoint field mapping is empty or invalid.")
            elif not isinstance(self.config.sql_to_sharepoint_mapping, dict) or not all(
                isinstance(k, str) and isinstance(v, str)
                for k, v in self.config.sql_to_sharepoint_mapping.items()
            ):
                errors.append(
                    "SQL to SharePoint field mapping is not a valid dictionary."
                )

        else:
            errors.append(f"Unknown sync direction: {direction}")

        if errors:
            for error_msg in errors:
                self.log_message.emit(f"⚠️ Config Error: {error_msg}", "error")
                logger.error(f"Config validation error: {error_msg}")
            return False

        logger.info(f"Configuration for '{direction}' sync validated successfully.")
        return True

    def cleanup(self):
        """Performs cleanup for SyncEngine."""
        if self.sync_worker and self.sync_worker.isRunning():
            self.sync_worker.stop()
            self.sync_worker.wait(5000)  # Give it some time to stop
            if self.sync_worker.isRunning():
                logger.warning(
                    "SyncWorker did not terminate within timeout during SyncEngine cleanup."
                )
        # Disconnect all signals
        try:
            self.progress_updated.disconnect()
            self.sync_completed.disconnect()
            self.log_message.disconnect()
            self.current_task_update.disconnect()  # Disconnect new signal
            logger.info("Disconnected SyncEngine signals.")
        except TypeError as e:
            logger.debug(
                f"Attempted to disconnect non-connected SyncEngine signal: {e}"
            )
        except Exception as e:
            logger.warning(f"Error during SyncEngine signal disconnection: {e}")
        logger.info("SyncEngine cleanup completed.")
