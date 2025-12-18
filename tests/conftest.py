"""
Pytest fixtures and mock utilities for testing the Jira MCP server.

Note: pytest-aiohttp is used for async mocking of aiohttp client session.
Note: pytest-asyncio is used for running async tests.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from aiohttp import ClientSession, ClientResponse
import json


@pytest.fixture
def mock_client_session():
    """Mock aiohttp ClientSession for testing HTTP clients."""
    session = MagicMock(spec=ClientSession)
    return session


@pytest.fixture
def mock_response():
    """Factory for creating mock aiohttp responses."""

    def _create(status: int, json_data=None, text_data: str | None = None):
        response = MagicMock(spec=ClientResponse)
        response.status = status
        response.headers = {"Content-Type": "application/json"}
        if json_data is not None:
            response.text = lambda **kwargs: json.dumps(json_data)
            response.json = lambda **kwargs: json_data
        elif text_data is not None:
            response.text = lambda **kwargs: text_data
        else:
            response.text = lambda **kwargs: ""
        return response

    return _create
