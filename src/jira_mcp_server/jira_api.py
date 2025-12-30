"""Jira API client implementation."""

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
    """Execute an HTTP request to Jira API with proper error handling and security."""
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
                    if "errorMessages" in error_data:
                        # Sanitize error messages before logging
                        sanitized_errors = [
                            sanitize_log_data(msg, 200)
                            for msg in error_data["errorMessages"]
                        ]
                        error_msg += f": {', '.join(sanitized_errors)}"
                    elif "errors" in error_data:
                        error_msg += f": {sanitize_log_data(error_data['errors'], 200)}"
                    else:
                        error_msg += f": {sanitize_log_data(response_text, 200)}"
                except json.JSONDecodeError:
                    error_msg += f": {sanitize_log_data(response_text, 200)}"

                logger.error(f"{method} {endpoint} - {error_msg}")
                raise RuntimeError(error_msg)

            # Parse JSON response
            if not response_text or response_text.strip() == "":
                return {}

            try:
                parsed_response = json.loads(response_text)
                logger.debug(f"Request successful: {method} {endpoint}")
                return parsed_response
            except json.JSONDecodeError as e:
                # Sanitize response text before logging
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
