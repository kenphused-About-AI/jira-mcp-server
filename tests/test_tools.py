import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from jira_mcp import tools


def test_list_jira_issues_calls_jira_request_with_defaults():
    async def _run():
        mock_response = {"issues": []}
        with patch("jira_mcp.tools.jira_request", new_callable=AsyncMock, return_value=mock_response) as mock_request:
            result = await tools.list_jira_issues({"project": "proj"})

        assert result is mock_response
        mock_request.assert_awaited_with(
            "search",
            params={
                "jql": "project = PROJ ORDER BY updated DESC",
                "maxResults": 50,
                "startAt": 0,
                "fields": "summary,status,assignee,priority,created,updated",
            },
        )

    asyncio.run(_run())


def test_get_jira_issue_uses_field_serializer():
    async def _run():
        with patch("jira_mcp.tools.jira_request", new_callable=AsyncMock) as mock_request:
            await tools.get_jira_issue({"issueKey": "proj-99", "fields": ["summary", "status"]})

        mock_request.assert_awaited_with(
            "issue/PROJ-99",
            params={"fields": "summary,status"},
        )

    asyncio.run(_run())


def test_transition_jira_issue_sanitizes_inputs():
    async def _run():
        with patch("jira_mcp.tools.jira_request", new_callable=AsyncMock) as mock_request:
            await tools.transition_jira_issue({"issueKey": "proj-10", "transitionId": " 21 "})

        mock_request.assert_awaited_with(
            "issue/PROJ-10/transitions",
            method="POST",
            json_body={"transition": {"id": "21"}},
        )

    asyncio.run(_run())


def test_add_jira_comment_rejects_invalid_body():
    async def _run():
        with pytest.raises(ValueError, match="Comment body must be non-empty"):
            await tools.add_jira_comment({"issueKey": "proj-1", "body": "   "})

    asyncio.run(_run())


def test_update_jira_issue_requires_fields():
    async def _run():
        with pytest.raises(ValueError, match="Fields must be a non-empty object"):
            await tools.update_jira_issue({"issueKey": "proj-1", "fields": {}})

    asyncio.run(_run())


def test_tools_registered():
    expected_tools = {
        "search_jira",
        "list_jira_issues",
        "get_jira_issue",
        "get_jira_comments",
        "get_jira_transitions",
        "get_jira_projects",
        "create_jira_issue",
        "update_jira_issue",
        "add_jira_comment",
        "transition_jira_issue",
    }
    assert expected_tools.issubset(set(tools.TOOLS))
    tool_names = {schema.name for schema in tools.TOOL_SCHEMAS}
    assert expected_tools.issubset(tool_names)
