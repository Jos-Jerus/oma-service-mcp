"""Main entry point for the OMA Service MCP Server."""

import uvicorn
from oma_service_mcp.src.api import app, server
from oma_service_mcp.src.settings import settings
from oma_service_mcp.src.logger import log


def main() -> None:
    """Start the MCP server.

    Initializes the server and starts the uvicorn server.
    """
    try:
        log.info("Starting OMA Service MCP Server")
        log.info(
            "Configuration: TRANSPORT=%s, HOST=%s, PORT=%s, AUTH_TYPE=%s",
            settings.TRANSPORT,
            settings.MCP_HOST,
            settings.MCP_PORT,
            settings.AUTH_TYPE,
        )

        tool_names = server.list_tools_sync()
        log.info("Registered %s tools: %s", len(tool_names), ", ".join(tool_names))

        uvicorn.run(app, host=settings.MCP_HOST, port=settings.MCP_PORT)

    except KeyboardInterrupt:
        log.info("Received keyboard interrupt, shutting down")
    except Exception as e:
        log.error("Server failed to start: %s", e, exc_info=True)
        raise
    finally:
        log.info("OMA Service MCP server shutting down")


if __name__ == "__main__":
    main()
