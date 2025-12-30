"""Unit tests for Jira MCP Server."""

import json
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any
from aiohttp import ClientResponse, ClientSession
from aiohttp.test_utils import AioHTTPTestCase

# Set required environment variables before importing the module
os.environ["JIRA_URL"] = "https://test.atlassian.net"
os.environ["JIRA_USERNAME"] = "test@example.com"
os.environ["JIRA_API_TOKEN"] = "test-token-123"

# Mock the mcp imports before importing the module
import sys
from unittest.mock import MagicMock


# Create a mock Server class that supports decorators
class MockServer:
    def __init__(self, name):
        self.name = name

    def list_tools(self):
        """Mock decorator for list_tools."""

        def decorator(func):
            return func

        return decorator

    def tool(self):
        """Mock decorator for tool registration."""

        def decorator(func):
            return func

        return decorator

    def call_tool(self):
        """Mock decorator for call_tool."""

        def decorator(func):
            return func

        return decorator

    def run(self, *args, **kwargs):
        """Mock run method."""
        pass

    def create_initialization_options(self):
        """Mock initialization options."""
        return {}


# Create mock TextContent class
class MockTextContent:
    def __init__(self, type, text):
        self.type = type
        self.text = text


# Create mock Tool class
class MockTool:
    def __init__(self, name, description, inputSchema):
        self.name = name
        self.description = description
        self.inputSchema = inputSchema


# Create mock modules
mock_mcp = MagicMock()
mock_mcp.server = MagicMock()
mock_mcp.server.Server = MockServer
mock_mcp.server.stdio = MagicMock()
mock_mcp.server.stdio.stdio_server = MagicMock()
mock_mcp.types = MagicMock()
mock_mcp.types.Tool = MockTool
mock_mcp.types.TextContent = MockTextContent

sys.modules["mcp"] = mock_mcp
sys.modules["mcp.server"] = mock_mcp.server
sys.modules["mcp.server.stdio"] = mock_mcp.server.stdio
sys.modules["mcp.types"] = mock_mcp.types

# Now import the module under test
import sys
import os

sys.path.insert(0, os.path.abspath("src"))
import jira_mcp_server
from jira_mcp_server.jira_api import execute_request
from jira_mcp_server.server import call_tool


class TestTextToADF:
    """Test the text_to_adf function."""

    def test_empty_text(self):
        """Test conversion of empty text."""
        result = jira_mcp_server.text_to_adf("")
        assert result == {"version": 1, "type": "doc", "content": []}

    def test_single_paragraph(self):
        """Test conversion of single paragraph."""
        result = jira_mcp_server.text_to_adf("Hello, World!")
        assert result == {
            "version": 1,
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": "Hello, World!"}],
                }
            ],
        }

    def test_multiple_paragraphs(self):
        """Test conversion of multiple paragraphs."""
        text = "First paragraph\n\nSecond paragraph\n\nThird paragraph"
        result = jira_mcp_server.text_to_adf(text)
        assert result["version"] == 1
        assert result["type"] == "doc"
        assert len(result["content"]) == 3
        assert result["content"][0]["content"][0]["text"] == "First paragraph"
        assert result["content"][1]["content"][0]["text"] == "Second paragraph"
        assert result["content"][2]["content"][0]["text"] == "Third paragraph"

    def test_whitespace_handling(self):
        """Test that extra whitespace is handled correctly."""
        text = "  Paragraph with spaces  \n\n  Another paragraph  "
        result = jira_mcp_server.text_to_adf(text)
        assert len(result["content"]) == 2
        assert result["content"][0]["content"][0]["text"] == "Paragraph with spaces"
        assert result["content"][1]["content"][0]["text"] == "Another paragraph"


class TestExecuteRequest:
    """Test the execute_request function (formerly execute_curl)."""

    @pytest.mark.asyncio
    async def test_successful_get_request(self):
        """Test successful GET request."""
        mock_response = {"key": "DSP-123", "fields": {"summary": "Test issue"}}

        # Create mock response
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.text = AsyncMock(return_value=json.dumps(mock_response))
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=None)

        # Mock session
        mock_session = AsyncMock()
        mock_session.request = MagicMock(return_value=mock_resp)

        with patch(
            "jira_mcp_server.jira_api.get_http_session", return_value=mock_session
        ):
            result = await jira_mcp_server.execute_request("issue/DSP-123")
            assert result == mock_response

    @pytest.mark.asyncio
    async def test_successful_post_request(self):
        """Test successful POST request."""
        mock_response = {"id": "10001", "key": "DSP-124"}

        mock_resp = AsyncMock()
        mock_resp.status = 201
        mock_resp.text = AsyncMock(return_value=json.dumps(mock_response))
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=None)

        mock_session = AsyncMock()
        mock_session.request = MagicMock(return_value=mock_resp)

        data = json.dumps({"fields": {"summary": "New issue"}})
        with patch(
            "jira_mcp_server.jira_api.get_http_session", return_value=mock_session
        ):
            result = await jira_mcp_server.execute_request(
                "issue", method="POST", data=data
            )
            assert result == mock_response

    @pytest.mark.asyncio
    async def test_http_error_400(self):
        """Test handling of HTTP 400 error."""
        error_response = {
            "errorMessages": ["Field 'summary' is required"],
            "errors": {},
        }

        mock_resp = AsyncMock()
        mock_resp.status = 400
        mock_resp.text = AsyncMock(return_value=json.dumps(error_response))
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=None)

        mock_session = AsyncMock()
        mock_session.request = MagicMock(return_value=mock_resp)

        with patch(
            "jira_mcp_server.jira_api.get_http_session", return_value=mock_session
        ):
            with pytest.raises(RuntimeError) as exc_info:
                await jira_mcp_server.execute_request("issue", method="POST")
            assert "HTTP 400" in str(exc_info.value)
            assert "Field 'summary' is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_http_error_404(self):
        """Test handling of HTTP 404 error."""
        error_response = {"errorMessages": ["Issue does not exist"]}

        mock_resp = AsyncMock()
        mock_resp.status = 404
        mock_resp.text = AsyncMock(return_value=json.dumps(error_response))
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=None)

        mock_session = AsyncMock()
        mock_session.request = MagicMock(return_value=mock_resp)

        with patch(
            "jira_mcp_server.jira_api.get_http_session", return_value=mock_session
        ):
            with pytest.raises(RuntimeError) as exc_info:
                await jira_mcp_server.execute_request("issue/INVALID-123")
            assert "HTTP 404" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_query_parameters(self):
        """Test that query parameters are properly encoded."""
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.text = AsyncMock(return_value=json.dumps({"issues": []}))
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=None)

        mock_session = AsyncMock()
        mock_session.request = MagicMock(return_value=mock_resp)

        with patch(
            "jira_mcp_server.jira_api.get_http_session", return_value=mock_session
        ):
            await jira_mcp_server.execute_request(
                "search", query_params={"jql": "project = TEST", "maxResults": 50}
            )
            # Verify request was called with params
            mock_session.request.assert_called_once()
            call_kwargs = mock_session.request.call_args[1]
            assert "params" in call_kwargs

    @pytest.mark.asyncio
    async def test_empty_response(self):
        """Test handling of empty response."""
        mock_resp = AsyncMock()
        mock_resp.status = 204
        mock_resp.text = AsyncMock(return_value="")
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=None)

        mock_session = AsyncMock()
        mock_session.request = MagicMock(return_value=mock_resp)

        with patch(
            "jira_mcp_server.jira_api.get_http_session", return_value=mock_session
        ):
            result = await jira_mcp_server.execute_request(
                "issue/DSP-123", method="PUT"
            )
            assert result == {}

    @pytest.mark.asyncio
    async def test_endpoint_sanitization(self):
        """Test that malicious endpoints are rejected."""
        with pytest.raises(ValueError) as exc_info:
            await jira_mcp_server.execute_request("../../etc/passwd")
        assert "Invalid endpoint" in str(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            await jira_mcp_server.execute_request("issue; rm -rf /")
        assert "Invalid endpoint" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_json_decode_error(self):
        """Test handling of invalid JSON response."""
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.text = AsyncMock(return_value="Invalid JSON")
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=None)

        mock_session = AsyncMock()
        mock_session.request = MagicMock(return_value=mock_resp)

        with patch(
            "jira_mcp_server.jira_api.get_http_session", return_value=mock_session
        ):
            with pytest.raises(RuntimeError) as exc_info:
                await jira_mcp_server.execute_request("issue/DSP-123")
            assert "Failed to parse JSON" in str(exc_info.value)


class TestToolValidation:
    """Test tool argument validation."""

    @pytest.mark.asyncio
    async def test_create_issue_missing_required_fields(self):
        """Test that create_jira_issue validates required fields."""
        # Mock the app's call_tool handler
        with patch("jira_mcp_server.execute_curl"):
            result = await jira_mcp_server.call_tool(
                "create_jira_issue",
                {"projectKey": "", "summary": "Test", "issueType": "Task"},
            )
            # Should return error message
            assert len(result) == 1
            assert (
                "Validation Error" in result[0].text
                or "required" in result[0].text.lower()
            )

    @pytest.mark.asyncio
    async def test_add_comment_missing_fields(self):
        """Test that add_jira_comment validates required fields."""
        with patch("jira_mcp_server.execute_curl"):
            result = await jira_mcp_server.call_tool(
                "add_jira_comment", {"issueKey": "", "comment": "Test comment"}
            )
            assert len(result) == 1
            assert (
                "Validation Error" in result[0].text
                or "required" in result[0].text.lower()
            )

    @pytest.mark.asyncio
    async def test_update_issue_no_fields(self):
        """Test that update_jira_issue requires at least one field."""
        with patch("jira_mcp_server.execute_curl"):
            result = await jira_mcp_server.call_tool(
                "update_jira_issue", {"issueKey": "DSP-123"}
            )
            assert len(result) == 1
            assert (
                "Validation Error" in result[0].text
                or "field" in result[0].text.lower()
            )

    @pytest.mark.asyncio
    async def test_transition_issue_missing_fields(self):
        """Test that transition_jira_issue validates required fields."""
        with patch("jira_mcp_server.execute_curl"):
            result = await jira_mcp_server.call_tool(
                "transition_jira_issue", {"issueKey": "DSP-123", "transitionId": ""}
            )
            assert len(result) == 1
            assert (
                "Validation Error" in result[0].text
                or "required" in result[0].text.lower()
            )


class TestToolIntegration:
    """Integration tests for tool handlers."""

    @pytest.mark.asyncio
    async def test_search_jira_success(self):
        """Test successful search_jira execution."""
        mock_response = {
            "issues": [{"key": "DSP-123", "fields": {"summary": "Test issue"}}],
            "total": 1,
        }
        mock_result = MagicMock()
        mock_result.stdout = json.dumps(mock_response) + "\n200"
        mock_result.stderr = ""

        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.text = AsyncMock(return_value=json.dumps(mock_response))
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=None)

        mock_session = AsyncMock()
        mock_session.request = MagicMock(return_value=mock_resp)

        with patch(
            "jira_mcp_server.jira_api.get_http_session", return_value=mock_session
        ):
            result = await jira_mcp_server.call_tool(
                "search_jira", {"jql": "project = TEST", "maxResults": 50}
            )
            assert len(result) == 1
            response_data = json.loads(result[0].text)
            assert response_data["total"] == 1

    @pytest.mark.asyncio
    async def test_create_issue_with_description(self):
        """Test create_jira_issue with description in ADF format."""
        mock_response = {"id": "10001", "key": "DSP-124"}
        mock_result = MagicMock()
        mock_result.stdout = json.dumps(mock_response) + "\n201"
        mock_result.stderr = ""

        mock_resp = AsyncMock()
        mock_resp.status = 201
        mock_resp.text = AsyncMock(return_value=json.dumps(mock_response))
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=None)

        mock_session = AsyncMock()
        mock_session.request = MagicMock(return_value=mock_resp)

        with patch(
            "jira_mcp_server.jira_api.get_http_session", return_value=mock_session
        ) as mock_session_getter:
            result = await jira_mcp_server.call_tool(
                "create_jira_issue",
                {
                    "projectKey": "DSP",
                    "summary": "Test issue",
                    "description": "This is a test\n\nWith multiple paragraphs",
                    "issueType": "Task",
                },
            )

            # Verify the data sent includes ADF format
            call_kwargs = mock_session.request.call_args[1]
            data = json.loads(call_kwargs["data"])

            assert "description" in data["fields"]
            assert data["fields"]["description"]["type"] == "doc"
            assert data["fields"]["description"]["version"] == 1
            assert len(data["fields"]["description"]["content"]) == 2

    @pytest.mark.asyncio
    async def test_add_comment_with_adf(self):
        """Test add_jira_comment converts text to ADF format."""
        mock_response = {"id": "10002"}
        mock_result = MagicMock()
        mock_result.stdout = json.dumps(mock_response) + "\n201"
        mock_result.stderr = ""

        mock_resp = AsyncMock()
        mock_resp.status = 201
        mock_resp.text = AsyncMock(return_value=json.dumps(mock_response))
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=None)

        mock_session = AsyncMock()
        mock_session.request = MagicMock(return_value=mock_resp)

        with patch(
            "jira_mcp_server.jira_api.get_http_session", return_value=mock_session
        ):
            result = await jira_mcp_server.call_tool(
                "add_jira_comment",
                {"issueKey": "DSP-123", "comment": "This is a comment"},
            )

            # Verify the comment is in ADF format
            call_kwargs = mock_session.request.call_args[1]
            data = json.loads(call_kwargs["data"])

            assert "body" in data
            assert data["body"]["type"] == "doc"
            assert data["body"]["version"] == 1

    @pytest.mark.asyncio
    async def test_unknown_tool(self):
        """Test handling of unknown tool name."""
        result = await jira_mcp_server.call_tool("unknown_tool", {})
        assert len(result) == 1
        assert "Unknown tool" in result[0].text or "Error" in result[0].text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
