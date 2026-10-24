"""Runtime de tools: las del servidor MCP más la delegación A2A al change advisor."""

from __future__ import annotations

import json
import sys
from contextlib import AsyncExitStack
from dataclasses import dataclass
from typing import Any

import httpx2
from mcp.client.streamable_http import streamable_http_client

from change_advisor import ChangeAdvisorClient
from change_advisor.client import ChangeAdvisorError
from mcp import Client, StdioServerParameters
from opsagent.config import Settings

ADVISOR_TOOL = "consult_change_advisor"
ADVISOR_TOOL_DEF: dict[str, Any] = {
    "name": ADVISOR_TOOL,
    "description": (
        "Consulta al change advisor (agente del equipo de gestión de cambios, vía A2A) si una acción "
        "en producción está permitida. Úsala antes de recomendar un rollback, reinicio, escalado, cambio "
        "de configuración o despliegue, y transmite su decisión y condiciones."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "service": {"type": "string"},
            "action": {"type": "string", "enum": ["rollback", "restart", "scale", "config_change", "deploy"]},
            "environment": {"type": "string", "enum": ["production", "staging"]},
            "incident_severity": {"type": "string", "enum": ["SEV1", "SEV2", "SEV3", "none"]},
            "reason": {"type": "string"},
        },
        "required": ["service", "action", "incident_severity"],
        "additionalProperties": False,
    },
}


@dataclass(frozen=True)
class ToolOutcome:
    text: str
    is_error: bool = False


class McpConnection:
    """Destino MCP: URL con token (despliegue) o subproceso stdio de ops-mcp (desarrollo local).

    El cliente HTTP vive lo que el proceso (pool de conexiones); el transporte es nuevo en
    cada ejecución porque el servidor es stateless.
    """

    def __init__(self, settings: Settings) -> None:
        self._url = settings.mcp_url
        self._http: httpx2.AsyncClient | None = None
        if self._url:
            headers = {"Authorization": f"Bearer {settings.mcp_token}"} if settings.mcp_token else {}
            self._http = httpx2.AsyncClient(headers=headers, timeout=httpx2.Timeout(30.0, read=300.0))

    def target(self) -> Any:
        if self._url and self._http is not None:
            return streamable_http_client(self._url, http_client=self._http)
        return StdioServerParameters(command=sys.executable, args=["-m", "ops_mcp", "--stdio"])

    async def aclose(self) -> None:
        if self._http is not None:
            await self._http.aclose()


class ToolRuntime:
    """Abre la conexión MCP durante una ejecución del agente y enruta cada llamada."""

    def __init__(self, mcp: Any, advisor: ChangeAdvisorClient | None) -> None:
        self._mcp_target, self._advisor = mcp, advisor
        self._stack = AsyncExitStack()
        self._mcp: Client | None = None
        self.definitions: list[dict[str, Any]] = []
        self.mcp_tools: set[str] = set()

    async def __aenter__(self) -> ToolRuntime:
        self._mcp = await self._stack.enter_async_context(Client(self._mcp_target))
        listed = await self._mcp.list_tools()
        for tool in listed.tools:
            self.mcp_tools.add(tool.name)
            self.definitions.append(
                {"name": tool.name, "description": tool.description or "", "input_schema": tool.input_schema}
            )
        if self._advisor is not None:
            self.definitions.append(ADVISOR_TOOL_DEF)
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self._stack.aclose()

    def tool_type(self, name: str) -> str:
        return "extension" if name in self.mcp_tools or name == ADVISOR_TOOL else "function"

    async def call(self, name: str, arguments: dict[str, Any]) -> ToolOutcome:
        if name == ADVISOR_TOOL and self._advisor is not None:
            change = {k: v for k, v in arguments.items() if v != "none"}
            try:
                verdict = await self._advisor.evaluate(change)
            except ChangeAdvisorError as exc:
                return ToolOutcome(str(exc), is_error=True)
            return ToolOutcome(json.dumps(verdict, ensure_ascii=False))
        if name not in self.mcp_tools or self._mcp is None:
            return ToolOutcome(f"Tool desconocida: {name}", is_error=True)
        result = await self._mcp.call_tool(name, arguments)
        if result.structured_content is not None:
            text = json.dumps(result.structured_content, ensure_ascii=False)
        else:
            text = "\n".join(getattr(block, "text", "") for block in result.content)
        return ToolOutcome(text, is_error=bool(result.is_error))
