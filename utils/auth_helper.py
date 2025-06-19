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
        """Get access token with caching"""
        if self.token and self.token_expiry and time.time() < self.token_expiry:
            return self.token
        return self._request_new_token()

    def _request_new_token(self) -> Optional[str]:
        """Request new access token from Azure AD"""
        try:
            domain = self.config.site_url.split("/")[2]
            url = f"https://accounts.accesscontrol.windows.net/{self.config.tenant_id}/tokens/OAuth/2"

            payload = {
                "grant_type": "client_credentials",
                "client_id": f"{self.config.client_id}@{self.config.tenant_id}",
                "client_secret": self.config.client_secret,
                "resource": f"00000003-0000-0ff1-ce00-000000000000/{domain}@{self.config.tenant_id}",
            }

            for attempt in range(self.config.max_retries):
                try:
                    response = requests.post(
                        url, data=payload, timeout=self.config.connection_timeout
                    )
                    response.raise_for_status()

                    token_data = response.json()
                    self.token = token_data.get("access_token")
                    expires_in = int(token_data.get("expires_in", 3600))
                    self.token_expiry = time.time() + expires_in - 300

                    logger.info("SharePoint access token obtained")
                    return self.token

                except requests.exceptions.RequestException as e:
                    logger.warning(f"Token attempt {attempt + 1} failed: {str(e)}")
                    if attempt < self.config.max_retries - 1:
                        time.sleep(2**attempt)
                    else:
                        raise

        except Exception as e:
            logger.error(f"Failed to get access token: {str(e)}")
            self.token = None
            self.token_expiry = None
            raise

    def invalidate_token(self):
        """Invalidate current token"""
        self.token = None
        self.token_expiry = None
