"""OMA Service MCP server implementation."""

import asyncio
import inspect
from functools import wraps
from typing import Any, Awaitable, Callable

from mcp.server.fastmcp import FastMCP
from oma_service_mcp.src.logger import log

from oma_service_mcp.utils.auth import get_access_token
from oma_service_mcp.src.settings import settings

# Import tool modules
from oma_service_mcp.src.tools import source_tools, assessment_tools


class OMAServiceMCPServer:
    """Main OMA Service MCP Server implementation.

    Provides read-only tools for interacting with the Migration Planner API
    to query sources, assessments, and cluster requirements.
    """

    def __init__(self) -> None:
        """Initialize the MCP server with migration planner tools."""
        try:
            use_stateless_http = settings.TRANSPORT == "streamable-http"

            self.mcp = FastMCP(
                "OMAService",
                host=settings.MCP_HOST,
                stateless_http=use_stateless_http,
            )

            self._get_access_token = lambda: get_access_token(self.mcp)
            self._register_mcp_tools()
            log.info("OMA Service MCP Server initialized successfully")
        except Exception as e:
            log.exception("Failed to initialize OMA Service MCP Server: %s", e)
            raise

    def _register_mcp_tools(self) -> None:
        """Register MCP tools for migration planner operations.

        Tools are organized by functional area:
        - Source management tools (list, get)
        - Assessment management tools (list, get, cluster requirements)
        """
        # Source tools
        self.mcp.tool()(self._wrap_tool(source_tools.list_sources))
        self.mcp.tool()(self._wrap_tool(source_tools.get_source))

        # Assessment tools
        self.mcp.tool()(self._wrap_tool(assessment_tools.list_assessments))
        self.mcp.tool()(self._wrap_tool(assessment_tools.get_assessment))
        self.mcp.tool()(self._wrap_tool(assessment_tools.calculate_cluster_requirements))

    def _wrap_tool(
        self, tool_func: Callable[..., Awaitable[Any]]
    ) -> Callable[..., Awaitable[Any]]:
        """Wrap a tool function to inject auth dependencies.

        Args:
            tool_func: The tool function to wrap.

        Returns:
            A wrapped async function that injects get_access_token.
        """

        @wraps(tool_func)
        async def wrapped(*args: Any, **kwargs: Any) -> Any:
            token = await asyncio.to_thread(self._get_access_token)
            return await tool_func(lambda: token, *args, **kwargs)

        # Get the original function signature
        sig = inspect.signature(tool_func)
        params = list(sig.parameters.values())

        # Remove the first parameter (auth token provider) since it's injected
        if len(params) >= 1:
            params = params[1:]

        # Create new signature with remaining parameters
        new_sig = sig.replace(parameters=params)
        wrapped.__signature__ = new_sig  # type: ignore[attr-defined]

        return wrapped

    async def list_tools(self) -> list[str]:
        """List all registered MCP tools (async)."""
        return [t.name for t in await self.mcp.list_tools()]

    def list_tools_sync(self) -> list[str]:
        """Synchronize tool listing with a safe sync wrapper."""
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.list_tools())

        raise RuntimeError(
            "list_tools_sync() cannot be called from within a running event loop. "
            "Use 'await list_tools()' in async contexts."
        )
