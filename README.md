# Jira MCP Server

A secure Model Context Protocol (MCP) server for interacting with Jira Cloud over HTTPS.
This server exposes Jira functionality (search, issues, comments, transitions, projects) as MCP tools, enabling integration with agent frameworks such as Langflow, Goose, and OpenWebUI.

The project uses:
- FastMCP (HTTP/HTTPS MCP transport)
- aiohttp for async Jira API access
- uv for dependency and environment management
- TLS-only communication (no stdio)

---

## Features

- HTTPS-only MCP server
- JQL search with pagination support
- Get issues, comments, transitions, and projects
- Create, update, comment, and transition Jira issues
- No business logic in __init__.py
- Connection pooling for Jira API requests
- Input sanitization for JQL and endpoints
- Environment-based configuration

---

## Requirements

- Python 3.11+
- Jira Cloud account
- Jira API token
- TLS certificate and key (self-signed or trusted)
- uv (https://github.com/astral-sh/uv)

---

## Project Structure

jira-mcp-server/
├── jira_mcp/
│   ├── __init__.py
│   ├── app.py            # HTTPS entrypoint
│   ├── config.py         # Environment & server config
│   ├── http_client.py    # aiohttp session handling
│   ├── jira_api.py       # Jira REST API wrapper
│   ├── sanitization.py  # Input validation
│   ├── server.py         # FastMCP server
│   └── tools.py          # MCP tool definitions
├── pyproject.toml
├── README.md
└── .gitignore

---

## Installation

1. Clone the repository

git clone https://github.com/your-org/jira-mcp-server.git
cd jira-mcp-server

2. Initialize the environment

uv venv
source .venv/bin/activate

3. Install dependencies

uv sync

---

## Configuration

Set the following environment variables:

export JIRA_URL="https://your-domain.atlassian.net"
export JIRA_USERNAME="email@example.com"
export JIRA_API_TOKEN="your-api-token"

export MCP_BIND_HOST="0.0.0.0"
export MCP_BIND_PORT="8443"

export MCP_TLS_CERT="cert.pem"
export MCP_TLS_KEY="key.pem"

IMPORTANT: JIRA_URL must use HTTPS.

---

## TLS Certificates

For local development, you can generate a self-signed certificate:

openssl req -x509 -newkey rsa:4096 \
  -keyout key.pem \
  -out cert.pem \
  -days 365 \
  -nodes

For production, use a trusted certificate such as Let’s Encrypt.

---

## Running the Server

Using uv:

uv run jira-mcp-server

Or directly:

uv run python -m jira_mcp.app

The MCP server will start on:

https://<host>:<port>

---

## Available MCP Tools

- search_jira – Search Jira issues using JQL
- list_jira_issues – List recent issues in a project
- get_jira_issue – Retrieve a single issue
- get_jira_comments – Retrieve issue comments
- get_jira_transitions – Get available transitions
- get_jira_projects – List Jira projects
- create_jira_issue – Create a new issue
- update_jira_issue – Update an existing issue
- add_jira_comment – Add a comment to an issue
- transition_jira_issue – Transition an issue to a new status

---

## Example JQL Queries

project = DSP ORDER BY updated DESC

project = MAX AND status = "In Progress"

---

## Security Notes

- TLS is required
- Jira credentials are read only from environment variables
- No credentials are logged
- Endpoints and JQL are sanitized
- Connection pooling limits concurrency

---

## Development

Linting:
uv run ruff check .

Type checking:
uv run mypy jira_mcp

Testing:
uv run pytest

---

## Roadmap

- OAuth 2.0 (3LO) support
- Rate-limit backoff handling
- Auto-pagination helpers
- Structured JSON logging
- Docker (uv-based) image

---

## License

MIT License

---

## Disclaimer

This project is not affiliated with Atlassian.
Jira is a trademark of Atlassian Pty Ltd.
