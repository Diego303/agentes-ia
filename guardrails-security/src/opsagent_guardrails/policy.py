"""Política de uso de tools: lista blanca, aprobación humana y bloqueo por contaminación.

Rompe la "tríada letal" (datos privados + contenido no confiable + capacidad de actuar):
cuando un turno ha leído contenido sospechoso, las tools con efectos quedan denegadas en ese
turno, aunque el humano estuviera dispuesto a aprobarlas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Decision(StrEnum):
    ALLOW = "allow"
    NEEDS_APPROVAL = "needs_approval"
    DENY = "deny"


@dataclass(frozen=True)
class ToolRule:
    side_effect: bool = False


@dataclass(frozen=True)
class PolicyResult:
    decision: Decision
    reason: str


@dataclass
class ToolPolicy:
    rules: dict[str, ToolRule] = field(default_factory=dict)
    max_tool_calls: int = 12

    def evaluate(self, tool_name: str, *, tainted: bool, calls_so_far: int) -> PolicyResult:
        rule = self.rules.get(tool_name)
        if rule is None:
            return PolicyResult(Decision.DENY, f"La tool '{tool_name}' no está en la lista blanca.")
        if calls_so_far >= self.max_tool_calls:
            return PolicyResult(
                Decision.DENY, f"Límite de {self.max_tool_calls} llamadas a tools por ejecución."
            )
        if rule.side_effect and tainted:
            return PolicyResult(
                Decision.DENY,
                "Acción con efectos bloqueada: la sesión leyó contenido con indicios de prompt injection.",
            )
        if rule.side_effect:
            return PolicyResult(Decision.NEEDS_APPROVAL, "Acción con efectos: requiere aprobación humana.")
        return PolicyResult(Decision.ALLOW, "Solo lectura.")
