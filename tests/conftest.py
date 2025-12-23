"""
Pytest fixtures and mock utilities for testing the Jira MCP server.

Note: pytest-aiohttp is used for async mocking of aiohttp client session.
Note: pytest-asyncio is used for running async tests.
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from aiohttp import ClientResponse, ClientSession

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os_environ_defaults = {
    "JIRA_URL": "https://example.atlassian.net",
    "JIRA_USERNAME": "test@example.com",
    "JIRA_API_TOKEN": "token",
}

for key, value in os_environ_defaults.items():
    os.environ.setdefault(key, value)


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
