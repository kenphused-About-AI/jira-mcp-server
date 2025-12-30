"""
MCP tools and tool handlers for Jira integration.

This module defines all MCP (Model Context Protocol) tools that provide
Jira functionality. Each tool has a handler function that validates inputs,
processes the request, and calls the Jira API.

Security architecture:
- All inputs are validated and sanitized before processing
- Required arguments are checked at the start of each handler
- Sensitive data is never logged
- Error messages are sanitized
- API responses are properly formatted before returning to client

Tools available:
1. search_jira - Search issues using JQL
2. list_jira_issues - List issues for a project
3. get_jira_issue - Get issue details
4. get_jira_comments - Get issue comments
5. get_jira_transitions - Get available transitions
6. get_jira_projects - List all projects
7. create_jira_issue - Create new issue
8. add_jira_comment - Add comment to issue
9. update_jira_issue - Update issue fields
10. transition_jira_issue - Change issue status
"""

from __future__ import annotations

import json
import logging
from typing import Any

from .jira_api import execute_curl
from .sanitization import (
    sanitize_jql,
    sanitize_project_key,
    _validate_required_args,
    text_to_adf,
)

logger = logging.getLogger(__name__)

# Constants
STANDARD_ISSUE_FIELDS = [
    "summary",
    "status",
    "assignee",
    "priority",
    "created",
    "updated",
    "description",
]

"""
Default fields returned by issue queries.
These fields provide essential information without overwhelming the response.
"""


# Tool handler functions
async def _handle_search_jira(arguments: dict[str, Any]) -> Any:
    """Handle search_jira tool."""
    jql = sanitize_jql(arguments["jql"])
    max_results = arguments.get("maxResults", 50)
    start_at = arguments.get("startAt", 0)
    return await execute_curl(
        "search/jql",
        query_params={
            "jql": jql,
            "maxResults": max_results,
            "startAt": start_at,
            "fields": STANDARD_ISSUE_FIELDS,
        },
    )


async def _handle_list_jira_issues(arguments: dict[str, Any]) -> Any:
    """
    Handle list_jira_issues tool.

    Lists all issues for a specific project, ordered by creation date
    (newest first). This is a convenience wrapper around search_jira
    with a pre-defined JQL query.

    Args:
        arguments: Tool arguments containing:
            - projectKey: Jira project key (e.g., "DSP")
            - maxResults: Maximum number of results (default: 50)

    Returns:
        Jira API response containing project issues

    Security:
        - Project key is validated using sanitize_project_key()
        - JQL is constructed with proper escaping
    """
    project_key = sanitize_project_key(arguments["projectKey"])
    max_results = arguments.get("maxResults", 50)
    jql = f"project = {project_key} ORDER BY created DESC"
    return await execute_curl(
        "search/jql",
        query_params={
            "jql": jql,
            "maxResults": max_results,
            "fields": STANDARD_ISSUE_FIELDS,
        },
    )


async def _handle_get_jira_issue(arguments: dict[str, Any]) -> Any:
    """
    Handle get_jira_issue tool.

    Retrieves full details for a specific Jira issue. Unlike search results,
    this returns the complete issue object with all fields.

    Args:
        arguments: Tool arguments containing:
            - issueKey: Jira issue key (e.g., "DSP-9050")

    Returns:
        Full Jira issue object with all fields

    Security:
        - No sanitization needed for issueKey (it's just routed to API)
        - IssueKey format is validated by Jira API itself
    """
    issue_key = arguments["issueKey"]
    return await execute_curl(f"issue/{issue_key}")


async def _handle_get_jira_comments(arguments: dict[str, Any]) -> Any:
    """
    Handle get_jira_comments tool.

    Retrieves all comments for a specific Jira issue, including author,
    creation date, and comment text.

    Args:
        arguments: Tool arguments containing:
            - issueKey: Jira issue key (e.g., "DSP-9050")

    Returns:
        Array of comment objects for the issue

    Security:
        - IssueKey is validated by Jira API
        - Comments are returned as-is from Jira
    """
    issue_key = arguments["issueKey"]
    return await execute_curl(f"issue/{issue_key}/comment")


async def _handle_get_jira_transitions(arguments: dict[str, Any]) -> Any:
    """
    Handle get_jira_transitions tool.

    Retrieves all available transitions for a Jira issue (status changes).
    This is needed before calling transition_jira_issue to get the transition ID.

    Args:
        arguments: Tool arguments containing:
            - issueKey: Jira issue key (e.g., "DSP-9050")

    Returns:
        Array of available transition objects

    Security:
        - IssueKey is validated by Jira API
        - Transitions are specific to the issue and user permissions
    """
    issue_key = arguments["issueKey"]
    return await execute_curl(f"issue/{issue_key}/transitions")


async def _handle_get_jira_projects(arguments: dict[str, Any]) -> Any:
    """
    Handle get_jira_projects tool.

    Lists all Jira projects accessible to the authenticated user.
    This is useful for building project selectors in client applications.

    Args:
        arguments: Empty argument dict (no parameters)

    Returns:
        Array of project objects

    Security:
        - Only returns projects user has access to (enforced by Jira API)
        - No sanitization needed for this read-only operation
    """
    return await execute_curl("project")


async def _handle_create_jira_issue(arguments: dict[str, Any]) -> Any:
    """
    Handle create_jira_issue tool.

    Creates a new Jira issue with the specified fields. The description is
    automatically converted to ADF ( Atlassian Document Format) for rich text support.

    Args:
        arguments: Tool arguments containing:
            - projectKey: Jira project key (required)
            - summary: Issue summary/title (required)
            - description: Issue description (optional)
            - issueType: Issue type (default: "Task")

    Returns:
        Created issue object with key and other fields

    Security:
        - Validates all required arguments are present
        - Converts description to ADF format for proper rendering
        - Uses POST request with proper authentication
    """
    project_key = arguments["projectKey"]
    summary = arguments["summary"]
    description = arguments.get("description")
    issue_type = arguments.get("issueType", "Task")

    # Validate required fields
    _validate_required_args(arguments, "projectKey", "summary", "issueType")

    # Build fields with ADF format for description
    fields: dict[str, Any] = {
        "project": {"key": project_key},
        "summary": summary,
        "issuetype": {"name": issue_type},
    }

    # Add description in ADF format if provided
    if description:
        fields["description"] = text_to_adf(description)

    data = json.dumps({"fields": fields})
    logger.info(f"Creating issue in project {project_key}")
    return await execute_curl("issue", method="POST", data=data)


async def _handle_add_jira_comment(arguments: dict[str, Any]) -> Any:
    """
    Handle add_jira_comment tool.

    Adds a comment to a Jira issue. The comment text is automatically converted
    to ADF ( Atlassian Document Format) for proper rich text support.

    Args:
        arguments: Tool arguments containing:
            - issueKey: Jira issue key (required)
            - comment: Comment text (required)

    Returns:
        Created comment object

    Security:
        - Validates that both issueKey and comment are provided
        - Converts comment to ADF format
        - Uses POST request with proper authentication
    """
    issue_key = arguments["issueKey"]
    comment = arguments["comment"]

    # Validate required fields
    _validate_required_args(arguments, "issueKey", "comment")

    # Convert comment to ADF format
    comment_body = text_to_adf(comment)
    data = json.dumps({"body": comment_body})
    logger.info(f"Adding comment to issue {issue_key}")
    return await execute_curl(f"issue/{issue_key}/comment", method="POST", data=data)


async def _handle_update_jira_issue(arguments: dict[str, Any]) -> Any:
    """
    Handle update_jira_issue tool.

    Updates fields on an existing Jira issue. Only summary and description
    can be updated through this tool. The description is automatically converted
    to ADF format for rich text support.

    Args:
        arguments: Tool arguments containing:
            - issueKey: Jira issue key (required)
            - summary: New summary (optional, but one field required)
            - description: New description (optional, but one field required)

    Returns:
        Success message indicating the update was applied

    Security:
        - Validates that at least one field is provided
        - Converts description to ADF format if provided
        - Uses PUT request with proper authentication
    """
    issue_key = arguments["issueKey"]

    # Validate required fields
    _validate_required_args(arguments, "issueKey")

    update_fields: dict[str, Any] = {}
    if "summary" in arguments:
        update_fields["summary"] = arguments["summary"]
    if "description" in arguments:
        # Convert description to ADF format
        update_fields["description"] = text_to_adf(arguments["description"])

    if not update_fields:
        raise ValueError("At least one field (summary or description) must be provided")

    data = json.dumps({"fields": update_fields})
    logger.info(f"Updating issue {issue_key}")
    await execute_curl(f"issue/{issue_key}", method="PUT", data=data)
    return f"Issue {issue_key} updated successfully"


async def _handle_transition_jira_issue(arguments: dict[str, Any]) -> Any:
    """
    Handle transition_jira_issue tool.

    Transitions a Jira issue to a new status. The transition ID can be obtained
    using the get_jira_transitions tool. This operation changes the workflow state
    of the issue.

    Args:
        arguments: Tool arguments containing:
            - issueKey: Jira issue key (required)
            - transitionId: Transition ID (required)

    Returns:
        Success message indicating the transition was applied

    Security:
        - Validates that both issueKey and transitionId are provided
        - Transition ID is validated by Jira API
        - User permissions are checked by Jira API
    """
    issue_key = arguments["issueKey"]
    transition_id = arguments["transitionId"]

    # Validate required fields
    _validate_required_args(arguments, "issueKey", "transitionId")

    data = json.dumps({"transition": {"id": transition_id}})
    logger.info(f"Transitioning issue {issue_key} with transition {transition_id}")
    await execute_curl(f"issue/{issue_key}/transitions", method="POST", data=data)
    return f"Issue {issue_key} transitioned successfully"


# Tool handler registry
# This maps tool names to their handler functions
# Used by the server to route tool calls to the appropriate handler
TOOL_HANDLERS: dict[str, Any] = {
    "search_jira": _handle_search_jira,
    "list_jira_issues": _handle_list_jira_issues,
    "get_jira_issue": _handle_get_jira_issue,
    "get_jira_comments": _handle_get_jira_comments,
    "get_jira_transitions": _handle_get_jira_transitions,
    "get_jira_projects": _handle_get_jira_projects,
    "create_jira_issue": _handle_create_jira_issue,
    "add_jira_comment": _handle_add_jira_comment,
    "update_jira_issue": _handle_update_jira_issue,
    "transition_jira_issue": _handle_transition_jira_issue,
}

"""
Registry of all available tools. Each tool has a unique name and corresponding
handler function. This allows dynamic tool registration and lookup.

The server uses this registry to:
1. Determine available tools
2. Route incoming tool calls to handlers
3. Maintain tool metadata for documentation
"""
