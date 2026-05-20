"""Shared test fixtures for OMA Service MCP tests."""

import pytest
from unittest.mock import patch

import httpx


@pytest.fixture
def mock_access_token_func():
    """Return a callable that provides a test token."""
    return lambda: "test-token-123"


@pytest.fixture
def mock_no_auth_func():
    """Return a callable that provides no token."""
    return lambda: None


@pytest.fixture
def mock_settings():
    """Patch settings for tests."""
    with patch("oma_service_mcp.src.settings.settings") as mock:
        mock.MIGRATION_PLANNER_URL = "http://test-planner:3443"
        mock.AUTH_TYPE = "none"
        mock.MCP_HOST = "0.0.0.0"
        mock.MCP_PORT = 8000
        mock.TRANSPORT = "streamable-http"
        mock.LOGGING_LEVEL = "INFO"
        mock.LOG_TO_FILE = False
        mock.__dict__ = {
            "MIGRATION_PLANNER_URL": "http://test-planner:3443",
            "AUTH_TYPE": "none",
        }
        yield mock


def make_response(status_code: int = 200, json_data: dict | list | None = None) -> httpx.Response:
    """Create a mock httpx Response."""
    response = httpx.Response(
        status_code=status_code,
        json=json_data or {},
        request=httpx.Request("GET", "http://test"),
    )
    return response
