"""Cliente A2A del change advisor: descubre el agente por su Agent Card y le envía la petición."""

from __future__ import annotations

from typing import Any

import httpx
from a2a.client import A2ACardResolver, ClientConfig, create_client
from a2a.helpers import get_data_parts, get_message_text, new_data_message
from a2a.types import Role, SendMessageRequest, TaskState


class ChangeAdvisorError(RuntimeError):
    pass


class ChangeAdvisorClient:
    def __init__(self, base_url: str, token: str, *, http_client: httpx.AsyncClient | None = None) -> None:
        self._http = http_client or httpx.AsyncClient(timeout=15.0)
        self._http.headers["Authorization"] = f"Bearer {token}"
        self._base_url = base_url
        self._client = None

    async def _connect(self):
        if self._client is None:
            card = await A2ACardResolver(httpx_client=self._http, base_url=self._base_url).get_agent_card()
            config = ClientConfig(streaming=False, httpx_client=self._http)
            self._client = await create_client(agent=card, client_config=config)
        return self._client

    async def evaluate(self, change: dict[str, Any]) -> dict[str, Any]:
        """Devuelve el veredicto (``decision``, ``reasons``, ``conditions``, ``required_approvers``)."""
        client = await self._connect()
        message = new_data_message(change, media_type="application/json", role=Role.ROLE_USER)
        task = None
        async for event in client.send_message(SendMessageRequest(message=message)):
            if event.HasField("task"):
                task = event.task
        if task is None:
            raise ChangeAdvisorError("El change advisor no devolvió ninguna tarea.")
        if task.status.state != TaskState.TASK_STATE_COMPLETED:
            reason = get_message_text(task.status.message) if task.status.HasField("message") else ""
            raise ChangeAdvisorError(f"Petición rechazada por el change advisor: {reason}".strip())
        for artifact in task.artifacts:
            for data in get_data_parts(artifact.parts):
                if isinstance(data, dict) and "decision" in data:
                    return data
        raise ChangeAdvisorError("La tarea terminó sin artefacto de veredicto.")

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.close()
        await self._http.aclose()
