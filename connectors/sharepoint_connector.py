import requests
import pandas as pd
import time
from typing import List, Dict, Optional
from utils.auth_helper import SharePointAuth
from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity
import logging

logger = logging.getLogger(__name__)


class SharePointConnector:
    """แก้แล้ว: ลบ duplicate auth code, ใช้ auth_helper อย่างเดียว"""

    def __init__(self, config):
        self.config = config
        self.auth = SharePointAuth(config)
        self.session = requests.Session()
        self.session.timeout = config.connection_timeout

    @handle_exceptions(ErrorCategory.CONNECTION, ErrorSeverity.HIGH)
    def test_connection(self) -> bool:
        """ทดสอบการเชื่อมต่อ SharePoint"""
        token = self.auth.get_access_token()
        if not token:
            return False

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json;odata=verbose",
        }

        url = f"{self.config.site_url}/_api/web"
        response = self.session.get(url, headers=headers)
        return response.status_code == 200

    @handle_exceptions(ErrorCategory.CONNECTION, ErrorSeverity.MEDIUM)
    def get_sites(self) -> List[Dict]:
        """ดึงรายการ SharePoint sites"""
        token = self.auth.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json;odata=verbose",
        }

        base_url = "/".join(self.config.site_url.split("/")[:3])
        url = f"{base_url}/_api/web/webs"

        response = self.session.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        sites = data.get("d", {}).get("results", [])
        logger.info(f"Retrieved {len(sites)} SharePoint sites")
        return sites

    @handle_exceptions(ErrorCategory.CONNECTION, ErrorSeverity.MEDIUM)
    def get_lists(self, site_url: Optional[str] = None) -> List[Dict]:
        """ดึงรายการ lists จาก SharePoint site"""
        token = self.auth.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json;odata=verbose",
        }

        target_url = site_url or self.config.site_url
        url = f"{target_url}/_api/web/lists"

        response = self.session.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        lists = data.get("d", {}).get("results", [])

        # Filter out hidden and system lists
        filtered_lists = [
            lst
            for lst in lists
            if not lst.get("Hidden", True) and lst.get("BaseType") != 1
        ]

        logger.info(f"Retrieved {len(filtered_lists)} SharePoint lists")
        return filtered_lists

    @handle_exceptions(ErrorCategory.CONNECTION, ErrorSeverity.MEDIUM)
    def get_list_fields(self, list_name: str) -> List[Dict]:
        """ดึง fields/columns จาก SharePoint list"""
        token = self.auth.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json;odata=verbose",
        }

        url = f"{self.config.site_url}/_api/web/lists/GetByTitle('{list_name}')/fields"
        response = self.session.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        fields = data.get("d", {}).get("results", [])

        # Filter user fields
        user_fields = [
            field
            for field in fields
            if not field.get("Hidden", True)
            and not field.get("ReadOnlyField", False)
            and field.get("FieldTypeKind") not in [12, 13, 17, 18, 19]
        ]

        logger.info(f"Retrieved {len(user_fields)} fields from list '{list_name}'")
        return user_fields

    @handle_exceptions(ErrorCategory.DATA, ErrorSeverity.HIGH)
    def fetch_data(self, batch_size: Optional[int] = None) -> Optional[pd.DataFrame]:
        """ดึงข้อมูลจาก SharePoint list พร้อม pagination"""
        token = self.auth.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json;odata=verbose",
        }

        base_url = f"{self.config.site_url}/_api/web/lists/GetByTitle('{self.config.list_name}')/items"

        # Add query parameters
        query_params = []
        if batch_size:
            query_params.append(f"$top={batch_size}")

        if query_params:
            base_url += "?" + "&".join(query_params)

        all_items = []
        url = base_url
        page_count = 0

        logger.info(f"Starting data fetch from list '{self.config.list_name}'")

        while url:
            page_count += 1
            logger.debug(f"Fetching page {page_count}")

            response = self.session.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            items = data.get("d", {}).get("results", [])

            if not items:
                break

            all_items.extend(items)
            logger.info(
                f"Page {page_count}: {len(items)} items (Total: {len(all_items)})"
            )

            # Get next page URL
            url = data.get("d", {}).get("__next")

            # Rate limiting
            if url:
                time.sleep(0.1)

        if not all_items:
            logger.warning("No data found in SharePoint list")
            return None

        # Convert to DataFrame
        df = pd.json_normalize(all_items)

        # Clean up metadata columns
        metadata_columns = [col for col in df.columns if col.startswith("__")]
        df = df.drop(columns=metadata_columns, errors="ignore")

        # Clean column names
        df.columns = [col.replace(".", "_") for col in df.columns]

        logger.info(f"Successfully fetched {len(df)} records from SharePoint")
        return df

    @handle_exceptions(ErrorCategory.CONNECTION, ErrorSeverity.LOW)
    def get_list_item_count(self, list_name: Optional[str] = None) -> int:
        """ดึงจำนวน items ใน SharePoint list"""
        token = self.auth.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json;odata=verbose",
        }

        target_list = list_name or self.config.list_name
        url = f"{self.config.site_url}/_api/web/lists/GetByTitle('{target_list}')/ItemCount"

        response = self.session.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        count = data.get("d", {}).get("ItemCount", 0)

        logger.info(f"List '{target_list}' contains {count} items")
        return count

    @handle_exceptions(ErrorCategory.CONNECTION, ErrorSeverity.LOW)
    def validate_list_access(self, list_name: Optional[str] = None) -> bool:
        """ตรวจสอบสิทธิ์เข้าถึง list"""
        token = self.auth.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json;odata=verbose",
        }

        target_list = list_name or self.config.list_name
        url = f"{self.config.site_url}/_api/web/lists/GetByTitle('{target_list}')"

        response = self.session.get(url, headers=headers)
        return response.status_code == 200

    @handle_exceptions(ErrorCategory.CONNECTION, ErrorSeverity.LOW)
    def get_list_info(self, list_name: Optional[str] = None) -> Dict:
        """ดึงข้อมูลรายละเอียดของ SharePoint list"""
        token = self.auth.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json;odata=verbose",
        }

        target_list = list_name or self.config.list_name
        url = f"{self.config.site_url}/_api/web/lists/GetByTitle('{target_list}')"

        response = self.session.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        list_info = data.get("d", {})

        return {
            "title": list_info.get("Title", ""),
            "description": list_info.get("Description", ""),
            "item_count": list_info.get("ItemCount", 0),
            "created": list_info.get("Created", ""),
            "last_modified": list_info.get("LastItemModifiedDate", ""),
            "base_type": list_info.get("BaseType", 0),
            "template_type": list_info.get("BaseTemplate", 0),
        }
