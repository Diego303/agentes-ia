"""Detección heurística de prompt injection en texto no confiable (resultados de tools, documentos).

Reglas en español e inglés. Un hallazgo ``high`` basta para marcar el texto como
sospechoso; los ``medium`` necesitan coincidir dos. El objetivo es alta precisión: un falso
positivo bloquea acciones con efectos en ese turno, nunca la conversación entera.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_I = re.IGNORECASE

# (regla, patrón, severidad)
_RULES: list[tuple[str, re.Pattern[str], str]] = [
    (
        "instruction_override",
        re.compile(
            r"\b(ignore|disregard|forget|override)\b[^.\n]{0,40}\b(instructions?|rules|guidelines|prompt)\b"
            r"|\b(ignora|olvida|omite|descarta)\b[^.\n]{0,40}\b(instrucciones|reglas|indicaciones|prompt)\b",
            _I,
        ),
        "high",
    ),
    (
        "role_hijack",
        re.compile(
            r"\b(you are now|from now on,? you|new instructions:|act as (an?|the) )"
            r"|\b(ahora eres|a partir de ahora,? (eres|actúa|debes)|nuevas instrucciones:)",
            _I,
        ),
        "high",
    ),
    (
        "system_prompt_exfiltration",
        re.compile(
            r"\b(reveal|print|repeat|show|output)\b[^.\n]{0,30}\b(system prompt|hidden instructions|your instructions)"
            r"|\b(revela|muestra|repite|imprime)\b[^.\n]{0,30}\b(prompt del sistema|instrucciones (ocultas|del sistema))",
            _I,
        ),
        "high",
    ),
    (
        "fake_delimiter",
        re.compile(
            r"</?\s*(system|untrusted_data|tool_result|instructions)\s*>|\[/?(SYSTEM|INST)\]|^#{2,}\s*system\b",
            _I | re.M,
        ),
        "high",
    ),
    (
        "agent_directive",
        re.compile(
            r"\b(assistant|ai|agent|model|llm)\b[,:]?\s+(you must|must|should|immediately)\b"
            r"|\b(asistente|agente|modelo|ia)\b[,:]?\s+(debes|tienes que|inmediatamente)\b",
            _I,
        ),
        "medium",
    ),
    (
        "action_coercion",
        re.compile(
            r"\b(create|open|delete|send|escalate|approve)\b[^.\n]{0,25}\b(incident|ticket|sev ?1|email|request)\b[^.\n]{0,40}\b(now|immediately|without (asking|approval))"
            r"|\b(crear?|abr(?:e|ir)|borrar?|env[ií]ar?|escalar?|aprueba|aprobar)\b[^.\n]{0,25}"
            r"\b(incidente|ticket|sev ?1|correo|petición)\b[^.\n]{0,40}\b(ya|inmediatamente|sin (preguntar|aprobación))",
            _I,
        ),
        "medium",
    ),
    (
        "exfiltration_link",
        re.compile(r"!\[[^\]]*\]\(https?://[^)\s]+\?[^)\s]*=[^)\s]*\)", _I),
        "high",
    ),
    (
        "hidden_characters",
        re.compile("[\U000e0000-\U000e007f]|[‪-‮⁦-⁩]|[​-‍⁠]{3,}"),
        "high",
    ),
    (
        "encoded_payload",
        re.compile(r"[A-Za-z0-9+/]{160,}={0,2}"),
        "medium",
    ),
]


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    excerpt: str


@dataclass(frozen=True)
class ScanResult:
    findings: list[Finding] = field(default_factory=list)

    @property
    def suspicious(self) -> bool:
        high = sum(f.severity == "high" for f in self.findings)
        medium = sum(f.severity == "medium" for f in self.findings)
        return high >= 1 or medium >= 2

    @property
    def rules(self) -> list[str]:
        return sorted({f.rule for f in self.findings})


def scan(text: str) -> ScanResult:
    """Analiza ``text`` y devuelve los hallazgos (como mucho uno por regla)."""
    findings = []
    for rule, pattern, severity in _RULES:
        match = pattern.search(text)
        if match:
            excerpt = match.group(0)
            findings.append(Finding(rule, severity, excerpt[:80].encode("unicode_escape").decode()))
    return ScanResult(findings)
