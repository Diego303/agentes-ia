"""Motor 0.8.0: H-01, H-02, H-05, presupuestos, especialistas por tags/rutas y metricas agregadas."""

from __future__ import annotations

import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

import support
import feature
import harness_lib as hl

FID = "DEMO-001"


class EngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "repo"
        self.root.mkdir()
        self.transcripts = Path(self._tmp.name) / "transcripts"
        self.paths = support.make_project(self.root)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def state(self) -> dict:
        return hl.load_yaml(self.paths.feature(FID) / "state.yaml")

    def build_and_fail(self, verdict: str, repairable: bool = False) -> None:
        support.write(self.root / "src" / "app.py", "def greet():\n    return 'hello'\n")
        support.write(self.paths.feature(FID) / "implementation.md", "## Build 1\n- T-01 -> src/app.py\n")
        support.fake_subagent(self.paths, self.transcripts, "a-bld1", "builder", FID, phase="implementation")
        self.assertEqual(0, support.cli(self.paths, "transition", FID, "build_complete")[0])
        support.verification_result(self.paths, FID, verdict, 1, 1, repairable=repairable)
        support.fake_subagent(self.paths, self.transcripts, "a-rev1", "reviewer", FID, phase="verification")

    def test_mode_repair_only_after_repairable_failure(self) -> None:
        support.advance_to_implementation(self, self.paths, self.transcripts, FID)
        self.assertIn("MODE: build", self.state()["next_action"])
        self.build_and_fail("FAIL_REPAIRABLE", repairable=True)
        hl.dump_yaml(self.paths.feature(FID) / "repair-request.yaml", {
            "version": 1, "feature_id": FID, "build_attempt": 2, "source_verification_attempt": 1,
            "failing_checks": ["AC-002"], "blocking_issues": [], "failure_summary": "saludo en ingles",
            "reproduction": "grep -q hola src/app.py", "allowed_scope": ["src/app.py"],
            "acceptance_must_remain_unchanged": True,
        })
        code, out = support.cli(self.paths, "transition", FID, "repairable_failure")
        self.assertEqual(0, code, out)
        self.assertIn("ATTEMPT: 2, MODE: repair", self.state()["next_action"])

    def test_retry_exploration_resets_the_gate_like_replan(self) -> None:
        support.advance_to_implementation(self, self.paths, self.transcripts, FID)
        self.build_and_fail("FAIL_NONREPAIRABLE")
        self.assertEqual(0, support.cli(self.paths, "transition", FID, "human_required", "--reason", "spec mala")[0])
        code, out = support.cli(self.paths, "transition", FID, "retry_exploration", "--by", "human",
                                "--response", "explora de nuevo")
        self.assertEqual(0, code, out)
        state = self.state()
        self.assertEqual("exploration", state["phase"])
        self.assertEqual("pending", state["gate1"]["status"])
        self.assertEqual({"build": 0, "verification": 0, "repair": 0, "human_retries": 0}, state["attempts"])
        self.assertIsNone(state["base_commit"])
        self.assertFalse((self.paths.feature(FID) / "SDD" / "spec.lock.json").exists())

    def test_lock_staleness_uses_last_activity(self) -> None:
        old = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
        recent = hl.now_iso()
        state = {"updated_at": old, "lock": {"active": True, "since": old}}
        events = [{"ts": old, "event": "transition"}, {"ts": old, "event": "subagent_stop", "finished_at": recent}]
        self.assertEqual(hl.parse_iso(recent), feature._last_activity(state, events))
        self.assertEqual(hl.parse_iso(old), feature._last_activity(state, events[:1]))

    def test_budget_must_be_positive(self) -> None:
        code, out = support.cli(self.paths, "add", FID, "Demo", "--budget", "0")
        self.assertEqual(2, code)
        self.assertIn("mayor que 0", out)
        self.assertEqual(0, support.cli(self.paths, "add", "F4-PORT-AGENT-01", "ID con varios segmentos")[0])
        self.assertEqual(2, support.cli(self.paths, "add", "../X-1", "ID con ruta")[0])

    def test_specialists_by_tags_and_paths(self) -> None:
        registry = {"agents": [
            {"name": "explorer", "role": "canonical", "phase": "exploration"},
            {"name": "security-auditor", "role": "specialist", "insertion": "post-implementation",
             "phase": "verification", "triggers_on_tags": ["auth"], "triggers_on_paths": ["src/auth/*", "*.sql"]},
            {"name": "test-strategist", "role": "specialist", "insertion": "pre-gate1", "phase": "design",
             "triggers_on_tags": ["*"]},
            {"name": "docs-keeper", "role": "specialist", "insertion": "post-verification", "triggers_on_tags": ["docs"]},
        ]}
        chosen = feature.select_specialists(registry, ["ui"], "post-implementation", ["src/auth/login.py", "README.md"])
        self.assertEqual(["security-auditor"], [item["name"] for item in chosen])
        self.assertIn("ruta src/auth/login.py ~ src/auth/*", chosen[0]["reasons"])
        self.assertEqual([], feature.select_specialists(registry, ["ui"], "post-implementation", ["README.md"]))
        self.assertEqual(["tag auth"], feature.select_specialists(registry, ["AUTH"], "post-implementation", [])[0]["reasons"])
        self.assertEqual(["siempre"], feature.select_specialists(registry, [], "pre-gate1", [])[0]["reasons"])
        # Las rutas solo cuentan en post-implementation
        self.assertEqual([], feature.select_specialists(registry, [], "post-verification", ["docs/x.md"]))

        hl.dump_yaml(self.paths.registry, registry)
        support.cli(self.paths, "add", FID, "Demo", "--tags", "docs")
        code, out = support.cli(self.paths, "specialists", FID, "--insertion", "post-verification", "--json")
        self.assertEqual(0, code, out)
        self.assertEqual("docs-keeper", json.loads(out)["specialists"]["post-verification"][0]["name"])


class MetricsTests(unittest.TestCase):
    def make_feature(self, root: Path, fid: str, phase: str, moves: list[tuple[str, str, str]],
                     runs: list[str], cost: float | None) -> None:
        folder = root / fid
        folder.mkdir(parents=True)
        hl.dump_yaml(folder / "state.yaml", {"feature_id": fid, "phase": phase, "created_at": "2026-10-01T10:00:00Z"})
        events = [{"ts": "2026-10-01T10:00:00Z", "event": "feature_started"}]
        for index, (name, source, target) in enumerate(moves):
            events.append({"ts": f"2026-10-01T1{index % 10}:30:00Z", "event": "transition", "transition": name,
                           "from": source, "to": target, "by": "human" if name == "approved" else "orchestrator"})
        for index, agent in enumerate(runs):
            events.append({"ts": "2026-10-01T11:00:00Z", "event": "subagent_stop", "agent": agent, "agent_id": f"{fid}-{index}"})
            events.append({"ts": "2026-10-01T11:00:01Z", "event": "subagent_stop", "agent": agent, "agent_id": f"{fid}-{index}"})
        (folder / "event.log").write_text("\n".join(json.dumps(e) for e in events) + "\nno-json\n", encoding="utf-8")
        if cost is not None:
            hl.dump_json(folder / "cost.json", {"total_usd": cost, "by_agent": {"builder": {"cost_usd": cost / 2}},
                                                "orchestrator": {"cost_usd": cost / 4}})

    def test_aggregates_a_state_directory(self) -> None:
        start = [("start_exploration", "intake", "exploration"), ("exploration_complete", "exploration", "design"),
                 ("design_complete", "design", "gate1_pending")]
        build = [("approved", "gate1_pending", "implementation"), ("build_complete", "implementation", "verification")]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_feature(root, "A-001", "archived", start + build + [("pass", "verification", "archived")],
                              ["explorer", "designer", "builder", "reviewer"], 10.0)
            self.make_feature(root, "B-002", "archived", start + [("changes_requested", "gate1_pending", "design"),
                              ("design_complete", "design", "gate1_pending")] + build
                              + [("repairable_failure", "verification", "implementation"),
                                 ("build_complete", "implementation", "verification"), ("pass", "verification", "archived")],
                              ["explorer", "designer", "designer", "builder", "reviewer", "builder", "reviewer"], 30.0)
            self.make_feature(root, "C-003", "blocked", start + build + [("human_required", "verification", "blocked")],
                              ["explorer"], None)
            (root / "hook-errors.log").write_text("x", encoding="utf-8")
            data = feature.collect_metrics(root)
        self.assertEqual(3, data["features"])
        self.assertEqual({"archived": 2, "blocked": 1}, data["by_phase"])
        self.assertEqual({"first_pass": 1, "with_repair": 1, "first_pass_rate": 0.5, "repairs": 1}, data["verification"])
        self.assertEqual(4, data["gate1"]["presented"])
        self.assertEqual({"human": 3}, data["gate1"]["approved_by"])
        self.assertEqual(1, data["gate1"]["changes_requested"])
        self.assertEqual(1, data["human_interventions"]["features_blocked_ever"])
        self.assertEqual(12, data["subagent_runs"]["total"])  # deduplicadas por agent_id
        self.assertEqual({"features_with_cost": 2, "total": 40.0, "mean": 20.0, "median": 20.0, "p90": 30.0},
                         {k: v for k, v in data["cost_usd"].items() if k != "by_agent"})
        self.assertEqual({"builder": 20.0, "orquestador": 10.0}, data["cost_usd"]["by_agent"])
        self.assertIsNotNone(data["lead_time_hours"]["median"])

    def test_cli_reads_an_external_state_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_feature(root / "state", "A-001", "archived", [("pass", "verification", "archived")], [], 5.0)
            (root / "repo").mkdir()
            paths = support.make_project(root / "repo")
            code, out = support.cli(paths, "metrics", "--state-dir", str(root / "state"))
            self.assertEqual(0, code, out)
            self.assertIn("PASS a la primera 1/1", out)
            self.assertEqual(1, support.cli(paths, "metrics", "--state-dir", str(root / "no-existe"))[0])


if __name__ == "__main__":
    unittest.main()
