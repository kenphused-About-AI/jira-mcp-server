# Jira MCP Server

A secure Model Context Protocol (MCP) server for interacting with Jira Cloud. For encrypted transport, run it behind a TLS-terminating proxy.
This server exposes Jira functionality (search, issues, comments, transitions, projects) as MCP tools, enabling integration with agent frameworks such as Langflow, Goose, and OpenWebUI.

The project uses:
- FastMCP (HTTP/HTTPS MCP transport)
- aiohttp for async Jira API access
- uv for dependency and environment management
- HTTPS-capable transport (no stdio)

---

## Features

- HTTPS-capable MCP server (pair with a TLS-terminating proxy to enforce encryption; direct TLS on the server remains optional)
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
- uv (https://github.com/astral-sh/uv)

To ensure encrypted traffic, deploy behind a forwarding proxy such as Nginx, Cloudflare, Pangolin, or ContextForge that terminates TLS and forwards requests to the MCP server. Running the MCP server without TLS is supported when it is isolated behind a trusted TLS front end.

---

## Project Structure
```txt
jira-mcp-server/
├── AGENTS.md
├── docs
│   ├── 251223-JIRA-PROJECT-KEY-VALIDATION.md
│   ├── agents
│   │   ├── 251217-RECOMMENDATIONS.md
│   │   ├── 251217-TEST-TODO.md
│   │   ├── 251217-UNIT-TEST-DETAILS.md
│   │   ├── 251217-UPDATES.md
│   │   └── 251219-TOOL-IMPLEMENTATION.md
│   ├── SECURITY.md
│   └── SETUP-GUIDE.md
├── jira_mcp
│   ├── app.py
│   ├── config.py
│   ├── http_client.py
│   ├── __init__.py
│   ├── jira_api.py
│   ├── sanitization.py
│   ├── server.py
│   └── tools.py
├── main.py
├── pyproject.toml
├── README.md
├── tests
│   ├── conftest.py
│   ├── test_jira_api_error_handling.py
│   ├── test_sanitization.py
│   └── test_tools.py
└── uv.lock
```

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

IMPORTANT: JIRA_URL must use HTTPS. If you terminate TLS on this service, also set:

export MCP_TLS_CERT="cert.pem"
export MCP_TLS_KEY="key.pem"

Otherwise, configure TLS on your proxy. When TLS is handled by a forwarding proxy, you may run the MCP server over HTTP inside the trusted network segment it serves.

---

## TLS Certificates

If you terminate TLS on this service, you can generate a self-signed certificate for local development:

openssl req -x509 -newkey rsa:4096 \
  -keyout key.pem \
  -out cert.pem \
  -days 365 \
  -nodes

For production, use a trusted certificate such as Let’s Encrypt or terminate TLS on a forwarding proxy (Nginx, Cloudflare, Pangolin, or ContextForge) and forward HTTP to the MCP server.

---

## Running the Server

Using uv:

uv run jira-mcp-server

Or directly:

uv run python -m jira_mcp.app

The MCP server will start on:

https://<host>:<port> when TLS variables are set, or http://<host>:<port> when TLS is terminated by a forwarding proxy.

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

### Tool Parameters and Defaults

- **search_jira** – `{ jql: string, maxResults: 50, startAt: 0, fields: summary,status,assignee,priority,created,updated }`
- **list_jira_issues** – `{ project: string, maxResults: 50, startAt: 0, fields: summary,status,assignee,priority,created,updated }`
- **get_jira_issue** – `{ issueKey: string, fields: summary,status,assignee,priority,created,updated }`
- **get_jira_comments** – `{ issueKey: string, maxResults: 50, startAt: 0 }`
- **get_jira_transitions** – `{ issueKey: string }`
- **get_jira_projects** – `{ maxResults: 50, startAt: 0 }`
- **create_jira_issue** – `{ project: string, summary: string, description: "", issueType: "Task" }`
- **update_jira_issue** – `{ issueKey: string, fields: object }`
- **add_jira_comment** – `{ issueKey: string, body: string }`
- **transition_jira_issue** – `{ issueKey: string, transitionId: string }`

---

## Example JQL Queries

project = DSP ORDER BY updated DESC

project = MAX AND status = "In Progress"

---

## Security Notes

- Use TLS via a forwarding proxy (Nginx, Cloudflare, Pangolin, or ContextForge) or by configuring `MCP_TLS_CERT` and `MCP_TLS_KEY` on the service
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
