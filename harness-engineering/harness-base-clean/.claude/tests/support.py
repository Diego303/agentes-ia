"""Utilidades de test: proyecto temporal con el bundle y ejecuciones simuladas de subagentes."""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
REAL_ROOT = TOOLS.parents[1]
sys.path.insert(0, str(TOOLS))

import feature  # noqa: E402
import harness_lib as hl  # noqa: E402
import ledger  # noqa: E402

REQUIREMENTS = """# Requisitos
## Funcionales
| ID | Requisito | Fuente |
| --- | --- | --- |
| FR-01 | greet() devuelve un saludo | peticion |
## No funcionales
| ID | Requisito | Fuente |
| --- | --- | --- |
| NFR-01 | El saludo esta en espanol | AGENTS.md |
"""

ACCEPTANCE = """version: 1
feature_id: {fid}
checks:
  - id: AC-001
    title: greet existe
    covers: [FR-01]
    kind: file
    required: true
    path: src/app.py
    expected: exists
    contains: "def greet\\\\("
  - id: AC-002
    title: el saludo es en espanol
    covers: [NFR-01]
    kind: command
    required: true
    command: grep -q hola src/app.py
    cwd: .
    timeout_seconds: 30
    expected_exit_code: 0
"""


def make_project(tmp: Path) -> hl.Paths:
    for name in ("CLAUDE.md", "AGENTS.md", "HARNESS.md"):
        shutil.copy(REAL_ROOT / name, tmp / name)
    shutil.copytree(
        REAL_ROOT / ".claude", tmp / ".claude",
        ignore=shutil.ignore_patterns("state", "__pycache__", "skill-creator", "*-workspace"),
    )
    (tmp / ".claude" / "state").mkdir()
    return hl.Paths(tmp)


def quiet(func, *args, **kwargs):
    """Ejecuta func silenciando stdout/stderr; devuelve (resultado, salida)."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        result = func(*args, **kwargs)
    return result, out.getvalue()


def cli(paths: hl.Paths, *argv: str) -> tuple[int, str]:
    return quiet(feature.main, ["--root", str(paths.root), *argv])


def usage(output: int, write: int = 2000, read: int = 0, one_hour: int = 0) -> dict:
    return {
        "input_tokens": 10, "output_tokens": output, "cache_read_input_tokens": read,
        "cache_creation_input_tokens": write + one_hour,
        "cache_creation": {"ephemeral_5m_input_tokens": write, "ephemeral_1h_input_tokens": one_hour},
    }


def fake_subagent(paths: hl.Paths, transcripts: Path, agent_id: str, agent_type: str, feature_id: str | None,
                  phase: str = "exploration", model: str = "claude-sonnet-5", session: str = "s-1",
                  prompt_prefix: str = "") -> None:
    """Escribe un transcript de subagente como los de Claude Code y dispara el hook SubagentStop."""
    main = transcripts / f"{session}.jsonl"
    main.parent.mkdir(parents=True, exist_ok=True)
    main.touch()
    sub = transcripts / session / "subagents" / f"agent-{agent_id}.jsonl"
    sub.parent.mkdir(parents=True, exist_ok=True)
    header = f"FEATURE_ID: {feature_id}\nPHASE: {phase}\n" if feature_id else ""
    now = hl.now_iso()
    lines = [
        {"type": "user", "timestamp": now, "message": {"role": "user", "content": prompt_prefix + header + "trabajo"}},
        {"type": "assistant", "timestamp": now, "message": {"id": f"m-{agent_id}", "model": model, "usage": usage(1),
                                                            "content": [{"type": "thinking"}]}},
        {"type": "assistant", "timestamp": now, "message": {"id": f"m-{agent_id}", "model": model, "usage": usage(1000),
                                                            "content": [{"type": "text", "text": "hecho"}]}},
    ]
    sub.write_text("\n".join(json.dumps(line) for line in lines) + "\n", encoding="utf-8")
    payload = {"hook_event_name": "SubagentStop", "session_id": session, "transcript_path": str(main),
               "agent_id": agent_id, "agent_type": agent_type}
    ledger.cmd_hook(paths, json.dumps(payload))


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_sdd(paths: hl.Paths, fid: str) -> None:
    sdd = paths.feature(fid) / "SDD"
    write(sdd / "proposal.md", "## Problema\nSaludar.\n")
    write(sdd / "requirements.md", REQUIREMENTS)
    write(sdd / "design.md", "## Enfoque\nFuncion greet en src/app.py.\n")
    write(sdd / "tasks.md", "- T-01 Implementar greet en src/app.py (FR-01), hecho cuando AC-001 y AC-002\n")
    write(sdd / "acceptance.yaml", ACCEPTANCE.format(fid=fid))


def verification_result(paths: hl.Paths, fid: str, verdict: str, build: int, verification: int,
                        repairable: bool = False) -> None:
    flags = {key: repairable for key in ("reproducible", "in_approved_scope", "design_unchanged",
                                         "acceptance_unchanged", "no_irreversible_side_effect")}
    hl.dump_yaml(paths.feature(fid) / "verification-result.yaml", {
        "version": 1, "feature_id": fid, "build_attempt": build, "verification_attempt": verification,
        "verdict": verdict, "inspections": [], "repairability": flags, "failure_summary": None,
    })


def advance_to_implementation(test, paths: hl.Paths, transcripts: Path, fid: str = "DEMO-001") -> None:
    """add -> start -> exploration -> design -> GATE#1 aprobado por el humano."""
    test.assertEqual(cli(paths, "add", fid, "Demo", "--tags", "demo")[0], 0)
    test.assertEqual(cli(paths, "start", fid)[0], 0)
    test.assertEqual(cli(paths, "transition", fid, "start_exploration")[0], 0)
    write(paths.feature(fid) / "SDD" / "context.md", "## Resumen\nDemo.\n")
    fake_subagent(paths, transcripts, "a-exp", "explorer", fid)
    test.assertEqual(cli(paths, "transition", fid, "exploration_complete")[0], 0)
    write_sdd(paths, fid)
    fake_subagent(paths, transcripts, "a-des", "designer", fid, phase="design", model="claude-opus-5-5")
    test.assertEqual(cli(paths, "transition", fid, "design_complete")[0], 0)
    code, out = cli(paths, "transition", fid, "approved", "--by", "human", "--response", "approve")
    test.assertEqual(code, 0, out)
