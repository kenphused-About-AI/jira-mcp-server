"""
Input validation and sanitization for Jira MCP Server.

This module provides functions to sanitize and validate user inputs to prevent security
vulnerabilities such as injection attacks, path traversal, and command injection.

All sanitization functions follow these principles:
1. Validate input format against expected patterns
2. Reject dangerous characters that could be used for injection
3. Provide clear error messages for debugging
4. Never log sensitive data
5. Raise ValueError for invalid inputs

Security considerations:
- JQL queries are validated to prevent command injection
- Project keys are validated to prevent injection and ensure proper format
- Endpoints are sanitized to prevent path traversal
- Log data is redacted to prevent credential leakage
"""

from __future__ import annotations

import re
from typing import Any, TypeVar

T = TypeVar("T")


def sanitize_log_data(data: Any, max_length: int = 200) -> str:
    """
    Sanitize data for logging by removing sensitive fields and truncating.

    This function recursively traverses data structures to redact sensitive information
    such as passwords, tokens, and API keys before logging. It's used throughout the
    application to prevent accidental logging of credentials.

    Args:
        data: Data to sanitize (dict, str, or other)
        max_length: Maximum length for string output (truncates long data)

    Returns:
        Sanitized string representation safe for logging

    Security:
        - Redacts fields containing 'password', 'token', 'secret', etc.
        - Case-insensitive matching for sensitive field names
        - Handles nested dicts and lists recursively
        - Truncates long output to prevent log spam

    Example:
        input: {'user': 'admin', 'apiToken': 'secret123', 'password': 'pass'}
        output: '{\'user\': \'admin\', \'apiToken\': \'**REDACTED**\', \'password\': \'**REDACTED**\'}'
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
    """
    Convert plain text to Atlassian Document Format (ADF).

    Atlassian Document Format is the rich text format used by Jira for descriptions
    and comments. This function converts simple plain text with paragraph breaks
    into the minimal ADF structure required by the Jira API.

    Args:
        text: Plain text string to convert

    Returns:
        ADF document structure as a dictionary
        Example: {
            "version": 1,
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "paragraph text"}]
                }
            ]
        }

    Note:
        Split text by double newlines to handle paragraphs correctly.
        Empty paragraphs are filtered out.
    """
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
    """
    Sanitize endpoint to prevent path traversal and injection attacks.

    Jira API endpoints can be manipulated through user input. This function validates
    that endpoints only contain safe characters and prevents directory traversal
    attempts.

    Args:
        endpoint: API endpoint path (e.g., "issue/KEY-123")

    Returns:
        Sanitized endpoint string

    Raises:
        ValueError: If endpoint contains dangerous characters or patterns

    Security:
        - Only allows alphanumeric, hyphens, underscores, and forward slashes
        - Rejects relative path patterns like ".."
        - Rejects absolute paths starting with "/"
    """
    # Allow only alphanumeric, hyphens, slashes, and underscores
    if not re.match(r"^[a-zA-Z0-9/_-]+$", endpoint):
        raise ValueError(f"Invalid endpoint format: {endpoint}")

    # Prevent path traversal
    if ".." in endpoint or endpoint.startswith("/"):
        raise ValueError(f"Invalid endpoint path: {endpoint}")

    return endpoint


def sanitize_jql(jql: str) -> str:
    """
    Sanitize JQL query to prevent injection attacks.

    JQL (Jira Query Language) is powerful but can be abused through injection attacks
    if improperly sanitized. This function checks for dangerous characters and patterns
    that could be used to execute arbitrary commands or access unauthorized data.

    Args:
        jql: The JQL query string to sanitize

    Returns:
        The validated JQL query string

    Raises:
        ValueError: If the JQL contains dangerous characters or patterns

    Security:
        - Rejects shell metacharacters: ; | & $ ` \n \r \x00
        - Detects SQL comment patterns that could hide malicious queries
        - Validates input is a non-empty string
        - Provides specific error messages for different injection vectors

    Example:
        Valid: 'project = DSP AND status = Open'
        Invalid: 'project = DSP; rm -rf /tmp' (contains shell metacharacter)
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
    """
    Sanitize project key to prevent injection attacks.

    Jira project keys follow a specific format (typically uppercase letters and numbers)
    and should not contain special characters that could be used for injection.

    Args:
        project_key: The project key to sanitize (e.g., "DSP", "PROJ")

    Returns:
        The validated project key string

    Raises:
        ValueError: If the project key contains invalid characters or format

    Security:
        - Only allows uppercase letters, numbers, and underscores
        - Enforces typical length constraints (2-10 characters)
        - Rejects lowercase letters and special characters

    Example:
        Valid: 'DSP', 'PROJ', 'A123'
        Invalid: 'dsp' (lowercase), 'PROJ!' (special char), 'a' (too short)
    """
    if not project_key or not isinstance(project_key, str):
        raise ValueError("Project key must be a non-empty string")

    # Project keys should only contain uppercase letters, numbers, and underscores
    # Typically 2-10 characters long
    if not re.match(r"^[A-Z0-9_]{2,10}$", project_key):
        raise ValueError(f"Invalid project key format: {project_key}")

    return project_key


def validate_issue_key(issue_key: str) -> str:
    """
    Validate Jira issue key format to prevent injection attacks.

    Jira issue keys follow the format: PROJECT-123 (e.g., DSP-9050)
    with uppercase letters, numbers, and hyphens only. This function validates
    the format to prevent injection through invalid issue keys.

    Args:
        issue_key: The issue key to validate (e.g., "DSP-9050")

    Returns:
        The validated issue key string

    Raises:
        ValueError: If the issue key doesn't match expected format

    Security:
        - Enforces format: ^[A-Z][A-Z0-9]+-\\d+$ (must have hyphen with digits after)
        - Rejects lowercase letters, special characters, and invalid formats
        - Prevents path traversal attempts through invalid issue keys

    Example:
        Valid: 'DSP-9050', 'PROJ-123', 'A1B2-456'
        Invalid: 'dsp-9050' (lowercase), 'DSP/9050' (slash), 'DSP-9-0-50' (mulitple hyphens)
    """
    if not issue_key or not isinstance(issue_key, str):
        raise ValueError("Issue key must be a non-empty string")

    # Issue keys follow format: PROJECT-123 (uppercase, hyphen, digits)
    # Must have at least one letter, then hyphen, then at least one digit
    if not re.match(r"^[A-Z][A-Z0-9]+-\d+$", issue_key):
        raise ValueError(f"Invalid issue key format: {issue_key}")

    return issue_key


def validate_required_args(arguments: dict[str, Any], *required_keys: str) -> None:
    """
    Validate that required arguments are present and non-empty.

    This helper function checks tool arguments before processing to ensure all required
    fields are provided. It's used at the start of all tool handlers to fail fast
    with clear error messages.

    Args:
        arguments: Dictionary of tool arguments
        required_keys: Variable list of required argument names

    Raises:
        ValueError: If any required argument is missing or empty

    Usage:
        # At the start of a tool handler:
        validate_required_args(arguments, "issueKey", "comment")
        # Raises ValueError if issueKey or comment is missing/empty
    """
    missing = [key for key in required_keys if not arguments.get(key)]
    if missing:
        raise ValueError(f"Missing required arguments: {', '.join(missing)}")
