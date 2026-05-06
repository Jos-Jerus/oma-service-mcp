"""Tests for logging utilities."""

import logging

from oma_service_mcp.src.logger import SensitiveFormatter


class TestSensitiveFormatter:
    """Tests for SensitiveFormatter."""

    def test_redacts_bearer_token(self):
        """Test that Bearer tokens are redacted in log output."""
        formatter = SensitiveFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        assert "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9" not in output
        assert "REDACTED" in output

    def test_redacts_token_key_value(self):
        """Test that token=value patterns are redacted."""
        formatter = SensitiveFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="token=abc123secret",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        assert "abc123secret" not in output
        assert "REDACTED" in output

    def test_leaves_non_sensitive_data_intact(self):
        """Test that non-sensitive messages are unchanged."""
        formatter = SensitiveFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Successfully retrieved 5 sources",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        assert "Successfully retrieved 5 sources" in output

    def test_uses_default_format(self):
        """Test that default format includes expected fields."""
        formatter = SensitiveFormatter()
        record = logging.LogRecord(
            name="test-logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="test message",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        assert "test-logger" in output
        assert "INFO" in output

    def test_custom_format(self):
        """Test that a custom format string is respected."""
        formatter = SensitiveFormatter(fmt="%(levelname)s: %(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="test.py",
            lineno=1,
            msg="warning message",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        assert output.startswith("WARNING: warning message")
