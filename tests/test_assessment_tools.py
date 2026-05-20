"""Tests for assessment tools."""

import json
import pytest
from unittest.mock import AsyncMock, patch


@pytest.fixture
def mock_client(mock_settings):
    with patch(
        "oma_service_mcp.src.tools.assessment_tools.MigrationPlannerClient"
    ) as MockClient:
        instance = AsyncMock()
        MockClient.return_value = instance
        yield instance


class TestListAssessments:
    @pytest.mark.asyncio
    async def test_returns_assessments(self, mock_client, mock_access_token_func):
        from oma_service_mcp.src.tools.assessment_tools import list_assessments

        mock_client.list_assessments.return_value = [{"id": "a1"}]

        result = await list_assessments(mock_access_token_func)
        parsed = json.loads(result)
        assert len(parsed) == 1

    @pytest.mark.asyncio
    async def test_empty_returns_message(self, mock_client, mock_access_token_func):
        from oma_service_mcp.src.tools.assessment_tools import list_assessments

        mock_client.list_assessments.return_value = []

        result = await list_assessments(mock_access_token_func)
        assert result == "No assessments found."

    @pytest.mark.asyncio
    async def test_passes_source_filter(self, mock_client, mock_access_token_func):
        from oma_service_mcp.src.tools.assessment_tools import list_assessments

        mock_client.list_assessments.return_value = []

        await list_assessments(mock_access_token_func, source_id="src-1")
        mock_client.list_assessments.assert_called_once_with(source_id="src-1")


class TestGetAssessment:
    @pytest.mark.asyncio
    async def test_returns_assessment(self, mock_client, mock_access_token_func):
        from oma_service_mcp.src.tools.assessment_tools import get_assessment

        assessment = {"id": "a1", "snapshots": []}
        mock_client.get_assessment.return_value = assessment

        result = await get_assessment(mock_access_token_func, assessment_id="a1")
        parsed = json.loads(result)
        assert parsed["id"] == "a1"


class TestCalculateClusterRequirements:
    @pytest.mark.asyncio
    async def test_passes_all_params(self, mock_client, mock_access_token_func):
        from oma_service_mcp.src.tools.assessment_tools import calculate_cluster_requirements

        mock_client.calculate_cluster_requirements.return_value = {"totalNodes": 5}

        result = await calculate_cluster_requirements(
            mock_access_token_func,
            assessment_id="a1",
            cluster_id="c1",
            cpu_overcommit_ratio="1:2",
            worker_node_cpu=32,
        )

        parsed = json.loads(result)
        assert parsed["totalNodes"] == 5
        mock_client.calculate_cluster_requirements.assert_called_once_with(
            assessment_id="a1",
            cluster_id="c1",
            cpu_overcommit_ratio="1:2",
            memory_overcommit_ratio="1:2",
            worker_node_cpu=32,
            worker_node_memory=64,
            control_plane_schedulable=False,
        )
