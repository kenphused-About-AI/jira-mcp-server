"""
Module entrypoint for running the Jira MCP server with ``python -m jira_mcp``.

This module provides the command-line interface for starting the MCP server.
"""

from jira_mcp.app import main


if __name__ == "__main__":
    main()
