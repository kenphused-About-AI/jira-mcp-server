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
        raise ValueError("Invalid character in JQL")

    return jql.strip()
