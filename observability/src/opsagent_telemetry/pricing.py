"""Precios por millón de tokens (USD) para estimar el coste de cada ejecución.

Fuente: https://platform.claude.com/docs/en/about-claude/pricing (verificado en la fecha
de ``PRICING_AS_OF``). La escritura de caché se factura como 5 minutos (1,25 × entrada),
que es lo que usa ``cache_control`` por defecto.
"""

from __future__ import annotations

from typing import Any

PRICING_AS_OF = "2026-10-24"

# input, output, cache_write (5 min), cache_read; ``long_context`` aplica por petición
# cuando la entrada total supera ``threshold`` tokens.
PRICING: dict[str, dict[str, Any]] = {
    "claude-opus-5-5": {"input": 4.0, "output": 20.0, "cache_write": 5.0, "cache_read": 0.20},
    "claude-sonnet-5-5": {"input": 2.0, "output": 10.0, "cache_write": 2.5, "cache_read": 0.10},
    "claude-haiku-5-5": {
        "input": 0.10,
        "output": 0.50,
        "cache_write": 0.125,
        "cache_read": 0.01,
        "long_context": {
            "threshold": 100_000,
            "input": 0.50,
            "output": 2.50,
            "cache_write": 0.625,
            "cache_read": 0.05,
        },
    },
}


def _get(usage: Any, field: str) -> int:
    value = usage.get(field) if isinstance(usage, dict) else getattr(usage, field, None)
    return int(value or 0)


def cost_usd(model: str, usage: Any) -> float | None:
    """Coste estimado de una respuesta, o ``None`` si el modelo no tiene precio.

    ``usage`` es el ``Usage`` de la respuesta del SDK de Anthropic (o un dict equivalente).
    Devolver ``None`` en lugar de 0 evita que un modelo sin precio parezca gratis.
    """
    prices = PRICING.get(model)
    if prices is None:
        return None
    tokens = {
        "input": _get(usage, "input_tokens"),
        "output": _get(usage, "output_tokens"),
        "cache_write": _get(usage, "cache_creation_input_tokens"),
        "cache_read": _get(usage, "cache_read_input_tokens"),
    }
    long_context = prices.get("long_context")
    total_input = tokens["input"] + tokens["cache_write"] + tokens["cache_read"]
    if long_context and total_input > long_context["threshold"]:
        prices = long_context
    return sum(tokens[k] * prices[k] for k in tokens) / 1_000_000
