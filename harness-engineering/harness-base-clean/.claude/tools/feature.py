#!/usr/bin/env python3
"""Motor de estado de las features: unico escritor de state.yaml.

Uso:
  feature.py add ID "titulo" [--tags a,b] [--priority N] [--budget USD] [--notes TEXTO]
  feature.py start ID
  feature.py status [ID]
  feature.py transition ID EVENTO [--by human|yolo-mode] [--response TEXTO]
                                  [--rationale TEXTO] [--reason TEXTO] [--dry-run]

`transition` aplica .claude/contracts/workflow.toml: comprueba que el evento existe
desde la fase actual, que el actor es el correcto y que todas sus guards pasan.
Si algo falla no escribe nada y sale con codigo 1.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_lib as hl  # noqa: E402
import validate_harness as vh  # noqa: E402

NEXT_ACTION = {
    "intake": "Ejecuta: python3 .claude/tools/feature.py transition {id} start_exploration",
    "exploration": "Lanza el subagente explorer (PHASE: exploration)",
    "design": "Lanza el subagente designer (PHASE: design)",
    "gate1_pending": "PARA. GATE#1: el humano decide con /approve {id} o /reject {id} <cambios>",
    "implementation": "Lanza el subagente builder (PHASE: implementation, ATTEMPT: {build})",
    "verification": "Lanza el subagente reviewer (PHASE: verification, ATTEMPT: {verification})",
    "blocked": "PARA. Decision humana: replan | retry_exploration | retry_build | retry_verification | cancel",
    "archived": "Cerrada. Muestra el resumen de archive.md y el coste final",
    "cancelled": "Cancelada",
}


def _git(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout if result.returncode == 0 else None


def _base_snapshot(root: Path) -> tuple[str | None, list[str]]:
    head = _git(root, "rev-parse", "HEAD")
    status = _git(root, "status", "--porcelain=v1", "--untracked-files=all", "--", ".") or ""
    dirty = [line for line in status.splitlines() if line.strip() and ".claude/" not in line]
    return (head.strip() if head else None), dirty[:200]


def _next_action(state: dict) -> str:
    attempts = state.get("attempts") or {}
    return NEXT_ACTION[state["phase"]].format(
        id=state["feature_id"], build=attempts.get("build", 0), verification=attempts.get("verification", 0)
    )


def _save_feature_status(paths: hl.Paths, feature_id: str, status: str) -> None:
    data = hl.load_json(paths.feature_list)
    for item in data["features"]:
        if item.get("id") == feature_id:
            item["status"] = status
    hl.dump_json(paths.feature_list, data)


def _print_acceptance_commands(paths: hl.Paths, feature_id: str) -> None:
    acceptance = hl.load_yaml(paths.feature(feature_id) / "SDD" / "acceptance.yaml") or {}
    sensitive = {item.split(" ")[0] for item in vh.sensitive_commands(acceptance)}
    print("Comandos de aceptacion que se ejecutaran sin mas confirmacion tras GATE#1 (muestralos al humano):")
    for check in acceptance.get("checks", []):
        if isinstance(check, dict) and check.get("kind") == "command":
            flag = " [SENSIBLE: requiere aprobacion humana explicita]" if check.get("id") in sensitive else ""
            print(f"  {check.get('id')}{flag} (cwd {check.get('cwd', '.')}): {check.get('command')}")


def _clean(record: dict) -> dict:
    return {key: value for key, value in record.items() if value not in (None, "", [])}


# ---------------------------------------------------------------------------
# Comandos
# ---------------------------------------------------------------------------


def cmd_add(paths: hl.Paths, args: argparse.Namespace) -> int:
    if not hl.FEATURE_ID_RE.match(args.feature_id):
        print(f"ID invalido {args.feature_id!r}: usa MAYUSCULAS-NNN, p. ej. AUTH-001", file=sys.stderr)
        return 2
    data = hl.load_json(paths.feature_list)
    if any(item.get("id") == args.feature_id for item in data["features"]):
        print(f"{args.feature_id} ya existe en feature_list.json", file=sys.stderr)
        return 1
    entry = {
        "id": args.feature_id,
        "title": args.title.strip(),
        "priority": args.priority,
        "tags": [tag.strip() for tag in (args.tags or "").split(",") if tag.strip()],
        "status": "proposed",
    }
    if args.budget:
        entry["budget_usd"] = args.budget
    if args.notes:
        entry["notes"] = args.notes.strip()
    data["features"].append(entry)
    hl.dump_json(paths.feature_list, data)
    print(f"Registrada {args.feature_id} (proposed). Siguiente: python3 .claude/tools/feature.py start {args.feature_id}")
    return 0


def cmd_start(paths: hl.Paths, args: argparse.Namespace) -> int:
    fid = args.feature_id
    feature = hl.find_feature(paths, fid) if hl.FEATURE_ID_RE.match(fid) else None
    if feature is None:
        print(f"{fid} no esta registrada. Usa: feature.py add {fid} \"titulo\"", file=sys.stderr)
        return 1
    if (paths.feature(fid) / "state.yaml").exists():
        print(f"{fid} ya tiene estado. Usa: feature.py status {fid} (o la skill feature-resume)", file=sys.stderr)
        return 1
    if feature.get("status") != "proposed":
        print(f"{fid} tiene status {feature.get('status')!r}; solo se inician features proposed", file=sys.stderr)
        return 1
    state = hl.load_yaml(paths.templates / "state.yaml")
    now = hl.now_iso()
    state.update({
        "feature_id": fid,
        "title": feature.get("title"),
        "status": "in_progress",
        "phase": "intake",
        "phase_entered_at": now,
        "created_at": now,
        "updated_at": now,
    })
    state["next_action"] = _next_action(state)
    (paths.feature(fid) / "SDD").mkdir(parents=True, exist_ok=True)
    hl.dump_yaml(paths.feature(fid) / "state.yaml", state, header="# Gestionado por .claude/tools/feature.py. No editar a mano.\n")
    _save_feature_status(paths, fid, "in_progress")
    hl.append_event(paths, fid, {"event": "feature_started", "title": feature.get("title")})
    print(f"{fid} iniciada en intake. Siguiente: {state['next_action']}")
    return 0


def cmd_transition(paths: hl.Paths, args: argparse.Namespace) -> int:
    fid = args.feature_id
    if not hl.FEATURE_ID_RE.match(fid) or not (paths.feature(fid) / "state.yaml").is_file():
        print(f"{fid}: feature sin estado (feature.py start {fid})", file=sys.stderr)
        return 1
    options = {"by": args.by, "response": args.response, "rationale": args.rationale, "reason": args.reason}
    ctx = vh.load_context(paths, fid, options)
    state, workflow = ctx.state, ctx.workflow
    phase = state.get("phase")
    transition = hl.find_transition(workflow, phase, args.event)
    if transition is None:
        allowed = ", ".join(t["event"] for t in hl.transitions_from(workflow, phase)) or "ninguno"
        print(f"RECHAZADA: '{args.event}' no existe desde '{phase}'. Eventos validos: {allowed}", file=sys.stderr)
        return 1
    problems = []
    if transition["actor"] == "human":
        if args.by == "yolo-mode" and args.event != "approved":
            problems.append("yolo-mode solo puede aprobar GATE#1; el resto de decisiones humanas no se delegan")
    elif args.by not in (None, "orchestrator"):
        problems.append(f"'{args.event}' es una transicion del orquestador; no uses --by {args.by}")
    problems += vh.run_guards(ctx, transition.get("guards", []))
    if problems:
        print(f"RECHAZADA {fid}: {phase} --{args.event}--> {transition['to']}", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    if args.dry_run:
        print(f"OK (dry-run) {fid}: {phase} --{args.event}--> {transition['to']}")
        return 0

    now = hl.now_iso()
    target = transition["to"]
    attempts = state["attempts"]
    gate = state["gate1"]
    event = args.event
    if event == "approved":
        gate.update(status="approved", decided_by=args.by, decided_at=now, response=args.response, rationale=args.rationale)
        attempts.update(build=1, verification=0, repair=0, human_retries=0)
        state["base_commit"], state["base_dirty"] = _base_snapshot(paths.root)
        hl.dump_json(paths.feature(fid) / "SDD" / "spec.lock.json", {
            "feature_id": fid, "locked_at": now, "approved_by": args.by, "files": vh.spec_fingerprint(paths, fid),
        })
    elif event == "changes_requested":
        gate.update(status="changes_requested", decided_by="human", decided_at=now, response=args.response, rationale=None)
    elif event in {"build_complete", "retry_verification"}:
        attempts["verification"] += 1
    elif event == "repairable_failure":
        attempts["repair"] += 1
        attempts["build"] += 1
    elif event == "retry_build":
        attempts["human_retries"] += 1
        attempts["build"] += 1
    elif event == "replan":
        gate.update(status="pending", decided_by=None, decided_at=None, response=None, rationale=None)
        attempts.update(build=0, verification=0, repair=0, human_retries=0)
        state["base_commit"], state["base_dirty"] = None, []
        (paths.feature(fid) / "SDD" / "spec.lock.json").unlink(missing_ok=True)
    if event in {"pass", "repairable_failure", "human_required"}:
        result = hl.load_yaml(paths.feature(fid) / "verification-result.yaml") or {}
        state["last_verdict"] = result.get("verdict")
    if target == "blocked":
        state["blocked_reason"] = args.reason or args.response
    elif phase == "blocked":
        state["blocked_reason"] = None
    idle = set(workflow["workflow"]["terminal_phases"]) | set(workflow["workflow"].get("human_wait_phases", []))
    active = target not in idle
    lock = state["lock"]
    lock["since"] = (lock.get("since") or now) if active else None
    lock["active"] = active
    state.update(phase=target, status=vh.expected_status(target), phase_entered_at=now, updated_at=now)
    state["next_action"] = _next_action(state)

    hl.dump_yaml(paths.feature(fid) / "state.yaml", state, header="# Gestionado por .claude/tools/feature.py. No editar a mano.\n")
    _save_feature_status(paths, fid, state["status"])
    hl.append_event(paths, fid, _clean({
        "event": "transition", "transition": event, "from": phase, "to": target,
        "by": args.by or "orchestrator", "response": args.response, "rationale": args.rationale, "reason": args.reason,
        "spec": vh.spec_fingerprint(paths, fid) if event == "design_complete" else None,
    }))
    print(f"OK {fid}: {phase} --{event}--> {target}")
    if event == "design_complete":
        _print_acceptance_commands(paths, fid)
    if target in {"archived", "cancelled"} and ctx.config.get("cost", {}).get("enabled", True):
        import ledger

        snapshot = ledger.write_snapshot(paths, fid, ctx.config)
        print(f"Coste final estimado: ${snapshot['total_usd']:.4f} ({snapshot['budget']['status']}) -> cost.json")
    print(f"Siguiente: {state['next_action']}")
    return 0


def cmd_status(paths: hl.Paths, args: argparse.Namespace) -> int:
    if not args.feature_id:
        print(f"{'feature':<14}{'estado':<13}{'fase':<16}siguiente")
        for item in hl.load_features(paths):
            fid = item.get("id", "?")
            state_path = paths.feature(fid) / "state.yaml"
            state = hl.load_yaml(state_path) if state_path.is_file() else {}
            print(f"{fid:<14}{str(item.get('status')):<13}{str(state.get('phase', '-')):<16}"
                  f"{state.get('next_action', 'feature.py start ' + fid)}")
        return 0
    fid = args.feature_id
    if not hl.FEATURE_ID_RE.match(fid) or not (paths.feature(fid) / "state.yaml").is_file():
        print(f"{fid}: sin estado", file=sys.stderr)
        return 1
    ctx = vh.load_context(paths, fid)
    state, workflow = ctx.state, ctx.workflow
    gate, attempts, lock = state.get("gate1") or {}, ctx.attempts, state.get("lock") or {}
    print(f"{fid} - {state.get('title')}")
    print(f"  fase: {state.get('phase')} ({state.get('status')}) desde {state.get('phase_entered_at')}")
    print(f"  intentos: build {attempts.get('build')} | verificacion {attempts.get('verification')} | "
          f"repair {attempts.get('repair')}/{workflow['workflow']['max_repair_attempts']} | "
          f"reintentos humanos {attempts.get('human_retries')}")
    print(f"  GATE#1: {gate.get('status')} {('por ' + str(gate.get('decided_by'))) if gate.get('decided_by') else ''}")
    if state.get("last_verdict"):
        print(f"  ultimo veredicto: {state['last_verdict']}")
    if state.get("blocked_reason"):
        print(f"  bloqueo: {state['blocked_reason']}")
    if lock.get("active"):
        since = hl.parse_iso(lock.get("since"))
        age = (hl.parse_iso(hl.now_iso()) - since).total_seconds() / 60 if since else 0
        stale = age > float(ctx.config.get("orchestration", {}).get("lock_stale_minutes", 120))
        print(f"  lock activo desde {lock.get('since')}{' (POSIBLEMENTE OBSOLETO: confirma con el humano)' if stale else ''}")
    allowed = [f"{t['event']} ({t['actor']})" for t in hl.transitions_from(workflow, state.get("phase"))]
    print(f"  eventos validos: {', '.join(allowed) or 'ninguno'}")
    if ctx.config.get("cost", {}).get("enabled", True):
        try:
            import ledger

            report = ledger.feature_cost(paths, fid, ctx.config)
            print(f"  coste estimado: ${report['total_usd']:.4f} ({report['budget']['status']})")
        except (hl.HarnessError, OSError, ValueError) as exc:
            print(f"  coste: no disponible ({exc})")
    runs = [e for e in ctx.events if e.get("event") == "subagent_stop"][-4:]
    for run in runs:
        print(f"  runtime {run.get('agent')} {run.get('agent_id')} fin {run.get('finished_at')}")
    print(f"  siguiente: {state.get('next_action')}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=None)
    sub = parser.add_subparsers(dest="command", required=True)
    add = sub.add_parser("add")
    add.add_argument("feature_id")
    add.add_argument("title")
    add.add_argument("--tags")
    add.add_argument("--priority", type=int, default=3)
    add.add_argument("--budget", type=float)
    add.add_argument("--notes")
    start = sub.add_parser("start")
    start.add_argument("feature_id")
    status = sub.add_parser("status")
    status.add_argument("feature_id", nargs="?")
    move = sub.add_parser("transition")
    move.add_argument("feature_id")
    move.add_argument("event")
    move.add_argument("--by", choices=["human", "yolo-mode", "orchestrator"])
    move.add_argument("--response")
    move.add_argument("--rationale")
    move.add_argument("--reason")
    move.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    paths = hl.Paths(args.root)
    handlers = {"add": cmd_add, "start": cmd_start, "status": cmd_status, "transition": cmd_transition}
    try:
        return handlers[args.command](paths, args)
    except hl.HarnessError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 - error interno, distinto de una transicion rechazada
        print(f"ERROR INTERNO {exc!r}. Ejecuta la skill harness-doctor.", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
