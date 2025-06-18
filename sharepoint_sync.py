# sharepoint_sync.py (ปรับปรุง)
import requests
import pandas as pd
from config import *
from db import create_table_if_not_exists, insert_dataframe
import time
import logging

# ตั้งค่าระบบล็อก
logging.basicConfig(
    filename="sync.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def get_access_token():
    """ดึง Access Token ด้วยการลองใหม่เมื่อเกิดข้อผิดพลาด"""
    url = f"https://accounts.accesscontrol.windows.net/{TENANT_ID}/tokens/OAuth/2"
    payload = {
        "grant_type": "client_credentials",
        "client_id": f"{SHAREPOINT_CLIENT_ID}@{TENANT_ID}",
        "client_secret": SHAREPOINT_CLIENT_SECRET,
        "resource": f"00000003-0000-0ff1-ce00-000000000000/{SHAREPOINT_SITE.split('/')[2]}@{TENANT_ID}",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    for attempt in range(3):  # ลองสูงสุด 3 ครั้ง
        try:
            response = requests.post(url, data=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json().get("access_token")
        except Exception as e:
            logging.warning(f"Token attempt {attempt+1} failed: {str(e)}")
            time.sleep(5)  # รอ 5 วินาทีก่อนลองใหม่

    logging.error("Failed to get access token after 3 attempts")
    raise Exception("Authentication failed")


def fetch_sharepoint_data():
    """ดึงข้อมูลจาก SharePoint พร้อมจัดการ pagination"""
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json;odata=verbose",
    }
    base_url = f"{SHAREPOINT_SITE}/_api/web/lists/GetByTitle('{SHAREPOINT_LIST}')/items"

    all_items = []
    url = base_url

    while url:
        try:
            response = requests.get(url, headers=headers, timeout=60)
            response.raise_for_status()
            data = response.json()

            # บันทึกล็อกเมื่อดึงข้อมูลสำเร็จ
            logging.info(
                f"Fetched page with {len(data.get('d', {}).get('results', []))} items"
            )

            all_items.extend(data["d"]["results"])

            # ตรวจสอบว่ามีหน้าถัดไปหรือไม่
            url = data["d"].get("__next", None)
        except Exception as e:
            logging.error(f"Data fetch failed: {str(e)}")
            raise

    if not all_items:
        logging.warning("No data fetched from SharePoint")
        return pd.DataFrame()

    df = pd.json_normalize(all_items)
    df = df.loc[:, ~df.columns.str.startswith("__")]

    # บันทึกจำนวนข้อมูลที่ดึงมา
    logging.info(f"Total items fetched: {len(df)}")
    return df


def sync_data():
    """ซิงค์ข้อมูลหลักพร้อมจัดการข้อผิดพลาด"""
    try:
        start_time = time.time()
        df = fetch_sharepoint_data()

        if df.empty:
            print("No data fetched.")
            return False

        create_table_if_not_exists(df)
        insert_dataframe(df)

        # คำนวณเวลาทำงาน
        duration = time.time() - start_time
        logging.info(f"✅ Data synced in {duration:.2f} seconds. Rows: {len(df)}")
        return True
    except Exception as e:
        logging.exception("❌ Error during sync")
        raise
