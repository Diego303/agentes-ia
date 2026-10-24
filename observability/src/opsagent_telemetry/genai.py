"""Spans y métricas del agente según las convenciones semánticas GenAI de OpenTelemetry.

El SDK de Anthropic ya emite un span ``anthropic.messages.create`` por llamada al modelo y
el SDK de MCP un span por ``tools/call``. Aquí se añade lo que ellos no ven: la ejecución
completa del agente (``invoke_agent``), las tools locales (``execute_tool``), el coste y
los eventos de guardrails.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from opentelemetry import metrics, trace
from opentelemetry.trace import Span, SpanKind, Status, StatusCode

from opsagent_telemetry.pricing import cost_usd

_tracer = trace.get_tracer("opsagent")
_meter = metrics.get_meter("opsagent")
_token_usage = _meter.create_histogram(
    "gen_ai.client.token.usage", unit="{token}", description="Tokens por llamada al modelo"
)
_cost = _meter.create_counter("opsagent.llm.cost", unit="USD", description="Coste estimado de las llamadas")
_guardrail_events = _meter.create_counter(
    "opsagent.guardrail.events", unit="{event}", description="Decisiones de los guardrails"
)


@contextmanager
def agent_span(agent_name: str, conversation_id: str, model: str) -> Iterator[Span]:
    """Span raíz de una ejecución del agente; las llamadas al modelo y a tools cuelgan de él."""
    attributes = {
        "gen_ai.operation.name": "invoke_agent",
        "gen_ai.agent.name": agent_name,
        "gen_ai.conversation.id": conversation_id,
        "gen_ai.provider.name": "anthropic",
        "gen_ai.request.model": model,
    }
    with _tracer.start_as_current_span(
        f"invoke_agent {agent_name}", kind=SpanKind.INTERNAL, attributes=attributes
    ) as span:
        yield span


@contextmanager
def tool_span(tool_name: str, call_id: str, tool_type: str = "function") -> Iterator[Span]:
    """Span de una tool. ``tool_type`` es ``function`` (local) o ``extension`` (MCP, A2A)."""
    attributes = {
        "gen_ai.operation.name": "execute_tool",
        "gen_ai.tool.name": tool_name,
        "gen_ai.tool.call.id": call_id,
        "gen_ai.tool.type": tool_type,
    }
    with _tracer.start_as_current_span(f"execute_tool {tool_name}", attributes=attributes) as span:
        yield span


def mark_error(span: Span, error_type: str, description: str = "") -> None:
    span.set_attribute("error.type", error_type)
    span.set_status(Status(StatusCode.ERROR, description))


def record_llm_usage(model: str, usage: Any) -> float | None:
    """Registra las métricas de tokens y coste de una respuesta y devuelve el coste estimado."""
    attrs = {"gen_ai.provider.name": "anthropic", "gen_ai.request.model": model}
    for token_type, field in (("input", "input_tokens"), ("output", "output_tokens")):
        _token_usage.record(int(getattr(usage, field, 0) or 0), {**attrs, "gen_ai.token.type": token_type})
    cost = cost_usd(model, usage)
    if cost is not None:
        _cost.add(cost, attrs)
    return cost


def record_guardrail_event(kind: str, action: str) -> None:
    """``kind``: injection, policy, redaction, budget. ``action``: flagged, blocked, approval, redacted."""
    _guardrail_events.add(1, {"opsagent.guardrail.kind": kind, "opsagent.guardrail.action": action})
    span = trace.get_current_span()
    span.add_event("guardrail", {"kind": kind, "action": action})
