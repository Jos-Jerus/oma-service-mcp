"""Tests for assessment tools."""

import json
import pytest
from unittest.mock import AsyncMock, patch

from oma_service_mcp.src.tools import assessment_tools


class TestCalculateMigrationEstimationTool:
    """Tests for calculate_migration_estimation tool function."""

    async def test_calculate_migration_estimation_returns_json(
        self,
        mock_access_token_func,
        sample_assessment_id: str,
        sample_cluster_id: str,
        migration_estimation_response: dict,
    ):
        """Test tool returns properly formatted JSON."""
        with patch(
            "oma_service_mcp.src.tools.assessment_tools.MigrationPlannerClient"
        ) as MockClient:
            mock_client = AsyncMock()
            mock_client.calculate_migration_estimation = AsyncMock(
                return_value=migration_estimation_response
            )
            MockClient.return_value = mock_client

            result = await assessment_tools.calculate_migration_estimation(
                mock_access_token_func,
                sample_assessment_id,
                sample_cluster_id,
            )

        parsed = json.loads(result)
        assert parsed == migration_estimation_response
        assert "totalDuration" in parsed
        assert "phases" in parsed

    async def test_calculate_migration_estimation_calls_client(
        self,
        mock_access_token_func,
        sample_assessment_id: str,
        sample_cluster_id: str,
        migration_estimation_response: dict,
    ):
        """Test tool calls client with correct parameters."""
        with patch(
            "oma_service_mcp.src.tools.assessment_tools.MigrationPlannerClient"
        ) as MockClient:
            mock_client = AsyncMock()
            mock_client.calculate_migration_estimation = AsyncMock(
                return_value=migration_estimation_response
            )
            MockClient.return_value = mock_client

            await assessment_tools.calculate_migration_estimation(
                mock_access_token_func,
                sample_assessment_id,
                sample_cluster_id,
            )

            mock_client.calculate_migration_estimation.assert_called_once_with(
                assessment_id=sample_assessment_id,
                cluster_id=sample_cluster_id,
            )


class TestCalculateMigrationComplexityTool:
    """Tests for calculate_migration_complexity tool function."""

    async def test_calculate_migration_complexity_returns_json(
        self,
        mock_access_token_func,
        sample_assessment_id: str,
        sample_cluster_id: str,
        migration_complexity_response: dict,
    ):
        """Test tool returns properly formatted JSON."""
        with patch(
            "oma_service_mcp.src.tools.assessment_tools.MigrationPlannerClient"
        ) as MockClient:
            mock_client = AsyncMock()
            mock_client.calculate_migration_complexity = AsyncMock(
                return_value=migration_complexity_response
            )
            MockClient.return_value = mock_client

            result = await assessment_tools.calculate_migration_complexity(
                mock_access_token_func,
                sample_assessment_id,
                sample_cluster_id,
            )

        parsed = json.loads(result)
        assert parsed == migration_complexity_response
        assert "overallComplexity" in parsed
        assert "breakdown" in parsed

    async def test_calculate_migration_complexity_calls_client(
        self,
        mock_access_token_func,
        sample_assessment_id: str,
        sample_cluster_id: str,
        migration_complexity_response: dict,
    ):
        """Test tool calls client with correct parameters."""
        with patch(
            "oma_service_mcp.src.tools.assessment_tools.MigrationPlannerClient"
        ) as MockClient:
            mock_client = AsyncMock()
            mock_client.calculate_migration_complexity = AsyncMock(
                return_value=migration_complexity_response
            )
            MockClient.return_value = mock_client

            await assessment_tools.calculate_migration_complexity(
                mock_access_token_func,
                sample_assessment_id,
                sample_cluster_id,
            )

            mock_client.calculate_migration_complexity.assert_called_once_with(
                assessment_id=sample_assessment_id,
                cluster_id=sample_cluster_id,
            )


class TestCalculateClusterRequirementsTool:
    """Tests for calculate_cluster_requirements tool function."""

    async def test_calculate_cluster_requirements_returns_json(
        self,
        mock_access_token_func,
        sample_assessment_id: str,
        sample_cluster_id: str,
        cluster_requirements_response: dict,
    ):
        """Test tool returns properly formatted JSON."""
        with patch(
            "oma_service_mcp.src.tools.assessment_tools.MigrationPlannerClient"
        ) as MockClient:
            mock_client = AsyncMock()
            mock_client.calculate_cluster_requirements = AsyncMock(
                return_value=cluster_requirements_response
            )
            MockClient.return_value = mock_client

            result = await assessment_tools.calculate_cluster_requirements(
                mock_access_token_func,
                sample_assessment_id,
                sample_cluster_id,
            )

        parsed = json.loads(result)
        assert parsed == cluster_requirements_response
        assert "clusterSizing" in parsed

    async def test_calculate_cluster_requirements_with_custom_params(
        self,
        mock_access_token_func,
        sample_assessment_id: str,
        sample_cluster_id: str,
        cluster_requirements_response: dict,
    ):
        """Test tool passes custom parameters to client."""
        with patch(
            "oma_service_mcp.src.tools.assessment_tools.MigrationPlannerClient"
        ) as MockClient:
            mock_client = AsyncMock()
            mock_client.calculate_cluster_requirements = AsyncMock(
                return_value=cluster_requirements_response
            )
            MockClient.return_value = mock_client

            await assessment_tools.calculate_cluster_requirements(
                mock_access_token_func,
                sample_assessment_id,
                sample_cluster_id,
                cpu_overcommit_ratio="1:2",
                memory_overcommit_ratio="1:1",
                worker_node_cpu=32,
                worker_node_memory=128,
                control_plane_schedulable=True,
            )

            mock_client.calculate_cluster_requirements.assert_called_once_with(
                assessment_id=sample_assessment_id,
                cluster_id=sample_cluster_id,
                cpu_overcommit_ratio="1:2",
                memory_overcommit_ratio="1:1",
                worker_node_cpu=32,
                worker_node_memory=128,
                control_plane_schedulable=True,
            )


class TestListAssessmentsTool:
    """Tests for list_assessments tool function."""

    async def test_list_assessments_returns_json(
        self,
        mock_access_token_func,
        list_assessments_response: list,
    ):
        """Test tool returns properly formatted JSON."""
        with patch(
            "oma_service_mcp.src.tools.assessment_tools.MigrationPlannerClient"
        ) as MockClient:
            mock_client = AsyncMock()
            mock_client.list_assessments = AsyncMock(return_value=list_assessments_response)
            MockClient.return_value = mock_client

            result = await assessment_tools.list_assessments(mock_access_token_func)

        parsed = json.loads(result)
        assert parsed == list_assessments_response
        assert len(parsed) == 2

    async def test_list_assessments_empty_returns_message(
        self,
        mock_access_token_func,
    ):
        """Test tool returns message when no assessments found."""
        with patch(
            "oma_service_mcp.src.tools.assessment_tools.MigrationPlannerClient"
        ) as MockClient:
            mock_client = AsyncMock()
            mock_client.list_assessments = AsyncMock(return_value=[])
            MockClient.return_value = mock_client

            result = await assessment_tools.list_assessments(mock_access_token_func)

        assert result == "No assessments found."

    async def test_list_assessments_with_source_filter(
        self,
        mock_access_token_func,
        sample_source_id: str,
        list_assessments_response: list,
    ):
        """Test tool passes source_id filter to client."""
        with patch(
            "oma_service_mcp.src.tools.assessment_tools.MigrationPlannerClient"
        ) as MockClient:
            mock_client = AsyncMock()
            mock_client.list_assessments = AsyncMock(return_value=list_assessments_response)
            MockClient.return_value = mock_client

            await assessment_tools.list_assessments(
                mock_access_token_func,
                source_id=sample_source_id,
            )

            mock_client.list_assessments.assert_called_once_with(source_id=sample_source_id)


class TestGetAssessmentTool:
    """Tests for get_assessment tool function."""

    async def test_get_assessment_returns_json(
        self,
        mock_access_token_func,
        sample_assessment_id: str,
        get_assessment_response: dict,
    ):
        """Test tool returns properly formatted JSON."""
        with patch(
            "oma_service_mcp.src.tools.assessment_tools.MigrationPlannerClient"
        ) as MockClient:
            mock_client = AsyncMock()
            mock_client.get_assessment = AsyncMock(return_value=get_assessment_response)
            MockClient.return_value = mock_client

            result = await assessment_tools.get_assessment(
                mock_access_token_func,
                sample_assessment_id,
            )

        parsed = json.loads(result)
        assert parsed == get_assessment_response
        assert parsed["id"] == sample_assessment_id
