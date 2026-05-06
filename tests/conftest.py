"""Shared test fixtures for OMA Service MCP tests."""

import pytest


@pytest.fixture
def mock_access_token() -> str:
    """Return a mock access token."""
    return "mock-access-token-12345"


@pytest.fixture
def mock_access_token_func(mock_access_token: str):
    """Return a function that returns a mock access token."""
    return lambda: mock_access_token


@pytest.fixture
def sample_assessment_id() -> str:
    """Return a sample assessment UUID."""
    return "550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def sample_cluster_id() -> str:
    """Return a sample cluster ID."""
    return "cluster-001"


@pytest.fixture
def sample_source_id() -> str:
    """Return a sample source UUID."""
    return "660e8400-e29b-41d4-a716-446655440001"


@pytest.fixture
def migration_estimation_response() -> dict:
    """Return a sample migration estimation response."""
    return {
        "totalDuration": "PT48H30M",
        "phases": [
            {"name": "Pre-Migration Checks", "duration": "PT2H"},
            {"name": "Storage Migration", "duration": "PT40H"},
            {"name": "VM Cutover", "duration": "PT4H"},
            {"name": "Post-Migration Checks", "duration": "PT2H30M"},
        ],
        "vmCount": 150,
        "totalStorageGB": 5000,
    }


@pytest.fixture
def migration_complexity_response() -> dict:
    """Return a sample migration complexity response."""
    return {
        "overallComplexity": "Medium",
        "complexityScore": 65,
        "breakdown": {
            "byDiskSize": {
                "small": {"count": 50, "complexity": "Low"},
                "medium": {"count": 80, "complexity": "Medium"},
                "large": {"count": 20, "complexity": "High"},
            },
            "byOS": {
                "linux": {"count": 100, "complexity": "Low"},
                "windows": {"count": 45, "complexity": "Medium"},
                "other": {"count": 5, "complexity": "High"},
            },
        },
    }


@pytest.fixture
def cluster_requirements_response() -> dict:
    """Return a sample cluster requirements response."""
    return {
        "clusterSizing": {
            "totalNodes": 10,
            "workerNodes": 7,
            "controlPlaneNodes": 3,
            "totalCPU": 112,
            "totalMemoryGB": 448,
        },
        "resourceConsumption": {
            "cpuRequested": 80,
            "memoryRequestedGB": 320,
        },
        "inventoryTotals": {
            "totalVMs": 150,
            "totalCPU": 400,
            "totalMemoryGB": 800,
        },
    }


@pytest.fixture
def list_assessments_response() -> list:
    """Return a sample list assessments response."""
    return [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Production Assessment",
            "sourceType": "inventory",
            "createdAt": "2024-01-15T10:30:00Z",
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "name": "Dev Assessment",
            "sourceType": "rvtools",
            "createdAt": "2024-01-16T14:00:00Z",
        },
    ]


@pytest.fixture
def get_assessment_response() -> dict:
    """Return a sample get assessment response."""
    return {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "Production Assessment",
        "sourceType": "inventory",
        "sourceId": "660e8400-e29b-41d4-a716-446655440001",
        "createdAt": "2024-01-15T10:30:00Z",
        "snapshots": [
            {
                "id": "snap-001",
                "timestamp": "2024-01-15T10:30:00Z",
                "vmCount": 150,
                "clusters": ["cluster-001", "cluster-002"],
            }
        ],
    }


@pytest.fixture
def list_sources_response() -> list:
    """Return a sample list sources response."""
    return [
        {
            "id": "660e8400-e29b-41d4-a716-446655440001",
            "name": "vCenter Production",
            "type": "vcenter",
            "status": "connected",
        },
    ]


@pytest.fixture
def get_source_response() -> dict:
    """Return a sample get source response."""
    return {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "name": "vCenter Production",
        "type": "vcenter",
        "status": "connected",
        "inventory": {"vmCount": 150, "clusterCount": 2},
    }
