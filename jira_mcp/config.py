"""
Configuration module for the Jira MCP Server.

This module provides runtime configuration through environment variables,
ensuring secure and flexible deployment options.

Environment Variables:
    JIRA_URL: Jira Cloud instance URL (required, must use HTTPS)
    JIRA_USERNAME: Jira username (required, typically email address)
    JIRA_API_TOKEN: Jira API token for authentication (required)
    MCP_BIND_HOST: Host address to bind the MCP server to (optional, default: 0.0.0.0)
    MCP_BIND_PORT: Port to bind the MCP server to (optional, default: 8443)

Raises:
    ValueError: If JIRA_URL doesn't use HTTPS protocol
"""

import os

# Jira Cloud API configuration
# Required: Basic authentication credentials for Jira Cloud
JIRA_URL = os.environ["JIRA_URL"].rstrip("/")
"""Jira Cloud instance URL (e.g., 'https://your-domain.atlassian.net')

Raises:
    ValueError: If JIRA_URL doesn't use HTTPS protocol
"""
JIRA_USERNAME = os.environ["JIRA_USERNAME"]
"""Jira username (typically email address)"""

JIRA_API_TOKEN = os.environ["JIRA_API_TOKEN"]
"""Jira API token for basic authentication"""

# MCP Server binding configuration
MCP_BIND_HOST = os.getenv("MCP_BIND_HOST", "0.0.0.0")
"""Host address to bind the MCP server to (default: 0.0.0.0)"""

MCP_BIND_PORT = int(os.getenv("MCP_BIND_PORT", "8443"))
"""Port to bind the MCP server to (default: 8443)"""

# Validate that JIRA_URL uses HTTPS
if not JIRA_URL.startswith("https://"):
    raise ValueError("JIRA_URL must use HTTPS")
