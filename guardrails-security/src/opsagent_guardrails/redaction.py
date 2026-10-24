"""Redacción de secretos y datos personales en las respuestas y en lo que se registra."""

from __future__ import annotations

import re

_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "private_key",
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]+?-----END [A-Z ]*PRIVATE KEY-----"),
    ),
    ("anthropic_key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}")),
    ("api_key", re.compile(r"\b(sk|rk|pk)-[A-Za-z0-9]{20,}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("aws_access_key", re.compile(r"\b(AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")),
    ("bearer_token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]{20,}=*")),
    ("connection_string", re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s:/@]+:[^\s@/]+@[^\s]+", re.IGNORECASE)),
    ("email", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("iban", re.compile(r"\b[A-Z]{2}\d{2}(?:\s?[A-Z0-9]{4}){3,7}\b")),
    ("card_number", re.compile(r"\b(?:\d[ -]?){13,19}\b")),
]


def _luhn_ok(candidate: str) -> bool:
    digits = [int(c) for c in candidate if c.isdigit()]
    checksum = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2:
            d = d * 2 - 9 if d > 4 else d * 2
        checksum += d
    return len(digits) >= 13 and checksum % 10 == 0


def redact(text: str) -> tuple[str, list[str]]:
    """Devuelve el texto redactado y los tipos encontrados (sin repetir)."""
    found: list[str] = []

    for kind, pattern in _PATTERNS:

        def _replace(match: re.Match[str], kind: str = kind) -> str:
            if kind == "card_number" and not _luhn_ok(match.group(0)):
                return match.group(0)
            if kind not in found:
                found.append(kind)
            return f"[REDACTADO:{kind}]"

        text = pattern.sub(_replace, text)
    return text, found
