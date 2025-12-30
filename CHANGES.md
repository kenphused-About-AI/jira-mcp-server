# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2025-12-11

### 🚀 Performance Improvements
- **BREAKING**: Replaced curl subprocess with aiohttp for true async HTTP requests
- Added HTTP connection pooling (10 concurrent connections, 5 per host)
- Implemented DNS caching (5-minute TTL) for faster lookups
- 3-5x performance improvement for concurrent requests
- Reduced memory overhead by eliminating subprocess spawning

### 🔒 Security Enhancements
- **CRITICAL FIX**: Credentials no longer exposed in process arguments
- Added input sanitization to prevent command injection attacks
- Implemented endpoint validation with regex patterns
- Added HTTPS enforcement for JIRA_URL
- Sanitized logging to prevent credential leakage
- Added 30-second request timeout to prevent DoS attacks

### ✨ New Features
- Automatic HTTP session management with connection pooling
- Graceful session cleanup on server shutdown
- Enhanced error messages with better context
- Support for async/await patterns throughout

### 🧪 Testing
- Updated all tests for aiohttp implementation
- Added security tests for input sanitization
- Added endpoint validation tests
- All 20 tests passing with 71% code coverage

### 📚 Documentation
- Updated README with security notes
- Added performance benchmarks
- Updated prerequisites (removed curl requirement)
- Enhanced troubleshooting section

### 🔧 Technical Details
- Added dependencies: aiohttp>=3.9.0
- Removed dependency on curl command-line tool
- Updated function names: `execute_curl` → `execute_request` (with backward compatibility alias)
- Added `get_http_session()` and `close_http_session()` functions

## [0.2.0] - 2024-XX-XX

### Added
- Fixed Jira API v3 compatibility with ADF format
- Added comprehensive error handling with HTTP status codes
- Implemented input validation with TypedDict
- Added structured logging throughout
- Created full unit test suite
- Added code quality tools (mypy, ruff)
- Improved documentation

## [0.1.0] - 2024-XX-XX

### Added
- Initial Python port from Node.js/TypeScript
- Support for Jira REST API v3
- Basic CRUD operations for issues
- JQL search support
- Comment management
- Workflow transitions