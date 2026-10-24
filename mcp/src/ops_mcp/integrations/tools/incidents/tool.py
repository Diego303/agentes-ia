"""Tool compleja: declarar un incidente. Tiene efectos y exige el scope ``ops:write``."""

# Sin `from __future__ import annotations`: ver ToolDeps.service_name_type.

from typing import Annotated, Literal

from mcp.server import MCPServer
from mcp.types import ToolAnnotations
from pydantic import Field

from ops_mcp.integrations.common import WRITE_SCOPE, ToolDeps, get_logger, logged_tool, require_scope
from ops_mcp.integrations.tools.incidents.models import Incident

NAME = "create_incident"
log = get_logger(__name__)


def register(server: MCPServer, deps: ToolDeps) -> None:
    ServiceName = deps.service_name_type()

    @server.tool(
        name=NAME,
        annotations=ToolAnnotations(
            read_only_hint=False, destructive_hint=False, idempotent_hint=False, open_world_hint=False
        ),
    )
    @logged_tool(NAME)
    async def create_incident(
        service: ServiceName,
        severity: Literal["SEV1", "SEV2", "SEV3"],
        summary: Annotated[str, Field(min_length=10, max_length=500)],
    ) -> Incident:
        """Declara un incidente. Tiene efectos: avisa a la guardia. Úsala solo cuando la guía de
        severidad lo justifique y el usuario lo haya pedido o aceptado."""
        await deps.service(service)
        created_by = require_scope(WRITE_SCOPE, auth_enabled=deps.auth_enabled)
        incident = await deps.incidents.create(service, severity, summary, created_by)
        log.info(
            "incident.created", extra={"incident": incident["id"], "service": service, "severity": severity}
        )
        return Incident(**incident)
