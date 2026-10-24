"""Modelos de salida que comparten varias tools."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

Health = Literal["healthy", "degraded", "down"]


class ServiceStatus(BaseModel):
    service: str
    tier: int = Field(description="0 = crítico (pagos, login), 2 = no crítico")
    owner: str
    status: Health
    error_rate_pct: float
    latency_p95_ms: int
    replicas_ready: int
    replicas_desired: int
    notes: str
    observed_at: str

    @classmethod
    def from_catalog(cls, name: str, data: dict[str, Any], observed_at: str) -> ServiceStatus:
        return cls(
            service=name,
            tier=data["tier"],
            owner=data["owner"],
            status=data["status"],
            error_rate_pct=data["error_rate_pct"],
            latency_p95_ms=data["latency_p95_ms"],
            replicas_ready=data["replicas"]["ready"],
            replicas_desired=data["replicas"]["desired"],
            notes=data["notes"],
            observed_at=observed_at,
        )
