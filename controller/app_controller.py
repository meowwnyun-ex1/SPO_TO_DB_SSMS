from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from .sync_engine import SyncEngine
from .connection_manager import ConnectionManager
from utils.config_manager import ConfigManager
from utils.cache_cleaner import AutoCacheManager
import logging

logger = logging.getLogger(__name__)


class AppController(QObject):
    """App Controller - แก้ field mapping และบัค"""

    # Core signals
    status_changed = pyqtSignal(str, str)
    progress_updated = pyqtSignal(str, int, str)
    sync_completed = pyqtSignal(bool, str, dict)
    log_message = pyqtSignal(str, str)

    # UI update signals
    sharepoint_sites_updated = pyqtSignal(list)
    sharepoint_lists_updated = pyqtSignal(list)
    database_names_updated = pyqtSignal(list)
    database_tables_updated = pyqtSignal(list)
    ui_enable_request = pyqtSignal(bool)

    # Status signals
    sharepoint_status_update = pyqtSignal(str)
    database_status_update = pyqtSignal(str)
    last_sync_status_update = pyqtSignal(str)
    auto_sync_status_update = pyqtSignal(bool)
    progress_update = pyqtSignal(int)
    current_task_update = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # Services
        self.config_manager = ConfigManager()
        self.connection_manager = ConnectionManager()
        self.sync_engine = SyncEngine()
        self.cache_manager = AutoCacheManager()

        # Auto-sync timer
        self.auto_sync_timer = QTimer()
        self.auto_sync_enabled = False

        self._setup_connections()
        self._start_cache_manager()

        logger.info("🎉 AppController initialized")

    def _setup_connections(self):
        """Setup signal connections"""
        self.sync_engine.progress_updated.connect(self.progress_updated)
        self.sync_engine.sync_completed.connect(self._handle_sync_completion)
        self.sync_engine.log_message.connect(self.log_message)

        self.connection_manager.status_changed.connect(
            self._handle_connection_status_change
        )
        self.connection_manager.log_message.connect(self.log_message)

        self.auto_sync_timer.timeout.connect(self._auto_sync_triggered)

        # Cache manager
        self.cache_manager.cleanup_completed.connect(self._on_cache_cleaned)
        self.cache_manager.log_message.connect(self.log_message)

    def _start_cache_manager(self):
        """เริ่ม cache manager"""
        self.cache_manager.start_auto_cleanup()

    # Configuration Management
    def get_config(self):
        return self.config_manager.get_config()

    def update_config(self, config_object):
        self.config_manager.save_config(config_object)
        self.log_message.emit("💾 Configuration updated", "success")

    # Connection Testing
    def test_sharepoint_connection(self):
        return self._test_connection("sharepoint")

    def test_database_connection(self):
        return self._test_connection("database")

    def _test_connection(self, conn_type):
        """Generic connection test method"""
        self.ui_enable_request.emit(False)

        try:
            config = self.get_config()

            if conn_type == "sharepoint":
                if not self._validate_sharepoint_config(config):
                    return False
                self.sharepoint_status_update.emit("connecting")
                success = self.connection_manager.test_sharepoint_connection(config)
                status = "connected" if success else "error"
                self.sharepoint_status_update.emit(status)

            else:  # database
                if not self._validate_database_config(config):
                    return False
                self.database_status_update.emit("connecting")
                success = self.connection_manager.test_database_connection(config)
                status = "connected" if success else "error"
                self.database_status_update.emit(status)

            msg = (
                f"✅ {conn_type.title()} connected"
                if success
                else f"❌ {conn_type.title()} failed"
            )
            self.log_message.emit(msg, "success" if success else "error")

            return success

        except Exception as e:
            self.log_message.emit(f"❌ {conn_type.title()} error: {str(e)}", "error")
            return False
        finally:
            self.ui_enable_request.emit(True)

    def _validate_sharepoint_config(self, config):
        """แก้: SharePoint validation"""
        required_fields = [
            config.sharepoint_client_id,
            config.sharepoint_client_secret,
            config.tenant_id,
            config.sharepoint_url or config.sharepoint_site,
        ]
        if not all(required_fields):
            self.log_message.emit("⚠️ SharePoint config incomplete", "warning")
            self.sharepoint_status_update.emit("warning")
            return False
        return True

    def _validate_database_config(self, config):
        """แก้: Database validation"""
        db_type = config.database_type or config.db_type

        if db_type and db_type.lower() == "sqlite":
            if not config.sqlite_file:
                self.log_message.emit("⚠️ SQLite file path required", "warning")
                self.database_status_update.emit("warning")
                return False
        else:  # SQL Server
            required_fields = [
                config.sql_server or config.db_host,
                config.sql_database or config.db_name,
            ]
            if not all(required_fields):
                self.log_message.emit("⚠️ Database config incomplete", "warning")
                self.database_status_update.emit("warning")
                return False
        return True

    def test_all_connections(self):
        """ทดสอบการเชื่อมต่อทั้งหมด"""
        self.log_message.emit("🔍 Testing all connections...", "info")

        sp_result = self.test_sharepoint_connection()
        db_result = self.test_database_connection()

        if sp_result and db_result:
            self.log_message.emit("🎉 All connections successful!", "success")
        else:
            self.log_message.emit("⚠️ Some connections failed", "warning")

        return sp_result and db_result

    # Data refresh methods
    def refresh_sharepoint_sites(self):
        self._refresh_data(
            "sites",
            self.connection_manager.get_sharepoint_sites,
            self.sharepoint_sites_updated,
        )

    def refresh_sharepoint_lists(self):
        self._refresh_data(
            "lists",
            self.connection_manager.get_sharepoint_lists,
            self.sharepoint_lists_updated,
        )

    def refresh_database_names(self):
        self._refresh_data(
            "databases",
            self.connection_manager.get_databases,
            self.database_names_updated,
        )

    def refresh_database_tables(self):
        self._refresh_data(
            "tables", self.connection_manager.get_tables, self.database_tables_updated
        )

    def _refresh_data(self, data_type, fetch_method, signal):
        """Generic data refresh method"""
        self.ui_enable_request.emit(False)
        try:
            config = self.get_config()
            data = fetch_method(config)
            signal.emit(data)
            self.log_message.emit(f"📡 Found {len(data)} {data_type}", "success")
        except Exception as e:
            self.log_message.emit(f"❌ Failed to get {data_type}: {str(e)}", "error")
        finally:
            self.ui_enable_request.emit(True)

    # Synchronization
    def run_full_sync(self):
        """เริ่มการซิงค์"""
        self.ui_enable_request.emit(False)
        self.last_sync_status_update.emit("in_progress")

        try:
            config = self.get_config()
            validation_result = self._validate_sync_config(config)

            if not validation_result["valid"]:
                self.log_message.emit(f"⚠️ {validation_result['message']}", "warning")
                self._sync_failed()
                return False

            if self.sync_engine.is_sync_running():
                self.log_message.emit("⚠️ Sync already running", "warning")
                self.ui_enable_request.emit(True)
                return False

            self.log_message.emit("🚀 Starting sync...", "info")
            self.sync_engine.start_sync(config)
            return True

        except Exception as e:
            self.log_message.emit(f"❌ Sync start failed: {str(e)}", "error")
            self._sync_failed()
            return False

    def _sync_failed(self):
        """Centralize sync failure handling"""
        self.ui_enable_request.emit(True)
        self.last_sync_status_update.emit("error")

    def stop_sync(self):
        """หยุดการซิงค์"""
        try:
            if self.sync_engine.is_sync_running():
                self.sync_engine.stop_sync()
                self.log_message.emit("⏹️ Sync stopped", "info")
                self.ui_enable_request.emit(True)
                self.last_sync_status_update.emit("never")
                return True
            else:
                self.log_message.emit("ℹ️ No sync running", "info")
                return False
        except Exception as e:
            self.log_message.emit(f"❌ Stop sync failed: {str(e)}", "error")
            return False

    # Auto-sync Management
    def toggle_auto_sync(self, enabled):
        """เปิด/ปิดการซิงค์อัตโนมัติ"""
        try:
            self.auto_sync_enabled = enabled
            config = self.get_config()
            interval = config.sync_interval

            if enabled:
                self.auto_sync_timer.start(interval * 60 * 1000)
                self.log_message.emit(
                    f"⏰ Auto sync enabled ({interval}min)", "success"
                )
            else:
                self.auto_sync_timer.stop()
                self.log_message.emit("⏸️ Auto sync disabled", "info")

            self.auto_sync_status_update.emit(enabled)
            return True

        except Exception as e:
            self.log_message.emit(f"❌ Auto sync toggle failed: {str(e)}", "error")
            return False

    def _auto_sync_triggered(self):
        """จัดการ auto-sync trigger"""
        if not self.sync_engine.is_sync_running():
            self.log_message.emit("🔄 Auto sync triggered", "info")
            self.run_full_sync()
        else:
            self.log_message.emit("⏭️ Auto sync skipped (running)", "info")

    # Utility Methods
    def clear_system_cache(self):
        """ล้างแคชระบบ"""
        try:
            self.log_message.emit("🧹 Clearing system cache...", "info")
            self.cache_manager.force_cleanup()
            return True
        except Exception as e:
            self.log_message.emit(f"❌ Cache clear failed: {str(e)}", "error")
            return False

    def _validate_sync_config(self, config):
        """แก้: ตรวจสอบการตั้งค่าสำหรับซิงค์"""
        # SharePoint validation
        sp_fields = [
            config.sharepoint_client_id,
            config.sharepoint_client_secret,
            config.tenant_id,
            config.sharepoint_url or config.sharepoint_site,
        ]
        if not all(sp_fields):
            return {"valid": False, "message": "SharePoint config incomplete"}

        if not config.sharepoint_list:
            return {"valid": False, "message": "No SharePoint list selected"}

        # Database validation
        db_type = config.database_type or config.db_type
        if db_type and db_type.lower() == "sqlite":
            if not all([config.sqlite_file, config.sqlite_table_name]):
                return {"valid": False, "message": "SQLite config incomplete"}
        else:  # SQL Server
            if not all(
                [
                    config.sql_server or config.db_host,
                    config.sql_database or config.db_name,
                    config.sql_table_name or config.db_table,
                ]
            ):
                return {"valid": False, "message": "SQL Server config incomplete"}

        return {"valid": True, "message": "Configuration valid"}

    # Event Handlers
    def _handle_sync_completion(self, success, message, stats):
        """จัดการเมื่อซิงค์เสร็จสิ้น"""
        self.sync_completed.emit(success, message, stats)

        if success:
            self.last_sync_status_update.emit("success")
            self.log_message.emit(f"✅ Sync completed: {message}", "success")
        else:
            self.last_sync_status_update.emit("error")
            self.log_message.emit(f"❌ Sync failed: {message}", "error")

        self.progress_update.emit(0)
        self.current_task_update.emit("Idle")
        self.ui_enable_request.emit(True)

    def _handle_connection_status_change(self, service_name, status):
        """จัดการการเปลี่ยนสถานะการเชื่อมต่อ"""
        if service_name == "SharePoint":
            self.sharepoint_status_update.emit(status)
        elif service_name == "Database":
            self.database_status_update.emit(status)
        self.status_changed.emit(service_name, status)

    def _on_cache_cleaned(self, result):
        """จัดการเมื่อล้างแคชเสร็จ"""
        self.log_message.emit(
            f"✅ Cache cleaned: {result.space_freed_mb:.1f}MB freed", "success"
        )

    def get_sync_status(self):
        """ดึงสถานะการซิงค์"""
        return {
            "is_running": self.sync_engine.is_sync_running(),
            "auto_sync_enabled": self.auto_sync_enabled,
            "auto_sync_interval": (
                self.auto_sync_timer.interval() // (1000 * 60)
                if self.auto_sync_timer.isActive()
                else 0
            ),
        }

    def cleanup(self):
        """แก้บัค: ทำความสะอาดก่อนปิดโปรแกรม"""
        try:
            if self.sync_engine.is_sync_running():
                self.sync_engine.stop_sync()

            self.auto_sync_timer.stop()

            # แก้: ตรวจสอบว่า cache_manager มี method นี้หรือไม่
            if hasattr(self.cache_manager, "stop_auto_cleanup"):
                self.cache_manager.stop_auto_cleanup()

            self.log_message.emit("🧹 Resources cleaned", "info")

        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")
