"""Tests for system tools."""

import json
import pytest
from unittest.mock import AsyncMock, patch


@pytest.fixture
def mock_client(mock_settings):
    with patch(
        "oma_service_mcp.src.tools.system_tools.MigrationPlannerClient"
    ) as MockClient:
        instance = AsyncMock()
        MockClient.return_value = instance
        yield instance


class TestGetSystemInfo:
    @pytest.mark.asyncio
    async def test_returns_info(self, mock_client, mock_access_token_func):
        from oma_service_mcp.src.tools.system_tools import get_system_info

        mock_client.get_info.return_value = {
            "gitCommit": "abc123",
            "versionName": "v0.12.0",
        }

        result = await get_system_info(mock_access_token_func)
        parsed = json.loads(result)
        assert parsed["gitCommit"] == "abc123"
        assert parsed["versionName"] == "v0.12.0"
