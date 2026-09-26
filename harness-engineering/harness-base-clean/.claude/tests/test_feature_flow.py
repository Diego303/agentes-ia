"""Flujo completo con el motor de estado, el libro mayor y el runner (subagentes simulados)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import support
import harness_lib as hl
import run_acceptance
import validate_harness as vh

FID = "DEMO-001"


class FeatureFlowTests(unittest.TestCase):
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

    def run_acceptance(self) -> int:
        return support.quiet(run_acceptance.main, ["--root", str(self.root), "--feature", FID])[0]

    def build(self, attempt: int, greeting: str) -> None:
        support.write(self.root / "src" / "app.py", f"def greet():\n    return '{greeting}'\n")
        report = self.paths.feature(FID) / "implementation.md"
        previous = report.read_text(encoding="utf-8") if report.exists() else ""
        support.write(report, previous + f"## Build {attempt}\n- T-01 -> src/app.py\n")
        support.fake_subagent(self.paths, self.transcripts, f"a-bld{attempt}", "builder", FID, phase="implementation")

    def test_happy_path_with_one_repair(self) -> None:
        support.advance_to_implementation(self, self.paths, self.transcripts, FID)
        state = self.state()
        self.assertEqual("implementation", state["phase"])
        self.assertEqual("approved", state["gate1"]["status"])
        self.assertEqual(1, state["attempts"]["build"])
        self.assertTrue((self.paths.feature(FID) / "SDD" / "spec.lock.json").is_file())

        # Build 1 con un defecto: el saludo no esta en espanol.
        self.build(1, "hello")
        self.assertEqual(0, support.cli(self.paths, "transition", FID, "build_complete")[0])
        self.assertEqual(1, self.run_acceptance())  # AC-002 falla
        support.verification_result(self.paths, FID, "FAIL_REPAIRABLE", 1, 1, repairable=True)
        hl.dump_yaml(self.paths.feature(FID) / "repair-request.yaml", {
            "version": 1, "feature_id": FID, "build_attempt": 2, "source_verification_attempt": 1,
            "failing_checks": ["AC-002"], "blocking_issues": [], "failure_summary": "saludo en ingles",
            "reproduction": "grep -q hola src/app.py", "allowed_scope": ["src/app.py"],
            "acceptance_must_remain_unchanged": True,
        })
        support.fake_subagent(self.paths, self.transcripts, "a-rev1", "reviewer", FID, phase="verification")
        self.assertEqual(0, support.cli(self.paths, "transition", FID, "repairable_failure")[0])
        self.assertEqual({"build": 2, "verification": 1, "repair": 1, "human_retries": 0}, self.state()["attempts"])

        # Build 2 (repair) y verificacion 2 con PASS.
        self.build(2, "hola")
        self.assertEqual(0, support.cli(self.paths, "transition", FID, "build_complete")[0])
        self.assertEqual(0, self.run_acceptance())
        support.verification_result(self.paths, FID, "PASS", 2, 2)
        support.write(self.paths.feature(FID) / "archive.md", "## Resumen\nSaludo implementado.\n")
        support.fake_subagent(self.paths, self.transcripts, "a-rev2", "reviewer", FID, phase="verification")
        code, out = support.cli(self.paths, "transition", FID, "pass")
        self.assertEqual(0, code, out)

        state = self.state()
        self.assertEqual(("archived", "archived", False), (state["phase"], state["status"], state["lock"]["active"]))
        self.assertEqual("PASS", state["last_verdict"])
        self.assertEqual("archived", hl.find_feature(self.paths, FID)["status"])
        cost = hl.load_json(self.paths.feature(FID) / "cost.json")
        self.assertGreater(cost["total_usd"], 0)
        self.assertEqual({"builder", "designer", "explorer", "reviewer"}, set(cost["by_agent"]))
        self.assertEqual(2, cost["by_agent"]["builder"]["runs"])
        errors = [i for i in vh.validate(self.root).issues if i.severity == "error"]
        self.assertEqual([], errors)

    def test_guards_reject_illegal_transitions(self) -> None:
        support.cli(self.paths, "add", FID, "Demo")
        support.cli(self.paths, "start", FID)
        support.cli(self.paths, "transition", FID, "start_exploration")
        code, out = support.cli(self.paths, "transition", FID, "exploration_complete")
        self.assertEqual(1, code)
        self.assertIn("explorer_runtime_recorded", out)
        self.assertIn("context_present", out)
        code, out = support.cli(self.paths, "transition", FID, "approved", "--by", "human", "--response", "x")
        self.assertEqual(1, code)
        self.assertIn("no existe desde 'exploration'", out)
        self.assertEqual("exploration", self.state()["phase"])

    def test_gate_requires_explicit_human_or_authorized_yolo(self) -> None:
        support.cli(self.paths, "add", FID, "Demo", "--tags", "auth")
        support.cli(self.paths, "start", FID)
        support.cli(self.paths, "transition", FID, "start_exploration")
        support.write(self.paths.feature(FID) / "SDD" / "context.md", "## Resumen\nDemo.\n")
        support.fake_subagent(self.paths, self.transcripts, "a1", "explorer", FID)
        support.cli(self.paths, "transition", FID, "exploration_complete")
        support.write_sdd(self.paths, FID)
        support.fake_subagent(self.paths, self.transcripts, "a2", "designer", FID, phase="design")
        self.assertEqual(0, support.cli(self.paths, "transition", FID, "design_complete")[0])

        code, out = support.cli(self.paths, "transition", FID, "approved")
        self.assertEqual(1, code)
        self.assertIn("decision_recorded", out)
        code, out = support.cli(self.paths, "transition", FID, "approved", "--by", "yolo-mode",
                                "--response", "auto-approve", "--rationale", "regla X")
        self.assertEqual(1, code)
        self.assertIn('mode = "yolo"', out)
        self.assertIn("exigen aprobacion humana", out)  # tag auth protegido
        self.assertEqual("gate1_pending", self.state()["phase"])

    def test_frozen_spec_blocks_build_and_acceptance(self) -> None:
        support.advance_to_implementation(self, self.paths, self.transcripts, FID)
        design = self.paths.feature(FID) / "SDD" / "design.md"
        design.write_text(design.read_text(encoding="utf-8") + "\nCambio no aprobado.\n", encoding="utf-8")
        self.build(1, "hola")
        code, out = support.cli(self.paths, "transition", FID, "build_complete")
        self.assertEqual(1, code)
        self.assertIn("design.md cambio despues de GATE#1", out)
        self.assertEqual(2, self.run_acceptance())

    def test_second_failure_goes_to_human_and_retry_is_human(self) -> None:
        support.advance_to_implementation(self, self.paths, self.transcripts, FID)
        self.build(1, "hello")
        support.cli(self.paths, "transition", FID, "build_complete")
        support.verification_result(self.paths, FID, "FAIL_NONREPAIRABLE", 1, 1)
        support.fake_subagent(self.paths, self.transcripts, "a-rev1", "reviewer", FID, phase="verification")
        self.assertEqual(1, support.cli(self.paths, "transition", FID, "repairable_failure")[0])
        code, out = support.cli(self.paths, "transition", FID, "human_required")
        self.assertEqual(1, code)
        self.assertIn("reason_recorded", out)
        self.assertEqual(0, support.cli(self.paths, "transition", FID, "human_required", "--reason", "spec incorrecta")[0])
        state = self.state()
        self.assertEqual(("blocked", "blocked", False), (state["phase"], state["status"], state["lock"]["active"]))
        self.assertEqual(1, support.cli(self.paths, "transition", FID, "retry_build")[0])
        code, out = support.cli(self.paths, "transition", FID, "retry_build", "--by", "human", "--response", "reintenta")
        self.assertEqual(0, code, out)
        self.assertEqual({"build": 2, "verification": 1, "repair": 0, "human_retries": 1}, self.state()["attempts"])

    def test_budget_exceeded_stops_new_work(self) -> None:
        support.cli(self.paths, "add", FID, "Demo", "--budget", "0.0001")
        support.cli(self.paths, "start", FID)
        support.cli(self.paths, "transition", FID, "start_exploration")
        support.write(self.paths.feature(FID) / "SDD" / "context.md", "## Resumen\nDemo.\n")
        support.fake_subagent(self.paths, self.transcripts, "a1", "explorer", FID)
        code, out = support.cli(self.paths, "transition", FID, "exploration_complete")
        self.assertEqual(1, code)
        self.assertIn("BUDGET_EXCEEDED", out)
        self.assertEqual(0, support.cli(self.paths, "transition", FID, "escalate", "--reason", "presupuesto")[0])


if __name__ == "__main__":
    unittest.main()
