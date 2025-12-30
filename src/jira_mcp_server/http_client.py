"""
HTTP client setup for Jira API requests.

This module provides the HTTP session management for all API communication with Jira.
It handles authentication, connection pooling, and session lifecycle with proper
security configurations.

Key features:
- Basic Auth authentication with proper base64 encoding
- Connection pooling for performance (10 total connections, 5 per host)
- DNS caching for 5 minutes to reduce resolution overhead
- 30-second timeout for all requests
- SSL/TLS validation enabled by default
- Session lifecycle management (create/close)

Security considerations:
- Uses HTTPS (enforced through Jira_URL config)
- Implements proper timeout to prevent DoS
- Connection limits to prevent resource exhaustion
- Automatic session closing on application exit
"""

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
    """
     Get or create the global HTTP session with connection pooling.

     This function implements the singleton pattern for HTTP sessions. It creates
     a new session only when needed (on first call or when previous session is closed),
    then reuses it for subsequent requests. This enables connection pooling and
     reduces overhead.

     Returns:
         Configured aiohttp.ClientSession instance

     Security:
         - Uses Basic Auth with username and API token
         - Sets proper Content-Type and Accept headers
         - Implements 30-second timeout (10s connect, 20s read)
         - Limits concurrent connections (10 total, 5 per host)
         - Enables DNS caching (5 minutes TTL)

     Note:
         The session is cached globally and shared across all API requests.
         The session is automatically closed when the application exits.
    """
    global _http_session

    if _http_session is None or _http_session.closed:
        # Create Basic Auth header
        # Jira API uses email as username and API token as password
        # The token is never logged and session is encrypted via HTTPS
        auth_string = f"{JIRA_USERNAME}:{JIRA_API_TOKEN}"
        auth_bytes = auth_string.encode("ascii")
        auth_b64 = base64.b64encode(auth_bytes).decode("ascii")

        # Configure session with security and performance settings
        # 30-second total timeout prevents hanging requests
        timeout = aiohttp.ClientTimeout(total=30, connect=10)

        # Connection pooling configuration
        # 10 total connections with 5 per host prevents resource exhaustion
        # DNS TTL of 5 minutes reduces lookup overhead for repeated requests
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

        # Create session with proper configuration
        # raise_for_status=False lets us handle error codes manually
        # with proper sanitization
        _http_session = aiohttp.ClientSession(
            headers=headers,
            timeout=timeout,
            connector=connector,
            raise_for_status=False,  # Handle status codes manually
        )

        logger.debug("Created new HTTP session with connection pooling")

    return _http_session


async def close_http_session() -> None:
    """
    Close the global HTTP session.

    This function should be called when the application exits to properly
    close the HTTP session and release resources. It handles the case where
    the session might already be closed.

    Security:
        - Releases network resources
        - Prevents resource leaks on application exit
        - Safe to call multiple times (idempotent)

    Note:
        This is called automatically in the server's main() function
        via the finally block to ensure cleanup even on errors.
    """
    global _http_session

    if _http_session and not _http_session.closed:
        await _http_session.close()
        _http_session = None
        logger.debug("Closed HTTP session")
