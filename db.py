# db.py (ปรับปรุง)
import pyodbc
import pandas as pd
from config import *
from datetime import datetime


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

    # ตรวจสอบว่าตารางมีอยู่แล้วหรือไม่
    cursor.execute(
        f"""
        IF NOT EXISTS (
            SELECT * FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = '{SQL_TABLE_NAME}'
        )
        BEGIN
            CREATE TABLE [{SQL_TABLE_NAME}] (
                [ID] INT IDENTITY(1,1) PRIMARY KEY,
                [SyncTimestamp] DATETIME DEFAULT GETDATE(),
                {', '.join([f'[{col}] NVARCHAR(MAX)' for col in df.columns])}
            )
        END
    """
    )
    conn.commit()
    cursor.close()
    conn.close()


def insert_dataframe(df: pd.DataFrame):
    conn = get_sql_connection()
    cursor = conn.cursor()

    # เพิ่มคอลัมน์ timestamp
    df["SyncTimestamp"] = datetime.now()

    # ใช้ bulk insert สำหรับประสิทธิภาพสูง
    placeholders = ", ".join(["?"] * len(df.columns))
    columns = ", ".join([f"[{col}]" for col in df.columns])
    sql = f"INSERT INTO [{SQL_TABLE_NAME}] ({columns}) VALUES ({placeholders})"

    # แปลง DataFrame เป็นลิสต์ของ tuples
    data = [tuple(row) for row in df.itertuples(index=False)]

    # ใช้ fast_executemany สำหรับการแทรกข้อมูลจำนวนมาก
    cursor.fast_executemany = True
    cursor.executemany(sql, data)

    conn.commit()
    cursor.close()
    conn.close()
