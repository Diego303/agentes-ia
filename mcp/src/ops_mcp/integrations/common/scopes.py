"""Scopes OAuth del servidor y comprobación dentro de una tool.

``ops:read`` lo exige el transporte para cualquier llamada (``AuthSettings.required_scopes``).
Las tools con efectos piden además ``ops:write`` con ``require_scope``.
"""

from __future__ import annotations

from mcp.server.auth.middleware.auth_context import get_access_token

from ops_mcp.integrations.common.errors import ToolError

READ_SCOPE = "ops:read"
WRITE_SCOPE = "ops:write"
LOCAL_CLIENT = "local-dev"


def require_scope(scope: str, *, auth_enabled: bool) -> str:
    """Devuelve el ``client_id`` que llama; si la autenticación está activa y falta el scope, falla.

    Sin autenticación (stdio o ``MCP_AUTH_DISABLED``) el cliente es ``local-dev``.
    """
    token = get_access_token()
    if auth_enabled and (token is None or scope not in token.scopes):
        raise ToolError(f"Falta el scope '{scope}' para esta operación.")
    return token.client_id if token else LOCAL_CLIENT
