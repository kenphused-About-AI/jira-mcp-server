import os

JIRA_URL = os.environ["JIRA_URL"].rstrip("/")
JIRA_USERNAME = os.environ["JIRA_USERNAME"]
JIRA_API_TOKEN = os.environ["JIRA_API_TOKEN"]

MCP_BIND_HOST = os.getenv("MCP_BIND_HOST", "0.0.0.0")
MCP_BIND_PORT = int(os.getenv("MCP_BIND_PORT", "8443"))

TLS_CERT = os.getenv("MCP_TLS_CERT", "cert.pem")
TLS_KEY = os.getenv("MCP_TLS_KEY", "key.pem")

if not JIRA_URL.startswith("https://"):
    raise ValueError("JIRA_URL must use HTTPS")
