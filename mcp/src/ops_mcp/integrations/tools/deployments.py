"""Tool simple: últimos despliegues de un servicio."""

# Sin `from __future__ import annotations`: ver ToolDeps.service_name_type.

from typing import Annotated

from mcp.server import MCPServer
from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field

from ops_mcp.integrations.common import ToolDeps, logged_tool

NAME = "list_recent_deployments"


class Deployment(BaseModel):
    version: str
    deployed_at: str
    author: str
    change: str


def register(server: MCPServer, deps: ToolDeps) -> None:
    ServiceName = deps.service_name_type()

    @server.tool(name=NAME, annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False))
    @logged_tool(NAME)
    async def list_recent_deployments(
        service: ServiceName, limit: Annotated[int, Field(ge=1, le=10)] = 3
    ) -> list[Deployment]:
        """Últimos despliegues de un servicio, del más reciente al más antiguo. Úsala para
        comprobar si un cambio reciente coincide con el inicio de un problema."""
        await deps.service(service)
        return [Deployment(**d) for d in await deps.catalog.recent_deployments(service, limit)]
