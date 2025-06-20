# utils/excel_import_handler.py
"""
Excel Import Handler - จัดการการ import ข้อมูลจาก Excel
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Any
from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity

logger = logging.getLogger(__name__)


class ExcelImportHandler:
    """จัดการการ import ข้อมูลจาก Excel"""

    def __init__(self):
        self.supported_formats = [".xlsx", ".xls", ".csv"]
        self.max_file_size_mb = 50  # จำกัดขนาดไฟล์ 50MB

    @handle_exceptions(ErrorCategory.DATA, ErrorSeverity.MEDIUM)
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """ตรวจสอบไฟล์ Excel"""
        path = Path(file_path)

        validation_result = {
            "is_valid": False,
            "error_message": "",
            "file_info": {},
            "preview_data": None,
        }

        # ตรวจสอบว่าไฟล์มีอยู่
        if not path.exists():
            validation_result["error_message"] = f"File not found: {file_path}"
            return validation_result

        # ตรวจสอบนามสกุลไฟล์
        if path.suffix.lower() not in self.supported_formats:
            validation_result["error_message"] = (
                f"Unsupported file format. Supported: {', '.join(self.supported_formats)}"
            )
            return validation_result

        # ตรวจสอบขนาดไฟล์
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            validation_result["error_message"] = (
                f"File too large: {file_size_mb:.1f}MB (max: {self.max_file_size_mb}MB)"
            )
            return validation_result

        # ลองอ่านไฟล์
        try:
            df = self._read_excel_file(file_path)
            if df.empty:
                validation_result["error_message"] = (
                    "File is empty or contains no readable data"
                )
                return validation_result

            validation_result.update(
                {
                    "is_valid": True,
                    "file_info": {
                        "file_size_mb": file_size_mb,
                        "total_rows": len(df),
                        "total_columns": len(df.columns),
                        "columns": list(df.columns),
                        "sample_data": df.head(5).to_dict("records"),
                    },
                    "preview_data": df.head(10),  # Preview 10 rows
                }
            )

            logger.info(
                f"Excel file validated: {path.name} ({len(df)} rows, {len(df.columns)} columns)"
            )

        except Exception as e:
            validation_result["error_message"] = f"Error reading file: {str(e)}"
            logger.error(f"Excel validation failed: {e}")

        return validation_result

    @handle_exceptions(ErrorCategory.DATA, ErrorSeverity.HIGH)
    def _read_excel_file(self, file_path: str) -> pd.DataFrame:
        """อ่านไฟล์ Excel/CSV"""
        path = Path(file_path)

        try:
            if path.suffix.lower() == ".csv":
                # ลองหลายๆ encoding สำหรับ CSV
                encodings = ["utf-8", "utf-8-sig", "cp1252", "iso-8859-1"]
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        logger.info(f"CSV read successfully with encoding: {encoding}")
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ValueError("Could not read CSV with any supported encoding")
            else:
                # Excel files
                df = pd.read_excel(
                    file_path, engine="openpyxl" if path.suffix == ".xlsx" else "xlrd"
                )

            # ทำความสะอาดข้อมูล
            df = self._clean_dataframe(df)
            return df

        except Exception as e:
            logger.error(f"Failed to read Excel file {file_path}: {e}")
            raise

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """ทำความสะอาดข้อมูล DataFrame"""
        # ลบแถวที่ว่างทั้งหมด
        df = df.dropna(how="all")

        # ทำความสะอาดชื่อ columns
        df.columns = [str(col).strip() for col in df.columns]

        # แทนที่ NaN ด้วย empty string สำหรับ text columns
        df = df.fillna("")

        return df

    @handle_exceptions(ErrorCategory.DATA, ErrorSeverity.HIGH)
    def prepare_for_sharepoint(
        self, df: pd.DataFrame, list_name: str = "ImportedData"
    ) -> Dict[str, Any]:
        """เตรียมข้อมูลสำหรับ SharePoint"""
        result = {"success": False, "data": None, "mapping": {}, "warnings": []}

        try:
            # ทำความสะอาดชื่อ columns สำหรับ SharePoint
            clean_columns = {}
            for col in df.columns:
                clean_col = self._clean_sharepoint_column_name(col)
                clean_columns[col] = clean_col

            # เปลี่ยนชื่อ columns
            df_clean = df.rename(columns=clean_columns)

            # จำกัดความยาวข้อมูลสำหรับ SharePoint (255 characters per field)
            for col in df_clean.columns:
                if df_clean[col].dtype == "object":
                    df_clean[col] = df_clean[col].astype(str).str[:255]

            result.update(
                {
                    "success": True,
                    "data": df_clean,
                    "mapping": clean_columns,
                    "warnings": (
                        [f"Data truncated to 255 characters per field"]
                        if any(
                            df[col].astype(str).str.len().max() > 255
                            for col in df.columns
                            if df[col].dtype == "object"
                        )
                        else []
                    ),
                }
            )

            logger.info(f"Data prepared for SharePoint: {len(df_clean)} rows")

        except Exception as e:
            result["warnings"].append(f"Error preparing data: {str(e)}")
            logger.error(f"SharePoint preparation failed: {e}")

        return result

    def _clean_sharepoint_column_name(self, name: str) -> str:
        """ทำความสะอาดชื่อ column สำหรับ SharePoint"""
        # SharePoint field name requirements
        clean_name = str(name).strip()

        # แทนที่ตัวอักษรที่ไม่รองรับ
        invalid_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|", "#", "%"]
        for char in invalid_chars:
            clean_name = clean_name.replace(char, "_")

        # ไม่ให้ขึ้นต้นด้วยตัวเลข
        if clean_name and clean_name[0].isdigit():
            clean_name = f"Col_{clean_name}"

        # จำกัดความยาว
        clean_name = clean_name[:32]

        return clean_name or "Column"

    @handle_exceptions(ErrorCategory.DATA, ErrorSeverity.HIGH)
    def prepare_for_sql(
        self, df: pd.DataFrame, table_name: str = "imported_data"
    ) -> Dict[str, Any]:
        """เตรียมข้อมูลสำหรับ SQL Database"""
        result = {
            "success": False,
            "data": None,
            "mapping": {},
            "sql_types": {},
            "warnings": [],
        }

        try:
            # ทำความสะอาดชื่อ columns สำหรับ SQL
            clean_columns = {}
            sql_types = {}

            for col in df.columns:
                clean_col = self._clean_sql_column_name(col)
                clean_columns[col] = clean_col

                # กำหนดประเภทข้อมูล SQL
                sql_types[clean_col] = self._infer_sql_type(df[col])

            # เปลี่ยนชื่อ columns
            df_clean = df.rename(columns=clean_columns)

            # แปลงประเภทข้อมูล
            for col, sql_type in sql_types.items():
                if col in df_clean.columns:
                    try:
                        if sql_type.startswith("INT"):
                            df_clean[col] = (
                                pd.to_numeric(df_clean[col], errors="coerce")
                                .fillna(0)
                                .astype(int)
                            )
                        elif sql_type.startswith("FLOAT"):
                            df_clean[col] = pd.to_numeric(
                                df_clean[col], errors="coerce"
                            ).fillna(0.0)
                        elif sql_type.startswith("DATE"):
                            df_clean[col] = pd.to_datetime(
                                df_clean[col], errors="coerce"
                            )
                        else:  # VARCHAR/TEXT
                            df_clean[col] = df_clean[col].astype(str)
                    except Exception as e:
                        result["warnings"].append(
                            f"Type conversion warning for {col}: {str(e)}"
                        )

            result.update(
                {
                    "success": True,
                    "data": df_clean,
                    "mapping": clean_columns,
                    "sql_types": sql_types,
                    "warnings": result["warnings"],
                }
            )

            logger.info(f"Data prepared for SQL: {len(df_clean)} rows")

        except Exception as e:
            result["warnings"].append(f"Error preparing data: {str(e)}")
            logger.error(f"SQL preparation failed: {e}")

        return result

    def _clean_sql_column_name(self, name: str) -> str:
        """ทำความสะอาดชื่อ column สำหรับ SQL"""
        clean_name = str(name).strip().lower()

        # แทนที่ช่องว่างและอักขระพิเศษด้วย underscore
        import re

        clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", clean_name)

        # ลบ underscore ที่ซ้ำกัน
        clean_name = re.sub(r"_+", "_", clean_name)

        # ไม่ให้ขึ้นต้นด้วยตัวเลข
        if clean_name and clean_name[0].isdigit():
            clean_name = f"col_{clean_name}"

        # จำกัดความยาว
        clean_name = clean_name[:63]  # PostgreSQL limit

        return clean_name or "column"

    def _infer_sql_type(self, series: pd.Series) -> str:
        """กำหนดประเภทข้อมูล SQL จาก pandas Series"""
        # ลองแปลงเป็นตัวเลข
        numeric_series = pd.to_numeric(series, errors="coerce")

        if not numeric_series.isna().all():
            # เป็นตัวเลข
            if (numeric_series == numeric_series.astype(int)).all():
                return "INT"
            else:
                return "FLOAT"

        # ลองแปลงเป็นวันที่
        try:
            date_series = pd.to_datetime(series, errors="coerce")
            if not date_series.isna().all():
                return "DATETIME"
        except:
            pass

        # ตรวจสอบความยาวข้อความ
        max_length = series.astype(str).str.len().max()
        if max_length <= 255:
            return f"VARCHAR({max_length})"
        else:
            return "TEXT"

    def get_import_summary(
        self, validation_result: Dict, preparation_result: Dict
    ) -> Dict[str, Any]:
        """สร้างสรุปการ import"""
        return {
            "file_info": validation_result.get("file_info", {}),
            "preparation_success": preparation_result.get("success", False),
            "column_mapping": preparation_result.get("mapping", {}),
            "warnings": preparation_result.get("warnings", []),
            "ready_for_import": validation_result.get("is_valid", False)
            and preparation_result.get("success", False),
        }
