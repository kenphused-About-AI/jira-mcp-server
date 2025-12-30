# Jira MCP Server (Python)

A Model Context Protocol (MCP) server that provides Jira integration. This server allows AI assistants to interact with Jira issues, search, create, update, and manage Jira workflows.

## Features

- **Search Issues**: Search Jira issues using JQL (Jira Query Language)
- **List Issues**: List issues from specific Jira projects
- **Get Issue Details**: Retrieve detailed information about specific issues
- **Get Comments**: Fetch all comments from an issue
- **Get Transitions**: View available status transitions for an issue
- **List Projects**: Get all accessible Jira projects
- **Create Issues**: Create new Jira issues
- **Add Comments**: Add comments to existing issues
- **Update Issues**: Update issue fields (summary, description, etc.)
- **Transition Issues**: Move issues through workflow states

## Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- A Jira account with API access
- Jira API token (generate from your Jira account settings)

## Installation

### Install uv (if not already installed)

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install the Server

1. Clone or download this repository
2. Navigate to the project directory:
   ```bash
   cd jira-mcp-server
   ```

3. Install dependencies using uv:
   ```bash
   uv sync
   ```

4. For development with testing tools:
   ```bash
   uv sync --dev
   ```

## Configuration

### Environment Variables

You need to set the following environment variables:

- `JIRA_URL`: Your Jira instance URL (e.g., `https://yourcompany.atlassian.net`)
- `JIRA_USERNAME`: Your Jira email address
- `JIRA_API_TOKEN`: Your Jira API token

### Getting Your Jira API Token

1. Log in to your Jira account
2. Go to Account Settings → Security → API tokens
3. Click "Create API token"
4. Give it a name and copy the generated token

### Setting Up in Bob IDE

Add the server to your Bob IDE MCP settings file (`~/.config/Bob-IDE/User/globalStorage/ibm.bob-code/settings/mcp_settings.json`):

```json
{
  "mcpServers": {
    "jira-mcp-server": {
      "command": "uvx",
      "args": ["--from", "/path/to/jira-mcp-server", "jira-mcp-server"],
      "env": {
        "JIRA_URL": "https://yourcompany.atlassian.net",
        "JIRA_USERNAME": "your.email@company.com",
        "JIRA_API_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

### Setting Up in Claude Desktop

Add to your Claude Desktop config file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "jira-mcp-server": {
      "command": "uvx",
      "args": ["--from", "/path/to/jira-mcp-server", "jira-mcp-server"],
      "env": {
        "JIRA_URL": "https://yourcompany.atlassian.net",
        "JIRA_USERNAME": "your.email@company.com",
        "JIRA_API_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

## Running the Server

### Using uvx (recommended)

```bash
# Set environment variables
export JIRA_URL="https://yourcompany.atlassian.net"
export JIRA_USERNAME="your.email@company.com"
export JIRA_API_TOKEN="your-api-token-here"

# Run the server
uvx --from . jira-mcp-server
```

### Using uv run

```bash
uv run jira-mcp-server
```

## Usage Examples

Once configured, you can use natural language to interact with Jira:

### Search for Issues
```
"Find all open issues assigned to me"
"Search for bugs in project DSP with high priority"
```

### Get Issue Details
```
"Show me details for issue DSP-21630"
"What's the status of SUPPORT-660?"
```

### Create Issues
```
"Create a new bug in project DSP with title 'Login page not loading'"
```

### Update Issues
```
"Update DSP-21630 summary to 'New feature implementation'"
"Add a comment to SUPPORT-660 saying 'Working on this now'"
```

## Available Tools

### search_jira
Search Jira issues using JQL.

**Parameters:**
- `jql` (required): JQL query string
- `maxResults` (optional): Maximum results to return (default: 50)
- `startAt` (optional): Starting index for pagination (default: 0)

### list_jira_issues
List issues from a specific project.

**Parameters:**
- `projectKey` (required): Project key (e.g., 'DSP', 'PROJ')
- `maxResults` (optional): Maximum results to return (default: 50)

### get_jira_issue
Get detailed information about a specific issue.

**Parameters:**
- `issueKey` (required): Issue key (e.g., 'DSP-9050')

### get_jira_comments
Get all comments from a specific issue.

**Parameters:**
- `issueKey` (required): Issue key

### get_jira_transitions
Get available status transitions for an issue.

**Parameters:**
- `issueKey` (required): Issue key

### get_jira_projects
List all accessible Jira projects.

**Parameters:** None

### create_jira_issue
Create a new Jira issue.

**Parameters:**
- `projectKey` (required): Project key
- `summary` (required): Issue summary/title
- `issueType` (required): Issue type (e.g., 'Task', 'Bug', 'Story')
- `description` (optional): Issue description

### add_jira_comment
Add a comment to an issue.

**Parameters:**
- `issueKey` (required): Issue key
- `comment` (required): Comment text

### update_jira_issue
Update fields of an existing issue.

**Parameters:**
- `issueKey` (required): Issue key
- `summary` (optional): New summary/title
- `description` (optional): New description

### transition_jira_issue
Transition an issue to a new status.

**Parameters:**
- `issueKey` (required): Issue key
- `transitionId` (required): Transition ID (get from get_jira_transitions)

## Development

### Project Structure
```
jira-mcp-server/
├── src/
│   └── jira_mcp_server/
│       ├── __init__.py          # Server initialization
│       ├── __main__.py          # CLI entry point
│       ├── config.py           # Configuration loading
│       ├── http_client.py      # Async HTTP client
│       ├── jira_api.py         # Jira API wrapper
│       ├── server.py           # FastMCP server
│       ├── tools.py            # Tool handlers
│       └── sanitization.py     # Input validation
├── tests/
│   └── test_jira_mcp_server.py  # Unit tests
├── pyproject.toml           # Project config
└── README.md               # Documentation
```

### Installing in Development Mode

```bash
uv sync --dev
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage report
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_jira_curl_server.py

# Run with verbose output
uv run pytest -v
```

### Code Quality Tools

```bash
# Type checking with mypy
uv run mypy src/

# Linting with ruff
uv run ruff check src/

# Format code with ruff
uv run ruff format src/
```

## Troubleshooting

### Authentication Errors
- Verify your `JIRA_URL`, `JIRA_USERNAME`, and `JIRA_API_TOKEN` are correct
- Ensure your API token hasn't expired
- Check that your Jira account has appropriate permissions

### Connection Issues
- Verify your Jira instance URL is accessible (must use HTTPS)
- Check if your network allows connections to Jira
- Check firewall settings if connection timeouts occur

### Import Errors
- Make sure you've run `uv sync` to install dependencies
- Verify you're using Python 3.10 or higher

### API Version Issues
- This server uses Jira REST API v3
- If you encounter API deprecation warnings, the server may need updates

## Security Best Practices

### Input Validation

All MCP tool arguments are validated and sanitized before use:

- ✅ **JQL Sanitization**: Jira Query Language input is validated to prevent injection attacks via `sanitize_jql()` function
- ✅ **Project Key Validation**: All project keys are validated using `sanitize_project_key()`
- ✅ **Issue Key Validation**: Issue identifiers are validated using `sanitize_issue_key()` to ensure proper format
- ✅ **Endpoint Sanitization**: API endpoints are sanitized to prevent path traversal attacks
- ✅ **Content Sanitization**: All content passed to APIs is validated

### Credential Management

- **Never commit credentials**: Never commit `.env`, `credentials.json`, or any file containing API tokens to version control
- **Use environment variables**: Store sensitive data in environment variables, not in code
- **Rotate tokens regularly**: Regularly rotate your Jira API tokens (recommended: every 30-90 days)
- **Limit permissions**: Use Jira API tokens with minimal required permissions
- **Use secrets manager**: For production deployments, use a secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.)

### Runtime Security

- **HTTPS enforcement**: The server enforces HTTPS for all requests (validation in `config.py`)
- **No credential logging**: Credentials are never logged (URL sanitization removes any embedded credentials)
- **Timeout protection**: All HTTP requests include a 30-second timeout to prevent hanging
- **Connection pooling**: HTTPClient with connection pooling for secure and efficient requests
- **Async operations**: Properly managed async operations to prevent resource exhaustion

### Developer Security

- **Development environment**: Create a `.env` file for local development with a dedicated test token
- **Pre-commit hooks**: Verify no credentials are committed using hooks
- **Dependency management**: Use `uv sync` to manage dependencies with proper Pinning
- **Code review**: All changes reviewed for security implications before merge

### Security Features

The server implements:

- **Comprehensive input validation** across all API endpoints
- **Automatic credential sanitization** for logging
- **HTTPS enforcement** for all Jira server communications
- **Request timeout protection** preventing denial of service
- **Connection pooling** with secure defaults
- **Proper error handling** that doesn't leak sensitive information

**For production deployments**, we recommend:
- Using dedicated Jira service accounts with minimal permissions
- Implementing network-level security (firewalls, VPNs)
- Monitoring for unusual API usage patterns
- Regularly audit access logs

## Recent Improvements

## Comparison with Node.js Version

This Python implementation provides the same functionality as the Node.js/TypeScript version but with:
- Modern Python async/await patterns with aiohttp
- HTTP connection pooling for better performance
- Type hints for better IDE support and type safety
- `uv` for fast, reliable dependency management
- `uvx` for easy execution without installation
- Comprehensive test coverage with pytest
- Proper ADF format support for Jira API v3
- Enhanced security with input sanitization

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Support

For issues or questions:
- Create an issue in the repository
- Contact the maintainer

