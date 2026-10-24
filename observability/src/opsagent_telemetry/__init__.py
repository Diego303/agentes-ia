"""Telemetría común: un solo arranque de OpenTelemetry y spans GenAI para todos los servicios."""

from opsagent_telemetry.bootstrap import instrument_asgi, setup_telemetry, shutdown_telemetry
from opsagent_telemetry.genai import (
    agent_span,
    mark_error,
    record_guardrail_event,
    record_llm_usage,
    tool_span,
)
from opsagent_telemetry.pricing import PRICING, PRICING_AS_OF, cost_usd

__all__ = [
    "PRICING",
    "PRICING_AS_OF",
    "agent_span",
    "cost_usd",
    "instrument_asgi",
    "mark_error",
    "record_guardrail_event",
    "record_llm_usage",
    "setup_telemetry",
    "shutdown_telemetry",
    "tool_span",
]
