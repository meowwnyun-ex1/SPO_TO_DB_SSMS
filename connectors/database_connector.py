# connectors/database_connector.py - Enhanced with Robustness and Performance
import pandas as pd
from sqlalchemy import create_engine, text, inspect, exc
from typing import List, Dict, Optional  # Added Optional import
import logging
from pathlib import Path
from urllib.parse import quote_plus  # For SQL Server connection string
from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity
from utils.config_manager import Config  # For type hinting

logger = logging.getLogger(__name__)


class DatabaseConnector:
    """
    Manages connections and operations with SQL Server and SQLite databases.
    Includes robust error handling and improved connection management.
    """

    def __init__(self, config: Config):
        self.config = config
        self.engine = None
        self._create_engine()
        logger.info(
            f"DatabaseConnector initialized for {self.config.database_type or self.config.db_type}."
        )

    @handle_exceptions(
        ErrorCategory.CONNECTION, ErrorSeverity.HIGH
    )  # Removed user_message argument
    def _create_engine(self):
        """
        Creates a SQLAlchemy engine based on the configuration.
        Includes dynamic handling for connection string parameters.
        """
        connection_string = ""
        db_type = (
            self.config.database_type.lower()
            if self.config.database_type
            else self.config.db_type.lower()
        )

        try:
            if db_type == "sqlserver":
                # Using trusted connection if no username/password provided, otherwise use credentials
                if self.config.sql_username and self.config.sql_password:
                    connection_string = (
                        f"mssql+pyodbc://{quote_plus(self.config.sql_username)}:"
                        f"{quote_plus(self.config.sql_password)}@"
                        f"{self.config.sql_server}/{self.config.sql_database}?"
                        "driver=ODBC+Driver+17+for+SQL+Server"
                    )
                else:
                    # Windows Authentication (Trusted Connection)
                    connection_string = (
                        f"mssql+pyodbc://{self.config.sql_server}/"
                        f"{self.config.sql_database}?"
                        "driver=ODBC+Driver+17+for+SQL+Server;"
                        "trusted_connection=yes"
                    )
                logger.debug(f"SQL Server connection string: {connection_string}")
            elif db_type == "sqlite":
                # Ensure the directory for the SQLite file exists
                sqlite_path = Path(self.config.sqlite_file)
                sqlite_path.parent.mkdir(parents=True, exist_ok=True)
                connection_string = f"sqlite:///{sqlite_path.resolve()}"
                logger.debug(f"SQLite connection string: {connection_string}")
            else:
                raise ValueError(f"Unsupported database type: {db_type}")

            self.engine = create_engine(
                connection_string,
                connect_args={"timeout": self.config.connection_timeout},
                pool_pre_ping=True,  # Ensures connections are alive
            )
            # Test connection immediately
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info(f"Successfully created and tested engine for {db_type}.")
        except exc.SQLAlchemyError as e:
            logger.error(
                f"SQLAlchemy engine creation or test failed: {e}", exc_info=True
            )
            raise  # Re-raise the exception to be caught by the decorator
        except Exception as e:
            logger.critical(
                f"An unexpected error occurred during engine creation: {e}",
                exc_info=True,
            )
            raise

    @handle_exceptions(
        ErrorCategory.CONNECTION, ErrorSeverity.HIGH
    )  # Removed user_message argument
    def test_connection(self) -> bool:
        """Tests the database connection."""
        if self.engine is None:
            logger.error("Database engine is not initialized.")
            return False
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Database connection test successful.")
            return True
        except exc.SQLAlchemyError as e:
            logger.error(f"Database connection test failed: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.critical(
                f"An unexpected error occurred during database connection test: {e}",
                exc_info=True,
            )
            return False

    @handle_exceptions(ErrorCategory.DATA, ErrorSeverity.MEDIUM)
    def read_table(self, table_name: str) -> Optional[List[Dict]]:
        """Reads all data from a specified table."""
        logger.info(f"Reading data from table: '{table_name}'")
        if self.engine is None:
            logger.error("Database engine is not initialized.")
            return None
        try:
            with self.engine.connect() as connection:
                query = text(f"SELECT * FROM {table_name}")
                df = pd.read_sql(query, connection)
            logger.info(f"Successfully read {len(df)} rows from table '{table_name}'.")
            return df.to_dict(orient="records")
        except exc.SQLAlchemyError as e:
            logger.error(f"Failed to read table '{table_name}': {e}", exc_info=True)
            return None
        except Exception as e:
            logger.critical(
                f"An unexpected error occurred while reading table '{table_name}': {e}",
                exc_info=True,
            )
            return None

    @handle_exceptions(ErrorCategory.DATA, ErrorSeverity.MEDIUM)
    def write_dataframe(
        self,
        df: pd.DataFrame,
        table_name: str,
        if_exists: str = "append",
        index: bool = False,
        create_table: bool = True,  # New parameter to control table creation
    ) -> int:
        """
        Writes a pandas DataFrame to a specified database table.
        if_exists: 'fail', 'replace', or 'append'.
        index: Write DataFrame index as a column.
        create_table: If True, ensures table is created or exists.
        """
        logger.info(
            f"Writing DataFrame to table '{table_name}' (if_exists='{if_exists}')."
        )
        if self.engine is None:
            logger.error("Database engine is not initialized. Cannot write DataFrame.")
            raise ConnectionError("Database engine not initialized.")

        try:
            # Check if table exists if create_table is False and if_exists is not 'replace'
            inspector = inspect(self.engine)
            if (
                not inspector.has_table(table_name)
                and not create_table
                and if_exists != "replace"
            ):
                logger.error(
                    f"Table '{table_name}' does not exist and create_table is False. Aborting write."
                )
                raise ValueError(f"Table '{table_name}' does not exist.")

            # Ensure the connection is disposed properly
            with self.engine.begin() as connection:  # begin() for transactional integrity
                # Use chunksize for large dataframes to prevent memory issues
                rows_written = df.to_sql(
                    table_name,
                    con=connection,  # Pass connection object directly
                    if_exists=if_exists,
                    index=index,
                    chunksize=1000,  # Write in chunks of 1000 rows
                )
            logger.info(
                f"Successfully wrote {len(df)} rows to table '{table_name}'. (Action: '{if_exists}')"
            )
            return len(df)  # pandas.to_sql returns None, so return df length
        except exc.SQLAlchemyError as e:
            logger.error(
                f"Failed to write DataFrame to table '{table_name}': {e}", exc_info=True
            )
            raise  # Re-raise for upstream error handling
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while writing DataFrame to table '{table_name}': {e}",
                exc_info=True,
            )
            raise  # Re-raise for upstream error handling

    def close(self):
        """Disposes the SQLAlchemy engine, closing all connections in the pool."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database engine disposed, all connections closed.")
            self.engine = None
