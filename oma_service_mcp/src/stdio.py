"""Stdio entry point for the OMA Service MCP Server.

Used when the MCP server is launched directly by an IDE (e.g., Cursor, Claude Code)
over stdin/stdout instead of running as a standalone HTTP/SSE server.
"""

from oma_service_mcp.src.logger import configure_logging
from oma_service_mcp.src.mcp import OMAServiceMCPServer

# Configure logging to file/stderr only (stdout is reserved for MCP protocol)
configure_logging()

server = OMAServiceMCPServer()


def main() -> None:
    """Run the MCP server over stdio transport."""
    server.mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
