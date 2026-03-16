"""Application setup for the OMA Service MCP server.

Initializes the app and sets up the MCP server
with appropriate transport protocols.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from oma_service_mcp.src.mcp import OMAServiceMCPServer
from oma_service_mcp.src.settings import settings
from oma_service_mcp.src.logger import log, configure_logging

# Ensure logging is configured before any module-level log usage
configure_logging()

# Initialize the MCP server
server = OMAServiceMCPServer()

# Choose the appropriate transport protocol based on settings
if settings.TRANSPORT == "streamable-http":
    app = server.mcp.streamable_http_app()
    log.info("Using StreamableHTTP transport (stateless)")
else:
    app = server.mcp.sse_app()
    log.info("Using SSE transport (stateful)")


# Health endpoint for readiness/liveness probes (used by OpenShift and docker-compose)
async def health(request: Request) -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse({"status": "ok"})


# Add health routes to the Starlette app
app.routes.append(Route("/health", health, methods=["GET"]))
app.routes.append(Route("/", health, methods=["GET"]))
