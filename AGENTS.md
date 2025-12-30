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
- Never log or store credentials
- Validate all external inputs
- Prepend `sanitize_` to validation functions
- Use HTTPS for all external calls
- Fail securely (prevent path traversal, script injection)

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
1. Define async handler in `tools.py`
2. Add to `TOOLS` dictionary
3. Add schema to `TOOL_SCHEMAS` list
4. Write tests covering:
   - Valid inputs
   - Invalid inputs (error cases)
   - Edge cases (empty, max length, special chars)

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
