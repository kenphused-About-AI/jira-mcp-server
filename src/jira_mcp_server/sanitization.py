"""Input validation and sanitization for Jira MCP Server."""

from __future__ import annotations

import re
from typing import Any


def sanitize_log_data(data: Any, max_length: int = 200) -> str:
    """
    Sanitize data for logging by removing sensitive fields and truncating.

    Args:
        data: Data to sanitize (dict, str, or other)
        max_length: Maximum length for string output

    Returns:
        Sanitized string representation
    """
    # Sensitive field names to redact
    sensitive_fields = {
        "password",
        "token",
        "api_key",
        "apikey",
        "secret",
        "authorization",
        "auth",
        "credential",
        "apiToken",
        "accessToken",
        "refreshToken",
        "privateKey",
        "apiSecret",
        "clientSecret",
    }

    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            # Check if key contains sensitive information
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_fields):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, (dict, list)):
                # Recursively sanitize nested structures
                sanitized[key] = sanitize_log_data(value, max_length)
            else:
                sanitized[key] = value
        result = str(sanitized)
    elif isinstance(data, list):
        sanitized_list = [sanitize_log_data(item, max_length) for item in data]
        result = "[" + ", ".join(str(item) for item in sanitized_list) + "]"
    else:
        result = str(data)

    # Truncate if too long
    if len(result) > max_length:
        result = result[:max_length] + "...[truncated]"

    return result


def text_to_adf(text: str) -> dict[str, Any]:
    """Convert plain text to Atlassian Document Format (ADF)."""
    if not text:
        return {"version": 1, "type": "doc", "content": []}

    # Split text into paragraphs
    paragraphs = text.split("\n\n")
    content = []

    for para in paragraphs:
        if para.strip():
            content.append(
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": para.strip()}],
                }
            )

    return {"version": 1, "type": "doc", "content": content}


def sanitize_endpoint(endpoint: str) -> str:
    """Sanitize endpoint to prevent path traversal and injection attacks."""
    # Allow only alphanumeric, hyphens, slashes, and underscores
    if not re.match(r"^[a-zA-Z0-9/_-]+$", endpoint):
        raise ValueError(f"Invalid endpoint format: {endpoint}")

    # Prevent path traversal
    if ".." in endpoint or endpoint.startswith("/"):
        raise ValueError(f"Invalid endpoint path: {endpoint}")

    return endpoint


def sanitize_jql(jql: str) -> str:
    """Sanitize JQL query to prevent injection attacks.

    Args:
        jql: The JQL query string to sanitize

    Returns:
        The sanitized JQL query

    Raises:
        ValueError: If the JQL contains dangerous characters
    """
    if not jql or not isinstance(jql, str):
        raise ValueError("JQL query must be a non-empty string")

    # Check for dangerous shell characters that could be used for injection
    dangerous_chars = [";", "|", "&", "$", "`", "\n", "\r", "\x00"]
    for char in dangerous_chars:
        if char in jql:
            raise ValueError(f"Invalid character in JQL query: {repr(char)}")

    # Check for suspicious patterns that might indicate injection attempts
    suspicious_patterns = [
        r"--",  # SQL comment
        r"/\*",  # Multi-line comment start
        r"\*/",  # Multi-line comment end
    ]
    for pattern in suspicious_patterns:
        if re.search(pattern, jql):
            raise ValueError(f"Suspicious pattern detected in JQL query: {pattern}")

    return jql


def sanitize_project_key(project_key: str) -> str:
    """Sanitize project key to prevent injection attacks.

    Args:
        project_key: The project key to sanitize

    Returns:
        The sanitized project key

    Raises:
        ValueError: If the project key format is invalid
    """
    if not project_key or not isinstance(project_key, str):
        raise ValueError("Project key must be a non-empty string")

    # Project keys should only contain uppercase letters, numbers, and underscores
    # Typically 2-10 characters long
    if not re.match(r"^[A-Z0-9_]{2,10}$", project_key):
        raise ValueError(f"Invalid project key format: {project_key}")

    return project_key


def _validate_required_args(arguments: dict[str, Any], *required_keys: str) -> None:
    """Validate that required arguments are present and non-empty."""
    missing = [key for key in required_keys if not arguments.get(key)]
    if missing:
        raise ValueError(f"Missing required arguments: {', '.join(missing)}")
