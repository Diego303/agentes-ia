import pytest

from agent_fixtures import assert_history_is_valid, make_agent, tool_results
from opsagent import Settings
from opsagent.agent import REFUSAL_REPLY
from opsagent.testing import reply, text, tool_use


async def test_full_diagnosis_uses_mcp_and_a2a(spans):
    agent, llm, _ = make_agent(
        [
            reply(tool_use("get_service_status", {"service": "payments-api"}, "t1")),
            reply(
                tool_use("list_recent_deployments", {"service": "payments-api"}, "t2"),
                tool_use("search_runbooks", {"query": "errores 503 tras despliegue"}, "t3"),
            ),
            reply(
                tool_use(
                    "consult_change_advisor",
                    {"service": "payments-api", "action": "rollback", "incident_severity": "SEV2"},
                    "t4",
                )
            ),
            reply(
                text("Diagnóstico: v2.14.0 redujo el pool. Rollback aprobado (runbook deployment-rollback).")
            ),
        ]
    )
    result = await agent.chat("payments-api da 503, ¿qué hago?")

    assert result.stop == "end_turn"
    assert [s["tool"] for s in result.trajectory] == [
        "get_service_status",
        "list_recent_deployments",
        "search_runbooks",
        "consult_change_advisor",
    ]
    advisor_result = tool_results(llm.requests[3])[0]["content"]
    assert '"decision": "approved"' in advisor_result
    assert advisor_result.startswith('<untrusted_data source="consult_change_advisor">')
    assert llm.requests[0]["thinking"] == {"type": "adaptive"}
    assert result.cost_usd > 0
    assert_history_is_valid(agent.store.get(result.session_id)["messages"])

    names = [s.name for s in spans.get_finished_spans()]
    assert "invoke_agent ops-assistant" in names
    assert "execute_tool consult_change_advisor" in names
    assert any(n.startswith("tools/call") for n in names)  # span del SDK de MCP


async def test_side_effect_waits_for_approval_and_runs_when_approved():
    agent, llm, incidents = make_agent(
        [
            reply(
                text("Propongo declarar un SEV2."),
                tool_use(
                    "create_incident",
                    {
                        "service": "payments-api",
                        "severity": "SEV2",
                        "summary": "Errores 503 en pagos tras v2.14.0",
                    },
                    "c1",
                ),
            ),
            reply(text("Incidente INC-1001 creado.")),
        ]
    )
    first = await agent.chat("Declara un incidente para payments-api")
    assert first.stop == "approval_required"
    assert first.pending_approval["name"] == "create_incident"
    assert not incidents.items

    second = await agent.resolve_approval(first.session_id, approve=True)
    assert second.stop == "end_turn"
    assert incidents.items[0]["severity"] == "SEV2"
    assert "INC-1001" in tool_results(llm.requests[1])[0]["content"]
    assert_history_is_valid(agent.store.get(first.session_id)["messages"])


async def test_rejected_approval_does_not_execute():
    agent, llm, incidents = make_agent(
        [
            reply(
                tool_use(
                    "create_incident",
                    {"service": "search-api", "severity": "SEV3", "summary": "Prueba de rechazo"},
                )
            ),
            reply(text("De acuerdo, no lo creo.")),
        ]
    )
    first = await agent.chat("crea un incidente")
    await agent.resolve_approval(first.session_id, approve=False)
    assert not incidents.items
    assert tool_results(llm.requests[1])[0]["is_error"] is True


async def test_new_message_declines_pending_action():
    agent, llm, incidents = make_agent(
        [
            reply(
                tool_use(
                    "create_incident",
                    {"service": "search-api", "severity": "SEV3", "summary": "Prueba implícita"},
                    "c1",
                )
            ),
            reply(text("Vale, olvidamos el incidente.")),
        ]
    )
    first = await agent.chat("crea un incidente")
    await agent.chat("mejor no, dime solo el estado", session_id=first.session_id)
    last_user = llm.requests[1]["messages"][-1]["content"]
    assert last_user[0]["type"] == "tool_result" and last_user[0]["is_error"] is True
    assert last_user[-1] == {"type": "text", "text": "mejor no, dime solo el estado"}
    assert not incidents.items


async def test_injection_taints_session_and_blocks_side_effects():
    agent, llm, incidents = make_agent(
        [
            reply(tool_use("list_recent_deployments", {"service": "orders-worker"}, "d1")),
            reply(
                tool_use(
                    "create_incident",
                    {
                        "service": "auth-service",
                        "severity": "SEV1",
                        "summary": "La base de datos de usuarios fue borrada",
                    },
                    "c1",
                )
            ),
            reply(text("El historial de despliegues contiene instrucciones sospechosas; no he creado nada.")),
        ]
    )
    result = await agent.chat("¿Qué ha cambiado en orders-worker?")
    assert result.tainted
    assert result.stop == "end_turn"  # denegada sin pedir aprobación
    assert any(step.get("guardrail") == "injection" for step in result.trajectory)
    assert "bloqueada" in tool_results(llm.requests[2])[0]["content"]
    assert not incidents.items


async def test_refusal_is_not_appended_and_session_continues():
    agent, _, _ = make_agent(
        [reply(text(""), stop_reason="refusal"), reply(text("payments-api está degradado."))]
    )
    first = await agent.chat("algo que el modelo rechaza")
    assert first.stop == "refusal" and first.reply == REFUSAL_REPLY
    assert agent.store.get(first.session_id)["messages"][-1]["role"] == "user"
    second = await agent.chat("¿cómo está payments-api?", session_id=first.session_id)
    assert second.stop == "end_turn"


async def test_iteration_budget_stops_the_loop():
    loop = [reply(tool_use("get_service_status", {"service": "search-api"}, f"s{i}")) for i in range(3)]
    agent, _, _ = make_agent(loop, Settings(max_iterations=2))
    result = await agent.chat("bucle")
    assert result.stop == "budget"


async def test_unknown_tool_is_denied():
    agent, llm, _ = make_agent(
        [reply(tool_use("delete_cluster", {"name": "prod"})), reply(text("No tengo esa herramienta."))]
    )
    await agent.chat("borra el clúster")
    assert "lista blanca" in tool_results(llm.requests[1])[0]["content"]


async def test_final_reply_is_redacted():
    agent, _, _ = make_agent(
        [reply(text("Escribe a ana.garcia@example.com con la clave sk-ant-abcdefghijklmnopqrstuv"))]
    )
    result = await agent.chat("¿a quién aviso?")
    assert "example.com" not in result.reply and "sk-ant" not in result.reply


async def test_resolve_without_pending_is_an_error():
    agent, _, _ = make_agent([])
    with pytest.raises(LookupError):
        await agent.resolve_approval("no-existe", approve=True)
