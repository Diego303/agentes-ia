"""Cableado del agente a partir de ``Settings``: lo comparten la API y la CLI."""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from change_advisor import ChangeAdvisorClient
from change_advisor.server import build_app as build_advisor_app
from opsagent.agent import Agent
from opsagent.config import Settings
from opsagent.llm import make_llm_client
from opsagent.tools import McpConnection, ToolRuntime

_LOCAL_ADVISOR_URL = "http://change-advisor.local/"
_LOCAL_ADVISOR_TOKEN = "local-dev"  # noqa: S105 - solo para el advisor servido en el mismo proceso


def make_advisor(settings: Settings) -> ChangeAdvisorClient:
    """Advisor remoto por A2A, o la misma app A2A servida en el proceso (sin red) en local."""
    if settings.advisor_url:
        return ChangeAdvisorClient(settings.advisor_url, settings.advisor_token or "")
    app = build_advisor_app(_LOCAL_ADVISOR_URL, [_LOCAL_ADVISOR_TOKEN])
    http = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url=_LOCAL_ADVISOR_URL)
    return ChangeAdvisorClient(_LOCAL_ADVISOR_URL, _LOCAL_ADVISOR_TOKEN, http_client=http)


@dataclass
class Runtime:
    agent: Agent
    mcp: McpConnection
    advisor: ChangeAdvisorClient

    async def aclose(self) -> None:
        await self.advisor.aclose()
        await self.mcp.aclose()


def build_runtime(settings: Settings) -> Runtime:
    mcp, advisor = McpConnection(settings), make_advisor(settings)
    agent = Agent(make_llm_client(settings), lambda: ToolRuntime(mcp.target(), advisor), settings)
    return Runtime(agent, mcp, advisor)
