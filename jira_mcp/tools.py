
from mcp.types import Tool
from .jira_api import jira_request
from .sanitization import sanitize_jql

STANDARD_FIELDS = [
    "summary",
    "status",
    "assignee",
    "priority",
    "created",
    "updated",
]

async def search_jira(args):
    jql = sanitize_jql(args["jql"])
    return await jira_request(
        "search",
        params={
            "jql": jql,
            "maxResults": args.get("maxResults", 50),
            "startAt": args.get("startAt", 0),
            "fields": ",".join(STANDARD_FIELDS),
        },
    )

TOOLS = {
    "search_jira": search_jira,
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
    )
]
