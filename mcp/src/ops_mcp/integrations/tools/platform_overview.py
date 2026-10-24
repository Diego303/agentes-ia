"""Tool simple: resumen de toda la plataforma, con los servicios con problemas primero.

Ejemplo de consulta en abanico: pide el estado de cada servicio a la vez (``gather_limited``)
en lugar de uno detrás de otro. Con fuentes reales (una llamada HTTP por servicio) el tiempo
total es el de la llamada más lenta, no la suma.
"""

from mcp.server import MCPServer
from mcp.types import ToolAnnotations
from pydantic import BaseModel

from ops_mcp.integrations.common import ToolDeps, gather_limited, logged_tool
from ops_mcp.integrations.common.models import ServiceStatus

NAME = "get_platform_overview"
_SEVERITY = {"down": 0, "degraded": 1, "healthy": 2}


class PlatformOverview(BaseModel):
    observed_at: str
    unhealthy: int
    services: list[ServiceStatus]


def register(server: MCPServer, deps: ToolDeps) -> None:
    @server.tool(name=NAME, annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False))
    @logged_tool(NAME)
    async def get_platform_overview() -> PlatformOverview:
        """Estado de todos los servicios, primero los caídos y degradados y, dentro de cada
        grupo, los más críticos. Úsala cuando la pregunta no nombra un servicio ("¿qué está
        fallando?", "¿cómo está la plataforma?")."""
        names = deps.catalog.service_names()
        observed_at = deps.catalog.observed_at

        async def status(name: str) -> ServiceStatus:
            return ServiceStatus.from_catalog(name, await deps.service(name), observed_at)

        services = await gather_limited([lambda n=name: status(n) for name in names], limit=8)
        services.sort(key=lambda s: (_SEVERITY[s.status], s.tier, s.service))
        return PlatformOverview(
            observed_at=observed_at,
            unhealthy=sum(s.status != "healthy" for s in services),
            services=services,
        )
