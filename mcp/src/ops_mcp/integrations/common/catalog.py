"""Catálogo de servicios y despliegues que consultan las tools.

Los datos son ficticios y se cargan una vez al arrancar. La interfaz es asíncrona a propósito:
en un sistema real cada método llamaría a su fuente (Prometheus, el CD, el CMDB) con un
cliente asíncrono, y las tools no cambiarían.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

RESOURCES_DIR = Path(__file__).resolve().parents[2] / "resources"


@dataclass(frozen=True)
class OpsCatalog:
    observed_at: str
    services: dict[str, dict[str, Any]]
    deployments: dict[str, list[dict[str, Any]]]

    @classmethod
    def load(cls, resources_dir: Path = RESOURCES_DIR) -> OpsCatalog:
        services = json.loads((resources_dir / "services.json").read_text(encoding="utf-8"))
        deployments = json.loads((resources_dir / "deployments.json").read_text(encoding="utf-8"))
        return cls(services["observed_at"], services["services"], deployments)

    def service_names(self) -> list[str]:
        return sorted(self.services)

    async def get_service(self, name: str) -> dict[str, Any] | None:
        return self.services.get(name)

    async def recent_deployments(self, name: str, limit: int) -> list[dict[str, Any]]:
        return self.deployments.get(name, [])[:limit]
