"""Arranque por Streamable HTTP (``ops-mcp``) o stdio (``ops-mcp --stdio``)."""

from __future__ import annotations

import sys

import uvicorn

from ops_mcp.app import build_http_app
from ops_mcp.auth import auth_from_env
from ops_mcp.config import Settings
from ops_mcp.integrations.common import configure_logging, get_logger
from ops_mcp.server import build_server
from opsagent_telemetry import setup_telemetry

log = get_logger(__name__)


def main() -> None:
    settings = Settings.from_env()
    configure_logging(settings.log_level, settings.log_format)
    setup_telemetry("ops-mcp")

    if "--stdio" in sys.argv:  # cliente local que lanza el servidor como subproceso
        build_server().run("stdio")
        return

    verifier, auth = auth_from_env()
    if verifier is None:
        log.warning("MCP_AUTH_DISABLED=true: servidor SIN autenticación. Solo para desarrollo local.")
    app = build_http_app(build_server(token_verifier=verifier, auth=auth), list(settings.allowed_hosts))
    log.info(
        "server.start", extra={"host": settings.host, "port": settings.port, "auth": verifier is not None}
    )
    uvicorn.run(app, host=settings.host, port=settings.port, log_config=None)


if __name__ == "__main__":
    main()
