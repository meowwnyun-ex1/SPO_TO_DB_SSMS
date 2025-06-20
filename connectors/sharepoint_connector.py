# connectors/sharepoint_connector.py - Fixed SharePoint Connector
import requests
from typing import List, Dict, Optional, Any
import logging
import time

from utils.auth_helper import SharePointAuth
from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity
from utils.config_manager import Config

logger = logging.getLogger(__name__)


class SharePointConnector:
    """
    Manages connections and operations with SharePoint Online.
    Enhanced with robust error handling and rate limiting.
    """

    def __init__(self, config: Config):
        self.config = config
        self.auth = SharePointAuth(config)
        self.session = requests.Session()
        self.session.timeout = getattr(config, "connection_timeout", 30)

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests

        # Setup session headers
        self.session.headers.update(
            {
                "User-Agent": "DENSO-Neural-Matrix/1.0",
                "Accept": "application/json;odata=verbose",
                "Content-Type": "application/json;odata=verbose",
            }
        )

        logger.info("SharePointConnector initialized")

    def _rate_limit(self):
        """Implement rate limiting to avoid throttling"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _get_site_url(self) -> str:
        """Get properly formatted site URL"""
        site_url = self.config.sharepoint_site
        if not site_url:
            raise ValueError("SharePoint site URL is not configured")

        # Ensure URL doesn't end with slash
        return site_url.rstrip("/")

    @handle_exceptions(ErrorCategory.CONNECTION, ErrorSeverity.HIGH)
    def test_connection(self) -> bool:
        """Test SharePoint connection by getting web properties"""
        try:
            token = self.auth.get_access_token()
            if not token:
                logger.error("Failed to get SharePoint access token")
                return False

            site_url = self._get_site_url()
            url = f"{site_url}/_api/web"

            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json;odata=verbose",
            }

            self._rate_limit()
            response = self.session.get(url, headers=headers)
            response.raise_for_status()

            # Verify response contains expected data
            data = response.json()
            if "d" in data and "Title" in data["d"]:
                logger.info(
                    f"Successfully connected to SharePoint site: {data['d'].get('Title', 'Unknown')}"
                )
                return True
            else:
                logger.warning(
                    "Connected to SharePoint but received unexpected response format"
                )
                return False

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.error("SharePoint authentication failed - check credentials")
            elif e.response.status_code == 403:
                logger.error("SharePoint access forbidden - check permissions")
            elif e.response.status_code == 404:
                logger.error("SharePoint site not found - check URL")
            else:
                logger.error(f"SharePoint HTTP error {e.response.status_code}: {e}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"SharePoint connection failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during SharePoint connection test: {e}")
            return False

    @handle_exceptions(ErrorCategory.DATA, ErrorSeverity.MEDIUM)
    def read_list_items(
        self,
        list_name: str,
        select_fields: List[str] = None,
        filter_query: str = None,
        top: int = None,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Read items from SharePoint list with enhanced querying options

        Args:
            list_name: Name of the SharePoint list
            select_fields: List of fields to select (None for all)
            filter_query: OData filter query
            top: Maximum number of items to return
        """
        if not list_name:
            logger.error("List name is required")
            return None

        logger.info(f"Reading items from SharePoint list: '{list_name}'")

        try:
            token = self.auth.get_access_token()
            if not token:
                logger.error("Failed to get access token for reading list items")
                return None

            site_url = self._get_site_url()

            # Build query URL
            url = f"{site_url}/_api/web/lists/GetByTitle('{list_name}')/items"

            # Build query parameters
            query_params = []

            if select_fields:
                select_query = ",".join(select_fields)
                query_params.append(f"$select={select_query}")

            if filter_query:
                query_params.append(f"$filter={filter_query}")

            if top:
                query_params.append(f"$top={top}")

            if query_params:
                url += "?" + "&".join(query_params)

            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json;odata=verbose",
            }

            all_items = []
            max_retries = getattr(self.config, "max_retries", 3)

            # Handle pagination
            while url:
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        self._rate_limit()
                        response = self.session.get(url, headers=headers)
                        response.raise_for_status()
                        break
                    except requests.exceptions.HTTPError as e:
                        if e.response.status_code == 429:  # Too Many Requests
                            retry_after = int(e.response.headers.get("Retry-After", 1))
                            logger.warning(
                                f"Rate limited, waiting {retry_after} seconds"
                            )
                            time.sleep(retry_after)
                            retry_count += 1
                        else:
                            raise
                    except requests.exceptions.RequestException as e:
                        retry_count += 1
                        if retry_count >= max_retries:
                            raise
                        wait_time = 2**retry_count
                        logger.warning(
                            f"Request failed, retrying in {wait_time} seconds"
                        )
                        time.sleep(wait_time)

                data = response.json().get("d", {})
                items = data.get("results", [])
                all_items.extend(items)

                # Check for next page
                url = data.get("__next")

                logger.debug(f"Retrieved {len(items)} items, total: {len(all_items)}")

            logger.info(
                f"Successfully retrieved {len(all_items)} items from list '{list_name}'"
            )
            return all_items

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to read SharePoint list '{list_name}': {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error reading SharePoint list '{list_name}': {e}")
            return None

    @handle_exceptions(ErrorCategory.DATA, ErrorSeverity.MEDIUM)
    def add_list_item(self, list_name: str, item_data: Dict[str, Any]) -> bool:
        """Add new item to SharePoint list"""
        if not list_name or not item_data:
            logger.error("List name and item data are required")
            return False

        logger.info(f"Adding item to SharePoint list: '{list_name}'")

        try:
            token = self.auth.get_access_token()
            if not token:
                logger.error("Failed to get access token for adding list item")
                return False

            site_url = self._get_site_url()

            # Get list entity type
            entity_type = self._get_list_entity_type(list_name)
            if not entity_type:
                logger.error(f"Could not determine entity type for list '{list_name}'")
                return False

            # Prepare payload
            payload = {"__metadata": {"type": entity_type}}
            payload.update(item_data)

            url = f"{site_url}/_api/web/lists/GetByTitle('{list_name}')/items"

            # Get request digest
            request_digest = self._get_request_digest(site_url, token)
            if not request_digest:
                logger.error("Failed to get request digest")
                return False

            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json;odata=verbose",
                "Content-Type": "application/json;odata=verbose",
                "X-RequestDigest": request_digest,
            }

            self._rate_limit()
            response = self.session.post(url, headers=headers, json=payload)
            response.raise_for_status()

            logger.info(f"Successfully added item to SharePoint list '{list_name}'")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to add item to SharePoint list '{list_name}': {e}")
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error adding item to SharePoint list '{list_name}': {e}"
            )
            return False

    @handle_exceptions(ErrorCategory.DATA, ErrorSeverity.MEDIUM)
    def update_list_item(
        self, list_name: str, item_id: int, item_data: Dict[str, Any]
    ) -> bool:
        """Update existing item in SharePoint list"""
        if not list_name or not item_id or not item_data:
            logger.error("List name, item ID, and item data are required")
            return False

        logger.info(f"Updating item ID {item_id} in SharePoint list: '{list_name}'")

        try:
            token = self.auth.get_access_token()
            if not token:
                logger.error("Failed to get access token for updating list item")
                return False

            site_url = self._get_site_url()

            # Get list entity type
            entity_type = self._get_list_entity_type(list_name)
            if not entity_type:
                logger.error(f"Could not determine entity type for list '{list_name}'")
                return False

            # Prepare payload
            payload = {"__metadata": {"type": entity_type}}
            payload.update(item_data)

            url = (
                f"{site_url}/_api/web/lists/GetByTitle('{list_name}')/items({item_id})"
            )

            # Get request digest
            request_digest = self._get_request_digest(site_url, token)
            if not request_digest:
                logger.error("Failed to get request digest")
                return False

            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json;odata=verbose",
                "Content-Type": "application/json;odata=verbose",
                "X-HTTP-Method": "MERGE",
                "If-Match": "*",
                "X-RequestDigest": request_digest,
            }

            self._rate_limit()
            response = self.session.post(url, headers=headers, json=payload)
            response.raise_for_status()

            logger.info(
                f"Successfully updated item ID {item_id} in SharePoint list '{list_name}'"
            )
            return True

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Failed to update item ID {item_id} in SharePoint list '{list_name}': {e}"
            )
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error updating item ID {item_id} in SharePoint list '{list_name}': {e}"
            )
            return False

    @handle_exceptions(ErrorCategory.CONNECTION, ErrorSeverity.LOW)
    def _get_request_digest(self, site_url: str, token: str) -> Optional[str]:
        """Get X-RequestDigest for write operations"""
        try:
            url = f"{site_url}/_api/contextinfo"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json;odata=verbose",
            }

            self._rate_limit()
            response = self.session.post(url, headers=headers)
            response.raise_for_status()

            data = response.json().get("d", {}).get("GetContextWebInformation", {})
            request_digest = data.get("FormDigestValue")

            if request_digest:
                logger.debug("Successfully obtained X-RequestDigest")
            else:
                logger.warning("FormDigestValue not found in contextinfo response")

            return request_digest

        except Exception as e:
            logger.error(f"Failed to get X-RequestDigest: {e}")
            return None

    @handle_exceptions(ErrorCategory.CONNECTION, ErrorSeverity.LOW)
    def _get_list_entity_type(self, list_name: str) -> Optional[str]:
        """Get ListItemEntityTypeFullName for a given list"""
        try:
            token = self.auth.get_access_token()
            if not token:
                return None

            site_url = self._get_site_url()
            url = f"{site_url}/_api/web/lists/GetByTitle('{list_name}')?$select=ListItemEntityTypeFullName"

            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json;odata=verbose",
            }

            self._rate_limit()
            response = self.session.get(url, headers=headers)
            response.raise_for_status()

            data = response.json().get("d", {}).get("ListItemEntityTypeFullName")
            if data:
                logger.debug(f"Retrieved entity type for '{list_name}': {data}")
            else:
                logger.warning(
                    f"ListItemEntityTypeFullName not found for list '{list_name}'"
                )

            return data

        except Exception as e:
            logger.error(f"Failed to get entity type for list '{list_name}': {e}")
            return None

    @handle_exceptions(ErrorCategory.DATA, ErrorSeverity.LOW)
    def get_list_info(self, list_name: str) -> Optional[Dict]:
        """Get information about a SharePoint list"""
        try:
            token = self.auth.get_access_token()
            if not token:
                return None

            site_url = self._get_site_url()
            url = f"{site_url}/_api/web/lists/GetByTitle('{list_name}')"

            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json;odata=verbose",
            }

            self._rate_limit()
            response = self.session.get(url, headers=headers)
            response.raise_for_status()

            data = response.json().get("d", {})

            list_info = {
                "Title": data.get("Title"),
                "Description": data.get("Description"),
                "ItemCount": data.get("ItemCount"),
                "Created": data.get("Created"),
                "LastItemModifiedDate": data.get("LastItemModifiedDate"),
                "ListItemEntityTypeFullName": data.get("ListItemEntityTypeFullName"),
            }

            logger.debug(f"Retrieved info for list '{list_name}'")
            return list_info

        except Exception as e:
            logger.error(f"Failed to get info for list '{list_name}': {e}")
            return None

    def close(self):
        """Close the requests session"""
        if self.session:
            self.session.close()
            logger.info("SharePoint requests session closed")
