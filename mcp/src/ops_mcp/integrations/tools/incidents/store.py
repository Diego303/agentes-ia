"""Almacén de incidentes en memoria; sustitúyelo por la API de tu herramienta de incidentes.

Varias llamadas a ``create_incident`` pueden llegar a la vez desde agentes distintos. El
``asyncio.Lock`` garantiza IDs únicos aunque la implementación real haga ``await`` (p. ej. una
petición HTTP) entre leer el siguiente ID y guardarlo.
"""

from __future__ import annotations

import asyncio
import itertools
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class IncidentStore:
    items: list[dict[str, Any]] = field(default_factory=list)
    _ids: itertools.count = field(default_factory=lambda: itertools.count(1001))
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def create(self, service: str, severity: str, summary: str, created_by: str) -> dict[str, Any]:
        async with self._lock:
            incident = {
                "id": f"INC-{next(self._ids)}",
                "service": service,
                "severity": severity,
                "summary": summary,
                "status": "open",
                "created_by": created_by,
                "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
            }
            self.items.append(incident)
            return incident
