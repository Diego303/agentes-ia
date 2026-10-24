"""Servidor MCP de operaciones de plataforma (base para MCP servers propios; datos ficticios)."""

from ops_mcp.integrations.tools.incidents import IncidentStore
from ops_mcp.server import build_server

__all__ = ["IncidentStore", "build_server"]
