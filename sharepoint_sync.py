# sharepoint_sync.py
import requests
import pandas as pd
from config import *
import time
import logging
from typing import List, Dict, Optional
from config import Config
from db import DatabaseConnector

logging.basicConfig(
    filename="sync.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class SharePointConnector:
    def __init__(
        self, site_url: str, client_id: str, client_secret: str, tenant_id: str
    ):
        self.site_url = site_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.token = None
        self.token_expiry = None

    def get_access_token(self) -> str:
        """Get access token with retry logic"""
        if self.token and self.token_expiry and time.time() < self.token_expiry:
            return self.token

        url = f"https://accounts.accesscontrol.windows.net/{self.tenant_id}/tokens/OAuth/2"
        payload = {
            "grant_type": "client_credentials",
            "client_id": f"{self.client_id}@{self.tenant_id}",
            "client_secret": self.client_secret,
            "resource": f"00000003-0000-0ff1-ce00-000000000000/{self.site_url.split('/')[2]}@{self.tenant_id}",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        for attempt in range(3):
            try:
                response = requests.post(url, data=payload, headers=headers, timeout=30)
                response.raise_for_status()
                token_data = response.json()
                self.token = token_data.get("access_token")
                self.token_expiry = (
                    time.time() + int(token_data.get("expires_in", 3600)) - 300
                )
                return self.token
            except Exception as e:
                logging.warning(f"Token attempt {attempt+1} failed: {str(e)}")
                time.sleep(5)

        logging.error("Failed to get access token after 3 attempts")
        raise Exception("Authentication failed")

    def get_sites(self) -> List[Dict]:
        """Get available SharePoint sites"""
        token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json;odata=verbose",
        }
        url = f"https://{self.site_url.split('/')[2]}/_api/web/webs"

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json().get("d", {}).get("results", [])
        except Exception as e:
            logging.error(f"Failed to get sites: {str(e)}")
            raise

    def get_lists(self, site_url: str) -> List[Dict]:
        """Get lists from a SharePoint site"""
        token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json;odata=verbose",
        }
        url = f"{site_url}/_api/web/lists"

        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json().get("d", {}).get("results", [])
        except Exception as e:
            logging.error(f"Failed to get lists: {str(e)}")
            raise

    def fetch_data(self, list_name: str) -> Optional[pd.DataFrame]:
        """Fetch data from SharePoint list with pagination"""
        token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json;odata=verbose",
        }
        base_url = f"{self.site_url}/_api/web/lists/GetByTitle('{list_name}')/items"

        all_items = []
        url = base_url

        while url:
            try:
                response = requests.get(url, headers=headers, timeout=60)
                response.raise_for_status()
                data = response.json()

                logging.info(
                    f"Fetched page with {len(data.get('d', {}).get('results', []))} items"
                )
                all_items.extend(data["d"]["results"])
                url = data["d"].get("__next", None)
            except Exception as e:
                logging.error(f"Data fetch failed: {str(e)}")
                raise

        if not all_items:
            logging.warning("No data fetched from SharePoint")
            return None

        df = pd.json_normalize(all_items)
        df = df.loc[:, ~df.columns.str.startswith("__")]
        logging.info(f"Total items fetched: {len(df)}")
        return df


def test_sharepoint_connection(
    site_url: str, client_id: str, client_secret: str, tenant_id: str
) -> bool:
    """Test SharePoint connection"""
    try:
        connector = SharePointConnector(site_url, client_id, client_secret, tenant_id)
        connector.get_access_token()
        return True
    except Exception as e:
        logging.error(f"SharePoint connection test failed: {str(e)}")
        raise


def sync_data(config: Config) -> bool:
    """Main sync function with error handling"""
    try:
        start_time = time.time()
        connector = SharePointConnector(
            config.sharepoint_site,
            config.sharepoint_client_id,
            config.sharepoint_client_secret,
            config.tenant_id,
        )
        df = connector.fetch_data(config.sharepoint_list)

        if df is None or df.empty:
            logging.warning("No data to sync")
            return False

        db_connector = DatabaseConnector(config)

        if config.database_type == "sqlserver":
            table_name = config.sql_table_name
        else:
            table_name = config.sqlite_table_name

        if (config.database_type == "sqlserver" and config.sql_create_table) or (
            config.database_type == "sqlite" and config.sqlite_create_table
        ):
            db_connector.create_table(df, table_name)

        db_connector.insert_data(df, table_name)

        duration = time.time() - start_time
        logging.info(f"✅ Data synced in {duration:.2f} seconds. Rows: {len(df)}")
        return True
    except Exception as e:
        logging.exception("❌ Error during sync")
        raise
