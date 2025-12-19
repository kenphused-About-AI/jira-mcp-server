"""Unit tests for sanitization functions."""

import pytest
from jira_mcp.sanitization import sanitize_jql, sanitize_endpoint


class TestSanitizeJQL:
    """Test JQL (Jira Query Language) sanitization."""

    def test_valid_unicode_jql(self):
        """Unicode characters in JQL should be allowed."""
        jql = 'project = TEST AND summary ~ "café"'
        result = sanitize_jql(jql)
        assert result == jql.strip()

    def test_valid_long_jql(self):
        """Long JQL strings should be accepted."""
        long_jql = "A" * 1000
        result = sanitize_jql(long_jql)
        assert result == long_jql.strip()

    def test_valid_jql_with_quotes_and_ordering(self):
        """Complex JQL with quotes and ordering should pass."""
        jql = 'project = PROJ AND status = "Open" ORDER BY created DESC'
        result = sanitize_jql(jql)
        assert result == jql.strip()

    def test_invalid_null_byte(self):
        """Null bytes should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid character in JQL"):
            sanitize_jql("project = TEST\x00")

    def test_invalid_backtick(self):
        """Backticks should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid character in JQL"):
            sanitize_jql("project = TEST`")

    def test_invalid_pipe_character(self):
        """Pipe characters should raise ValueError."""
        with pytest.raises(ValueError, match=r"Invalid character in JQL\."):
            sanitize_jql("project = TEST | status = Open")

    def test_invalid_ampersand_character(self):
        """Ampersands should raise ValueError."""
        with pytest.raises(ValueError, match=r"Invalid character in JQL\."):
            sanitize_jql("project = TEST & status = Open")

    def test_invalid_empty_string(self):
        """Empty string should raise ValueError."""
        with pytest.raises(ValueError, match="JQL must be non-empty"):
            sanitize_jql("")

    def test_trim_whitespace(self):
        """JQL should be trimmed."""
        jql = "  project = TEST  "
        result = sanitize_jql(jql)
        assert result == "project = TEST"


class TestSanitizeEndpoint:
    """Test endpoint path sanitization."""

    def test_valid_issue_endpoint(self):
        """Issue endpoints should be allowed."""
        endpoint = "issue/ABC-123"
        result = sanitize_endpoint(endpoint)
        assert result == endpoint

    def test_valid_search_endpoint(self):
        """Search endpoints should be allowed."""
        endpoint = "search"
        result = sanitize_endpoint(endpoint)
        assert result == endpoint

    def test_valid_project_endpoint(self):
        """Project endpoints should be allowed."""
        endpoint = "project"
        result = sanitize_endpoint(endpoint)
        assert result == endpoint

    def test_valid_path_with_hyphens_and_underscores(self):
        """Paths with hyphens and underscores should be allowed."""
        endpoint = "my-project_v2"
        result = sanitize_endpoint(endpoint)
        assert result == endpoint

    def test_invalid_path_traversal(self):
        """Path traversal attempts should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid endpoint"):
            sanitize_endpoint("../issue/ABC-123")

    def test_invalid_leading_slash(self):
        """Leading slashes should raise ValueError."""
        with pytest.raises(ValueError, match="Path traversal detected"):
            sanitize_endpoint("/issue/ABC-123")

    def test_invalid_special_characters(self):
        """Special characters should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid endpoint"):
            sanitize_endpoint("issue/ABC-123?foo=bar")

    def test_reject_invalid_characters(self):
        """Non-alphanumeric characters should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid endpoint"):
            sanitize_endpoint("issue/ABC-123!comment")
