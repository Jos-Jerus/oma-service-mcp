"""Tests for the Migration Planner API client."""

import pytest
from unittest.mock import AsyncMock, patch

import httpx

from tests.conftest import make_response


@pytest.fixture
def client(mock_settings):
    from oma_service_mcp.src.service_client.migration_planner_client import MigrationPlannerClient

    return MigrationPlannerClient(access_token="test-token")


@pytest.fixture
def client_no_auth(mock_settings):
    from oma_service_mcp.src.service_client.migration_planner_client import MigrationPlannerClient

    return MigrationPlannerClient(access_token=None)


class TestClientInit:
    def test_headers_with_token(self, client):
        headers = client._get_headers()
        assert headers["Authorization"] == "Bearer test-token"
        assert headers["Accept"] == "application/json"

    def test_headers_without_token(self, client_no_auth):
        headers = client_no_auth._get_headers()
        assert "Authorization" not in headers

    def test_base_url_trailing_slash_stripped(self, mock_settings):
        mock_settings.__dict__["MIGRATION_PLANNER_URL"] = "http://example.com/"
        from oma_service_mcp.src.service_client.migration_planner_client import (
            MigrationPlannerClient,
        )

        c = MigrationPlannerClient()
        assert c.base_url == "http://example.com"


class TestListSources:
    @pytest.mark.asyncio
    async def test_returns_sources(self, client):
        sources = [{"id": "src-1", "name": "vcenter-1"}]
        mock_resp = make_response(200, sources)

        with patch.object(client, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_get.return_value = mock_client

            result = await client.list_sources()
            assert result == sources
            mock_client.get.assert_called_once_with("/api/v1/sources")

    @pytest.mark.asyncio
    async def test_returns_empty_list_on_empty_array(self, client):
        mock_resp = make_response(200, [])

        with patch.object(client, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_get.return_value = mock_client

            result = await client.list_sources()
            assert result == []


class TestGetSource:
    @pytest.mark.asyncio
    async def test_returns_source(self, client):
        source = {"id": "src-1", "name": "vcenter-1", "inventory": {}}
        mock_resp = make_response(200, source)

        with patch.object(client, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_get.return_value = mock_client

            result = await client.get_source("src-1")
            assert result == source
            mock_client.get.assert_called_once_with("/api/v1/sources/src-1")


class TestListAssessments:
    @pytest.mark.asyncio
    async def test_without_filter(self, client):
        assessments = [{"id": "a-1"}]
        mock_resp = make_response(200, assessments)

        with patch.object(client, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_get.return_value = mock_client

            result = await client.list_assessments()
            assert result == assessments
            mock_client.get.assert_called_once_with("/api/v1/assessments", params={})

    @pytest.mark.asyncio
    async def test_with_source_filter(self, client):
        mock_resp = make_response(200, [])

        with patch.object(client, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_get.return_value = mock_client

            await client.list_assessments(source_id="src-1")
            mock_client.get.assert_called_once_with(
                "/api/v1/assessments", params={"sourceId": "src-1"}
            )


class TestCalculateClusterRequirements:
    @pytest.mark.asyncio
    async def test_sends_correct_body(self, client):
        result_data = {"totalNodes": 5}
        mock_resp = make_response(200, result_data)

        with patch.object(client, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_get.return_value = mock_client

            result = await client.calculate_cluster_requirements(
                assessment_id="a-1", cluster_id="c-1"
            )
            assert result == result_data

            call_args = mock_client.post.call_args
            assert call_args[0][0] == "/api/v1/assessments/a-1/cluster-requirements"
            body = call_args[1]["json"]
            assert body["clusterId"] == "c-1"
            assert body["cpuOverCommitRatio"] == "1:4"
            assert body["workerNodeCPU"] == 16


class TestGetComplexityEstimation:
    @pytest.mark.asyncio
    async def test_sends_cluster_id(self, client):
        result_data = {"complexityByDisk": [], "complexityByOS": []}
        mock_resp = make_response(200, result_data)

        with patch.object(client, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_get.return_value = mock_client

            result = await client.get_complexity_estimation("a-1", "c-1")
            assert result == result_data

            call_args = mock_client.post.call_args
            assert call_args[0][0] == "/api/v1/assessments/a-1/complexity-estimation"
            assert call_args[1]["json"] == {"clusterId": "c-1"}


class TestGetMigrationEstimation:
    @pytest.mark.asyncio
    async def test_minimal_params(self, client):
        result_data = {"estimation": {}}
        mock_resp = make_response(200, result_data)

        with patch.object(client, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_get.return_value = mock_client

            result = await client.get_migration_estimation("a-1", "c-1")
            assert result == result_data

            body = mock_client.post.call_args[1]["json"]
            assert body == {"clusterId": "c-1"}
            assert "params" not in body

    @pytest.mark.asyncio
    async def test_with_optional_params(self, client):
        mock_resp = make_response(200, {})

        with patch.object(client, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_get.return_value = mock_client

            await client.get_migration_estimation(
                "a-1", "c-1", transfer_rate_mbps=1000, post_migration_engineers=5
            )

            body = mock_client.post.call_args[1]["json"]
            assert body["params"]["transfer_rate_mbps"] == 1000
            assert body["params"]["post_migration_engineers"] == 5
            assert "work_hours_per_day" not in body["params"]


class TestGetMigrationEstimationByComplexity:
    @pytest.mark.asyncio
    async def test_calls_correct_endpoint(self, client):
        mock_resp = make_response(200, {"complexityByOsDisk": []})

        with patch.object(client, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_get.return_value = mock_client

            await client.get_migration_estimation_by_complexity("a-1", "c-1")
            endpoint = mock_client.post.call_args[0][0]
            assert endpoint == "/api/v1/assessments/a-1/migration-estimation/by-complexity"


class TestGetInfo:
    @pytest.mark.asyncio
    async def test_returns_info(self, client):
        info = {"gitCommit": "abc123", "versionName": "v0.1.0"}
        mock_resp = make_response(200, info)

        with patch.object(client, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_get.return_value = mock_client

            result = await client.get_info()
            assert result == info
            mock_client.get.assert_called_once_with("/api/v1/info")


class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_http_error_raises_api_error(self, client):
        from oma_service_mcp.src.service_client.exceptions import MigrationPlannerAPIError

        error_resp = httpx.Response(
            404,
            json={"message": "not found"},
            request=httpx.Request("GET", "http://test/api/v1/sources/bad"),
        )

        with patch.object(client, "_get_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=error_resp)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            mock_get.return_value = mock_client

            with pytest.raises(MigrationPlannerAPIError, match="404"):
                await client.get_source("bad")
