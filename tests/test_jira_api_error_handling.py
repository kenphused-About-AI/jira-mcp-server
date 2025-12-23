"""Integration-style tests for jira_request error handling."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from jira_mcp.jira_api import jira_request


class _MockResponse:
    def __init__(self, status: int, text: str):
        self.status = status
        self._text = text

    async def text(self, **kwargs):
        return self._text


class _AsyncResponse:
    def __init__(self, status: int, text: str):
        self._delegate = _MockResponse(status, text)
        self.status = status

    async def __aenter__(self):
        return self._delegate

    async def __aexit__(self, exc_type, exc, tb):
        return False


def test_jira_request_raises_runtime_error_on_http_failure():
    async def _run():
        session = MagicMock()
        session.request.return_value = _AsyncResponse(401, "Unauthorized")

        with patch("jira_mcp.jira_api.get_session", AsyncMock(return_value=session)):
            with pytest.raises(RuntimeError, match="Jira 401: Unauthorized"):
                await jira_request("issue/PROJ-1")

    asyncio.run(_run())


def test_jira_request_returns_json_on_success():
    async def _run():
        response_body = {"key": "PROJ-1"}
        session = MagicMock()
        session.request.return_value = _AsyncResponse(200, "{\"key\": \"PROJ-1\"}")

        with patch("jira_mcp.jira_api.get_session", AsyncMock(return_value=session)):
            result = await jira_request("issue/PROJ-1")

        assert result == response_body
        session.request.assert_called_with(
            "GET",
            "https://example.atlassian.net/rest/api/3/issue/PROJ-1",
            params=None,
            json=None,
        )

    asyncio.run(_run())
