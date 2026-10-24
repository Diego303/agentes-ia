"""Guardrails deterministas del agente. No sustituyen al diseño: lo refuerzan.

La defensa principal es arquitectónica (mínimo privilegio, aprobación humana para efectos
y bloqueo de tools con efectos cuando el contexto contiene datos sospechosos). La detección
heurística solo decide cuándo un turno queda "contaminado".
"""

from opsagent_guardrails.injection import Finding, ScanResult, scan
from opsagent_guardrails.policy import Decision, PolicyResult, ToolPolicy, ToolRule
from opsagent_guardrails.redaction import redact
from opsagent_guardrails.spotlight import UNTRUSTED_DATA_RULE, spotlight

__all__ = [
    "UNTRUSTED_DATA_RULE",
    "Decision",
    "Finding",
    "PolicyResult",
    "ScanResult",
    "ToolPolicy",
    "ToolRule",
    "redact",
    "scan",
    "spotlight",
]
