"""MCP tools and tool handlers for Jira integration."""

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
    """Handle list_jira_issues tool."""
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
    """Handle get_jira_issue tool."""
    issue_key = arguments["issueKey"]
    return await execute_curl(f"issue/{issue_key}")


async def _handle_get_jira_comments(arguments: dict[str, Any]) -> Any:
    """Handle get_jira_comments tool."""
    issue_key = arguments["issueKey"]
    return await execute_curl(f"issue/{issue_key}/comment")


async def _handle_get_jira_transitions(arguments: dict[str, Any]) -> Any:
    """Handle get_jira_transitions tool."""
    issue_key = arguments["issueKey"]
    return await execute_curl(f"issue/{issue_key}/transitions")


async def _handle_get_jira_projects(arguments: dict[str, Any]) -> Any:
    """Handle get_jira_projects tool."""
    return await execute_curl("project")


async def _handle_create_jira_issue(arguments: dict[str, Any]) -> Any:
    """Handle create_jira_issue tool."""
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
    """Handle add_jira_comment tool."""
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
    """Handle update_jira_issue tool."""
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
    """Handle transition_jira_issue tool."""
    issue_key = arguments["issueKey"]
    transition_id = arguments["transitionId"]

    # Validate required fields
    _validate_required_args(arguments, "issueKey", "transitionId")

    data = json.dumps({"transition": {"id": transition_id}})
    logger.info(f"Transitioning issue {issue_key} with transition {transition_id}")
    await execute_curl(f"issue/{issue_key}/transitions", method="POST", data=data)
    return f"Issue {issue_key} transitioned successfully"


# Tool handler registry
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
