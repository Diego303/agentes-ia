"""Autenticación del servidor MCP como resource server OAuth 2.1 (spec de autorización de MCP).

Dos verificadores con la misma interfaz (``TokenVerifier`` del SDK):

- ``JWTTokenVerifier``: producción. Valida firma (JWKS del IdP: Entra ID, Keycloak...),
  emisor, audiencia (el recurso MCP) y caducidad; los scopes salen de ``scp``/``scope`` o
  de ``roles`` (app roles de Entra ID).
- ``StaticTokenVerifier``: desarrollo y tráfico interno sin IdP. Tokens opacos con scopes,
  leídos de un secreto; comparación en tiempo constante.

Scopes: ``ops:read`` para todas las tools y ``ops:write`` para las que tienen efectos.
"""

from __future__ import annotations

import asyncio
import hmac
import json
import os
from typing import Any

import jwt
from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings

from ops_mcp.integrations.common.scopes import READ_SCOPE, WRITE_SCOPE

__all__ = ["READ_SCOPE", "WRITE_SCOPE", "JWTTokenVerifier", "StaticTokenVerifier", "auth_from_env"]


class StaticTokenVerifier:
    def __init__(self, tokens: dict[str, dict[str, Any]], resource: str) -> None:
        # {"<token>": {"client_id": "ops-agent", "scopes": ["ops:read", "ops:write"]}}
        self._tokens, self._resource = tokens, resource

    async def verify_token(self, token: str) -> AccessToken | None:
        match = None
        for known, info in self._tokens.items():
            if hmac.compare_digest(known.encode(), token.encode()):
                match = info
        if match is None:
            return None
        return AccessToken(
            token=token,
            client_id=match["client_id"],
            scopes=list(match.get("scopes", [])),
            resource=self._resource,
        )


class JWTTokenVerifier:
    def __init__(self, jwks_url: str, issuer: str, audience: str) -> None:
        self._jwks = jwt.PyJWKClient(jwks_url, cache_keys=True)
        self._issuer, self._audience = issuer, audience

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            claims = await asyncio.to_thread(self._decode, token)
        except jwt.PyJWTError:
            return None
        scopes = str(claims.get("scp") or claims.get("scope") or "").split() + list(claims.get("roles", []))
        return AccessToken(
            token=token,
            client_id=str(claims.get("azp") or claims.get("appid") or claims.get("client_id") or ""),
            scopes=scopes,
            expires_at=claims.get("exp"),
            resource=self._audience,
            subject=claims.get("sub"),
            claims={"iss": claims.get("iss")},
        )

    def _decode(self, token: str) -> dict[str, Any]:
        key = self._jwks.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            key.key,
            algorithms=["RS256", "ES256"],
            audience=self._audience,
            issuer=self._issuer,
            options={"require": ["exp", "iss", "aud"]},
        )


def auth_from_env() -> tuple[Any, AuthSettings] | tuple[None, None]:
    """Configura la autenticación desde el entorno; sin configuración, falla en cerrado.

    ``MCP_AUTH_DISABLED=true`` solo para desarrollo local (el servidor avisa al arrancar).
    """
    if os.getenv("MCP_AUTH_DISABLED", "").lower() == "true":
        return None, None
    resource_url = os.environ["MCP_RESOURCE_URL"]
    issuer_url = os.environ["MCP_ISSUER_URL"]
    if jwks_url := os.getenv("MCP_JWKS_URL"):
        verifier: Any = JWTTokenVerifier(jwks_url, issuer_url, resource_url)
    else:
        verifier = StaticTokenVerifier(json.loads(os.environ["MCP_TOKENS"]), resource_url)
    settings = AuthSettings(
        issuer_url=issuer_url,
        resource_server_url=resource_url,
        required_scopes=[READ_SCOPE],
        validate_token_resource=True,  # rechaza tokens emitidos para otro recurso
    )
    return verifier, settings
