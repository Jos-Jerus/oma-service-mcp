"""Tests for exception handling utilities."""

import pytest
from unittest.mock import MagicMock, AsyncMock

import httpx

from oma_service_mcp.src.service_client.exceptions import (
    MigrationPlannerAPIError,
    sanitize_exceptions,
)


class TestSanitizeExceptions:
    """Tests for the sanitize_exceptions decorator."""

    async def test_passes_through_on_success(self):
        """Test that successful calls pass through unchanged."""

        @sanitize_exceptions
        async def good_func():
            return {"result": "ok"}

        result = await good_func()
        assert result == {"result": "ok"}

    async def test_wraps_http_status_error_4xx(self):
        """Test that 4xx HTTP errors include response body in message."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request: invalid parameter"

        @sanitize_exceptions
        async def bad_request_func():
            raise httpx.HTTPStatusError(
                "Bad Request",
                request=MagicMock(),
                response=mock_response,
            )

        with pytest.raises(MigrationPlannerAPIError) as exc_info:
            await bad_request_func()

        error_msg = str(exc_info.value)
        assert "400" in error_msg
        assert "Bad Request: invalid parameter" in error_msg

    async def test_wraps_http_status_error_5xx_without_body(self):
        """Test that 5xx HTTP errors do NOT include response body."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error with secrets"

        @sanitize_exceptions
        async def server_error_func():
            raise httpx.HTTPStatusError(
                "Server Error",
                request=MagicMock(),
                response=mock_response,
            )

        with pytest.raises(MigrationPlannerAPIError) as exc_info:
            await server_error_func()

        error_msg = str(exc_info.value)
        assert "500" in error_msg
        assert "Internal Server Error with secrets" not in error_msg

    async def test_wraps_request_error(self):
        """Test that connection/request errors are wrapped."""

        @sanitize_exceptions
        async def connection_error_func():
            raise httpx.RequestError("Connection refused", request=MagicMock())

        with pytest.raises(MigrationPlannerAPIError) as exc_info:
            await connection_error_func()

        assert "connection_error_func" in str(exc_info.value)

    async def test_wraps_unexpected_error(self):
        """Test that unexpected errors are wrapped with generic message."""

        @sanitize_exceptions
        async def unexpected_func():
            raise ValueError("something broke")

        with pytest.raises(MigrationPlannerAPIError) as exc_info:
            await unexpected_func()

        assert "internal error" in str(exc_info.value).lower()

    async def test_preserves_function_name(self):
        """Test that the decorator preserves the wrapped function's name."""

        @sanitize_exceptions
        async def my_named_function():
            return True

        assert my_named_function.__name__ == "my_named_function"

    async def test_http_status_error_404(self):
        """Test 404 error includes details (it's a 4xx)."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Assessment not found"

        @sanitize_exceptions
        async def not_found_func():
            raise httpx.HTTPStatusError(
                "Not Found",
                request=MagicMock(),
                response=mock_response,
            )

        with pytest.raises(MigrationPlannerAPIError) as exc_info:
            await not_found_func()

        error_msg = str(exc_info.value)
        assert "404" in error_msg
        assert "Assessment not found" in error_msg

    async def test_http_status_error_422(self):
        """Test 422 error includes details (it's a 4xx)."""
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.text = '{"detail":"Validation error"}'

        @sanitize_exceptions
        async def validation_func():
            raise httpx.HTTPStatusError(
                "Unprocessable Entity",
                request=MagicMock(),
                response=mock_response,
            )

        with pytest.raises(MigrationPlannerAPIError) as exc_info:
            await validation_func()

        error_msg = str(exc_info.value)
        assert "422" in error_msg
        assert "Validation error" in error_msg
