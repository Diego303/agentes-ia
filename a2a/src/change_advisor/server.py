"""App ASGI del agente A2A: Agent Card pública y endpoint JSON-RPC protegido con bearer token."""

from __future__ import annotations

import hmac
import json
import logging
import os

import uvicorn
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
    HTTPAuthSecurityScheme,
    SecurityRequirement,
    SecurityScheme,
    StringList,
)
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from change_advisor.executor import ChangeAdvisorExecutor
from opsagent_telemetry import instrument_asgi, setup_telemetry

log = logging.getLogger("change_advisor")
PUBLIC_PATHS = {"/.well-known/agent-card.json", "/healthz"}


def agent_card(public_url: str) -> AgentCard:
    return AgentCard(
        name="change-advisor",
        description="Evalúa cambios en producción (rollback, restart, scale, config_change, deploy) "
        "contra la política de cambios y devuelve approved, needs_approval o rejected con motivos.",
        version="0.1.0",
        default_input_modes=["application/json", "text/plain"],
        default_output_modes=["application/json", "text/plain"],
        capabilities=AgentCapabilities(streaming=False),
        supported_interfaces=[
            AgentInterface(protocol_binding="JSONRPC", url=public_url, protocol_version="1.0")
        ],
        security_schemes={
            "bearer": SecurityScheme(http_auth_security_scheme=HTTPAuthSecurityScheme(scheme="bearer"))
        },
        security_requirements=[SecurityRequirement(schemes={"bearer": StringList(list=[])})],
        skills=[
            AgentSkill(
                id="evaluate_change",
                name="Evaluar cambio",
                description="Decide si un cambio en producción está permitido según tier, incidente activo "
                "y ventanas de congelación.",
                tags=["change-management", "sre"],
                examples=['{"service": "payments-api", "action": "rollback", "incident_severity": "SEV2"}'],
            )
        ],
    )


class BearerAuthMiddleware:
    """ASGI: exige ``Authorization: Bearer`` salvo en la Agent Card y el health check."""

    def __init__(self, app, tokens: list[str]) -> None:
        self.app, self.tokens = app, [t.encode() for t in tokens]

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["path"] in PUBLIC_PATHS:
            return await self.app(scope, receive, send)
        header = dict(scope["headers"]).get(b"authorization", b"")
        token = header[7:] if header.lower().startswith(b"bearer ") else b""
        if not any(hmac.compare_digest(token, t) for t in self.tokens):
            response = JSONResponse(
                {"error": "unauthorized"}, status_code=401, headers={"WWW-Authenticate": "Bearer"}
            )
            return await response(scope, receive, send)
        return await self.app(scope, receive, send)


async def _healthz(_: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


def build_app(public_url: str, tokens: list[str], executor: ChangeAdvisorExecutor | None = None):
    card = agent_card(public_url)
    handler = DefaultRequestHandler(
        agent_executor=executor or ChangeAdvisorExecutor(), task_store=InMemoryTaskStore(), agent_card=card
    )
    routes = [
        *create_agent_card_routes(card),
        *create_jsonrpc_routes(handler, "/"),
        Route("/healthz", _healthz),
    ]
    return BearerAuthMiddleware(Starlette(routes=routes), tokens)


def main() -> None:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    setup_telemetry("change-advisor")
    tokens = json.loads(os.environ["A2A_TOKENS"])  # lista de tokens aceptados (secreto)
    app = build_app(os.environ.get("A2A_PUBLIC_URL", "http://127.0.0.1:9000/"), tokens)
    uvicorn.run(instrument_asgi(app), host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", "9000")))  # noqa: S104


if __name__ == "__main__":
    main()
