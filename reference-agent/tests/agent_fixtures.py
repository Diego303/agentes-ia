"""Construcción del agente para tests: modelo con guion, MCP en memoria y change advisor A2A en proceso."""

from datetime import UTC, datetime

import httpx

from change_advisor import ChangeAdvisorClient
from change_advisor.executor import ChangeAdvisorExecutor
from change_advisor.server import build_app as build_advisor
from ops_mcp import IncidentStore, build_server
from opsagent import Agent, Settings
from opsagent.testing import ScriptedLLM
from opsagent.tools import ToolRuntime

WEDNESDAY = datetime(2026, 10, 21, 11, 0, tzinfo=UTC)


def make_agent(script, settings: Settings | None = None):
    incidents = IncidentStore()
    app = build_advisor("http://advisor/", ["t"], executor=ChangeAdvisorExecutor(clock=lambda: WEDNESDAY))
    http = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://advisor/")
    advisor = ChangeAdvisorClient("http://advisor/", "t", http_client=http)
    llm = ScriptedLLM(script)
    agent = Agent(
        llm, lambda: ToolRuntime(build_server(incidents=incidents), advisor), settings or Settings()
    )
    return agent, llm, incidents


def assert_history_is_valid(messages):
    """Cada tool_use tiene su tool_result en el mensaje de usuario siguiente."""
    for i, msg in enumerate(messages):
        uses = {b["id"] for b in msg["content"] if msg["role"] == "assistant" and b["type"] == "tool_use"}
        if uses:
            following = messages[i + 1]
            assert following["role"] == "user"
            assert uses == {b["tool_use_id"] for b in following["content"] if b["type"] == "tool_result"}


def tool_results(request):
    return [b for b in request["messages"][-1]["content"] if b["type"] == "tool_result"]
