from PyQt6.QtCore import QThread, QObject, pyqtSignal
from connectors.sharepoint_connector import SharePointConnector
from connectors.database_connector import DatabaseConnector
from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class SyncWorker(QThread):
    """แก้แล้ว: แยก worker logic ออกมา, ลด complexity"""

    progress_updated = pyqtSignal(str, int, str)
    sync_completed = pyqtSignal(bool, str, dict)
    log_message = pyqtSignal(str, str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.should_stop = False
        self.sync_stats = self._init_stats()

    def _init_stats(self):
        """สร้าง stats object"""
        return {
            "start_time": datetime.now(),
            "records_processed": 0,
            "records_inserted": 0,
            "errors": 0,
            "duration": 0,
        }

    def run(self):
        """แก้แล้ว: แยกเป็น phases ชัดเจน"""
        start_time = time.time()

        try:
            # Phase 1: SharePoint
            if not self._phase_sharepoint():
                return

            # Phase 2: Database
            if not self._phase_database():
                return

            # Phase 3: Complete
            self._phase_complete(start_time)

        except Exception as e:
            self._handle_error(str(e), start_time)

    @handle_exceptions(ErrorCategory.SYNC, ErrorSeverity.HIGH)
    def _phase_sharepoint(self):
        """Phase 1: SharePoint connection และ data retrieval"""
        self.progress_updated.emit("🔗 Connecting to SharePoint...", 15, "info")

        if self.should_stop:
            return False

        sp_connector = SharePointConnector(self.config)

        if not sp_connector.test_connection():
            self.sync_completed.emit(
                False, "SharePoint connection failed", self.sync_stats
            )
            return False

        self.progress_updated.emit("⬇️ Downloading data...", 30, "info")

        if self.should_stop:
            return False

        self.data = sp_connector.fetch_data()

        if self.data is None or self.data.empty:
            self.progress_updated.emit("⚠️ No data found", 50, "warning")
            self.sync_completed.emit(
                False, "No data in SharePoint list", self.sync_stats
            )
            return False

        self.sync_stats["records_processed"] = len(self.data)
        self.progress_updated.emit(f"📊 Found {len(self.data)} records", 50, "success")
        return True

    @handle_exceptions(ErrorCategory.SYNC, ErrorSeverity.HIGH)
    def _phase_database(self):
        """Phase 2: Database connection และ data insertion"""
        self.progress_updated.emit("💾 Connecting to database...", 60, "info")

        if self.should_stop:
            return False

        db_connector = DatabaseConnector(self.config)

        if not db_connector.test_connection():
            self.sync_completed.emit(
                False, "Database connection failed", self.sync_stats
            )
            return False

        self.progress_updated.emit("🛠️ Preparing table...", 70, "info")

        table_name = self._get_table_name()

        if self._should_create_table():
            try:
                db_connector.create_table_if_not_exists(self.data, table_name)
                self.log_message.emit(f"📋 Table '{table_name}' ready", "info")
            except Exception as e:
                self.log_message.emit(f"⚠️ Table creation failed: {str(e)}", "warning")

        self.progress_updated.emit("📤 Saving data...", 85, "info")

        if self.should_stop:
            return False

        # Add metadata
        self.data["sync_timestamp"] = datetime.now()
        self.data["sync_id"] = f"sync_{int(time.time())}"

        inserted_count = db_connector.insert_data(self.data, table_name)
        self.sync_stats["records_inserted"] = inserted_count
        return True

    def _phase_complete(self, start_time):
        """Phase 3: Completion"""
        duration = time.time() - start_time
        self.sync_stats["duration"] = duration
        self.sync_stats["end_time"] = datetime.now()

        self.progress_updated.emit("✅ Sync completed!", 100, "success")

        success_message = (
            f"Sync successful! "
            f"Processed: {self.sync_stats['records_processed']} records "
            f"Saved: {self.sync_stats['records_inserted']} records "
            f"Duration: {duration:.1f}s"
        )

        self.sync_completed.emit(True, success_message, self.sync_stats)

    def _handle_error(self, error_msg, start_time):
        """จัดการ error"""
        error_message = f"Sync failed: {error_msg}"
        self.sync_stats["errors"] = 1
        self.sync_stats["error_message"] = error_msg
        self.sync_stats["duration"] = time.time() - start_time

        self.progress_updated.emit(f"❌ {error_message}", 0, "error")
        self.sync_completed.emit(False, error_message, self.sync_stats)
        logger.exception("Sync operation failed")

    def _get_table_name(self):
        """ดึงชื่อ table ตาม config"""
        return (
            self.config.sql_table_name
            if self.config.database_type == "sqlserver"
            else self.config.sqlite_table_name
        )

    def _should_create_table(self):
        """ตรวจสอบว่าควรสร้าง table หรือไม่"""
        return (
            self.config.sql_create_table
            if self.config.database_type == "sqlserver"
            else self.config.sqlite_create_table
        )

    def stop(self):
        """หยุดการซิงค์"""
        self.should_stop = True
        self.log_message.emit("⏹️ Stopping sync...", "info")


class SyncEngine(QObject):
    """แก้แล้ว: ลด complexity, เน้น coordination อย่างเดียว"""

    progress_updated = pyqtSignal(str, int, str)
    sync_completed = pyqtSignal(bool, str, dict)
    log_message = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.sync_worker = None
        self.last_sync_stats = None

    def is_sync_running(self):
        """ตรวจสอบสถานะการซิงค์"""
        return self.sync_worker is not None and self.sync_worker.isRunning()

    @handle_exceptions(ErrorCategory.SYNC, ErrorSeverity.MEDIUM)
    def start_sync(self, config):
        """เริ่มการซิงค์"""
        if self.is_sync_running():
            self.log_message.emit("⚠️ Sync already running", "warning")
            return False

        if not self._validate_config(config):
            return False

        # สร้าง worker ใหม่
        self.sync_worker = SyncWorker(config)

        # เชื่อมต่อ signals
        self.sync_worker.progress_updated.connect(self.progress_updated)
        self.sync_worker.sync_completed.connect(self._on_sync_completed)
        self.sync_worker.log_message.connect(self.log_message)

        # เริ่ม worker
        self.sync_worker.start()
        self.log_message.emit("🚀 Sync started", "info")
        return True

    @handle_exceptions(ErrorCategory.SYNC, ErrorSeverity.LOW)
    def stop_sync(self):
        """หยุดการซิงค์"""
        if self.is_sync_running():
            self.sync_worker.stop()
            self.sync_worker.wait(5000)  # รอ 5 วินาที

            if self.sync_worker.isRunning():
                self.sync_worker.terminate()
                self.sync_worker.wait()

            self.log_message.emit("⏹️ Sync stopped", "info")
            return True
        else:
            self.log_message.emit("ℹ️ No sync running", "info")
            return False

    def get_last_sync_stats(self):
        """ดึงสถิติการซิงค์ครั้งล่าสุด"""
        return self.last_sync_stats

    def _validate_config(self, config):
        """ตรวจสอบ config อย่างง่าย"""
        errors = []

        # SharePoint validation
        if not all(
            [
                config.tenant_id,
                config.client_id,
                config.client_secret,
                config.site_url,
                config.list_name,
            ]
        ):
            errors.append("SharePoint config incomplete")

        # Database validation
        if config.database_type == "sqlserver":
            if not all([config.sql_server, config.sql_database, config.sql_table_name]):
                errors.append("SQL Server config incomplete")
        else:  # SQLite
            if not all([config.sqlite_file, config.sqlite_table_name]):
                errors.append("SQLite config incomplete")

        if errors:
            error_message = "Config validation failed: " + ", ".join(errors)
            self.log_message.emit(f"⚠️ {error_message}", "error")
            return False

        return True

    def _on_sync_completed(self, success, message, stats):
        """จัดการเมื่อซิงค์เสร็จสิ้น"""
        self.last_sync_stats = stats
        self.sync_completed.emit(success, message, stats)

        # Log stats
        if success and stats:
            duration = stats.get("duration", 0)
            records = stats.get("records_inserted", 0)
            self.log_message.emit(
                f"📊 Stats: {records} records in {duration:.1f}s", "info"
            )

    def get_sync_progress(self):
        """ดึงความคืบหน้าการซิงค์"""
        if self.is_sync_running():
            return {
                "running": True,
                "thread_id": self.sync_worker.ident if self.sync_worker else None,
            }
        else:
            return {"running": False}
