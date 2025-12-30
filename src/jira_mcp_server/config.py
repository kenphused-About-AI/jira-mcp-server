"""
Configuration loading and validation for Jira MCP Server.

This module handles the configuration requirements for the Jira MCP server.
It loads environment variables and validates their correctness before the
application starts.

Environment variables required:
- JIRA_URL: URL to your Jira instance (must use HTTPS)
- JIRA_USERNAME: Username for basic auth (typically email)
- JIRA_API_TOKEN: API token for authentication

Security considerations:
- All configuration is loaded at startup
- Required variables are validated before proceeding
- Sensitive values are never logged in full
- HTTPS is enforced for the Jira URL
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


# Get and validate environment variables
# These variables are loaded once at startup and used throughout the application
JIRA_URL = os.getenv("JIRA_URL")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

"""
Load configuration from environment variables.

The application expects these variables to be set either through:
1. Environment variables in the shell
2. A .env file loaded by the application
3. Provided by the deployment platform

All variables are required and will cause the application to fail
with a clear error message if missing.
"""

if not JIRA_URL or not JIRA_USERNAME or not JIRA_API_TOKEN:
    logger.error("Missing required environment variables")
    raise ValueError(
        "JIRA_URL, JIRA_USERNAME, and JIRA_API_TOKEN environment variables are required"
    )

# Validate JIRA_URL uses HTTPS
# This is critical for security - we never connect to HTTP endpoints
if not JIRA_URL.startswith("https://"):
    raise ValueError("JIRA_URL must use HTTPS protocol")

# Sanitize URL for logging (remove any credentials if present)
# This prevents accidental logging of credentials in URLs
sanitized_url = JIRA_URL.split("@")[-1] if "@" in JIRA_URL else JIRA_URL
logger.info(f"Initialized Jira server for {sanitized_url}")
