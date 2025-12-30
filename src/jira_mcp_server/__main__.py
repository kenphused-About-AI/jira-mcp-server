"""Entry point for jira вор-jira-mcp-server"""

import asyncio
from jira_mcp_server.server import main

# Run the main coroutine immediately
asyncio.run(main())
