"""Integration tests for error handling in Jira API client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from jira_mcp.jira_api import JiraAPI


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error scenarios and graceful degradation."""

    async def test_network_timeout_error(self):
        """Network timeout should raise RuntimeError with clean message."""
        api = JiraAPI()

        with patch.object(api._client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = TimeoutError("Connection timed out")

            with pytest.raises(RuntimeError, match="Failed to connect") as exc_info:
                await api.get_issue("TEST-123")

        assert "Connection timed out" not in str(exc_info.value)

    async def test_401_unauthorized_error(self):
        """401 error should not leak credential information."""
        api = JiraAPI()

        with patch.object(api._client, "get", new_callable=AsyncMock) as mock_get:
            response = MagicMock()
            response.status = 401
            response.json = lambda: {"errorMessages": ["User not found"]}
            mock_get.return_value.__aenter__.return_value = response

            with pytest.raises(RuntimeError, match="Unauthorized") as exc_info:
                await api.get_issue("TEST-123")

        assert "User not found" not in str(exc_info.value)
        assert "email@example.com" not in str(exc_info.value)

    async def test_403_forbidden_error(self):
        """403 error should not expose Jira error details."""
        api = JiraAPI()

        with patch.object(api._client, "get", new_callable=AsyncMock) as mock_get:
            response = MagicMock()
            response.status = 403
            response.json = lambda: {"errorMessages": ["Permission denied"]}
            mock_get.return_value.__aenter__.return_value = response

            with pytest.raises(RuntimeError, match="Forbidden") as exc_info:
                await api.get_issue("TEST-123")

        assert "Permission denied" not in str(exc_info.value)

    async def test_non_json_error_response(self):
        """Non-JSON error responses should not crash JSON parsing."""
        api = JiraAPI()

        with patch.object(api._client, "get", new_callable=AsyncMock) as mock_get:
            response = MagicMock()
            response.status = 500
            response.text = lambda **kwargs: "<html>Internal Server Error</html>"
            mock_get.return_value.__aenter__.return_value = response

            # Should not raise JSONDecodeError
            with pytest.raises(RuntimeError, match="Internal Server Error") as exc_info:
                await api.get_issue("TEST-123")

        assert "<html>" not in str(exc_info.value)

    async def test_rate_limit_error(self):
        """429 rate limit should be handled gracefully."""
        api = JiraAPI()

        with patch.object(api._client, "get", new_callable=AsyncMock) as mock_get:
            response = MagicMock()
            response.status = 429
            response.json = lambda: {"errorMessages": ["Rate limit exceeded"]}
            mock_get.return_value.__aenter__.return_value = response

            with pytest.raises(RuntimeError, match="Rate limit exceeded") as exc_info:
                await api.get_issue("TEST-123")

        assert "errorMessages" not in str(exc_info.value)
