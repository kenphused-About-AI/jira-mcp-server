## The implementation plan for adding unit tests to sanitization.py:
1. Create a new file at tests/test_sanitization.py
2. Write tests for sanitize_jql() covering:
   - Valid inputs: Unicode text, long valid strings, JQL with quotes and ordering
   - Invalid inputs: Null bytes, backticks, empty strings
   - Test that function returns cleaned JQL for valid inputs and raises ValueError for invalid ones
3. Write tests for sanitize_endpoint() covering:
   - Valid inputs: Simple paths, alphanumeric endpoints
   - Invalid inputs: Path traversal attempts, special characters, leading slashes
   - Test that function returns cleaned endpoint for valid inputs and raises ValueError for invalid ones
4. Use pytest framework which is already in dependencies
5. Make tests synchronous since sanitization functions are pure Python
6. Run tests with uv run pytest tests/ to ensure they work

## Error Scenario Tests Implementation Plan:
1. Create mock integration tests in tests/test_jira_api_error_handling.py
2. Mock aiohttp responses using pytest-aiohttp
3. Test network timeout scenarios and verify RuntimeError with clean message
4. Test 401/403 responses and verify error messages don't leak credentials
5. Test invalid JSON responses and verify graceful handling
6. Use pytest.mark.asyncio for async tests
7. Run tests with uv run pytest tests/
