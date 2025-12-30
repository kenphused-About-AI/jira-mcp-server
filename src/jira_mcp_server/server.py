"""MCP server implementation for Jira integration."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from mcp.server import FastMCP
from mcp.types import TextContent

from .http_client import close_http_session
from .tools import TOOL_HANDLERS


logger = logging.getLogger(__name__)

# Create server instance
app = FastMCP("jira-mcp-server")

# Property definitions for tool schemas
ISSUE_KEY_PROPERTY = {
    "type": "string",
    "description": "Issue key (e.g., 'DSP-9050')",
}

PROJECT_KEY_PROPERTY = {
    "type": "string",
    "description": "Project key (e.g., 'DSP', 'PROJ')",
}

MAX_RESULTS_PROPERTY = {
    "type": "number",
    "description": "Maximum number of results to return (default: 50)",
    "default": 50,
}

TOOL_DEFINITIONS = [
    {
        "name": "search_jira",
        "description": "Search Jira issues using JQL (Jira Query Language). Returns matching issues with key fields.",
        "properties": {
            "jql": {
                "type": "string",
                "description": "JQL query string (e.g., 'project = DSP AND status = Open')",
            },
            "maxResults": MAX_RESULTS_PROPERTY,
            "startAt": {
                "type": "number",
                "description": "Starting index for pagination (default: 0)",
                "default": 0,
            },
        },
    },
    {
        "name": "list_jira_issues",
        "description": "List issues for a specific project.",
        "properties": {
            "projectKey": PROJECT_KEY_PROPERTY,
            "maxResults": MAX_RESULTS_PROPERTY,
        },
    },
    {
        "name": "get_jira_issue",
        "description": "Get details for a specific Jira issue.",
        "properties": {
            "issueKey": ISSUE_KEY_PROPERTY,
        },
    },
    {
        "name": "get_jira_comments",
        "description": "Get comments for a specific Jira issue.",
        "properties": {
            "issueKey": ISSUE_KEY_PROPERTY,
        },
    },
    {
        "name": "get_jira_transitions",
        "description": "Get available transitions for a Jira issue.",
        "properties": {
            "issueKey": ISSUE_KEY_PROPERTY,
        },
    },
    {
        "name": "get_jira_projects",
        "description": "Get list of Jira projects.",
        "properties": {},
    },
    {
        "name": "create_jira_issue",
        "description": "Create a new Jira issue.",
        "properties": {
            "projectKey": PROJECT_KEY_PROPERTY,
            "summary": {
                "type": "string",
                "description": "Issue summary (title)",
            },
            "description": {
                "type": "string",
                "description": "Issue description",
            },
            "issueType": {
                "type": "string",
                "description": "Issue type (e.g., Task, Bug, Story)",
            },
        },
    },
    {
        "name": "add_jira_comment",
        "description": "Add a comment to a Jira issue.",
        "properties": {
            "issueKey": ISSUE_KEY_PROPERTY,
            "comment": {
                "type": "string",
                "description": "Comment text",
            },
        },
    },
    {
        "name": "update_jira_issue",
        "description": "Update an existing Jira issue.",
        "properties": {
            "issueKey": ISSUE_KEY_PROPERTY,
            "summary": {
                "type": "string",
                "description": "New issue summary",
            },
            "description": {
                "type": "string",
                "description": "New issue description",
            },
        },
    },
    {
        "name": "transition_jira_issue",
        "description": "Transition a Jira issue to a new status.",
        "properties": {
            "issueKey": ISSUE_KEY_PROPERTY,
            "transitionId": {
                "type": "string",
                "description": "ID of the transition",
            },
        },
    },
]


def _format_response(data: Any) -> str:
    """Format response data for the MCP protocol."""
    if isinstance(data, str):
        return data
    return json.dumps(data)


async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls from the MCP server."""
    try:
        handler = TOOL_HANDLERS.get(name)
        if not handler:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        result = await handler(arguments)
        return [TextContent(type="text", text=_format_response(result))]

    except ValueError as e:
        return [TextContent(type="text", text=f"Validation Error: {e}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]


@app.tool()
async def search_jira(
    jql: str, maxResults: int = 50, startAt: int = 0
) -> list[TextContent]:
    """Search Jira issues using JQL."""
    return await call_tool(
        "search_jira", {"jql": jql, "maxResults": maxResults, "startAt": startAt}
    )


@app.tool()
async def list_jira_issues(projectKey: str, maxResults: int = 50) -> list[TextContent]:
    """List issues for a specific project."""
    return await call_tool(
        "list_jira_issues", {"projectKey": projectKey, "maxResults": maxResults}
    )


@app.tool()
async def get_jira_issue(issueKey: str) -> list[TextContent]:
    """Get details for a specific Jira issue."""
    return await call_tool("get_jira_issue", {"issueKey": issueKey})


@app.tool()
async def get_jira_comments(issueKey: str) -> list[TextContent]:
    """Get comments for a specific Jira issue."""
    return await call_tool("get_jira_comments", {"issueKey": issueKey})


@app.tool()
async def get_jira_transitions(issueKey: str) -> list[TextContent]:
    """Get available transitions for a Jira issue."""
    return await call_tool("get_jira_transitions", {"issueKey": issueKey})


@app.tool()
async def get_jira_projects() -> list[TextContent]:
    """Get list of Jira projects."""
    return await call_tool("get_jira_projects", {})


@app.tool()
async def create_jira_issue(
    projectKey: str, summary: str, description: str = "", issueType: str = "Task"
) -> list[TextContent]:
    """Create a new Jira issue."""
    return await call_tool(
        "create_jira_issue",
        {
            "projectKey": projectKey,
            "summary": summary,
            "description": description,
            "issueType": issueType,
        },
    )


@app.tool()
async def add_jira_comment(issueKey: str, comment: str) -> list[TextContent]:
    """Add a comment to a Jira issue."""
    return await call_tool(
        "add_jira_comment", {"issueKey": issueKey, "comment": comment}
    )


@app.tool()
async def update_jira_issue(
    issueKey: str, summary: str = "", description: str = ""
) -> list[TextContent]:
    """Update an existing Jira issue."""
    return await call_tool(
        "update_jira_issue",
        {
            "issueKey": issueKey,
            "summary": summary,
            "description": description,
        },
    )


@app.tool()
async def transition_jira_issue(issueKey: str, transitionId: str) -> list[TextContent]:
    """Transition a Jira issue to a new status."""
    return await call_tool(
        "transition_jira_issue", {"issueKey": issueKey, "transitionId": transitionId}
    )


async def main() -> None:
    """Main entry point for the MCP server."""
    from .config import JIRA_URL

    logger.info(f"Starting Jira MCP server for {JIRA_URL}")

    try:
        await app.run_stdio_async()
        logger.info("Jira MCP server started")
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        logger.info("Jira MCP server stopped")
        await close_http_session()


if __name__ == "__main__":
    asyncio.run(main())
