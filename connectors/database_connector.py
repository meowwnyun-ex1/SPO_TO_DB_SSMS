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

logger = logging.getLogger(__name__)


class DatabaseConnector:
    def __init__(self, config):
        self.config = config
        self.engine = None
        self._create_engine()

    def _create_engine(self):
        try:
            if self.config.database_type == "sqlserver":
                connection_string = self._build_sqlserver_connection_string()
            elif self.config.database_type == "sqlite":
                connection_string = self._build_sqlite_connection_string()
            else:
                raise ValueError(
                    f"Unsupported database type: {self.config.database_type}"
                )

            self.engine = create_engine(
                connection_string, pool_pre_ping=True, pool_recycle=3600, echo=False
            )
            logger.info(f"Database engine created for {self.config.database_type}")

        except Exception as e:
            logger.error(f"Failed to create database engine: {str(e)}")
            raise

    def _build_sqlserver_connection_string(self) -> str:
        return (
            f"mssql+pyodbc://{self.config.sql_username}:"
            f"{self.config.sql_password}@{self.config.sql_server}/"
            f"{self.config.sql_database}?"
            f"driver=ODBC+Driver+17+for+SQL+Server&"
            f"timeout={self.config.connection_timeout}"
        )

    def _build_sqlite_connection_string(self) -> str:
        db_path = os.path.abspath(self.config.sqlite_file)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
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
        try:
            if self.config.database_type == "sqlite":
                return []

            with self.engine.connect() as conn:
                if self.config.database_type == "sqlserver":
                    result = conn.execute(
                        text(
                            "SELECT name FROM sys.databases "
                            "WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb') "
                            "ORDER BY name"
                        )
                    )
                else:
                    return []

                databases = [row[0] for row in result]
                logger.info(f"Found {len(databases)} databases")
                return databases

        except Exception as e:
            logger.error(f"Failed to get databases: {str(e)}")
            return []

    def get_tables(self) -> List[str]:
        try:
            with self.engine.connect() as conn:
                if self.config.database_type == "sqlserver":
                    result = conn.execute(
                        text(
                            f"SELECT TABLE_NAME FROM {self.config.sql_database}.INFORMATION_SCHEMA.TABLES "
                            "WHERE TABLE_TYPE = 'BASE TABLE' "
                            "ORDER BY TABLE_NAME"
                        )
                    )
                elif self.config.database_type == "sqlite":
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
        try:
            tables = self.get_tables()
            return table_name in tables
        except Exception as e:
            logger.error(f"Failed to check if table exists: {str(e)}")
            return False

    def create_table_if_not_exists(self, df: pd.DataFrame, table_name: str) -> bool:
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
        cleaned = name.replace(".", "_").replace(" ", "_").replace("-", "_")
        cleaned = "".join(c for c in cleaned if c.isalnum() or c == "_")
        if cleaned and cleaned[0].isdigit():
            cleaned = f"col_{cleaned}"
        if not cleaned:
            cleaned = "unnamed_column"
        return cleaned.lower()

    def insert_data(self, df: pd.DataFrame, table_name: str) -> int:
        try:
            df_copy = df.copy()
            df_copy["sync_timestamp"] = datetime.now()
            df_copy["sync_id"] = f"sync_{int(datetime.now().timestamp())}"
            df_copy.columns = [self._clean_column_name(col) for col in df_copy.columns]

            if (
                hasattr(self.config, "sql_truncate_before")
                and self.config.sql_truncate_before
            ):
                self.truncate_table(table_name)

            rows_inserted = df_copy.to_sql(
                table_name,
                self.engine,
                if_exists="append",
                index=False,
                method="multi",
                chunksize=self.config.batch_size,
            )

            logger.info(
                f"Successfully inserted {len(df_copy)} rows into table '{table_name}'"
            )
            return len(df_copy)

        except Exception as e:
            logger.error(f"Failed to insert data into table '{table_name}': {str(e)}")
            raise

    def truncate_table(self, table_name: str) -> bool:
        try:
            with self.engine.connect() as conn:
                if self.config.database_type == "sqlserver":
                    conn.execute(text(f"TRUNCATE TABLE [{table_name}]"))
                elif self.config.database_type == "sqlite":
                    conn.execute(text(f"DELETE FROM {table_name}"))
                conn.commit()

            logger.info(f"Successfully truncated table '{table_name}'")
            return True

        except Exception as e:
            logger.error(f"Failed to truncate table '{table_name}': {str(e)}")
            return False

    def close(self):
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")
