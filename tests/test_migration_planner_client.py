"""Tests for the Migration Planner client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from oma_service_mcp.src.service_client.migration_planner_client import MigrationPlannerClient
from oma_service_mcp.src.service_client.exceptions import MigrationPlannerAPIError


class TestMigrationPlannerClient:
    """Tests for MigrationPlannerClient."""

    @pytest.fixture
    def client(self, mock_access_token: str) -> MigrationPlannerClient:
        """Create a client instance with mocked settings."""
        with patch(
            "oma_service_mcp.src.service_client.migration_planner_client.get_setting"
        ) as mock_get_setting:
            mock_get_setting.return_value = "http://localhost:8080"
            return MigrationPlannerClient(mock_access_token)

    def test_client_initialization(self, client: MigrationPlannerClient, mock_access_token: str):
        """Test client initializes with correct values."""
        assert client.access_token == mock_access_token
        assert client.base_url == "http://localhost:8080"

    def test_get_headers_with_token(self, client: MigrationPlannerClient, mock_access_token: str):
        """Test headers include authorization when token is present."""
        headers = client._get_headers()
        assert headers["Authorization"] == f"Bearer {mock_access_token}"
        assert headers["Accept"] == "application/json"
        assert headers["Content-Type"] == "application/json"

    def test_get_headers_without_token(self):
        """Test headers exclude authorization when no token."""
        with patch(
            "oma_service_mcp.src.service_client.migration_planner_client.get_setting"
        ) as mock_get_setting:
            mock_get_setting.return_value = "http://localhost:8080"
            client = MigrationPlannerClient(None)
            headers = client._get_headers()
            assert "Authorization" not in headers


class TestCalculateMigrationEstimation:
    """Tests for calculate_migration_estimation method."""

    @pytest.fixture
    def client(self, mock_access_token: str) -> MigrationPlannerClient:
        """Create a client instance."""
        with patch(
            "oma_service_mcp.src.service_client.migration_planner_client.get_setting"
        ) as mock_get_setting:
            mock_get_setting.return_value = "http://localhost:8080"
            return MigrationPlannerClient(mock_access_token)

    async def test_calculate_migration_estimation_success(
        self,
        client: MigrationPlannerClient,
        sample_assessment_id: str,
        sample_cluster_id: str,
        migration_estimation_response: dict,
    ):
        """Test successful migration estimation calculation."""
        mock_response = MagicMock()
        mock_response.json.return_value = migration_estimation_response
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.calculate_migration_estimation(
                sample_assessment_id, sample_cluster_id
            )

        assert result == migration_estimation_response
        mock_client.post.assert_called_once_with(
            f"/api/v1/assessments/{sample_assessment_id}/migration-estimation",
            json={"clusterId": sample_cluster_id},
        )

    async def test_calculate_migration_estimation_api_error(
        self,
        client: MigrationPlannerClient,
        sample_assessment_id: str,
        sample_cluster_id: str,
    ):
        """Test migration estimation handles API errors."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Assessment not found"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found", request=MagicMock(), response=mock_response
        )

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_client", return_value=mock_client):
            with pytest.raises(MigrationPlannerAPIError) as exc_info:
                await client.calculate_migration_estimation(
                    sample_assessment_id, sample_cluster_id
                )

        assert "404" in str(exc_info.value)


class TestCalculateMigrationComplexity:
    """Tests for calculate_migration_complexity method."""

    @pytest.fixture
    def client(self, mock_access_token: str) -> MigrationPlannerClient:
        """Create a client instance."""
        with patch(
            "oma_service_mcp.src.service_client.migration_planner_client.get_setting"
        ) as mock_get_setting:
            mock_get_setting.return_value = "http://localhost:8080"
            return MigrationPlannerClient(mock_access_token)

    async def test_calculate_migration_complexity_success(
        self,
        client: MigrationPlannerClient,
        sample_assessment_id: str,
        sample_cluster_id: str,
        migration_complexity_response: dict,
    ):
        """Test successful migration complexity calculation."""
        mock_response = MagicMock()
        mock_response.json.return_value = migration_complexity_response
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.calculate_migration_complexity(
                sample_assessment_id, sample_cluster_id
            )

        assert result == migration_complexity_response
        mock_client.post.assert_called_once_with(
            f"/api/v1/assessments/{sample_assessment_id}/complexity-estimation",
            json={"clusterId": sample_cluster_id},
        )

    async def test_calculate_migration_complexity_api_error(
        self,
        client: MigrationPlannerClient,
        sample_assessment_id: str,
        sample_cluster_id: str,
    ):
        """Test migration complexity handles API errors."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=MagicMock(), response=mock_response
        )

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_client", return_value=mock_client):
            with pytest.raises(MigrationPlannerAPIError) as exc_info:
                await client.calculate_migration_complexity(
                    sample_assessment_id, sample_cluster_id
                )

        assert "500" in str(exc_info.value)


class TestCalculateClusterRequirements:
    """Tests for calculate_cluster_requirements method."""

    @pytest.fixture
    def client(self, mock_access_token: str) -> MigrationPlannerClient:
        """Create a client instance."""
        with patch(
            "oma_service_mcp.src.service_client.migration_planner_client.get_setting"
        ) as mock_get_setting:
            mock_get_setting.return_value = "http://localhost:8080"
            return MigrationPlannerClient(mock_access_token)

    async def test_calculate_cluster_requirements_success(
        self,
        client: MigrationPlannerClient,
        sample_assessment_id: str,
        sample_cluster_id: str,
        cluster_requirements_response: dict,
    ):
        """Test successful cluster requirements calculation."""
        mock_response = MagicMock()
        mock_response.json.return_value = cluster_requirements_response
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.calculate_cluster_requirements(
                sample_assessment_id, sample_cluster_id
            )

        assert result == cluster_requirements_response
        mock_client.post.assert_called_once()


class TestListAssessments:
    """Tests for list_assessments method."""

    @pytest.fixture
    def client(self, mock_access_token: str) -> MigrationPlannerClient:
        """Create a client instance."""
        with patch(
            "oma_service_mcp.src.service_client.migration_planner_client.get_setting"
        ) as mock_get_setting:
            mock_get_setting.return_value = "http://localhost:8080"
            return MigrationPlannerClient(mock_access_token)

    async def test_list_assessments_success(
        self,
        client: MigrationPlannerClient,
        list_assessments_response: list,
    ):
        """Test successful list assessments."""
        mock_response = MagicMock()
        mock_response.json.return_value = list_assessments_response
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.list_assessments()

        assert result == list_assessments_response
        assert len(result) == 2

    async def test_list_assessments_empty(
        self,
        client: MigrationPlannerClient,
    ):
        """Test list assessments returns empty list when no assessments."""
        mock_response = MagicMock()
        mock_response.json.return_value = None
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.list_assessments()

        assert result == []


class TestGetSource:
    """Tests for get_source method."""

    @pytest.fixture
    def client(self, mock_access_token: str) -> MigrationPlannerClient:
        """Create a client instance."""
        with patch(
            "oma_service_mcp.src.service_client.migration_planner_client.get_setting"
        ) as mock_get_setting:
            mock_get_setting.return_value = "http://localhost:8080"
            return MigrationPlannerClient(mock_access_token)

    async def test_get_source_success(
        self,
        client: MigrationPlannerClient,
        sample_source_id: str,
        get_source_response: dict,
    ):
        """Test successful get source."""
        mock_response = MagicMock()
        mock_response.json.return_value = get_source_response
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.get_source(sample_source_id)

        assert result == get_source_response
        mock_client.get.assert_called_once_with(f"/api/v1/sources/{sample_source_id}")

    async def test_get_source_not_found(
        self,
        client: MigrationPlannerClient,
        sample_source_id: str,
    ):
        """Test get source handles 404."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Source not found"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found", request=MagicMock(), response=mock_response
        )

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_client", return_value=mock_client):
            with pytest.raises(MigrationPlannerAPIError) as exc_info:
                await client.get_source(sample_source_id)

        assert "404" in str(exc_info.value)


class TestGetAssessment:
    """Tests for get_assessment method."""

    @pytest.fixture
    def client(self, mock_access_token: str) -> MigrationPlannerClient:
        """Create a client instance."""
        with patch(
            "oma_service_mcp.src.service_client.migration_planner_client.get_setting"
        ) as mock_get_setting:
            mock_get_setting.return_value = "http://localhost:8080"
            return MigrationPlannerClient(mock_access_token)

    async def test_get_assessment_success(
        self,
        client: MigrationPlannerClient,
        sample_assessment_id: str,
        get_assessment_response: dict,
    ):
        """Test successful get assessment."""
        mock_response = MagicMock()
        mock_response.json.return_value = get_assessment_response
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.get_assessment(sample_assessment_id)

        assert result == get_assessment_response
        mock_client.get.assert_called_once_with(
            f"/api/v1/assessments/{sample_assessment_id}"
        )

    async def test_get_assessment_not_found(
        self,
        client: MigrationPlannerClient,
        sample_assessment_id: str,
    ):
        """Test get assessment handles 404."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Assessment not found"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found", request=MagicMock(), response=mock_response
        )

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_client", return_value=mock_client):
            with pytest.raises(MigrationPlannerAPIError) as exc_info:
                await client.get_assessment(sample_assessment_id)

        assert "404" in str(exc_info.value)


class TestListSources:
    """Tests for list_sources method."""

    @pytest.fixture
    def client(self, mock_access_token: str) -> MigrationPlannerClient:
        """Create a client instance."""
        with patch(
            "oma_service_mcp.src.service_client.migration_planner_client.get_setting"
        ) as mock_get_setting:
            mock_get_setting.return_value = "http://localhost:8080"
            return MigrationPlannerClient(mock_access_token)

    async def test_list_sources_success(
        self,
        client: MigrationPlannerClient,
        list_sources_response: list,
    ):
        """Test successful list sources."""
        mock_response = MagicMock()
        mock_response.json.return_value = list_sources_response
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.list_sources()

        assert result == list_sources_response

    async def test_list_sources_empty(
        self,
        client: MigrationPlannerClient,
    ):
        """Test list sources returns empty list when no sources."""
        mock_response = MagicMock()
        mock_response.json.return_value = None
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.list_sources()

        assert result == []

    async def test_list_sources_connection_error(
        self,
        client: MigrationPlannerClient,
    ):
        """Test list sources handles connection errors."""
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(
            side_effect=httpx.RequestError("Connection refused", request=MagicMock())
        )
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_client", return_value=mock_client):
            with pytest.raises(MigrationPlannerAPIError):
                await client.list_sources()


class TestListAssessmentsWithFilter:
    """Tests for list_assessments with source_id filter."""

    @pytest.fixture
    def client(self, mock_access_token: str) -> MigrationPlannerClient:
        """Create a client instance."""
        with patch(
            "oma_service_mcp.src.service_client.migration_planner_client.get_setting"
        ) as mock_get_setting:
            mock_get_setting.return_value = "http://localhost:8080"
            return MigrationPlannerClient(mock_access_token)

    async def test_list_assessments_with_source_filter(
        self,
        client: MigrationPlannerClient,
        sample_source_id: str,
        list_assessments_response: list,
    ):
        """Test list assessments passes source_id as query parameter."""
        mock_response = MagicMock()
        mock_response.json.return_value = list_assessments_response
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        with patch.object(client, "_get_client", return_value=mock_client):
            result = await client.list_assessments(source_id=sample_source_id)

        assert result == list_assessments_response
        mock_client.get.assert_called_once_with(
            "/api/v1/assessments",
            params={"sourceId": sample_source_id},
        )
