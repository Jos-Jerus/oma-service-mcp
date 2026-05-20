"""Async HTTP client for the Migration Planner API.

Provides the MigrationPlannerClient class for interacting with the
Migration Planner service endpoints for sources, assessments,
cluster requirements, complexity/migration estimations, and system info.
"""

from typing import Any, Optional

import httpx
from oma_service_mcp.src.logger import log
from oma_service_mcp.src.settings import get_setting
from .exceptions import sanitize_exceptions


class MigrationPlannerClient:
    """Async client for the Migration Planner API.

    Args:
        access_token: The access token for authenticating with the API.
            None if no authentication is required (AUTH_TYPE=none).
    """

    def __init__(self, access_token: str | None = None) -> None:
        """Initialize the client with an optional access token."""
        self.access_token = access_token
        self.base_url: str = get_setting("MIGRATION_PLANNER_URL").rstrip("/")

    def _get_headers(self) -> dict[str, str]:
        """Build request headers including auth if configured."""
        headers: dict[str, str] = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def _get_client(self) -> httpx.AsyncClient:
        """Create an httpx async client with base URL and headers."""
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._get_headers(),
            timeout=30.0,
        )

    @sanitize_exceptions
    async def list_sources(self) -> list[dict[str, Any]]:
        """List all sources.

        Returns:
            list[dict]: A list of source objects.
        """
        log.info("Listing all sources")
        async with self._get_client() as client:
            response = await client.get("/api/v1/sources")
            response.raise_for_status()
            result = response.json()
            log.info("Successfully listed %d sources", len(result) if result else 0)
            return result if result else []

    @sanitize_exceptions
    async def get_source(self, source_id: str) -> dict[str, Any]:
        """Get a specific source by ID.

        Args:
            source_id: The UUID of the source.

        Returns:
            dict: The source object.
        """
        log.info("Getting source %s", source_id)
        async with self._get_client() as client:
            response = await client.get(f"/api/v1/sources/{source_id}")
            response.raise_for_status()
            result = response.json()
            log.info("Successfully retrieved source %s", source_id)
            return result

    @sanitize_exceptions
    async def list_assessments(
        self, source_id: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """List assessments, optionally filtered by source ID.

        Args:
            source_id: Optional source UUID to filter assessments.

        Returns:
            list[dict]: A list of assessment objects.
        """
        log.info("Listing assessments (source_id filter: %s)", source_id)
        params: dict[str, str] = {}
        if source_id:
            params["sourceId"] = source_id

        async with self._get_client() as client:
            response = await client.get("/api/v1/assessments", params=params)
            response.raise_for_status()
            result = response.json()
            log.info("Successfully listed %d assessments", len(result) if result else 0)
            return result if result else []

    @sanitize_exceptions
    async def get_assessment(self, assessment_id: str) -> dict[str, Any]:
        """Get a specific assessment by ID.

        Args:
            assessment_id: The UUID of the assessment.

        Returns:
            dict: The assessment object.
        """
        log.info("Getting assessment %s", assessment_id)
        async with self._get_client() as client:
            response = await client.get(f"/api/v1/assessments/{assessment_id}")
            response.raise_for_status()
            result = response.json()
            log.info("Successfully retrieved assessment %s", assessment_id)
            return result

    @sanitize_exceptions
    async def calculate_cluster_requirements(
        self,
        assessment_id: str,
        cluster_id: str,
        cpu_overcommit_ratio: str = "1:4",
        memory_overcommit_ratio: str = "1:2",
        worker_node_cpu: int = 16,
        worker_node_memory: int = 64,
        control_plane_schedulable: bool = False,
    ) -> dict[str, Any]:
        """Calculate cluster requirements for an assessment.

        Args:
            assessment_id: The UUID of the assessment.
            cluster_id: The ID of the cluster to calculate requirements for.
            cpu_overcommit_ratio: CPU over-commit ratio (e.g., "1:1", "1:2", "1:4", "1:6").
            memory_overcommit_ratio: Memory over-commit ratio (e.g., "1:1", "1:2", "1:4").
            worker_node_cpu: CPU cores per worker node.
            worker_node_memory: Memory (GB) per worker node.
            control_plane_schedulable: Allow workload scheduling on control plane nodes.

        Returns:
            dict: Cluster requirements response with sizing, resource consumption, and inventory totals.
        """
        log.info(
            "Calculating cluster requirements for assessment %s, cluster %s",
            assessment_id,
            cluster_id,
        )
        request_body = {
            "clusterId": cluster_id,
            "cpuOverCommitRatio": cpu_overcommit_ratio,
            "memoryOverCommitRatio": memory_overcommit_ratio,
            "workerNodeCPU": worker_node_cpu,
            "workerNodeMemory": worker_node_memory,
            "controlPlaneSchedulable": control_plane_schedulable,
        }
        async with self._get_client() as client:
            response = await client.post(
                f"/api/v1/assessments/{assessment_id}/cluster-requirements",
                json=request_body,
            )
            response.raise_for_status()
            result = response.json()
            log.info(
                "Successfully calculated cluster requirements for assessment %s",
                assessment_id,
            )
            return result

    @sanitize_exceptions
    async def get_complexity_estimation(
        self, assessment_id: str, cluster_id: str
    ) -> dict[str, Any]:
        """Get migration complexity estimation for a cluster.

        Args:
            assessment_id: The UUID of the assessment.
            cluster_id: The ID of the cluster to estimate complexity for.

        Returns:
            dict: Complexity estimation with complexityByDisk and complexityByOS arrays.
        """
        log.info(
            "Getting complexity estimation for assessment %s, cluster %s",
            assessment_id,
            cluster_id,
        )
        request_body = {"clusterId": cluster_id}
        async with self._get_client() as client:
            response = await client.post(
                f"/api/v1/assessments/{assessment_id}/complexity-estimation",
                json=request_body,
            )
            response.raise_for_status()
            result = response.json()
            log.info(
                "Successfully retrieved complexity estimation for assessment %s",
                assessment_id,
            )
            return result

    def _build_estimation_body(
        self,
        cluster_id: str,
        transfer_rate_mbps: Optional[int] = None,
        work_hours_per_day: Optional[int] = None,
        troubleshoot_mins_per_vm: Optional[int] = None,
        post_migration_engineers: Optional[int] = None,
    ) -> dict[str, Any]:
        """Build the request body for migration estimation endpoints.

        Constructs the JSON body with cluster ID and optional estimation
        parameters. Only includes the 'params' key when at least one
        optional parameter is provided.
        """
        param_fields = {
            "transfer_rate_mbps": transfer_rate_mbps,
            "work_hours_per_day": work_hours_per_day,
            "troubleshoot_mins_per_vm": troubleshoot_mins_per_vm,
            "post_migration_engineers": post_migration_engineers,
        }
        params = {k: v for k, v in param_fields.items() if v is not None}

        request_body: dict[str, Any] = {"clusterId": cluster_id}
        if params:
            request_body["params"] = params
        return request_body

    @sanitize_exceptions
    async def get_migration_estimation(
        self,
        assessment_id: str,
        cluster_id: str,
        transfer_rate_mbps: Optional[int] = None,
        work_hours_per_day: Optional[int] = None,
        troubleshoot_mins_per_vm: Optional[int] = None,
        post_migration_engineers: Optional[int] = None,
    ) -> dict[str, Any]:
        """Get migration time estimation for a cluster.

        Args:
            assessment_id: The UUID of the assessment.
            cluster_id: The ID of the cluster to estimate migration time for.
            transfer_rate_mbps: Network transfer rate in Mbps.
            work_hours_per_day: Working hours per day for migration.
            troubleshoot_mins_per_vm: Minutes allocated for troubleshooting per VM.
            post_migration_engineers: Number of engineers for post-migration tasks.

        Returns:
            dict: Migration estimation with time breakdown and context.
        """
        log.info(
            "Getting migration estimation for assessment %s, cluster %s",
            assessment_id,
            cluster_id,
        )
        request_body = self._build_estimation_body(
            cluster_id, transfer_rate_mbps, work_hours_per_day,
            troubleshoot_mins_per_vm, post_migration_engineers,
        )

        async with self._get_client() as client:
            response = await client.post(
                f"/api/v1/assessments/{assessment_id}/migration-estimation",
                json=request_body,
            )
            response.raise_for_status()
            result = response.json()
            log.info(
                "Successfully retrieved migration estimation for assessment %s",
                assessment_id,
            )
            return result

    @sanitize_exceptions
    async def get_migration_estimation_by_complexity(
        self,
        assessment_id: str,
        cluster_id: str,
        transfer_rate_mbps: Optional[int] = None,
        work_hours_per_day: Optional[int] = None,
        troubleshoot_mins_per_vm: Optional[int] = None,
        post_migration_engineers: Optional[int] = None,
    ) -> dict[str, Any]:
        """Get migration estimation grouped by complexity level.

        Args:
            assessment_id: The UUID of the assessment.
            cluster_id: The ID of the cluster to estimate migration time for.
            transfer_rate_mbps: Network transfer rate in Mbps.
            work_hours_per_day: Working hours per day for migration.
            troubleshoot_mins_per_vm: Minutes allocated for troubleshooting per VM.
            post_migration_engineers: Number of engineers for post-migration tasks.

        Returns:
            dict: Migration estimation grouped by OS+Disk combined complexity level.
        """
        log.info(
            "Getting migration estimation by complexity for assessment %s, cluster %s",
            assessment_id,
            cluster_id,
        )
        request_body = self._build_estimation_body(
            cluster_id, transfer_rate_mbps, work_hours_per_day,
            troubleshoot_mins_per_vm, post_migration_engineers,
        )

        async with self._get_client() as client:
            response = await client.post(
                f"/api/v1/assessments/{assessment_id}/migration-estimation/by-complexity",
                json=request_body,
            )
            response.raise_for_status()
            result = response.json()
            log.info(
                "Successfully retrieved migration estimation by complexity for assessment %s",
                assessment_id,
            )
            return result

    @sanitize_exceptions
    async def get_info(self) -> dict[str, Any]:
        """Get system information.

        Returns:
            dict: System info with gitCommit and versionName.
        """
        log.info("Getting system info")
        async with self._get_client() as client:
            response = await client.get("/api/v1/info")
            response.raise_for_status()
            result = response.json()
            log.info("Successfully retrieved system info")
            return result
