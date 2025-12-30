# Security Improvements - Issue #5: No input validation for issue keys

## Summary
Added comprehensive input validation for Jira issue keys across all tools that use them to prevent injection attacks and ensure proper formatting.

## Changes Made

### 1. New Validation Function (`src/jira_mcp_server/sanitization.py`)
- Added `validate_issue_key()` function that enforces the standard Jira issue key format: `^[A-Z][A-Z0-9]+-\\d+$`
- Validates: uppercase letters, numbers, hyphen, digits
- Rejects: lowercase letters, special characters, invalid formats
- Provides clear error messages for debugging

### 2. Updated Tools (`src/jira_mcp_server/tools.py`)
Added issue key validation to 6 tools:
- `get_jira_issue` (line 132)
- `get_jira_comments` (line 156)
- `get_jira_transitions` (line 180)
- `add_jira_comment` (line 274)
- `update_jira_issue` (line 311)
- `transition_jira_issue` (line 357)

### 3. Security Benefits
- **Prevents injection attacks**: Valid issue key format prevents malicious inputs
- **Fail-fast behavior**: Invalid keys are rejected immediately with clear errors
- **Consistent validation**: All tools now validate keys using the same function
- **Documentation**: Clear docstrings explain security implications

## Testing
- All 20 existing tests pass
- Code passes `ruff` linting
- Code passes `mypy` type checking
- No breaking changes to existing functionality

## Validation Pattern
Issue keys must match format: `^[A-Z][A-Z0-9]+-\\d+$`

Examples:
- ✅ Valid: `DSP-9050`, `PROJ-123`, `A1B2-456`
- ❌ Invalid: `dsp-9050` (lowercase), `DSP/9050` (slash), `DSP-9-0-50` (multiple hyphens)
