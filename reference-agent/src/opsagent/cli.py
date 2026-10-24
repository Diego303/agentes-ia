"""CLI interactiva para desarrollo local.

Solo necesita una credencial del modelo (``ANTHROPIC_API_KEY`` o ``LLM_GATEWAY_URL`` +
``LLM_GATEWAY_KEY``). Sin ``MCP_URL`` lanza ops-mcp por stdio y sin ``ADVISOR_URL`` sirve el
change advisor en el mismo proceso: el protocolo MCP y A2A es el real en ambos casos.
"""

from __future__ import annotations

import asyncio
import os

from opsagent.config import Settings
from opsagent.runtime import build_runtime
from opsagent_telemetry import setup_telemetry, shutdown_telemetry


async def _repl() -> None:
    runtime = build_runtime(Settings.from_env())
    session_id = None
    print("ops-assistant · escribe tu pregunta (vacío para salir)")
    try:
        while True:
            message = await asyncio.to_thread(input, "\n> ")
            if not message.strip():
                break
            result = await runtime.agent.chat(message, session_id)
            session_id = result.session_id
            while result.stop == "approval_required":
                print(f"\n{result.reply}")
                answer = await asyncio.to_thread(input, "¿Apruebas? [s/N] ")
                result = await runtime.agent.resolve_approval(
                    session_id, answer.strip().lower() in ("s", "si", "sí", "y")
                )
            tools = ", ".join(step["tool"] for step in result.trajectory if "tool" in step) or "ninguna"
            print(f"\n{result.reply}\n\n[tools: {tools} · coste ≈ ${result.cost_usd:.4f}]")
    finally:
        await runtime.aclose()


def main() -> None:
    setup_telemetry(os.getenv("OTEL_SERVICE_NAME", "ops-agent-cli"), instrument_httpx=True)
    try:
        asyncio.run(_repl())
    finally:
        shutdown_telemetry()


if __name__ == "__main__":
    main()
