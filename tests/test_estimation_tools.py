"""Tests for estimation tools."""

import json
import pytest
from unittest.mock import AsyncMock, patch


@pytest.fixture
def mock_client(mock_settings):
    with patch(
        "oma_service_mcp.src.tools.estimation_tools.MigrationPlannerClient"
    ) as MockClient:
        instance = AsyncMock()
        MockClient.return_value = instance
        yield instance


class TestGetComplexityEstimation:
    @pytest.mark.asyncio
    async def test_returns_complexity(self, mock_client, mock_access_token_func):
        from oma_service_mcp.src.tools.estimation_tools import get_complexity_estimation

        mock_client.get_complexity_estimation.return_value = {
            "complexityByDisk": [{"score": 1, "count": 50}],
            "complexityByOS": [{"score": 1, "count": 30}],
        }

        result = await get_complexity_estimation(
            mock_access_token_func, assessment_id="a1", cluster_id="c1"
        )
        parsed = json.loads(result)
        assert "complexityByDisk" in parsed
        assert "complexityByOS" in parsed

    @pytest.mark.asyncio
    async def test_passes_params_correctly(self, mock_client, mock_access_token_func):
        from oma_service_mcp.src.tools.estimation_tools import get_complexity_estimation

        mock_client.get_complexity_estimation.return_value = {}

        await get_complexity_estimation(
            mock_access_token_func, assessment_id="a1", cluster_id="c1"
        )
        mock_client.get_complexity_estimation.assert_called_once_with(
            assessment_id="a1", cluster_id="c1"
        )


class TestGetMigrationEstimation:
    @pytest.mark.asyncio
    async def test_minimal_params(self, mock_client, mock_access_token_func):
        from oma_service_mcp.src.tools.estimation_tools import get_migration_estimation

        mock_client.get_migration_estimation.return_value = {
            "estimation": {"network-based": {"minTotalDuration": "4h30m"}}
        }

        result = await get_migration_estimation(
            mock_access_token_func, assessment_id="a1", cluster_id="c1"
        )
        parsed = json.loads(result)
        assert "estimation" in parsed

    @pytest.mark.asyncio
    async def test_with_optional_params(self, mock_client, mock_access_token_func):
        from oma_service_mcp.src.tools.estimation_tools import get_migration_estimation

        mock_client.get_migration_estimation.return_value = {}

        await get_migration_estimation(
            mock_access_token_func,
            assessment_id="a1",
            cluster_id="c1",
            transfer_rate_mbps=1000,
            post_migration_engineers=5,
        )

        mock_client.get_migration_estimation.assert_called_once_with(
            assessment_id="a1",
            cluster_id="c1",
            transfer_rate_mbps=1000,
            work_hours_per_day=None,
            troubleshoot_mins_per_vm=None,
            post_migration_engineers=5,
        )


class TestGetMigrationEstimationByComplexity:
    @pytest.mark.asyncio
    async def test_returns_grouped_results(self, mock_client, mock_access_token_func):
        from oma_service_mcp.src.tools.estimation_tools import (
            get_migration_estimation_by_complexity,
        )

        mock_client.get_migration_estimation_by_complexity.return_value = {
            "complexityByOsDisk": [{"score": 1, "vmCount": 20}],
            "complexityMatrix": {},
        }

        result = await get_migration_estimation_by_complexity(
            mock_access_token_func, assessment_id="a1", cluster_id="c1"
        )
        parsed = json.loads(result)
        assert "complexityByOsDisk" in parsed
