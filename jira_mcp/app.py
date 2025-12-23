"""
Application entry point for the Jira MCP Server.

This module initializes and runs the FastMCP server, providing
a Model Context Protocol endpoint for Jira Cloud integration.
"""

from jira_mcp.server import mcp
from jira_mcp.config import MCP_BIND_HOST, MCP_BIND_PORT


def main():
    """
    Main application entry point.

    Initializes the FastMCP server and starts it listening on
    the configured host and port (from MCP_BIND_HOST and MCP_BIND_PORT).

    The server provides various MCP tools for interacting with Jira Cloud,
    including issue search, retrieval, creation, updating, and more.

    Example:
        >>> python -m jira_mcp.app  # Starts the MCP server
    """
    mcp.run(
        host=MCP_BIND_HOST,
        port=MCP_BIND_PORT,
    )


if __name__ == "__main__":
    main()
