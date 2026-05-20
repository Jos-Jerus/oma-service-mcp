"""Tests for authentication utilities."""

import pytest
from unittest.mock import MagicMock, patch


class TestExtractBearerFromRequest:
    def test_extracts_token(self):
        from oma_service_mcp.utils.auth import _extract_bearer_from_request

        mcp = MagicMock()
        context = MagicMock()
        request = MagicMock()
        request.headers.get.return_value = "Bearer my-token-123"
        context.request_context.request = request
        mcp.get_context.return_value = context

        token = _extract_bearer_from_request(mcp)
        assert token == "my-token-123"

    def test_returns_none_when_no_header(self):
        from oma_service_mcp.utils.auth import _extract_bearer_from_request

        mcp = MagicMock()
        context = MagicMock()
        request = MagicMock()
        request.headers.get.return_value = None
        context.request_context.request = request
        mcp.get_context.return_value = context

        assert _extract_bearer_from_request(mcp) is None

    def test_returns_none_when_context_fails(self):
        from oma_service_mcp.utils.auth import _extract_bearer_from_request

        mcp = MagicMock()
        mcp.get_context.side_effect = Exception("no context")

        assert _extract_bearer_from_request(mcp) is None

    def test_returns_none_for_non_bearer(self):
        from oma_service_mcp.utils.auth import _extract_bearer_from_request

        mcp = MagicMock()
        context = MagicMock()
        request = MagicMock()
        request.headers.get.return_value = "Basic dXNlcjpwYXNz"
        context.request_context.request = request
        mcp.get_context.return_value = context

        assert _extract_bearer_from_request(mcp) is None


class TestGetAccessToken:
    def test_none_auth_returns_none(self):
        from oma_service_mcp.utils.auth import get_access_token

        mcp = MagicMock()
        with patch("oma_service_mcp.utils.auth.get_setting", return_value="none"):
            assert get_access_token(mcp) is None

    def test_forwarded_returns_token(self):
        from oma_service_mcp.utils.auth import get_access_token

        mcp = MagicMock()
        context = MagicMock()
        request = MagicMock()
        request.headers.get.return_value = "Bearer forwarded-token"
        context.request_context.request = request
        mcp.get_context.return_value = context

        with patch("oma_service_mcp.utils.auth.get_setting", return_value="forwarded"):
            token = get_access_token(mcp)
            assert token == "forwarded-token"

    def test_forwarded_raises_when_no_token(self):
        from oma_service_mcp.utils.auth import get_access_token

        mcp = MagicMock()
        mcp.get_context.side_effect = Exception("no context")

        with patch("oma_service_mcp.utils.auth.get_setting", return_value="forwarded"):
            with pytest.raises(RuntimeError, match="no Authorization Bearer header"):
                get_access_token(mcp)

    def test_unknown_auth_type_raises(self):
        from oma_service_mcp.utils.auth import get_access_token

        mcp = MagicMock()
        with patch("oma_service_mcp.utils.auth.get_setting", return_value="oauth"):
            with pytest.raises(RuntimeError, match="Unknown AUTH_TYPE"):
                get_access_token(mcp)
