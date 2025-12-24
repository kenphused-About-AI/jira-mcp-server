"""
HTTP client module providing connection pooling for Jira API requests.

This module manages a shared aiohttp ClientSession for making HTTP requests
to the Jira API with connection pooling and proper authentication.

The module provides:
    - Connection pooling for efficient HTTP requests
    - Basic authentication for Jira API
    - Async session management

Example:
    >>> from jira_mcp.http_client import get_session, close_session

    >>> # Get the HTTP session for making requests
    >>> session = await get_session()

    >>> # Close the session when done
    >>> await close_session()
"""

import base64
import aiohttp
from .config import JIRA_USERNAME, JIRA_API_TOKEN

_session: aiohttp.ClientSession | None = None


async def get_session() -> aiohttp.ClientSession:
    """
    Get or create a shared HTTP session for Jira API requests.

    This function implements connection pooling by maintaining a single
    aiohttp.ClientSession instance across multiple requests. The session
    is created with appropriate authentication headers and timeout configuration.

    Returns:
        aiohttp.ClientSession: The shared HTTP session for making API requests

    Example:
        >>> session = await get_session()
        >>> async with session.get(url) as response:
        >>>     data = await response.json()
    """
    global _session
    if _session and not _session.closed:
        return _session

    auth = base64.b64encode(f"{JIRA_USERNAME}:{JIRA_API_TOKEN}".encode()).decode()

    _session = aiohttp.ClientSession(
        headers={
            "Authorization": f"Basic {auth}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        timeout=aiohttp.ClientTimeout(total=30),
        raise_for_status=False,
    )
    return _session


async def close_session():
    """
    Close the HTTP session and clean up resources.

    This function should be called when the application is shutting down
    to properly close the HTTP session and release resources.

    Returns:
        None

    Example:
        >>> await close_session()  # Clean up when done
    """
    global _session
    if _session:
        await _session.close()
        _session = None
