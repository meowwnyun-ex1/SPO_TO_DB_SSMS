# config.py (เพิ่มเติม)
import os
from dotenv import load_dotenv

# โหลดค่าจาก .env ถ้ามี
load_dotenv()

# ค่าติดตั้ง (ใช้ค่าจาก environment variables เป็นหลัก)
SHAREPOINT_SITE = os.getenv(
    "SHAREPOINT_SITE", "https://yourdomain.sharepoint.com/sites/YourSite"
)
SHAREPOINT_LIST = os.getenv("SHAREPOINT_LIST", "data_samples_py")
SHAREPOINT_CLIENT_ID = os.getenv("SHAREPOINT_CLIENT_ID", "your-client-id")
SHAREPOINT_CLIENT_SECRET = os.getenv("SHAREPOINT_CLIENT_SECRET", "your-client-secret")
TENANT_ID = os.getenv("TENANT_ID", "your-tenant-id")

SQL_SERVER = os.getenv("SQL_SERVER", "your_sql_server.database.windows.net")
SQL_DATABASE = os.getenv("SQL_DATABASE", "your_database")
SQL_USERNAME = os.getenv("SQL_USERNAME", "your_username")
SQL_PASSWORD = os.getenv("SQL_PASSWORD", "your_password")
SQL_TABLE_NAME = os.getenv("SQL_TABLE_NAME", "data_samples_py")

# การตั้งค่าเพิ่มเติม
SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", "3600"))  # ค่าเริ่มต้น: 1 ชั่วโมง
