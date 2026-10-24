"""App ASGI de Streamable HTTP con la configuración de despliegue (la usan el arranque y los tests)."""

from __future__ import annotations

from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from starlette.applications import Starlette


def build_http_app(server: MCPServer, allowed_hosts: list[str]) -> Starlette:
    """Streamable HTTP sin estado y con protección de DNS rebinding por cabecera ``Host``.

    ``allowed_hosts`` admite comodín de puerto (``ops-mcp:*``); en Kubernetes incluye el
    nombre corto del Service y su FQDN.
    """
    return server.streamable_http_app(
        stateless_http=True,  # sin sesión en memoria: cualquier réplica atiende cualquier petición
        json_response=True,
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=True, allowed_hosts=allowed_hosts, allowed_origins=[]
        ),
    )
