"""Configuration loading and validation for Jira MCP Server."""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


# Get and validate environment variables
JIRA_URL = os.getenv("JIRA_URL")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")


if not JIRA_URL or not JIRA_USERNAME or not JIRA_API_TOKEN:
    logger.error("Missing required environment variables")
    raise ValueError(
        "JIRA_URL, JIRA_USERNAME, and JIRA_API_TOKEN environment variables are required"
    )

# Validate JIRA_URL uses HTTPS
if not JIRA_URL.startswith("https://"):
    raise ValueError("JIRA_URL must use HTTPS protocol")

# Sanitize URL for logging (remove any credentials if present)
sanitized_url = JIRA_URL.split("@")[-1] if "@" in JIRA_URL else JIRA_URL
logger.info(f"Initialized Jira server for {sanitized_url}")
