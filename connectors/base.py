"""
TERRA-X Base Connector with Rate Limiting, Retry Handling & Contract Enforcements
"""

import time
import logging
from typing import Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger("terrax.connectors")


class BaseConnector:
    """Robust base connector for geospatial API querying."""

    def __init__(
        self,
        name: str,
        base_url: str,
        client_id: str = "TERRA-X-SpaceApps-2026/1.0",
        timeout: int = 5,
        max_retries: int = 3,
    ):
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.timeout = timeout
        self.session = requests.Session()
        
        retries = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.session.headers.update({
            "User-Agent": f"TERRA-X/{self.name} ({self.client_id})",
            "Client-Id": self.client_id,
            "Accept": "application/json",
        })

    def request_with_rate_limit(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}" if endpoint else self.base_url
        req_headers = self.session.headers.copy()
        if headers:
            req_headers.update(headers)

        retries = 2
        while retries > 0:
            try:
                resp = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    headers=req_headers,
                    json=json_data,
                    timeout=self.timeout,
                )
                
                # Check for rate limiting 429
                if resp.status_code == 429:
                    retry_after = int(resp.headers.get("Retry-After", 1))
                    logger.warning(
                        "Received 429 Too Many Requests from %s. Sleeping %d sec.",
                        self.name,
                        retry_after,
                    )
                    time.sleep(retry_after)
                    retries -= 1
                    continue

                return resp
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                # Sandbox network isolation or offline: fall back immediately without waiting
                logger.debug("Network unavailable for %s (%s). Using fallback contract response.", url, e)
                break
            except requests.exceptions.RequestException as e:
                logger.warning("Request failed on %s: %s", url, e)
                retries -= 1
                time.sleep(0.5)

        # Fallback empty response
        dummy = requests.Response()
        dummy.status_code = 503
        dummy._content = b'{"error": "Sandbox network isolation active or timeout"}'
        return dummy
