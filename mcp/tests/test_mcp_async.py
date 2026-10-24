"""Concurrencia y logging de las tools: varias llamadas a la vez no se esperan unas a otras."""

import asyncio
import json
import logging
import time

from mcp.server import MCPServer

from mcp import Client
from ops_mcp import IncidentStore, build_server
from ops_mcp.integrations.common import JsonFormatter, logged_tool
from ops_mcp.integrations.tools.runbooks import build_retriever

PARALLEL = 6
DELAY = 0.5


class SlowRetriever:
    """Recuperador síncrono y lento, como una librería que bloquea (CPU o HTTP síncrono)."""

    def __init__(self, delay: float) -> None:
        self._inner, self._delay = build_retriever(), delay

    def search(self, query: str, k: int):
        time.sleep(self._delay)
        return self._inner.search(query, k)


async def test_async_tools_run_concurrently_on_the_event_loop():
    server = MCPServer("prueba")

    @server.tool()
    @logged_tool("slow_io")
    async def slow_io(n: int) -> int:
        await asyncio.sleep(DELAY)  # una llamada de red lenta
        return n

    async with Client(server) as client:
        start = time.perf_counter()
        results = await asyncio.gather(*(client.call_tool("slow_io", {"n": i}) for i in range(PARALLEL)))
        elapsed = time.perf_counter() - start
    assert [r.structured_content["result"] for r in results] == list(range(PARALLEL))
    assert elapsed < DELAY * PARALLEL / 2  # en serie serían 3 s


async def test_blocking_search_goes_to_a_thread_and_does_not_freeze_the_server():
    async with Client(build_server(retriever=SlowRetriever(DELAY))) as client:
        start = time.perf_counter()
        searches = asyncio.gather(
            *(client.call_tool("search_runbooks", {"query": f"latencia alta {i}"}) for i in range(4))
        )
        await asyncio.sleep(0.05)  # las búsquedas ya están ocupando hilos
        status = await client.call_tool("get_service_status", {"service": "search-api"})
        status_at = time.perf_counter() - start
        results = await searches
        elapsed = time.perf_counter() - start
    assert not status.is_error
    assert status_at < DELAY  # respondió mientras las búsquedas seguían en marcha
    assert all(not r.is_error for r in results)
    assert elapsed < DELAY * 4 / 2  # cuatro búsquedas en paralelo, no 2 s seguidos


async def test_concurrent_incidents_get_unique_ids():
    incidents = IncidentStore()
    async with Client(build_server(incidents=incidents)) as client:
        results = await asyncio.gather(
            *(
                client.call_tool(
                    "create_incident",
                    {"service": "search-api", "severity": "SEV3", "summary": f"Prueba concurrente {i:02d}"},
                )
                for i in range(10)
            )
        )
    assert not any(r.is_error for r in results)
    assert len({i["id"] for i in incidents.items}) == 10


async def test_each_call_is_logged_and_unexpected_errors_are_hidden(caplog):
    server = MCPServer("prueba")

    @server.tool()
    @logged_tool("broken")
    async def broken() -> str:
        raise RuntimeError("cadena de conexión postgres://usuario:secreto@db")

    with caplog.at_level(logging.INFO, logger="ops_mcp"):
        async with Client(build_server()) as ok_client:
            await ok_client.call_tool("get_service_status", {"service": "search-api"})
            await ok_client.call_tool("get_service_status", {"service": "billing"})
        async with Client(server) as client:
            result = await client.call_tool("broken", {})

    calls = [r for r in caplog.records if r.getMessage() == "tool.call"]
    assert [(r.tool, r.outcome) for r in calls] == [
        ("get_service_status", "ok"),
        ("get_service_status", "tool_error"),
        ("broken", "error"),
    ]
    assert all(r.duration_ms >= 0 and len(r.call_id) == 12 for r in calls)
    assert result.is_error
    assert "secreto" not in result.content[0].text
    assert calls[-1].call_id in result.content[0].text  # referencia para buscar el log

    line = json.loads(JsonFormatter().format(calls[0]))
    assert line["msg"] == "tool.call" and line["tool"] == "get_service_status" and line["outcome"] == "ok"
