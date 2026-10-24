from datetime import UTC, datetime

import httpx
import pytest

from change_advisor import ChangeAdvisorClient, ChangeRequest, evaluate
from change_advisor.client import ChangeAdvisorError
from change_advisor.executor import ChangeAdvisorExecutor
from change_advisor.server import build_app

WEDNESDAY = datetime(2026, 10, 21, 11, 0, tzinfo=UTC)
SATURDAY = datetime(2026, 10, 24, 11, 0, tzinfo=UTC)


@pytest.mark.parametrize(
    ("request_", "now", "decision"),
    [
        (ChangeRequest("payments-api", "rollback", incident_severity="SEV2"), WEDNESDAY, "approved"),
        (ChangeRequest("payments-api", "deploy", incident_severity="SEV2"), WEDNESDAY, "rejected"),
        (ChangeRequest("payments-api", "restart"), WEDNESDAY, "needs_approval"),
        (ChangeRequest("orders-worker", "scale"), SATURDAY, "approved"),
        (ChangeRequest("search-api", "deploy"), SATURDAY, "needs_approval"),
        (ChangeRequest("search-api", "deploy"), WEDNESDAY, "approved"),
        (
            ChangeRequest("search-api", "deploy", environment="staging", incident_severity="SEV1"),
            WEDNESDAY,
            "approved",
        ),
        (ChangeRequest("search-api", "delete-cluster"), WEDNESDAY, "rejected"),
    ],
)
def test_policy(request_, now, decision):
    assert evaluate(request_, now).decision == decision


def test_tier0_mitigation_requires_notifying_incident_commander():
    verdict = evaluate(ChangeRequest("auth-service", "rollback", incident_severity="SEV1"), WEDNESDAY)
    assert any("incident commander" in c for c in verdict.conditions)


def _client(token: str = "secret") -> ChangeAdvisorClient:
    app = build_app("http://advisor/", ["secret"], executor=ChangeAdvisorExecutor(clock=lambda: WEDNESDAY))
    http = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://advisor/")
    return ChangeAdvisorClient("http://advisor/", token, http_client=http)


async def test_a2a_roundtrip_returns_verdict():
    client = _client()
    try:
        verdict = await client.evaluate(
            {"service": "payments-api", "action": "rollback", "incident_severity": "SEV2"}
        )
    finally:
        await client.aclose()
    assert verdict["decision"] == "approved"
    assert verdict["conditions"]


async def test_agent_card_is_public_and_declares_bearer():
    app = build_app("http://advisor/", ["secret"])
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://advisor") as http:
        card = (await http.get("/.well-known/agent-card.json")).json()
        unauthorized = await http.post(
            "/", json={"jsonrpc": "2.0", "id": 1, "method": "SendMessage", "params": {}}
        )
    assert card["name"] == "change-advisor"
    assert "bearer" in card["securitySchemes"]
    assert unauthorized.status_code == 401


async def test_invalid_request_is_rejected():
    client = _client()
    try:
        with pytest.raises(ChangeAdvisorError):
            await client.evaluate({"servicio": "x"})
    finally:
        await client.aclose()
