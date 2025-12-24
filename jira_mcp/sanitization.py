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
