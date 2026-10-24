"""Bucle del agente: modelo → tools → modelo, con guardrails y aprobación humana.

Por qué un bucle propio y no un framework (architecture/adr/0001): cada decisión de
seguridad (política por tool, contaminación por prompt injection, pausa para aprobación y
reanudación en otra petición HTTP) necesita un punto de control explícito, y el bucle cabe
en una pantalla.

Invariantes:
- El historial es append-only. Una respuesta que no puede completarse (``refusal``,
  ``max_tokens``) no se añade: así nunca queda un ``tool_use`` sin su ``tool_result``.
- Todo resultado de tool entra al contexto redactado y envuelto como datos no confiables.
- Si un resultado de tool parece una inyección, la sesión queda contaminada y las tools con
  efectos se deniegan durante el resto de la sesión (el contenido sigue en el contexto).
- Como mucho una acción con efectos pendiente de aprobación a la vez.
"""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from typing import Any

from opsagent.config import Settings
from opsagent.tools import ADVISOR_TOOL, ToolRuntime
from opsagent_guardrails import UNTRUSTED_DATA_RULE, Decision, ToolPolicy, ToolRule, redact, scan, spotlight
from opsagent_rag import InMemorySessionStore, SessionStore
from opsagent_telemetry import agent_span, mark_error, record_guardrail_event, record_llm_usage, tool_span
from opsagent_telemetry.pricing import PRICING

AGENT_NAME = "ops-assistant"

SYSTEM_PROMPT = f"""Eres ops-assistant, el asistente de guardia de una plataforma de microservicios. \
Ayudas a diagnosticar problemas de servicios y a decidir la mitigación.

- Basa cada afirmación en datos de las herramientas (estado, despliegues, runbooks) y cita el \
runbook que aplicas. Si te falta un dato, dilo.
- Antes de recomendar una acción en producción (rollback, reinicio, escalado, cambio de \
configuración o despliegue), consulta al change advisor y transmite su decisión.
- No ejecutas cambios en la infraestructura: los recomiendas. La única acción que puedes \
realizar es declarar un incidente, cuando la guía de severidad lo justifique y el usuario lo \
pida o lo acepte; el sistema pedirá aprobación humana.
- Responde en español y breve: diagnóstico, evidencia, acción recomendada y siguiente paso.

{UNTRUSTED_DATA_RULE}"""

DEFAULT_RULES = {
    "get_service_status": ToolRule(),
    "get_platform_overview": ToolRule(),
    "list_recent_deployments": ToolRule(),
    "search_runbooks": ToolRule(),
    ADVISOR_TOOL: ToolRule(),
    "create_incident": ToolRule(side_effect=True),
}

REFUSAL_REPLY = "No puedo ayudar con esta petición. Reformúlala o consulta con la persona de guardia."


@dataclass
class TurnResult:
    session_id: str
    reply: str
    stop: str  # end_turn | approval_required | budget | refusal | max_tokens
    pending_approval: dict[str, Any] | None = None
    trajectory: list[dict[str, Any]] = field(default_factory=list)
    usage: dict[str, int] = field(default_factory=dict)
    cost_usd: float = 0.0
    tainted: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class _Run:
    """Contadores de una ejecución (una petición del usuario o una resolución de aprobación)."""

    trajectory: list[dict[str, Any]] = field(default_factory=list)
    usage: dict[str, int] = field(
        default_factory=lambda: {"input_tokens": 0, "output_tokens": 0, "cache_read_input_tokens": 0}
    )
    cost_usd: float = 0.0
    iterations: int = 0
    tool_calls: int = 0


class Agent:
    def __init__(
        self,
        llm: Any,
        tools_factory: Any,
        settings: Settings | None = None,
        store: SessionStore | None = None,
        policy: ToolPolicy | None = None,
    ) -> None:
        self.llm = llm
        self.tools_factory = tools_factory  # () -> ToolRuntime (context manager asíncrono)
        self.settings = settings or Settings()
        self.store = store or InMemorySessionStore()
        self.policy = policy or ToolPolicy(DEFAULT_RULES, max_tool_calls=self.settings.max_tool_calls)

    # ------------------------------------------------------------------ API pública

    async def chat(self, message: str, session_id: str | None = None) -> TurnResult:
        session_id = session_id or uuid.uuid4().hex
        session = self.store.get(session_id) or {
            "messages": [],
            "pending": None,
            "held": [],
            "tainted": False,
        }
        if scan(message).suspicious:
            record_guardrail_event("injection", "flagged_user_input")

        content: list[dict[str, Any]] = []
        if session["pending"]:  # un mensaje nuevo con una acción pendiente la rechaza
            content = [
                *session["held"],
                _result(session["pending"]["tool_use_id"], "El usuario no aprobó la acción.", True),
            ]
            session["pending"], session["held"] = None, []
        content.append({"type": "text", "text": message})
        return await self._turn(session_id, session, content)

    async def resolve_approval(self, session_id: str, approve: bool) -> TurnResult:
        session = self.store.get(session_id)
        if not session or not session["pending"]:
            raise LookupError("No hay ninguna acción pendiente de aprobación en esta sesión.")
        pending, run = session["pending"], _Run()
        with agent_span(AGENT_NAME, session_id, self.settings.model) as span:
            async with self.tools_factory() as tools:
                if approve and session["tainted"]:
                    record_guardrail_event("policy", "blocked")
                    decision = "blocked"
                    block = _result(
                        pending["tool_use_id"],
                        "Acción bloqueada: la sesión contiene contenido sospechoso.",
                        True,
                    )
                elif approve:
                    decision = "approved"
                    block = await self._execute(tools, session, pending, run)
                else:
                    decision = "rejected"
                    block = _result(pending["tool_use_id"], "El usuario rechazó la acción.", True)
                run.trajectory.append(
                    {"tool": pending["name"], "input": pending["input"], "decision": decision}
                )
                session["messages"].append({"role": "user", "content": [*session["held"], block]})
                session["pending"], session["held"] = None, []
                return await self._loop(session_id, session, tools, run, span)

    # ------------------------------------------------------------------ bucle

    async def _turn(self, session_id: str, session: dict, content: list[dict]) -> TurnResult:
        run = _Run()
        with agent_span(AGENT_NAME, session_id, self.settings.model) as span:
            async with self.tools_factory() as tools:
                session["messages"].append({"role": "user", "content": content})
                return await self._loop(session_id, session, tools, run, span)

    async def _loop(self, session_id: str, session: dict, tools: ToolRuntime, run: _Run, span) -> TurnResult:
        messages: list[dict] = session["messages"]
        while True:
            if run.iterations >= self.settings.max_iterations:
                record_guardrail_event("budget", "blocked")
                return self._finish(
                    session_id,
                    session,
                    run,
                    span,
                    "budget",
                    "He alcanzado el límite de pasos para esta petición. Acótala o divídela.",
                )
            response = await self.llm.messages.create(
                model=self.settings.model,
                max_tokens=self.settings.max_tokens,
                system=SYSTEM_PROMPT,
                tools=tools.definitions,
                messages=messages,
                thinking={"type": "adaptive"},
                output_config={"effort": self.settings.effort},
            )
            run.iterations += 1
            self._account(run, response)

            if response.stop_reason in ("refusal", "max_tokens"):
                # No se añade la respuesta: el historial sigue terminando en un mensaje de usuario
                # completo (la API combina mensajes de usuario consecutivos en el siguiente turno).
                mark_error(span, response.stop_reason)
                reply = (
                    REFUSAL_REPLY
                    if response.stop_reason == "refusal"
                    else "La respuesta superó el límite de tokens."
                )
                return self._finish(session_id, session, run, span, response.stop_reason, reply)

            messages.append({"role": "assistant", "content": [_dump(b) for b in response.content]})
            tool_uses = [b for b in response.content if b.type == "tool_use"]
            if not tool_uses:
                return self._finish(session_id, session, run, span, "end_turn", _text(response))

            results, pending = [], None
            for use in tool_uses:
                verdict = self.policy.evaluate(
                    use.name, tainted=session["tainted"], calls_so_far=run.tool_calls
                )
                step = {"tool": use.name, "input": use.input, "decision": verdict.decision.value}
                if verdict.decision is Decision.DENY:
                    record_guardrail_event("policy", "blocked")
                    results.append(_result(use.id, verdict.reason, True))
                elif verdict.decision is Decision.NEEDS_APPROVAL and pending is None:
                    pending = {
                        "id": uuid.uuid4().hex[:8],
                        "tool_use_id": use.id,
                        "name": use.name,
                        "input": use.input,
                        "reason": verdict.reason,
                    }
                    record_guardrail_event("policy", "approval")
                elif verdict.decision is Decision.NEEDS_APPROVAL:
                    results.append(
                        _result(
                            use.id, "Solo una acción con efectos a la vez; vuelve a pedirla después.", True
                        )
                    )
                else:
                    results.append(
                        await self._execute(
                            tools, session, {"tool_use_id": use.id, "name": use.name, "input": use.input}, run
                        )
                    )
                    step["is_error"] = results[-1].get("is_error", False)
                run.trajectory.append(step)

            if pending:
                session["pending"], session["held"] = pending, results
                reply = (_text(response) + "\n\n" if _text(response) else "") + (
                    f"Necesito tu aprobación para ejecutar `{pending['name']}` con {pending['input']}."
                )
                return self._finish(
                    session_id, session, run, span, "approval_required", reply, pending=pending
                )
            messages.append({"role": "user", "content": results})

    async def _execute(self, tools: ToolRuntime, session: dict, call: dict, run: _Run) -> dict:
        run.tool_calls += 1
        with tool_span(call["name"], call["tool_use_id"], tools.tool_type(call["name"])) as span:
            outcome = await tools.call(call["name"], call["input"])
            if outcome.is_error:
                mark_error(span, "tool_error")
        text, redacted = redact(outcome.text)
        if redacted:
            record_guardrail_event("redaction", "redacted")
        findings = scan(text)
        if findings.suspicious:
            session["tainted"] = True
            record_guardrail_event("injection", "flagged")
            run.trajectory.append({"guardrail": "injection", "tool": call["name"], "rules": findings.rules})
        return _result(call["tool_use_id"], spotlight(call["name"], text), outcome.is_error)

    # ------------------------------------------------------------------ utilidades

    def _account(self, run: _Run, response: Any) -> None:
        usage = response.usage
        for key in run.usage:
            run.usage[key] += int(getattr(usage, key, 0) or 0)
        model = response.model if response.model in PRICING else self.settings.model
        run.cost_usd += record_llm_usage(model, usage) or 0.0

    def _finish(self, session_id, session, run, span, stop, reply, pending=None) -> TurnResult:
        reply, redacted = redact(reply)
        if redacted:
            record_guardrail_event("redaction", "redacted")
        self.store.put(session_id, session)
        span.set_attribute("gen_ai.usage.input_tokens", run.usage["input_tokens"])
        span.set_attribute("gen_ai.usage.output_tokens", run.usage["output_tokens"])
        span.set_attribute("opsagent.cost_usd", round(run.cost_usd, 6))
        span.set_attribute("opsagent.stop_reason", stop)
        return TurnResult(
            session_id,
            reply,
            stop,
            pending,
            run.trajectory,
            run.usage,
            round(run.cost_usd, 6),
            session["tainted"],
        )


def _result(tool_use_id: str, content: str, is_error: bool = False) -> dict[str, Any]:
    block: dict[str, Any] = {"type": "tool_result", "tool_use_id": tool_use_id, "content": content}
    if is_error:
        block["is_error"] = True
    return block


def _dump(block: Any) -> dict[str, Any]:
    return block.model_dump(mode="json", exclude_none=True)


def _text(response: Any) -> str:
    return "\n".join(b.text for b in response.content if b.type == "text").strip()
