from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from .sync_engine import SyncEngine
from .connection_manager import ConnectionManager
from utils.config_manager import ConfigManager
import logging


logger = logging.getLogger(__name__)


class AppController(QObject):
    # Signals for UI communication
    status_changed = pyqtSignal(str, str)  # service_name, status
    progress_updated = pyqtSignal(str, int, str)  # message, progress, level
    sync_completed = pyqtSignal(bool, str, dict)  # Added dict for sync stats
    log_message = pyqtSignal(str, str)  # message, level

    # New signals for dashboard/config panel updates
    sharepoint_sites_updated = pyqtSignal(list)
    sharepoint_lists_updated = pyqtSignal(list)
    database_names_updated = pyqtSignal(list)
    database_tables_updated = pyqtSignal(list)
    ui_enable_request = pyqtSignal(bool)  # To enable/disable UI during operations

    # Specific status update signals for status cards
    sharepoint_status_update = pyqtSignal(
        str
    )  # "connected", "disconnected", "error", etc.
    database_status_update = pyqtSignal(
        str
    )  # "connected", "disconnected", "error", etc.
    last_sync_status_update = pyqtSignal(
        str
    )  # "success", "error", "never", "in_progress"
    auto_sync_status_update = pyqtSignal(bool)  # True/False
    progress_update = pyqtSignal(int)  # Overall progress 0-100%
    current_task_update = pyqtSignal(str)  # Description of current task

    def __init__(self):
        super().__init__()

        # Initialize core components
        self.config_manager = ConfigManager()
        self.connection_manager = ConnectionManager()
        self.sync_engine = SyncEngine()

        # Auto-sync timer
        self.auto_sync_timer = QTimer()
        self.auto_sync_enabled = False

        # Setup internal connections
        self._setup_connections()

        logger.info("🎉 AppController initialized successfully")

    def _setup_connections(self):
        """Setup internal signal connections"""
        # Sync engine signals
        self.sync_engine.progress_updated.connect(self.progress_updated)
        self.sync_engine.sync_completed.connect(
            self._handle_sync_completion
        )  # Connect to internal handler
        self.sync_engine.log_message.connect(self.log_message)

        # Connection manager signals
        self.connection_manager.status_changed.connect(
            self._handle_connection_status_change
        )
        self.connection_manager.log_message.connect(self.log_message)

        # Auto-sync timer
        self.auto_sync_timer.timeout.connect(self._auto_sync_triggered)

        logger.debug("Internal signal connections established")

    def _handle_sync_completion(self, success, message, stats):
        """Handle sync completion, update UI and log."""
        self.sync_completed.emit(success, message, stats)  # Re-emit for other listeners
        if success:
            self.last_sync_status_update.emit("success")
            self.log_message.emit(f"✅ Sync completed: {message}", "success")
        else:
            self.last_sync_status_update.emit("error")
            self.log_message.emit(f"❌ Sync failed: {message}", "error")
        self.progress_update.emit(0)  # Reset overall progress
        self.current_task_update.emit("Idle")  # Reset current task
        self.ui_enable_request.emit(True)  # Re-enable UI

    def _handle_connection_status_change(self, service_name, status):
        """Handle connection status changes and propagate to UI."""
        if service_name == "SharePoint":
            self.sharepoint_status_update.emit(status)
        elif service_name == "Database":
            self.database_status_update.emit(status)
        self.status_changed.emit(service_name, status)  # Re-emit generic status_changed

    # Configuration Management
    def get_config(self):
        """Get current configuration"""
        return self.config_manager.get_config()

    def update_config(self, config_object):
        """Update and save configuration from UI"""
        # This method is called from ConfigPanel via config_changed signal
        self.config_manager.save_config(config_object)
        self.log_message.emit("💾 การตั้งค่าได้รับการอัปเดตแล้ว", "success")
        # After config update, you might want to re-test connections or update UI elements
        # For simplicity, we just save here. More complex logic might involve emitting
        # signals back to UI to update specific fields if config values change validation.

    # Connection Testing (updated to emit specific status signals)
    def test_sharepoint_connection(self):
        """Test SharePoint connection"""
        self.ui_enable_request.emit(False)  # Disable UI during test
        try:
            config = self.get_config()
            if not all(
                [
                    config.sharepoint_client_id,  # Updated from client_id
                    config.sharepoint_client_secret,  # Updated from client_secret
                    config.tenant_id,
                    config.sharepoint_site,  # Updated from site_url
                ]
            ):
                self.log_message.emit("⚠️ กรุณากรอกข้อมูล SharePoint ให้ครบถ้วน", "warning")
                self.sharepoint_status_update.emit("warning")
                self.ui_enable_request.emit(True)
                return False

            self.sharepoint_status_update.emit("connecting")
            self.log_message.emit("🔍 กำลังทดสอบการเชื่อมต่อ SharePoint...", "info")

            success = self.connection_manager.test_sharepoint_connection(config)

            if success:
                self.sharepoint_status_update.emit("connected")
                self.log_message.emit("✅ เชื่อมต่อ SharePoint สำเร็จ", "success")
            else:
                self.sharepoint_status_update.emit("error")
                self.log_message.emit("❌ เชื่อมต่อ SharePoint ล้มเหลว", "error")

            self.ui_enable_request.emit(True)
            return success

        except Exception as e:
            self.sharepoint_status_update.emit("error")
            self.log_message.emit(f"❌ ข้อผิดพลาดการเชื่อมต่อ SharePoint: {str(e)}", "error")
            self.ui_enable_request.emit(True)
            return False

    def test_database_connection(self):
        """Test database connection"""
        self.ui_enable_request.emit(False)  # Disable UI during test
        try:
            config = self.get_config()

            # Validate database config
            if config.database_type == "sqlserver":
                if not all(
                    [config.sql_server, config.sql_database, config.sql_username]
                ):
                    self.log_message.emit(
                        "⚠️ กรุณากรอกข้อมูล SQL Server ให้ครบถ้วน", "warning"
                    )
                    self.database_status_update.emit("warning")
                    self.ui_enable_request.emit(True)
                    return False
            else:  # SQLite
                if not config.sqlite_file:
                    self.log_message.emit("⚠️ กรุณาเลือกไฟล์ SQLite", "warning")
                    self.database_status_update.emit("warning")
                    self.ui_enable_request.emit(True)
                    return False

            self.database_status_update.emit("connecting")
            self.log_message.emit("🔍 กำลังทดสอบการเชื่อมต่อฐานข้อมูล...", "info")

            success = self.connection_manager.test_database_connection(config)

            if success:
                self.database_status_update.emit("connected")
                self.log_message.emit("✅ เชื่อมต่อฐานข้อมูลสำเร็จ", "success")
            else:
                self.database_status_update.emit("error")
                self.log_message.emit("❌ เชื่อมต่อฐานข้อมูลล้มเหลว", "error")

            self.ui_enable_request.emit(True)
            return success

        except Exception as e:
            self.database_status_update.emit("error")
            self.log_message.emit(f"❌ ข้อผิดพลาดการเชื่อมต่อฐานข้อมูล: {str(e)}", "error")
            self.ui_enable_request.emit(True)
            return False

    def test_all_connections(self):
        """Test both SharePoint and database connections"""
        self.log_message.emit("🔍 ทดสอบการเชื่อมต่อทั้งหมด...", "info")

        sp_result = self.test_sharepoint_connection()
        db_result = self.test_database_connection()

        if sp_result and db_result:
            self.log_message.emit("🎉 ทดสอบการเชื่อมต่อทั้งหมดสำเร็จ!", "success")
        else:
            self.log_message.emit("⚠️ การทดสอบการเชื่อมต่อมีปัญหา", "warning")

        return sp_result and db_result

    # SharePoint Data Browse (updated to emit specific update signals for UI)
    def refresh_sharepoint_sites(self):
        """Refresh and populate SharePoint sites in UI."""
        self.ui_enable_request.emit(False)
        try:
            sites = self.connection_manager.get_sharepoint_sites(self.get_config())
            self.sharepoint_sites_updated.emit(sites)
            self.log_message.emit(f"📡 พบไซต์ SharePoint {len(sites)} รายการ", "success")
        except Exception as e:
            self.log_message.emit(f"❌ ไม่สามารถดึงรายการไซต์: {str(e)}", "error")
        finally:
            self.ui_enable_request.emit(True)

    def refresh_sharepoint_lists(self):
        """Refresh and populate SharePoint lists for the selected site."""
        self.ui_enable_request.emit(False)
        try:
            config = self.get_config()
            site_url = config.sharepoint_site  # Get selected site from config
            if site_url:
                lists = self.connection_manager.get_sharepoint_lists(config, site_url)
                self.sharepoint_lists_updated.emit(lists)
                self.log_message.emit(
                    f"📋 พบลิสต์ SharePoint {len(lists)} รายการ", "success"
                )
            else:
                self.log_message.emit("⚠️ กรุณาเลือก SharePoint Site ก่อน", "warning")
        except Exception as e:
            self.log_message.emit(f"❌ ไม่สามารถดึงรายการลิสต์: {str(e)}", "error")
        finally:
            self.ui_enable_request.emit(True)

    # Database Browse (updated to emit specific update signals for UI)
    def refresh_database_names(self):
        """Refresh and populate database names in UI."""
        self.ui_enable_request.emit(False)
        try:
            databases = self.connection_manager.get_databases(self.get_config())
            self.database_names_updated.emit(databases)
            self.log_message.emit(f"🗄️ พบฐานข้อมูล {len(databases)} รายการ", "success")
        except Exception as e:
            self.log_message.emit(f"❌ ไม่สามารถดึงรายการฐานข้อมูล: {str(e)}", "error")
        finally:
            self.ui_enable_request.emit(True)

    def refresh_database_tables(self):
        """Refresh and populate database tables for the selected database."""
        self.ui_enable_request.emit(False)
        try:
            config = self.get_config()
            tables = self.connection_manager.get_tables(config)
            self.database_tables_updated.emit(tables)
            self.log_message.emit(f"📊 พบตาราง {len(tables)} รายการ", "success")
        except Exception as e:
            self.log_message.emit(f"❌ ไม่สามารถดึงรายการตาราง: {str(e)}", "error")
        finally:
            self.ui_enable_request.emit(True)

    # Synchronization
    def run_full_sync(self):  # Renamed from start_sync
        """Start synchronization process (manual trigger)"""
        self.ui_enable_request.emit(False)  # Disable UI during sync
        self.last_sync_status_update.emit("in_progress")  # Set status to in progress
        try:
            # Validate configuration
            config = self.get_config()
            validation_result = self._validate_sync_config(config)

            if not validation_result["valid"]:
                self.log_message.emit(f"⚠️ {validation_result['message']}", "warning")
                self.ui_enable_request.emit(True)  # Re-enable UI on validation failure
                self.last_sync_status_update.emit("error")  # Set status to error
                return False

            # Check if sync is already running
            if self.sync_engine.is_sync_running():
                self.log_message.emit("⚠️ การซิงค์กำลังดำเนินการอยู่", "warning")
                self.ui_enable_request.emit(True)  # Re-enable UI
                self.last_sync_status_update.emit(
                    "in_progress"
                )  # Keep status in progress
                return False

            self.log_message.emit("🚀 เริ่มการซิงค์ข้อมูล...", "info")

            # Start sync (sync_engine will emit progress and completion signals)
            # No need to return success here, as _handle_sync_completion will manage UI updates
            self.sync_engine.start_sync(config)
            return True

        except Exception as e:
            self.log_message.emit(f"❌ ไม่สามารถเริ่มการซิงค์: {str(e)}", "error")
            self.ui_enable_request.emit(True)  # Re-enable UI on error
            self.last_sync_status_update.emit("error")  # Set status to error
            return False

    def stop_sync(self):
        """Stop current synchronization"""
        try:
            if self.sync_engine.is_sync_running():
                self.sync_engine.stop_sync()
                self.log_message.emit("⏹️ หยุดการซิงค์แล้ว", "info")
                self.ui_enable_request.emit(True)  # Re-enable UI
                self.last_sync_status_update.emit(
                    "never"
                )  # Set status to never or disconnected
                return True
            else:
                self.log_message.emit("ℹ️ ไม่มีการซิงค์ที่กำลังทำงาน", "info")
                return False
        except Exception as e:
            self.log_message.emit(f"❌ ไม่สามารถหยุดการซิงค์: {str(e)}", "error")
            return False

    # Auto-sync Management
    def toggle_auto_sync(
        self, enabled
    ):  # Removed interval parameter as it's from config now
        """Toggle automatic synchronization"""
        try:
            self.auto_sync_enabled = enabled
            config = self.get_config()  # Get interval from config
            interval = (
                config.sync_interval
            )  # Assuming sync_interval is in minutes from config_panel

            if enabled:
                # Convert minutes to milliseconds for QTimer
                self.auto_sync_timer.start(interval * 60 * 1000)
                self.log_message.emit(
                    f"⏰ เปิดการซิงค์อัตโนมัติ (ทุก {interval} นาที)", "success"
                )
            else:
                self.auto_sync_timer.stop()
                self.log_message.emit("⏸️ หยุดการซิงค์อัตโนมัติ", "info")

            self.auto_sync_status_update.emit(enabled)  # Update UI checkbox
            return True

        except Exception as e:
            self.log_message.emit(
                f"❌ ไม่สามารถเปลี่ยนการตั้งค่าการซิงค์อัตโนมัติ: {str(e)}", "error"
            )
            return False

    def _auto_sync_triggered(self):
        """Handle auto-sync timer trigger"""
        if not self.sync_engine.is_sync_running():
            self.log_message.emit("🔄 การซิงค์อัตโนมัติ", "info")
            self.run_full_sync()  # Call the new run_full_sync
        else:
            self.log_message.emit("⏭️ ข้ามการซิงค์อัตโนมัติ (กำลังซิงค์อยู่)", "info")

    # Utility Methods
    def clear_system_cache(self):
        """Clears the system cache (placeholder for actual implementation)."""
        self.log_message.emit("🧹 กำลังล้างแคชระบบ...", "info")
        # --- Placeholder for actual cache clearing logic ---
        # In a real application, this would involve clearing temporary files,
        # resetting internal states, or interacting with a cache manager.
        # For now, it's just a logging message.
        # ---------------------------------------------------
        logger.info("System cache cleared (placeholder).")
        self.log_message.emit("✅ ล้างแคชระบบสำเร็จ", "success")
        return True

    def _validate_sync_config(self, config):
        """Validate configuration for sync operation"""
        # SharePoint validation
        if not all(
            [
                config.sharepoint_client_id,
                config.sharepoint_client_secret,
                config.tenant_id,
                config.sharepoint_site,
            ]
        ):
            return {"valid": False, "message": "กรุณากรอกข้อมูล SharePoint ให้ครบถ้วน"}

        if not config.sharepoint_list:  # Updated from list_name
            return {"valid": False, "message": "กรุณาเลือกรายการ SharePoint"}

        # Database validation
        if config.database_type == "sqlserver":
            if not all([config.sql_server, config.sql_database, config.sql_table_name]):
                return {"valid": False, "message": "กรุณากรอกข้อมูล SQL Server ให้ครบถ้วน"}
        elif config.database_type == "sqlite":  # SQLite
            if not all([config.sqlite_file, config.sqlite_table_name]):
                return {"valid": False, "message": "กรุณากรอกข้อมูล SQLite ให้ครบถ้วน"}
        else:  # Handle other database types if added
            return {"valid": False, "message": "ประเภทฐานข้อมูลไม่ถูกต้อง"}

        return {"valid": True, "message": "การตั้งค่าถูกต้อง"}

    def get_sync_status(self):
        """Get current sync status"""
        return {
            "is_running": self.sync_engine.is_sync_running(),
            "auto_sync_enabled": self.auto_sync_enabled,
            "auto_sync_interval": (
                self.auto_sync_timer.interval()
                // (1000 * 60)  # Convert milliseconds to minutes
                if self.auto_sync_timer.isActive()
                else 0
            ),
        }

    def cleanup(self):
        """Cleanup resources before application exit"""
        try:
            if self.sync_engine.is_sync_running():
                self.sync_engine.stop_sync()

            self.auto_sync_timer.stop()
            self.log_message.emit("� ล้างทรัพยากรเสร็จสิ้น", "info")

        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
