# OMA Service MCP

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that exposes migration planning tools for the OpenShift Migration Advisor (OMA). It acts as a bridge between AI assistants (Claude, Llama via lightspeed-stack, IDE integrations) and the [Migration Planner API](https://github.com/kubev2v/migration-planner), providing read-only access to sources, assessments, cluster sizing, migration estimation, and complexity analysis.

## Architecture

```
+-----------------+       +------------------+       +---------------------+
|  AI Assistant   | MCP   | OMA Service MCP  | HTTP  | Migration Planner   |
|  (Claude, IDE,  |------>|  (this service)  |------>| API                 |
|   Llama Stack)  |       |  Port 8000       |       | /api/v1/...         |
+-----------------+       +------------------+       +---------------------+
```

The server supports three transport modes:

| Transport | Use case | Entry point |
|-----------|----------|-------------|
| `streamable-http` | Production with lightspeed-stack | `oma_service_mcp.src.main` |
| `sse` | Server-Sent Events for compatible clients | `oma_service_mcp.src.main` (set `TRANSPORT=sse`) |
| `stdio` | IDE integration (Cursor, Claude Code) | `oma_service_mcp.src.stdio` |

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `list_sources` | List all migration sources (discovered vSphere environments) |
| `get_source` | Get detailed info for a specific source (inventory, VMs, clusters) |
| `list_assessments` | List all assessments, optionally filtered by source |
| `get_assessment` | Get detailed assessment data including snapshots and inventory |
| `calculate_cluster_requirements` | Calculate OpenShift cluster sizing for migrating VMs |
| `calculate_migration_estimation` | Estimate migration duration with phase breakdown |
| `calculate_migration_complexity` | Analyze migration complexity by disk size and OS type |

## Prerequisites

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) (package manager)
- Access to a running Migration Planner API instance

## Quick Start

```bash
# Install dependencies
make sync

# Copy and configure environment
cp .env.example .env
# Edit .env to set MIGRATION_PLANNER_URL to your instance

# Run the server (HTTP, port 8000)
make run-local

# Or run over stdio (for IDE integration)
make run-stdio
```

## Configuration

All configuration is via environment variables (or `.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_HOST` | `0.0.0.0` | Host address for the MCP server |
| `MCP_PORT` | `8000` | Port number (1024-65535) |
| `TRANSPORT` | `streamable-http` | Transport protocol: `streamable-http` or `sse` |
| `MIGRATION_PLANNER_URL` | `http://localhost:7443` | Migration Planner API base URL |
| `AUTH_TYPE` | `none` | Authentication: `none` (local dev) or `forwarded` (production) |
| `LOGGING_LEVEL` | `INFO` | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `LOG_TO_FILE` | `true` | Write logs to `oma-service-mcp.log` (set `false` in containers) |
| `LOGGER_NAME` | `oma-service-mcp` | Logger name |

## Authentication

Two modes are supported:

- **`none`** -- No auth headers sent to Migration Planner. Use for local development.
- **`forwarded`** -- Forwards the `Authorization: Bearer <token>` header from the incoming request to the Migration Planner API. Used in production with lightspeed-stack, which resolves auth from secret files, Kubernetes tokens, or client-provided tokens.

See `examples/lightspeed-stack.yaml` for integration examples.

## IDE Integration

### Cursor

A `.cursor/mcp.json` is included. Adjust the `MIGRATION_PLANNER_URL` in it to point to your local Migration Planner instance:

```json
{
  "mcpServers": {
    "oma-service-mcp": {
      "command": "uv",
      "args": ["run", "python", "-m", "oma_service_mcp.src.stdio"],
      "cwd": "/path/to/oma-service-mcp",
      "env": {
        "MIGRATION_PLANNER_URL": "http://localhost:7443",
        "AUTH_TYPE": "none"
      }
    }
  }
}
```

### Claude Code

Add to your Claude Code MCP settings:

```json
{
  "mcpServers": {
    "oma-service-mcp": {
      "command": "uv",
      "args": ["run", "python", "-m", "oma_service_mcp.src.stdio"],
      "cwd": "/path/to/oma-service-mcp",
      "env": {
        "MIGRATION_PLANNER_URL": "http://localhost:7443",
        "AUTH_TYPE": "none"
      }
    }
  }
}
```

## Running on OpenShift

### Build and push the container image

```bash
make build                  # Build with podman
make push                   # Push to quay.io/oma/oma-service-mcp
```

### Deploy

```bash
# Deploy to current namespace
make deploy

# Or build, push, and deploy in one step
make deploy-image
```

The deployment includes:
- **ConfigMap** (`deploy/openshift/configmap.yaml`) -- Migration Planner URL and auth type
- **Secret** (`deploy/openshift/secret.yaml`) -- Optional token storage
- **Deployment** with health probes on `/health`
- **Service** (ClusterIP on port 8000)
- **Route** with TLS edge termination

### Operations

```bash
make deploy-status          # Check deployment status
make deploy-logs            # Tail pod logs
make deploy-set-config KEY=migration-planner-url VALUE=http://host:7443
make undeploy               # Remove from OpenShift
```

## Development

```bash
make sync                   # Install dependencies
make test                   # Run tests
make test-coverage          # Run tests with HTML coverage report
make lint                   # Run ruff linter
make typecheck              # Run mypy type checker
make format                 # Auto-format code
make verify                 # Run all checks (lint + typecheck + test)
```

## Project Structure

```
oma_service_mcp/
  src/
    main.py                 # HTTP server entry point (uvicorn)
    stdio.py                # Stdio transport entry point (IDE integration)
    api.py                  # Starlette app setup, health endpoint
    mcp_server.py           # MCP server class, tool registration, auth wrapping
    settings.py             # Pydantic settings from env vars
    logger.py               # Logging with sensitive data redaction
    tools/
      source_tools.py       # list_sources, get_source
      assessment_tools.py   # list/get assessments, cluster sizing, estimation, complexity
    service_client/
      migration_planner_client.py   # Async HTTP client for Migration Planner API
      exceptions.py                 # Error handling and exception sanitization
  utils/
    auth.py                 # Bearer token extraction and forwarding
tests/
  conftest.py               # Shared fixtures
  test_assessment_tools.py   # Assessment tool tests
  test_source_tools.py       # Source tool tests
  test_migration_planner_client.py  # API client tests
  test_mcp_server.py         # Server initialization and tool registration tests
deploy/openshift/            # OpenShift manifests (Deployment, Service, Route, ConfigMap, Secret)
examples/
  lightspeed-stack.yaml      # lightspeed-stack integration examples
```
