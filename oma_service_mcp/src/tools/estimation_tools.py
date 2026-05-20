"""Estimation tools for OMA Service MCP Server."""

import json
from typing import Annotated, Any, Callable, Optional

from pydantic import Field

from oma_service_mcp.src.service_client.migration_planner_client import MigrationPlannerClient
from oma_service_mcp.src.logger import log


async def _call_migration_estimation(
    get_access_token_func: Callable[[], str | None],
    client_method_name: str,
    assessment_id: str,
    cluster_id: str,
    transfer_rate_mbps: Optional[int],
    work_hours_per_day: Optional[int],
    troubleshoot_mins_per_vm: Optional[int],
    post_migration_engineers: Optional[int],
) -> str:
    """Shared implementation for migration estimation tool functions."""
    log.info(
        "Getting %s: assessment=%s, cluster=%s, "
        "transfer_rate=%s, work_hours=%s, troubleshoot_mins=%s, engineers=%s",
        client_method_name,
        assessment_id,
        cluster_id,
        transfer_rate_mbps,
        work_hours_per_day,
        troubleshoot_mins_per_vm,
        post_migration_engineers,
    )

    client = MigrationPlannerClient(get_access_token_func())
    method = getattr(client, client_method_name)
    result: dict[str, Any] = await method(
        assessment_id=assessment_id,
        cluster_id=cluster_id,
        transfer_rate_mbps=transfer_rate_mbps,
        work_hours_per_day=work_hours_per_day,
        troubleshoot_mins_per_vm=troubleshoot_mins_per_vm,
        post_migration_engineers=post_migration_engineers,
    )

    log.info("Successfully retrieved %s for assessment %s", client_method_name, assessment_id)
    return json.dumps(result, indent=2, default=str)


async def get_complexity_estimation(
    get_access_token_func: Callable[[], str | None],
    assessment_id: Annotated[
        str,
        Field(description="The UUID of the assessment to estimate complexity for."),
    ],
    cluster_id: Annotated[
        str,
        Field(description="The ID of the cluster within the assessment to estimate complexity for."),
    ],
) -> str:
    """Calculate migration complexity scores for VMs in a cluster.

    Computes a migration complexity score (1-4) for each VM in the specified cluster,
    broken down by disk size complexity and OS type complexity. Higher scores indicate
    more complex migrations. This helps prioritize which VMs to migrate first and
    estimate the effort involved.

    Prerequisites:
        - Valid assessment UUID (from list_assessments)
        - Valid cluster ID within that assessment's inventory

    Returns:
        str: A formatted string containing:
            - complexityByDisk: per-VM complexity scores based on disk size
            - complexityByOS: per-VM complexity scores based on operating system type
    """
    log.info(
        "Getting complexity estimation: assessment=%s, cluster=%s",
        assessment_id,
        cluster_id,
    )

    client = MigrationPlannerClient(get_access_token_func())
    result = await client.get_complexity_estimation(
        assessment_id=assessment_id,
        cluster_id=cluster_id,
    )

    log.info("Successfully retrieved complexity estimation for assessment %s", assessment_id)
    return json.dumps(result, indent=2, default=str)


async def get_migration_estimation(
    get_access_token_func: Callable[[], str | None],
    assessment_id: Annotated[
        str,
        Field(description="The UUID of the assessment to estimate migration time for."),
    ],
    cluster_id: Annotated[
        str,
        Field(description="The ID of the cluster within the assessment to estimate migration time for."),
    ],
    transfer_rate_mbps: Annotated[
        Optional[int],
        Field(
            default=None,
            description="Network transfer rate in Mbps for data migration. "
            "If not provided, the server uses a default value.",
        ),
    ] = None,
    work_hours_per_day: Annotated[
        Optional[int],
        Field(
            default=None,
            description="Number of working hours per day allocated for migration. "
            "If not provided, the server uses a default value.",
        ),
    ] = None,
    troubleshoot_mins_per_vm: Annotated[
        Optional[int],
        Field(
            default=None,
            description="Minutes allocated for troubleshooting per VM during migration. "
            "If not provided, the server uses a default value.",
        ),
    ] = None,
    post_migration_engineers: Annotated[
        Optional[int],
        Field(
            default=None,
            description="Number of engineers available for post-migration validation tasks. "
            "If not provided, the server uses a default value.",
        ),
    ] = None,
) -> str:
    """Calculate migration time estimation for a cluster using network-based and storage-offload schemas.

    Estimates how long a migration will take based on the cluster's VM inventory,
    considering network transfer rates, working hours, troubleshooting overhead,
    and post-migration staffing. Provides both a network-based transfer estimate
    and a storage-offload approach for comparison.

    Prerequisites:
        - Valid assessment UUID (from list_assessments)
        - Valid cluster ID within that assessment's inventory

    Returns:
        str: A formatted string containing:
            - Migration time estimation breakdown by transfer schema
            - Context parameters used for the calculation
            - Per-VM and total migration duration estimates
    """
    return await _call_migration_estimation(
        get_access_token_func, "get_migration_estimation",
        assessment_id, cluster_id,
        transfer_rate_mbps, work_hours_per_day,
        troubleshoot_mins_per_vm, post_migration_engineers,
    )


async def get_migration_estimation_by_complexity(
    get_access_token_func: Callable[[], str | None],
    assessment_id: Annotated[
        str,
        Field(description="The UUID of the assessment to estimate migration time for."),
    ],
    cluster_id: Annotated[
        str,
        Field(description="The ID of the cluster within the assessment to estimate migration time for."),
    ],
    transfer_rate_mbps: Annotated[
        Optional[int],
        Field(
            default=None,
            description="Network transfer rate in Mbps for data migration. "
            "If not provided, the server uses a default value.",
        ),
    ] = None,
    work_hours_per_day: Annotated[
        Optional[int],
        Field(
            default=None,
            description="Number of working hours per day allocated for migration. "
            "If not provided, the server uses a default value.",
        ),
    ] = None,
    troubleshoot_mins_per_vm: Annotated[
        Optional[int],
        Field(
            default=None,
            description="Minutes allocated for troubleshooting per VM during migration. "
            "If not provided, the server uses a default value.",
        ),
    ] = None,
    post_migration_engineers: Annotated[
        Optional[int],
        Field(
            default=None,
            description="Number of engineers available for post-migration validation tasks. "
            "If not provided, the server uses a default value.",
        ),
    ] = None,
) -> str:
    """Calculate migration time estimation grouped by OS and disk combined complexity level.

    Similar to get_migration_estimation, but groups the results by the combined
    complexity level (OS type + disk size). This provides a breakdown of migration
    effort by difficulty tier, helping teams plan migration waves by tackling
    simpler VMs first and allocating more resources for complex ones.

    Prerequisites:
        - Valid assessment UUID (from list_assessments)
        - Valid cluster ID within that assessment's inventory

    Returns:
        str: A formatted string containing:
            - Migration estimation grouped by combined complexity level
            - Per-complexity-tier VM counts and time estimates
            - Context parameters used for the calculation
    """
    return await _call_migration_estimation(
        get_access_token_func, "get_migration_estimation_by_complexity",
        assessment_id, cluster_id,
        transfer_rate_mbps, work_hours_per_day,
        troubleshoot_mins_per_vm, post_migration_engineers,
    )
