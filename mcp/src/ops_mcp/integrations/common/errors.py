"""Errores previstos de las tools.

Un ``ToolError`` llega al modelo como resultado con ``is_error``: su mensaje tiene que decir
qué hacer para corregirse ("servicios válidos: ..."), nunca detalles internos.
"""

from __future__ import annotations

from mcp.server.mcpserver.exceptions import ToolError

__all__ = ["ToolError", "unknown_service"]


def unknown_service(name: str, known: list[str]) -> ToolError:
    return ToolError(f"Servicio desconocido '{name}'. Servicios válidos: {', '.join(known)}.")
