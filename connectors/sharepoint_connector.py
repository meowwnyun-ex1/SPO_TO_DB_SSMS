import requests
import pandas as pd
import time
from typing import List, Dict, Optional
from utils.auth_helper import SharePointAuth
import logging

logger = logging.getLogger(__name__)


class SharePointConnector:
    """SharePoint API connector"""

    def __init__(self, config):
        self.config = config
        self.auth = SharePointAuth(config)
        self.session = requests.Session()

        # Configure session
        self.session.timeout = config.connection_timeout

    def test_connection(self) -> bool:
        """Test SharePoint connection"""
        try:
            token = self.auth.get_access_token()
            if not token:
                return False

            # Test with a simple API call
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json;odata=verbose",
            }

            url = f"{self.config.site_url}/_api/web"
            response = self.session.get(url, headers=headers)

            return response.status_code == 200

        except Exception as e:
            logger.error(f"SharePoint connection test failed: {str(e)}")
            return False

    def get_sites(self) -> List[Dict]:
        """Get available SharePoint sites"""
        try:
            token = self.auth.get_access_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json;odata=verbose",
            }

            # Get site collection URL
            base_url = "/".join(self.config.site_url.split("/")[:3])
            url = f"{base_url}/_api/web/webs"

            response = self.session.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            sites = data.get("d", {}).get("results", [])

            logger.info(f"Retrieved {len(sites)} SharePoint sites")
            return sites

        except Exception as e:
            logger.error(f"Failed to get SharePoint sites: {str(e)}")
            raise

    def get_lists(self, site_url: Optional[str] = None) -> List[Dict]:
        """Get lists from SharePoint site"""
        try:
            token = self.auth.get_access_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json;odata=verbose",
            }

            # Use provided site URL or default
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
                if not lst.get("Hidden", True)
                and lst.get("BaseType") != 1  # Not document libraries
            ]

            logger.info(f"Retrieved {len(filtered_lists)} SharePoint lists")
            return filtered_lists

        except Exception as e:
            logger.error(f"Failed to get SharePoint lists: {str(e)}")
            raise

    def get_list_fields(self, list_name: str) -> List[Dict]:
        """Get fields/columns from a SharePoint list"""
        try:
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

            # Filter out hidden and internal fields
            user_fields = [
                field
                for field in fields
                if not field.get("Hidden", True)
                and not field.get("ReadOnlyField", False)
                and field.get("FieldTypeKind")
                not in [12, 13, 17, 18, 19]  # Exclude certain types
            ]

            logger.info(f"Retrieved {len(user_fields)} fields from list '{list_name}'")
            return user_fields

        except Exception as e:
            logger.error(f"Failed to get list fields: {str(e)}")
            raise

    def fetch_data(self, batch_size: Optional[int] = None) -> Optional[pd.DataFrame]:
        """Fetch data from SharePoint list with pagination"""
        try:
            token = self.auth.get_access_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json;odata=verbose",
            }

            # Build query URL
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
                    time.sleep(0.1)  # Small delay between requests

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
            logger.info(f"DataFrame shape: {df.shape}, Columns: {list(df.columns)}")

            return df

        except Exception as e:
            logger.error(f"Failed to fetch data from SharePoint: {str(e)}")
            raise

    def get_list_item_count(self, list_name: Optional[str] = None) -> int:
        """Get total number of items in a SharePoint list"""
        try:
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

        except Exception as e:
            logger.error(f"Failed to get item count: {str(e)}")
            return 0

    def validate_list_access(self, list_name: Optional[str] = None) -> bool:
        """Validate if we have access to the specified list"""
        try:
            token = self.auth.get_access_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json;odata=verbose",
            }

            target_list = list_name or self.config.list_name
            url = f"{self.config.site_url}/_api/web/lists/GetByTitle('{target_list}')"

            response = self.session.get(url, headers=headers)
            return response.status_code == 200

        except Exception as e:
            logger.error(f"List access validation failed: {str(e)}")
            return False

    def get_list_info(self, list_name: Optional[str] = None) -> Dict:
        """Get detailed information about a SharePoint list"""
        try:
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

        except Exception as e:
            logger.error(f"Failed to get list info: {str(e)}")
            return {}


# utils/auth_helper.py - Authentication helper
"""
SharePoint authentication helper
"""

import requests
import time
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SharePointAuth:
    """SharePoint authentication helper"""

    def __init__(self, config):
        self.config = config
        self.token = None
        self.token_expiry = None

    def get_access_token(self) -> Optional[str]:
        """Get access token with caching and retry logic"""
        # Check if we have a valid cached token
        if self.token and self.token_expiry and time.time() < self.token_expiry:
            return self.token

        # Get new token
        return self._request_new_token()

    def _request_new_token(self) -> Optional[str]:
        """Request new access token from Azure AD"""
        try:
            # Extract domain from site URL
            domain = self.config.site_url.split("/")[2]

            url = f"https://accounts.accesscontrol.windows.net/{self.config.tenant_id}/tokens/OAuth/2"

            payload = {
                "grant_type": "client_credentials",
                "client_id": f"{self.config.client_id}@{self.config.tenant_id}",
                "client_secret": self.config.client_secret,
                "resource": f"00000003-0000-0ff1-ce00-000000000000/{domain}@{self.config.tenant_id}",
            }

            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            # Retry logic
            for attempt in range(self.config.max_retries):
                try:
                    response = requests.post(
                        url,
                        data=payload,
                        headers=headers,
                        timeout=self.config.connection_timeout,
                    )
                    response.raise_for_status()

                    token_data = response.json()
                    self.token = token_data.get("access_token")

                    # Set expiry time (subtract 5 minutes for safety)
                    expires_in = int(token_data.get("expires_in", 3600))
                    self.token_expiry = time.time() + expires_in - 300

                    logger.info("Successfully obtained SharePoint access token")
                    return self.token

                except requests.exceptions.RequestException as e:
                    logger.warning(
                        f"Token request attempt {attempt + 1} failed: {str(e)}"
                    )
                    if attempt < self.config.max_retries - 1:
                        time.sleep(2**attempt)  # Exponential backoff
                    else:
                        raise

        except Exception as e:
            logger.error(f"Failed to get access token: {str(e)}")
            self.token = None
            self.token_expiry = None
            raise

    def invalidate_token(self):
        """Invalidate current token to force refresh"""
        self.token = None
        self.token_expiry = None
        logger.info("SharePoint access token invalidated")
