from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import support
import harness_lib as hl
import run_acceptance

FID = "DEMO-001"
EXTRA_CHECKS = """  - id: AC-003
    title: herramienta ausente
    covers: [FR-01]
    kind: command
    required: false
    command: comando-que-no-existe-xyz
    cwd: .
    timeout_seconds: 10
    expected_exit_code: 0
  - id: AC-004
    title: sin secretos
    covers: [FR-01]
    kind: file
    required: false
    path: src/app.py
    expected: exists
    not_contains: "password"
  - id: AC-005
    title: revision manual
    covers: [FR-01]
    kind: inspection
    required: false
    procedure: lee el codigo
    expected: es legible
"""


class RunAcceptanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "repo"
        self.root.mkdir()
        self.paths = support.make_project(self.root)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_tool(self, *extra: str) -> int:
        return support.quiet(run_acceptance.main, ["--root", str(self.root), "--feature", FID, *extra])[0]

    def test_refuses_unapproved_spec(self) -> None:
        support.cli(self.paths, "add", FID, "Demo")
        support.cli(self.paths, "start", FID)
        support.write_sdd(self.paths, FID)
        self.assertEqual(2, self.run_tool())
        self.assertFalse((self.paths.feature(FID) / "acceptance-results.json").exists())

    def test_statuses_and_evidence(self) -> None:
        support.advance_to_implementation(self, self.paths, Path(self._tmp.name) / "t", FID)
        support.write(self.root / "src" / "app.py", "def greet():\n    return 'hello'\n")
        results_path = self.paths.feature(FID) / "acceptance-results.json"
        self.assertEqual(1, self.run_tool())  # AC-002 obligatorio falla
        results = {r["id"]: r for r in hl.load_json(results_path)["results"]}
        self.assertEqual("pass", results["AC-001"]["status"])
        self.assertEqual("fail", results["AC-002"]["status"])
        self.assertIn("stdout_tail", results["AC-002"])

        support.write(self.root / "src" / "app.py", "def greet():\n    return 'hola'\n")
        self.assertEqual(0, self.run_tool())
        document = hl.load_json(results_path)
        self.assertEqual(hl.sha256_file(self.paths.feature(FID) / "SDD" / "acceptance.yaml"), document["acceptance_sha256"])
        self.assertEqual([], document["summary"]["required_failed"])

    def test_blocked_manual_and_partial_runs(self) -> None:
        with tempfile.TemporaryDirectory() as transcripts:
            # Checks extra antes de aprobar: la spec aprobada los incluye.
            support.cli(self.paths, "add", FID, "Demo")
            support.cli(self.paths, "start", FID)
            support.cli(self.paths, "transition", FID, "start_exploration")
            support.write(self.paths.feature(FID) / "SDD" / "context.md", "## Resumen\nDemo.\n")
            support.fake_subagent(self.paths, Path(transcripts), "e", "explorer", FID)
            support.cli(self.paths, "transition", FID, "exploration_complete")
            support.write_sdd(self.paths, FID)
            acceptance = self.paths.feature(FID) / "SDD" / "acceptance.yaml"
            acceptance.write_text(acceptance.read_text(encoding="utf-8") + EXTRA_CHECKS, encoding="utf-8")
            support.fake_subagent(self.paths, Path(transcripts), "d", "designer", FID, phase="design")
            self.assertEqual(0, support.cli(self.paths, "transition", FID, "design_complete")[0])
            self.assertEqual(0, support.cli(self.paths, "transition", FID, "approved", "--by", "human", "--response", "ok")[0])
        support.write(self.root / "src" / "app.py", "def greet():\n    return 'hola'\n")
        self.assertEqual(0, self.run_tool())  # AC-003 no es obligatorio
        results = {r["id"]: r for r in hl.load_json(self.paths.feature(FID) / "acceptance-results.json")["results"]}
        self.assertEqual("blocked", results["AC-003"]["status"])
        self.assertEqual("pass", results["AC-004"]["status"])
        self.assertEqual("manual", results["AC-005"]["status"])
        before = (self.paths.feature(FID) / "acceptance-results.json").read_text(encoding="utf-8")
        self.assertEqual(0, self.run_tool("--only", "AC-001"))
        self.assertEqual(before, (self.paths.feature(FID) / "acceptance-results.json").read_text(encoding="utf-8"))


class RunnerHygieneTests(unittest.TestCase):
    def test_secret_env_is_not_inherited_and_output_is_redacted(self) -> None:
        import os

        os.environ["DEMO_API_KEY"] = "abc123secret"
        try:
            env = run_acceptance._environment("DEMO-001")
        finally:
            del os.environ["DEMO_API_KEY"]
        self.assertNotIn("DEMO_API_KEY", env)
        self.assertEqual("DEMO-001", env["HARNESS_FEATURE_ID"])
        text = run_acceptance._tail("token=abcd1234efgh Authorization: Bearer xyz987654 ghp_abcdefghijklmnopqrstuv")
        self.assertNotIn("abcd1234efgh", text)
        self.assertNotIn("xyz987654", text)
        self.assertNotIn("ghp_abcdefghijklmnopqrstuv", text)


if __name__ == "__main__":
    unittest.main()
