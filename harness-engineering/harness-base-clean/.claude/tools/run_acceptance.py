#!/usr/bin/env python3
"""Ejecuta los checks de SDD/acceptance.yaml de una feature y guarda la evidencia.

Uso:
  python3 .claude/tools/run_acceptance.py --feature F [--only AC-001,AC-002] [--no-write]

Solo ejecuta especificaciones aprobadas: exige SDD/spec.lock.json y que
acceptance.yaml no haya cambiado desde GATE#1 (sus comandos los reviso el humano).
Resultado en .claude/state/<F>/acceptance-results.json.

Exit: 0 todos los checks obligatorios ejecutables pasan; 1 alguno falla;
      2 bloqueo (herramienta ausente, spec no aprobada o invalida).
Los checks `inspection` quedan como `manual`: los resuelve el reviewer con evidencia.

Seguridad: los comandos no heredan variables de entorno con aspecto de secreto
(tokens, claves, contrasenas) y la salida guardada como evidencia se redacta.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_lib as hl  # noqa: E402
import validate_harness as vh  # noqa: E402

TAIL = 1500
SECRET_ENV = re.compile(r"TOKEN|SECRET|PASSW|API_?KEY|PRIVATE_?KEY|CREDENTIAL|ACCESS_?KEY|AUTH", re.IGNORECASE)
REDACT = [
    (re.compile(r"(?i)\b(bearer|basic)\s+[A-Za-z0-9._~+/=-]{4,}"), r"\1 ***"),
    (re.compile(r"(?i)((?:api[_-]?key|token|secret|password|passwd|authorization)[\"']?\s*[=:]\s*[\"']?)"
                r"([^\s'\"]{4,})"), r"\1***"),
    (re.compile(r"\b(ghp_|gho_|ghs_|github_pat_|sk-ant-|sk-|xox[baprs]-)[A-Za-z0-9_-]{10,}"), r"\1***"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AKIA***"),
]


def _redact(text: str) -> str:
    for pattern, replacement in REDACT:
        text = pattern.sub(replacement, text)
    return text


def _tail(text: str) -> str:
    text = _redact(text or "")
    return text if len(text) <= TAIL else "..." + text[-TAIL:]


def _environment(feature_id: str) -> dict:
    env = {key: value for key, value in os.environ.items() if not SECRET_ENV.search(key)}
    env["HARNESS_FEATURE_ID"] = feature_id
    return env


def run_command(check: dict, root: Path, feature_id: str) -> dict:
    cwd = root / check.get("cwd", ".")
    timeout = int(check.get("timeout_seconds", 120))
    expected = int(check.get("expected_exit_code", 0))
    env = _environment(feature_id)
    started = time.monotonic()
    try:
        process = subprocess.Popen(
            check["command"], shell=True, cwd=cwd, env=env, text=True, errors="replace",
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            executable=shutil.which("bash"), start_new_session=True,
        )
    except OSError as exc:
        return {"status": "blocked", "reason": f"no se pudo lanzar: {exc}"}
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (OSError, AttributeError):
            process.kill()
        stdout, stderr = process.communicate()
        return {"status": "fail", "reason": f"timeout tras {timeout}s", "stdout_tail": _tail(stdout),
                "stderr_tail": _tail(stderr), "duration_ms": int((time.monotonic() - started) * 1000)}
    code = process.returncode
    result = {"exit_code": code, "expected_exit_code": expected, "duration_ms": int((time.monotonic() - started) * 1000)}
    if code == expected:
        result["status"] = "pass"
    elif code in (126, 127):
        result.update(status="blocked", reason="comando no encontrado o no ejecutable (BLOCKED_TOOLING)")
    else:
        result["status"] = "fail"
    if result["status"] != "pass":
        result.update(stdout_tail=_tail(stdout), stderr_tail=_tail(stderr))
    return result


def run_file(check: dict, root: Path) -> dict:
    path = root / check["path"]
    exists = path.is_file()
    if check["expected"] == "absent":
        return {"status": "pass" if not path.exists() else "fail", "reason": None if not path.exists() else "existe"}
    if not exists:
        return {"status": "fail", "reason": "no existe"}
    text = path.read_text(encoding="utf-8", errors="replace")
    if "contains" in check and not re.search(str(check["contains"]), text, re.MULTILINE):
        return {"status": "fail", "reason": f"no contiene /{check['contains']}/"}
    if "not_contains" in check and re.search(str(check["not_contains"]), text, re.MULTILINE):
        return {"status": "fail", "reason": f"contiene /{check['not_contains']}/"}
    return {"status": "pass"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--feature", required=True)
    parser.add_argument("--only", help="IDs separados por comas")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)
    paths = hl.Paths(args.root)
    fid = args.feature
    if not hl.FEATURE_ID_RE.match(fid):
        print(f"ID de feature invalido: {fid!r}", file=sys.stderr)
        return 2
    acceptance_path = paths.feature(fid) / "SDD" / "acceptance.yaml"
    lock_problems = vh.spec_lock_problems(paths, fid)
    if lock_problems:
        print("BLOQUEADO: solo se ejecuta acceptance aprobado en GATE#1 y sin cambios:", file=sys.stderr)
        for problem in lock_problems:
            print(f"  - {problem}", file=sys.stderr)
        return 2
    try:
        spec = hl.load_yaml(acceptance_path)
    except hl.YamlError as exc:
        print(f"BLOQUEADO: {exc}", file=sys.stderr)
        return 2
    problems = vh.acceptance_problems(spec)
    if problems:
        print("BLOQUEADO: acceptance.yaml invalido:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 2
    only = {item.strip() for item in (args.only or "").split(",") if item.strip()}
    results = []
    for check in spec["checks"]:
        if only and check["id"] not in only:
            continue
        if check["kind"] == "command":
            outcome = run_command(check, paths.root, fid)
        elif check["kind"] == "file":
            outcome = run_file(check, paths.root)
        else:
            outcome = {"status": "manual", "reason": "inspection: la resuelve el reviewer con evidencia"}
        results.append({"id": check["id"], "kind": check["kind"], "required": check["required"],
                        **{k: v for k, v in outcome.items() if v is not None}})
    required = [r for r in results if r["required"] and r["kind"] != "inspection"]
    blocked = [r["id"] for r in required if r["status"] == "blocked"]
    failed = [r["id"] for r in required if r["status"] == "fail"]
    try:
        head = subprocess.run(["git", "-C", str(paths.root), "rev-parse", "HEAD"],
                              capture_output=True, text=True, timeout=15)
        git_head = head.stdout.strip() if head.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        git_head = None
    document = {
        "feature_id": fid,
        "run_at": hl.now_iso(),
        "acceptance_sha256": hl.sha256_file(acceptance_path),
        "git_head": git_head,
        "partial": bool(only),
        "results": results,
        "summary": {"required_failed": failed, "required_blocked": blocked,
                    "manual": [r["id"] for r in results if r["status"] == "manual"]},
    }
    if not args.no_write:
        if only:
            print("Aviso: ejecucion parcial (--only); no se sobrescribe acceptance-results.json")
        else:
            hl.dump_json(paths.feature(fid) / "acceptance-results.json", document)
    for item in results:
        detail = item.get("reason") or (f"exit {item['exit_code']}" if "exit_code" in item else "")
        print(f"{item['status'].upper():8} {item['id']} ({item['kind']}{', obligatorio' if item['required'] else ''}) {detail}")
    if blocked:
        print(f"BLOQUEADO por herramientas: {', '.join(blocked)}")
        return 2
    if failed:
        print(f"FALLAN obligatorios: {', '.join(failed)}")
        return 1
    print("Todos los checks obligatorios ejecutables pasan" + (" (quedan inspecciones manuales)" if document["summary"]["manual"] else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
