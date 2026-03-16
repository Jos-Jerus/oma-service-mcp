FROM registry.access.redhat.com/ubi9/python-311:9.7-1766406230

ENV APP_HOME=/opt/app-root/src
WORKDIR ${APP_HOME}

USER 0

RUN pip install uv

COPY pyproject.toml .
COPY uv.lock .
RUN uv sync

COPY oma_service_mcp ./oma_service_mcp/

RUN chown -R 1001:0 ${APP_HOME}

USER 1001

# Disable file logging in containers - only log to stderr
ENV LOG_TO_FILE=false

EXPOSE 8000

LABEL com.redhat.component="oma-service-mcp" \
      name="oma-service-mcp" \
      description="MCP server for Migration Planner Service" \
      io.k8s.description="MCP server for Migration Planner Service" \
      distribution-scope="public" \
      release="main" \
      version="latest" \
      vendor="Red Hat, Inc."

CMD ["uv", "--cache-dir", "/tmp/uv-cache", "run", "python", "-m", "oma_service_mcp.src.main"]
