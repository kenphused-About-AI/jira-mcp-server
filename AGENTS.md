# AGENTS.md

## Build/Lint/Test Commands

### Linting
- Check code style: `uv run ruff check .`
- Auto-fix violations: `uv run ruff check . --fix`

### Type Checking
- Full type check: `uv run mypy jira_mcp`

### Testing
- Run all tests: `uv run pytest`
- Run specific test file: `uv run pytest tests/test_sanitization.py`
- Run specific test function: `uv run pytest tests/test_sanitization.py::TestSanitizeJQL::test_valid_unicode_jql -v`
- Run tests with coverage: `uv run pytest --cov=jira_mcp --cov-report=term-missing`

### Pre-commit
- Lint and type check: `uv run ruff check . && uv run mypy jira_mcp`

## Installation and Usage

### Package Installation
- Install in development mode: `pip install -e .`
- Install globally: `pip install .`

### Running the Server
- Run via package entry point: `jira-mcp-server`
- Run directly: `uv run python src/jira_mcp_server/__main__.py`

### Environment Variables
Provide `.env.example` with defaults including:
- `JIRA_BASE_URL`: URL to your Jira instance
- `JIRA_API_TOKEN`: API token for authentication
- `JIRA_USERNAME`: Username for basic auth
- `JIRA_PROJECT_KEY`: Default project key

Example `.env.example` content:
```
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_API_TOKEN=your-api-token-here
JIRA_USERNAME=email@example.com
JIRA_PROJECT_KEY=PROJ
```

### FastMCP Usage
The server implements 8 MCP tools:
- `search_jira`: Search issues using JQL
- `create_jira_issue`: Validates project keys and converts text to ADF safely
- `update_jira_issue`: Sanitizes field updates and validates required parameters
- `transition_jira_issue`: Validates transition IDs before sending to API
- All other tools validate keys and identifiers before making API calls

## Code Style Guidelines

### Import Order
1. Standard library imports
2. Third-party imports
3. Local application imports

Example:
```python
import json
from mcp.server.fastmcp import FastMCP
from jira_mcp.tools import TOOLS
```

### Formatting
- Line length: 88 characters (Ruff default)
- No trailing whitespace
- Use double quotes for strings
- Black-compatible formatting (handled by Ruff)

### Type Hints
- Use type hints for all functions and methods
- Prefer `dict | None` over `Optional[dict]`
- No type ignores for public APIs
- Use TYPE_CHECKING for complex type imports

Example:
```python
def sanitize_endpoint(endpoint: str) -> str:
    if not re.fullmatch(r"[a-zA-Z0-9/_-]+", endpoint):
        raise ValueError("Invalid endpoint")
    return endpoint
```

### Naming Conventions
- Functions and variables: `snake_case`
- Classes and type aliases: `DescriptiveCamelCase`
- Constants: `UPPER_SNAKE_CASE`
- Test classes: `DescriptiveTestCase` (e.g., `TestSanitizeJQL`)
- Test methods: `test_what_behavior_under_condition`

### Error Handling
- Raise `ValueError` for invalid user inputs
- Raise `RuntimeError` for external system errors
- Never raise generic `Exception`
- Sanitize all inputs before processing
- Validate inputs before making API calls

Example:
```python
def sanitize_jql(jql: str) -> str:
    if not isinstance(jql, str) or not jql.strip():
        raise ValueError("JQL must be non-empty")
    forbidden = ["`", "\x00", "|", "&"]
    if any(c in jql for c in forbidden):
        raise ValueError("Invalid character in JQL")
    return jql.strip()
```

### Security
### MCP Tool Security
- Input validation: All MCP tool arguments must be validated and sanitized before use
- Never trust client-provided data
- Document security implications for each tool
- Handle error conditions gracefully without leaking stack traces or sensitive data
- Log tool invocations with sanitized arguments only

FastMCP implements 8 tools with strict input validation:
- `search_jira`: Validates JQL syntax and prevents injection via `sanitize_jql()`
- `create_jira_issue`: Validates project keys and converts text to ADF safely
- `update_jira_issue`: Sanitizes field updates and validates required parameters
- `transition_jira_issue`: Validates transition IDs before sending to API
- All other tools validate keys and identifiers before making API calls

Example security check pattern:
```python
# Always validate arguments at the start of tool handlers
def _validate_required_args(arguments: dict[Any], *required_fields: str) -> None:
    """Validate that all required fields are present in arguments."""
    missing = [field for field in required_fields if field not in arguments]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

async def _handle_create_jira_issue(arguments: dict[str, Any]) -> Any:
    """Handle create_jira_issue with full validation."""
    # Validate required fields first
    _validate_required_args(arguments, "projectKey", "summary", "issueType")
    
    # Sanitize inputs
    project_key = sanitize_project_key(arguments["projectKey"])
    summary = sanitize_text(arguments["summary"])
    
    # ... rest of implementation
```

Example:
```python
async def _handle_search_jira(arguments: dict[str, Any]) -> Any:
    """Handle search_jira tool with input sanitization."""
    # Sanitize inputs before processing
    jql = sanitize_jql(arguments["jql"])
    max_results = max(1, min(100, arguments.get("maxResults", 50)))
    
    # Execute Jira search
    return await execute_curl(
        "search/jql",
        query_params={
            "jql": jql,
            "maxResults": max_results,
        },
    )
```

### Logging
- Configure logging in `app.py` with INFO level (stdout)
- Use `logger = logging.getLogger(__name__)` in each module
- Log levels:
  - INFO: User actions, API calls, tool invocations
  - DEBUG: Detailed request/response data, internal state
  - WARNING: Unexpected conditions, failed validations
  - ERROR: Failed API requests, runtime errors
- Never log credentials or sensitive data
- log to STDOUT as default
  - when running the mcp server from the command line, logging output should be seen in the terminal.

Example:
```python
import logging
from .sanitization import sanitize_endpoint

logger = logging.getLogger(__name__)

async def jira_request(endpoint: str, *):
    endpoint = sanitize_endpoint(endpoint)
    logger.info(f"Making GET request to {endpoint}")
    # ... API call ...
    logger.info("Request completed successfully")
```

## Repository Conventions

### Project Structure
```
jira_mcp/
    __init__.py          # No logic, only imports
    app.py               # Entry point
    server.py            # MCP server
    jira_api.py          # API client
    http_client.py       # HTTP session
    tools.py             # MCP tools
    sanitization.py      # Input validation
    config.py            # Config loading

    └── tests/
        conftest.py       # Test fixtures
        test_*.py         # Unit tests
```

### No Logic in `__init__.py`
- `__init__.py` files should contain only imports
- No logic or initialization code
- Keep package imports minimal

### Configuration
- Use environment variables for all configuration
- Provide `.env.example` with defaults
- Validate environment variables at startup

### Tool Implementation
1. Define async handler in `tools.py` (prefix with `_handle_`)
2. Add to `TOOL_HANDLERS` dictionary with handler name as key
3. Ensure proper configuration in `__main__.py` entry point
4. Write tests covering:
   - Valid inputs
   - Invalid inputs (error cases)
   - Edge cases (empty, max length, special chars)
   
Example:
```python
async def _handle_search_jira(arguments: dict[str, Any]) -> Any:
    """Handle search_jira tool."""
    jql = sanitize_jql(arguments["jql"])
    max_results = arguments.get("maxResults", 50)
    start_at = arguments.get("startAt", 0)
    return await execute_curl(
        "search/jql",
        query_params={
            "jql": jql,
            "maxResults": max_results,
            "startAt": start_at,
            "fields": STANDARD_ISSUE_FIELDS,
        },
    )

TOOL_HANDLERS: dict[str, Any] = {
    "search_jira": _handle_search_jira,
    "list_jira_issues": _handle_list_jira_issues,
    # ... other tools
}
```

All handlers should:
- Validate all inputs at start via `_validate_required_args()`
- Sanitize inputs using `sanitize_*` functions
- Log tool invocations with sanitized arguments
- Handle errors gracefully without exposing sensitive details

### Test Organization
- One test class per feature
- Test class name: `TestFeatureName`
- Test method: `test_behavior_under_conditions`
- Use pytest parametrize for similar test cases

Example:
```python
class TestSanitizeJQL:
    """Test JQL (Jira Query Language) sanitization."""

    def test_valid_unicode_jql(self):
        """Unicode characters in JQL should be allowed."""
        jql = 'project = TEST AND summary ~ "café"'
        assert sanitize_jql(jql) == jql.strip()
```

### Documentation
- Keep inline comments minimal
- Use docstrings for public functions
- Document edge cases and security considerations
- Update AGENTS.md when adding new tools or commands

## Agent-Specific Instructions

### When Adding New Tools
1. Verify no overlapping functionality
2. Check for security implications
3. Add comprehensive tests
4. Document in README.md and AGENTS.md

### When Making Security Changes
1. Update sanitization rules
2. Add regression tests
3. Validate against injection attacks
4. Review error messages for info leakage

### When Adding Configuration
1. Add environment variable
2. Add validation
3. Document in README.md
4. Provide reasonable defaults

## Cursors Rules / Copilot Instructions

None found in repository. Review `.cursor/rules/` or `.github/copilot-instructions.md` when they exist.

## Linter and Type Check Rules

### Ruff Configuration
- Enabled by: `ruff check .`
- Rules: Standard Ruff + project-specific
- Auto-fix: `ruff check . --fix`

### MyPy Configuration
- Strict mode enabled
- No type ignores for public APIs
- Follows PEP 484 conventions
- Check with: `uv run mypy jira_mcp`

## Git Best Practices

### Branching Strategy
- Use feature branches for all changes (not main/master)
- Branch names: `feature/name`, `fix/name`, `docs/name`, `test/name`
- Prefix with `WIP-` for work-in-progress branches

### Commit Messages
- Separate subject and body with blank line
- Subject: 50 chars max, imperative mood (add, fix, update)
- Body: explain why, not what (72 chars per line)
- Reference issues with "Fixes #123" or "Closes #456"

Examples:
```
Add JQL sanitization for backticks

Prevent command injection through JQL parameters
by rejecting backticks and null bytes.
Related to SEC-42

Fix Jira request error handling

Return proper error messages for 400+ responses
instead of crashing.
Fixes #213
```

### Workflow
- Commit early, commit often
- Small, focused commits (one logical change each)
- Rebase feature branches on main before PR
- Avoid force-pushing to shared branches
- Squash merge feature branches into main

### Rebasing vs Merging
- Rebase: use for local branch cleanup
- Merge: use when working with others (creates merge commits)
- Never rebase public history (shared branches)

### Pre-commit Hooks
- hooks/lint: runs `ruff check`
- hooks/typecheck: runs `mypy`
- hooks/test: runs `pytest`

## Agent Working Document Location
All development markdown files are stored in the `docs/agents` directory. Future agent working documents will be created and maintained in this location.
