"""HTTP client setup for Jira API requests."""

from __future__ import annotations

import base64
import logging
from typing import Optional

import aiohttp

from .config import JIRA_API_TOKEN, JIRA_USERNAME

logger = logging.getLogger(__name__)

# Global session variable
_http_session: Optional[aiohttp.ClientSession] = None


async def get_http_session() -> aiohttp.ClientSession:
    """Get or create the global HTTP session with connection pooling."""
    global _http_session

    if _http_session is None or _http_session.closed:
        # Create Basic Auth header
        auth_string = f"{JIRA_USERNAME}:{JIRA_API_TOKEN}"
        auth_bytes = auth_string.encode("ascii")
        auth_b64 = base64.b64encode(auth_bytes).decode("ascii")

        # Configure session with security and performance settings
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        connector = aiohttp.TCPConnector(
            limit=10,  # Max 10 concurrent connections
            limit_per_host=5,  # Max 5 per host
            ttl_dns_cache=300,  # Cache DNS for 5 minutes
        )

        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        _http_session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout,
            connector=connector,
            raise_for_status=False,  # Handle status codes manually
        )

        logger.debug("Created new HTTP session with connection pooling")

    return _http_session


async def close_http_session() -> None:
    """Close the global HTTP session."""
    global _http_session

    if _http_session and not _http_session.closed:
        await _http_session.close()
        _http_session = None
        logger.debug("Closed HTTP session")
