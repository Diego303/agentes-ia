"""scripts/ola.sh de punta a punta en un repo temporal: abrir, estado, integrar (con y sin conflictos) y cerrar."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import support

SCRIPT = support.REAL_ROOT / "scripts" / "ola.sh"
BASH_OK = shutil.which("bash") and shutil.which("git") and subprocess.run(
    ["bash", "-c", "[ ${BASH_VERSINFO[0]} -ge 4 ]"], check=False).returncode == 0


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def set_feature(root: Path, fid: str, **fields: object) -> None:
    path = root / ".claude" / "feature_list.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for item in data["features"]:
        if item["id"] == fid:
            item.update(fields)
            break
    else:
        data["features"].append({"id": fid, "title": fid, "priority": 3, "tags": [], "status": "proposed", **fields})
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def finish_feature(worktree: Path, fid: str, message: str) -> None:
    """Lo que deja una sesion al archivar: estado archived, archive.md y codigo sin commit."""
    set_feature(worktree, fid, status="archived")
    state = worktree / ".claude" / "state" / fid
    state.mkdir(parents=True, exist_ok=True)
    (state / "archive.md").write_text(f"# Archivo\n\n## Resumen\n\nHecho.\n\n## Commit sugerido\n\n```text\n{message}\n```\n",
                                      encoding="utf-8")


@unittest.skipUnless(BASH_OK, "requiere bash 4+ y git")
class OlaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.repo = self.tmp / "app"
        self.repo.mkdir()
        support.make_project(self.repo)
        (self.repo / "scripts").mkdir()
        shutil.copy(SCRIPT, self.repo / "scripts" / "ola.sh")
        (self.repo / "README.md").write_text("linea 1\nlinea 2\n", encoding="utf-8")
        data = {"version": 1, "features": [
            {"id": "APP-001", "title": "uno", "priority": 1, "tags": [], "status": "proposed", "notes": "v1 · orden 1"},
            {"id": "APP-002", "title": "dos", "priority": 2, "tags": [], "status": "proposed",
             "notes": "v1 · orden 2 · depende de: APP-001 · maquetas: ninguna"},
        ]}
        (self.repo / ".claude" / "feature_list.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        git(self.repo, "init", "-q", "-b", "develop")
        git(self.repo, "config", "user.email", "test@example.com")
        git(self.repo, "config", "user.name", "Test")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "chore: base")
        self.wt = self.tmp / "wt"

    def ola(self, *args: str, claude: bool = False) -> subprocess.CompletedProcess:
        env = {k: v for k, v in os.environ.items() if k not in ("CLAUDECODE", "TMUX", "OLA_DIR")}
        env.update(XDG_RUNTIME_DIR=str(self.tmp), HOME=str(self.tmp))
        if claude:
            env["CLAUDECODE"] = "1"
        return subprocess.run(["bash", "scripts/ola.sh", *args, "--dir", str(self.wt), "--sin-tmux"],
                              cwd=self.repo, env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True)

    def test_help_and_version(self) -> None:
        self.assertEqual(0, subprocess.run(["bash", "-n", str(SCRIPT)], check=False).returncode)
        result = self.ola("ayuda")
        self.assertEqual(0, result.returncode)
        self.assertIn("integrar --continuar", result.stdout)
        self.assertIn("ola.sh 3", self.ola("version").stdout)

    def test_full_cycle(self) -> None:
        # Una dependencia sin integrar impide abrir; el ID se normaliza a mayusculas.
        refused = self.ola("abrir", "app-002")
        self.assertEqual(1, refused.returncode)
        self.assertIn("depende de APP-001", refused.stderr)

        opened = self.ola("abrir", "APP-001")
        self.assertEqual(0, opened.returncode, opened.stderr)
        worktree = self.wt / "app-001"
        self.assertTrue((worktree / ".claude" / "tools" / "feature.py").is_file())
        self.assertIn("wt/app-001", git(self.repo, "branch", "--list", "wt/app-001"))
        self.assertIn("claude", opened.stdout)
        self.assertIn("sin arrancar", self.ola("estado").stdout)

        # Sin terminal no commitea en el worktree: para y da el comando.
        finish_feature(worktree, "APP-001", "feat(app): APP-001 primera feature")
        (worktree / "src").mkdir(exist_ok=True)
        (worktree / "src" / "uno.py").write_text("UNO = 1\n", encoding="utf-8")
        pending = self.ola("integrar", "APP-001")
        self.assertEqual(1, pending.returncode)
        self.assertIn("falta el commit del worktree", pending.stderr)

        git(worktree, "add", "-A")
        git(worktree, "commit", "-q", "--no-verify", "-m", "chore(app-001): trabajo de la feature")
        integrated = self.ola("integrar", "APP-001")
        self.assertEqual(0, integrated.returncode, integrated.stderr)
        self.assertIn("Haz tú el commit", integrated.stdout)
        msg_file = Path(git(self.repo, "rev-parse", "--absolute-git-dir")) / "ola-commit-msg"
        git(self.repo, "commit", "-q", "-F", str(msg_file))
        self.assertEqual("feat(app): APP-001 primera feature", git(self.repo, "log", "-1", "--format=%s"))

        closed = self.ola("cerrar", "APP-001")
        self.assertEqual(0, closed.returncode, closed.stderr)
        self.assertFalse(worktree.exists())
        self.assertEqual("", git(self.repo, "branch", "--list", "wt/app-001"))
        self.assertIn("No hay features abiertas", self.ola("estado").stdout)

    def test_conflicts_feature_list_is_automatic_and_the_rest_waits(self) -> None:
        set_feature(self.repo, "APP-001", status="archived")
        git(self.repo, "commit", "-qam", "chore: APP-001 integrada")
        self.assertEqual(0, self.ola("abrir", "APP-002").returncode)
        worktree = self.wt / "app-002"

        # develop avanza: un follow-up en feature_list.json y un cambio en la misma linea del README.
        set_feature(self.repo, "APP-003", notes="follow-up")
        (self.repo / "README.md").write_text("linea 1 develop\nlinea 2\n", encoding="utf-8")
        git(self.repo, "commit", "-qam", "chore: avanza develop")

        finish_feature(worktree, "APP-002", "feat(app): APP-002 segunda feature")
        set_feature(worktree, "APP-004", notes="follow-up de APP-002")  # los dos lados añaden al final
        (worktree / "README.md").write_text("linea 1 feature\nlinea 2\n", encoding="utf-8")
        git(worktree, "add", "-A")
        git(worktree, "commit", "-q", "--no-verify", "-m", "chore(app-002): trabajo de la feature")

        conflicted = self.ola("integrar", "APP-002")
        self.assertEqual(2, conflicted.returncode, conflicted.stderr)
        self.assertIn("auto: .claude/feature_list.json", conflicted.stdout)
        self.assertIn("README.md", conflicted.stderr + conflicted.stdout)

        # Con marcas no continua; resuelto, si.
        self.assertEqual(1, self.ola("integrar", "--continuar").returncode)
        (self.repo / "README.md").write_text("linea 1 develop\nlinea 1 feature\nlinea 2\n", encoding="utf-8")
        resumed = self.ola("integrar", "--continuar")
        self.assertEqual(0, resumed.returncode, resumed.stderr)
        features = {f["id"]: f["status"] for f in
                    json.loads((self.repo / ".claude" / "feature_list.json").read_text(encoding="utf-8"))["features"]}
        self.assertEqual({"APP-001": "archived", "APP-002": "archived", "APP-003": "proposed", "APP-004": "proposed"}, features)

    def test_project_config_and_failing_verify(self) -> None:
        script = self.repo / "scripts" / "ola.sh"
        text = script.read_text(encoding="utf-8")
        text = text.replace("declare -A IMPLICITAS=(\n", 'declare -A IMPLICITAS=(\n  [APP-003]="APP-002"\n', 1)
        text = text.replace("TRAS_INTEGRAR=(\n", "TRAS_INTEGRAR=(\n  '^src/ :: echo regenerado > generado.txt'\n", 1)
        script.write_text(text, encoding="utf-8")
        set_feature(self.repo, "APP-003")
        git(self.repo, "commit", "-qam", "chore: APP-003 y config")

        refused = self.ola("abrir", "APP-003")
        self.assertEqual(1, refused.returncode)
        self.assertIn("depende de APP-002", refused.stderr)  # implicita: no esta en las notas

        self.assertEqual(0, self.ola("abrir", "APP-001").returncode)
        worktree = self.wt / "app-001"
        finish_feature(worktree, "APP-001", "feat(app): APP-001 primera feature")
        (worktree / "src").mkdir(exist_ok=True)
        (worktree / "src" / "uno.py").write_text("UNO = 1\n", encoding="utf-8")
        git(worktree, "add", "-A")
        git(worktree, "commit", "-q", "--no-verify", "-m", "chore(app-001): trabajo de la feature")

        verify = self.repo / ".claude" / "bootstrap" / "verify.sh"
        verify.write_text("#!/usr/bin/env bash\necho rojo\nexit 1\n", encoding="utf-8")
        git(self.repo, "commit", "-qam", "test: verify en rojo")
        failed = self.ola("integrar", "APP-001")
        self.assertEqual(1, failed.returncode)
        self.assertIn("verify.sh falla", failed.stderr)
        self.assertEqual("regenerado", (self.repo / "generado.txt").read_text(encoding="utf-8").strip())
        self.assertIn("hay una integración a medias", self.ola("integrar", "APP-001").stderr)
        self.assertEqual(0, self.ola("integrar", "--abortar", "--si").returncode)
        self.assertEqual("", git(self.repo, "status", "--porcelain"))

    def test_never_confirms_from_claude_code(self) -> None:
        refused = self.ola("cerrar", "APP-001", "--si", claude=True)
        self.assertEqual(1, refused.returncode)
        self.assertIn("--si no se permite desde Claude Code", refused.stderr)
        self.assertEqual(1, self.ola("cerrar", "APP-001", claude=True).returncode)  # no integrada: no cierra


if __name__ == "__main__":
    unittest.main()
