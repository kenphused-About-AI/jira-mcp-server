# AGENTS.md

## Build/Lint/Test Commands
- Lint: `uv run ruff check .`
- Type check: `uv run mypy jira_mcp`
- Test: `uv run pytest`

## Code Style Guidelines
- **Imports**: Standard library first, then third-party, then local
- **Formatting**: Follow Ruff and mypy rules
- **Types**: Use type hints, no type ignores for public APIs
- **Naming**: snake_case for functions/variables, DescriptiveCamelCase for classes
- **Error Handling**: Raise ValueError for invalid inputs, sanitize all user inputs
- **Security**: No credentials in code/logs, strict input validation

## Repository Conventions
- No logic in `__init__.py`
- async/await for I/O operations
- Environment variables for configuration
- HTTPS-only for external calls

## Agent Working Document Location
All development markdown files are stored in the `docs/agents` directory. Future agent working documents will be created and maintained in this location.
