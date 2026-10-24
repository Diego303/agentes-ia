"""Cliente del modelo: el SDK oficial de Anthropic apuntando al gateway.

El gateway (LiteLLM) expone el endpoint ``/v1/messages`` de Anthropic, así que la
aplicación usa el SDK nativo (tipos, errores tipados, spans OTel) y el gateway centraliza
claves, fallbacks, límites y presupuesto. La clave que ve la aplicación es la del gateway,
nunca la del proveedor.
"""

from __future__ import annotations

from anthropic import AsyncAnthropic

from opsagent.config import Settings


def make_llm_client(settings: Settings) -> AsyncAnthropic:
    if settings.gateway_url:
        return AsyncAnthropic(base_url=settings.gateway_url, api_key=settings.gateway_key, timeout=120.0)
    return AsyncAnthropic(timeout=120.0)  # ANTHROPIC_API_KEY u otra credencial del entorno
