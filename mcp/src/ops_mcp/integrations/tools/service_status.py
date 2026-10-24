"""Tool simple: estado de un servicio."""

# Sin `from __future__ import annotations`: ver ToolDeps.service_name_type.

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from ops_mcp.integrations.common import ToolDeps, logged_tool
from ops_mcp.integrations.common.models import ServiceStatus

NAME = "get_service_status"


def register(server: MCPServer, deps: ToolDeps) -> None:
    ServiceName = deps.service_name_type()

    @server.tool(name=NAME, annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False))
    @logged_tool(NAME)
    async def get_service_status(service: ServiceName) -> ServiceStatus:
        """Estado actual de un servicio: salud, tasa de errores, latencia p95, réplicas y notas.
        Úsala primero ante cualquier pregunta sobre un servicio concreto."""
        data = await deps.service(service)
        return ServiceStatus.from_catalog(service, data, deps.catalog.observed_at)
