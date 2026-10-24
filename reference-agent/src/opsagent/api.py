"""API HTTP del agente.

- ``POST /v1/chat``                          ``{"message": "...", "session_id": "opcional"}``
- ``POST /v1/sessions/{session_id}/approval`` ``{"approve": true}``
- ``GET  /healthz``

Ambas respuestas devuelven ``TurnResult``: ``reply``, ``stop`` (``approval_required`` si hay
una acción esperando), ``pending_approval``, ``trajectory``, ``usage`` y ``cost_usd``.
"""

from __future__ import annotations

import hmac
import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from anthropic import APIConnectionError, APIStatusError, RateLimitError
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from opsagent.agent import Agent
from opsagent.config import Settings
from opsagent.runtime import build_runtime
from opsagent_telemetry import instrument_asgi, setup_telemetry, shutdown_telemetry

log = logging.getLogger("opsagent.api")


def build_app(agent: Agent, api_tokens: list[str], lifespan=None) -> Starlette:
    tokens = [t.encode() for t in api_tokens]

    def authorized(request: Request) -> bool:
        header = request.headers.get("authorization", "")
        token = header[7:].encode() if header.lower().startswith("bearer ") else b""
        return any(hmac.compare_digest(token, t) for t in tokens)

    async def run(request: Request, call) -> JSONResponse:
        if not authorized(request):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        try:
            body = await request.json()
            result = await call(body)
        except (ValueError, KeyError, TypeError):
            return JSONResponse({"error": "cuerpo JSON no válido"}, status_code=400)
        except LookupError as exc:
            return JSONResponse({"error": str(exc)}, status_code=409)
        except RateLimitError:
            return JSONResponse({"error": "límite de peticiones al modelo; reintenta"}, status_code=429)
        except (APIStatusError, APIConnectionError):
            log.exception("Error llamando al modelo")
            return JSONResponse({"error": "el modelo o el gateway no están disponibles"}, status_code=502)
        return JSONResponse(result.to_dict())

    async def chat(request: Request) -> JSONResponse:
        async def call(body: dict):
            message = body["message"]
            if not isinstance(message, str) or not 0 < len(message) <= 8000:
                raise ValueError("message")
            return await agent.chat(message, session_id=body.get("session_id"))

        return await run(request, call)

    async def approval(request: Request) -> JSONResponse:
        session_id = request.path_params["session_id"]
        return await run(request, lambda body: agent.resolve_approval(session_id, bool(body["approve"])))

    async def healthz(_: Request) -> JSONResponse:
        return JSONResponse({"status": "ok"})

    return Starlette(
        routes=[
            Route("/v1/chat", chat, methods=["POST"]),
            Route("/v1/sessions/{session_id}/approval", approval, methods=["POST"]),
            Route("/healthz", healthz),
        ],
        lifespan=lifespan,
    )


def main() -> None:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    setup_telemetry("ops-agent", instrument_httpx=True)
    settings = Settings.from_env()
    if not settings.api_tokens:
        raise SystemExit("AGENT_API_TOKENS vacío: la API no arranca sin autenticación.")
    runtime = build_runtime(settings)

    @asynccontextmanager
    async def lifespan(_app):
        yield
        await runtime.aclose()
        shutdown_telemetry()

    app = build_app(runtime.agent, settings.api_tokens, lifespan=lifespan)
    uvicorn.run(instrument_asgi(app), host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", "8080")))  # noqa: S104


if __name__ == "__main__":
    main()
