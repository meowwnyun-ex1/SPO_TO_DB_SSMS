import pandas as pd
from sqlalchemy import (
    create_engine,
    text,
    MetaData,
    Table,
    Column,
    String,
    DateTime,
    Integer,
)
from datetime import datetime
from typing import List
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class DatabaseConnector:
    def __init__(self, config):
        self.config = config
        self.engine = None
        self._create_engine()

    def _create_engine(self):
        try:
            if (
                self.config.database_type == "sqlserver"
                or self.config.db_type == "SQL Server"
            ):
                connection_string = self._build_sqlserver_connection_string()
            elif (
                self.config.database_type == "sqlite" or self.config.db_type == "SQLite"
            ):
                connection_string = self._build_sqlite_connection_string()
            else:
                raise ValueError(
                    f"Unsupported database type: {self.config.database_type}"
                )

            self.engine = create_engine(
                connection_string, pool_pre_ping=True, pool_recycle=3600, echo=False
            )
            logger.info(
                f"Database engine created for {self.config.database_type or self.config.db_type}"
            )

        except Exception as e:
            logger.error(f"Failed to create database engine: {str(e)}")
            raise

    def _build_sqlserver_connection_string(self) -> str:
        """สร้าง connection string สำหรับ SQL Server"""
        server = self.config.sql_server or self.config.db_host
        database = self.config.sql_database or self.config.db_name
        username = self.config.sql_username or self.config.db_username
        password = self.config.sql_password or self.config.db_password
        timeout = getattr(self.config, "connection_timeout", 30)

        return (
            f"mssql+pyodbc://{username}:{password}@{server}/"
            f"{database}?driver=ODBC+Driver+17+for+SQL+Server&"
            f"timeout={timeout}"
        )

    def _build_sqlite_connection_string(self) -> str:
        """สร้าง connection string สำหรับ SQLite"""
        sqlite_file = self.config.sqlite_file or "data.db"

        # แก้: สร้าง absolute path และสร้าง directory
        if not os.path.isabs(sqlite_file):
            sqlite_file = os.path.join(os.getcwd(), sqlite_file)

        db_path = Path(sqlite_file)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        return f"sqlite:///{db_path}"

    def test_connection(self) -> bool:
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as test"))
                test_value = result.fetchone()[0]
                logger.info(
                    f"Database connection test successful (returned: {test_value})"
                )
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False

    def get_databases(self) -> List[str]:
        """ดึงรายการ databases - SQL Server เท่านั้น"""
        try:
            db_type = self.config.database_type or self.config.db_type

            if db_type.lower() in ["sqlite"]:
                return []

            with self.engine.connect() as conn:
                result = conn.execute(
                    text(
                        "SELECT name FROM sys.databases "
                        "WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb') "
                        "ORDER BY name"
                    )
                )
                databases = [row[0] for row in result]
                logger.info(f"Found {len(databases)} databases")
                return databases

        except Exception as e:
            logger.error(f"Failed to get databases: {str(e)}")
            return []

    def get_tables(self) -> List[str]:
        """ดึงรายการ tables"""
        try:
            db_type = self.config.database_type or self.config.db_type

            with self.engine.connect() as conn:
                if db_type.lower() in ["sqlserver", "sql server"]:
                    database_name = self.config.sql_database or self.config.db_name
                    result = conn.execute(
                        text(
                            f"SELECT TABLE_NAME FROM {database_name}.INFORMATION_SCHEMA.TABLES "
                            "WHERE TABLE_TYPE = 'BASE TABLE' "
                            "ORDER BY TABLE_NAME"
                        )
                    )
                elif db_type.lower() == "sqlite":
                    result = conn.execute(
                        text(
                            "SELECT name FROM sqlite_master "
                            "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
                            "ORDER BY name"
                        )
                    )
                else:
                    return []

                tables = [row[0] for row in result]
                logger.info(f"Found {len(tables)} tables")
                return tables

        except Exception as e:
            logger.error(f"Failed to get tables: {str(e)}")
            return []

    def table_exists(self, table_name: str) -> bool:
        """ตรวจสอบว่า table มีอยู่หรือไม่"""
        try:
            tables = self.get_tables()
            return table_name in tables
        except Exception as e:
            logger.error(f"Failed to check if table exists: {str(e)}")
            return False

    def create_table_if_not_exists(self, df: pd.DataFrame, table_name: str) -> bool:
        """สร้าง table ถ้ายังไม่มี"""
        try:
            if self.table_exists(table_name):
                logger.info(f"Table '{table_name}' already exists")
                return False

            metadata = MetaData()
            columns = [
                Column("id", Integer, primary_key=True, autoincrement=True),
                Column("sync_timestamp", DateTime, default=datetime.now),
                Column("sync_id", String(50)),
            ]

            # สร้าง columns จาก DataFrame
            for col_name in df.columns:
                clean_name = self._clean_column_name(col_name)
                if df[col_name].dtype == "object":
                    col_type = String(500)
                elif df[col_name].dtype in ["int64", "int32"]:
                    col_type = Integer
                else:
                    col_type = String(500)
                columns.append(Column(clean_name, col_type))

            table = Table(table_name, metadata, *columns)
            metadata.create_all(self.engine)
            logger.info(
                f"Successfully created table '{table_name}' with {len(columns)} columns"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to create table '{table_name}': {str(e)}")
            raise

    def _clean_column_name(self, name: str) -> str:
        """ทำความสะอาดชื่อ column"""
        cleaned = name.replace(".", "_").replace(" ", "_").replace("-", "_")
        cleaned = "".join(c for c in cleaned if c.isalnum() or c == "_")
        if cleaned and cleaned[0].isdigit():
            cleaned = f"col_{cleaned}"
        if not cleaned:
            cleaned = "unnamed_column"
        return cleaned.lower()

    def insert_data(self, df: pd.DataFrame, table_name: str) -> int:
        """บันทึกข้อมูลลงฐานข้อมูล"""
        try:
            df_copy = df.copy()
            df_copy["sync_timestamp"] = datetime.now()
            df_copy["sync_id"] = f"sync_{int(datetime.now().timestamp())}"
            df_copy.columns = [self._clean_column_name(col) for col in df_copy.columns]

            # ตรวจสอบการ truncate
            if getattr(self.config, "sql_truncate_before", False):
                self.truncate_table(table_name)

            batch_size = getattr(self.config, "batch_size", 1000)

            rows_inserted = df_copy.to_sql(
                table_name,
                self.engine,
                if_exists="append",
                index=False,
                method="multi",
                chunksize=batch_size,
            )

            logger.info(
                f"Successfully inserted {len(df_copy)} rows into table '{table_name}'"
            )
            return len(df_copy)

        except Exception as e:
            logger.error(f"Failed to insert data into table '{table_name}': {str(e)}")
            raise

    def truncate_table(self, table_name: str) -> bool:
        """ล้างข้อมูลใน table"""
        try:
            db_type = self.config.database_type or self.config.db_type

            with self.engine.connect() as conn:
                if db_type.lower() in ["sqlserver", "sql server"]:
                    conn.execute(text(f"TRUNCATE TABLE [{table_name}]"))
                elif db_type.lower() == "sqlite":
                    conn.execute(text(f"DELETE FROM {table_name}"))
                conn.commit()

            logger.info(f"Successfully truncated table '{table_name}'")
            return True

        except Exception as e:
            logger.error(f"Failed to truncate table '{table_name}': {str(e)}")
            return False

    def get_table_info(self, table_name: str) -> dict:
        """ดึงข้อมูลเกี่ยวกับ table"""
        try:
            db_type = self.config.database_type or self.config.db_type

            with self.engine.connect() as conn:
                if db_type.lower() in ["sqlserver", "sql server"]:
                    # ดึงจำนวน rows
                    count_result = conn.execute(
                        text(f"SELECT COUNT(*) FROM [{table_name}]")
                    )
                    row_count = count_result.fetchone()[0]

                    # ดึงข้อมูล columns
                    columns_result = conn.execute(
                        text(
                            f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'"
                        )
                    )
                    columns = [
                        {"name": row[0], "type": row[1]} for row in columns_result
                    ]

                elif db_type.lower() == "sqlite":
                    # ดึงจำนวน rows
                    count_result = conn.execute(
                        text(f"SELECT COUNT(*) FROM {table_name}")
                    )
                    row_count = count_result.fetchone()[0]

                    # ดึงข้อมูล columns
                    columns_result = conn.execute(
                        text(f"PRAGMA table_info({table_name})")
                    )
                    columns = [
                        {"name": row[1], "type": row[2]} for row in columns_result
                    ]
                else:
                    return {}

                return {
                    "table_name": table_name,
                    "row_count": row_count,
                    "columns": columns,
                    "database_type": db_type,
                }

        except Exception as e:
            logger.error(f"Failed to get table info for '{table_name}': {str(e)}")
            return {}

    def close(self):
        """ปิดการเชื่อมต่อฐานข้อมูล"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")
