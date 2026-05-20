"""Tests for source tools."""

import json
import pytest
from unittest.mock import AsyncMock, patch


@pytest.fixture
def mock_client(mock_settings):
    with patch(
        "oma_service_mcp.src.tools.source_tools.MigrationPlannerClient"
    ) as MockClient:
        instance = AsyncMock()
        MockClient.return_value = instance
        yield instance


class TestListSources:
    @pytest.mark.asyncio
    async def test_returns_formatted_sources(self, mock_client, mock_access_token_func):
        from oma_service_mcp.src.tools.source_tools import list_sources

        mock_client.list_sources.return_value = [
            {"id": "s1", "name": "vcenter-prod"}
        ]

        result = await list_sources(mock_access_token_func)
        parsed = json.loads(result)
        assert len(parsed) == 1
        assert parsed[0]["name"] == "vcenter-prod"

    @pytest.mark.asyncio
    async def test_returns_message_when_empty(self, mock_client, mock_access_token_func):
        from oma_service_mcp.src.tools.source_tools import list_sources

        mock_client.list_sources.return_value = []

        result = await list_sources(mock_access_token_func)
        assert result == "No sources found."


class TestGetSource:
    @pytest.mark.asyncio
    async def test_returns_source_detail(self, mock_client, mock_access_token_func):
        from oma_service_mcp.src.tools.source_tools import get_source

        source = {"id": "s1", "name": "vcenter-prod", "inventory": {"vms": 100}}
        mock_client.get_source.return_value = source

        result = await get_source(mock_access_token_func, source_id="s1")
        parsed = json.loads(result)
        assert parsed["inventory"]["vms"] == 100
        mock_client.get_source.assert_called_once_with("s1")
