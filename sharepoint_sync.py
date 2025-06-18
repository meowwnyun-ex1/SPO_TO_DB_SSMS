# sharepoint_sync.py
import requests
import pandas as pd
from config import *
from db import create_table_if_not_exists, insert_dataframe


def get_access_token():
    url = f"https://accounts.accesscontrol.windows.net/{TENANT_ID}/tokens/OAuth/2"
    payload = {
        "grant_type": "client_credentials",
        "client_id": f"{SHAREPOINT_CLIENT_ID}@{TENANT_ID}",
        "client_secret": SHAREPOINT_CLIENT_SECRET,
        "resource": f"00000003-0000-0ff1-ce00-000000000000/{SHAREPOINT_SITE.split('/')[2]}@{TENANT_ID}",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=payload, headers=headers)
    return response.json().get("access_token")


def fetch_sharepoint_data():
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json;odata=verbose",
    }
    endpoint = f"{SHAREPOINT_SITE}/_api/web/lists/GetByTitle('{SHAREPOINT_LIST}')/items"

    response = requests.get(endpoint, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error fetching data: {response.text}")

    data = response.json()["d"]["results"]
    df = pd.json_normalize(data)
    df = df.loc[:, ~df.columns.str.startswith("__")]
    return df


def sync_data():
    df = fetch_sharepoint_data()
    if df.empty:
        print("No data fetched.")
        return
    create_table_if_not_exists(df)
    insert_dataframe(df)
    print("✅ Data synced from SharePoint to SQL Server.")


if __name__ == "__main__":
    try:
        sync_data()
    except Exception as e:
        print(f"❌ Error during sync: {e}")
