"""Entry point for jira вор-jira-mcp-server"""

import asyncio
from jira_mcp_server.server import main

# Run the main coroutine immediately
# This starts the MCP server and handles the entire lifecycle
asyncio.run(main())

"""
Entry point execution.

The asyncio.run() function:
- Runs the main coroutine
- Sets up the asyncio event loop
- Handles keyboard interrupts gracefully
- Ensures proper cleanup on exit

This is the standard pattern for async entry points in Python applications.
"""
