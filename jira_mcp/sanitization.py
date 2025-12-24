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
    r"^[\t\n\r \\u0020-~]+$"
)

CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")

FORBIDDEN_JQL_CHARS = re.compile(r"[`;|&\\"]")

FORBIDDEN_COMMENT_CHARS = re.compile(r"[\x00`;|&\\"]")

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

    # Validate that all top-level segments are known
    segments = normalized.split("/")
    for segment in segments:
        if segment and segment not in KNOWN_ENDPOINT_SEGMENTS:
            raise ValueError(f"Unknown endpoint segment: {segment}")

    return normalized


def sanitize_jql(jql: str) -> str:
    if not isinstance(jql, str) or not jql.strip():
        raise ValueError("JQL must be non-empty")

    original_jql = jql
    jql = jql.strip()

    if len(jql) > MAX_JQL_LENGTH:
        raise ValueError(
            f"JQL query too long (max {MAX_JQL_LENGTH} characters)"
        )

    # Check for control characters
    if CONTROL_CHARACTERS.search(jql):
        raise ValueError("Control characters not allowed in JQL")

    # Check for forbidden characters
    if FORBIDDEN_JQL_CHARS.search(jql):
        raise ValueError("Invalid characters in JQL query")

    # Check for Unicode bidirectional control characters
    if UNICODE_BIDIControl.search(jql):
        raise ValueError(
            "Bidirectional control characters not allowed in JQL"
        )

    # Normalize whitespace: collapse multiple spaces and newlines
    jql = re.sub(r"\s+", " ", jql)

    # Check for balanced quotes and parentheses
    open_quotes = jql.count('"') + jql.count("'")
    if open_quotes % 2 != 0:
        raise ValueError("Unbalanced quotes in JQL query")

    open_parens = jql.count("(")
    close_parens = jql.count(")")
    if open_parens != close_parens:
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
        raise ValueError("Invalid characters in comment body")

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
    if not isinstance(transition_id, str) or not transition_id.strip():
        raise ValueError("Transition ID must be a non-empty string")

    # Convert to integer to validate and normalize
    try:
        num = int(transition_id)
    except ValueError:
        raise ValueError("Transition ID must be a number")

    if num <= 0:
        raise ValueError("Transition ID must be positive")

    if num > MAX_TRANSITION_ID:
        raise ValueError(
            f"Transition ID too large (max {MAX_TRANSITION_ID})"
        )

    # Return normalized string without leading zeros
    return str(num)



def sanitize_endpoint(endpoint: str) -> str:
    """
    Sanitize Jira API endpoint to prevent path traversal.

    Args:
        endpoint: The API endpoint (e.g., 'issue/KEY-123', 'search')

    Returns:
        The sanitized endpoint string

    Raises:
        ValueError: If endpoint contains invalid characters or path traversal attempts

    Examples:
        >>> sanitize_endpoint('issue/KEY-123')
        'issue/KEY-123'

        >>> sanitize_endpoint('issue/../../../etc/passwd')
        ValueError: Path traversal detected
    """
    if not re.fullmatch(r"[a-zA-Z0-9/_-]+", endpoint):
        raise ValueError("Invalid endpoint")
    if endpoint.startswith("/") or ".." in endpoint:
        raise ValueError("Path traversal detected")
    return endpoint


def sanitize_jql(jql: str) -> str:
    """
    Sanitize JQL (Jira Query Language) to prevent injection.

    Validates that the JQL string:
    - Is non-empty
    - Doesn't contain backticks (code injection)
    - Doesn't contain null bytes (termination attacks)
    - Doesn't contain shell meta-characters

    Args:
        jql: The JQL query string

    Returns:
        The sanitized JQL string (trimmed)

    Raises:
        ValueError: If JQL contains forbidden characters or is empty

    Examples:
        >>> sanitize_jql('project = DSP ORDER BY updated DESC')
        'project = DSP ORDER BY updated DESC'

        >>> sanitize_jql('`REVERT --help`')
        ValueError: Invalid character in JQL.
    """
    if not isinstance(jql, str) or not jql.strip():
        raise ValueError("JQL must be non-empty")

    forbidden = ["`", "\x00", "|", "&"]
    if any(c in jql for c in forbidden):
        raise ValueError("Invalid character in JQL.")

    return jql.strip()


def sanitize_issue_key(issue_key: str) -> str:
    """
    Sanitize and validate Jira issue key format.

    Valid issue keys must match the pattern: PROJECTNUMBER-SEQUENCE
    where PROJECT is uppercase letters, and NUMBER is digits.

    Args:
        issue_key: The issue key (e.g., 'KEY-123', 'MAX-456')

    Returns:
        The normalized, uppercase issue key

    Raises:
        ValueError: If issue key format is invalid

    Examples:
        >>> sanitize_issue_key('KEY-123')
        'KEY-123'

        >>> sanitize_issue_key('invalid')
        ValueError: Invalid issue key format
    """
    if not isinstance(issue_key, str):
        raise ValueError("Issue key must be a string")

    normalized_key = issue_key.strip().upper()
    if not normalized_key:
        raise ValueError("Issue key must be non-empty")

    if not re.fullmatch(r"[A-Z][A-Z0-9]+-\d+", normalized_key):
        raise ValueError("Invalid issue key format")

    return normalized_key


def sanitize_project_key(project_key: str) -> str:
    """
    Sanitize and validate Jira project key format.

    Valid project keys must:
    - Start with a letter
    - Contain only alphanumeric characters and underscores
    - Be 2-10 characters long

    Args:
        project_key: The project key (e.g., 'DSP', 'MAX', 'CUSTOMER_Portal')

    Returns:
        The normalized, uppercase project key

    Raises:
        ValueError: If project key format is invalid

    Examples:
        >>> sanitize_project_key('DSP')
        'DSP'

        >>> sanitize_project_key('1INVALID')
        ValueError: Project key must start with a letter
    """
    if not isinstance(project_key, str):
        raise ValueError("Project key must be a string")

    normalized_key = project_key.strip().upper()
    if not normalized_key:
        raise ValueError("Project key must be non-empty")

    if not normalized_key[0].isalpha():
        raise ValueError("Project key must start with a letter")

    if not re.fullmatch(r"[A-Z][A-Z0-9_]{1,9}", normalized_key):
        raise ValueError("Invalid project key format")

    return normalized_key


def sanitize_comment_body(body: str) -> str:
    """
    Sanitize comment body text to prevent injection attacks.

    Validates that comment:
    - Is non-empty
    - Doesn't contain backticks (code injection)
    - Doesn't contain null bytes
    - Doesn't contain shell meta-characters

    Args:
        body: The comment body text

    Returns:
        The sanitized comment text (trimmed)

    Raises:
        ValueError: If comment contains forbidden characters or is empty

    Examples:
        >>> sanitize_comment_body('Fixed the issue')
        'Fixed the issue'

        >>> sanitize_comment_body('')
        ValueError: Comment body must be non-empty
    """
    if not isinstance(body, str):
        raise ValueError("Comment body must be a string")

    trimmed_body = body.strip()
    if not trimmed_body:
        raise ValueError("Comment body must be non-empty")

    forbidden = ["\x00", "`", "|", "&"]
    if any(char in trimmed_body for char in forbidden):
        raise ValueError("Invalid character in comment body")

    return trimmed_body


def sanitize_transition_id(transition_id: str) -> str:
    """
    Sanitize and validate Jira transition ID.

    Transition IDs must be numeric values representing the transition ID
    in the Jira workflow.

    Args:
        transition_id: The transition ID (e.g., '11', '21')

    Returns:
        The sanitized, trimmed transition ID

    Raises:
        ValueError: If transition ID is not numeric or empty

    Examples:
        >>> sanitize_transition_id('11')
        '11'

        >>> sanitize_transition_id('invalid')
        ValueError: Transition ID must be numeric
    """
    if not isinstance(transition_id, str):
        raise ValueError("Transition ID must be a string")

    trimmed_id = transition_id.strip()
    if not trimmed_id:
        raise ValueError("Transition ID must be non-empty")

    if not re.fullmatch(r"\d+", trimmed_id):
        raise ValueError("Transition ID must be numeric")

    return trimmed_id
