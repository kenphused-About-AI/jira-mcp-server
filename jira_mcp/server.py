from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent
from .tools import TOOLS, TOOL_SCHEMAS

mcp = FastMCP("jira-mcp")

@mcp.list_tools()
async def list_tools():
    return TOOL_SCHEMAS

@mcp.call_tool()
async def call_tool(name: str, arguments: dict):
    handler = TOOLS.get(name)
    if not handler:
        raise ValueError(f"Unknown tool: {name}")
    result = await handler(arguments)
    return [TextContent(type="text", text=str(result))]
