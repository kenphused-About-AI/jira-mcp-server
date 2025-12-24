"""
Input sanitization utilities for Jira MCP Server.

This module provides validation functions to prevent:
- Path traversal attacks
- JQL injection
- SQL injection (via JQL)
- Invalid input formats
- Malicious characters in queries and parameters
"""

import re

# Constants for validation
MAX_ENDPOINT_LENGTH = 200

MAX_JQL_LENGTH = 10000

MAX_ISSUE_KEY_LENGTH = 255

MAX_PROJECT_KEY_LENGTH = 10

MAX_COMMENT_LENGTH = 10000

MAX_TRANSITION_ID = 10000

# Known valid endpoint segments (top-level)
KNOWN_ENDPOINT_SEGMENTS = {
    "issue", "search", "project", "comment", "transitions"
}

ALLOWED_CHARACTERS = re.compile(r"^[a-zA-Z0-9/_-]+$")

JQL_ALLOWLIST_PATTERN = re.compile(
    # Tabs/newlines plus printable characters excluding control ranges
    r"^[\t\n\r \u0020-\u007E\u00A0-\uFFFF]+$"
)

CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")

FORBIDDEN_JQL_CHARS = re.compile(r"[`;|&\\]")

FORBIDDEN_COMMENT_CHARS = re.compile(r'[\x00`;|&\\"]')

UNICODE_BIDIControl = re.compile(r"[\u202A-\u202F\u2066-\u2069]")


def sanitize_endpoint(endpoint: str) -> str:
    if not isinstance(endpoint, str) or not endpoint.strip():
        raise ValueError("Endpoint must be non-empty")

    # Normalize: strip whitespace, collapse duplicate slashes, remove trailing slashes
    normalized = re.sub(r"[/]+", "/", endpoint.strip())
    normalized = normalized.rstrip("/")

    if len(normalized) > MAX_ENDPOINT_LENGTH:
        raise ValueError(f"Endpoint too long (max {MAX_ENDPOINT_LENGTH} characters)")

    if not ALLOWED_CHARACTERS.fullmatch(normalized):
        raise ValueError("Invalid endpoint")

    if normalized.startswith("/") or ".." in normalized:
        raise ValueError("Path traversal detected")

    return normalized


def sanitize_jql(jql: str) -> str:
    """Validate and normalize a JQL (Jira Query Language) expression.

    The sanitizer enforces:
    - Non-empty string input trimmed of surrounding whitespace
    - A strict allowlist of printable characters (excluding control characters)
    - Maximum length of ``MAX_JQL_LENGTH``
    - Rejection of shell/meta characters (````, ``;``, ``|``, ``&``, ``\\``)
    - Explicit control-character and Unicode bidi checks
    - Structured balancing for quotes and parentheses (each quote type tracked
      independently and parentheses only counted when not inside quotes)

    Args:
        jql: The JQL query string.

    Returns:
        The normalized JQL string with collapsed internal whitespace.

    Raises:
        ValueError: If validation fails for any of the rules above.
    """

    if not isinstance(jql, str) or not jql.strip():
        raise ValueError("JQL must be non-empty")

    jql = jql.strip()

    if len(jql) > MAX_JQL_LENGTH:
        raise ValueError(
            f"JQL query too long (max {MAX_JQL_LENGTH} characters)"
        )

    # Check for control characters
    if CONTROL_CHARACTERS.search(jql):
        raise ValueError("Control characters not allowed in JQL")

    # Check for Unicode bidirectional control characters
    if UNICODE_BIDIControl.search(jql):
        raise ValueError(
            "Bidirectional control characters not allowed in JQL"
        )

    # Check for forbidden characters
    if FORBIDDEN_JQL_CHARS.search(jql):
        raise ValueError("Invalid characters in JQL query")

    if not JQL_ALLOWLIST_PATTERN.fullmatch(jql):
        raise ValueError("Invalid characters in JQL query")

    # Normalize whitespace: collapse multiple spaces and newlines
    jql = re.sub(r"\s+", " ", jql)

    # Structured balance checks (ignore parentheses while inside quotes)
    parentheses_stack: list[str] = []
    active_quote: str | None = None
    unclosed_quotes = {"'": 0, '"': 0}

    for char in jql:
        if char in unclosed_quotes:
            if active_quote is None:
                active_quote = char
                unclosed_quotes[char] += 1
            elif active_quote == char:
                unclosed_quotes[char] -= 1
                active_quote = None
            continue

        if active_quote:
            continue

        if char == "(":
            parentheses_stack.append(char)
        elif char == ")":
            if not parentheses_stack:
                raise ValueError("Unbalanced parentheses in JQL query")
            parentheses_stack.pop()

    if active_quote is not None or any(count != 0 for count in unclosed_quotes.values()):
        raise ValueError("Unbalanced quotes in JQL query")

    if parentheses_stack:
        raise ValueError("Unbalanced parentheses in JQL query")

    return jql


def sanitize_issue_key(issue_key: str) -> str:
    if not isinstance(issue_key, str):
        raise ValueError("Issue key must be a string")

    normalized_key = issue_key.strip().upper()
    if not normalized_key:
        raise ValueError("Issue key must be non-empty")

    if len(normalized_key) > MAX_ISSUE_KEY_LENGTH:
        raise ValueError(
            f"Issue key too long (max {MAX_ISSUE_KEY_LENGTH} characters). "
            f"Expected format: PROJECTNUMBER-SEQUENCE (e.g., KEY-123)"
        )

    if not re.fullmatch(r"[A-Z][A-Z0-9]+-\d+", normalized_key):
        raise ValueError(
            "Invalid issue key format. Expected format: PROJECTNUMBER-SEQUENCE "
            "(e.g., KEY-123)"
        )

    return normalized_key


def sanitize_project_key(project_key: str) -> str:
    if not isinstance(project_key, str):
        raise ValueError("Project key must be a string")

    normalized_key = project_key.strip().upper()
    if not normalized_key:
        raise ValueError("Project key must be non-empty")

    if len(normalized_key) > MAX_PROJECT_KEY_LENGTH:
        raise ValueError(
            f"Project key too long (max {MAX_PROJECT_KEY_LENGTH} characters)"
        )

    if not normalized_key[0].isalpha():
        raise ValueError("Project key must start with a letter")

    if not re.fullmatch(r"[A-Z][A-Z0-9_]{1,9}", normalized_key):
        raise ValueError(
            "Invalid project key format. Expected format: "
            "[A-Z][A-Z0-9_]{1,9}"
        )

    return normalized_key


def sanitize_comment_body(body: str) -> str:
    if not isinstance(body, str):
        raise ValueError("Comment body must be a string")

    if not body.strip():
        raise ValueError("Comment body must be non-empty")

    # Check for control characters
    if CONTROL_CHARACTERS.search(body):
        raise ValueError("Control characters not allowed in comment body")

    # Check for forbidden characters
    if FORBIDDEN_COMMENT_CHARS.search(body):
        raise ValueError("Invalid character in comment body")

    # Check for Unicode bidirectional control characters
    if UNICODE_BIDIControl.search(body):
        raise ValueError(
            "Bidirectional control characters not allowed in comment body"
        )

    if len(body) > MAX_COMMENT_LENGTH:
        raise ValueError(
            f"Comment body too long (max {MAX_COMMENT_LENGTH} characters)"
        )

    # Normalize newlines: convert CRLF to LF
    body = body.replace("\r\n", "\n").replace("\r", "\n")
    body = body.strip()

    return body


def sanitize_transition_id(transition_id: str) -> str:
    if not isinstance(transition_id, str):
        raise ValueError("Transition ID must be a string")

    trimmed_id = transition_id.strip()
    if not trimmed_id:
        raise ValueError("Transition ID must be non-empty")

    # Convert to integer to validate and normalize
    try:
        num = int(trimmed_id)
    except ValueError:
        raise ValueError("Transition ID must be numeric")

    if num <= 0:
        raise ValueError("Transition ID must be positive")

    if num > MAX_TRANSITION_ID:
        raise ValueError(
            f"Transition ID too large (max {MAX_TRANSITION_ID})"
        )

    # Return normalized string without leading zeros
    return str(num)



