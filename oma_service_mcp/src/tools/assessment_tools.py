"""Assessment management tools for OMA Service MCP Server."""

import json
from typing import Annotated, Callable, Optional

from pydantic import Field

from oma_service_mcp.src.service_client.migration_planner_client import MigrationPlannerClient
from oma_service_mcp.src.logger import log


async def list_assessments(
    get_access_token_func: Callable[[], str | None],
    source_id: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Optional source UUID to filter assessments by. "
            "If not provided, all assessments are returned.",
        ),
    ] = None,
) -> str:
    """List all assessments, optionally filtered by source.

    Retrieves a summary of all assessments in the Migration Planner. Assessments represent
    migration readiness evaluations of VMware environments, created either from agent-collected
    inventory, manual inventory upload, or RVTools file import.

    Returns:
        str: A formatted list of assessments, each containing:
            - Assessment name and ID
            - Source type (inventory, rvtools, source)
            - Associated source ID (if any)
            - Number of snapshots
            - Creation timestamp
            - Per-snapshot inventory: VM counts, clusters, resources
    """
    log.info("Retrieving list of assessments (source_id: %s)", source_id)
    client = MigrationPlannerClient(get_access_token_func())
    assessments = await client.list_assessments(source_id=source_id)

    if not assessments:
        return "No assessments found."

    log.info("Successfully retrieved %d assessments", len(assessments))
    return json.dumps(assessments, indent=2, default=str)


async def get_assessment(
    get_access_token_func: Callable[[], str | None],
    assessment_id: Annotated[
        str,
        Field(description="The UUID of the assessment to retrieve detailed information for."),
    ],
) -> str:
    """Get detailed information about a specific assessment.

    Retrieves comprehensive assessment data including all snapshots with their
    inventory information. Each snapshot contains the full inventory state at a
    point in time, including VM counts, resource breakdown, infrastructure details,
    and migration readiness.

    Prerequisites:
        - Valid assessment UUID (from list_assessments)

    Returns:
        str: A formatted string containing detailed assessment information including:
            - Assessment metadata (name, ID, source type, owner)
            - Snapshots with timestamps
            - Per-snapshot inventory: VM counts, clusters, resources
    """
    log.info("Retrieving assessment %s", assessment_id)
    client = MigrationPlannerClient(get_access_token_func())
    assessment = await client.get_assessment(assessment_id)

    log.info("Successfully retrieved assessment %s", assessment_id)
    return json.dumps(assessment, indent=2, default=str)


async def calculate_cluster_requirements(
    get_access_token_func: Callable[[], str | None],
    assessment_id: Annotated[
        str,
        Field(description="The UUID of the assessment to calculate cluster requirements for."),
    ],
    cluster_id: Annotated[
        str,
        Field(description="The ID of the cluster within the assessment to size."),
    ],
    cpu_overcommit_ratio: Annotated[
        str,
        Field(
            default="1:4",
            description="CPU over-commit ratio. Valid values: '1:1', '1:2', '1:4', '1:6'. "
            "Default is '1:4'.",
        ),
    ] = "1:4",
    memory_overcommit_ratio: Annotated[
        str,
        Field(
            default="1:2",
            description="Memory over-commit ratio. Valid values: '1:1', '1:2', '1:4'. "
            "Default is '1:2'.",
        ),
    ] = "1:2",
    worker_node_cpu: Annotated[
        int,
        Field(
            default=16,
            description="CPU cores per worker node (2-200). Default is 16.",
        ),
    ] = 16,
    worker_node_memory: Annotated[
        int,
        Field(
            default=64,
            description="Memory (GB) per worker node (4-512). Default is 64.",
        ),
    ] = 64,
    control_plane_schedulable: Annotated[
        bool,
        Field(
            default=False,
            description="Whether to allow workload scheduling on control plane nodes. Default is False.",
        ),
    ] = False,
) -> str:
    """Calculate OpenShift cluster sizing requirements for migrating VMs from an assessment.

    Given an assessment and cluster parameters, computes the required OpenShift cluster
    sizing including number of worker/control plane nodes, total resources, and resource
    consumption. This helps plan the target OpenShift infrastructure needed to host
    the migrated VM workloads.

    Prerequisites:
        - Valid assessment UUID (from list_assessments)
        - Valid cluster ID within that assessment's inventory

    Returns:
        str: A formatted string containing:
            - Cluster sizing: total nodes, worker nodes, control plane nodes, total CPU/memory
            - Resource consumption: CPU and memory requested, limits, over-commit ratios
            - Inventory totals: total VMs, CPU, and memory from the source cluster
    """
    log.info(
        "Calculating cluster requirements: assessment=%s, cluster=%s, "
        "cpu_ratio=%s, mem_ratio=%s, worker_cpu=%d, worker_mem=%d, cp_schedulable=%s",
        assessment_id,
        cluster_id,
        cpu_overcommit_ratio,
        memory_overcommit_ratio,
        worker_node_cpu,
        worker_node_memory,
        control_plane_schedulable,
    )

    client = MigrationPlannerClient(get_access_token_func())
    result = await client.calculate_cluster_requirements(
        assessment_id=assessment_id,
        cluster_id=cluster_id,
        cpu_overcommit_ratio=cpu_overcommit_ratio,
        memory_overcommit_ratio=memory_overcommit_ratio,
        worker_node_cpu=worker_node_cpu,
        worker_node_memory=worker_node_memory,
        control_plane_schedulable=control_plane_schedulable,
    )

    log.info("Successfully calculated cluster requirements for assessment %s", assessment_id)
    return json.dumps(result, indent=2, default=str)
