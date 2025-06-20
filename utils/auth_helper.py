# utils/auth_helper.py - Fixed SharePoint Authentication Helper
import requests
import time
from typing import Optional
import logging
from urllib.parse import urlparse

from utils.config_manager import Config

logger = logging.getLogger(__name__)


class SharePointAuth:
    """
    SharePoint authentication helper with enhanced error handling and token management.
    Supports both App-Only authentication and future Graph API authentication.
    """

    def __init__(self, config: Config):
        self.config = config
        self.token = None
        self.token_expiry = None
        self.token_type = "Bearer"
        self.last_error = None

        # Validate configuration on initialization
        self._validate_config()

        logger.debug("SharePointAuth initialized")

    def _validate_config(self):
        """Validate SharePoint configuration"""
        required_fields = [
            "sharepoint_site",
            "sharepoint_client_id",
            "sharepoint_client_secret",
            "tenant_id",
        ]

        missing_fields = []
        for field in required_fields:
            if not getattr(self.config, field, None):
                missing_fields.append(field)

        if missing_fields:
            error_msg = f"Missing required SharePoint configuration: {', '.join(missing_fields)}"
            logger.error(error_msg)
            self.last_error = error_msg
            raise ValueError(error_msg)

    def get_access_token(self) -> Optional[str]:
        """
        Get access token with caching and automatic refresh.
        Returns cached token if still valid, otherwise requests new token.
        """
        try:
            # Check if we have a valid cached token
            if self._is_token_valid():
                logger.debug("Using cached access token")
                return self.token

            # Request new token
            logger.info("Requesting new SharePoint access token")
            return self._request_new_token()

        except Exception as e:
            logger.error(f"Failed to get access token: {e}")
            self.last_error = str(e)
            return None

    def _is_token_valid(self) -> bool:
        """Check if current token is valid and not expired"""
        if not self.token or not self.token_expiry:
            return False

        # Add 5-minute buffer before expiry
        buffer_time = 300  # 5 minutes
        return time.time() < (self.token_expiry - buffer_time)

    def _request_new_token(self) -> Optional[str]:
        """Request new access token from Azure AD"""
        try:
            # Extract domain from SharePoint site URL
            site_url = self.config.sharepoint_site
            parsed_url = urlparse(site_url)
            domain = parsed_url.netloc

            if not domain:
                raise ValueError(f"Invalid SharePoint site URL: {site_url}")

            # Build token endpoint URL
            tenant_id = self.config.tenant_id
            token_url = (
                f"https://accounts.accesscontrol.windows.net/{tenant_id}/tokens/OAuth/2"
            )

            # Prepare authentication payload
            payload = {
                "grant_type": "client_credentials",
                "client_id": f"{self.config.sharepoint_client_id}@{tenant_id}",
                "client_secret": self.config.sharepoint_client_secret,
                "resource": f"00000003-0000-0ff1-ce00-000000000000/{domain}@{tenant_id}",
            }

            # Request headers
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            }

            # Get retry configuration
            max_retries = getattr(self.config, "max_retries", 3)
            timeout = getattr(self.config, "connection_timeout", 30)

            # Attempt to get token with retries
            for attempt in range(max_retries):
                try:
                    logger.debug(f"Token request attempt {attempt + 1}/{max_retries}")

                    response = requests.post(
                        token_url, data=payload, headers=headers, timeout=timeout
                    )

                    # Check for successful response
                    response.raise_for_status()

                    # Parse token response
                    token_data = response.json()
                    return self._process_token_response(token_data)

                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 401:
                        error_msg = "Authentication failed - check client ID, secret, and tenant ID"
                        logger.error(error_msg)
                        self.last_error = error_msg
                        raise ValueError(error_msg)
                    elif e.response.status_code == 403:
                        error_msg = "Access forbidden - check application permissions"
                        logger.error(error_msg)
                        self.last_error = error_msg
                        raise ValueError(error_msg)
                    else:
                        logger.warning(f"HTTP error on attempt {attempt + 1}: {e}")
                        if attempt == max_retries - 1:
                            raise

                except requests.exceptions.ConnectionError as e:
                    logger.warning(f"Connection error on attempt {attempt + 1}: {e}")
                    if attempt == max_retries - 1:
                        error_msg = (
                            "Failed to connect to SharePoint authentication service"
                        )
                        logger.error(error_msg)
                        self.last_error = error_msg
                        raise ConnectionError(error_msg)

                except requests.exceptions.Timeout as e:
                    logger.warning(f"Timeout on attempt {attempt + 1}: {e}")
                    if attempt == max_retries - 1:
                        error_msg = "Authentication request timed out"
                        logger.error(error_msg)
                        self.last_error = error_msg
                        raise TimeoutError(error_msg)

                except requests.exceptions.RequestException as e:
                    logger.warning(f"Request error on attempt {attempt + 1}: {e}")
                    if attempt == max_retries - 1:
                        raise

                # Wait before retry (exponential backoff)
                if attempt < max_retries - 1:
                    wait_time = 2**attempt
                    logger.debug(f"Waiting {wait_time} seconds before retry")
                    time.sleep(wait_time)

        except Exception as e:
            error_msg = f"Failed to request access token: {e}"
            logger.error(error_msg)
            self.last_error = error_msg
            self.token = None
            self.token_expiry = None
            raise

    def _process_token_response(self, token_data: dict) -> Optional[str]:
        """Process token response and extract access token"""
        try:
            # Validate response structure
            if not isinstance(token_data, dict):
                raise ValueError("Invalid token response format")

            # Extract access token
            access_token = token_data.get("access_token")
            if not access_token:
                error_msg = "No access token in response"
                if "error" in token_data:
                    error_msg += f": {token_data.get('error')} - {token_data.get('error_description', '')}"
                raise ValueError(error_msg)

            # Extract expiry information
            expires_in = token_data.get("expires_in")
            if expires_in:
                try:
                    expires_in = int(expires_in)
                    # Set expiry with 5-minute buffer for safety
                    self.token_expiry = time.time() + expires_in - 300
                except (ValueError, TypeError):
                    logger.warning("Invalid expires_in value, using default 1 hour")
                    self.token_expiry = time.time() + 3600 - 300
            else:
                # Default to 1 hour if no expiry provided
                self.token_expiry = time.time() + 3600 - 300

            # Store token
            self.token = access_token
            self.last_error = None

            logger.info("SharePoint access token obtained successfully")
            logger.debug(f"Token expires at: {time.ctime(self.token_expiry)}")

            return self.token

        except Exception as e:
            error_msg = f"Failed to process token response: {e}"
            logger.error(error_msg)
            self.last_error = error_msg
            raise

    def invalidate_token(self):
        """Invalidate current token to force refresh on next request"""
        logger.info("Invalidating SharePoint access token")
        self.token = None
        self.token_expiry = None
        self.last_error = None

    def is_authenticated(self) -> bool:
        """Check if currently authenticated with valid token"""
        return self._is_token_valid()

    def get_token_info(self) -> dict:
        """Get information about current token"""
        return {
            "has_token": bool(self.token),
            "is_valid": self._is_token_valid(),
            "expires_at": self.token_expiry,
            "expires_in_seconds": (
                max(0, self.token_expiry - time.time()) if self.token_expiry else 0
            ),
            "last_error": self.last_error,
        }

    def test_token(self) -> bool:
        """Test if current token works by making a simple API call"""
        try:
            if not self.token:
                logger.warning("No token available for testing")
                return False

            # Make a simple test request to SharePoint
            site_url = self.config.sharepoint_site.rstrip("/")
            test_url = f"{site_url}/_api/web"

            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json;odata=verbose",
            }

            timeout = getattr(self.config, "connection_timeout", 30)

            response = requests.get(test_url, headers=headers, timeout=timeout)

            if response.status_code == 200:
                logger.info("Token test successful")
                return True
            elif response.status_code == 401:
                logger.warning("Token test failed - token expired or invalid")
                self.invalidate_token()
                return False
            else:
                logger.warning(f"Token test failed with status {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Token test failed with exception: {e}")
            return False

    def refresh_token(self) -> Optional[str]:
        """Force refresh of access token"""
        logger.info("Forcing token refresh")
        self.invalidate_token()
        return self.get_access_token()

    def get_last_error(self) -> Optional[str]:
        """Get last authentication error"""
        return self.last_error

    def __str__(self) -> str:
        """String representation for debugging"""
        info = self.get_token_info()
        return (
            f"SharePointAuth(has_token={info['has_token']}, "
            f"is_valid={info['is_valid']}, "
            f"expires_in={info['expires_in_seconds']:.0f}s)"
        )
