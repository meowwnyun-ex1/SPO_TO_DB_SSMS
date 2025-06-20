# connectors/database_connector.py - Fixed Database Connector
import pandas as pd
from sqlalchemy import create_engine, text, inspect, exc
from typing import List, Dict, Optional
import logging
from pathlib import Path
from urllib.parse import quote_plus

from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity
from utils.config_manager import Config

logger = logging.getLogger(__name__)


class DatabaseConnector:
    """
    Manages connections and operations with SQL Server and SQLite databases.
    Enhanced with robust error handling and improved connection management.
    """

    def __init__(self, config: Config):
        self.config = config
        self.engine = None
        self.connection_string = ""
        self._create_engine()
        logger.info(f"DatabaseConnector initialized for {self.config.database_type}")

    @handle_exceptions(ErrorCategory.CONNECTION, ErrorSeverity.HIGH)
    def _create_engine(self):
        """Create SQLAlchemy engine based on configuration"""
        db_type = self.config.database_type.lower()

        try:
            if db_type == "sqlserver":
                self.connection_string = self._build_sqlserver_connection_string()
            elif db_type == "sqlite":
                self.connection_string = self._build_sqlite_connection_string()
            else:
                raise ValueError(f"Unsupported database type: {db_type}")

            # Create engine with appropriate settings
            engine_kwargs = {
                "pool_pre_ping": True,  # Verify connections before use
                "pool_recycle": 3600,  # Recreate connections after 1 hour
                "echo": False,  # Set to True for SQL debugging
            }

            # Add timeout for SQL Server
            if db_type == "sqlserver":
                engine_kwargs["connect_args"] = {
                    "timeout": self.config.connection_timeout,
                    "autocommit": True,
                }

            self.engine = create_engine(self.connection_string, **engine_kwargs)

            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            logger.info(f"Database engine created successfully for {db_type}")

        except exc.SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error during engine creation: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during engine creation: {e}")
            raise

    def _build_sqlserver_connection_string(self) -> str:
        """Build SQL Server connection string"""
        if not all([self.config.sql_server, self.config.sql_database]):
            raise ValueError("SQL Server and database name are required")

        # Check if using Windows Authentication
        if self.config.sql_username and self.config.sql_password:
            # SQL Server Authentication
            connection_string = (
                f"mssql+pyodbc://{quote_plus(self.config.sql_username)}:"
                f"{quote_plus(self.config.sql_password)}@"
                f"{self.config.sql_server}/{self.config.sql_database}?"
                f"driver=ODBC+Driver+17+for+SQL+Server&"
                f"timeout={self.config.connection_timeout}"
            )
        else:
            # Windows Authentication
            connection_string = (
                f"mssql+pyodbc://{self.config.sql_server}/"
                f"{self.config.sql_database}?"
                f"driver=ODBC+Driver+17+for+SQL+Server&"
                f"trusted_connection=yes&"
                f"timeout={self.config.connection_timeout}"
            )

        logger.debug("SQL Server connection string built (credentials hidden)")
        return connection_string

    def _build_sqlite_connection_string(self) -> str:
        """Build SQLite connection string"""
        if not self.config.sqlite_file:
            raise ValueError("SQLite file path is required")

        # Ensure directory exists
        sqlite_path = Path(self.config.sqlite_file)
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)

        connection_string = f"sqlite:///{sqlite_path.resolve()}"
        logger.debug(f"SQLite connection string: {connection_string}")
        return connection_string

    @handle_exceptions(ErrorCategory.CONNECTION, ErrorSeverity.HIGH)
    def test_connection(self) -> bool:
        """Test database connection"""
        if self.engine is None:
            logger.error("Database engine is not initialized")
            return False

        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            logger.info("Database connection test successful")
            return True
        except exc.SQLAlchemyError as e:
            logger.error(f"Database connection test failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection test: {e}")
            return False

    @handle_exceptions(ErrorCategory.DATA, ErrorSeverity.MEDIUM)
    def read_table(self, table_name: str) -> Optional[List[Dict]]:
        """Read all data from specified table"""
        if not table_name:
            logger.error("Table name is required")
            return None

        logger.info(f"Reading data from table: '{table_name}'")

        if self.engine is None:
            logger.error("Database engine is not initialized")
            return None

        try:
            with self.engine.connect() as conn:
                # Check if table exists
                inspector = inspect(self.engine)
                if not inspector.has_table(table_name):
                    logger.warning(f"Table '{table_name}' does not exist")
                    return []

                query = text(f"SELECT * FROM [{table_name}]")
                df = pd.read_sql(query, conn)

            logger.info(f"Successfully read {len(df)} rows from table '{table_name}'")
            return df.to_dict(orient="records")

        except exc.SQLAlchemyError as e:
            logger.error(f"Failed to read table '{table_name}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error reading table '{table_name}': {e}")
            return None

    @handle_exceptions(ErrorCategory.DATA, ErrorSeverity.MEDIUM)
    def write_dataframe(
        self,
        df: pd.DataFrame,
        table_name: str,
        if_exists: str = "append",
        index: bool = False,
        create_table: bool = True,
        chunksize: int = None,
    ) -> int:
        """
        Write pandas DataFrame to database table

        Args:
            df: DataFrame to write
            table_name: Target table name
            if_exists: 'fail', 'replace', 'append'
            index: Whether to write DataFrame index
            create_table: Whether to create table if not exists
            chunksize: Number of rows to write at once

        Returns:
            Number of rows written
        """
        if df.empty:
            logger.warning("DataFrame is empty, nothing to write")
            return 0

        if not table_name:
            raise ValueError("Table name is required")

        logger.info(
            f"Writing {len(df)} rows to table '{table_name}' (mode: {if_exists})"
        )

        if self.engine is None:
            raise ConnectionError("Database engine not initialized")

        try:
            # Check table existence if needed
            inspector = inspect(self.engine)
            table_exists = inspector.has_table(table_name)

            if not table_exists and not create_table and if_exists != "replace":
                raise ValueError(
                    f"Table '{table_name}' does not exist and create_table=False"
                )

            # Use configured batch size if chunksize not specified
            if chunksize is None:
                chunksize = getattr(self.config, "batch_size", 1000)

            # Write data using transaction
            with self.engine.begin() as conn:
                rows_written = df.to_sql(
                    table_name,
                    con=conn,
                    if_exists=if_exists,
                    index=index,
                    chunksize=chunksize,
                    method="multi",  # Use multi-row INSERT for better performance
                )

            logger.info(f"Successfully wrote {len(df)} rows to table '{table_name}'")
            return len(df)

        except exc.SQLAlchemyError as e:
            logger.error(f"Failed to write DataFrame to table '{table_name}': {e}")
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error writing DataFrame to table '{table_name}': {e}"
            )
            raise

    @handle_exceptions(ErrorCategory.DATA, ErrorSeverity.MEDIUM)
    def execute_query(self, query: str, params: dict = None) -> Optional[List[Dict]]:
        """Execute custom SQL query"""
        if not query.strip():
            raise ValueError("Query cannot be empty")

        logger.info("Executing custom query")
        logger.debug(f"Query: {query}")

        if self.engine is None:
            raise ConnectionError("Database engine not initialized")

        try:
            with self.engine.connect() as conn:
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))

                # Handle SELECT queries
                if result.returns_rows:
                    rows = result.fetchall()
                    columns = result.keys()
                    data = [dict(zip(columns, row)) for row in rows]
                    logger.info(f"Query returned {len(data)} rows")
                    return data
                else:
                    # Handle INSERT/UPDATE/DELETE
                    rowcount = result.rowcount
                    logger.info(f"Query affected {rowcount} rows")
                    return [{"affected_rows": rowcount}]

        except exc.SQLAlchemyError as e:
            logger.error(f"Failed to execute query: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error executing query: {e}")
            raise

    @handle_exceptions(ErrorCategory.DATA, ErrorSeverity.LOW)
    def get_table_info(self, table_name: str) -> Optional[Dict]:
        """Get table schema information"""
        if not table_name:
            return None

        if self.engine is None:
            return None

        try:
            inspector = inspect(self.engine)

            if not inspector.has_table(table_name):
                return None

            columns = inspector.get_columns(table_name)
            indexes = inspector.get_indexes(table_name)

            return {
                "table_name": table_name,
                "columns": columns,
                "indexes": indexes,
                "column_count": len(columns),
            }

        except Exception as e:
            logger.error(f"Failed to get table info for '{table_name}': {e}")
            return None

    @handle_exceptions(ErrorCategory.DATA, ErrorSeverity.LOW)
    def list_tables(self) -> List[str]:
        """List all tables in database"""
        if self.engine is None:
            return []

        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            logger.debug(f"Found {len(tables)} tables in database")
            return tables
        except Exception as e:
            logger.error(f"Failed to list tables: {e}")
            return []

    def close(self):
        """Close database connection and dispose engine"""
        if self.engine:
            try:
                self.engine.dispose()
                logger.info("Database engine disposed, connections closed")
            except Exception as e:
                logger.error(f"Error disposing database engine: {e}")
            finally:
                self.engine = None
                self.connection_string = ""
