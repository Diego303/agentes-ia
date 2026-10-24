"""0.8.0: tramo de contexto largo, validacion del registro y de [verification], hooks y runner con pipefail."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

import support
import harness_lib as hl
import ledger
import run_acceptance
import validate_harness as vh
from test_validate_harness import check, doc

HAIKU = {"claude-haiku-5-5": {
    "input": 0.1, "output": 0.5, "cache_write_5m": 0.125, "cache_write_1h": 0.2, "cache_read": 0.01,
    "long_context": {"threshold": 100_000, "input": 0.5, "output": 2.5, "cache_write_5m": 0.625, "cache_write_1h": 1.0,
                     "cache_read": 0.05},
}}


def codes(root: Path) -> set[str]:
    return {issue.code for issue in vh.validate(root).issues}


class LongContextPricingTests(unittest.TestCase):
    def test_requests_over_the_threshold_use_the_long_tier(self) -> None:
        small = {"input": 1_000, "output": 1_000_000, "cache_write_5m": 0, "cache_write_1h": 0, "cache_read": 50_000}
        large = {**small, "cache_read": 150_000}
        self.assertEqual("claude-haiku-5-5", ledger.tiered_key("claude-haiku-5-5", small, HAIKU))
        self.assertEqual("claude-haiku-5-5|long", ledger.tiered_key("claude-haiku-5-5", large, HAIKU))
        self.assertEqual("claude-sonnet-5-5", ledger.tiered_key("claude-sonnet-5-5", large, HAIKU))  # sin tramo
        self.assertAlmostEqual(0.5, ledger.price("claude-haiku-5-5", {**small, "input": 0, "cache_read": 0}, HAIKU))
        self.assertAlmostEqual(2.5, ledger.price("claude-haiku-5-5|long", {**small, "input": 0, "cache_read": 0}, HAIKU))

    def test_transcript_usage_is_split_per_request(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "agent.jsonl"
            lines = [{"type": "user", "timestamp": "2026-10-24T00:00:00Z", "message": {"content": "FEATURE_ID: DEMO-001\nx"}}]
            for index, read in enumerate((1_000, 200_000)):
                lines.append({"type": "assistant", "timestamp": "2026-10-24T00:00:01Z", "message": {
                    "id": f"m{index}", "model": "claude-haiku-5-5", "usage": support.usage(10, write=0, read=read)}})
            path.write_text("\n".join(json.dumps(line) for line in lines), encoding="utf-8")
            usage = ledger.parse_subagent_transcript(path, HAIKU)["usage"]
            self.assertEqual({"claude-haiku-5-5", "claude-haiku-5-5|long"}, set(usage))
            self.assertEqual(200_000, usage["claude-haiku-5-5|long"]["cache_read"])
            self.assertEqual({"claude-haiku-5-5"}, set(ledger.parse_subagent_transcript(path)["usage"]))

    def test_current_pricing_table_has_the_current_models(self) -> None:
        models = hl.load_config(hl.Paths(support.REAL_ROOT))["cost"]["pricing"]["models"]
        for model in ("claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5", "claude-fable-5-1"):
            self.assertIn(model, models)
        self.assertEqual(100_000, models["claude-haiku-5-5"]["long_context"]["threshold"])


class RegistryAndConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.paths = support.make_project(Path(self._tmp.name))

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def add_specialist(self, entry: dict, frontmatter: str = "effort: low\nomitClaudeMd: true\n",
                       tools: str = "Read, Write") -> None:
        name = entry["name"]
        (self.paths.bundle / "agents" / f"{name}.md").write_text(
            f"---\nname: {name}\ndescription: d\ntools: {tools}\nmodel: claude-sonnet-5-5\n{frontmatter}---\n# {name}\n",
            encoding="utf-8")
        registry = hl.load_yaml(self.paths.registry)
        registry["agents"].append({"file": f".claude/agents/{name}.md", "role": "specialist", **entry})
        hl.dump_yaml(self.paths.registry, registry)

    def test_valid_specialist_passes(self) -> None:
        self.add_specialist({"name": "docs-keeper", "insertion": "post-verification", "phase": "verification",
                             "triggers_on_tags": ["docs"], "product_writes": ["docs/*"]})
        self.assertEqual([], [i for i in vh.validate(self.paths.root).issues if i.severity == "error"])

    def test_invalid_specialist_entries(self) -> None:
        self.add_specialist({"name": "bad-one", "insertion": "whenever", "phase": "gate1_pending",
                             "triggers_on_tags": "auth", "product_writes": [".claude/settings.json", "*.py", "../x"]},
                            frontmatter="", tools="Read, Agent")
        found = codes(self.paths.root)
        for code in ("registry_insertion", "registry_phase", "registry_triggers_on_tags", "registry_product_writes",
                     "agent_depth", "agent_runtime", "agent_context"):
            self.assertIn(code, found)

    def test_model_alias_and_unpriced_models_warn(self) -> None:
        explorer = self.paths.bundle / "agents" / "explorer.md"
        explorer.write_text(explorer.read_text(encoding="utf-8").replace("model: claude-sonnet-5-5", "model: sonnet"),
                            encoding="utf-8")
        designer = self.paths.bundle / "agents" / "designer.md"
        designer.write_text(designer.read_text(encoding="utf-8").replace("model: claude-opus-5-5", "model: claude-nuevo-9"),
                            encoding="utf-8")
        found = codes(self.paths.root)
        self.assertIn("agent_model_alias", found)
        self.assertIn("agent_model_unpriced", found)

    def test_guard_must_cover_read_tools(self) -> None:
        settings = hl.load_json(self.paths.settings)
        settings["hooks"]["PreToolUse"] = settings["hooks"]["PreToolUse"][:1]
        hl.dump_json(self.paths.settings, settings)
        self.assertIn("hook_guard_tools", codes(self.paths.root))

    def test_required_hooks_and_bad_config(self) -> None:
        text = self.paths.harness_toml.read_text(encoding="utf-8")
        text = text.replace("required_hooks = []", 'required_hooks = [".claude/hooks/project_guard.py"]')
        text = text.replace('"claude-sonnet-5-5" = { input = 2.0', '"claude-sonnet-5-5" = { long_context = 5, input = 2.0', 1)
        self.paths.harness_toml.write_text(text, encoding="utf-8")
        found = codes(self.paths.root)
        self.assertTrue({"hook_project", "hook_project_missing", "config_pricing"} <= found)


class VerificationRulesTests(unittest.TestCase):
    def test_required_regression(self) -> None:
        config = {"verification": {"required_regression": "bash .claude/bootstrap/verify.sh"}}
        self.assertEqual(1, len(vh.regression_problems(doc(check()), config)))
        ok = doc(check(), check(id="AC-002", command="bash  .claude/bootstrap/verify.sh"))
        self.assertEqual([], vh.regression_problems(ok, config))
        optional = doc(check(), check(id="AC-002", required=False, command="bash .claude/bootstrap/verify.sh"))
        self.assertEqual(1, len(vh.regression_problems(optional, config)))
        self.assertEqual([], vh.regression_problems(doc(check()), {}))

    def test_required_by_tag(self) -> None:
        config = {"verification": {"required_by_tag": {"auth": "tests/security", "ui": ["e2e", "a11y"]}}}
        self.assertEqual(1, len(vh.tag_check_problems(doc(check()), config, ["Auth"])))
        self.assertEqual([], vh.tag_check_problems(doc(check(command="pytest tests/security -q")), config, ["auth"]))
        self.assertEqual(2, len(vh.tag_check_problems(doc(check()), config, ["ui"])))
        self.assertEqual([], vh.tag_check_problems(doc(check()), config, ["otro"]))

    def test_checks_cannot_hide_the_exit_code(self) -> None:
        for command in ("pytest -q || true", "pytest -q; exit 0", "pytest -q | head -5", "pytest -q | less"):
            with self.subTest(command=command):
                self.assertTrue(vh.acceptance_problems(doc(check(command=command))))
        self.assertEqual([], vh.acceptance_problems(doc(check(command="pytest -q 2>&1 | tail -20"))))


class RunnerPipefailTests(unittest.TestCase):
    def test_a_failure_inside_a_pipe_fails_the_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_acceptance.run_command(
                {"id": "AC-001", "command": "false | cat", "cwd": ".", "timeout_seconds": 10, "expected_exit_code": 0},
                Path(tmp), "DEMO-001")
        self.assertNotEqual("passed", result["status"])

    def test_display_variables_are_kept(self) -> None:
        os.environ["XAUTHORITY"] = "/tmp/xauth"
        try:
            env = run_acceptance._environment("DEMO-001")
        finally:
            del os.environ["XAUTHORITY"]
        self.assertEqual("/tmp/xauth", env["XAUTHORITY"])


if __name__ == "__main__":
    unittest.main()
