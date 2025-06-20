# utils/excel_import_handler.py - Enhanced Excel Import Handler
import pandas as pd
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot  # Added QObject and pyqtSlot
from typing import Dict, Optional
import logging
import os

from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity
from connectors.database_connector import DatabaseConnector
from utils.config_manager import Config  # For type hinting

logger = logging.getLogger(__name__)


class ExcelImportResult:
    def __init__(self):
        self.success = False
        self.message = ""
        self.total_rows_read = 0
        self.rows_imported_to_db = 0
        self.errors = []
        self.file_path = ""
        self.table_name = ""


class ExcelImportHandler(QObject):
    """
    Handles the import of data from Excel files into the database.
    Operates in a separate thread to prevent UI freezing.
    """

    import_progress = pyqtSignal(int, str)  # percentage, message
    import_completed = pyqtSignal(object)  # ExcelImportResult object
    log_message = pyqtSignal(str, str)  # message, level

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.db_connector: Optional[DatabaseConnector] = None
        self._should_stop = False  # Flag for graceful stopping
        logger.info("ExcelImportHandler initialized.")

    @pyqtSlot(str, str, dict)
    @handle_exceptions(
        ErrorCategory.DATA_IMPORT,
        ErrorSeverity.CRITICAL,
        # Removed 'user_message' as it's not a direct parameter for the decorator
    )
    def start_import(
        self, file_path: str, table_name: str, column_mapping: Dict[str, str]
    ):
        """
        Starts the Excel import process in a new thread.
        file_path: Path to the Excel file.
        table_name: The target database table name.
        column_mapping: A dictionary mapping Excel column names to DB column names.
        """
        if not file_path or not os.path.exists(file_path):
            result = ExcelImportResult()
            result.message = "Invalid Excel file path provided."
            result.success = False
            self.log_message.emit(result.message, "error")
            self.import_completed.emit(result)
            logger.error(f"Excel import failed: {result.message}")
            return

        if not table_name:
            result = ExcelImportResult()
            result.message = "Target database table name is not specified."
            result.success = False
            self.log_message.emit(result.message, "error")
            self.import_completed.emit(result)
            logger.error(f"Excel import failed: {result.message}")
            return

        if not column_mapping:
            result = ExcelImportResult()
            result.message = "Column mapping is empty. Please provide Excel column to Database column mapping."
            result.success = False
            self.log_message.emit(result.message, "error")
            self.import_completed.emit(result)
            logger.error(f"Excel import failed: {result.message}")
            return

        self._should_stop = False
        result = ExcelImportResult()
        result.file_path = file_path
        result.table_name = table_name

        self.log_message.emit(f"🚀 Starting Excel import from: {file_path}", "info")
        self.import_progress.emit(0, "Initializing import...")
        logger.info(
            f"Excel import started for '{file_path}' into table '{table_name}'."
        )

        try:
            self.db_connector = DatabaseConnector(self.config)

            # Read Excel file based on extension
            df = self._read_excel_file(file_path)
            if df is None:
                result.message = f"Failed to read Excel file: {file_path}"
                result.success = False
                self.import_completed.emit(result)
                logger.error(result.message)
                return

            result.total_rows_read = len(df)
            self.log_message.emit(f"Read {len(df)} rows from Excel file.", "info")
            self.import_progress.emit(10, "Applying column mapping...")

            # Apply column mapping
            df_mapped = pd.DataFrame()
            missing_excel_cols = []
            for excel_col, db_col in column_mapping.items():
                if excel_col in df.columns:
                    df_mapped[db_col] = df[excel_col]
                else:
                    missing_excel_cols.append(excel_col)
                    self.log_message.emit(
                        f"⚠️ Warning: Excel column '{excel_col}' not found. Skipping.",
                        "warning",
                    )
                    logger.warning(
                        f"Excel column '{excel_col}' not found in source data."
                    )

            if missing_excel_cols:
                result.errors.append(
                    f"Missing Excel columns: {', '.join(missing_excel_cols)}"
                )

            if df_mapped.empty:
                result.message = "No valid data after applying column mapping. Check your Excel file and mapping."
                result.success = False
                self.log_message.emit(result.message, "error")
                self.import_completed.emit(result)
                logger.error(result.message)
                return

            self.import_progress.emit(50, "Writing data to database...")
            self.log_message.emit(
                f"Writing {len(df_mapped)} mapped rows to database table '{table_name}'...",
                "info",
            )

            # Write to database (use 'append' or 'replace' based on config or user choice)
            # For simplicity, assuming 'append' or 'replace' logic already handled by connector if_exists
            rows_written = self.db_connector.write_dataframe(
                df=df_mapped,
                table_name=table_name,
                if_exists="append",  # Or "replace" based on your needs
                index=False,
                create_table=True,  # Assume we want to create table if it doesn't exist
            )

            result.rows_imported_to_db = rows_written
            result.success = True
            result.message = (
                f"Successfully imported {rows_written} rows from Excel to database."
            )
            self.log_message.emit(f"✅ {result.message}", "success")
            self.import_progress.emit(100, "Import completed!")

        except Exception as e:
            result.success = False
            result.message = f"An error occurred during Excel import: {e}"
            result.errors.append(str(e))
            self.log_message.emit(f"❌ {result.message}", "critical")
            logger.critical(f"Critical Excel import error: {e}", exc_info=True)
        finally:
            if self.db_connector:
                self.db_connector.close()
            self.import_completed.emit(result)
            logger.info("Excel import process finished.")

    def _read_excel_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """Reads an Excel file into a pandas DataFrame."""
        try:
            if file_path.endswith(".xlsx"):
                df = pd.read_excel(file_path, engine="openpyxl")
            elif file_path.endswith(".xls"):
                df = pd.read_excel(file_path, engine="xlrd")  # xlrd is needed for .xls
            else:
                self.log_message.emit(
                    "Unsupported file format. Please use .xlsx or .xls.", "error"
                )
                logger.error(f"Unsupported Excel file format: {file_path}")
                return None
            return df
        except FileNotFoundError:
            self.log_message.emit(f"Excel file not found: {file_path}", "error")
            logger.error(f"Excel file not found: {file_path}")
            return None
        except Exception as e:
            self.log_message.emit(f"Error reading Excel file: {e}", "error")
            logger.error(f"Error reading Excel file '{file_path}': {e}", exc_info=True)
            return None

    @pyqtSlot()
    def stop_import(self):
        """Sets the internal flag to stop the import process gracefully."""
        self._should_stop = True
        self.log_message.emit(
            "Excel import received stop signal. Will attempt to terminate.", "warning"
        )
        logger.info("ExcelImportHandler received stop signal.")

    def cleanup(self):
        """Performs cleanup for ExcelImportHandler."""
        logger.info("ExcelImportHandler cleanup initiated.")
        if self.db_connector:
            self.db_connector.close()
            self.db_connector = None
            logger.debug("Database connector closed in ExcelImportHandler cleanup.")
        # Disconnect signals
        try:
            self.import_progress.disconnect()
            self.import_completed.disconnect()
            self.log_message.disconnect()
            logger.info("Disconnected ExcelImportHandler signals.")
        except TypeError as e:
            logger.debug(
                f"Attempted to disconnect non-connected ExcelImportHandler signal: {e}"
            )
        except Exception as e:
            logger.warning(f"Error during ExcelImportHandler signal disconnection: {e}")
        logger.info("ExcelImportHandler cleanup completed.")
