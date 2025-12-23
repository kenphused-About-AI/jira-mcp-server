import re


def sanitize_endpoint(endpoint: str) -> str:
    if not re.fullmatch(r"[a-zA-Z0-9/_-]+", endpoint):
        raise ValueError("Invalid endpoint")
    if endpoint.startswith("/") or ".." in endpoint:
        raise ValueError("Path traversal detected")
    return endpoint


def sanitize_jql(jql: str) -> str:
    if not isinstance(jql, str) or not jql.strip():
        raise ValueError("JQL must be non-empty")

    forbidden = ["`", "\x00", "|", "&"]
    if any(c in jql for c in forbidden):
        raise ValueError("Invalid character in JQL.")

    return jql.strip()


def sanitize_issue_key(issue_key: str) -> str:
    if not isinstance(issue_key, str):
        raise ValueError("Issue key must be a string")

    normalized_key = issue_key.strip().upper()
    if not normalized_key:
        raise ValueError("Issue key must be non-empty")

    if not re.fullmatch(r"[A-Z][A-Z0-9]+-\d+", normalized_key):
        raise ValueError("Invalid issue key format")

    return normalized_key


def sanitize_project_key(project_key: str) -> str:
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
    if not isinstance(transition_id, str):
        raise ValueError("Transition ID must be a string")

    trimmed_id = transition_id.strip()
    if not trimmed_id:
        raise ValueError("Transition ID must be non-empty")

    if not re.fullmatch(r"\d+", trimmed_id):
        raise ValueError("Transition ID must be numeric")

    return trimmed_id
