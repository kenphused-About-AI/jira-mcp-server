import ssl
from jira_mcp.server import mcp
from jira_mcp.config import MCP_BIND_HOST, MCP_BIND_PORT, TLS_CERT, TLS_KEY

def main():
    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain(TLS_CERT, TLS_KEY)

    mcp.run(
        host=MCP_BIND_HOST,
        port=MCP_BIND_PORT,
        ssl_context=ssl_ctx,
    )

if __name__ == "__main__":
    main()
