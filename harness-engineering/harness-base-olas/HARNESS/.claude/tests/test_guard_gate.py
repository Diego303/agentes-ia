"""La firma humana de las decisiones del flujo no se puede esquivar con invocaciones no estandar."""

from __future__ import annotations

import unittest

import support  # noqa: F401
import guard
import harness_lib as hl

F = "python3 .claude/tools/feature.py"


def decision(command: str, agent: str | None = None, mode: str = "manual") -> str | None:
    original = guard._mode
    guard._mode = lambda: mode
    try:
        payload = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": str(hl.ROOT)}
        if agent:
            payload.update(agent_id="a1", agent_type=agent)
        result = guard.evaluate(payload)
    finally:
        guard._mode = original
    return result and result["hookSpecificOutput"]["permissionDecision"]


class GateSignatureTests(unittest.TestCase):
    def test_orchestrator_commands_run_without_prompt(self) -> None:
        for command in (f"{F} status", f"{F} add DEMO-002 'Human resources' --tags hr", f"{F} start DEMO-002",
                        f"{F} transition DEMO-001 build_complete",
                        f"{F} transition DEMO-001 escalate --reason 'el humano decide'"):
            with self.subTest(command=command):
                self.assertIsNone(decision(command))

    def test_human_decisions_and_obfuscations_ask(self) -> None:
        for command in (
            f"{F} transition DEMO-001 approved --by human --response 'approve: ok'",
            f"{F} transition DEMO-001 approved --b human --response ok",
            f"{F} transition DEMO-001 appr\"o\"ved --by hu\"m\"an --response ok",
            "python3 .claude/tools/fea\"tu\"re.py transition DEMO-001 approved --by human",
            "python3 -c \"import importlib; importlib.import_module('fea'+'ture')\"",
            f"{F} transition DEMO-001 build_complete --by human",
            f"{F} transition DEMO-001 pass; echo hecho",
            f"{F} transition DEMO-001 approved --by yolo-mode --response \"$(id)\"",
        ):
            with self.subTest(command=command):
                self.assertEqual("ask", decision(command, mode="yolo"))

    def test_yolo_delegation_requires_yolo_mode(self) -> None:
        command = f"{F} transition DEMO-001 approved --by yolo-mode --response auto --rationale 'regla 1'"
        self.assertIsNone(decision(command, mode="yolo"))
        self.assertEqual("ask", decision(command, mode="manual"))

    def test_subagents_never_touch_the_engine(self) -> None:
        self.assertEqual("deny", decision(f"{F} transition DEMO-001 pass", agent="reviewer"))
        self.assertEqual("deny", decision("python3 .claude/tools/fea''ture.py status", agent="builder"))


if __name__ == "__main__":
    unittest.main()
