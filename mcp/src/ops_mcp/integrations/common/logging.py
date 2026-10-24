"""Logger del servidor y decorador que registra cada llamada a una tool.

Los logs van siempre a **stderr**: con el transporte stdio, stdout es el canal del protocolo y
cualquier línea extra lo rompe. Formato JSON (una línea por evento, para el colector de logs)
o texto (desarrollo), con ``MCP_LOG_FORMAT`` y ``MCP_LOG_LEVEL``.

Cada llamada deja un evento ``tool.call`` con la tool, un ``call_id``, el cliente, la duración,
el resultado (``ok``, ``tool_error`` o ``error``) y el ``trace_id`` de OpenTelemetry, para
saltar del log a la traza. Los argumentos solo se registran en DEBUG.
"""

from __future__ import annotations

import functools
import json
import logging
import sys
import time
import uuid
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any, ParamSpec, TypeVar

from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.mcpserver.exceptions import ToolError
from opentelemetry import trace

ROOT_LOGGER = "ops_mcp"
_STANDARD_ATTRS = set(vars(logging.makeLogRecord({}))) | {"message", "asctime", "taskName", "color_message"}

P = ParamSpec("P")
R = TypeVar("R")


class JsonFormatter(logging.Formatter):
    """Una línea JSON por registro, con los campos de ``extra`` al primer nivel."""

    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, UTC).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        entry.update({k: v for k, v in vars(record).items() if k not in _STANDARD_ATTRS})
        if record.exc_info:
            entry["exc"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=False, default=str)


def configure_logging(level: str = "INFO", fmt: str = "json") -> None:
    """Configura el logger del paquete y los de uvicorn con el mismo formato.

    Idempotente: se puede llamar más de una vez.
    """
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        JsonFormatter()
        if fmt == "json"
        else logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    for name in (ROOT_LOGGER, "uvicorn", "uvicorn.access"):
        logger = logging.getLogger(name)
        logger.handlers[:] = [handler]
        logger.setLevel(level.upper())
        logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Logger hijo de ``ops_mcp`` (p. ej. ``get_logger(__name__)`` en cada módulo)."""
    return logging.getLogger(name if name.startswith(ROOT_LOGGER) else f"{ROOT_LOGGER}.{name}")


def _trace_id() -> str | None:
    context = trace.get_current_span().get_span_context()
    return format(context.trace_id, "032x") if context.is_valid else None


def logged_tool(name: str) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """Envuelve una tool asíncrona: registra la llamada y oculta los errores inesperados.

    - ``ToolError`` (error previsto, con un mensaje para el modelo) se registra como
      ``tool_error`` y se propaga tal cual.
    - Cualquier otra excepción se registra con su traza y se sustituye por un ``ToolError``
      genérico con el ``call_id``: el modelo no ve detalles internos y el operador encuentra
      el log.

    ``functools.wraps`` conserva firma y anotaciones, así que el SDK genera el mismo esquema.
    """
    log = get_logger("tools")

    def decorator(fn: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @functools.wraps(fn)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            call_id = uuid.uuid4().hex[:12]
            token = get_access_token()
            fields: dict[str, Any] = {
                "tool": name,
                "call_id": call_id,
                "client_id": token.client_id if token else None,
                "trace_id": _trace_id(),
            }
            log.debug("tool.start", extra={**fields, "arguments": kwargs})
            start = time.perf_counter()
            outcome = "ok"
            try:
                return await fn(*args, **kwargs)
            except ToolError:
                outcome = "tool_error"
                raise
            except Exception as exc:
                outcome = "error"
                log.exception("tool.unexpected_error", extra=fields)
                raise ToolError(f"Error interno en {name}. Referencia para soporte: {call_id}.") from exc
            finally:
                level = logging.INFO if outcome != "error" else logging.ERROR
                duration_ms = round((time.perf_counter() - start) * 1000, 1)
                log.log(level, "tool.call", extra={**fields, "outcome": outcome, "duration_ms": duration_ms})

        return wrapper

    return decorator
