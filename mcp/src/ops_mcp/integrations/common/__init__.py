"""Lo que comparten las tools: dependencias, catálogo, errores, scopes, logging y concurrencia."""

from ops_mcp.integrations.common.catalog import RESOURCES_DIR, OpsCatalog
from ops_mcp.integrations.common.concurrency import gather_limited, run_blocking
from ops_mcp.integrations.common.deps import ToolDeps
from ops_mcp.integrations.common.errors import ToolError, unknown_service
from ops_mcp.integrations.common.logging import JsonFormatter, configure_logging, get_logger, logged_tool
from ops_mcp.integrations.common.scopes import READ_SCOPE, WRITE_SCOPE, require_scope

__all__ = [
    "READ_SCOPE",
    "RESOURCES_DIR",
    "WRITE_SCOPE",
    "JsonFormatter",
    "OpsCatalog",
    "ToolDeps",
    "ToolError",
    "configure_logging",
    "gather_limited",
    "get_logger",
    "logged_tool",
    "require_scope",
    "run_blocking",
    "unknown_service",
]
