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
from typing import List, Optional, Dict
import logging
import os

logger = logging.getLogger(__name__)


class DatabaseConnector:
    """Database connector supporting multiple database types"""

    def __init__(self, config):
        self.config = config
        self.engine = None
        self._create_engine()

    def _create_engine(self):
        """Create database engine based on configuration"""
        try:
            if self.config.database_type == "sqlserver":
                connection_string = self._build_sqlserver_connection_string()
            elif self.config.database_type == "sqlite":
                connection_string = self._build_sqlite_connection_string()
            elif self.config.database_type == "mysql":
                connection_string = self._build_mysql_connection_string()
            elif self.config.database_type == "postgresql":
                connection_string = self._build_postgresql_connection_string()
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
        """Build SQL Server connection string"""
        return (
            f"mssql+pyodbc://{self.config.sql_username}:"
            f"{self.config.sql_password}@{self.config.sql_server}/"
            f"{self.config.sql_database}?"
            f"driver=ODBC+Driver+17+for+SQL+Server&"
            f"timeout={self.config.connection_timeout}"
        )

    def _build_sqlite_connection_string(self) -> str:
        """Build SQLite connection string"""
        # Ensure directory exists
        db_path = os.path.abspath(self.config.sqlite_file)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return f"sqlite:///{db_path}"

    def _build_mysql_connection_string(self) -> str:
        """Build MySQL connection string"""
        return (
            f"mysql+pymysql://{self.config.sql_username}:"
            f"{self.config.sql_password}@{self.config.sql_server}/"
            f"{self.config.sql_database}"
        )

    def _build_postgresql_connection_string(self) -> str:
        """Build PostgreSQL connection string"""
        return (
            f"postgresql+psycopg2://{self.config.sql_username}:"
            f"{self.config.sql_password}@{self.config.sql_server}/"
            f"{self.config.sql_database}"
        )

    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                if self.config.database_type == "sqlserver":
                    result = conn.execute(text("SELECT 1 as test"))
                elif self.config.database_type == "sqlite":
                    result = conn.execute(text("SELECT 1 as test"))
                elif self.config.database_type == "mysql":
                    result = conn.execute(text("SELECT 1 as test"))
                elif self.config.database_type == "postgresql":
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
        """Get available databases (SQL Server/MySQL/PostgreSQL only)"""
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
                elif self.config.database_type == "mysql":
                    result = conn.execute(text("SHOW DATABASES"))
                elif self.config.database_type == "postgresql":
                    result = conn.execute(
                        text(
                            "SELECT datname FROM pg_database "
                            "WHERE datistemplate = false "
                            "ORDER BY datname"
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
        """Get available tables"""
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
                elif self.config.database_type == "mysql":
                    result = conn.execute(
                        text(
                            f"SELECT TABLE_NAME FROM information_schema.TABLES "
                            f"WHERE TABLE_SCHEMA = '{self.config.sql_database}' "
                            "AND TABLE_TYPE = 'BASE TABLE' "
                            "ORDER BY TABLE_NAME"
                        )
                    )
                elif self.config.database_type == "postgresql":
                    result = conn.execute(
                        text(
                            "SELECT tablename FROM pg_tables "
                            "WHERE schemaname = 'public' "
                            "ORDER BY tablename"
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
        """Check if table exists"""
        try:
            tables = self.get_tables()
            return table_name in tables
        except Exception as e:
            logger.error(f"Failed to check if table exists: {str(e)}")
            return False

    def create_table_if_not_exists(self, df: pd.DataFrame, table_name: str) -> bool:
        """Create table based on DataFrame structure if it doesn't exist"""
        try:
            if self.table_exists(table_name):
                logger.info(f"Table '{table_name}' already exists")
                return False

            # Create table schema based on DataFrame
            metadata = MetaData()

            # Define base columns
            columns = [
                Column("id", Integer, primary_key=True, autoincrement=True),
                Column("sync_timestamp", DateTime, default=datetime.now),
                Column("sync_id", String(50)),
            ]

            # Add columns from DataFrame
            for col_name in df.columns:
                # Clean column name
                clean_name = self._clean_column_name(col_name)

                # Determine column type based on data
                if df[col_name].dtype == "object":
                    col_type = String(500)  # Use VARCHAR for text
                elif df[col_name].dtype in ["int64", "int32"]:
                    col_type = Integer
                elif df[col_name].dtype in ["float64", "float32"]:
                    col_type = String(50)  # Store as string to avoid precision issues
                else:
                    col_type = String(500)  # Default to string

                columns.append(Column(clean_name, col_type))

            # Create table
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
        """Clean column name for database compatibility"""
        # Replace problematic characters
        cleaned = name.replace(".", "_").replace(" ", "_").replace("-", "_")
        cleaned = "".join(c for c in cleaned if c.isalnum() or c == "_")

        # Ensure it doesn't start with a number
        if cleaned and cleaned[0].isdigit():
            cleaned = f"col_{cleaned}"

        # Ensure it's not empty
        if not cleaned:
            cleaned = "unnamed_column"

        return cleaned.lower()

    def insert_data(self, df: pd.DataFrame, table_name: str) -> int:
        """Insert DataFrame data into database table"""
        try:
            # Add metadata columns
            df_copy = df.copy()
            df_copy["sync_timestamp"] = datetime.now()
            df_copy["sync_id"] = f"sync_{int(datetime.now().timestamp())}"

            # Clean column names
            df_copy.columns = [self._clean_column_name(col) for col in df_copy.columns]

            # Handle truncate option
            if (
                self.config.database_type == "sqlserver"
                and self.config.sql_truncate_before
            ) or (
                self.config.database_type == "sqlite"
                and hasattr(self.config, "sqlite_truncate_before")
                and self.config.sqlite_truncate_before
            ):
                self.truncate_table(table_name)

            # Insert data
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
        """Truncate table data"""
        try:
            with self.engine.connect() as conn:
                if self.config.database_type == "sqlserver":
                    conn.execute(text(f"TRUNCATE TABLE [{table_name}]"))
                elif self.config.database_type == "sqlite":
                    conn.execute(text(f"DELETE FROM {table_name}"))
                elif self.config.database_type in ["mysql", "postgresql"]:
                    conn.execute(text(f"TRUNCATE TABLE {table_name}"))

                conn.commit()

            logger.info(f"Successfully truncated table '{table_name}'")
            return True

        except Exception as e:
            logger.error(f"Failed to truncate table '{table_name}': {str(e)}")
            return False

    def get_table_info(self, table_name: str) -> Dict:
        """Get information about a table"""
        try:
            with self.engine.connect() as conn:
                # Get row count
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                row_count = result.fetchone()[0]

                # Get column info
                if self.config.database_type == "sqlserver":
                    result = conn.execute(
                        text(
                            f"SELECT COLUMN_NAME, DATA_TYPE FROM {self.config.sql_database}.INFORMATION_SCHEMA.COLUMNS "
                            f"WHERE TABLE_NAME = '{table_name}' ORDER BY ORDINAL_POSITION"
                        )
                    )
                elif self.config.database_type == "sqlite":
                    result = conn.execute(text(f"PRAGMA table_info({table_name})"))
                elif self.config.database_type == "mysql":
                    result = conn.execute(
                        text(
                            f"SELECT COLUMN_NAME, DATA_TYPE FROM information_schema.COLUMNS "
                            f"WHERE TABLE_SCHEMA = '{self.config.sql_database}' AND TABLE_NAME = '{table_name}' "
                            "ORDER BY ORDINAL_POSITION"
                        )
                    )
                elif self.config.database_type == "postgresql":
                    result = conn.execute(
                        text(
                            f"SELECT column_name, data_type FROM information_schema.columns "
                            f"WHERE table_name = '{table_name}' ORDER BY ordinal_position"
                        )
                    )

                columns = []
                for row in result:
                    if self.config.database_type == "sqlite":
                        columns.append({"name": row[1], "type": row[2]})
                    else:
                        columns.append({"name": row[0], "type": row[1]})

                return {
                    "table_name": table_name,
                    "row_count": row_count,
                    "column_count": len(columns),
                    "columns": columns,
                }

        except Exception as e:
            logger.error(f"Failed to get table info for '{table_name}': {str(e)}")
            return {}

    def backup_table(
        self, table_name: str, backup_suffix: Optional[str] = None
    ) -> bool:
        """Create a backup of the table"""
        try:
            if backup_suffix is None:
                backup_suffix = datetime.now().strftime("%Y%m%d_%H%M%S")

            backup_table_name = f"{table_name}_backup_{backup_suffix}"

            with self.engine.connect() as conn:
                if self.config.database_type == "sqlserver":
                    conn.execute(
                        text(f"SELECT * INTO [{backup_table_name}] FROM [{table_name}]")
                    )
                elif self.config.database_type == "sqlite":
                    conn.execute(
                        text(
                            f"CREATE TABLE {backup_table_name} AS SELECT * FROM {table_name}"
                        )
                    )
                elif self.config.database_type in ["mysql", "postgresql"]:
                    conn.execute(
                        text(
                            f"CREATE TABLE {backup_table_name} AS SELECT * FROM {table_name}"
                        )
                    )

                conn.commit()

            logger.info(f"Successfully created backup table '{backup_table_name}'")
            return True

        except Exception as e:
            logger.error(f"Failed to backup table '{table_name}': {str(e)}")
            return False

    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")
