"""
Configuration Validation System - ระบบตรวจสอบความถูกต้องของการตั้งค่า
แยกออกจาก app_controller เพื่อให้ง่ายต่อการบำรุงรักษา
"""

import re
import sqlite3
import pyodbc  # Might not be directly used if SQLAlchemy handles, but useful for driver check
from typing import Dict, List
from dataclasses import dataclass
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """ผลการตรวจสอบ"""

    is_valid: bool
    message: str
    details: Dict = None
    suggestions: List[str] = None
    error_code: str = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.suggestions is None:
            self.suggestions = []


class SharePointValidator:
    """ตรวจสอบการตั้งค่า SharePoint"""

    @staticmethod
    def validate_url(url: str) -> ValidationResult:
        """ตรวจสอบ URL format"""
        if not url:
            return ValidationResult(
                False,
                "SharePoint URL is required",
                error_code="SP001",
                suggestions=[
                    "กรอก URL ในรูปแบบ https://company.sharepoint.com/sites/sitename หรือ https://company.sharepoint.com"
                ],
            )

        # Pattern สำหรับ SharePoint URL (รองรับทั้ง site collection และ root site)
        sp_pattern = (
            r"^https:\/\/[a-zA-Z0-9-]+\.sharepoint\.com(\/sites\/[a-zA-Z0-9_-]+)?$"
        )
        if not re.match(sp_pattern, url):
            return ValidationResult(
                False,
                f"Invalid SharePoint URL format: {url}",
                error_code="SP002",
                suggestions=[
                    "URL ต้องขึ้นต้นด้วย 'https://' และเป็นโดเมน 'sharepoint.com'",
                    "ตัวอย่าง: https://yourdomain.sharepoint.com/sites/YourSite หรือ https://yourdomain.sharepoint.com",
                ],
            )
        return ValidationResult(True, "SharePoint URL is valid")

    @staticmethod
    def validate_client_credentials(
        client_id: str, client_secret: str, tenant_id: str
    ) -> ValidationResult:
        """ตรวจสอบ Client ID, Client Secret, Tenant ID"""
        if not client_id:
            return ValidationResult(
                False, "SharePoint Client ID is required", error_code="SP003"
            )
        if not client_secret:
            return ValidationResult(
                False, "SharePoint Client Secret is required", error_code="SP004"
            )
        if not tenant_id:
            return ValidationResult(
                False, "SharePoint Tenant ID is required", error_code="SP005"
            )

        # Basic format validation for GUIDs (Client ID, Tenant ID)
        guid_pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
        if not re.match(guid_pattern, client_id):
            return ValidationResult(
                False, "Invalid Client ID format. Must be a GUID.", error_code="SP006"
            )
        if not re.match(guid_pattern, tenant_id):
            return ValidationResult(
                False, "Invalid Tenant ID format. Must be a GUID.", error_code="SP007"
            )

        return ValidationResult(True, "SharePoint credentials are valid")

    @staticmethod
    def validate_list_name(list_name: str) -> ValidationResult:
        """ตรวจสอบชื่อ List"""
        if not list_name:
            return ValidationResult(
                False, "SharePoint List Name is required", error_code="SP008"
            )
        # Add more specific validation if SharePoint list names have character restrictions
        return ValidationResult(True, "SharePoint List Name is valid")


class DatabaseValidator:
    """ตรวจสอบการตั้งค่า Database"""

    @staticmethod
    def validate_sqlserver_config(
        server: str, database: str, username: str, password: str
    ) -> ValidationResult:
        """ตรวจสอบ SQL Server config fields"""
        if not server:
            return ValidationResult(
                False, "SQL Server address is required", error_code="DB001"
            )
        if not database:
            return ValidationResult(
                False, "SQL Database name is required", error_code="DB002"
            )
        if not username:
            return ValidationResult(
                False, "SQL Username is required", error_code="DB003"
            )
        if not password:
            return ValidationResult(
                False, "SQL Password is required", error_code="DB004"
            )
        return ValidationResult(True, "SQL Server configuration fields are valid")

    @staticmethod
    def validate_sqlite_config(file_path: str) -> ValidationResult:
        """ตรวจสอบ SQLite config fields"""
        if not file_path:
            return ValidationResult(
                False, "SQLite database file path is required", error_code="DB005"
            )
        # Ensure it's a valid path format
        try:
            p = Path(file_path)
            # Check if directory is writable if file doesn't exist, or file is readable/writable if it exists
            if not p.parent.exists():
                return ValidationResult(
                    False,
                    f"Directory for SQLite file does not exist: {p.parent}",
                    error_code="DB006",
                )
            if not (p.parent.is_dir() and os.access(p.parent, os.W_OK)):
                return ValidationResult(
                    False,
                    f"Directory for SQLite file is not writable: {p.parent}",
                    error_code="DB007",
                )
        except Exception as e:
            return ValidationResult(
                False, f"Invalid SQLite file path: {e}", error_code="DB008"
            )
        return ValidationResult(True, "SQLite configuration fields are valid")

    @staticmethod
    def test_sql_server_connection(
        server: str, database: str, username: str, password: str
    ) -> ValidationResult:
        """ทดสอบการเชื่อมต่อ SQL Server โดยตรง"""
        try:
            # Use pyodbc for direct testing outside of SQLAlchemy
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};DATABASE={database};UID={username};PWD={password}"
            )
            with pyodbc.connect(conn_str, timeout=10) as conn:  # Short timeout for test
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
            return ValidationResult(True, "SQL Server connection successful.")
        except pyodbc.Error as e:
            sqlstate = e.args[0]
            if sqlstate == "08001":  # SQLSTATE for connection errors
                return ValidationResult(
                    False,
                    f"SQL Server connection failed: Host or port unreachable.",
                    error_code="DB009",
                    suggestions=[
                        "ตรวจสอบ Server Address และ Port",
                        "ตรวจสอบ Firewall",
                        "ตรวจสอบ Network",
                    ],
                )
            elif sqlstate == "28000":  # SQLSTATE for authentication errors
                return ValidationResult(
                    False,
                    f"SQL Server authentication failed: Invalid username or password.",
                    error_code="DB010",
                    suggestions=["ตรวจสอบ Username และ Password"],
                )
            else:
                return ValidationResult(
                    False,
                    f"SQL Server connection failed: {e}",
                    error_code="DB011",
                    suggestions=["ตรวจสอบการตั้งค่า SQL Server", "ตรวจสอบ ODBC Driver"],
                )
        except Exception as e:
            return ValidationResult(
                False,
                f"An unexpected error occurred during SQL Server connection test: {e}",
                error_code="DB012",
            )

    @staticmethod
    def test_sqlite_connection(file_path: str) -> ValidationResult:
        """ทดสอบการเชื่อมต่อ SQLite โดยตรง"""
        try:
            # Attempt to connect and close to test file access
            with sqlite3.connect(file_path, timeout=5) as conn:
                conn.close()
            return ValidationResult(
                True, f"SQLite connection to '{file_path}' successful."
            )
        except sqlite3.Error as e:
            return ValidationResult(
                False,
                f"SQLite connection failed: {e}",
                error_code="DB013",
                suggestions=["ตรวจสอบ Path ไฟล์ SQLite", "ตรวจสอบสิทธิ์การเข้าถึงไฟล์"],
            )
        except Exception as e:
            return ValidationResult(
                False,
                f"An unexpected error occurred during SQLite connection test: {e}",
                error_code="DB014",
            )


class GeneralValidator:
    """General validation for application settings."""

    @staticmethod
    def validate_sync_interval(interval: int) -> ValidationResult:
        """Validate synchronization interval."""
        if not isinstance(interval, int) or interval <= 0:
            return ValidationResult(
                False, "Sync interval must be a positive integer.", error_code="GEN001"
            )
        return ValidationResult(True, "Sync interval is valid.")

    @staticmethod
    def validate_batch_size(batch_size: int) -> ValidationResult:
        """Validate batch size for data operations."""
        if not isinstance(batch_size, int) or batch_size <= 0:
            return ValidationResult(
                False, "Batch size must be a positive integer.", error_code="GEN002"
            )
        return ValidationResult(True, "Batch size is valid.")

    @staticmethod
    def validate_mapping(mapping: Dict) -> ValidationResult:
        """Validate a field mapping dictionary."""
        if not isinstance(mapping, dict) or not mapping:
            return ValidationResult(
                False, "Field mapping cannot be empty.", error_code="GEN003"
            )
        for key, value in mapping.items():
            if not isinstance(key, str) or not key.strip():
                return ValidationResult(
                    False,
                    f"Mapping key '{key}' is invalid (must be non-empty string).",
                    error_code="GEN004",
                )
            if not isinstance(value, str) or not value.strip():
                return ValidationResult(
                    False,
                    f"Mapping value for key '{key}' is invalid (must be non-empty string).",
                    error_code="GEN005",
                )
        return ValidationResult(True, "Field mapping is valid.")


def quick_validate_sharepoint(
    url: str, client_id: str, client_secret: str, tenant_id: str, list_name: str
) -> ValidationResult:
    """Quick validation for SharePoint settings."""
    result = SharePointValidator.validate_url(url)
    if not result.is_valid:
        return result
    result = SharePointValidator.validate_client_credentials(
        client_id, client_secret, tenant_id
    )
    if not result.is_valid:
        return result
    result = SharePointValidator.validate_list_name(list_name)
    if not result.is_valid:
        return result
    return ValidationResult(True, "All SharePoint basic configurations are valid.")


def quick_validate_database(db_type: str, **kwargs) -> ValidationResult:
    """Quick validation for database settings based on type."""
    if db_type.lower() == "sqlserver":
        config_result = DatabaseValidator.validate_sqlserver_config(
            kwargs.get("server", ""),
            kwargs.get("database", ""),
            kwargs.get("username", ""),
            kwargs.get("password", ""),
        )
        if not config_result.is_valid:
            return config_result

        # This part should ideally be in a connection test, not pure config validation
        # return DatabaseValidator.test_sql_server_connection(
        #     kwargs["server"], kwargs["database"], kwargs["username"], kwargs["password"]
        # )
        return ValidationResult(
            True, "SQL Server configuration fields are valid for quick check."
        )

    elif db_type.lower() in ["sqlite", "sqlite3"]:
        config_result = DatabaseValidator.validate_sqlite_config(
            kwargs.get("file_path", "")
        )
        if not config_result.is_valid:
            return config_result

        # This part should ideally be in a connection test, not pure config validation
        # return DatabaseValidator.test_sqlite_connection(kwargs["file_path"])
        return ValidationResult(
            True, "SQLite configuration fields are valid for quick check."
        )

    else:
        return ValidationResult(
            False,
            f"Unsupported database type: {db_type}",
            error_code="DB015",
            suggestions=["ใช้ 'sqlserver' หรือ 'sqlite'"],
        )


# ทดสอบการทำงาน
if __name__ == "__main__":
    from datetime import datetime

    print("--- SharePoint Validation Tests ---")
    # Valid
    sp_result = quick_validate_sharepoint(
        "https://company.sharepoint.com/sites/test",
        "12345678-1234-1234-1234-123456789012",
        "some_secret",
        "87654321-4321-4321-4321-210987654321",
        "MyList",
    )
    print(f"Valid SharePoint Config: {sp_result.is_valid} - {sp_result.message}")

    # Invalid URL
    sp_result = quick_validate_sharepoint(
        "http://invalid.com",
        "12345678-1234-1234-1234-123456789012",
        "some_secret",
        "87654321-4321-4321-4321-210987654321",
        "MyList",
    )
    print(f"Invalid URL: {sp_result.is_valid} - {sp_result.message}")

    # Missing Client ID
    sp_result = quick_validate_sharepoint(
        "https://company.sharepoint.com/sites/test",
        "",
        "some_secret",
        "87654321-4321-4321-4321-210987654321",
        "MyList",
    )
    print(f"Missing Client ID: {sp_result.is_valid} - {sp_result.message}")

    print("\n--- Database Validation Tests ---")
    # Valid SQL Server (config check only, not connection)
    db_result = quick_validate_database(
        "sqlserver",
        server="localhost",
        database="mydb",
        username="user",
        password="pwd",
    )
    print(f"Valid SQL Server Config: {db_result.is_valid} - {db_result.message}")

    # Missing SQL Server Username
    db_result = quick_validate_database(
        "sqlserver", server="localhost", database="mydb", username="", password="pwd"
    )
    print(f"Missing SQL Username: {db_result.is_valid} - {db_result.message}")

    # Valid SQLite (config check only, not connection)
    db_result = quick_validate_database("sqlite", file_path="test_db.db")
    print(f"Valid SQLite Config: {db_result.is_valid} - {db_result.message}")

    # Missing SQLite file path
    db_result = quick_validate_database("sqlite", file_path="")
    print(f"Missing SQLite Path: {db_result.is_valid} - {db_result.message}")

    print("\n--- General Validation Tests ---")
    print(
        f"Valid Sync Interval (60): {GeneralValidator.validate_sync_interval(60).is_valid}"
    )
    print(
        f"Invalid Sync Interval (0): {GeneralValidator.validate_sync_interval(0).is_valid}"
    )
    print(
        f"Valid Batch Size (100): {GeneralValidator.validate_batch_size(100).is_valid}"
    )
    print(
        f"Invalid Batch Size (-1): {GeneralValidator.validate_batch_size(-1).is_valid}"
    )

    valid_mapping = {"SharePointField": "SQLColumn", "AnotherSPField": "AnotherSQLCol"}
    invalid_mapping_empty = {}
    invalid_mapping_value = {"SP": ""}
    print(f"Valid Mapping: {GeneralValidator.validate_mapping(valid_mapping).is_valid}")
    print(
        f"Invalid Empty Mapping: {GeneralValidator.validate_mapping(invalid_mapping_empty).is_valid}"
    )
    print(
        f"Invalid Mapping Value: {GeneralValidator.validate_mapping(invalid_mapping_value).is_valid}"
    )

    print("\n--- Direct Connection Tests (requires actual drivers and servers) ---")
    # For these tests, you need actual SQL Server/SQLite to be set up.
    # try:
    #     print(f"SQL Server Live Test: {DatabaseValidator.test_sql_server_connection('your_server', 'your_db', 'your_user', 'your_pass').is_valid}")
    # except Exception as e:
    #     print(f"SQL Server Live Test Failed: {e}")

    # try:
    #     Path("temp_test.db").touch()
    #     print(f"SQLite Live Test: {DatabaseValidator.test_sqlite_connection('temp_test.db').is_valid}")
    #     Path("temp_test.db").unlink()
    # except Exception as e:
    #     print(f"SQLite Live Test Failed: {e}")
