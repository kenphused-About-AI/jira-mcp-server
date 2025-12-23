# 251223-REMOVE-TLS

## Objective
Remove TLS enforcement from the Jira MCP Server to make encryption optional, allowing servers to run without TLS when behind a trusted proxy.

## Current TLS Implementation

### Files containing TLS code
- `jira_mcp/app.py` (lines 1-3, 5-8, 12)
  - Creates SSL context
  - Loads certificate chain
  - Passes SSL context to MCP server
  
- `jira_mcp/config.py` (lines 10-11)
  - Defines `TLS_CERT` and `TLS_KEY` environment variables
  - Defaults to certificate files (cert.pem, key.pem)

### Current TLS behavior
1. Server always creates SSL context with client auth
2. Loads certificate chain from environment or default files
3. Passes SSL context to MCP server (line 12 in app.py)
4. According to README, TLS is optional but currently enforced in code

## Implementation Plan

### Changes to `jira_mcp/app.py`
1. Remove TLS import (line 1)
2. Remove TLS_CERT and TLS_KEY imports (line 3)
3. Remove SSL context creation and loading (lines 5-8)
4. Remove ssl_context parameter from mcp.run() (line 12)

### Changes to `jira_mcp/config.py`
1. Remove TLS_CERT constant definition (line 10)
2. Remove TLS_KEY constant definition (line 11)

### Documentation changes
1. Update `app.py` docstring if it mentions TLS
2. Consider updating README to reflect that TLS is now truly optional

## Expected Results
- Server no longer requires TLS certificates
- MCP server runs without SSL context
- Transport security can be handled by frontend proxy
- Backward compatibility maintained for those not using TLS

## Testing Strategy
1. Verify server starts without TLS configuration
2. Check that MCP tools work over plain HTTP
3. Confirm no dependency on cert.pem or key.pem files
4. Run linting: `uv run ruff check .`
5. Run type checking: `uv run mypy jira_mcp`
6. Run tests: `uv run pytest`