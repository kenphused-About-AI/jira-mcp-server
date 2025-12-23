# 2025-12-23: Jira Project Key Validation Updates

## Summary
This document records the validation changes made to project key sanitization in the Jira MCP server.

## Changes Made

### 1. Validation Rules Implementation
The `sanitize_project_key()` function in `jira_mcp/sanitization.py` has been updated to enforce the following rules:

- **Allowed characters**: uppercase letters (A-Z), digits (0-9), and underscores (_)
- **Length**: 2-10 characters
- **Start character**: Must start with an uppercase letter
- **Case normalization**: Input is normalized to uppercase

### 2. Implementation Details

#### Previous Implementation
```python
def sanitize_project_key(project_key: str) -> str:
    if not isinstance(project_key, str):
        raise ValueError("Project key must be a string")

    normalized_key = project_key.strip().upper()
    if not normalized_key:
        raise ValueError("Project key must be non-empty")

    if not re.fullmatch(r"[A-Z][A-Z0-9_]+", normalized_key):
        raise ValueError("Invalid project key format")

    return normalized_key
```

#### Updated Implementation
```python
def sanitize_project_key(project_key: str) -> str:
    if not isinstance(project_key, str):
        raise ValueError("Project key must be a string")

    normalized_key = project_key.strip().upper()
    if not normalized_key:
        raise ValueError("Project key must be non-empty")

    if not normalized_key[0].isalpha():
        raise ValueError("Project key must start with a letter")

    if not re.fullmatch(r"[A-Z][A-Z0-9_]{1,9}", normalized_key):
        raise ValueError("Invalid project key format")

    return normalized_key
```

### 3. Key Changes

1. **Explicit length validation**: Added explicit validation that the key is 2-10 characters using `{1,9}` to limit the character count after the first letter.

2. **Improved error handling**: Added explicit check for letter-starting requirement-formed before regex check for better error messages.

3. **Better constraint clarity**: The regex pattern now clearly enforces the 2-10 character constraint: `[A-Z]` (1 letter) + `[A-Z0-9_]{1,9}` (1-9 alphanumeric/underscore) = 2-10 total characters.

## Validation Examples

### Valid Project Keys
- `MAX` → `MAX`
- `PROJECT` → `PROJECT`  
- `ABC_123` → `ABC_123`
- `DSP` → `DSP`
- `TEST_1` → `TEST_1`

### Invalid Project Keys

| Input | Error Message | Reason |
|-------|----------------|--------|
| `A` | "Invalid project key format" | Too short (1 character) |
| `1ABC` | "Project key must start with a letter" | Starts with digit |
| `PROJECT!` | "Invalid project key format" | Contains invalid character |
| `` (empty) | "Project key must be non-empty" | Empty string |
| `VERYLONGKEYNAME` | "Invalid project key format" | Too long (14 characters) |

## Testing

All existing tests pass with the updated validation. The changes maintain backward compatibility with valid Jira project keys while enforcing stricter validation.

### Test Coverage
```bash
$ uv run pytest tests/test_sanitization.py -v
==================== 29 passed in 0.03s =====================
```

## Impact

- **Breaking Changes**: None - Only rejects invalid keys that would have failed in Jira anyway
- **Security**: Improved input validation prevents potentially malformed project keys
- **User Experience**: Clear error messages help users correct invalid inputs

## Related Files

- `jira_mcp/sanitization.py` - Main implementation
- `tests/test_sanitization.py` - Test suite (all passing)
