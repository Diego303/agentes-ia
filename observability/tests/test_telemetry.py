from types import SimpleNamespace

import pytest

from opsagent_telemetry import agent_span, cost_usd, record_guardrail_event, record_llm_usage, tool_span


def test_cost_uses_cache_categories():
    usage = {
        "input_tokens": 1_000_000,
        "output_tokens": 100_000,
        "cache_creation_input_tokens": 200_000,
        "cache_read_input_tokens": 1_000_000,
    }
    # 4 + 2 + 1 + 0.2
    assert cost_usd("claude-opus-5-5", usage) == pytest.approx(7.2)


def test_long_context_tier_applies_per_request():
    short = {"input_tokens": 50_000, "output_tokens": 1_000}
    long = {"input_tokens": 20_000, "cache_read_input_tokens": 90_000, "output_tokens": 1_000}
    assert cost_usd("claude-haiku-5-5", short) == pytest.approx((50_000 * 0.10 + 1_000 * 0.50) / 1e6)
    assert cost_usd("claude-haiku-5-5", long) == pytest.approx(
        (20_000 * 0.50 + 90_000 * 0.05 + 1_000 * 2.50) / 1e6
    )


def test_unknown_model_has_no_price():
    assert cost_usd("modelo-inventado", {"input_tokens": 10}) is None


def test_span_tree_follows_genai_conventions(spans):
    with agent_span("ops-assistant", "conv-1", "claude-opus-5-5"):
        with tool_span("search_runbooks", "toolu_1", "extension"):
            record_guardrail_event("injection", "flagged")
        record_llm_usage("claude-opus-5-5", SimpleNamespace(input_tokens=10, output_tokens=5))

    finished = {s.name: s for s in spans.get_finished_spans()}
    agent, tool = finished["invoke_agent ops-assistant"], finished["execute_tool search_runbooks"]
    assert tool.parent.span_id == agent.context.span_id
    assert agent.attributes["gen_ai.operation.name"] == "invoke_agent"
    assert agent.attributes["gen_ai.conversation.id"] == "conv-1"
    assert tool.attributes["gen_ai.tool.type"] == "extension"
    assert tool.events[0].attributes["kind"] == "injection"
