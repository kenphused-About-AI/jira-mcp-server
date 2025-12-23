# Plan: Implement Missing Jira MCP Tools

## Objectives
- Add the nine Jira MCP tools advertised in the README but not yet implemented.
- Keep tooling consistent with existing patterns: async handlers, sanitized inputs, and centralized HTTP access via `jira_mcp.jira_api.jira_request`.
- Ensure each tool is documented in schemas and validated through automated tests.
- Document expectations clearly so the work is unblockable for future contributors and traceable against README promises.

## Guiding Principles
- **Security & Validation:** Reuse `sanitize_jql` for JQL inputs and extend sanitization with helper validators for issue keys, project keys, comment bodies, and transition IDs. Reject empty or malformed inputs with `ValueError`.
- **HTTP Layer:** Use `jira_request` for all Jira REST calls. Favor explicit endpoints (e.g., `issue/{key}`, `issue/{key}/comment`) and keep methods clear (`GET`, `POST`, `PUT`).
- **Consistency:** Mirror existing `search_jira` structure: handler functions plus `Tool` schemas registered in `TOOLS` and `TOOL_SCHEMAS`.
- **Tests:** Add coverage for tool input validation, schema defaults, and HTTP invocation shapes using mocks to avoid live Jira calls.

## Definition of Done
- All nine tools are exposed through `TOOLS` and `TOOL_SCHEMAS` with JSON schema defaults that match README defaults.
- Validators for JQL, issue keys, project keys, transition IDs, and comment bodies are unit-tested and imported where handlers need them.
- README and `docs/SETUP-GUIDE.md` list the new tools with parameters, defaults, and usage notes.
- Automated checks remain green: `uv run ruff check .`, `uv run mypy jira_mcp`, and `uv run pytest`.

## Implementation Steps
1. **Input Validation Helpers**
   - Add small validators in `jira_mcp.sanitization` (e.g., `sanitize_issue_key`, `sanitize_project_key`, `sanitize_comment_body`, `sanitize_transition_id`).
   - Write unit tests to cover happy paths and rejection of dangerous characters, empty strings, and traversal attempts.

2. **Tool Handlers in `jira_mcp/tools.py`**
   - General refactor: keep `STANDARD_FIELDS` reusable; consider adding helper for field string assembly.
   - Implement async handlers using `jira_request`:
     - `list_jira_issues`: GET `search` with `project` filter, pagination, and optional `fields`.
     - `get_jira_issue`: GET `issue/{issueKey}` with basic fields.
     - `get_jira_comments`: GET `issue/{issueKey}/comment` with pagination controls.
     - `get_jira_transitions`: GET `issue/{issueKey}/transitions`.
     - `get_jira_projects`: GET `project/search` with pagination.
     - `create_jira_issue`: POST `issue` with `fields` including project key, summary, description, and issue type.
     - `update_jira_issue`: PUT `issue/{issueKey}` with provided `fields` payload.
     - `add_jira_comment`: POST `issue/{issueKey}/comment` with sanitized body.
     - `transition_jira_issue`: POST `issue/{issueKey}/transitions` with transition ID.
   - Validate inputs inside each handler before calling Jira.
   - Ensure defaults (e.g., `maxResults`, `startAt`) match README expectations and existing `search_jira` behavior.
   - Keep responses consistently shaped (e.g., returning raw Jira payloads) to align with `search_jira` and simplify clients.

3. **Tool Schemas in `jira_mcp/tools.py`**
   - Add `Tool` entries for each handler with descriptive names and JSON schemas that enforce required fields, types, and defaults.
   - Register handlers in `TOOLS` mapping so `server.py` can dispatch them.

4. **Documentation Alignment**
   - Update README (and `docs/SETUP-GUIDE.md` if necessary) to reflect input parameters and validation notes for each tool.
   - Provide brief examples for common actions (search, create issue, transition, comment).

5. **Testing Strategy**
   - Unit tests for new sanitization helpers (`tests/test_sanitization.py`).
   - Tool handler tests using `pytest` and `unittest.mock` to assert calls to `jira_request` with expected endpoints/methods/params and to validate error handling on bad inputs.
   - Smoke test for `list_tools` to ensure all schemas are exposed.

6. **Follow-up Housekeeping**
   - Consider adding lightweight data classes or typed dicts for request bodies to improve mypy coverage.
   - Ensure `uv run ruff check .`, `uv run mypy jira_mcp`, and `uv run pytest` remain green after changes.
