"""Modelo con guion para probar el bucle del agente sin red ni coste.

Devuelve objetos ``anthropic.types.Message`` reales, así que el agente ejecuta exactamente
el mismo código que con el modelo de verdad. Registra cada petición para poder comprobar
qué se envió (historial, tools, parámetros).
"""

from __future__ import annotations

import copy
import itertools
from collections.abc import Callable
from typing import Any

from anthropic.types import Message

Step = dict[str, Any] | Callable[[dict[str, Any]], dict[str, Any]]


def text(value: str) -> dict[str, Any]:
    return {"type": "text", "text": value}


def tool_use(name: str, arguments: dict[str, Any], call_id: str | None = None) -> dict[str, Any]:
    return {"type": "tool_use", "id": call_id or f"toolu_{name}", "name": name, "input": arguments}


def reply(*blocks: dict[str, Any], stop_reason: str | None = None) -> dict[str, Any]:
    if stop_reason is None:
        stop_reason = "tool_use" if any(b["type"] == "tool_use" for b in blocks) else "end_turn"
    return {"content": list(blocks), "stop_reason": stop_reason}


class _Messages:
    def __init__(self, owner: ScriptedLLM) -> None:
        self._owner = owner

    async def create(self, **kwargs: Any) -> Message:
        self._owner.requests.append(copy.deepcopy(kwargs))  # el agente sigue mutando el historial
        if not self._owner.script:
            raise AssertionError(
                "El guion del modelo se ha agotado: el agente hizo más llamadas de las previstas."
            )
        step = self._owner.script.pop(0)
        data = step(kwargs) if callable(step) else step
        return Message.model_validate(
            {
                "id": f"msg_{next(self._owner.ids)}",
                "type": "message",
                "role": "assistant",
                "model": kwargs.get("model", "claude-opus-5-5"),
                "content": data["content"],
                "stop_reason": data["stop_reason"],
                "stop_sequence": None,
                "usage": data.get("usage", {"input_tokens": 1200, "output_tokens": 150}),
            }
        )


class ScriptedLLM:
    def __init__(self, script: list[Step]) -> None:
        self.script = list(script)
        self.requests: list[dict[str, Any]] = []
        self.ids = itertools.count(1)
        self.messages = _Messages(self)
