"""Tests for the MCP server initialization and tool registration."""

import pytest
from unittest.mock import patch, MagicMock


class TestOMAServiceMCPServer:
    @pytest.fixture
    def server(self):
        mock_settings_obj = MagicMock()
        mock_settings_obj.TRANSPORT = "streamable-http"
        mock_settings_obj.MCP_HOST = "0.0.0.0"

        with (
            patch("oma_service_mcp.src.mcp.settings", mock_settings_obj),
            patch("oma_service_mcp.src.mcp.FastMCP") as MockMCP,
            patch("oma_service_mcp.src.mcp.get_access_token"),
            patch("oma_service_mcp.src.settings.settings", mock_settings_obj),
        ):
            mock_mcp = MagicMock()
            mock_mcp.tool.return_value = lambda f: f
            MockMCP.return_value = mock_mcp

            from oma_service_mcp.src.mcp import OMAServiceMCPServer

            srv = OMAServiceMCPServer()
            srv._mock_mcp = mock_mcp
            yield srv

    def test_registers_all_tools(self, server):
        tool_calls = server._mock_mcp.tool.call_count
        assert tool_calls == 9

    def test_has_mcp_attribute(self, server):
        assert server.mcp is not None

    def test_wrap_tool_removes_first_param(self, server):
        import inspect

        async def sample_tool(get_access_token_func, param_a: str) -> str:
            return param_a

        wrapped = server._wrap_tool(sample_tool)
        sig = inspect.signature(wrapped)
        param_names = list(sig.parameters.keys())
        assert "get_access_token_func" not in param_names
        assert "param_a" in param_names
