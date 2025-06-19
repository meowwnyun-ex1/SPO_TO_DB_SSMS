"""
Configuration Validation System - ระบบตรวจสอบความถูกต้องของการตั้งค่า
แยกออกจาก app_controller เพื่อให้ง่ายต่อการบำรุงรักษา
"""

import re
import sqlite3
import pyodbc
import requests
from typing import Dict, List, Optional
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
                    "กรอก URL ในรูปแบบ https://company.sharepoint.com/sites/sitename"
                ],
            )

        # Pattern สำหรับ SharePoint URL
        sp_pattern = r"^https://[a-zA-Z0-9-]+\.sharepoint\.com/sites/[a-zA-Z0-9-_]+/?$"

        if not re.match(sp_pattern, url):
            return ValidationResult(
                False,
                "Invalid SharePoint URL format",
                error_code="SP002",
                details={"provided_url": url},
                suggestions=[
                    "ใช้รูปแบบ: https://company.sharepoint.com/sites/sitename",
                    "ตรวจสอบว่าไม่มี path เพิ่มเติมหลัง site name",
                ],
            )

        return ValidationResult(True, "SharePoint URL format is valid")

    @staticmethod
    def validate_credentials(
        tenant_id: str, client_id: str, client_secret: str
    ) -> ValidationResult:
        """ตรวจสอบ credentials"""
        missing_fields = []

        if not tenant_id:
            missing_fields.append("Tenant ID")
        if not client_id:
            missing_fields.append("Client ID")
        if not client_secret:
            missing_fields.append("Client Secret")

        if missing_fields:
            return ValidationResult(
                False,
                f"Missing required fields: {', '.join(missing_fields)}",
                error_code="SP003",
                suggestions=[
                    "รับ credentials จาก Azure AD App Registration",
                    "ตรวจสอบ permissions: Sites.Read.All, Sites.ReadWrite.All",
                ],
            )

        # ตรวจสอบรูปแบบ GUID
        guid_pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"

        if not re.match(guid_pattern, tenant_id, re.IGNORECASE):
            return ValidationResult(
                False,
                "Invalid Tenant ID format (must be GUID)",
                error_code="SP004",
                suggestions=[
                    "Tenant ID ต้องเป็น GUID เช่น 12345678-1234-1234-1234-123456789012"
                ],
            )

        if not re.match(guid_pattern, client_id, re.IGNORECASE):
            return ValidationResult(
                False,
                "Invalid Client ID format (must be GUID)",
                error_code="SP005",
                suggestions=["Client ID ต้องเป็น GUID จาก Azure AD App Registration"],
            )

        return ValidationResult(True, "SharePoint credentials format is valid")

    @staticmethod
    def test_connection(
        url: str, tenant_id: str, client_id: str, client_secret: str
    ) -> ValidationResult:
        """ทดสอบการเชื่อมต่อจริง"""
        try:
            # ลองขอ access token
            domain = url.split("/")[2]
            token_url = (
                f"https://accounts.accesscontrol.windows.net/{tenant_id}/tokens/OAuth/2"
            )

            payload = {
                "grant_type": "client_credentials",
                "client_id": f"{client_id}@{tenant_id}",
                "client_secret": client_secret,
                "resource": f"00000003-0000-0ff1-ce00-000000000000/{domain}@{tenant_id}",
            }

            response = requests.post(token_url, data=payload, timeout=10)

            if response.status_code == 200:
                # ทดสอบเรียก API
                token = response.json().get("access_token")
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json;odata=verbose",
                }

                test_url = f"{url}/_api/web"
                test_response = requests.get(test_url, headers=headers, timeout=10)

                if test_response.status_code == 200:
                    return ValidationResult(True, "SharePoint connection successful")
                else:
                    return ValidationResult(
                        False,
                        f"SharePoint API test failed: {test_response.status_code}",
                        error_code="SP006",
                        details={"status_code": test_response.status_code},
                        suggestions=["ตรวจสอบ Site URL และ permissions"],
                    )
            else:
                error_data = (
                    response.json()
                    if response.headers.get("content-type", "").startswith(
                        "application/json"
                    )
                    else {}
                )
                return ValidationResult(
                    False,
                    f"Authentication failed: {response.status_code}",
                    error_code="SP007",
                    details={"auth_error": error_data},
                    suggestions=[
                        "ตรวจสอบ Tenant ID, Client ID, Client Secret",
                        "ตรวจสอบ App Registration permissions",
                    ],
                )

        except requests.exceptions.Timeout:
            return ValidationResult(
                False,
                "Connection timeout",
                error_code="SP008",
                suggestions=["ตรวจสอบการเชื่อมต่อ internet", "ลองใหม่อีกครั้ง"],
            )
        except Exception as e:
            return ValidationResult(
                False,
                f"Connection error: {str(e)}",
                error_code="SP009",
                suggestions=["ตรวจสอบ network settings", "ตรวจสอบ firewall"],
            )


class DatabaseValidator:
    """ตรวจสอบการตั้งค่าฐานข้อมูล"""

    @staticmethod
    def validate_sql_server_config(
        server: str, database: str, username: str, password: str
    ) -> ValidationResult:
        """ตรวจสอบการตั้งค่า SQL Server"""
        missing_fields = []

        if not server:
            missing_fields.append("Server")
        if not database:
            missing_fields.append("Database")
        if not username:
            missing_fields.append("Username")

        if missing_fields:
            return ValidationResult(
                False,
                f"Missing SQL Server fields: {', '.join(missing_fields)}",
                error_code="DB001",
                suggestions=["กรอกข้อมูลให้ครบทุกฟิลด์"],
            )

        # ตรวจสอบ server format
        server_pattern = r"^[a-zA-Z0-9.-]+(?:\\[a-zA-Z0-9]+)?(?:,[0-9]+)?$"
        if not re.match(server_pattern, server):
            return ValidationResult(
                False,
                "Invalid SQL Server format",
                error_code="DB002",
                suggestions=[
                    "รูปแบบที่ถูกต้อง: server\\instance หรือ server,port",
                    "ตัวอย่าง: localhost\\SQLEXPRESS หรือ server.com,1433",
                ],
            )

        return ValidationResult(True, "SQL Server configuration is valid")

    @staticmethod
    def validate_sqlite_config(file_path: str) -> ValidationResult:
        """ตรวจสอบการตั้งค่า SQLite"""
        if not file_path:
            return ValidationResult(
                False,
                "SQLite file path is required",
                error_code="DB003",
                suggestions=["ระบุ path ของไฟล์ SQLite"],
            )

        path = Path(file_path)

        # ตรวจสอบ extension
        if not file_path.endswith((".db", ".sqlite", ".sqlite3")):
            return ValidationResult(
                False,
                "Invalid SQLite file extension",
                error_code="DB004",
                suggestions=["ใช้นามสกุล .db, .sqlite หรือ .sqlite3"],
            )

        # ตรวจสอบ directory
        if not path.parent.exists():
            return ValidationResult(
                False,
                f"Directory does not exist: {path.parent}",
                error_code="DB005",
                suggestions=[f"สร้าง directory: {path.parent}"],
            )

        # ตรวจสอบสิทธิ์การเขียน
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            test_file = path.parent / "test_write.tmp"
            test_file.touch()
            test_file.unlink()
        except PermissionError:
            return ValidationResult(
                False,
                "No write permission to SQLite directory",
                error_code="DB006",
                suggestions=["ตรวจสอบสิทธิ์การเขียนในโฟลเดอร์"],
            )

        return ValidationResult(True, "SQLite configuration is valid")

    @staticmethod
    def test_sql_server_connection(
        server: str, database: str, username: str, password: str
    ) -> ValidationResult:
        """ทดสอบการเชื่อมต่อ SQL Server"""
        try:
            conn_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=yes;"
                f"Connection Timeout=30;"
            )

            conn = pyodbc.connect(conn_string)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()

            if result and result[0] == 1:
                conn.close()
                return ValidationResult(True, "SQL Server connection successful")
            else:
                conn.close()
                return ValidationResult(
                    False, "SQL Server test query failed", error_code="DB007"
                )

        except pyodbc.Error as e:
            error_msg = str(e)
            suggestions = []

            if "Login failed" in error_msg:
                suggestions = [
                    "ตรวจสอบ username และ password",
                    "ตรวจสอบ SQL Server Authentication",
                ]
            elif "Server not found" in error_msg:
                suggestions = ["ตรวจสอบ server name", "ตรวจสอบ SQL Server instance"]
            elif "timeout" in error_msg.lower():
                suggestions = ["ตรวจสอบ network connection", "เพิ่ม connection timeout"]
            else:
                suggestions = [
                    "ตรวจสอบ SQL Server configuration",
                    "ตรวจสอบ firewall settings",
                ]

            return ValidationResult(
                False,
                f"SQL Server connection failed: {error_msg}",
                error_code="DB008",
                suggestions=suggestions,
            )
        except Exception as e:
            return ValidationResult(
                False, f"Unexpected database error: {str(e)}", error_code="DB009"
            )

    @staticmethod
    def test_sqlite_connection(file_path: str) -> ValidationResult:
        """ทดสอบการเชื่อมต่อ SQLite"""
        try:
            # สร้าง directory ถ้าไม่มี
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            conn = sqlite3.connect(file_path, timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()

            if result and result[0] == 1:
                conn.close()
                return ValidationResult(True, "SQLite connection successful")
            else:
                conn.close()
                return ValidationResult(
                    False, "SQLite test query failed", error_code="DB010"
                )

        except sqlite3.Error as e:
            return ValidationResult(
                False,
                f"SQLite connection failed: {str(e)}",
                error_code="DB011",
                suggestions=["ตรวจสอบ file path และ permissions"],
            )
        except Exception as e:
            return ValidationResult(
                False, f"Unexpected SQLite error: {str(e)}", error_code="DB012"
            )


class ConfigValidator:
    """ตัวจัดการการตรวจสอบการตั้งค่าหลัก"""

    def __init__(self):
        self.sp_validator = SharePointValidator()
        self.db_validator = DatabaseValidator()

    def validate_all(self, config) -> Dict[str, ValidationResult]:
        """ตรวจสอบการตั้งค่าทั้งหมด"""
        results = {}

        # SharePoint validation
        results["sp_url"] = self.sp_validator.validate_url(config.sharepoint_site)
        results["sp_credentials"] = self.sp_validator.validate_credentials(
            config.tenant_id,
            config.sharepoint_client_id,
            config.sharepoint_client_secret,
        )

        # Database validation
        if config.database_type == "sqlserver":
            results["db_config"] = self.db_validator.validate_sql_server_config(
                config.sql_server,
                config.sql_database,
                config.sql_username,
                config.sql_password,
            )
        else:  # SQLite
            results["db_config"] = self.db_validator.validate_sqlite_config(
                config.sqlite_file
            )

        # Sync configuration
        results["sync_config"] = self._validate_sync_config(config)

        return results

    def test_connections(self, config) -> Dict[str, ValidationResult]:
        """ทดสอบการเชื่อมต่อจริง"""
        results = {}

        # Test SharePoint
        if all(
            [
                config.sharepoint_site,
                config.tenant_id,
                config.sharepoint_client_id,
                config.sharepoint_client_secret,
            ]
        ):
            results["sp_connection"] = self.sp_validator.test_connection(
                config.sharepoint_site,
                config.tenant_id,
                config.sharepoint_client_id,
                config.sharepoint_client_secret,
            )

        # Test Database
        if config.database_type == "sqlserver":
            if all([config.sql_server, config.sql_database, config.sql_username]):
                results["db_connection"] = self.db_validator.test_sql_server_connection(
                    config.sql_server,
                    config.sql_database,
                    config.sql_username,
                    config.sql_password,
                )
        else:  # SQLite
            if config.sqlite_file:
                results["db_connection"] = self.db_validator.test_sqlite_connection(
                    config.sqlite_file
                )

        return results

    def _validate_sync_config(self, config) -> ValidationResult:
        """ตรวจสอบการตั้งค่า sync"""
        issues = []

        if config.sync_interval < 60:
            issues.append("Sync interval ต้องไม่น้อยกว่า 60 วินาที")

        if config.batch_size < 1 or config.batch_size > 10000:
            issues.append("Batch size ต้องอยู่ระหว่าง 1-10000")

        if config.connection_timeout < 5:
            issues.append("Connection timeout ต้องไม่น้อยกว่า 5 วินาที")

        if issues:
            return ValidationResult(
                False,
                f"Sync configuration issues: {'; '.join(issues)}",
                error_code="SYNC001",
                suggestions=["ปรับค่าตามข้อแนะนำ", "ใช้ค่าเริ่มต้นที่แนะนำ"],
            )

        return ValidationResult(True, "Sync configuration is valid")

    def get_validation_summary(self, results: Dict[str, ValidationResult]) -> Dict:
        """สรุปผลการตรวจสอบ"""
        total_checks = len(results)
        passed_checks = sum(1 for result in results.values() if result.is_valid)
        failed_checks = total_checks - passed_checks

        errors = []
        warnings = []
        suggestions = []

        for check_name, result in results.items():
            if not result.is_valid:
                errors.append(f"{check_name}: {result.message}")
                if result.suggestions:
                    suggestions.extend(result.suggestions)

        return {
            "total_checks": total_checks,
            "passed": passed_checks,
            "failed": failed_checks,
            "success_rate": (
                (passed_checks / total_checks * 100) if total_checks > 0 else 0
            ),
            "errors": errors,
            "suggestions": suggestions,
            "overall_status": "valid" if failed_checks == 0 else "invalid",
        }


class ValidationCache:
    """แคชสำหรับเก็บผลการตรวจสอบ"""

    def __init__(self, ttl_seconds: int = 300):  # Cache 5 นาที
        self.cache = {}
        self.ttl = ttl_seconds

    def get(self, key: str) -> Optional[ValidationResult]:
        """ดึงผลการตรวจสอบจากแคช"""
        if key in self.cache:
            result, timestamp = self.cache[key]
            if (datetime.now() - timestamp).total_seconds() < self.ttl:
                return result
            else:
                del self.cache[key]
        return None

    def set(self, key: str, result: ValidationResult):
        """เก็บผลการตรวจสอบในแคช"""
        self.cache[key] = (result, datetime.now())

    def clear(self):
        """ล้างแคช"""
        self.cache.clear()


class SmartConfigValidator(ConfigValidator):
    """ตัวตรวจสอบการตั้งค่าอัจฉริยะพร้อมแคช"""

    def __init__(self, use_cache: bool = True):
        super().__init__()
        self.cache = ValidationCache() if use_cache else None

    def validate_with_cache(
        self, config, force_refresh: bool = False
    ) -> Dict[str, ValidationResult]:
        """ตรวจสอบการตั้งค่าพร้อมใช้แคช"""
        cache_key = self._generate_cache_key(config)

        if not force_refresh and self.cache:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.debug("Using cached validation result")
                return cached_result

        results = self.validate_all(config)

        if self.cache:
            self.cache.set(cache_key, results)

        return results

    def _generate_cache_key(self, config) -> str:
        """สร้าง cache key จาก config"""
        import hashlib

        key_data = f"{config.sharepoint_site}_{config.tenant_id}_{config.database_type}_{config.sql_server}_{config.sqlite_file}"
        return hashlib.md5(key_data.encode()).hexdigest()


# Helper functions สำหรับใช้งานง่าย
def quick_validate_sharepoint(
    url: str, tenant_id: str, client_id: str, client_secret: str
) -> ValidationResult:
    """ตรวจสอบ SharePoint แบบเร็ว"""
    validator = SharePointValidator()

    # ตรวจสอบ format ก่อน
    url_result = validator.validate_url(url)
    if not url_result.is_valid:
        return url_result

    cred_result = validator.validate_credentials(tenant_id, client_id, client_secret)
    if not cred_result.is_valid:
        return cred_result

    # ถ้า format ถูกต้อง ลองเชื่อมต่อ
    return validator.test_connection(url, tenant_id, client_id, client_secret)


def quick_validate_database(db_type: str, **kwargs) -> ValidationResult:
    """ตรวจสอบฐานข้อมูลแบบเร็ว"""
    validator = DatabaseValidator()

    if db_type.lower() == "sqlserver":
        config_result = validator.validate_sql_server_config(
            kwargs.get("server", ""),
            kwargs.get("database", ""),
            kwargs.get("username", ""),
            kwargs.get("password", ""),
        )
        if not config_result.is_valid:
            return config_result

        return validator.test_sql_server_connection(
            kwargs["server"], kwargs["database"], kwargs["username"], kwargs["password"]
        )

    elif db_type.lower() in ["sqlite", "sqlite3"]:
        config_result = validator.validate_sqlite_config(kwargs.get("file_path", ""))
        if not config_result.is_valid:
            return config_result

        return validator.test_sqlite_connection(kwargs["file_path"])

    else:
        return ValidationResult(
            False,
            f"Unsupported database type: {db_type}",
            error_code="DB013",
            suggestions=["ใช้ 'sqlserver' หรือ 'sqlite'"],
        )


# ทดสอบการทำงาน
if __name__ == "__main__":
    from datetime import datetime

    # ทดสอบ SharePoint validation
    sp_result = quick_validate_sharepoint(
        "https://company.sharepoint.com/sites/test",
        "12345678-1234-1234-1234-123456789012",
        "87654321-4321-4321-4321-210987654321",
        "secret123",
    )
    print(f"SharePoint validation: {sp_result.is_valid} - {sp_result.message}")

    # ทดสอบ SQLite validation
    sqlite_result = quick_validate_database("sqlite", file_path="test.db")
    print(f"SQLite validation: {sqlite_result.is_valid} - {sqlite_result.message}")
