from mcp.types import Tool

from .jira_api import jira_request
from .sanitization import (
    sanitize_comment_body,
    sanitize_issue_key,
    sanitize_jql,
    sanitize_project_key,
    sanitize_transition_id,
)

STANDARD_FIELDS = [
    "summary",
    "status",
    "assignee",
    "priority",
    "created",
    "updated",
]


def _serialize_fields(fields):
    if fields is None:
        return ",".join(STANDARD_FIELDS)

    if not isinstance(fields, list) or not all(isinstance(f, str) and f.strip() for f in fields):
        raise ValueError("Fields must be a list of non-empty strings")

    return ",".join(field.strip() for field in fields)


async def search_jira(args):
    jql = sanitize_jql(args["jql"])
    return await jira_request(
        "search",
        params={
            "jql": jql,
            "maxResults": args.get("maxResults", 50),
            "startAt": args.get("startAt", 0),
            "fields": _serialize_fields(None),
        },
    )


async def list_jira_issues(args):
    project_key = sanitize_project_key(args["project"])
    max_results = args.get("maxResults", 50)
    start_at = args.get("startAt", 0)
    fields = _serialize_fields(args.get("fields"))

    jql = f"project = {project_key} ORDER BY updated DESC"
    return await jira_request(
        "search",
        params={
            "jql": jql,
            "maxResults": max_results,
            "startAt": start_at,
            "fields": fields,
        },
    )


async def get_jira_issue(args):
    issue_key = sanitize_issue_key(args["issueKey"])
    fields = _serialize_fields(args.get("fields"))
    return await jira_request(
        f"issue/{issue_key}",
        params={"fields": fields},
    )


async def get_jira_comments(args):
    issue_key = sanitize_issue_key(args["issueKey"])
    return await jira_request(
        f"issue/{issue_key}/comment",
        params={
            "maxResults": args.get("maxResults", 50),
            "startAt": args.get("startAt", 0),
        },
    )


async def get_jira_transitions(args):
    issue_key = sanitize_issue_key(args["issueKey"])
    return await jira_request(f"issue/{issue_key}/transitions")


async def get_jira_projects(args):
    return await jira_request(
        "project/search",
        params={
            "maxResults": args.get("maxResults", 50),
            "startAt": args.get("startAt", 0),
        },
    )


async def create_jira_issue(args):
    project_key = sanitize_project_key(args["project"])
    summary = args.get("summary", "").strip()
    if not summary:
        raise ValueError("Summary must be non-empty")

    issue_type = args.get("issueType", "Task").strip()
    if not issue_type:
        raise ValueError("Issue type must be non-empty")

    description = args.get("description", "")
    if not isinstance(description, str):
        raise ValueError("Description must be a string")

    return await jira_request(
        "issue",
        method="POST",
        json_body={
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": issue_type},
            }
        },
    )


async def update_jira_issue(args):
    issue_key = sanitize_issue_key(args["issueKey"])
    fields = args.get("fields")
    if not isinstance(fields, dict) or not fields:
        raise ValueError("Fields must be a non-empty object")

    return await jira_request(
        f"issue/{issue_key}",
        method="PUT",
        json_body={"fields": fields},
    )


async def add_jira_comment(args):
    issue_key = sanitize_issue_key(args["issueKey"])
    body = sanitize_comment_body(args["body"])
    return await jira_request(
        f"issue/{issue_key}/comment",
        method="POST",
        json_body={"body": body},
    )


async def transition_jira_issue(args):
    issue_key = sanitize_issue_key(args["issueKey"])
    transition_id = sanitize_transition_id(args["transitionId"])
    return await jira_request(
        f"issue/{issue_key}/transitions",
        method="POST",
        json_body={"transition": {"id": transition_id}},
    )


TOOLS = {
    "search_jira": search_jira,
    "list_jira_issues": list_jira_issues,
    "get_jira_issue": get_jira_issue,
    "get_jira_comments": get_jira_comments,
    "get_jira_transitions": get_jira_transitions,
    "get_jira_projects": get_jira_projects,
    "create_jira_issue": create_jira_issue,
    "update_jira_issue": update_jira_issue,
    "add_jira_comment": add_jira_comment,
    "transition_jira_issue": transition_jira_issue,
}


TOOL_SCHEMAS = [
    Tool(
        name="search_jira",
        description="Search Jira using JQL",
        inputSchema={
            "type": "object",
            "properties": {
                "jql": {"type": "string"},
                "maxResults": {"type": "number", "default": 50},
                "startAt": {"type": "number", "default": 0},
            },
            "required": ["jql"],
        },
    ),
    Tool(
        name="list_jira_issues",
        description="List Jira issues in a project with pagination",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string"},
                "maxResults": {"type": "number", "default": 50},
                "startAt": {"type": "number", "default": 0},
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": STANDARD_FIELDS,
                },
            },
            "required": ["project"],
        },
    ),
    Tool(
        name="get_jira_issue",
        description="Retrieve details for a Jira issue",
        inputSchema={
            "type": "object",
            "properties": {
                "issueKey": {"type": "string"},
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": STANDARD_FIELDS,
                },
            },
            "required": ["issueKey"],
        },
    ),
    Tool(
        name="get_jira_comments",
        description="Retrieve comments for a Jira issue",
        inputSchema={
            "type": "object",
            "properties": {
                "issueKey": {"type": "string"},
                "maxResults": {"type": "number", "default": 50},
                "startAt": {"type": "number", "default": 0},
            },
            "required": ["issueKey"],
        },
    ),
    Tool(
        name="get_jira_transitions",
        description="List available transitions for a Jira issue",
        inputSchema={
            "type": "object",
            "properties": {"issueKey": {"type": "string"}},
            "required": ["issueKey"],
        },
    ),
    Tool(
        name="get_jira_projects",
        description="List Jira projects with pagination support",
        inputSchema={
            "type": "object",
            "properties": {
                "maxResults": {"type": "number", "default": 50},
                "startAt": {"type": "number", "default": 0},
            },
        },
    ),
    Tool(
        name="create_jira_issue",
        description="Create a new Jira issue",
        inputSchema={
            "type": "object",
            "properties": {
                "project": {"type": "string"},
                "summary": {"type": "string"},
                "description": {"type": "string", "default": ""},
                "issueType": {"type": "string", "default": "Task"},
            },
            "required": ["project", "summary"],
        },
    ),
    Tool(
        name="update_jira_issue",
        description="Update fields on an existing Jira issue",
        inputSchema={
            "type": "object",
            "properties": {
                "issueKey": {"type": "string"},
                "fields": {"type": "object"},
            },
            "required": ["issueKey", "fields"],
        },
    ),
    Tool(
        name="add_jira_comment",
        description="Add a comment to a Jira issue",
        inputSchema={
            "type": "object",
            "properties": {
                "issueKey": {"type": "string"},
                "body": {"type": "string"},
            },
            "required": ["issueKey", "body"],
        },
    ),
    Tool(
        name="transition_jira_issue",
        description="Transition a Jira issue to a new status",
        inputSchema={
            "type": "object",
            "properties": {
                "issueKey": {"type": "string"},
                "transitionId": {"type": "string"},
            },
            "required": ["issueKey", "transitionId"],
        },
    ),
]
