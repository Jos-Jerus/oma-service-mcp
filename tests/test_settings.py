"""Tests for settings module."""

import pytest
from unittest.mock import patch

from oma_service_mcp.src.settings import Settings, validate_config, get_setting


class TestSettings:
    """Tests for Settings configuration."""

    def test_default_values(self):
        """Test that settings have correct defaults."""
        with patch.dict("os.environ", {}, clear=True):
            s = Settings()
            assert s.MCP_HOST == "0.0.0.0"
            assert s.MCP_PORT == 8000
            assert s.TRANSPORT == "streamable-http"
            assert s.MIGRATION_PLANNER_URL == "http://localhost:7443"
            assert s.AUTH_TYPE == "none"
            assert s.LOGGING_LEVEL == "INFO"
            assert s.LOG_TO_FILE is True

    def test_env_override(self):
        """Test that environment variables override defaults."""
        env = {
            "MCP_HOST": "127.0.0.1",
            "MCP_PORT": "9090",
            "TRANSPORT": "sse",
            "MIGRATION_PLANNER_URL": "http://planner:7443",
            "AUTH_TYPE": "forwarded",
            "LOGGING_LEVEL": "DEBUG",
            "LOG_TO_FILE": "false",
        }
        with patch.dict("os.environ", env, clear=True):
            s = Settings()
            assert s.MCP_HOST == "127.0.0.1"
            assert s.MCP_PORT == 9090
            assert s.TRANSPORT == "sse"
            assert s.MIGRATION_PLANNER_URL == "http://planner:7443"
            assert s.AUTH_TYPE == "forwarded"
            assert s.LOGGING_LEVEL == "DEBUG"
            assert s.LOG_TO_FILE is False

    def test_logging_level_normalized_to_upper(self):
        """Test that logging level is normalized to uppercase."""
        with patch.dict("os.environ", {"LOGGING_LEVEL": "debug"}, clear=True):
            s = Settings()
            assert s.LOGGING_LEVEL == "DEBUG"

    def test_invalid_transport_rejected(self):
        """Test that invalid transport values are rejected."""
        with patch.dict("os.environ", {"TRANSPORT": "websocket"}, clear=True):
            with pytest.raises(Exception):
                Settings()

    def test_invalid_auth_type_rejected(self):
        """Test that invalid auth type values are rejected."""
        with patch.dict("os.environ", {"AUTH_TYPE": "oauth2"}, clear=True):
            with pytest.raises(Exception):
                Settings()

    def test_port_below_range_rejected(self):
        """Test that port below 1024 is rejected."""
        with patch.dict("os.environ", {"MCP_PORT": "80"}, clear=True):
            with pytest.raises(Exception):
                Settings()

    def test_port_above_range_rejected(self):
        """Test that port above 65535 is rejected."""
        with patch.dict("os.environ", {"MCP_PORT": "70000"}, clear=True):
            with pytest.raises(Exception):
                Settings()


class TestValidateConfig:
    """Tests for validate_config function."""

    def test_valid_config_passes(self):
        """Test that valid configuration passes validation."""
        s = Settings()
        validate_config(s)  # Should not raise

    def test_invalid_port_raises(self):
        """Test that invalid port raises ValueError."""
        s = Settings()
        # Bypass pydantic validation to test validate_config directly
        object.__setattr__(s, "MCP_PORT", 80)
        with pytest.raises(ValueError, match="MCP_PORT must be between"):
            validate_config(s)


class TestGetSetting:
    """Tests for get_setting function."""

    def test_returns_setting_value(self):
        """Test that get_setting returns the correct value."""
        result = get_setting("MCP_PORT")
        assert isinstance(result, int)

    def test_returns_default_transport(self):
        """Test that get_setting returns default transport."""
        result = get_setting("TRANSPORT")
        assert result in ("streamable-http", "sse")
