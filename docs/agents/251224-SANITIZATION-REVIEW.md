# Sanitization module review and improvement suggestions

## Summary
The current `jira_mcp/sanitization.py` covers major inputs but can be hardened and made more consistent. Suggested improvements below are grouped by function.

## Recommendations

### `sanitize_endpoint`
- Normalize the endpoint before validation (e.g., collapse duplicate slashes) and reject trailing slashes that could bypass path checks. This avoids variants like `issue//123` that currently pass the regex.
- Enforce a length cap to avoid excessively long path components used for denial-of-service attempts.
- Consider accepting only known top-level segments (e.g., `issue`, `search`, `project`) to reduce the attack surface if the set of endpoints is finite. 【F:jira_mcp/sanitization.py†L15-L39】

### `sanitize_jql`
- Replace the small forbidden-character list with an allowlist-oriented regex that also blocks control characters, semicolons, and multi-line input. Right now newline and carriage-return sequences are accepted and could alter downstream parsing. 【F:jira_mcp/sanitization.py†L42-L75】
- Add structural validation such as balanced quotes/parentheses and maximum length to guard against resource-exhaustion queries.
- Normalize whitespace (e.g., collapse multiple spaces) to make queries easier to compare and log safely.

### `sanitize_issue_key` and `sanitize_project_key`
- Enforce maximum lengths for issue and project keys (e.g., project keys are typically ≤10 characters, issue keys ≤255), and surface clearer error messages that include the expected format. 【F:jira_mcp/sanitization.py†L78-L152】
- Allow configuration of accepted project prefixes or patterns so the sanitizer can align with instance-specific naming policies.
- Consider returning structured data (project key + numeric ID) to avoid repeated parsing elsewhere and reduce the risk of inconsistent handling.

### `sanitize_comment_body`
- Strip or encode control characters beyond null bytes (e.g., other C0 controls, bidirectional markers) to avoid log-forgery or UI confusion. 【F:jira_mcp/sanitization.py†L155-L192】
- Apply a length cap and optional HTML/Markdown escaping if the body is later rendered, ensuring UI safety as well as API safety.
- Normalize newline style (e.g., convert CRLF to `\n`) so downstream systems receive consistent content.

### `sanitize_transition_id`
- Convert the numeric string to an integer and back (or store as `int`) to ensure canonical formatting and to reject leading-zero variants that might be ambiguous. 【F:jira_mcp/sanitization.py†L195-L228】
- Add explicit bounds (e.g., positive, reasonable upper limit) to prevent out-of-range IDs from reaching Jira APIs.

### Cross-cutting improvements
- Centralize the forbidden/allowed character sets and length limits in constants to keep validation consistent across sanitizers.
- Add unit tests for edge cases noted above (duplicate slashes, control characters, multi-line JQL) to ensure regressions are caught early.
