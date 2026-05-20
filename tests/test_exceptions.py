"""Tests for exception handling utilities."""

import pytest

import httpx

from oma_service_mcp.src.service_client.exceptions import (
    sanitize_exceptions,
    MigrationPlannerAPIError,
)


class TestSanitizeExceptions:
    @pytest.mark.asyncio
    async def test_passes_through_on_success(self):
        @sanitize_exceptions
        async def good_func():
            return "ok"

        assert await good_func() == "ok"

    @pytest.mark.asyncio
    async def test_wraps_http_status_error(self):
        @sanitize_exceptions
        async def bad_func():
            response = httpx.Response(
                500,
                json={"error": "internal"},
                request=httpx.Request("GET", "http://test"),
            )
            raise httpx.HTTPStatusError("err", request=response.request, response=response)

        with pytest.raises(MigrationPlannerAPIError, match="500"):
            await bad_func()

    @pytest.mark.asyncio
    async def test_includes_body_for_4xx(self):
        @sanitize_exceptions
        async def bad_request_func():
            response = httpx.Response(
                400,
                text='{"detail": "bad cluster id"}',
                request=httpx.Request("POST", "http://test"),
            )
            raise httpx.HTTPStatusError("err", request=response.request, response=response)

        with pytest.raises(MigrationPlannerAPIError, match="bad cluster id"):
            await bad_request_func()

    @pytest.mark.asyncio
    async def test_wraps_request_error(self):
        @sanitize_exceptions
        async def timeout_func():
            raise httpx.ConnectError("Connection refused")

        with pytest.raises(MigrationPlannerAPIError, match="Request failed"):
            await timeout_func()

    @pytest.mark.asyncio
    async def test_wraps_unexpected_error(self):
        @sanitize_exceptions
        async def crash_func():
            raise ValueError("unexpected")

        with pytest.raises(MigrationPlannerAPIError, match="internal error"):
            await crash_func()
