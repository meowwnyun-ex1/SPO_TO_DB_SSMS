# db.py
import pyodbc
import sqlite3
import pandas as pd
from datetime import datetime
import logging
from typing import List
from config import Config

logger = logging.getLogger(__name__)


class DatabaseConnector:
    def __init__(self, config: Config):
        self.config = config

    def test_connection(self) -> bool:
        """Test database connection based on config"""
        if self.config.database_type == "sqlserver":
            return self._test_sql_connection()
        else:
            return self._test_sqlite_connection()

    def _test_sql_connection(self) -> bool:
        """Test SQL Server connection"""
        try:
            conn = self._get_sql_connection()
            conn.close()
            logger.info("SQL Server connection test successful")
            return True
        except Exception as e:
            logger.error(f"SQL Server connection test failed: {str(e)}")
            raise

    def _test_sqlite_connection(self) -> bool:
        """Test SQLite connection"""
        try:
            conn = self._get_sqlite_connection()
            conn.close()
            logger.info("SQLite connection test successful")
            return True
        except Exception as e:
            logger.error(f"SQLite connection test failed: {str(e)}")
            raise

    def get_databases(self) -> List[str]:
        """Get available databases (SQL Server only)"""
        if self.config.database_type != "sqlserver":
            return []

        try:
            conn = pyodbc.connect(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.config.sql_server};"
                f"UID={self.config.sql_username};"
                f"PWD={self.config.sql_password};"
                "Trusted_Connection=no;"
            )
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sys.databases WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb')"
            )
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching databases: {str(e)}")
            raise

    def get_tables(self) -> List[str]:
        """Get available tables"""
        if self.config.database_type == "sqlserver":
            return self._get_sql_tables()
        else:
            return self._get_sqlite_tables()

    def _get_sql_tables(self) -> List[str]:
        """Get tables from SQL Server"""
        try:
            conn = self._get_sql_connection()
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT TABLE_NAME 
                FROM {self.config.sql_database}.INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
            """
            )
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching SQL Server tables: {str(e)}")
            raise

    def _get_sqlite_tables(self) -> List[str]:
        """Get tables from SQLite"""
        try:
            conn = self._get_sqlite_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching SQLite tables: {str(e)}")
            raise

    def create_table(self, df: pd.DataFrame, table_name: str) -> bool:
        """Create table based on DataFrame structure"""
        if self.config.database_type == "sqlserver":
            return self._create_sql_table(df, table_name)
        else:
            return self._create_sqlite_table(df, table_name)

    def _create_sql_table(self, df: pd.DataFrame, table_name: str) -> bool:
        """Create SQL Server table"""
        conn = None
        try:
            conn = self._get_sql_connection()
            cursor = conn.cursor()

            # Check if table exists
            cursor.execute(
                f"""
                SELECT COUNT(*) 
                FROM {self.config.sql_database}.INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = '{table_name}'
            """
            )
            exists = cursor.fetchone()[0] > 0

            if exists:
                logger.info(f"Table '{table_name}' already exists")
                return False

            # Create table
            columns = []
            for col in df.columns:
                columns.append(f"[{col}] NVARCHAR(MAX)")

            create_sql = (
                f"CREATE TABLE [{table_name}] ("
                f"[ID] INT IDENTITY(1,1) PRIMARY KEY, "
                f"[SyncTimestamp] DATETIME DEFAULT GETDATE(), "
                f"{', '.join(columns)}"
                f")"
            )
            cursor.execute(create_sql)
            conn.commit()
            logger.info(f"Created new table '{table_name}'")
            return True
        except Exception as e:
            logger.error(f"Error creating SQL Server table: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def _create_sqlite_table(self, df: pd.DataFrame, table_name: str) -> bool:
        """Create SQLite table"""
        conn = None
        try:
            conn = self._get_sqlite_connection()
            cursor = conn.cursor()

            # Check if table exists
            cursor.execute(
                f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{table_name}'"
            )
            exists = cursor.fetchone()[0] > 0

            if exists:
                logger.info(f"Table '{table_name}' already exists")
                return False

            # Create table
            columns = []
            for col in df.columns:
                columns.append(f"{col} TEXT")

            create_sql = (
                f"CREATE TABLE {table_name} ("
                f"id INTEGER PRIMARY KEY AUTOINCREMENT, "
                f"SyncTimestamp DATETIME DEFAULT CURRENT_TIMESTAMP, "
                f"{', '.join(columns)}"
                f")"
            )
            cursor.execute(create_sql)
            conn.commit()
            logger.info(f"Created new SQLite table '{table_name}'")
            return True
        except Exception as e:
            logger.error(f"Error creating SQLite table: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def insert_data(self, df: pd.DataFrame, table_name: str) -> bool:
        """Insert data into the database"""
        if self.config.database_type == "sqlserver":
            return self._insert_sql_data(df, table_name)
        else:
            return self._insert_sqlite_data(df, table_name)

    def _insert_sql_data(self, df: pd.DataFrame, table_name: str) -> bool:
        """Insert data into SQL Server"""
        conn = None
        try:
            conn = self._get_sql_connection()
            df["SyncTimestamp"] = datetime.now()

            placeholders = ", ".join(["?"] * len(df.columns))
            columns = ", ".join([f"[{col}]" for col in df.columns])
            sql = f"INSERT INTO [{table_name}] ({columns}) VALUES ({placeholders})"
            data = [tuple(row) for row in df.itertuples(index=False)]

            cursor = conn.cursor()
            cursor.fast_executemany = True
            cursor.executemany(sql, data)
            conn.commit()

            logger.info(f"Inserted {len(df)} rows into SQL Server table '{table_name}'")
            return True
        except Exception as e:
            logger.error(f"Error inserting data into SQL Server: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def _insert_sqlite_data(self, df: pd.DataFrame, table_name: str) -> bool:
        """Insert data into SQLite"""
        conn = None
        try:
            conn = self._get_sqlite_connection()
            df["SyncTimestamp"] = datetime.now()

            columns = ", ".join(df.columns)
            placeholders = ", ".join(["?"] * len(df.columns))
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            data = [tuple(row) for row in df.itertuples(index=False)]

            cursor = conn.cursor()
            cursor.executemany(sql, data)
            conn.commit()

            logger.info(f"Inserted {len(df)} rows into SQLite table '{table_name}'")
            return True
        except Exception as e:
            logger.error(f"Error inserting data into SQLite: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()

    def _get_sql_connection(self):
        """Get SQL Server connection"""
        return pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.config.sql_server};"
            f"DATABASE={self.config.sql_database};"
            f"UID={self.config.sql_username};"
            f"PWD={self.config.sql_password}"
        )

    def _get_sqlite_connection(self):
        """Get SQLite connection"""
        return sqlite3.connect(self.config.sqlite_file)
