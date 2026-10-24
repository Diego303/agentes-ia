"""guard.py 0.8.0: lexico con comillas y heredocs, solo lectura por Bash, especialistas y secretos."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

import support  # noqa: F401
import guard
from test_guard import STATE, bash, decision, edit

import harness_lib as hl


def read(tool: str, agent: str | None = None, **tool_input: str) -> dict:
    payload = {"tool_name": tool, "tool_input": tool_input, "cwd": str(hl.ROOT)}
    if agent:
        payload.update(agent_id="a1", agent_type=agent)
    return payload


class LexerTests(unittest.TestCase):
    def test_quoted_text_is_not_a_redirect_or_invocation(self) -> None:
        for command in ('grep -n "-> None" src/app.py', "rg 'Vec<String>' src", 'rg "git push" src',
                        "grep -n '> x' .claude/settings.json"):
            with self.subTest(command=command):
                self.assertFalse(guard.writes_by_bash(command))
                self.assertIsNone(decision(bash(command, "reviewer")))
        # Antes, el patron entrecomillado con '>' y una ruta de control pedia confirmacion.
        self.assertIsNone(decision(bash("grep -n '> x' .claude/settings.json")))

    def test_real_writes_are_detected(self) -> None:
        for command in ("echo hi > src/a.txt", 'cat <<EOF > src/x.py\nprint(1)\nEOF', "sort -o out.txt in.txt",
                        "find . -name '*.pyc' -exec rm {} +", '"cp" a.txt b.txt', "python3 -c 'print(1)'",
                        "ls | xargs rm", "cmd &> log.txt"):
            with self.subTest(command=command):
                self.assertTrue(guard.writes_by_bash(command))

    def test_heredoc_body_is_text(self) -> None:
        message = "git commit -F- <<'EOF'\nfix: no toques .claude/settings.json > nunca\nEOF"
        self.assertFalse(guard._write_hint(message))

    def test_inline_code_depends_on_the_interpreter(self) -> None:
        for command in ("python3 -m pytest -p no:cacheprovider -c pytest.ini", "python3 -m pytest -r a",
                        "node --version", "bash .claude/bootstrap/verify.sh"):
            with self.subTest(command=command):
                self.assertIsNone(guard.readonly_write_problem(command))
        for command in ("python3 -c 'import os'", "node -e 'x()'", "perl -pe 's/a/b/' f", "bash -lc 'ls'",
                        "cat x.py | python3", "python3 - < x.py"):
            with self.subTest(command=command):
                self.assertIsNotNone(guard.readonly_write_problem(command))


class ReadOnlyBashTests(unittest.TestCase):
    def test_only_the_builder_writes_by_bash(self) -> None:
        writes = ["echo x > src/app.py", "sed -i 's/a/b/' src/app.py", "ruff check --fix src", "black src",
                  "npx prettier --write .", "mkdir build", "cp a.txt src/b.txt", "pytest --junitxml=report.xml",
                  "find src -name '*.py' -exec sed -i s/a/b/ {} +", "eval ls"]
        for command in writes:
            with self.subTest(command=command):
                self.assertEqual("deny", decision(bash(command, "reviewer")))
                self.assertEqual("deny", decision(bash(command, "security-auditor")))
        for command in ("echo x > src/app.py", "mkdir build", "pytest --junitxml=report.xml"):
            with self.subTest(command=command):
                self.assertIsNone(decision(bash(command, "builder")))

    def test_read_only_agents_can_read_test_and_use_temp(self) -> None:
        for command in ("pytest -q tests", "python3 -m pytest -q", "ruff check src", "black --check src",
                        "git diff abc123 -- . > /tmp/diff.txt", "pytest --junitxml=/tmp/r.xml", "npm test",
                        "cargo fmt --check", "git tag --list"):
            with self.subTest(command=command):
                self.assertIsNone(decision(bash(command, "reviewer")))

    def test_more_installs_are_human_decisions(self) -> None:
        for command in ("npx some-tool", "pnpm dlx create-x", "pnpm -C web add react", "yarn upgrade", "cargo update",
                        "rustup toolchain install nightly", "corepack enable"):
            with self.subTest(command=command):
                self.assertEqual("deny", decision(bash(command, "builder")))
        self.assertEqual("deny", decision(bash("git tag v1.0.0", "reviewer")))


class SpecialistTests(unittest.TestCase):
    REGISTRY = {"name": "docs-keeper", "role": "specialist", "insertion": "post-verification",
                "product_writes": ["docs/*", "README.md"]}

    def test_specialist_writes_only_its_report_and_product_writes(self) -> None:
        with mock.patch.object(guard, "_registry_entry", lambda agent: self.REGISTRY if agent == "docs-keeper" else None):
            self.assertIsNone(decision(edit(f"{STATE}/docs-keeper.md", "docs-keeper")))
            self.assertIsNone(decision(edit("docs/guia.md", "docs-keeper")))
            self.assertIsNone(decision(edit("README.md", "docs-keeper")))
            for path in ("src/app.py", "docs/CLAUDE.md", ".claude/settings.json", f"{STATE}/SDD/design.md"):
                with self.subTest(path=path):
                    self.assertEqual("deny", decision(edit(path, "docs-keeper")))

    def test_unregistered_subagents_never_write_product_code(self) -> None:
        self.assertEqual("deny", decision(edit("src/app.py", "general-purpose")))
        self.assertIsNone(decision(edit(f"{STATE}/general-purpose.md", "general-purpose")))

    def test_unreadable_registry_fails_closed(self) -> None:
        def broken(agent: str) -> dict:
            raise hl.YamlError("registro roto")

        with mock.patch.object(guard, "_registry_entry", broken), mock.patch.object(guard, "_log", lambda message: None):
            with mock.patch("sys.stdin") as stdin, mock.patch("builtins.print") as printed:
                stdin.read.return_value = __import__("json").dumps(edit("docs/x.md", "docs-keeper"))
                guard.main()
            self.assertIn('"deny"', printed.call_args[0][0])


class SecretTests(unittest.TestCase):
    def test_read_grep_glob_cannot_reach_secrets(self) -> None:
        denied = [read("Read", file_path=".env"), read("Read", file_path="config/.env.local"),
                  read("Read", file_path="certs/server.pem"), read("Read", file_path=str(Path.home() / ".ssh" / "id_rsa")),
                  read("Read", file_path="~/.aws/credentials"), read("Glob", pattern="**/.env*"),
                  read("Glob", pattern="**/*.pem"), read("Grep", pattern="KEY", path=".env"),
                  read("Grep", pattern="KEY", glob="*.key"), read("Read", "explorer", file_path="secrets/db.txt")]
        for payload in denied:
            with self.subTest(payload=payload["tool_input"]):
                self.assertEqual("deny", decision(payload))
        allowed = [read("Read", file_path=".env.example"), read("Read", file_path="src/secrets/manager.py"),
                   read("Glob", pattern="**/*.py"), read("Glob", pattern="src/*"), read("Grep", pattern=".env", path="src"),
                   read("Read", file_path="docs/keys.md")]
        for payload in allowed:
            with self.subTest(payload=payload["tool_input"]):
                self.assertIsNone(decision(payload))

    def test_nobody_writes_secret_files(self) -> None:
        self.assertEqual("deny", decision(edit(".env")))
        self.assertEqual("deny", decision(edit("deploy/id_ed25519", "builder")))
        self.assertIsNone(decision(edit(".env.example", "builder")))

    def test_indirect_secret_reads_by_bash(self) -> None:
        for command in ("cat .en?", "cat *.pem", "grep -rn KEY .", "rg --hidden KEY", "xargs cat < files.txt",
                        "echo $(cat secret.txt)"):
            with self.subTest(command=command):
                self.assertEqual("deny", decision(bash(command, "reviewer")))
        self.assertEqual("ask", decision(bash("echo $(cat secret.txt)")))
        self.assertEqual("ask", decision(bash("cat .en?")))
        for command in ("grep -rn TODO src", "rg KEY src", "ls src/*"):
            with self.subTest(command=command):
                self.assertIsNone(decision(bash(command, "reviewer")))


class MainSessionReadSubcommandsTests(unittest.TestCase):
    def test_metrics_and_specialists_need_no_confirmation(self) -> None:
        for command in ("python3 .claude/tools/feature.py metrics --json",
                        "python3 .claude/tools/feature.py metrics --state-dir /tmp/otro/.claude/state",
                        "python3 .claude/tools/feature.py specialists DEMO-001 --insertion post-implementation"):
            with self.subTest(command=command):
                self.assertIsNone(decision(bash(command)))


if __name__ == "__main__":
    unittest.main()
