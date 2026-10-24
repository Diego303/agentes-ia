import time

import httpx2
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from mcp.client.streamable_http import streamable_http_client
from mcp.server.auth.settings import AuthSettings
from starlette.testclient import TestClient

from mcp import Client
from ops_mcp import IncidentStore, build_server
from ops_mcp.app import build_http_app
from ops_mcp.auth import JWTTokenVerifier, StaticTokenVerifier


async def test_lists_tools_with_read_only_annotations():
    async with Client(build_server()) as client:
        tools = {t.name: t for t in (await client.list_tools()).tools}
    assert set(tools) == {
        "get_service_status",
        "get_platform_overview",
        "list_recent_deployments",
        "search_runbooks",
        "create_incident",
    }
    assert tools["get_service_status"].annotations.read_only_hint is True
    assert tools["create_incident"].annotations.read_only_hint is False
    assert "payments-api" in tools["get_service_status"].input_schema["properties"]["service"]["description"]


async def test_status_and_deployments_are_structured():
    async with Client(build_server()) as client:
        status = await client.call_tool("get_service_status", {"service": "payments-api"})
        deploys = await client.call_tool("list_recent_deployments", {"service": "payments-api", "limit": 1})
    assert status.structured_content["status"] == "degraded"
    assert status.structured_content["tier"] == 0
    assert deploys.structured_content["result"][0]["version"] == "v2.14.0"


async def test_platform_overview_lists_problems_first():
    async with Client(build_server()) as client:
        result = await client.call_tool("get_platform_overview", {})
    overview = result.structured_content
    statuses = [s["status"] for s in overview["services"]]
    assert statuses == sorted(statuses, key={"down": 0, "degraded": 1, "healthy": 2}.get)
    assert overview["unhealthy"] == sum(s != "healthy" for s in statuses) > 0


async def test_unknown_service_is_an_actionable_error():
    async with Client(build_server()) as client:
        result = await client.call_tool("get_service_status", {"service": "billing"})
    assert result.is_error
    assert "payments-api" in result.content[0].text


async def test_search_runbooks_finds_rollback_guidance():
    async with Client(build_server()) as client:
        result = await client.call_tool("search_runbooks", {"query": "errores 503 después de un despliegue"})
    runbooks = [hit["runbook"] for hit in result.structured_content["result"]]
    assert "high-error-rate" in runbooks


async def test_create_incident_without_auth_in_local_mode():
    incidents = IncidentStore()
    async with Client(build_server(incidents=incidents)) as client:
        result = await client.call_tool(
            "create_incident",
            {"service": "payments-api", "severity": "SEV2", "summary": "Errores 503 en pagos"},
        )
    assert result.structured_content["id"] == "INC-1001"
    assert incidents.items[0]["created_by"] == "local-dev"


TOKENS = {
    "read-token": {"client_id": "viewer", "scopes": ["ops:read"]},
    "write-token": {"client_id": "ops-agent", "scopes": ["ops:read", "ops:write"]},
}


def _http_app(incidents: IncidentStore):
    resource = "http://testserver/mcp"
    auth = AuthSettings(
        issuer_url="https://idp.example.com",
        resource_server_url=resource,
        required_scopes=["ops:read"],
        validate_token_resource=True,
    )
    server = build_server(
        token_verifier=StaticTokenVerifier(TOKENS, resource), auth=auth, incidents=incidents
    )
    return build_http_app(server, ["testserver", "testserver:*"])


def test_http_requires_bearer_token_and_valid_host():
    with TestClient(_http_app(IncidentStore())) as client:
        response = client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        metadata = client.get("/.well-known/oauth-protected-resource/mcp")
        rebinding = client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            headers={"Host": "evil.example", "Authorization": "Bearer write-token"},
        )
    assert response.status_code == 401
    assert "resource_metadata" in response.headers.get("www-authenticate", "")
    assert metadata.json()["authorization_servers"] == ["https://idp.example.com"]
    assert rebinding.status_code == 421


@pytest.mark.parametrize(("token", "allowed"), [("read-token", False), ("write-token", True)])
async def test_write_tool_requires_write_scope(token, allowed):
    incidents = IncidentStore()
    app = _http_app(incidents)
    http = httpx2.AsyncClient(
        transport=httpx2.ASGITransport(app=app),
        headers={"Authorization": f"Bearer {token}"},
        base_url="http://testserver",
    )
    async with app.router.lifespan_context(app), http:
        async with Client(streamable_http_client("http://testserver/mcp", http_client=http)) as client:
            status = await client.call_tool("get_service_status", {"service": "search-api"})
            created = await client.call_tool(
                "create_incident",
                {"service": "search-api", "severity": "SEV3", "summary": "Prueba de permisos"},
            )
    assert not status.is_error
    assert created.is_error is (not allowed)
    assert len(incidents.items) == (1 if allowed else 0)


async def test_jwt_verifier_checks_audience_and_maps_scopes():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    verifier = JWTTokenVerifier("https://idp.example.com/jwks", "https://idp.example.com", "http://mcp/mcp")

    class _Key:
        def __init__(self):
            self.key = key.public_key()

    verifier._jwks.get_signing_key_from_jwt = lambda _token: _Key()
    claims = {
        "iss": "https://idp.example.com",
        "aud": "http://mcp/mcp",
        "exp": int(time.time()) + 60,
        "azp": "ops-agent",
    }
    good = jwt.encode({**claims, "scp": "ops:read ops:write"}, key, algorithm="RS256")
    wrong_audience = jwt.encode({**claims, "aud": "http://otro"}, key, algorithm="RS256")

    token = await verifier.verify_token(good)
    assert token.client_id == "ops-agent" and token.scopes == ["ops:read", "ops:write"]
    assert await verifier.verify_token(wrong_audience) is None
