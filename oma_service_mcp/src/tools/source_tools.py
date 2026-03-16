"""Source management tools for OMA Service MCP Server."""

import json
from typing import Annotated, Callable

from pydantic import Field

from oma_service_mcp.src.service_client.migration_planner_client import MigrationPlannerClient
from oma_service_mcp.src.logger import log


async def list_sources(get_access_token_func: Callable[[], str | None]) -> str:
    """List all migration sources.

    Retrieves a summary of all sources registered in the Migration Planner. Each source
    represents a vSphere environment that has been discovered by the migration planner agent.
    Sources contain inventory data about VMs, infrastructure, and clusters.

    Returns:
        str: A formatted list of sources, each containing:
            - Source name and ID
            - Agent status and version
            - Whether it is on-premises
            - Creation and last update timestamps
    """
    log.info("Retrieving list of all sources")
    client = MigrationPlannerClient(get_access_token_func())
    sources = await client.list_sources()

    if not sources:
        return "No sources found."

    log.info("Successfully retrieved %d sources", len(sources))
    return json.dumps(sources, indent=2, default=str)


async def get_source(
    get_access_token_func: Callable[[], str | None],
    source_id: Annotated[
        str,
        Field(description="The UUID of the source to retrieve detailed information for."),
    ],
) -> str:
    """Get detailed information about a specific migration source.

    Retrieves comprehensive information about a source including its full inventory data:
    VM counts, resource breakdown (CPU, RAM, disk), infrastructure details (hosts, networks,
    datastores), migration readiness assessment, and OS distribution.

    Prerequisites:
        - Valid source UUID (from list_sources)

    Returns:
        str: A formatted string containing detailed source information including:
            - Source name, ID, and metadata
            - Agent connection status
            - Inventory summary per cluster: VM counts, migratable VMs, resource totals
            - Infrastructure: hosts, networks, datastores
            - Migration issues and warnings
    """
    log.info("Retrieving source information for source_id: %s", source_id)
    client = MigrationPlannerClient(get_access_token_func())
    source = await client.get_source(source_id)

    log.info("Successfully retrieved source %s", source_id)
    return json.dumps(source, indent=2, default=str)
