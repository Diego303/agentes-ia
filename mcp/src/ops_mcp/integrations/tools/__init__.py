"""Registro de las tools del servidor.

Una tool simple vive en su propio módulo (``service_status.py``); una compleja, en su carpeta
con sus piezas (``runbooks/``: índice, modelos y tool). Todas exponen ``register(server, deps)``.
Para añadir una, créala y añádela a ``TOOLS``.
"""

from __future__ import annotations

from collections.abc import Callable

from mcp.server import MCPServer

from ops_mcp.integrations.common import ToolDeps
from ops_mcp.integrations.tools import deployments, incidents, platform_overview, runbooks, service_status

TOOLS: tuple[Callable[[MCPServer, ToolDeps], None], ...] = (
    service_status.register,
    platform_overview.register,
    deployments.register,
    runbooks.register,
    incidents.register,
)


def register_tools(server: MCPServer, deps: ToolDeps) -> None:
    for register in TOOLS:
        register(server, deps)
