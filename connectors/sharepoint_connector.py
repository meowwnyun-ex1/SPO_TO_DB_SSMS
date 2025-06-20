# connectors/sharepoint_connector.py - Enhanced with Upload/Update Capability and Robustness
import requests
from typing import List, Dict, Optional, Any
from utils.auth_helper import SharePointAuth
from utils.error_handling import handle_exceptions, ErrorCategory, ErrorSeverity
from utils.config_manager import Config  # For type hinting
import logging

logger = logging.getLogger(__name__)


class SharePointConnector:
    """
    Manages connections and operations with SharePoint Online (Microsoft 365).
    Includes methods for testing connection, reading list items, and adding/updating items.
    """

    def __init__(self, config: Config):
        self.config = config
        self.auth = SharePointAuth(config)
        self.session = requests.Session()
        # Set a default timeout for all requests using this session
        self.session.timeout = getattr(
            config, "connection_timeout", 30
        )  # Default to 30 seconds
        logger.info("SharePointConnector initialized.")

    @handle_exceptions(
        ErrorCategory.CONNECTION, ErrorSeverity.HIGH
    )  # Removed user_message argument
    def test_connection(self) -> bool:
        """Tests the SharePoint connection by attempting to get web properties."""
        try:
            token = self.auth.get_access_token()
            if not token:
                logger.error("Failed to get SharePoint access token.")
                return False

            # Use site_url from config, prioritizing sharepoint_url if available
            site_url = self.config.sharepoint_url or self.config.sharepoint_site
            if not site_url:
                logger.error("SharePoint site URL is not configured.")
                return False

            url = f"{site_url}/_api/web"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json;odata=verbose",
            }

            response = self.session.get(url, headers=headers)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
            logger.info("Successfully connected to SharePoint site.")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"SharePoint connection test failed: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.critical(
                f"An unexpected error occurred during SharePoint connection test: {e}",
                exc_info=True,
            )
            return False

    @handle_exceptions(ErrorCategory.DATA, ErrorSeverity.MEDIUM)
    def read_list_items(
        self, list_name: str, select_fields: List[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Reads all items from a specified SharePoint list.
        Optionally selects specific fields.
        """
        logger.info(f"Attempting to read items from SharePoint list: '{list_name}'")
        try:
            token = self.auth.get_access_token()
            if not token:
                logger.error(
                    "Failed to get SharePoint access token for reading list items."
                )
                return None

            site_url = self.config.sharepoint_url or self.config.sharepoint_site
            if not site_url:
                logger.error(
                    "SharePoint site URL is not configured for reading list items."
                )
                return None

            # Construct URL for list items, with optional field selection
            url = f"{site_url}/_api/web/lists/GetByTitle('{list_name}')/items"
            if select_fields:
                select_query = ",".join(select_fields)
                url += f"?$select={select_query}"

            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json;odata=verbose",
            }

            all_items = []
            while url:
                response = self.session.get(url, headers=headers)
                response.raise_for_status()
                data = response.json().get("d", {})
                items = data.get("results", [])
                all_items.extend(items)

                # Check for next page (pagination)
                url = data.get("__next")  # OData for next page URL

            logger.info(
                f"Successfully retrieved {len(all_items)} items from SharePoint list '{list_name}'."
            )
            return all_items
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Failed to read SharePoint list '{list_name}': {e}", exc_info=True
            )
            return None
        except Exception as e:
            logger.critical(
                f"An unexpected error occurred while reading SharePoint list '{list_name}': {e}",
                exc_info=True,
            )
            return None

    @handle_exceptions(ErrorCategory.DATA, ErrorSeverity.MEDIUM)
    def add_list_item(self, list_name: str, item_data: Dict[str, Any]) -> bool:
        """Adds a new item to a SharePoint list."""
        logger.info(f"Attempting to add item to SharePoint list: '{list_name}'")
        try:
            token = self.auth.get_access_token()
            if not token:
                logger.error(
                    "Failed to get SharePoint access token for adding list item."
                )
                return False

            site_url = self.config.sharepoint_url or self.config.sharepoint_site
            if not site_url:
                logger.error(
                    "SharePoint site URL is not configured for adding list item."
                )
                return False

            # Get the ListItemEntityTypeFullName which is required for adding items
            entity_type = self._get_list_entity_type(list_name)
            if not entity_type:
                logger.error(
                    f"Could not determine entity type for list '{list_name}'. Cannot add item."
                )
                return False

            # Add the required '__metadata' for the entity type
            payload = {"__metadata": {"type": entity_type}}
            payload.update(item_data)  # Merge item data with metadata

            url = f"{site_url}/_api/web/lists/GetByTitle('{list_name}')/items"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json;odata=verbose",
                "Content-Type": "application/json;odata=verbose",
                "X-RequestDigest": self._get_request_digest(
                    site_url, token
                ),  # Important for POST/PUT/DELETE
            }
            if not headers["X-RequestDigest"]:
                logger.error("Failed to get X-RequestDigest. Cannot add item.")
                return False

            response = self.session.post(url, headers=headers, json=payload)
            response.raise_for_status()
            logger.info(f"Successfully added item to SharePoint list '{list_name}'.")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Failed to add item to SharePoint list '{list_name}': {e}",
                exc_info=True,
            )
            return False
        except Exception as e:
            logger.critical(
                f"An unexpected error occurred while adding item to SharePoint list '{list_name}': {e}",
                exc_info=True,
            )
            return False

    @handle_exceptions(ErrorCategory.DATA, ErrorSeverity.MEDIUM)
    def update_list_item(
        self, list_name: str, item_id: int, item_data: Dict[str, Any]
    ) -> bool:
        """Updates an existing item in a SharePoint list."""
        logger.info(
            f"Attempting to update item ID {item_id} in SharePoint list: '{list_name}'"
        )
        try:
            token = self.auth.get_access_token()
            if not token:
                logger.error(
                    "Failed to get SharePoint access token for updating list item."
                )
                return False

            site_url = self.config.sharepoint_url or self.config.sharepoint_site
            if not site_url:
                logger.error(
                    "SharePoint site URL is not configured for updating list item."
                )
                return False

            # Get the ListItemEntityTypeFullName which is required for updating items
            entity_type = self._get_list_entity_type(list_name)
            if not entity_type:
                logger.error(
                    f"Could not determine entity type for list '{list_name}'. Cannot update item."
                )
                return False

            # Add the required '__metadata' for the entity type
            payload = {"__metadata": {"type": entity_type}}
            payload.update(item_data)  # Merge item data with metadata

            url = (
                f"{site_url}/_api/web/lists/GetByTitle('{list_name}')/items({item_id})"
            )
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json;odata=verbose",
                "Content-Type": "application/json;odata=verbose",
                "X-HTTP-Method": "MERGE",  # Use MERGE for update
                "If-Match": "*",  # Use '*' to indicate any version of the item
                "X-RequestDigest": self._get_request_digest(site_url, token),
            }
            if not headers["X-RequestDigest"]:
                logger.error("Failed to get X-RequestDigest. Cannot update item.")
                return False

            response = self.session.post(url, headers=headers, json=payload)
            response.raise_for_status()  # 204 No Content for successful update
            logger.info(
                f"Successfully updated item ID {item_id} in SharePoint list '{list_name}'."
            )
            return True
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Failed to update item ID {item_id} in SharePoint list '{list_name}': {e}",
                exc_info=True,
            )
            return False
        except Exception as e:
            logger.critical(
                f"An unexpected error occurred while updating item ID {item_id} in SharePoint list '{list_name}': {e}",
                exc_info=True,
            )
            return False

    @handle_exceptions(ErrorCategory.CONNECTION, ErrorSeverity.LOW)
    def _get_request_digest(self, site_url: str, token: str) -> Optional[str]:
        """Gets the X-RequestDigest for write operations."""
        logger.debug("Getting X-RequestDigest...")
        try:
            url = f"{site_url}/_api/contextinfo"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json;odata=verbose",
            }
            response = self.session.post(url, headers=headers)
            response.raise_for_status()
            data = response.json().get("d", {}).get("GetContextWebInformation", {})
            request_digest = data.get("FormDigestValue")
            if request_digest:
                logger.debug("Successfully obtained X-RequestDigest.")
            else:
                logger.warning("FormDigestValue not found in contextinfo response.")
            return request_digest
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get X-RequestDigest: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(
                f"An unexpected error occurred getting X-RequestDigest: {e}",
                exc_info=True,
            )
            return None

    @handle_exceptions(ErrorCategory.CONNECTION, ErrorSeverity.LOW)
    def _get_list_entity_type(self, list_name: str) -> Optional[str]:
        """Gets the ListItemEntityTypeFullName for a given list."""
        logger.debug(f"Getting entity type for list: '{list_name}'")
        try:
            token = self.auth.get_access_token()
            if not token:
                logger.error(
                    "Failed to get SharePoint access token for entity type lookup."
                )
                return None

            site_url = self.config.sharepoint_url or self.config.sharepoint_site
            url = f"{site_url}/_api/web/lists/GetByTitle('{list_name}')?$select=ListItemEntityTypeFullName"

            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json;odata=verbose",
            }

            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            data = response.json().get("d", {}).get("ListItemEntityTypeFullName")
            if data:
                logger.debug(f"Retrieved entity type for '{list_name}': {data}")
            else:
                logger.warning(
                    f"ListItemEntityTypeFullName not found for list '{list_name}'. Ensure list name is correct and accessible."
                )
            return data
        except requests.exceptions.RequestException as e:
            logger.error(
                f"Failed to get entity type for list '{list_name}': {e}", exc_info=True
            )
            return None
        except Exception as e:
            logger.error(
                f"An unexpected error occurred getting entity type for '{list_name}': {e}",
                exc_info=True,
            )
            return None

    def close(self):
        """Closes the requests session."""
        if self.session:
            self.session.close()
            logger.info("SharePoint requests session closed.")
