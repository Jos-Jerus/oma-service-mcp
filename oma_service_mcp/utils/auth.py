"""Authentication utilities for OMA Service MCP Server.

Supports two authentication modes:
- 'none': No authentication (local/dev environments)
- 'forwarded': Forward Authorization header from incoming request (lightspeed-stack)

When using 'forwarded' mode with lightspeed-stack, the stack resolves auth from
one of three sources (configured via authorization_headers in lightspeed-stack.yaml):
  1. Secret file: reads a token from a mounted file path
  2. Kubernetes: forwards the authenticated user's k8s service-account token
  3. Client-provided: extracts from the MCP-HEADERS JSON header sent by clients

In all cases, lightspeed-stack sends the resolved token as a standard
Authorization: Bearer <token> header in requests to this MCP server.
"""

from typing import Any

from oma_service_mcp.src.logger import log
from oma_service_mcp.src.settings import get_setting


def _extract_bearer_from_request(mcp: Any) -> str | None:
    """Extract Bearer token from the incoming request's Authorization header.

    When lightspeed-stack sends requests to this MCP server, it includes the
    resolved Authorization header (from secret files, kubernetes tokens, or
    client-provided tokens via MCP-HEADERS).

    Args:
        mcp: The FastMCP instance to get request context from.

    Returns:
        str | None: The bearer token if found, None otherwise.
    """
    try:
        context = mcp.get_context()
    except Exception:
        return None

    if context and context.request_context:
        request = context.request_context.request
        if request is not None:
            header = request.headers.get("Authorization")
            if header is not None:
                parts = header.split()
                if len(parts) == 2 and parts[0].lower() == "bearer":
                    log.debug("Found bearer token in Authorization header")
                    return parts[1]
    return None


def get_access_token(mcp: Any) -> str | None:
    """Retrieve the access token based on the configured auth type.

    Supports two modes:
    - 'none': Returns None (no auth needed, for local dev)
    - 'forwarded': Extracts and forwards the Authorization header from the
      incoming request. This is the mode to use with lightspeed-stack, which
      resolves auth and sends it in the Authorization header.

    Args:
        mcp: The FastMCP instance to get request context from.

    Returns:
        str | None: The access token, or None if auth_type is 'none'.

    Raises:
        RuntimeError: If auth_type is 'forwarded' but no token is found.
    """
    auth_type = get_setting("AUTH_TYPE")
    log.debug("Getting access token for auth_type: %s", auth_type)

    if auth_type == "none":
        return None

    if auth_type == "forwarded":
        token = _extract_bearer_from_request(mcp)
        if not token:
            raise RuntimeError(
                "AUTH_TYPE is 'forwarded' but no Authorization Bearer header found "
                "in the incoming request. Ensure lightspeed-stack is configured with "
                "authorization_headers for this MCP server."
            )
        return token

    raise RuntimeError(f"Unknown AUTH_TYPE: {auth_type}")
