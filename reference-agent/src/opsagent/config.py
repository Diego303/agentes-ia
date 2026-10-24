"""Configuración por variables de entorno (12-factor): la misma imagen en local y en Kubernetes."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    model: str = "claude-opus-5-5"
    effort: str = "medium"
    max_tokens: int = 16000
    max_iterations: int = 8
    max_tool_calls: int = 12
    # Gateway LLM (LiteLLM). Sin él, el SDK habla directamente con la API de Anthropic.
    gateway_url: str | None = None
    gateway_key: str | None = None
    # Servidor MCP. Sin URL, el agente lanza ops-mcp como subproceso stdio (desarrollo local).
    mcp_url: str | None = None
    mcp_token: str | None = None
    # Change advisor (A2A). Sin URL, se sirve en el mismo proceso (desarrollo local).
    advisor_url: str | None = None
    advisor_token: str | None = None
    api_tokens: list[str] = field(default_factory=list)

    @classmethod
    def from_env(cls) -> Settings:
        env = os.environ.get
        return cls(
            model=env("OPSAGENT_MODEL", cls.model),
            effort=env("OPSAGENT_EFFORT", cls.effort),
            max_tokens=int(env("OPSAGENT_MAX_TOKENS", str(cls.max_tokens))),
            max_iterations=int(env("OPSAGENT_MAX_ITERATIONS", str(cls.max_iterations))),
            max_tool_calls=int(env("OPSAGENT_MAX_TOOL_CALLS", str(cls.max_tool_calls))),
            gateway_url=env("LLM_GATEWAY_URL"),
            gateway_key=env("LLM_GATEWAY_KEY"),
            mcp_url=env("MCP_URL"),
            mcp_token=env("MCP_TOKEN"),
            advisor_url=env("ADVISOR_URL"),
            advisor_token=env("ADVISOR_TOKEN"),
            api_tokens=json.loads(env("AGENT_API_TOKENS", "[]")),
        )
