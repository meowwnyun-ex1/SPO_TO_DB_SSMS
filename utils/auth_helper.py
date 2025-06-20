import requests
import time
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SharePointAuth:
    """SharePoint authentication helper - แก้ field mapping"""

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
            # แก้: ใช้ field ที่ถูกต้อง
            site_url = self.config.sharepoint_url or self.config.sharepoint_site
            tenant_id = self.config.tenant_id
            client_id = self.config.sharepoint_client_id
            client_secret = self.config.sharepoint_client_secret

            if not all([site_url, tenant_id, client_id, client_secret]):
                logger.error("Missing SharePoint configuration")
                return None

            domain = site_url.split("/")[2]
            url = (
                f"https://accounts.accesscontrol.windows.net/{tenant_id}/tokens/OAuth/2"
            )

            payload = {
                "grant_type": "client_credentials",
                "client_id": f"{client_id}@{tenant_id}",
                "client_secret": client_secret,
                "resource": f"00000003-0000-0ff1-ce00-000000000000/{domain}@{tenant_id}",
            }

            max_retries = getattr(self.config, "max_retries", 3)
            connection_timeout = getattr(self.config, "connection_timeout", 30)

            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        url, data=payload, timeout=connection_timeout
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
                    if attempt < max_retries - 1:
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
