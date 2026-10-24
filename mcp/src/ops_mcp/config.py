"""Configuración del proceso desde variables de entorno.

La autenticación tiene su propia lectura del entorno en ``auth.auth_from_env``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    host: str = "0.0.0.0"  # noqa: S104 - en un contenedor escucha en todas las interfaces
    port: int = 8000
    allowed_hosts: tuple[str, ...] = ("127.0.0.1:*", "localhost:*")
    log_level: str = "INFO"
    log_format: str = "json"

    @classmethod
    def from_env(cls) -> Settings:
        hosts = os.getenv("MCP_ALLOWED_HOSTS")
        return cls(
            host=os.getenv("HOST", cls.host),
            port=int(os.getenv("PORT", str(cls.port))),
            allowed_hosts=tuple(h for h in hosts.split(",") if h) if hosts else cls.allowed_hosts,
            log_level=os.getenv("MCP_LOG_LEVEL", cls.log_level),
            log_format=os.getenv("MCP_LOG_FORMAT", cls.log_format),
        )
