"""Política de cambios en producción, determinista y auditable.

Un agente A2A no tiene por qué ser un LLM: lo que importa es el contrato (Agent Card,
tareas, artefactos). Esta política es código porque una decisión de control de cambios
debe ser reproducible; un LLM, si se añade, solo redactaría la explicación.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime

ACTIONS = ("rollback", "restart", "scale", "config_change", "deploy")
MITIGATIONS = ("rollback", "restart", "scale")
# Vista propia del CMDB del equipo de cambios (no depende del servidor MCP).
SERVICES = {
    "payments-api": {"tier": 0, "owner": "team-payments"},
    "auth-service": {"tier": 0, "owner": "team-identity"},
    "checkout-web": {"tier": 1, "owner": "team-checkout"},
    "orders-worker": {"tier": 1, "owner": "team-orders"},
    "search-api": {"tier": 2, "owner": "team-discovery"},
}


@dataclass(frozen=True)
class ChangeRequest:
    service: str
    action: str
    environment: str = "production"
    incident_severity: str | None = None
    reason: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> ChangeRequest:
        allowed = {
            k: data[k]
            for k in ("service", "action", "environment", "incident_severity", "reason")
            if k in data
        }
        return cls(**allowed)


@dataclass(frozen=True)
class Verdict:
    decision: str  # approved | needs_approval | rejected
    reasons: list[str]
    conditions: list[str] = field(default_factory=list)
    required_approvers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _in_weekend_freeze(now: datetime) -> bool:
    """Congelación de fin de semana: viernes 16:00 UTC a lunes 08:00 UTC."""
    weekday, hour = now.weekday(), now.hour
    return (weekday == 4 and hour >= 16) or weekday in (5, 6) or (weekday == 0 and hour < 8)


def evaluate(req: ChangeRequest, now: datetime) -> Verdict:
    if req.action not in ACTIONS:
        return Verdict("rejected", [f"Acción desconocida '{req.action}'. Válidas: {', '.join(ACTIONS)}."])
    if req.service not in SERVICES:
        return Verdict("rejected", [f"Servicio '{req.service}' fuera del inventario de cambios."])
    if req.environment != "production":
        return Verdict("approved", ["Fuera de producción no se requiere control de cambios."])

    service = SERVICES[req.service]
    major_incident = req.incident_severity in ("SEV1", "SEV2")
    mitigation = req.action in MITIGATIONS

    if major_incident and not mitigation:
        return Verdict(
            "rejected",
            [f"Congelación de cambios durante un {req.incident_severity}: solo se permiten mitigaciones."],
        )
    if service["tier"] == 0:
        if mitigation and major_incident:
            return Verdict(
                "approved",
                [f"Mitigación ({req.action}) de un servicio tier 0 durante un {req.incident_severity}."],
                conditions=[
                    "Avisar al incident commander antes de ejecutar.",
                    "Ejecutar con el pipeline de despliegue.",
                ],
            )
        return Verdict(
            "needs_approval",
            ["Los cambios en servicios tier 0 fuera de un incidente mayor pasan por el change manager."],
            required_approvers=["change-manager", service["owner"]],
        )
    if not mitigation and _in_weekend_freeze(now):
        return Verdict(
            "needs_approval",
            ["Congelación de fin de semana para cambios que no son mitigaciones."],
            required_approvers=["change-manager"],
        )
    return Verdict(
        "approved",
        [f"Cambio de riesgo controlado en un servicio tier {service['tier']}."],
        conditions=["Ejecutar con el pipeline de despliegue y vigilar 10 minutos."],
    )
