from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from .sync_engine import SyncEngine
from .connection_manager import ConnectionManager
from utils.config_manager import ConfigManager
import logging

logger = logging.getLogger(__name__)


class AppController(QObject):
    # Signals for UI communication
    status_changed = pyqtSignal(str, str)  # service_name, status
    progress_updated = pyqtSignal(str, int, str)  # message, progress, level
    sync_completed = pyqtSignal(bool, str)  # success, message
    log_message = pyqtSignal(str, str)  # message, level

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
        self.sync_engine.sync_completed.connect(self.sync_completed)
        self.sync_engine.log_message.connect(self.log_message)

        # Connection manager signals
        self.connection_manager.status_changed.connect(self.status_changed)
        self.connection_manager.log_message.connect(self.log_message)

        # Auto-sync timer
        self.auto_sync_timer.timeout.connect(self._auto_sync_triggered)

        logger.debug("Internal signal connections established")

    # Configuration Management
    def get_config(self):
        """Get current configuration"""
        return self.config_manager.get_config()

    def save_config(self, config):
        """Save configuration"""
        try:
            self.config_manager.save_config(config)
            self.log_message.emit("💾 บันทึกการตั้งค่าแล้ว", "success")
            return True
        except Exception as e:
            self.log_message.emit(f"❌ ไม่สามารถบันทึกการตั้งค่า: {str(e)}", "error")
            return False

    # Connection Testing
    def test_sharepoint_connection(self):
        """Test SharePoint connection"""
        try:
            config = self.get_config()
            if not all(
                [
                    config.tenant_id,
                    config.client_id,
                    config.client_secret,
                    config.site_url,
                ]
            ):
                self.log_message.emit("⚠️ กรุณากรอกข้อมูล SharePoint ให้ครบถ้วน", "warning")
                return False

            self.status_changed.emit("SharePoint", "connecting")
            self.log_message.emit("🔍 กำลังทดสอบการเชื่อมต่อ SharePoint...", "info")

            success = self.connection_manager.test_sharepoint_connection(config)

            if success:
                self.status_changed.emit("SharePoint", "connected")
                self.log_message.emit("✅ เชื่อมต่อ SharePoint สำเร็จ", "success")
            else:
                self.status_changed.emit("SharePoint", "error")
                self.log_message.emit("❌ เชื่อมต่อ SharePoint ล้มเหลว", "error")

            return success

        except Exception as e:
            self.status_changed.emit("SharePoint", "error")
            self.log_message.emit(f"❌ ข้อผิดพลาดการเชื่อมต่อ SharePoint: {str(e)}", "error")
            return False

    def test_database_connection(self):
        """Test database connection"""
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
                    return False
            else:  # SQLite
                if not config.sqlite_file:
                    self.log_message.emit("⚠️ กรุณาเลือกไฟล์ SQLite", "warning")
                    return False

            self.status_changed.emit("Database", "connecting")
            self.log_message.emit("🔍 กำลังทดสอบการเชื่อมต่อฐานข้อมูล...", "info")

            success = self.connection_manager.test_database_connection(config)

            if success:
                self.status_changed.emit("Database", "connected")
                self.log_message.emit("✅ เชื่อมต่อฐานข้อมูลสำเร็จ", "success")
            else:
                self.status_changed.emit("Database", "error")
                self.log_message.emit("❌ เชื่อมต่อฐานข้อมูลล้มเหลว", "error")

            return success

        except Exception as e:
            self.status_changed.emit("Database", "error")
            self.log_message.emit(f"❌ ข้อผิดพลาดการเชื่อมต่อฐานข้อมูล: {str(e)}", "error")
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

    # SharePoint Data Browsing
    def get_sharepoint_sites(self):
        """Get available SharePoint sites"""
        try:
            config = self.get_config()
            self.log_message.emit("🔍 กำลังดึงรายการไซต์ SharePoint...", "info")

            sites = self.connection_manager.get_sharepoint_sites(config)
            self.log_message.emit(f"📡 พบไซต์ SharePoint {len(sites)} รายการ", "success")
            return sites

        except Exception as e:
            self.log_message.emit(f"❌ ไม่สามารถดึงรายการไซต์: {str(e)}", "error")
            return []

    def get_sharepoint_lists(self, site_url):
        """Get lists from SharePoint site"""
        try:
            config = self.get_config()
            self.log_message.emit("📋 กำลังดึงรายการลิสต์ SharePoint...", "info")

            lists = self.connection_manager.get_sharepoint_lists(config, site_url)
            self.log_message.emit(f"📋 พบลิสต์ SharePoint {len(lists)} รายการ", "success")
            return lists

        except Exception as e:
            self.log_message.emit(f"❌ ไม่สามารถดึงรายการลิสต์: {str(e)}", "error")
            return []

    # Database Browsing
    def get_databases(self):
        """Get available databases (SQL Server only)"""
        try:
            config = self.get_config()
            if config.database_type != "sqlserver":
                return []

            self.log_message.emit("🗄️ กำลังดึงรายการฐานข้อมูล...", "info")
            databases = self.connection_manager.get_databases(config)
            self.log_message.emit(f"🗄️ พบฐานข้อมูล {len(databases)} รายการ", "success")
            return databases

        except Exception as e:
            self.log_message.emit(f"❌ ไม่สามารถดึงรายการฐานข้อมูล: {str(e)}", "error")
            return []

    def get_tables(self):
        """Get available tables"""
        try:
            config = self.get_config()
            self.log_message.emit("📊 กำลังดึงรายการตาราง...", "info")

            tables = self.connection_manager.get_tables(config)
            self.log_message.emit(f"📊 พบตาราง {len(tables)} รายการ", "success")
            return tables

        except Exception as e:
            self.log_message.emit(f"❌ ไม่สามารถดึงรายการตาราง: {str(e)}", "error")
            return []

    # Synchronization
    def start_sync(self):
        """Start synchronization process"""
        try:
            # Validate configuration
            config = self.get_config()
            validation_result = self._validate_sync_config(config)

            if not validation_result["valid"]:
                self.log_message.emit(f"⚠️ {validation_result['message']}", "warning")
                return False

            # Check if sync is already running
            if self.sync_engine.is_sync_running():
                self.log_message.emit("⚠️ การซิงค์กำลังดำเนินการอยู่", "warning")
                return False

            self.log_message.emit("🚀 เริ่มการซิงค์ข้อมูล...", "info")

            # Start sync
            success = self.sync_engine.start_sync(config)
            return success

        except Exception as e:
            self.log_message.emit(f"❌ ไม่สามารถเริ่มการซิงค์: {str(e)}", "error")
            return False

    def stop_sync(self):
        """Stop current synchronization"""
        try:
            if self.sync_engine.is_sync_running():
                self.sync_engine.stop_sync()
                self.log_message.emit("⏹️ หยุดการซิงค์แล้ว", "info")
                return True
            else:
                self.log_message.emit("ℹ️ ไม่มีการซิงค์ที่กำลังทำงาน", "info")
                return False
        except Exception as e:
            self.log_message.emit(f"❌ ไม่สามารถหยุดการซิงค์: {str(e)}", "error")
            return False

    # Auto-sync Management
    def toggle_auto_sync(self, enabled, interval=3600):
        """Toggle automatic synchronization"""
        try:
            self.auto_sync_enabled = enabled

            if enabled:
                self.auto_sync_timer.start(interval * 1000)  # Convert to milliseconds
                self.log_message.emit(
                    f"⏰ เปิดการซิงค์อัตโนมัติ (ทุก {interval} วินาที)", "success"
                )
            else:
                self.auto_sync_timer.stop()
                self.log_message.emit("⏸️ หยุดการซิงค์อัตโนมัติ", "info")

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
            self.start_sync()
        else:
            self.log_message.emit("⏭️ ข้ามการซิงค์อัตโนมัติ (กำลังซิงค์อยู่)", "info")

    # Utility Methods
    def _validate_sync_config(self, config):
        """Validate configuration for sync operation"""
        # SharePoint validation
        if not all(
            [config.tenant_id, config.client_id, config.client_secret, config.site_url]
        ):
            return {"valid": False, "message": "กรุณากรอกข้อมูล SharePoint ให้ครบถ้วน"}

        if not config.list_name:
            return {"valid": False, "message": "กรุณาเลือกรายการ SharePoint"}

        # Database validation
        if config.database_type == "sqlserver":
            if not all([config.sql_server, config.sql_database, config.sql_table_name]):
                return {"valid": False, "message": "กรุณากรอกข้อมูล SQL Server ให้ครบถ้วน"}
        else:  # SQLite
            if not all([config.sqlite_file, config.sqlite_table_name]):
                return {"valid": False, "message": "กรุณากรอกข้อมูล SQLite ให้ครบถ้วน"}

        return {"valid": True, "message": "การตั้งค่าถูกต้อง"}

    def get_sync_status(self):
        """Get current sync status"""
        return {
            "is_running": self.sync_engine.is_sync_running(),
            "auto_sync_enabled": self.auto_sync_enabled,
            "auto_sync_interval": (
                self.auto_sync_timer.interval() // 1000
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
            self.log_message.emit("🧹 ล้างทรัพยากรเสร็จสิ้น", "info")

        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
