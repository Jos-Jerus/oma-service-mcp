"""Tests for settings configuration."""

import pytest
from unittest.mock import patch


class TestSettings:
    def test_default_values(self):
        with patch.dict("os.environ", {}, clear=True):
            from oma_service_mcp.src.settings import Settings

            s = Settings()
            assert s.MCP_HOST == "0.0.0.0"
            assert s.MCP_PORT == 8000
            assert s.TRANSPORT == "streamable-http"
            assert s.AUTH_TYPE == "none"
            assert s.LOGGING_LEVEL == "INFO"

    def test_env_override(self):
        env = {
            "MCP_PORT": "9000",
            "AUTH_TYPE": "forwarded",
            "MIGRATION_PLANNER_URL": "http://custom:3443",
        }
        with patch.dict("os.environ", env, clear=True):
            from oma_service_mcp.src.settings import Settings

            s = Settings()
            assert s.MCP_PORT == 9000
            assert s.AUTH_TYPE == "forwarded"
            assert s.MIGRATION_PLANNER_URL == "http://custom:3443"

    def test_logging_level_normalized(self):
        with patch.dict("os.environ", {"LOGGING_LEVEL": "debug"}, clear=True):
            from oma_service_mcp.src.settings import Settings

            s = Settings()
            assert s.LOGGING_LEVEL == "DEBUG"

    def test_invalid_port_rejected(self):
        from pydantic import ValidationError
        from oma_service_mcp.src.settings import Settings

        with pytest.raises(ValidationError):
            Settings(MCP_PORT=80)


class TestValidateConfig:
    def test_valid_config_passes(self):
        from oma_service_mcp.src.settings import Settings, validate_config

        cfg = Settings()
        validate_config(cfg)

    def test_invalid_port_fails(self):
        from oma_service_mcp.src.settings import validate_config
        from unittest.mock import MagicMock

        cfg = MagicMock()
        cfg.MCP_PORT = 80
        with pytest.raises(ValueError):
            validate_config(cfg)


class TestGetSetting:
    def test_returns_attribute(self, mock_settings):
        from oma_service_mcp.src.settings import get_setting

        result = get_setting("AUTH_TYPE")
        assert result == "none"

    def test_returns_dict_override(self, mock_settings):
        from oma_service_mcp.src.settings import get_setting

        result = get_setting("MIGRATION_PLANNER_URL")
        assert result == "http://test-planner:3443"
