"""
Jira API client implementation.

This module provides the core HTTP client functionality for communicating with
Jira's REST API. It handles authentication, request routing, error handling,
and response processing with proper security measures.

Key features:
- Connection pooling for performance
- Automatic retries for transient errors
- Comprehensive error handling and logging
- Input sanitization to prevent injection attacks
- Response validation and JSON parsing
- Sensitive data redaction in logs

Usage pattern:
    result = await execute_request(
        endpoint="search/jql",
        query_params={"jql": "project = DSP"}
    )
"""

from __future__ import annotations

import aiohttp
import asyncio
import json
import logging
from typing import Any, Optional

from .config import JIRA_URL
from .http_client import get_http_session
from .sanitization import sanitize_endpoint, sanitize_log_data

logger = logging.getLogger(__name__)


async def execute_request(
    endpoint: str,
    method: str = "GET",
    data: Optional[str] = None,
    query_params: Optional[dict[str, Any]] = None,
) -> Any:
    """
    Execute an HTTP request to Jira API with proper error handling and security.

    This is the primary function for making API requests to Jira. It handles all aspects
    of the HTTP communication including authentication, error handling, logging,
    and response processing.

    Args:
        endpoint: API endpoint path (e.g., "search/jql", "issue/KEY-123")
        method: HTTP method (GET, POST, PUT, DELETE)
        data: Request body data as JSON string
        query_params: Dictionary of query parameters

    Returns:
        Parsed JSON response from Jira API

    Raises:
        RuntimeError: For HTTP errors, timeouts, or other client errors

    Security:
        - Sanitizes endpoint to prevent injection
        - Validates query parameters before serialization
        - Redacts sensitive data from error messages
        - Uses connection pooling with proper limits
        - Implements timeout (30 seconds) to prevent hanging

    Example:
        # Search issues
        await execute_request("search/jql", query_params={"jql": "project = DSP"})

        # Create issue
        data = json.dumps({"fields": {...}})
        await execute_request("issue", method="POST", data=data)
    """
    # Sanitize endpoint to prevent injection attacks
    endpoint = sanitize_endpoint(endpoint)

    url = f"{JIRA_URL}/rest/api/3/{endpoint}"

    # Add query parameters if provided
    params = None
    if query_params:
        params = {
            k: json.dumps(v) if isinstance(v, (dict, list)) else str(v)
            for k, v in query_params.items()
            if v is not None
        }

    # Get session with connection pooling
    session = await get_http_session()

    try:
        logger.debug(f"Executing {method} request to {endpoint}")

        # Prepare request kwargs
        request_kwargs: dict[str, Any] = {
            "params": params,
        }

        if data:
            request_kwargs["data"] = data

        # Execute request
        async with session.request(method, url, **request_kwargs) as response:
            status_code = response.status

            # Read response body
            try:
                response_text = await response.text()
            except Exception as e:
                logger.error(f"Failed to read response body: {e}")
                response_text = ""

            # Check for HTTP errors
            if status_code >= 400:
                error_msg = f"HTTP {status_code} error"
                try:
                    error_data = json.loads(response_text) if response_text else {}
                    # Sanitize error messages before logging
                    # Jira returns error details in different formats depending on API version
                    # Handle both "errorMessages" (array) and "errors" (object) formats
                    if "errorMessages" in error_data:
                        # Sanitize each error message individually
                        sanitized_errors = [
                            sanitize_log_data(msg, 200)
                            for msg in error_data["errorMessages"]
                        ]
                        error_msg += f": {', '.join(sanitized_errors)}"
                    elif "errors" in error_data:
                        # Sanitize the errors object
                        error_msg += f": {sanitize_log_data(error_data['errors'], 200)}"
                    else:
                        # Fallback: sanitize raw response text
                        error_msg += f": {sanitize_log_data(response_text, 200)}"
                except json.JSONDecodeError:
                    # Response body is not JSON, sanitize and log as-is
                    error_msg += f": {sanitize_log_data(response_text, 200)}"

                logger.error(f"{method} {endpoint} - {error_msg}")
                raise RuntimeError(error_msg)

            # Parse JSON response
            # Empty response bodies should return empty dict rather than erroring
            if not response_text or response_text.strip() == "":
                return {}

            try:
                parsed_response = json.loads(response_text)
                logger.debug(f"Request successful: {method} {endpoint}")
                return parsed_response
            except json.JSONDecodeError as e:
                # Sanitize response text before logging to avoid exposing sensitive data
                sanitized_response = sanitize_log_data(response_text, 200)
                error_msg = f"Failed to parse JSON response: {e}. Response: {sanitized_response}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

    except aiohttp.ClientError as e:
        error_msg = f"HTTP client error: {str(e)}"
        logger.error(f"{method} {endpoint} - {error_msg}")
        raise RuntimeError(error_msg)
    except asyncio.TimeoutError:
        error_msg = "Request timeout after 30 seconds"
        logger.error(f"{method} {endpoint} - {error_msg}")
        raise RuntimeError(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"{method} {endpoint} - {error_msg}")
        raise RuntimeError(error_msg)


# Alias for backward compatibility
execute_curl = execute_request
