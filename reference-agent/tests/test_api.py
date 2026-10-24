from starlette.testclient import TestClient

from agent_fixtures import make_agent
from opsagent.api import build_app
from opsagent.testing import reply, text, tool_use


def test_chat_and_approval_over_http():
    agent, _, incidents = make_agent(
        [
            reply(
                tool_use(
                    "create_incident",
                    {"service": "search-api", "severity": "SEV3", "summary": "Prueba por HTTP"},
                )
            ),
            reply(text("Creado.")),
        ]
    )
    headers = {"Authorization": "Bearer secreto"}
    with TestClient(build_app(agent, ["secreto"])) as client:
        assert client.post("/v1/chat", json={"message": "hola"}).status_code == 401
        first = client.post("/v1/chat", json={"message": "crea un incidente"}, headers=headers).json()
        assert first["stop"] == "approval_required"
        second = client.post(
            f"/v1/sessions/{first['session_id']}/approval", json={"approve": True}, headers=headers
        ).json()
        assert second["reply"] == "Creado."
        assert (
            client.post(
                f"/v1/sessions/{first['session_id']}/approval", json={"approve": True}, headers=headers
            ).status_code
            == 409
        )
        assert client.post("/v1/chat", json={"message": ""}, headers=headers).status_code == 400
    assert len(incidents.items) == 1
