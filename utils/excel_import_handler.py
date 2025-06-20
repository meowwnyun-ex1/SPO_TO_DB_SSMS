# utils/excel_import_handler.py - Fixed Excel Import Handler
import pandas as pd
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from typing import Dict, Optional
import logging
import os
from pathlib import Path

from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity
from connectors.database_connector import DatabaseConnector
from utils.config_manager import Config

logger = logging.getLogger(__name__)


class ExcelImportResult:
    """Results from Excel import operation"""

    def __init__(self):
        self.success = False
        self.message = ""
        self.total_rows_read = 0
        self.rows_imported_to_db = 0
        self.errors = []
        self.file_path = ""
        self.table_name = ""
        self.column_mapping = {}
        self.duration_seconds = 0.0


class ExcelImportWorker(QThread):
    """Worker thread for Excel import operations"""

    progress_updated = pyqtSignal(int, str)  # percentage, message
    import_completed = pyqtSignal(object)  # ExcelImportResult
    log_message = pyqtSignal(str, str)  # message, level

    def __init__(
        self,
        config: Config,
        file_path: str,
        table_name: str,
        column_mapping: Dict[str, str],
    ):
        super().__init__()
        self.config = config
        self.file_path = file_path
        self.table_name = table_name
        self.column_mapping = column_mapping
        self._should_stop = False
        self.db_connector = None

    def run(self):
        """Main execution method for import worker"""
        import time

        start_time = time.time()

        result = ExcelImportResult()
        result.file_path = self.file_path
        result.table_name = self.table_name
        result.column_mapping = self.column_mapping

        try:
            self.log_message.emit(
                f"🚀 Starting Excel import from: {self.file_path}", "info"
            )
            self.progress_updated.emit(0, "Initializing import...")

            # Validate file
            if not self._validate_file():
                result.message = f"File validation failed: {self.file_path}"
                result.success = False
                self.import_completed.emit(result)
                return

            self.progress_updated.emit(10, "Reading Excel file...")

            # Read Excel file
            df = self._read_excel_file()
            if df is None:
                result.message = f"Failed to read Excel file: {self.file_path}"
                result.success = False
                self.import_completed.emit(result)
                return

            result.total_rows_read = len(df)
            self.log_message.emit(f"📊 Read {len(df)} rows from Excel file", "info")

            if self._should_stop:
                result.message = "Import cancelled by user"
                result.success = False
                self.import_completed.emit(result)
                return

            self.progress_updated.emit(30, "Applying column mapping...")

            # Apply column mapping
            df_mapped = self._apply_column_mapping(df)
            if df_mapped is None or df_mapped.empty:
                result.message = "No valid data after applying column mapping"
                result.success = False
                self.import_completed.emit(result)
                return

            self.progress_updated.emit(60, "Connecting to database...")

            # Initialize database connector
            self.db_connector = DatabaseConnector(self.config)

            if not self.db_connector.test_connection():
                result.message = "Failed to connect to database"
                result.success = False
                self.import_completed.emit(result)
                return

            self.progress_updated.emit(80, "Writing data to database...")
            self.log_message.emit(
                f"💾 Writing {len(df_mapped)} rows to database table '{self.table_name}'",
                "info",
            )

            # Write to database
            rows_written = self.db_connector.write_dataframe(
                df=df_mapped,
                table_name=self.table_name,
                if_exists="append",  # Default to append mode
                index=False,
                create_table=True,
            )

            result.rows_imported_to_db = rows_written
            result.success = True
            result.message = (
                f"Successfully imported {rows_written} rows from Excel to database"
            )
            result.duration_seconds = time.time() - start_time

            self.progress_updated.emit(100, "Import completed!")
            self.log_message.emit(f"✅ {result.message}", "success")

        except Exception as e:
            result.success = False
            result.message = f"Error during Excel import: {e}"
            result.errors.append(str(e))
            result.duration_seconds = time.time() - start_time
            self.log_message.emit(f"❌ {result.message}", "error")
            logger.error(f"Excel import error: {e}", exc_info=True)
        finally:
            if self.db_connector:
                self.db_connector.close()
            self.import_completed.emit(result)

    def _validate_file(self) -> bool:
        """Validate Excel file before processing"""
        try:
            file_path = Path(self.file_path)

            # Check if file exists
            if not file_path.exists():
                self.log_message.emit(f"File not found: {self.file_path}", "error")
                return False

            # Check file extension
            if file_path.suffix.lower() not in [".xlsx", ".xls"]:
                self.log_message.emit(
                    "Unsupported file format. Please use .xlsx or .xls", "error"
                )
                return False

            # Check file size (limit to 50MB)
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > 50:
                self.log_message.emit(
                    f"File too large: {file_size_mb:.1f}MB. Maximum size is 50MB",
                    "error",
                )
                return False

            # Check if file is readable
            try:
                with open(file_path, "rb") as f:
                    f.read(1024)  # Try to read first 1KB
            except PermissionError:
                self.log_message.emit(
                    "Permission denied. File may be open in another application",
                    "error",
                )
                return False

            return True

        except Exception as e:
            self.log_message.emit(f"File validation error: {e}", "error")
            return False

    def _read_excel_file(self) -> Optional[pd.DataFrame]:
        """Read Excel file into pandas DataFrame"""
        try:
            file_path = Path(self.file_path)

            # Choose appropriate engine based on file extension
            if file_path.suffix.lower() == ".xlsx":
                df = pd.read_excel(self.file_path, engine="openpyxl")
            elif file_path.suffix.lower() == ".xls":
                df = pd.read_excel(self.file_path, engine="xlrd")
            else:
                self.log_message.emit("Unsupported file format", "error")
                return None

            # Basic data cleaning
            # Remove completely empty rows
            df = df.dropna(how="all")

            # Strip whitespace from string columns
            for col in df.select_dtypes(include=["object"]).columns:
                df[col] = df[col].astype(str).str.strip()

            # Replace 'nan' strings with actual NaN
            df = df.replace("nan", pd.NA)

            logger.info(
                f"Successfully read Excel file: {len(df)} rows, {len(df.columns)} columns"
            )
            return df

        except Exception as e:
            self.log_message.emit(f"Error reading Excel file: {e}", "error")
            logger.error(
                f"Error reading Excel file '{self.file_path}': {e}", exc_info=True
            )
            return None

    def _apply_column_mapping(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Apply column mapping from Excel columns to database columns"""
        try:
            if not self.column_mapping:
                self.log_message.emit("No column mapping provided", "warning")
                return df  # Return original DataFrame if no mapping

            df_mapped = pd.DataFrame()
            missing_columns = []

            for excel_col, db_col in self.column_mapping.items():
                if excel_col in df.columns:
                    df_mapped[db_col] = df[excel_col]
                    logger.debug(f"Mapped column: '{excel_col}' -> '{db_col}'")
                else:
                    missing_columns.append(excel_col)
                    self.log_message.emit(
                        f"⚠️ Excel column '{excel_col}' not found", "warning"
                    )

            if missing_columns:
                self.log_message.emit(
                    f"Missing columns: {', '.join(missing_columns)}", "warning"
                )

            if df_mapped.empty:
                self.log_message.emit("No valid columns found after mapping", "error")
                return None

            # Data type optimization
            df_mapped = self._optimize_data_types(df_mapped)

            logger.info(
                f"Column mapping applied: {len(df_mapped.columns)} columns mapped"
            )
            return df_mapped

        except Exception as e:
            self.log_message.emit(f"Error applying column mapping: {e}", "error")
            logger.error(f"Column mapping error: {e}", exc_info=True)
            return None

    def _optimize_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize data types for better performance and storage"""
        try:
            for col in df.columns:
                # Convert object columns that look like numbers
                if df[col].dtype == "object":
                    # Try to convert to numeric
                    numeric_series = pd.to_numeric(df[col], errors="coerce")
                    if not numeric_series.isna().all():  # If some values are numeric
                        df[col] = numeric_series

                # Optimize integer columns
                elif pd.api.types.is_integer_dtype(df[col]):
                    if df[col].min() >= 0:  # Unsigned integers
                        if df[col].max() <= 255:
                            df[col] = df[col].astype("uint8")
                        elif df[col].max() <= 65535:
                            df[col] = df[col].astype("uint16")
                        elif df[col].max() <= 4294967295:
                            df[col] = df[col].astype("uint32")
                    else:  # Signed integers
                        if df[col].min() >= -128 and df[col].max() <= 127:
                            df[col] = df[col].astype("int8")
                        elif df[col].min() >= -32768 and df[col].max() <= 32767:
                            df[col] = df[col].astype("int16")
                        elif (
                            df[col].min() >= -2147483648 and df[col].max() <= 2147483647
                        ):
                            df[col] = df[col].astype("int32")

                # Convert datetime-like strings
                elif df[col].dtype == "object":
                    # Try to parse dates
                    try:
                        date_series = pd.to_datetime(
                            df[col], errors="coerce", infer_datetime_format=True
                        )
                        if not date_series.isna().all():
                            df[col] = date_series
                    except:
                        pass  # Keep as string if date parsing fails

            return df

        except Exception as e:
            logger.warning(f"Data type optimization failed: {e}")
            return df  # Return original if optimization fails

    def stop(self):
        """Stop the import process"""
        self._should_stop = True
        self.log_message.emit("Import cancellation requested", "warning")


class ExcelImportHandler(QObject):
    """
    Handles Excel import operations using worker threads.
    """

    import_progress = pyqtSignal(int, str)  # percentage, message
    import_completed = pyqtSignal(object)  # ExcelImportResult
    log_message = pyqtSignal(str, str)  # message, level

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.worker: Optional[ExcelImportWorker] = None
        logger.info("ExcelImportHandler initialized")

    @pyqtSlot(str, str, dict)
    @handle_exceptions(ErrorCategory.DATA_IMPORT, ErrorSeverity.HIGH)
    def start_import(
        self, file_path: str, table_name: str, column_mapping: Dict[str, str]
    ):
        """Start Excel import in worker thread"""
        # Validate inputs
        if not file_path or not os.path.exists(file_path):
            result = ExcelImportResult()
            result.message = "Invalid Excel file path provided"
            result.success = False
            self.log_message.emit(result.message, "error")
            self.import_completed.emit(result)
            return

        if not table_name:
            result = ExcelImportResult()
            result.message = "Target database table name is not specified"
            result.success = False
            self.log_message.emit(result.message, "error")
            self.import_completed.emit(result)
            return

        # Stop any existing import
        if self.worker and self.worker.isRunning():
            self.log_message.emit("Stopping existing import...", "warning")
            self.worker.stop()
            self.worker.wait(5000)  # Wait up to 5 seconds

        # Create and start new worker
        self.worker = ExcelImportWorker(
            self.config, file_path, table_name, column_mapping or {}
        )

        # Connect signals
        self.worker.progress_updated.connect(self.import_progress.emit)
        self.worker.import_completed.connect(self._handle_import_completed)
        self.worker.log_message.connect(self.log_message.emit)

        # Start worker
        self.worker.start()
        logger.info(f"Excel import started: {file_path} -> {table_name}")

    @pyqtSlot(object)
    def _handle_import_completed(self, result: ExcelImportResult):
        """Handle import completion"""
        self.import_completed.emit(result)

        if result.success:
            logger.info(
                f"Excel import completed successfully: {result.rows_imported_to_db} rows"
            )
        else:
            logger.error(f"Excel import failed: {result.message}")

    @pyqtSlot()
    def stop_import(self):
        """Stop current import operation"""
        if self.worker and self.worker.isRunning():
            self.log_message.emit("Stopping Excel import...", "warning")
            self.worker.stop()
            self.worker.wait(5000)
            logger.info("Excel import stopped")
        else:
            self.log_message.emit("No active import to stop", "info")

    def cleanup(self):
        """Perform cleanup for ExcelImportHandler"""
        logger.info("ExcelImportHandler cleanup initiated")

        # Stop worker if running
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(5000)
            if self.worker.isRunning():
                self.worker.terminate()
                self.worker.wait(2000)

        # Disconnect signals
        try:
            self.import_progress.disconnect()
            self.import_completed.disconnect()
            self.log_message.disconnect()
            logger.info("ExcelImportHandler signals disconnected")
        except (TypeError, RuntimeError):
            pass  # Signals already disconnected

        logger.info("ExcelImportHandler cleanup completed")
