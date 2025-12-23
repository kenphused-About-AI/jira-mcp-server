from jira_mcp.server import mcp
from jira_mcp.config import MCP_BIND_HOST, MCP_BIND_PORT


def main():
    mcp.run(
        host=MCP_BIND_HOST,
        port=MCP_BIND_PORT,
    )


if __name__ == "__main__":
    main()
