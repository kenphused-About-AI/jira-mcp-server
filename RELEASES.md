# Releases

## [0.3.0-beta]

### Features
- Added comprehensive input validation for all MCP tool arguments
- Implemented JQL sanitization to prevent command injection attacks
- Added project key validation with regex patterns
- Created ADF (Atlassian Document Format) conversion for rich text
- Added transition ID validation before API calls
- Implemented field value sanitization for issue updates
- Added endpoint validation with regex patterns
- Created secure logging function to handle BrokenPipeError

### Bug Fixes
- Fixed duplicate entry point issue causing 'coroutine was never awaited' warning
- Resolved HTTP session cleanup on server shutdown
- Fixed import order in test files to comply with linter rules
- Updated README with correct environment variable names
- Fixed security documentation to match implementation

### Security Improvements
- Input validation for all tool arguments
- JQL sanitization preventing backtick injection
- Credential handling improvements
- Secure logging without credential leakage
- Endpoint validation with strict regex patterns

### Documentation
- Created comprehensive AGENTS.md with development guidelines
- Added SECURITY_PERFORMANCE_REVIEW.md with security analysis
- Created SECURITY_IMPROVEMENTS.md detailing all security measures
- Updated README with installation and usage instructions

### Testing
- Added full test coverage for sanitization functions
- Created validation tests for all input types
- Added security test cases for injection attempts
- Updated test conventions in AGENTS.md

This release represents the 0.3.0-beta branch, focusing on security and input validation improvements while maintaining backward compatibility with existing MCP tool implementations.
