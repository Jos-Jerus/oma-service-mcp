"""Tests for source tools."""

import json
import pytest
from unittest.mock import AsyncMock, patch

from oma_service_mcp.src.tools import source_tools


class TestListSourcesTool:
    """Tests for list_sources tool function."""

    async def test_list_sources_returns_json(
        self,
        mock_access_token_func,
        list_sources_response: list,
    ):
        """Test tool returns properly formatted JSON."""
        with patch(
            "oma_service_mcp.src.tools.source_tools.MigrationPlannerClient"
        ) as MockClient:
            mock_client = AsyncMock()
            mock_client.list_sources = AsyncMock(return_value=list_sources_response)
            MockClient.return_value = mock_client

            result = await source_tools.list_sources(mock_access_token_func)

        parsed = json.loads(result)
        assert parsed == list_sources_response
        assert len(parsed) == 1

    async def test_list_sources_empty_returns_message(
        self,
        mock_access_token_func,
    ):
        """Test tool returns message when no sources found."""
        with patch(
            "oma_service_mcp.src.tools.source_tools.MigrationPlannerClient"
        ) as MockClient:
            mock_client = AsyncMock()
            mock_client.list_sources = AsyncMock(return_value=[])
            MockClient.return_value = mock_client

            result = await source_tools.list_sources(mock_access_token_func)

        assert result == "No sources found."

    async def test_list_sources_uses_access_token(
        self,
        mock_access_token_func,
        mock_access_token: str,
        list_sources_response: list,
    ):
        """Test tool passes access token to client."""
        with patch(
            "oma_service_mcp.src.tools.source_tools.MigrationPlannerClient"
        ) as MockClient:
            mock_client = AsyncMock()
            mock_client.list_sources = AsyncMock(return_value=list_sources_response)
            MockClient.return_value = mock_client

            await source_tools.list_sources(mock_access_token_func)

            MockClient.assert_called_once_with(mock_access_token)


class TestGetSourceTool:
    """Tests for get_source tool function."""

    async def test_get_source_returns_json(
        self,
        mock_access_token_func,
        sample_source_id: str,
        get_source_response: dict,
    ):
        """Test tool returns properly formatted JSON."""
        with patch(
            "oma_service_mcp.src.tools.source_tools.MigrationPlannerClient"
        ) as MockClient:
            mock_client = AsyncMock()
            mock_client.get_source = AsyncMock(return_value=get_source_response)
            MockClient.return_value = mock_client

            result = await source_tools.get_source(
                mock_access_token_func,
                sample_source_id,
            )

        parsed = json.loads(result)
        assert parsed == get_source_response
        assert parsed["id"] == sample_source_id

    async def test_get_source_calls_client(
        self,
        mock_access_token_func,
        sample_source_id: str,
        get_source_response: dict,
    ):
        """Test tool calls client with correct source_id."""
        with patch(
            "oma_service_mcp.src.tools.source_tools.MigrationPlannerClient"
        ) as MockClient:
            mock_client = AsyncMock()
            mock_client.get_source = AsyncMock(return_value=get_source_response)
            MockClient.return_value = mock_client

            await source_tools.get_source(
                mock_access_token_func,
                sample_source_id,
            )

            mock_client.get_source.assert_called_once_with(sample_source_id)
