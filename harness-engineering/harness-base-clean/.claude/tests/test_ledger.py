from __future__ import annotations

import json
import re
import tempfile
import unittest
from pathlib import Path

import support
import harness_lib as hl
import ledger

MODELS = {
    "claude-sonnet-5": {"input": 2.0, "output": 10.0, "cache_write_5m": 2.5, "cache_write_1h": 4.0, "cache_read": 0.2},
    "claude-opus-5-5": {"input": 4.0, "output": 20.0, "cache_write_5m": 5.0, "cache_write_1h": 8.0, "cache_read": 0.2,
                        "fast_multiplier": 2.0},
    "claude-haiku-4-5": {"input": 1.0, "output": 5.0, "cache_write_5m": 1.25, "cache_write_1h": 2.0, "cache_read": 0.1},
}


class PricingTests(unittest.TestCase):
    def test_usage_splits_cache_ttl(self) -> None:
        counters = ledger.usage_counters(support.usage(output=7, write=100, read=50, one_hour=30))
        self.assertEqual({"input": 10, "output": 7, "cache_write_5m": 100, "cache_write_1h": 30, "cache_read": 50}, counters)

    def test_model_key_strips_date_and_marks_fast(self) -> None:
        self.assertEqual("claude-haiku-4-5", ledger.model_key("claude-haiku-4-5-20251001", "standard"))
        self.assertEqual("claude-opus-5-5|fast", ledger.model_key("claude-opus-5-5", "fast"))

    def test_price_per_category_and_fast(self) -> None:
        counters = {"input": 1_000_000, "output": 1_000_000, "cache_write_5m": 0, "cache_write_1h": 1_000_000, "cache_read": 1_000_000}
        self.assertAlmostEqual(4 + 20 + 8 + 0.2, ledger.price("claude-opus-5-5", counters, MODELS))
        self.assertAlmostEqual(2 * (4 + 20 + 8 + 0.2), ledger.price("claude-opus-5-5|fast", counters, MODELS))
        self.assertIsNone(ledger.price("claude-sonnet-5|fast", counters, MODELS))  # fast sin precio publicado
        self.assertIsNone(ledger.price("claude-desconocido", counters, MODELS))

    def test_budget_status(self) -> None:
        self.assertEqual("BUDGET_OK", ledger.budget_status(1, 5, 20))
        self.assertEqual("BUDGET_WARN", ledger.budget_status(6, 5, 20))
        self.assertEqual("BUDGET_EXCEEDED", ledger.budget_status(21, 5, 20))
        self.assertEqual((20.0, 20.0), ledger.budget({"cost": {"warn_usd": 50, "limit_usd": 20}}, None))
        self.assertEqual((5.0, 3.0)[1], ledger.budget({"cost": {"warn_usd": 5, "limit_usd": 20}}, {"budget_usd": 3})[1])


class TranscriptTests(unittest.TestCase):
    def test_streamed_message_counts_final_usage_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "agent.jsonl"
            lines = [
                {"type": "user", "timestamp": "2026-01-01T00:00:00Z", "message": {"content": "FEATURE_ID: DEMO-001\nPHASE: design\nx"}},
                {"type": "assistant", "timestamp": "2026-01-01T00:00:01Z", "message": {"id": "m1", "model": "claude-haiku-4-5-20251001", "usage": support.usage(1)}},
                {"type": "assistant", "timestamp": "2026-01-01T00:00:02Z", "message": {"id": "m1", "model": "claude-haiku-4-5-20251001", "usage": support.usage(1)}},
                {"type": "assistant", "timestamp": "2026-01-01T00:00:03Z", "message": {"id": "m1", "model": "claude-haiku-4-5-20251001", "usage": support.usage(360)}},
                {"type": "assistant", "timestamp": "2026-01-01T00:00:04Z", "message": {"id": "m2", "model": "<synthetic>", "usage": support.usage(99)}},
            ]
            path.write_text("\n".join(json.dumps(line) for line in lines), encoding="utf-8")
            run = ledger.parse_subagent_transcript(path)
            self.assertEqual({"feature_id": "DEMO-001", "phase": "design"}, run["header"])
            self.assertEqual(360, run["usage"]["claude-haiku-4-5"]["output"])
            self.assertEqual(2000, run["usage"]["claude-haiku-4-5"]["cache_write_5m"])
            self.assertEqual(("2026-01-01T00:00:00Z", "2026-01-01T00:00:04Z"), (run["started_at"], run["finished_at"]))

    def test_header_only_counts_at_the_top_of_the_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "agent.jsonl"
            content = "\n".join(["linea"] * 20 + ["FEATURE_ID: EVIL-001"])
            path.write_text(json.dumps({"type": "user", "message": {"content": content}}), encoding="utf-8")
            self.assertEqual({}, ledger.parse_subagent_transcript(path)["header"])


class HookTests(unittest.TestCase):
    def test_hook_records_harness_runs_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            paths = support.make_project(root)
            transcripts = Path(tmp) / "t"
            support.cli(paths, "add", "DEMO-001", "Demo")
            support.cli(paths, "start", "DEMO-001")
            support.fake_subagent(paths, transcripts, "ajeno", "general-purpose", None)
            support.fake_subagent(paths, transcripts, "sinestado", "explorer", "OTRA-001")
            support.fake_subagent(paths, transcripts, "bueno", "explorer", "DEMO-001")
            runs = [e for e in hl.read_events(paths, "DEMO-001") if e.get("event") == "subagent_stop"]
            self.assertEqual(["bueno"], [r["agent_id"] for r in runs])
            self.assertEqual("explorer", runs[0]["agent"])
            self.assertGreater(runs[0]["cost_usd"], 0)
            self.assertFalse(paths.feature("OTRA-001").exists())
            self.assertIn("OTRA-001", (paths.state / "hook-errors.log").read_text(encoding="utf-8"))

    def test_hook_never_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = support.make_project(Path(tmp))
            self.assertEqual(0, ledger.cmd_hook(paths, "{no es json"))
            self.assertEqual(0, ledger.cmd_hook(paths, json.dumps({"hook_event_name": "SubagentStop", "agent_id": "../../x"})))


class OrchestratorAttributionTests(unittest.TestCase):
    def test_only_turns_mentioning_the_feature_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "main.jsonl"
            lines = [
                {"type": "user", "message": {"content": "pregunta sin relacion"}},
                {"type": "assistant", "message": {"id": "a", "model": "claude-opus-5-5", "usage": support.usage(100)}},
                {"type": "user", "message": {"content": "sigue"}},
                {"type": "assistant", "message": {"id": "b", "model": "claude-opus-5-5", "usage": support.usage(1),
                                                   "content": [{"type": "tool_use", "input": {"command": "feature.py status DEMO-001"}}]}},
                {"type": "user", "message": {"content": [{"type": "tool_result", "content": "ok"}]}},
                {"type": "assistant", "message": {"id": "b2", "model": "claude-opus-5-5", "usage": support.usage(50)}},
                {"type": "assistant", "isSidechain": True, "message": {"id": "s", "model": "claude-opus-5-5", "usage": support.usage(999)}},
                {"type": "user", "message": {"content": "DEMO-0011 no es la misma feature"}},
                {"type": "assistant", "message": {"id": "c", "model": "claude-opus-5-5", "usage": support.usage(7)}},
                {"type": "user", "message": {"content": "compara DEMO-001 con DEMO-002"}},
                {"type": "assistant", "message": {"id": "d", "model": "claude-opus-5-5", "usage": support.usage(40)}},
            ]
            path.write_text("\n".join(json.dumps(line) for line in lines), encoding="utf-8")
            total: dict = {}
            ledger._scan_main_transcript(path, "DEMO-001", {"DEMO-001", "DEMO-002", "DEMO-0011"}, total)
            # 1 + 50 del turno propio y la mitad (20) del turno compartido con DEMO-002
            self.assertEqual(71, round(total["claude-opus-5-5"]["output"]))

    def test_header_tolerates_comments_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "agent.jsonl"
            content = "**FEATURE_ID**: DEMO-001 (demo)\nPHASE: implementation\nATTEMPT: 2  # build\nMODE: repair"
            path.write_text(json.dumps({"type": "user", "message": {"content": content}}), encoding="utf-8")
            header = ledger.parse_subagent_transcript(path)["header"]
            self.assertEqual({"feature_id": "DEMO-001", "phase": "implementation", "attempt": "2", "mode": "repair"}, header)


if __name__ == "__main__":
    unittest.main()
