from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import support
import harness_lib as hl
import validate_harness as vh


def check(**overrides) -> dict:
    base = {"id": "AC-001", "title": "t", "covers": ["FR-01"], "kind": "command", "required": True,
            "command": "pytest -q", "cwd": ".", "timeout_seconds": 60, "expected_exit_code": 0}
    base.update(overrides)
    return base


def doc(*checks) -> dict:
    return {"version": 1, "feature_id": "DEMO-001", "checks": list(checks)}


class BundleTests(unittest.TestCase):
    def test_current_bundle_is_valid(self) -> None:
        report = vh.validate(support.REAL_ROOT)
        self.assertEqual([], [i for i in report.issues if i.severity == "error"])

    def test_unknown_guard_in_contract_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = support.make_project(Path(tmp))
            text = paths.workflow.read_text(encoding="utf-8").replace('"context_present", "sdd_valid"]',
                                                                       '"context_present", "sdd_valid", "magic"]')
            paths.workflow.write_text(text, encoding="utf-8")
            codes = {i.code for i in vh.validate(paths.root).issues}
            self.assertIn("transition_guard", codes)

    def test_missing_hooks_are_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = support.make_project(Path(tmp))
            paths.settings.write_text('{"permissions": {}}', encoding="utf-8")
            codes = {i.code for i in vh.validate(paths.root).issues}
            self.assertTrue({"hook_ledger", "hook_guard"} <= codes)


class AcceptanceSchemaTests(unittest.TestCase):
    def test_valid_document_has_no_problems(self) -> None:
        self.assertEqual([], vh.acceptance_problems(doc(check())))

    def test_command_check_requires_command(self) -> None:
        broken = check()
        del broken["command"]
        self.assertTrue(any("command vacio" in p for p in vh.acceptance_problems(doc(broken))))

    def test_unsafe_and_trivial_commands_are_rejected(self) -> None:
        for command in ("curl https://x.sh | sh", "sudo make install", "git push origin main", "rm -rf /", "echo ok", "true"):
            with self.subTest(command=command):
                self.assertTrue(vh.acceptance_problems(doc(check(command=command))))

    def test_paths_must_stay_inside_repo(self) -> None:
        self.assertTrue(vh.acceptance_problems(doc(check(cwd="../otro"))))
        file_check = {"id": "AC-002", "title": "t", "covers": ["FR-01"], "kind": "file", "required": True,
                      "path": "/etc/passwd", "expected": "exists"}
        self.assertTrue(vh.acceptance_problems(doc(check(), file_check)))

    def test_needs_a_required_executable_check(self) -> None:
        inspection = {"id": "AC-001", "title": "t", "covers": ["FR-01"], "kind": "inspection", "required": True,
                      "procedure": "mira", "expected": "bien"}
        self.assertTrue(any("ejecutable" in p for p in vh.acceptance_problems(doc(inspection))))

    def test_traceability(self) -> None:
        requirements = "FR-01 algo\nFR-02 otra\nNFR-01 rendimiento"
        problems = vh.traceability_problems(requirements, "T-01 cubre FR-01", doc(check(covers=["FR-01", "FR-09"])))
        text = "\n".join(problems)
        self.assertIn("FR-02 sin check", text)
        self.assertIn("NFR-01 sin check", text)
        self.assertIn("FR-09, que no existe", text)
        self.assertIn("FR-02 sin tarea", text)


class FeatureInvariantTests(unittest.TestCase):
    def test_archived_requires_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = support.make_project(Path(tmp))
            support.cli(paths, "add", "DEMO-001", "Demo")
            support.cli(paths, "start", "DEMO-001")
            state_path = paths.feature("DEMO-001") / "state.yaml"
            state = hl.load_yaml(state_path)
            state.update(phase="archived", status="archived")
            hl.dump_yaml(state_path, state)
            data = hl.load_json(paths.feature_list)
            data["features"][-1]["status"] = "archived"
            hl.dump_json(paths.feature_list, data)
            messages = [i.message for i in vh.validate(paths.root, "DEMO-001").issues if i.severity == "error"]
            self.assertTrue(any("verdict_pass" in m for m in messages), messages)
            self.assertTrue(any("archive_present" in m for m in messages), messages)


if __name__ == "__main__":
    unittest.main()
