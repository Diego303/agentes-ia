"""Executor A2A: traduce una tarea A2A en una evaluación de la política de cambios."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime

from a2a.helpers import (
    get_data_parts,
    get_message_text,
    new_data_part,
    new_task_from_user_message,
    new_text_message,
    new_text_part,
)
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater

from change_advisor.policy import ChangeRequest, evaluate

EXPECTED = (
    'Envía un data part (o texto JSON) con {"service", "action", "environment", '
    '"incident_severity", "reason"}; action ∈ rollback|restart|scale|config_change|deploy.'
)


def _parse(context: RequestContext) -> ChangeRequest | None:
    data = [d for d in get_data_parts(context.message.parts) if isinstance(d, dict)]
    if not data:
        try:
            loaded = json.loads(get_message_text(context.message))
        except (json.JSONDecodeError, TypeError):
            return None
        data = [loaded] if isinstance(loaded, dict) else []
    try:
        return ChangeRequest.from_dict(data[0]) if data else None
    except TypeError:
        return None


class ChangeAdvisorExecutor(AgentExecutor):
    def __init__(self, clock: Callable[[], datetime] = lambda: datetime.now(UTC)) -> None:
        self._clock = clock

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task = context.current_task
        if task is None:
            task = new_task_from_user_message(context.message)
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue=event_queue, task_id=task.id, context_id=task.context_id)

        request = _parse(context)
        if request is None:
            await updater.reject(new_text_message(f"Petición no válida. {EXPECTED}"))
            return

        verdict = evaluate(request, self._clock())
        summary = f"{verdict.decision}: {' '.join(verdict.reasons)}"
        await updater.add_artifact(
            parts=[new_data_part(verdict.to_dict(), media_type="application/json"), new_text_part(summary)],
            name="verdict",
        )
        await updater.complete()

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError("Las evaluaciones son instantáneas: no hay nada que cancelar.")
