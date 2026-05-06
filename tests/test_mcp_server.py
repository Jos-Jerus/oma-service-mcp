"""Tests for the MCP server."""

import pytest
from unittest.mock import patch, MagicMock

from oma_service_mcp.src.mcp_server import OMAServiceMCPServer


class TestOMAServiceMCPServer:
    """Tests for OMAServiceMCPServer."""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for server initialization."""
        mock = MagicMock()
        mock.TRANSPORT = "stdio"
        mock.MCP_HOST = "localhost"
        return mock

    @pytest.fixture
    def server(self, mock_settings):
        """Create a server instance with mocked dependencies."""
        with patch("oma_service_mcp.src.mcp_server.settings", mock_settings):
            with patch("oma_service_mcp.src.mcp_server.get_access_token", return_value=None):
                return OMAServiceMCPServer()

    def test_server_initialization(self, server: OMAServiceMCPServer):
        """Test server initializes successfully."""
        assert server.mcp is not None

    def test_server_registers_all_tools(self, server: OMAServiceMCPServer):
        """Test server registers all expected tools."""
        tools = server.list_tools_sync()

        expected_tools = [
            "list_sources",
            "get_source",
            "list_assessments",
            "get_assessment",
            "calculate_cluster_requirements",
            "calculate_migration_estimation",
            "calculate_migration_complexity",
        ]

        assert len(tools) == len(expected_tools)
        for tool_name in expected_tools:
            assert tool_name in tools, f"Tool '{tool_name}' not registered"

    def test_server_registers_source_tools(self, server: OMAServiceMCPServer):
        """Test server registers source management tools."""
        tools = server.list_tools_sync()

        source_tools = ["list_sources", "get_source"]
        for tool_name in source_tools:
            assert tool_name in tools

    def test_server_registers_assessment_tools(self, server: OMAServiceMCPServer):
        """Test server registers assessment management tools."""
        tools = server.list_tools_sync()

        assessment_tools = [
            "list_assessments",
            "get_assessment",
            "calculate_cluster_requirements",
        ]
        for tool_name in assessment_tools:
            assert tool_name in tools

    def test_server_registers_migration_tools(self, server: OMAServiceMCPServer):
        """Test server registers migration estimation and complexity tools."""
        tools = server.list_tools_sync()

        migration_tools = [
            "calculate_migration_estimation",
            "calculate_migration_complexity",
        ]
        for tool_name in migration_tools:
            assert tool_name in tools


class TestToolWrapping:
    """Tests for the tool wrapping functionality."""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings for server initialization."""
        mock = MagicMock()
        mock.TRANSPORT = "stdio"
        mock.MCP_HOST = "localhost"
        return mock

    @pytest.fixture
    def server(self, mock_settings):
        """Create a server instance with mocked dependencies."""
        with patch("oma_service_mcp.src.mcp_server.settings", mock_settings):
            with patch("oma_service_mcp.src.mcp_server.get_access_token", return_value=None):
                return OMAServiceMCPServer()

    def test_wrap_tool_removes_auth_parameter(self, server: OMAServiceMCPServer):
        """Test that wrapped tools have auth parameter removed from signature."""
        import inspect
        from oma_service_mcp.src.tools import assessment_tools

        original_sig = inspect.signature(assessment_tools.calculate_migration_estimation)
        original_params = list(original_sig.parameters.keys())

        assert "get_access_token_func" in original_params

        wrapped = server._wrap_tool(assessment_tools.calculate_migration_estimation)
        wrapped_sig = inspect.signature(wrapped)
        wrapped_params = list(wrapped_sig.parameters.keys())

        assert "get_access_token_func" not in wrapped_params
        assert "assessment_id" in wrapped_params
        assert "cluster_id" in wrapped_params
