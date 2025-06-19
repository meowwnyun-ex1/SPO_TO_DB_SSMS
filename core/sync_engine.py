from PyQt6.QtCore import QThread, QObject, pyqtSignal
from connectors.sharepoint_connector import SharePointConnector
from connectors.database_connector import DatabaseConnector
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class SyncThread(QThread):
    """Background thread for sync operations"""

    progress_updated = pyqtSignal(str, int, str)  # message, progress, level
    sync_completed = pyqtSignal(bool, str, dict)  # success, message, stats
    log_message = pyqtSignal(str, str)  # message, level

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.should_stop = False

    def run(self):
        """Main sync execution"""
        try:
            start_time = time.time()
            sync_stats = {
                "start_time": datetime.now(),
                "records_processed": 0,
                "records_inserted": 0,
                "errors": 0,
                "duration": 0,
            }

            # Phase 1: SharePoint Connection
            self.progress_updated.emit("🔄 เริ่มการซิงค์ข้อมูล...", 5, "info")

            if self.should_stop:
                return

            self.progress_updated.emit("🔗 เชื่อมต่อ SharePoint...", 15, "info")
            sp_connector = SharePointConnector(self.config)

            # Test connection
            if not sp_connector.test_connection():
                self.sync_completed.emit(False, "ไม่สามารถเชื่อมต่อ SharePoint", sync_stats)
                return

            # Phase 2: Data Retrieval
            self.progress_updated.emit("⬇️ ดาวน์โหลดข้อมูลจาก SharePoint...", 30, "info")

            if self.should_stop:
                return

            data = sp_connector.fetch_data()

            if data is None or data.empty:
                self.progress_updated.emit("⚠️ ไม่พบข้อมูลที่ต้องซิงค์", 50, "warning")
                self.sync_completed.emit(
                    False, "ไม่มีข้อมูลในรายการ SharePoint", sync_stats
                )
                return

            sync_stats["records_processed"] = len(data)
            self.progress_updated.emit(f"📊 พบข้อมูล {len(data)} รายการ", 50, "success")

            # Phase 3: Database Connection
            self.progress_updated.emit("💾 เชื่อมต่อฐานข้อมูล...", 60, "info")

            if self.should_stop:
                return

            db_connector = DatabaseConnector(self.config)

            if not db_connector.test_connection():
                self.sync_completed.emit(False, "ไม่สามารถเชื่อมต่อฐานข้อมูล", sync_stats)
                return

            # Phase 4: Table Preparation
            self.progress_updated.emit("🛠️ เตรียมตารางฐานข้อมูล...", 70, "info")

            table_name = (
                self.config.sql_table_name
                if self.config.database_type == "sqlserver"
                else self.config.sqlite_table_name
            )

            # Create table if needed
            create_table = (
                self.config.sql_create_table
                if self.config.database_type == "sqlserver"
                else self.config.sqlite_create_table
            )

            if create_table:
                try:
                    db_connector.create_table_if_not_exists(data, table_name)
                    self.log_message.emit(f"📋 ตรวจสอบตาราง '{table_name}' แล้ว", "info")
                except Exception as e:
                    self.log_message.emit(f"⚠️ ไม่สามารถสร้างตาราง: {str(e)}", "warning")

            # Phase 5: Data Insertion
            self.progress_updated.emit("📤 บันทึกข้อมูลลงฐานข้อมูล...", 85, "info")

            if self.should_stop:
                return

            # Add sync metadata
            data["sync_timestamp"] = datetime.now()
            data["sync_id"] = f"sync_{int(time.time())}"

            inserted_count = db_connector.insert_data(data, table_name)
            sync_stats["records_inserted"] = inserted_count

            # Phase 6: Completion
            duration = time.time() - start_time
            sync_stats["duration"] = duration
            sync_stats["end_time"] = datetime.now()

            self.progress_updated.emit("✅ ซิงค์ข้อมูลเสร็จสิ้น!", 100, "success")

            success_message = (
                f"ซิงค์สำเร็จ! "
                f"ประมวลผล: {sync_stats['records_processed']} รายการ "
                f"บันทึก: {sync_stats['records_inserted']} รายการ "
                f"ใช้เวลา: {duration:.1f} วินาที"
            )

            self.sync_completed.emit(True, success_message, sync_stats)

        except Exception as e:
            error_message = f"เกิดข้อผิดพลาดในการซิงค์: {str(e)}"
            sync_stats["errors"] = 1
            sync_stats["error_message"] = str(e)

            self.progress_updated.emit(f"❌ {error_message}", 0, "error")
            self.sync_completed.emit(False, error_message, sync_stats)
            logger.exception("Sync operation failed")

    def stop(self):
        """Stop the sync operation"""
        self.should_stop = True
        self.log_message.emit("⏹️ กำลังหยุดการซิงค์...", "info")


class SyncEngine(QObject):
    """Main sync engine controller"""

    progress_updated = pyqtSignal(str, int, str)  # message, progress, level
    sync_completed = pyqtSignal(bool, str, dict)  # success, message, stats
    log_message = pyqtSignal(str, str)  # message, level

    def __init__(self):
        super().__init__()
        self.sync_thread = None
        self.last_sync_stats = None

    def is_sync_running(self):
        """Check if sync is currently running"""
        return self.sync_thread is not None and self.sync_thread.isRunning()

    def start_sync(self, config):
        """Start synchronization process"""
        try:
            # Check if already running
            if self.is_sync_running():
                self.log_message.emit("⚠️ การซิงค์กำลังดำเนินการอยู่", "warning")
                return False

            # Validate configuration
            if not self._validate_config(config):
                return False

            # Create and start sync thread
            self.sync_thread = SyncThread(config)

            # Connect signals
            self.sync_thread.progress_updated.connect(self.progress_updated)
            self.sync_thread.sync_completed.connect(self._on_sync_completed)
            self.sync_thread.log_message.connect(self.log_message)

            # Start the thread
            self.sync_thread.start()

            self.log_message.emit("🚀 เริ่มการซิงค์ข้อมูล", "info")
            return True

        except Exception as e:
            self.log_message.emit(f"❌ ไม่สามารถเริ่มการซิงค์: {str(e)}", "error")
            return False

    def stop_sync(self):
        """Stop current synchronization"""
        try:
            if self.is_sync_running():
                self.sync_thread.stop()
                self.sync_thread.wait(5000)  # Wait up to 5 seconds

                if self.sync_thread.isRunning():
                    self.sync_thread.terminate()
                    self.sync_thread.wait()

                self.log_message.emit("⏹️ หยุดการซิงค์แล้ว", "info")
                return True
            else:
                self.log_message.emit("ℹ️ ไม่มีการซิงค์ที่กำลังทำงาน", "info")
                return False

        except Exception as e:
            self.log_message.emit(f"❌ ไม่สามารถหยุดการซิงค์: {str(e)}", "error")
            return False

    def get_last_sync_stats(self):
        """Get statistics from last sync operation"""
        return self.last_sync_stats

    def _validate_config(self, config):
        """Validate configuration before sync"""
        errors = []

        # SharePoint validation
        if not config.tenant_id:
            errors.append("ไม่มี Tenant ID")
        if not config.client_id:
            errors.append("ไม่มี Client ID")
        if not config.client_secret:
            errors.append("ไม่มี Client Secret")
        if not config.site_url:
            errors.append("ไม่มี Site URL")
        if not config.list_name:
            errors.append("ไม่ได้เลือกรายการ SharePoint")

        # Database validation
        if config.database_type == "sqlserver":
            if not config.sql_server:
                errors.append("ไม่มีชื่อเซิร์ฟเวอร์ SQL")
            if not config.sql_database:
                errors.append("ไม่มีชื่อฐานข้อมูล")
            if not config.sql_table_name:
                errors.append("ไม่มีชื่อตาราง SQL")
            if not config.sql_username:
                errors.append("ไม่มีชื่อผู้ใช้ SQL")
        else:  # SQLite
            if not config.sqlite_file:
                errors.append("ไม่ได้เลือกไฟล์ SQLite")
            if not config.sqlite_table_name:
                errors.append("ไม่มีชื่อตาราง SQLite")

        if errors:
            error_message = "การตั้งค่าไม่ครบถ้วน: " + ", ".join(errors)
            self.log_message.emit(f"⚠️ {error_message}", "error")
            return False

        return True

    def _on_sync_completed(self, success, message, stats):
        """Handle sync completion"""
        self.last_sync_stats = stats
        self.sync_completed.emit(success, message, stats)

        # Log detailed stats
        if success and stats:
            duration = stats.get("duration", 0)
            records = stats.get("records_inserted", 0)
            self.log_message.emit(
                f"📊 สถิติการซิงค์: {records} รายการ ใน {duration:.1f} วินาที", "info"
            )

    def get_sync_progress(self):
        """Get current sync progress (if running)"""
        if self.is_sync_running():
            return {
                "running": True,
                "thread_id": self.sync_thread.ident if self.sync_thread else None,
            }
        else:
            return {"running": False}
