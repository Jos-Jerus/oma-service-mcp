"""Tests for authentication utilities."""

from unittest.mock import MagicMock, patch

import pytest

from oma_service_mcp.utils.auth import get_access_token, _extract_bearer_from_request


class TestExtractBearerFromRequest:
    """Tests for _extract_bearer_from_request."""

    def test_extracts_valid_bearer_token(self):
        """Test extraction of a valid Bearer token from request headers."""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "Bearer my-secret-token"

        mock_context = MagicMock()
        mock_context.request_context.request = mock_request

        mcp = MagicMock()
        mcp.get_context.return_value = mock_context

        result = _extract_bearer_from_request(mcp)
        assert result == "my-secret-token"

    def test_returns_none_when_no_auth_header(self):
        """Test returns None when Authorization header is missing."""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = None

        mock_context = MagicMock()
        mock_context.request_context.request = mock_request

        mcp = MagicMock()
        mcp.get_context.return_value = mock_context

        result = _extract_bearer_from_request(mcp)
        assert result is None

    def test_returns_none_when_not_bearer_scheme(self):
        """Test returns None when auth header uses a non-Bearer scheme."""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "Basic dXNlcjpwYXNz"

        mock_context = MagicMock()
        mock_context.request_context.request = mock_request

        mcp = MagicMock()
        mcp.get_context.return_value = mock_context

        result = _extract_bearer_from_request(mcp)
        assert result is None

    def test_returns_none_when_malformed_header(self):
        """Test returns None when Authorization header has unexpected format."""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "Bearer"

        mock_context = MagicMock()
        mock_context.request_context.request = mock_request

        mcp = MagicMock()
        mcp.get_context.return_value = mock_context

        result = _extract_bearer_from_request(mcp)
        assert result is None

    def test_returns_none_when_get_context_raises(self):
        """Test returns None when get_context raises an exception."""
        mcp = MagicMock()
        mcp.get_context.side_effect = Exception("No context available")

        result = _extract_bearer_from_request(mcp)
        assert result is None

    def test_returns_none_when_request_is_none(self):
        """Test returns None when request object is None."""
        mock_context = MagicMock()
        mock_context.request_context.request = None

        mcp = MagicMock()
        mcp.get_context.return_value = mock_context

        result = _extract_bearer_from_request(mcp)
        assert result is None

    def test_returns_none_when_request_context_is_none(self):
        """Test returns None when request_context is None."""
        mock_context = MagicMock()
        mock_context.request_context = None

        mcp = MagicMock()
        mcp.get_context.return_value = mock_context

        result = _extract_bearer_from_request(mcp)
        assert result is None

    def test_bearer_case_insensitive(self):
        """Test that Bearer scheme matching is case-insensitive."""
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "BEARER my-token"

        mock_context = MagicMock()
        mock_context.request_context.request = mock_request

        mcp = MagicMock()
        mcp.get_context.return_value = mock_context

        result = _extract_bearer_from_request(mcp)
        assert result == "my-token"


class TestGetAccessToken:
    """Tests for get_access_token."""

    @patch("oma_service_mcp.utils.auth.get_setting")
    def test_returns_none_for_auth_type_none(self, mock_get_setting):
        """Test returns None when AUTH_TYPE is 'none'."""
        mock_get_setting.return_value = "none"
        mcp = MagicMock()

        result = get_access_token(mcp)
        assert result is None

    @patch("oma_service_mcp.utils.auth._extract_bearer_from_request")
    @patch("oma_service_mcp.utils.auth.get_setting")
    def test_returns_token_for_forwarded_auth(self, mock_get_setting, mock_extract):
        """Test returns forwarded token when AUTH_TYPE is 'forwarded'."""
        mock_get_setting.return_value = "forwarded"
        mock_extract.return_value = "forwarded-token-123"
        mcp = MagicMock()

        result = get_access_token(mcp)
        assert result == "forwarded-token-123"

    @patch("oma_service_mcp.utils.auth._extract_bearer_from_request")
    @patch("oma_service_mcp.utils.auth.get_setting")
    def test_raises_when_forwarded_but_no_token(self, mock_get_setting, mock_extract):
        """Test raises RuntimeError when forwarded auth has no token."""
        mock_get_setting.return_value = "forwarded"
        mock_extract.return_value = None
        mcp = MagicMock()

        with pytest.raises(RuntimeError, match="no Authorization Bearer header found"):
            get_access_token(mcp)

    @patch("oma_service_mcp.utils.auth.get_setting")
    def test_raises_for_unknown_auth_type(self, mock_get_setting):
        """Test raises RuntimeError for unknown AUTH_TYPE."""
        mock_get_setting.return_value = "oauth2"
        mcp = MagicMock()

        with pytest.raises(RuntimeError, match="Unknown AUTH_TYPE: oauth2"):
            get_access_token(mcp)
