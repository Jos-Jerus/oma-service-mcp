"""System information tools for OMA Service MCP Server."""

import json
from typing import Callable

from oma_service_mcp.src.service_client.migration_planner_client import MigrationPlannerClient
from oma_service_mcp.src.logger import log


async def get_system_info(get_access_token_func: Callable[[], str | None]) -> str:
    """Get system version information from the Migration Planner service.

    Retrieves basic system metadata including the git commit hash and version name
    of the running Migration Planner instance. Useful for verifying which version
    of the service is deployed.

    Returns:
        str: A formatted string containing:
            - gitCommit: The git commit hash of the deployed version
            - versionName: The human-readable version name
    """
    log.info("Retrieving system info")
    client = MigrationPlannerClient(get_access_token_func())
    result = await client.get_info()

    log.info("Successfully retrieved system info")
    return json.dumps(result, indent=2, default=str)
