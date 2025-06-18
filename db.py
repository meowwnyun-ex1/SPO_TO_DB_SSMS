# db.py
import pyodbc
import pandas as pd
from config import *


def get_sql_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        f"UID={SQL_USERNAME};"
        f"PWD={SQL_PASSWORD}"
    )
    return pyodbc.connect(conn_str)


def create_table_if_not_exists(df: pd.DataFrame):
    conn = get_sql_connection()
    cursor = conn.cursor()

    columns_sql = ", ".join([f"[{col}] NVARCHAR(MAX)" for col in df.columns])
    create_sql = f"""
    IF NOT EXISTS (
        SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{SQL_TABLE_NAME}'
    )
    CREATE TABLE [{SQL_TABLE_NAME}] ({columns_sql})
    """
    cursor.execute(create_sql)
    conn.commit()
    cursor.close()
    conn.close()


def insert_dataframe(df: pd.DataFrame):
    conn = get_sql_connection()
    cursor = conn.cursor()
    for _, row in df.iterrows():
        placeholders = ", ".join(["?" for _ in row])
        insert_sql = f"INSERT INTO [{SQL_TABLE_NAME}] ({', '.join(row.index)}) VALUES ({placeholders})"
        cursor.execute(insert_sql, tuple(row))
    conn.commit()
    cursor.close()
    conn.close()
