"""Construcción del servidor MCP: dependencias, tools y ruta de salud."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mcp.server import MCPServer
from starlette.requests import Request
from starlette.responses import JSONResponse

from ops_mcp.integrations.common import OpsCatalog, ToolDeps
from ops_mcp.integrations.tools import register_tools
from ops_mcp.integrations.tools.incidents import IncidentStore
from ops_mcp.integrations.tools.runbooks import build_retriever

if TYPE_CHECKING:
    from mcp.server.auth.provider import TokenVerifier
    from mcp.server.auth.settings import AuthSettings

    from opsagent_rag import Retriever

NAME = "ops-mcp"
VERSION = "0.2.0"
INSTRUCTIONS = (
    "Herramientas de operaciones de plataforma. Consulta estado y despliegues antes de "
    "diagnosticar, busca el runbook aplicable antes de proponer una mitigación y crea "
    "incidentes solo cuando la guía de severidad lo justifique."
)


def build_server(
    *,
    catalog: OpsCatalog | None = None,
    retriever: Retriever | None = None,
    incidents: IncidentStore | None = None,
    token_verifier: TokenVerifier | None = None,
    auth: AuthSettings | None = None,
) -> MCPServer:
    """Servidor con todas las tools. Sin ``auth`` no exige token (stdio y desarrollo local)."""
    deps = ToolDeps(
        catalog=catalog or OpsCatalog.load(),
        retriever=retriever or build_retriever(),
        incidents=incidents if incidents is not None else IncidentStore(),
        auth_enabled=auth is not None,
    )
    server = MCPServer(
        NAME, version=VERSION, instructions=INSTRUCTIONS, token_verifier=token_verifier, auth=auth
    )
    register_tools(server, deps)

    @server.custom_route("/healthz", methods=["GET"])
    async def healthz(_: Request) -> JSONResponse:
        return JSONResponse({"status": "ok"})

    return server
