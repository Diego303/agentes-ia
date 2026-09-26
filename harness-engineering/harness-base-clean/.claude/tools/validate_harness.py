#!/usr/bin/env python3
"""Validador determinista del harness (bundle y features).

Uso:
  python3 .claude/tools/validate_harness.py                        bundle + todas las features
  python3 .claude/tools/validate_harness.py --feature F            bundle + una feature
  python3 .claude/tools/validate_harness.py --feature F --pre-gate solo artefactos SDD listos para GATE#1
  python3 .claude/tools/validate_harness.py --json                 salida JSON

Exit 0 sin errores, 1 con errores. Los avisos (warning) no bloquean.
Las guards de .claude/contracts/workflow.toml se implementan aqui (GUARDS) y las usa feature.py.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_lib as hl  # noqa: E402

VERDICTS = {"PASS", "FAIL_REPAIRABLE", "FAIL_NONREPAIRABLE", "BLOCKED_TOOLING"}
FEATURE_STATUSES = {"proposed", "in_progress", "blocked", "archived", "cancelled"}
GATE_STATUSES = {"pending", "approved", "changes_requested"}
MODES = {"manual", "auto", "yolo"}
MODELS = {"sonnet", "opus", "haiku", "fable", "inherit"}
EFFORTS = {"low", "medium", "high", "xhigh", "max"}
COLORS = {"red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"}
PRICE_FIELDS = ("input", "output", "cache_write_5m", "cache_write_1h", "cache_read")
REQ_ID_RE = re.compile(r"\bN?FR-[0-9]+\b")
FR_ID_RE = re.compile(r"\bFR-[0-9]+\b")
CHECK_ID_RE = re.compile(r"^AC-[0-9]+$")
TRIVIAL_COMMAND_RE = re.compile(r"^\s*(true|:|exit\s+0|echo\b[^|;&]*)\s*$")
UNSAFE_COMMANDS = [
    (re.compile(r"\bsudo\b"), "sudo"),
    (re.compile(r"\brm\s+-[a-zA-Z]*[rR][a-zA-Z]*\s+(/|~|\$HOME|\*|\.{1,2}(\s|$))"), "rm recursivo sobre raiz, home o comodin"),
    (re.compile(r"\bgit\s+(push|commit|reset|clean|stash|rebase|checkout|restore|switch)\b"), "git que altera historial o descarta cambios"),
    (re.compile(r"\b(curl|wget)\b[^|;&]*\|\s*(ba|z|k|da)?sh\b"), "descarga ejecutada en shell"),
    (re.compile(r"\b(mkfs|fdisk|shutdown|reboot|halt)\b"), "comando de sistema destructivo"),
    (re.compile(r"\bdd\b[^\n]*\bof=/dev/"), "dd sobre dispositivo"),
    (re.compile(r":\(\)\s*\{"), "fork bomb"),
    (re.compile(r"\bchmod\s+-R\s+777\b"), "chmod -R 777"),
]
SECRET_REF = hl.SECRET_REF
INLINE_CODE = hl.INLINE_CODE
PHASE_REQUIREMENTS = {
    "intake": [],
    "exploration": [],
    "design": ["context_present"],
    "gate1_pending": ["context_present", "sdd_valid"],
    "implementation": ["context_present", "sdd_valid", "gate1_was_approved", "spec_unchanged"],
    "verification": ["context_present", "sdd_valid", "gate1_was_approved", "spec_unchanged",
                     "implementation_report_present"],
    "archived": ["context_present", "sdd_valid", "gate1_was_approved", "spec_unchanged",
                 "implementation_report_present", "verdict_pass", "required_checks_passed", "archive_present",
                 "runtime_history_complete"],
    "blocked": ["blocked_reason_present"],
    "cancelled": [],
}


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    path: str
    message: str


@dataclass
class Report:
    root: Path
    issues: list[Issue] = field(default_factory=list)

    def add(self, severity: str, code: str, path: Path | str, message: str) -> None:
        path = Path(path)
        try:
            shown = path.resolve().relative_to(self.root).as_posix()
        except ValueError:
            shown = path.as_posix()
        self.issues.append(Issue(severity, code, shown, message))

    def error(self, code: str, path: Path | str, message: str) -> None:
        self.add("error", code, path, message)

    def warn(self, code: str, path: Path | str, message: str) -> None:
        self.add("warning", code, path, message)

    @property
    def ok(self) -> bool:
        return not any(item.severity == "error" for item in self.issues)


# ---------------------------------------------------------------------------
# Acceptance y trazabilidad (compartido con run_acceptance.py)
# ---------------------------------------------------------------------------


def _safe_relative(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts


def acceptance_problems(data: object) -> list[str]:
    """Errores de esquema y seguridad de un acceptance.yaml ya parseado."""
    if not isinstance(data, dict):
        return ["el documento debe ser un mapeo"]
    problems = []
    if data.get("version") != 1:
        problems.append("version debe ser 1")
    if not isinstance(data.get("feature_id"), str):
        problems.append("falta feature_id")
    checks = data.get("checks")
    if not isinstance(checks, list) or not checks:
        return problems + ["checks debe ser una lista no vacia"]
    seen: set[str] = set()
    executable_required = False
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            problems.append(f"checks[{index}] no es un mapeo")
            continue
        cid = check.get("id")
        label = cid if isinstance(cid, str) else f"checks[{index}]"
        if not isinstance(cid, str) or not CHECK_ID_RE.match(cid):
            problems.append(f"{label}: id debe tener formato AC-NNN")
        elif cid in seen:
            problems.append(f"{label}: id duplicado")
        seen.add(str(cid))
        if not isinstance(check.get("title"), str) or not check["title"].strip():
            problems.append(f"{label}: falta title")
        if not isinstance(check.get("required"), bool):
            problems.append(f"{label}: required debe ser true o false")
        covers = check.get("covers")
        if not isinstance(covers, list) or not covers or not all(
            isinstance(item, str) and REQ_ID_RE.fullmatch(item) for item in covers
        ):
            problems.append(f"{label}: covers debe listar IDs FR-NN/NFR-NN")
        kind = check.get("kind")
        if kind == "command":
            command = check.get("command")
            if not isinstance(command, str) or not command.strip():
                problems.append(f"{label}: command vacio")
            else:
                if TRIVIAL_COMMAND_RE.match(command):
                    problems.append(f"{label}: command trivial ({command.strip()!r}) no verifica nada")
                for pattern, reason in UNSAFE_COMMANDS:
                    if pattern.search(command):
                        problems.append(f"{label}: command inseguro ({reason})")
                if SECRET_REF.search(command):
                    problems.append(f"{label}: command referencia secretos (.env, claves, credenciales)")
            if not _safe_relative(check.get("cwd", ".")):
                problems.append(f"{label}: cwd debe ser relativo al repo y sin '..'")
            timeout = check.get("timeout_seconds", 120)
            if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= 3600:
                problems.append(f"{label}: timeout_seconds debe ser un entero entre 1 y 3600")
            code = check.get("expected_exit_code", 0)
            if not isinstance(code, int) or isinstance(code, bool):
                problems.append(f"{label}: expected_exit_code debe ser entero")
            executable_required |= check.get("required") is True
        elif kind == "file":
            if not _safe_relative(check.get("path")):
                problems.append(f"{label}: path debe ser relativo al repo y sin '..'")
            elif SECRET_REF.search(str(check.get("path"))):
                problems.append(f"{label}: path apunta a un secreto")
            expected = check.get("expected")
            if expected not in {"exists", "absent"}:
                problems.append(f"{label}: expected debe ser exists o absent")
            for key in ("contains", "not_contains"):
                if key in check:
                    if expected == "absent":
                        problems.append(f"{label}: {key} no tiene sentido con expected: absent")
                    try:
                        re.compile(str(check[key]))
                    except re.error as exc:
                        problems.append(f"{label}: {key} no es una regex valida ({exc})")
            executable_required |= check.get("required") is True
        elif kind == "inspection":
            for key in ("procedure", "expected"):
                if not isinstance(check.get(key), str) or not check[key].strip():
                    problems.append(f"{label}: inspection necesita {key}")
        else:
            problems.append(f"{label}: kind desconocido {kind!r} (command | file | inspection)")
    if not executable_required:
        problems.append("se necesita al menos un check obligatorio ejecutable (command o file)")
    return problems


def traceability_problems(requirements: str, tasks: str, acceptance: dict) -> list[str]:
    defined = set(REQ_ID_RE.findall(requirements))
    if not defined:
        return ["requirements.md no define ningun FR-NN / NFR-NN"]
    covered = {
        item for check in acceptance.get("checks", []) if isinstance(check, dict)
        for item in (check.get("covers") or []) if isinstance(item, str)
    }
    problems = [f"{req} sin check de aceptacion que lo cubra" for req in sorted(defined - covered)]
    problems += [f"acceptance cubre {req}, que no existe en requirements.md" for req in sorted(covered - defined)]
    in_tasks = set(FR_ID_RE.findall(tasks))
    problems += [f"{req} sin tarea en tasks.md" for req in sorted(r for r in defined if r.startswith("FR-")) if req not in in_tasks]
    return problems


def sensitive_commands(acceptance: dict) -> list[str]:
    """Checks validos que exigen decision humana explicita: red externa o codigo en linea."""
    found = []
    for check in acceptance.get("checks", []):
        if not isinstance(check, dict) or check.get("kind") != "command":
            continue
        command = str(check.get("command") or "")
        reasons = [reason for reason, hit in (("red externa", hl.external_network(command)),
                                               ("codigo en linea", bool(INLINE_CODE.search(command)))) if hit]
        if reasons:
            found.append(f"{check.get('id')} ({', '.join(reasons)})")
    return found


# ---------------------------------------------------------------------------
# Spec lock (congelacion en GATE#1)
# ---------------------------------------------------------------------------


def spec_fingerprint(paths: hl.Paths, feature_id: str) -> dict:
    sdd = paths.feature(feature_id) / "SDD"
    return {f"SDD/{name}": hl.sha256_file(sdd / name) for name in hl.SPEC_FILES if (sdd / name).is_file()}


def spec_lock_problems(paths: hl.Paths, feature_id: str) -> list[str]:
    lock = paths.feature(feature_id) / "SDD" / "spec.lock.json"
    if not lock.is_file():
        return ["falta SDD/spec.lock.json (la spec se congela al aprobar GATE#1)"]
    try:
        recorded = hl.load_json(lock).get("files", {})
    except (ValueError, AttributeError):
        return ["SDD/spec.lock.json ilegible"]
    current = spec_fingerprint(paths, feature_id)
    problems = [f"{name} cambio despues de GATE#1" for name, digest in sorted(recorded.items()) if current.get(name) != digest]
    problems += [f"{name} no estaba en la spec aprobada" for name in sorted(set(current) - set(recorded))]
    return problems


# ---------------------------------------------------------------------------
# Guards (nombres referenciados por workflow.toml)
# ---------------------------------------------------------------------------


@dataclass
class Context:
    paths: hl.Paths
    feature_id: str
    config: dict
    workflow: dict
    state: dict
    feature: dict | None
    events: list[dict]
    args: dict = field(default_factory=dict)

    @property
    def dir(self) -> Path:
        return self.paths.feature(self.feature_id)

    @property
    def attempts(self) -> dict:
        return self.state.get("attempts") or {}


def load_context(paths: hl.Paths, feature_id: str, args: dict | None = None) -> Context:
    state_path = paths.feature(feature_id) / "state.yaml"
    state = hl.load_yaml(state_path) if state_path.is_file() else {}
    return Context(
        paths=paths,
        feature_id=feature_id,
        config=hl.load_config(paths),
        workflow=hl.load_workflow(paths),
        state=state if isinstance(state, dict) else {},
        feature=hl.find_feature(paths, feature_id),
        events=hl.read_events(paths, feature_id),
        args=args or {},
    )


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.is_file() else ""


def _yaml_or_error(path: Path) -> tuple[dict | None, str | None]:
    if not path.is_file():
        return None, f"falta {path.name}"
    try:
        data = hl.load_yaml(path)
    except hl.YamlError as exc:
        return None, str(exc)
    if not isinstance(data, dict):
        return None, f"{path.name} debe ser un mapeo"
    return data, None


def verified_run(event: dict, feature_id: str) -> dict | None:
    """Relee el transcript del subagente que cita el evento: una linea de event.log no basta."""
    import ledger  # import local: ledger no depende del validador

    transcript = event.get("transcript")
    if not isinstance(transcript, str):
        return None
    payload = {"agent_id": event.get("agent_id"), "session_id": event.get("session_id"),
               "transcript_path": str(Path(transcript).expanduser())}
    located = ledger.locate_subagent_transcript(payload)
    if located is None:
        return None
    run = ledger.parse_subagent_transcript(located)
    return run if run["header"].get("feature_id") == feature_id else None


def _runtime_recorded(agent: str) -> Callable[[Context], list[str]]:
    def guard(ctx: Context) -> list[str]:
        since = hl.parse_iso(ctx.state.get("phase_entered_at"))
        for event in reversed(ctx.events):
            if event.get("event") != "subagent_stop" or event.get("agent") != agent or not event.get("agent_id"):
                continue
            run = verified_run(event, ctx.feature_id)
            finished = hl.parse_iso((run or {}).get("finished_at"))
            if run and (since is None or (finished and finished >= since)):
                return []
        return [f"no hay ejecucion real de '{agent}' en esta fase verificable en su transcript "
                "(¿se lanzo como subagente con la cabecera FEATURE_ID? ¿esta activo el hook SubagentStop?). "
                "Si acaba de terminar, reintenta."]
    return guard


def g_feature_registered(ctx: Context) -> list[str]:
    return [] if ctx.feature else [f"{ctx.feature_id} no esta en feature_list.json"]


def g_context_present(ctx: Context) -> list[str]:
    text = _read(ctx.dir / "SDD" / "context.md")
    if not text.strip():
        return ["falta SDD/context.md o esta vacio"]
    return [] if re.search(r"^## ", text, re.MULTILINE) else ["SDD/context.md no tiene secciones '## '"]


def g_sdd_valid(ctx: Context) -> list[str]:
    sdd = ctx.dir / "SDD"
    problems = [f"falta SDD/{name} o esta vacio" for name in hl.SPEC_FILES if not _read(sdd / name).strip()]
    if problems:
        return problems
    acceptance, error = _yaml_or_error(sdd / "acceptance.yaml")
    if error:
        return [f"acceptance.yaml: {error}"]
    problems += [f"acceptance.yaml: {item}" for item in acceptance_problems(acceptance)]
    if acceptance.get("feature_id") != ctx.feature_id:
        problems.append("acceptance.yaml: feature_id no coincide con la feature")
    if "HARNESS_VERIFY_PLACEHOLDER" in _read(ctx.paths.bundle / "bootstrap" / "verify.sh") and any(
        "verify.sh" in str(check.get("command", "")) for check in acceptance.get("checks", []) if isinstance(check, dict)
    ):
        problems.append("acceptance.yaml usa verify.sh, que sigue sin configurar: su exito no demostraria nada")
    problems += traceability_problems(_read(sdd / "requirements.md"), _read(sdd / "tasks.md"), acceptance)
    return problems


def g_decision_recorded(ctx: Context) -> list[str]:
    problems = []
    if ctx.args.get("by") not in {"human", "yolo-mode"}:
        problems.append("decision humana: indica --by human (o --by yolo-mode solo para approved)")
    if not str(ctx.args.get("response") or "").strip():
        problems.append("decision humana: --response debe contener la respuesta literal del humano")
    return problems


def g_approver_authorized(ctx: Context) -> list[str]:
    by = ctx.args.get("by")
    if by == "human":
        return []
    if by != "yolo-mode":
        return ["GATE#1 solo lo aprueba el humano o, por delegacion explicita, yolo-mode"]
    orchestration = ctx.config.get("orchestration", {})
    problems = []
    if orchestration.get("mode") != "yolo":
        problems.append("yolo-mode solo puede aprobar con [orchestration].mode = \"yolo\"")
    stems = [str(tag).lower().rstrip("s") for tag in orchestration.get("human_gate_tags", [])]
    protected = {tag for tag in (ctx.feature or {}).get("tags", [])
                 if any(stem and stem in str(tag).lower() for stem in stems)}
    if protected:
        problems.append(f"tags {sorted(protected)} exigen aprobacion humana incluso en yolo")
    if not str(ctx.args.get("rationale") or "").strip():
        problems.append("yolo-mode exige --rationale citando la regla de AGENTS.md/HARNESS.md aplicada")
    acceptance, _ = _yaml_or_error(ctx.dir / "SDD" / "acceptance.yaml")
    sensitive = sensitive_commands(acceptance or {})
    if sensitive:
        problems.append(f"comandos de aceptacion sensibles {sensitive}: los aprueba el humano, no yolo")
    return problems


def g_reason_recorded(ctx: Context) -> list[str]:
    return [] if str(ctx.args.get("reason") or "").strip() else ["indica --reason con el motivo concreto"]


def g_gate1_was_approved(ctx: Context) -> list[str]:
    gate = ctx.state.get("gate1") or {}
    if gate.get("status") != "approved":
        return ["GATE#1 no esta aprobado"]
    missing = [key for key in ("decided_by", "decided_at", "response") if not gate.get(key)]
    return [f"GATE#1 aprobado sin {', '.join(missing)}"] if missing else []


def g_spec_unchanged(ctx: Context) -> list[str]:
    return spec_lock_problems(ctx.paths, ctx.feature_id)


def g_implementation_report_present(ctx: Context) -> list[str]:
    build = ctx.attempts.get("build") or 0
    text = _read(ctx.dir / "implementation.md")
    if not text.strip():
        return ["falta implementation.md"]
    if not re.search(rf"^#{{1,3}}\s*Build\s+{build}\b", text, re.MULTILINE):
        return [f"implementation.md no tiene la seccion '## Build {build}' del intento actual"]
    return []


def _verification(ctx: Context) -> tuple[dict | None, list[str]]:
    data, error = _yaml_or_error(ctx.dir / "verification-result.yaml")
    if error:
        return None, [error]
    problems = []
    if data.get("verdict") not in VERDICTS:
        problems.append(f"verdict invalido {data.get('verdict')!r}")
    if data.get("build_attempt") != ctx.attempts.get("build"):
        problems.append("verification-result.yaml no corresponde al build actual")
    if data.get("verification_attempt") != ctx.attempts.get("verification"):
        problems.append("verification-result.yaml no corresponde a la verificacion actual")
    return data, problems


def _repairable(data: dict) -> bool:
    flags = data.get("repairability") or {}
    keys = ("reproducible", "in_approved_scope", "design_unchanged", "acceptance_unchanged", "no_irreversible_side_effect")
    return all(flags.get(key) is True for key in keys)


def g_verdict_pass(ctx: Context) -> list[str]:
    data, problems = _verification(ctx)
    if data and data.get("verdict") != "PASS":
        problems.append(f"el veredicto es {data.get('verdict')}, no PASS")
    return problems


def g_verdict_fail_repairable(ctx: Context) -> list[str]:
    data, problems = _verification(ctx)
    if data:
        if data.get("verdict") != "FAIL_REPAIRABLE":
            problems.append(f"el veredicto es {data.get('verdict')}, no FAIL_REPAIRABLE")
        elif not _repairable(data):
            problems.append("FAIL_REPAIRABLE sin todas las condiciones de repairability en true")
    return problems


def g_verdict_requires_human(ctx: Context) -> list[str]:
    data, problems = _verification(ctx)
    if problems or not data:
        return problems
    budget_left = (ctx.attempts.get("repair") or 0) < ctx.workflow["workflow"]["max_repair_attempts"]
    if data.get("verdict") == "PASS":
        return ["el veredicto es PASS: usa el evento pass"]
    if data.get("verdict") == "FAIL_REPAIRABLE" and budget_left and _repairable(data):
        return ["fallo reparable con presupuesto disponible: usa repairable_failure"]
    return []


def g_repair_budget_available(ctx: Context) -> list[str]:
    limit = ctx.workflow["workflow"]["max_repair_attempts"]
    return [] if (ctx.attempts.get("repair") or 0) < limit else [f"presupuesto de repair agotado ({limit})"]


def g_repair_request_valid(ctx: Context) -> list[str]:
    data, error = _yaml_or_error(ctx.dir / "repair-request.yaml")
    if error:
        return [error]
    problems = []
    if data.get("build_attempt") != (ctx.attempts.get("build") or 0) + 1:
        problems.append("repair-request.yaml: build_attempt debe ser el siguiente build")
    if data.get("source_verification_attempt") != ctx.attempts.get("verification"):
        problems.append("repair-request.yaml: source_verification_attempt no coincide")
    if not str(data.get("failure_summary") or "").strip():
        problems.append("repair-request.yaml: falta failure_summary")
    if not (data.get("failing_checks") or data.get("blocking_issues")):
        problems.append("repair-request.yaml: indica failing_checks o blocking_issues")
    if data.get("acceptance_must_remain_unchanged") is not True:
        problems.append("repair-request.yaml: acceptance_must_remain_unchanged debe ser true")
    return problems


def g_required_checks_passed(ctx: Context) -> list[str]:
    acceptance, error = _yaml_or_error(ctx.dir / "SDD" / "acceptance.yaml")
    if error:
        return [error]
    results_path = ctx.dir / "acceptance-results.json"
    if not results_path.is_file():
        return ["falta acceptance-results.json (ejecuta run_acceptance.py)"]
    try:
        results = hl.load_json(results_path)
    except (ValueError, OSError) as exc:
        return [f"acceptance-results.json ilegible ({exc}): vuelve a ejecutar run_acceptance.py"]
    problems = []
    if results.get("acceptance_sha256") != hl.sha256_file(ctx.dir / "SDD" / "acceptance.yaml"):
        problems.append("acceptance-results.json no corresponde al acceptance.yaml aprobado")
    entered = hl.parse_iso(ctx.state.get("phase_entered_at"))
    run_at = hl.parse_iso(results.get("run_at"))
    if ctx.state.get("phase") == "verification" and entered and (not run_at or run_at < entered):
        problems.append("acceptance-results.json es anterior a esta verificacion: el reviewer debe ejecutarlo de nuevo")
    by_id = {item.get("id"): item for item in results.get("results", []) if isinstance(item, dict)}
    verification, _ = _yaml_or_error(ctx.dir / "verification-result.yaml")
    inspections = {
        item.get("id"): item for item in ((verification or {}).get("inspections") or []) if isinstance(item, dict)
    }
    for check in acceptance.get("checks", []):
        if not isinstance(check, dict) or check.get("required") is not True:
            continue
        cid = check.get("id")
        if check.get("kind") == "inspection":
            item = inspections.get(cid) or {}
            if item.get("status") != "pass" or not str(item.get("evidence") or "").strip():
                problems.append(f"{cid}: inspeccion obligatoria sin status pass y evidencia en verification-result.yaml")
        elif (by_id.get(cid) or {}).get("status") != "pass":
            problems.append(f"{cid}: check obligatorio no paso ({(by_id.get(cid) or {}).get('status', 'sin ejecutar')})")
    return problems


def g_archive_present(ctx: Context) -> list[str]:
    return [] if _read(ctx.dir / "archive.md").strip() else ["falta archive.md"]


def g_runtime_history_complete(ctx: Context) -> list[str]:
    agents = {e.get("agent") for e in ctx.events if e.get("event") == "subagent_stop" and e.get("agent_id")}
    required = set(ctx.workflow.get("phase_agents", {}).values())
    return [f"sin ejecucion registrada de '{agent}'" for agent in sorted(required - agents)]


def g_blocked_reason_present(ctx: Context) -> list[str]:
    return [] if str(ctx.state.get("blocked_reason") or "").strip() else ["feature bloqueada sin blocked_reason"]


def g_within_budget(ctx: Context) -> list[str]:
    if not ctx.config.get("cost", {}).get("enabled", True):
        return []
    import ledger  # import local: evita coste de import cuando no se usa

    report = ledger.feature_cost(ctx.paths, ctx.feature_id, ctx.config, include_orchestrator=False, live=True)
    budget = report["budget"]
    problems = []
    if budget["status"] == "BUDGET_EXCEEDED":
        problems.append(f"BUDGET_EXCEEDED: ${report['total_usd']:.2f} (subagentes) > limite ${budget['limit_usd']:.2f}. "
                        "Solo el humano puede ampliar el presupuesto (budget_usd en feature_list.json)")
    if report["unpriced_models"]:
        problems.append(f"uso sin precio conocido {report['unpriced_models']}: anade la tarifa en "
                        "[cost.pricing.models] de harness.toml para poder controlar el gasto")
    return problems


def g_spec_as_presented(ctx: Context) -> list[str]:
    """Lo que se aprueba es exactamente la spec presentada al terminar el diseno (#7)."""
    presented = next((e.get("spec") for e in reversed(ctx.events)
                      if e.get("event") == "transition" and e.get("transition") == "design_complete"), None)
    if not isinstance(presented, dict):
        return ["no consta la huella de la spec presentada en design_complete"]
    if presented != spec_fingerprint(ctx.paths, ctx.feature_id):
        return ["la especificacion cambio despues de presentarse en GATE#1: vuelve a design (changes_requested)"]
    return []


GUARDS: dict[str, Callable[[Context], list[str]]] = {
    "feature_registered": g_feature_registered,
    "context_present": g_context_present,
    "sdd_valid": g_sdd_valid,
    "decision_recorded": g_decision_recorded,
    "approver_authorized": g_approver_authorized,
    "reason_recorded": g_reason_recorded,
    "gate1_was_approved": g_gate1_was_approved,
    "spec_unchanged": g_spec_unchanged,
    "implementation_report_present": g_implementation_report_present,
    "verdict_pass": g_verdict_pass,
    "verdict_fail_repairable": g_verdict_fail_repairable,
    "verdict_requires_human": g_verdict_requires_human,
    "repair_budget_available": g_repair_budget_available,
    "repair_request_valid": g_repair_request_valid,
    "required_checks_passed": g_required_checks_passed,
    "archive_present": g_archive_present,
    "runtime_history_complete": g_runtime_history_complete,
    "blocked_reason_present": g_blocked_reason_present,
    "within_budget": g_within_budget,
    "spec_as_presented": g_spec_as_presented,
    "explorer_runtime_recorded": _runtime_recorded("explorer"),
    "designer_runtime_recorded": _runtime_recorded("designer"),
    "builder_runtime_recorded": _runtime_recorded("builder"),
    "reviewer_runtime_recorded": _runtime_recorded("reviewer"),
}


def run_guards(ctx: Context, names: list[str]) -> list[str]:
    problems = []
    for name in names:
        guard = GUARDS.get(name)
        if guard is None:
            problems.append(f"guard desconocida en el contrato: {name}")
            continue
        problems += [f"[{name}] {item}" for item in guard(ctx)]
    return problems


# ---------------------------------------------------------------------------
# Validacion de feature
# ---------------------------------------------------------------------------


def expected_status(phase: str) -> str:
    return {"archived": "archived", "cancelled": "cancelled", "blocked": "blocked"}.get(phase, "in_progress")


def validate_feature(report: Report, paths: hl.Paths, feature_id: str, pre_gate: bool = False) -> None:
    state_path = paths.feature(feature_id) / "state.yaml"
    if not hl.FEATURE_ID_RE.match(feature_id):
        report.error("feature_id", state_path, f"ID invalido {feature_id!r}")
        return
    if not state_path.is_file():
        report.error("feature_state", state_path, "falta state.yaml")
        return
    try:
        ctx = load_context(paths, feature_id)
    except hl.HarnessError as exc:
        report.error("feature_state", state_path, str(exc))
        return
    if pre_gate:
        for problem in run_guards(ctx, ["context_present", "sdd_valid"]):
            report.error("pre_gate", paths.feature(feature_id) / "SDD", problem)
        acceptance, _ = _yaml_or_error(ctx.dir / "SDD" / "acceptance.yaml")
        for item in sensitive_commands(acceptance or {}):
            report.warn("acceptance_sensitive", ctx.dir / "SDD" / "acceptance.yaml",
                        f"{item}: destacalo en GATE#1; requiere aprobacion humana explicita")
        return
    state, workflow = ctx.state, ctx.workflow
    phase = state.get("phase")
    phases = workflow["workflow"]["phases"]
    if state.get("feature_id") != feature_id:
        report.error("state_feature_id", state_path, "feature_id no coincide con el directorio")
    if phase not in phases:
        report.error("state_phase", state_path, f"fase invalida {phase!r}")
        return
    if state.get("status") != expected_status(phase):
        report.error("state_status", state_path, f"status {state.get('status')!r} incoherente con la fase {phase}")
    attempts = ctx.attempts
    counters = ("build", "verification", "repair", "human_retries")
    if not all(isinstance(attempts.get(key), int) and attempts[key] >= 0 for key in counters):
        report.error("state_attempts", state_path, "attempts.* deben ser enteros >= 0")
    else:
        max_repairs = workflow["workflow"]["max_repair_attempts"]
        if attempts["repair"] > max_repairs:
            report.error("repair_budget", state_path, f"repair {attempts['repair']} supera el maximo {max_repairs}")
        if phase in {"implementation", "verification", "archived"} and \
                attempts["build"] != 1 + attempts["repair"] + attempts["human_retries"]:
            report.error("state_attempts", state_path, "build debe ser 1 + repair + human_retries")
    gate = state.get("gate1") or {}
    if gate.get("status") not in GATE_STATUSES:
        report.error("state_gate", state_path, f"gate1.status invalido {gate.get('status')!r}")
    if gate.get("decided_by") not in {None, "human", "yolo-mode"}:
        report.error("state_gate", state_path, "gate1.decided_by debe ser human o yolo-mode")
    lock = state.get("lock") or {}
    idle = set(workflow["workflow"]["terminal_phases"]) | set(workflow["workflow"].get("human_wait_phases", []))
    if lock.get("active") and phase in idle:
        report.error("state_lock", state_path, "lock activo en una fase terminal o de espera humana")
    if ctx.feature and ctx.feature.get("status") != state.get("status"):
        report.error("feature_status_drift", paths.feature_list,
                     f"{feature_id}: feature_list dice {ctx.feature.get('status')!r} y state.yaml {state.get('status')!r}")
    for problem in run_guards(ctx, PHASE_REQUIREMENTS.get(phase, [])):
        report.error("phase_invariant", paths.feature(feature_id), f"fase {phase}: {problem}")


# ---------------------------------------------------------------------------
# Validacion del bundle
# ---------------------------------------------------------------------------


REQUIRED_FILES = (
    "CLAUDE.md", "AGENTS.md", "HARNESS.md",
    ".claude/harness.toml", ".claude/settings.json", ".claude/feature_list.json", ".claude/CHANGELOG.md",
    ".claude/contracts/workflow.toml", ".claude/agents/agent-registry.yaml",
    ".claude/templates/state.yaml", ".claude/templates/acceptance.yaml",
    ".claude/templates/verification-result.yaml", ".claude/templates/repair-request.yaml",
    ".claude/tools/harness_lib.py", ".claude/tools/feature.py", ".claude/tools/run_acceptance.py",
    ".claude/tools/ledger.py", ".claude/tools/guard.py", ".claude/bootstrap/verify.sh",
)


def _check_config(report: Report, paths: hl.Paths, config: dict) -> None:
    where = paths.harness_toml
    orchestration = config.get("orchestration", {})
    if orchestration.get("mode") not in MODES:
        report.error("config_mode", where, f"[orchestration].mode debe ser uno de {sorted(MODES)}")
    if not isinstance(orchestration.get("human_gate_tags", []), list):
        report.error("config_tags", where, "[orchestration].human_gate_tags debe ser una lista")
    if config.get("project", {}).get("flow_type") != "simple":
        report.error("config_flow", where, "este bundle implementa flow_type = \"simple\"")
    cost = config.get("cost", {})
    warn, limit = cost.get("warn_usd", 0), cost.get("limit_usd", 0)
    if not all(isinstance(v, (int, float)) and v >= 0 for v in (warn, limit)):
        report.error("config_budget", where, "[cost] warn_usd y limit_usd deben ser numeros >= 0")
    elif limit and warn > limit:
        report.error("config_budget", where, "[cost] warn_usd no puede superar limit_usd")
    models = cost.get("pricing", {}).get("models", {})
    if cost.get("enabled", True) and not models:
        report.error("config_pricing", where, "[cost.pricing.models] vacio: no se puede estimar el coste")
    for name, rates in models.items():
        bad = [f for f in PRICE_FIELDS if not isinstance((rates or {}).get(f), (int, float)) or rates[f] < 0]
        if bad:
            report.error("config_pricing", where, f"{name}: faltan o son invalidos {bad}")


def _check_workflow(report: Report, paths: hl.Paths, workflow: dict) -> None:
    where = paths.workflow
    body = workflow.get("workflow", {})
    phases = body.get("phases", [])
    if len(set(phases)) != len(phases) or not phases:
        report.error("workflow_phases", where, "phases vacio o con duplicados")
    for key in ("terminal_phases", "human_wait_phases"):
        if not set(body.get(key, [])) <= set(phases):
            report.error("workflow_phases", where, f"{key} contiene fases desconocidas")
    if body.get("max_repair_attempts") != 1:
        report.error("repair_budget", where, "max_repair_attempts debe ser 1")
    if set(workflow.get("verdicts", {}).values()) != VERDICTS:
        report.error("verdict_contract", where, f"los veredictos deben ser exactamente {sorted(VERDICTS)}")
    for phase, agent in workflow.get("phase_agents", {}).items():
        if phase not in phases:
            report.error("workflow_agents", where, f"phase_agents usa la fase desconocida {phase}")
    keys: set[tuple[str, str]] = set()
    events = set()
    for transition in workflow.get("transitions", []):
        sources = transition.get("from")
        sources = sources if isinstance(sources, list) else [sources]
        event, target, actor = transition.get("event"), transition.get("to"), transition.get("actor")
        events.add(event)
        if target not in phases or not all(source in phases for source in sources):
            report.error("transition_phase", where, f"transicion invalida {sources}/{event}/{target}")
        if actor not in {"orchestrator", "human"}:
            report.error("transition_actor", where, f"{event}: actor debe ser orchestrator o human")
        for source in sources:
            if (source, event) in keys:
                report.error("transition_duplicate", where, f"{source}/{event} duplicada")
            keys.add((source, event))
            if source in body.get("terminal_phases", []):
                report.error("transition_terminal", where, f"{event} sale de la fase terminal {source}")
        for guard in transition.get("guards", []):
            if guard not in GUARDS:
                report.error("transition_guard", where, f"{event}: guard sin implementacion {guard!r}")
    missing = {"approved", "pass", "repairable_failure", "human_required", "cancel"} - events
    if missing:
        report.error("transition_missing", where, f"faltan eventos {sorted(missing)}")


def _check_agents(report: Report, paths: hl.Paths, workflow: dict) -> None:
    try:
        registry = hl.load_yaml(paths.registry) or {}
    except hl.YamlError as exc:
        report.error("registry", paths.registry, str(exc))
        return
    entries = registry.get("agents") if isinstance(registry, dict) else None
    if not isinstance(entries, list):
        report.error("registry", paths.registry, "falta la lista agents")
        return
    canonical = {agent: phase for phase, agent in workflow.get("phase_agents", {}).items()}
    registered = set()
    skills_dir = paths.bundle / "skills"
    for entry in entries:
        name = (entry or {}).get("name")
        if not name or name in registered:
            report.error("registry_name", paths.registry, f"nombre ausente o duplicado {name!r}")
            continue
        registered.add(name)
        agent_path = paths.root / str(entry.get("file", ""))
        if not agent_path.is_file() or agent_path.parent != paths.bundle / "agents":
            report.error("agent_missing", paths.registry, f"{name}: file debe apuntar a .claude/agents/<nombre>.md")
            continue
        try:
            meta = hl.frontmatter(agent_path)
        except hl.YamlError as exc:
            report.error("agent_frontmatter", agent_path, str(exc))
            continue
        if not meta:
            report.error("agent_frontmatter", agent_path, "frontmatter YAML ausente")
            continue
        if meta.get("name") != name or agent_path.stem != name:
            report.error("agent_name", agent_path, "name, nombre de archivo y registro deben coincidir")
        for key in ("description", "tools", "model"):
            if not meta.get(key):
                report.error("agent_contract", agent_path, f"falta {key}")
        model = str(meta.get("model", ""))
        if model and model not in MODELS and not model.startswith("claude-"):
            report.error("agent_model", agent_path, f"modelo desconocido {model!r}")
        if meta.get("effort") is not None and meta["effort"] not in EFFORTS:
            report.error("agent_effort", agent_path, f"effort invalido {meta['effort']!r}")
        if meta.get("color") is not None and meta["color"] not in COLORS:
            report.warn("agent_color", agent_path, f"color no soportado por Claude Code {meta['color']!r}")
        tools = meta.get("tools", "")
        tool_list = tools if isinstance(tools, list) else [t.strip() for t in str(tools).split(",")]
        for skill in meta.get("skills") or []:
            if not (skills_dir / str(skill) / "SKILL.md").is_file():
                report.error("agent_skill", agent_path, f"skill precargada inexistente {skill!r}")
        if name in canonical:
            if entry.get("role") != "canonical" or entry.get("phase") != canonical[name]:
                report.error("registry_phase", paths.registry, f"{name}: role canonical y phase {canonical[name]}")
            if not meta.get("effort"):
                report.error("agent_runtime", agent_path, "los agentes canonicos declaran model y effort")
            if {"Agent", "Task"} & set(tool_list):
                report.error("agent_depth", agent_path, "los subagentes canonicos no lanzan subagentes (max_depth = 1)")
            if meta.get("memory"):
                report.warn("agent_memory", agent_path, "memory introduce estado oculto; promueve lo aprendido a AGENTS.md")
        elif entry.get("role") != "specialist":
            report.error("registry_role", paths.registry, f"{name}: role debe ser canonical o specialist")
    for agent in canonical:
        if agent not in registered:
            report.error("registry_canonical", paths.registry, f"falta el agente canonico {agent}")
    for agent_file in sorted((paths.bundle / "agents").glob("*.md")):
        if agent_file.stem not in registered:
            report.warn("agent_unregistered", agent_file, "agente no registrado en agent-registry.yaml")


def _check_skills(report: Report, paths: hl.Paths) -> None:
    for skill in sorted((paths.bundle / "skills").glob("*/SKILL.md")):
        try:
            meta = hl.frontmatter(skill) or {}
        except hl.YamlError as exc:
            report.error("skill_frontmatter", skill, str(exc))
            continue
        name = meta.get("name")
        if name != skill.parent.name:
            report.error("skill_name", skill, "name debe coincidir con el nombre de la carpeta")
        description = str(meta.get("description") or "").strip()
        if not description:
            report.error("skill_frontmatter", skill, "falta description")
        elif len(description) > 1536:
            report.error("skill_description", skill, f"description de {len(description)} caracteres (maximo 1536)")
    for command in sorted((paths.bundle / "commands").glob("*.md")):
        try:
            meta = hl.frontmatter(command)
        except hl.YamlError as exc:
            report.error("command_frontmatter", command, str(exc))
            continue
        if not meta or not meta.get("description"):
            report.error("command_frontmatter", command, "falta description en el frontmatter")


def _hook_commands(settings: dict, event: str) -> list[str]:
    commands = []
    for group in (settings.get("hooks", {}) or {}).get(event, []) or []:
        for hook in (group or {}).get("hooks", []) or []:
            commands.append(str((hook or {}).get("command", "")))
    return commands


def _check_settings(report: Report, paths: hl.Paths) -> None:
    try:
        settings = hl.load_json(paths.settings)
    except (OSError, ValueError) as exc:
        report.error("settings_json", paths.settings, str(exc))
        return
    if not any("ledger.py" in c for c in _hook_commands(settings, "SubagentStop")):
        report.error("hook_ledger", paths.settings, "falta el hook SubagentStop -> ledger.py (runtimes y costes)")
    if not any("guard.py" in c for c in _hook_commands(settings, "PreToolUse")):
        report.error("hook_guard", paths.settings, "falta el hook PreToolUse -> guard.py (fronteras de seguridad)")


def _check_features(report: Report, paths: hl.Paths, only: str | None) -> list[str]:
    try:
        data = hl.load_json(paths.feature_list)
    except (OSError, ValueError) as exc:
        report.error("feature_list", paths.feature_list, str(exc))
        return []
    features = data.get("features") if isinstance(data, dict) else None
    if not isinstance(features, list):
        report.error("feature_list", paths.feature_list, "falta la lista features")
        return []
    ids: set[str] = set()
    for item in features:
        fid = (item or {}).get("id")
        if not isinstance(fid, str) or not hl.FEATURE_ID_RE.match(fid) or fid in ids:
            report.error("feature_id", paths.feature_list, f"ID ausente, invalido o duplicado {fid!r}")
            continue
        ids.add(fid)
        if not str(item.get("title") or "").strip():
            report.error("feature_title", paths.feature_list, f"{fid}: falta title")
        if item.get("status") not in FEATURE_STATUSES:
            report.error("feature_status", paths.feature_list, f"{fid}: status invalido {item.get('status')!r}")
        if not isinstance(item.get("tags", []), list):
            report.error("feature_tags", paths.feature_list, f"{fid}: tags debe ser una lista")
        budget = item.get("budget_usd")
        if budget is not None and (not isinstance(budget, (int, float)) or budget <= 0):
            report.error("feature_budget", paths.feature_list, f"{fid}: budget_usd debe ser > 0")
        has_state = (paths.feature(fid) / "state.yaml").is_file()
        if item.get("status") != "proposed" and not has_state:
            report.error("feature_state", paths.feature(fid), f"{fid} ({item.get('status')}) sin state.yaml")
    if paths.state.is_dir():
        for directory in sorted(p for p in paths.state.iterdir() if p.is_dir()):
            if directory.name not in ids:
                report.error("feature_orphan", directory, "directorio de estado sin entrada en feature_list.json")
    targets = [only] if only else sorted(fid for fid in ids if (paths.feature(fid) / "state.yaml").is_file())
    return targets


def validate(root: Path | None = None, feature: str | None = None, pre_gate: bool = False) -> Report:
    paths = hl.Paths(root)
    report = Report(paths.root)
    if pre_gate:
        if not feature:
            report.error("usage", paths.root, "--pre-gate requiere --feature")
        else:
            validate_feature(report, paths, feature, pre_gate=True)
        return report
    for relative in REQUIRED_FILES:
        if not (paths.root / relative).is_file():
            report.error("missing_file", paths.root / relative, "archivo obligatorio del harness ausente")
    if not report.ok:
        return report
    try:
        config = hl.load_config(paths)
        workflow = hl.load_workflow(paths)
    except hl.HarnessError as exc:
        report.error("config", paths.bundle, str(exc))
        return report
    _check_config(report, paths, config)
    _check_workflow(report, paths, workflow)
    _check_agents(report, paths, workflow)
    _check_skills(report, paths)
    _check_settings(report, paths)
    version = str(config.get("harness", {}).get("bundle_version", ""))
    match = re.search(r"^##\s+\[?(\d+\.\d+\.\d+)", _read(paths.bundle / "CHANGELOG.md"), re.MULTILINE)
    if not match or match.group(1) != version:
        report.error("version_drift", paths.bundle / "CHANGELOG.md", f"ultima version del changelog != bundle_version {version!r}")
    for name in ("state.yaml", "verification-result.yaml", "repair-request.yaml"):
        try:
            hl.load_yaml(paths.templates / name)
        except hl.YamlError as exc:
            report.error("template", paths.templates / name, str(exc))
    try:
        for problem in acceptance_problems(hl.load_yaml(paths.templates / "acceptance.yaml")):
            report.error("template_acceptance", paths.templates / "acceptance.yaml", problem)
    except hl.YamlError as exc:
        report.error("template", paths.templates / "acceptance.yaml", str(exc))
    if "HARNESS_VERIFY_PLACEHOLDER" in _read(paths.bundle / "bootstrap" / "verify.sh"):
        report.warn("verify_placeholder", paths.bundle / "bootstrap" / "verify.sh",
                    "verify.sh sin configurar: añade lint/tests del proyecto (skill project-bootstrap)")
    hook_errors = paths.state / "hook-errors.log"
    if hook_errors.is_file() and hook_errors.read_text(encoding="utf-8", errors="replace").strip():
        report.warn("hook_errors", hook_errors, "los hooks registraron errores: revisalos y vacia el archivo (el orquestador pedira confirmacion)")
    for fid in _check_features(report, paths, feature):
        validate_feature(report, paths, fid)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--feature")
    parser.add_argument("--pre-gate", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    report = validate(args.root, args.feature, args.pre_gate)
    if args.as_json:
        print(json.dumps({"ok": report.ok, "issues": [asdict(item) for item in report.issues]}, indent=2, ensure_ascii=False))
    else:
        for item in report.issues:
            print(f"{item.severity.upper()} {item.code} {item.path}: {item.message}")
        errors = sum(item.severity == "error" for item in report.issues)
        warnings = len(report.issues) - errors
        print(f"Harness validation {'passed' if report.ok else 'FAILED'} ({errors} errores, {warnings} avisos)")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
