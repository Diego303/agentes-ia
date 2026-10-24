"""Memoria de sesión: el historial de cada conversación con TTL y límite de sesiones.

El historial se trata como append-only: los bloques de razonamiento (thinking) de los
modelos actuales solo siguen siendo válidos si no se editan los turnos anteriores. Para
conversaciones muy largas, la compactación debe hacerla la API (compaction / context
editing), no el cliente reescribiendo mensajes.
"""

from __future__ import annotations

import time
from collections import OrderedDict
from typing import Any, Protocol


class SessionStore(Protocol):
    def get(self, session_id: str) -> dict[str, Any] | None: ...
    def put(self, session_id: str, state: dict[str, Any]) -> None: ...
    def delete(self, session_id: str) -> None: ...


class InMemorySessionStore:
    """Sesiones en memoria del proceso. Con varias réplicas hace falta un almacén externo
    (Redis, PostgreSQL) que implemente el mismo protocolo; ver architecture/adr/0006."""

    def __init__(self, ttl_seconds: float = 3600, max_sessions: int = 1000) -> None:
        self._ttl, self._max = ttl_seconds, max_sessions
        self._data: OrderedDict[str, tuple[float, dict[str, Any]]] = OrderedDict()

    def get(self, session_id: str) -> dict[str, Any] | None:
        item = self._data.get(session_id)
        if item is None:
            return None
        stored_at, state = item
        if time.monotonic() - stored_at > self._ttl:
            del self._data[session_id]
            return None
        self._data.move_to_end(session_id)
        return state

    def put(self, session_id: str, state: dict[str, Any]) -> None:
        self._data[session_id] = (time.monotonic(), state)
        self._data.move_to_end(session_id)
        while len(self._data) > self._max:
            self._data.popitem(last=False)

    def delete(self, session_id: str) -> None:
        self._data.pop(session_id, None)
