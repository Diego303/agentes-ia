#!/usr/bin/env python3
"""Motor de estado de las features: unico escritor de state.yaml.

Uso:
  feature.py add ID "titulo" [--tags a,b] [--priority N] [--budget USD] [--notes TEXTO]
  feature.py start ID
  feature.py status [ID]
  feature.py transition ID EVENTO [--by human|yolo-mode] [--response TEXTO]
                                  [--rationale TEXTO] [--reason TEXTO] [--dry-run]
  feature.py specialists ID [--insertion pre-gate1|post-implementation|post-verification] [--json]
  feature.py metrics [--state-dir RUTA] [--json]

`transition` aplica .claude/contracts/workflow.toml: comprueba que el evento existe
desde la fase actual, que el actor es el correcto y que todas sus guards pasan.
Si algo falla no escribe nada y sale con codigo 1.

`specialists` y `metrics` solo leen: el primero calcula que especialistas tocan
en cada punto de insercion (tags y rutas cambiadas); el segundo agrega las
metricas de todas las features de un directorio de estado.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import statistics
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
    "implementation": "Lanza el subagente builder (PHASE: implementation, ATTEMPT: {build}, MODE: {mode})",
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


def _next_action(state: dict, last_event: str | None = None) -> str:
    """Siguiente accion. MODE es repair solo si se entra en implementation por repairable_failure."""
    attempts = state.get("attempts") or {}
    mode = "repair" if last_event == "repairable_failure" else "build"
    return NEXT_ACTION[state["phase"]].format(
        id=state["feature_id"], build=attempts.get("build", 0), verification=attempts.get("verification", 0),
        mode=mode,
    )


def _last_activity(state: dict, events: list[dict]):
    """Ultima actividad conocida: updated_at del estado o el ultimo evento (transicion o subagent_stop)."""
    stamps = [hl.parse_iso(state.get("updated_at"))]
    stamps += [hl.parse_iso(event.get("ts")) for event in events[-50:]]
    stamps += [hl.parse_iso(event.get("finished_at")) for event in events[-50:] if event.get("event") == "subagent_stop"]
    known = [stamp for stamp in stamps if stamp is not None]
    return max(known) if known else None


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
        print(f"ID invalido {args.feature_id!r}: segmentos en MAYUSCULAS terminados en numero, "
              "p. ej. AUTH-001 o F4-PORT-AGENT-01", file=sys.stderr)
        return 2
    if args.budget is not None and args.budget <= 0:
        print("--budget debe ser un numero de USD mayor que 0", file=sys.stderr)
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
    if args.budget is not None:
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
    elif event in {"replan", "retry_exploration"}:
        # Las dos salidas vuelven a especificar: la aprobacion anterior deja de valer (hallazgo H-02).
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
    state["next_action"] = _next_action(state, event)

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
        print(f"{'feature':<20}{'estado':<13}{'fase':<16}siguiente")
        for item in hl.load_features(paths):
            fid = item.get("id", "?")
            state_path = paths.feature(fid) / "state.yaml"
            state = hl.load_yaml(state_path) if state_path.is_file() else {}
            print(f"{fid:<20}{str(item.get('status')):<13}{str(state.get('phase', '-')):<16}"
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
        # Hallazgo H-01: lo que importa es la inactividad, no la antiguedad del lock.
        activity = _last_activity(state, ctx.events) or hl.parse_iso(lock.get("since"))
        idle = (hl.parse_iso(hl.now_iso()) - activity).total_seconds() / 60 if activity else 0
        stale = idle > float(ctx.config.get("orchestration", {}).get("lock_stale_minutes", 120))
        print(f"  lock activo desde {lock.get('since')}, sin actividad desde hace {idle:.0f} min"
              f"{' (POSIBLEMENTE OBSOLETO: confirma con el humano)' if stale else ''}")
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


INSERTIONS = ("pre-gate1", "post-implementation", "post-verification")


def changed_paths(root: Path, base: str | None) -> list[str]:
    """Archivos cambiados desde base (o HEAD) mas los no versionados, relativos a la raiz y sin el estado."""
    found: set[str] = set()
    for args in (("diff", "--name-only", base or "HEAD", "--", "."), ("ls-files", "--others", "--exclude-standard")):
        output = _git(root, *args)
        if output is None:
            raise hl.HarnessError(f"git {args[0]} fallo: sin git no se pueden evaluar triggers_on_paths")
        found.update(line.strip() for line in output.splitlines() if line.strip())
    return sorted(path for path in found if not path.startswith(".claude/state/"))


def select_specialists(registry: dict, tags: list, insertion: str, changed: list[str]) -> list[dict]:
    """Especialistas de un punto de insercion: por tag ("*" = siempre) y, en post-implementation, por ruta."""
    wanted = {str(tag).lower() for tag in tags}
    selected = []
    for entry in registry.get("agents") or []:
        if not isinstance(entry, dict) or entry.get("role") != "specialist" or entry.get("insertion") != insertion:
            continue
        triggers = [str(tag).lower() for tag in entry.get("triggers_on_tags") or []]
        reasons = ["siempre"] if "*" in triggers else [f"tag {tag}" for tag in triggers if tag in wanted]
        if insertion == "post-implementation":
            for pattern in entry.get("triggers_on_paths") or []:
                hits = [path for path in changed if fnmatch.fnmatchcase(path, str(pattern))]
                if hits:
                    reasons.append(f"ruta {hits[0]} ~ {pattern}" + (f" (+{len(hits) - 1})" if len(hits) > 1 else ""))
        if reasons:
            selected.append({"name": entry.get("name"), "phase": entry.get("phase"), "reasons": reasons})
    return selected


def cmd_specialists(paths: hl.Paths, args: argparse.Namespace) -> int:
    feature = hl.find_feature(paths, args.feature_id)
    if feature is None:
        raise hl.HarnessError(f"{args.feature_id} no esta en feature_list.json")
    registry = hl.load_yaml(paths.registry) or {}
    state_path = paths.feature(args.feature_id) / "state.yaml"
    state = (hl.load_yaml(state_path) or {}) if state_path.is_file() else {}
    insertions = [args.insertion] if args.insertion else list(INSERTIONS)
    changed = changed_paths(paths.root, state.get("base_commit")) if "post-implementation" in insertions else []
    result = {insertion: select_specialists(registry, feature.get("tags") or [], insertion, changed)
              for insertion in insertions}
    if args.json:
        print(json.dumps({"feature": args.feature_id, "changed_paths": changed, "specialists": result},
                         ensure_ascii=False, indent=2))
        return 0
    print(f"{args.feature_id} - tags: {', '.join(feature.get('tags') or []) or '(ninguno)'}")
    for insertion, chosen in result.items():
        print(f"[{insertion}]")
        for item in chosen:
            print(f"  {item['name']:<28} PHASE: {item['phase'] or '-':<15} por: {'; '.join(item['reasons'])}")
        if not chosen:
            print("  (ninguno)")
    return 0


def _percentile(values: list[float], fraction: float) -> float:
    """Percentil por rango mas cercano (sin interpolar): un valor que de verdad ocurrio."""
    ordered = sorted(values)
    return ordered[max(0, min(len(ordered) - 1, int(-(-fraction * len(ordered) // 1)) - 1))]


def _events(log: Path) -> list[dict]:
    events = []
    if log.is_file():
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if isinstance(record, dict):
                events.append(record)
    return events


def collect_metrics(state_dir: Path) -> dict:
    """Metricas agregadas de todas las features de un directorio de estado. Solo lee."""
    phases: dict[str, int] = {}
    transitions: dict[str, int] = {}
    approvals: dict[str, int] = {}
    runs_by_agent: dict[str, int] = {}
    costs: list[float] = []
    cost_by_agent: dict[str, float] = {}
    lead_hours: list[float] = []
    first_pass = with_repair = blocked_ever = 0
    features = sorted(path for path in state_dir.iterdir()
                      if path.is_dir() and hl.FEATURE_ID_RE.match(path.name) and (path / "state.yaml").is_file())
    for folder in features:
        state = hl.load_yaml(folder / "state.yaml") or {}
        phase = str(state.get("phase") or "?")
        phases[phase] = phases.get(phase, 0) + 1
        events = _events(folder / "event.log")
        moves = [event for event in events if event.get("event") == "transition"]
        for move in moves:
            name = str(move.get("transition"))
            transitions[name] = transitions.get(name, 0) + 1
            if name == "approved":
                approvals[str(move.get("by"))] = approvals.get(str(move.get("by")), 0) + 1
        verdicts = [str(move.get("transition")) for move in moves if move.get("from") == "verification"]
        if phase == "archived":
            first_pass += bool(verdicts) and verdicts[0] == "pass"
            with_repair += "repairable_failure" in verdicts
            done = next((move.get("ts") for move in reversed(moves) if move.get("transition") == "pass"), None)
            start, end = hl.parse_iso(state.get("created_at")), hl.parse_iso(done)
            if start and end:
                lead_hours.append((end - start).total_seconds() / 3600)
        blocked_ever += any(move.get("to") == "blocked" for move in moves)
        last_run: dict[str, dict] = {}
        for event in events:
            if event.get("event") == "subagent_stop":
                last_run[str(event.get("agent_id") or len(last_run))] = event  # el ultimo es acumulado
        for run in last_run.values():
            agent = str(run.get("agent") or "unknown")
            runs_by_agent[agent] = runs_by_agent.get(agent, 0) + 1
        cost_file = folder / "cost.json"
        if cost_file.is_file():
            data = hl.load_json(cost_file)
            if isinstance(data.get("total_usd"), (int, float)):
                costs.append(float(data["total_usd"]))
            for agent, slot in (data.get("by_agent") or {}).items():
                cost_by_agent[agent] = cost_by_agent.get(agent, 0.0) + float((slot or {}).get("cost_usd") or 0)
            if (data.get("orchestrator") or {}).get("cost_usd"):
                cost_by_agent["orquestador"] = cost_by_agent.get("orquestador", 0.0) + float(data["orchestrator"]["cost_usd"])
    archived = phases.get("archived", 0)
    presented = transitions.get("design_complete", 0)

    def ratio(part: float, whole: float) -> float | None:
        return round(part / whole, 3) if whole else None

    return {
        "state_dir": str(state_dir),
        "features": len(features),
        "by_phase": dict(sorted(phases.items())),
        "archived": archived,
        "verification": {
            "first_pass": first_pass, "with_repair": with_repair,
            "first_pass_rate": ratio(first_pass, archived),
            "repairs": transitions.get("repairable_failure", 0),
        },
        "gate1": {
            "presented": presented, "approved_by": dict(sorted(approvals.items())),
            "changes_requested": transitions.get("changes_requested", 0),
            "changes_requested_rate": ratio(transitions.get("changes_requested", 0), presented),
        },
        "human_interventions": {
            "features_blocked_ever": blocked_ever,
            **{name: transitions.get(name, 0) for name in (
                "escalate", "human_required", "replan", "retry_exploration", "retry_build", "retry_verification",
                "cancel")},
        },
        "subagent_runs": {"total": sum(runs_by_agent.values()), "by_agent": dict(sorted(runs_by_agent.items()))},
        "cost_usd": {
            "features_with_cost": len(costs), "total": round(sum(costs), 2),
            "mean": round(statistics.mean(costs), 2) if costs else None,
            "median": round(statistics.median(costs), 2) if costs else None,
            "p90": round(_percentile(costs, 0.9), 2) if costs else None,
            "by_agent": {k: round(v, 2) for k, v in sorted(cost_by_agent.items(), key=lambda item: -item[1])},
        },
        "lead_time_hours": {
            "median": round(statistics.median(lead_hours), 1) if lead_hours else None,
            "p90": round(_percentile(lead_hours, 0.9), 1) if lead_hours else None,
        },
        "transitions": dict(sorted(transitions.items())),
    }


def cmd_metrics(paths: hl.Paths, args: argparse.Namespace) -> int:
    state_dir = Path(args.state_dir).expanduser() if args.state_dir else paths.state
    if not state_dir.is_dir():
        raise hl.HarnessError(f"{state_dir} no es un directorio de estado")
    data = collect_metrics(state_dir)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    verification, gate, human, cost = data["verification"], data["gate1"], data["human_interventions"], data["cost_usd"]

    def pct(value: float | None) -> str:
        return "-" if value is None else f"{value * 100:.0f} %"

    print(f"Metricas de {data['state_dir']}")
    print(f"  features: {data['features']} | por fase: {', '.join(f'{k} {v}' for k, v in data['by_phase'].items()) or '-'}")
    print(f"  verificacion: PASS a la primera {verification['first_pass']}/{data['archived']} "
          f"({pct(verification['first_pass_rate'])}) | con repair {verification['with_repair']} | "
          f"repairs {verification['repairs']}")
    print(f"  GATE#1: presentados {gate['presented']} | aprobados por {gate['approved_by'] or '-'} | "
          f"cambios pedidos {gate['changes_requested']} ({pct(gate['changes_requested_rate'])})")
    print(f"  intervenciones humanas: bloqueadas alguna vez {human['features_blocked_ever']} | escalate "
          f"{human['escalate']} | human_required {human['human_required']} | replan {human['replan']} | "
          f"retry_build {human['retry_build']} | cancel {human['cancel']}")
    print(f"  subagentes: {data['subagent_runs']['total']} ejecuciones "
          f"({', '.join(f'{k} {v}' for k, v in data['subagent_runs']['by_agent'].items()) or '-'})")
    if cost["features_with_cost"]:
        print(f"  coste (cost.json, precios API): total ${cost['total']} | media ${cost['mean']} | "
              f"mediana ${cost['median']} | p90 ${cost['p90']} sobre {cost['features_with_cost']} features")
    lead = data["lead_time_hours"]
    if lead["median"] is not None:
        print(f"  tiempo de ciclo (inicio -> archived): mediana {lead['median']} h | p90 {lead['p90']} h")
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
    specialists = sub.add_parser("specialists")
    specialists.add_argument("feature_id")
    specialists.add_argument("--insertion", choices=INSERTIONS)
    specialists.add_argument("--json", action="store_true")
    metrics = sub.add_parser("metrics")
    metrics.add_argument("--state-dir")
    metrics.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    paths = hl.Paths(args.root)
    handlers = {"add": cmd_add, "start": cmd_start, "status": cmd_status, "transition": cmd_transition,
                "specialists": cmd_specialists, "metrics": cmd_metrics}
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
