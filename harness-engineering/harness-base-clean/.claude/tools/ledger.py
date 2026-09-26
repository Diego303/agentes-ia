#!/usr/bin/env python3
"""Libro mayor por feature: ejecuciones reales de subagentes y coste estimado.

Uso:
  ledger.py hook                  Hook SubagentStop (lee el JSON del hook por stdin).
  ledger.py cost [FEATURE]        Informe de coste (todas las features si se omite).
      --json                      Salida JSON.
      --check                     Imprime BUDGET_OK|BUDGET_WARN|BUDGET_EXCEEDED; exit 2 si se excede.
      --snapshot                  Congela el calculo en .claude/state/<F>/cost.json.
      --live                      Recalcula aunque exista cost.json.
      --no-orchestrator           Excluye la estimacion del coste de la sesion principal.

El coste es una estimacion a precios de API (tabla [cost.pricing] de harness.toml)
calculada a partir del `usage` real de los transcripts de Claude Code. Con planes de
suscripcion no es lo facturado, pero sirve para comparar features y controlar gasto.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_lib as hl  # noqa: E402

HEADER_RE = re.compile(
    r"^[ \t]*[*_]*(FEATURE_ID|PHASE|ATTEMPT|MODE)[*_]*[ \t]*:[ \t]*[*_]*([A-Za-z0-9][A-Za-z0-9_.-]*)", re.MULTILINE)
ID_TOKEN = re.compile(r"(?<![A-Za-z0-9_-])([A-Z][A-Z0-9]*-[0-9]+)(?![A-Za-z0-9_-])")
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")
DATE_SUFFIX_RE = re.compile(r"-[0-9]{8}$")
TOKEN_FIELDS = ("input", "output", "cache_write_5m", "cache_write_1h", "cache_read")
HEADER_LINES = 12  # la cabecera del orquestador va al principio del prompt


# ---------------------------------------------------------------------------
# Lectura de transcripts
# ---------------------------------------------------------------------------


def _iter_jsonl(path: Path):
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict):
                yield item


def _text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block.get("text", "") for block in content if isinstance(block, dict) and block.get("type") == "text"
        )
    return ""


def _zero() -> dict:
    return {field: 0 for field in TOKEN_FIELDS}


def usage_counters(usage: dict) -> dict:
    """Normaliza `message.usage` a las cinco categorias con precio propio."""
    creation = usage.get("cache_creation") or {}
    written = int(usage.get("cache_creation_input_tokens") or 0)
    one_hour = int(creation.get("ephemeral_1h_input_tokens") or 0)
    return {
        "input": int(usage.get("input_tokens") or 0),
        "output": int(usage.get("output_tokens") or 0),
        "cache_write_5m": max(written - one_hour, 0),
        "cache_write_1h": one_hour,
        "cache_read": int(usage.get("cache_read_input_tokens") or 0),
    }


def model_key(model: str, speed: str | None) -> str:
    base = DATE_SUFFIX_RE.sub("", model or "unknown")
    return f"{base}|fast" if speed == "fast" else base


def _accumulate(target: dict, counters: dict) -> None:
    for field in TOKEN_FIELDS:
        target[field] += int(counters.get(field) or 0)


def _add(bucket: dict, key: str, counters: dict) -> None:
    _accumulate(bucket.setdefault(key, _zero()), counters)


class _MessageUsage:
    """Usage por mensaje unico.

    Claude Code escribe una linea por bloque de contenido con el mismo message.id;
    las lineas intermedias de un mensaje en streaming llevan output_tokens parcial y
    la ultima el valor final. Se conserva, por mensaje, el usage con mas output.
    """

    def __init__(self) -> None:
        self.by_id: dict[str, tuple[str, dict]] = {}

    def take(self, record: dict) -> None:
        message = record.get("message") or {}
        usage = message.get("usage")
        model = message.get("model") or "unknown"
        if not isinstance(usage, dict) or model == "<synthetic>":
            return
        key = str(message.get("id") or record.get("requestId") or record.get("uuid"))
        counters = usage_counters(usage)
        previous = self.by_id.get(key)
        if previous is None or counters["output"] >= previous[1]["output"]:
            self.by_id[key] = (model_key(model, usage.get("speed")), counters)

    def totals(self) -> dict:
        bucket: dict = {}
        for model, counters in self.by_id.values():
            _add(bucket, model, counters)
        return bucket


def parse_subagent_transcript(path: Path) -> dict:
    prompt, first_ts, last_ts = None, None, None
    messages = _MessageUsage()
    for record in _iter_jsonl(path):
        stamp = record.get("timestamp")
        if stamp:
            first_ts = first_ts or stamp
            last_ts = stamp
        kind = record.get("type")
        if kind == "user" and prompt is None:
            prompt = _text_of((record.get("message") or {}).get("content"))
        elif kind == "assistant":
            messages.take(record)
    header: dict = {}
    head = "\n".join((prompt or "").splitlines()[:HEADER_LINES])
    for name, value in HEADER_RE.findall(head):
        header.setdefault(name.lower(), value)
    return {"header": header, "header_seen": "FEATURE_ID" in head, "usage": messages.totals(),
            "started_at": first_ts, "finished_at": last_ts}


def locate_subagent_transcript(payload: dict) -> Path | None:
    agent_id = str(payload.get("agent_id") or "")
    session_id = str(payload.get("session_id") or "")
    transcript = payload.get("transcript_path")
    if not SAFE_ID_RE.match(agent_id):
        return None
    candidates = []
    if payload.get("agent_transcript_path"):
        candidates.append(Path(payload["agent_transcript_path"]))
    if transcript and SAFE_ID_RE.match(session_id):
        candidates.append(Path(transcript).parent / session_id / "subagents" / f"agent-{agent_id}.jsonl")
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    if transcript:
        for candidate in Path(transcript).parent.glob(f"*/subagents/agent-{agent_id}.jsonl"):
            return candidate
    return None


# ---------------------------------------------------------------------------
# Precios y presupuestos
# ---------------------------------------------------------------------------


def pricing(config: dict) -> tuple[dict, str]:
    table = config.get("cost", {}).get("pricing", {})
    return table.get("models", {}), str(table.get("as_of", "?"))


def price(key: str, counters: dict, models: dict) -> float | None:
    base, _, speed = key.partition("|")
    rates = models.get(base)
    if not rates:
        return None
    multiplier = 1.0
    if speed == "fast":
        multiplier = float(rates.get("fast_multiplier") or 0)
        if not multiplier:
            return None
    total = sum(counters.get(field, 0) * float(rates.get(field, 0)) for field in TOKEN_FIELDS)
    return total * multiplier / 1_000_000


def budget(config: dict, feature: dict | None) -> tuple[float, float]:
    cost = config.get("cost", {})
    limit = float((feature or {}).get("budget_usd") or cost.get("limit_usd") or 0)
    warn = float(cost.get("warn_usd") or 0)
    if limit and (not warn or warn > limit):
        warn = limit
    return warn, limit


def budget_status(total: float, warn: float, limit: float) -> str:
    if limit and total > limit:
        return "BUDGET_EXCEEDED"
    if warn and total > warn:
        return "BUDGET_WARN"
    return "BUDGET_OK"


# ---------------------------------------------------------------------------
# Atribucion del coste de la sesion principal (orquestador)
# ---------------------------------------------------------------------------


def default_transcripts_dir(root: Path) -> Path:
    config_dir = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
    return config_dir / "projects" / re.sub(r"[^A-Za-z0-9]", "-", str(root))


def orchestrator_usage(paths: hl.Paths, feature_id: str, events: list[dict], since: str | None) -> dict:
    """Suma el usage de los turnos de la sesion principal que referencian la feature.

    Heuristica: un turno (prompt humano + respuesta) cuenta si el prompt humano o
    alguna llamada a herramienta menciona el ID de la feature. Los subagentes
    (sidechains) se excluyen porque ya estan en el libro mayor.
    """
    directories = {Path(e["transcript"]).expanduser().parent for e in events if isinstance(e.get("transcript"), str)}
    directories.add(default_transcripts_dir(paths.root))
    started = hl.parse_iso(since)
    known = {str(item.get("id")) for item in hl.load_features(paths)}
    total: dict = {}
    for directory in sorted(directories):
        if not directory.is_dir():
            continue
        for transcript in sorted(directory.glob("*.jsonl")):
            if started and transcript.stat().st_mtime < started.timestamp():
                continue
            _scan_main_transcript(transcript, feature_id, known, total)
    return {key: {field: int(round(value)) for field, value in counters.items()} for key, counters in total.items()}


def _scan_main_transcript(path: Path, feature_id: str, known: set[str], total: dict) -> None:
    """Imputa a la feature su parte de cada turno que la menciona (repartido entre las features citadas)."""
    turn = _MessageUsage()
    mentioned: set[str] = set()

    def mentions(text: str) -> set[str]:
        return {match for match in ID_TOKEN.findall(text) if match in known}

    def flush() -> None:
        if feature_id in mentioned:
            share = 1 / len(mentioned)
            for key, counters in turn.totals().items():
                slot = total.setdefault(key, _zero())
                for field in TOKEN_FIELDS:
                    slot[field] += counters[field] * share

    for record in _iter_jsonl(path):
        if record.get("isSidechain"):
            continue
        kind = record.get("type")
        if kind == "user":
            content = (record.get("message") or {}).get("content")
            tool_result = isinstance(content, list) and any(
                isinstance(block, dict) and block.get("type") == "tool_result" for block in content
            )
            if tool_result or record.get("isMeta"):
                continue
            flush()
            turn, mentioned = _MessageUsage(), mentions(_text_of(content))
        elif kind == "assistant":
            turn.take(record)
            for block in (record.get("message") or {}).get("content") or []:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    mentioned |= mentions(json.dumps(block.get("input"), ensure_ascii=False))
    flush()


# ---------------------------------------------------------------------------
# Coste por feature
# ---------------------------------------------------------------------------


def _priced(usage_by_model: dict, models: dict) -> tuple[float, list[str]]:
    total, unpriced = 0.0, []
    for key, counters in usage_by_model.items():
        value = price(key, counters, models)
        if value is None:
            if any(counters.values()):
                unpriced.append(key)
        else:
            total += value
    return total, unpriced


def feature_cost(paths: hl.Paths, feature_id: str, config: dict | None = None,
                 include_orchestrator: bool = True, live: bool = False) -> dict:
    snapshot = paths.feature(feature_id) / "cost.json"
    if snapshot.is_file() and not live:
        data = hl.load_json(snapshot)
        data["source"] = "snapshot"
        return data
    config = config if config is not None else hl.load_config(paths)
    models, as_of = pricing(config)
    events = hl.read_events(paths, feature_id)
    runs: dict[str, dict] = {}
    for event in events:
        if event.get("event") == "subagent_stop" and event.get("agent_id"):
            runs[event["agent_id"]] = event  # el ultimo evento de un agent_id es acumulado
    by_agent: dict = {}
    by_model: dict = {}
    unpriced: set[str] = set()
    for run in runs.values():
        agent = str(run.get("agent") or "unknown")
        slot = by_agent.setdefault(agent, {"runs": 0, "cost_usd": 0.0, "tokens": _zero()})
        slot["runs"] += 1
        usage = run.get("usage") or {}
        cost, missing = _priced(usage, models)
        slot["cost_usd"] += cost
        unpriced.update(missing)
        for key, counters in usage.items():
            _add(by_model, key, counters)
            _accumulate(slot["tokens"], counters)
    orchestrator = None
    if include_orchestrator:
        state_path = paths.feature(feature_id) / "state.yaml"
        created = None
        if state_path.is_file():
            state = hl.load_yaml(state_path) or {}
            created = state.get("created_at")
        usage = orchestrator_usage(paths, feature_id, events, created)
        cost, missing = _priced(usage, models)
        unpriced.update(missing)
        tokens = _zero()
        for key, counters in usage.items():
            _add(by_model, key, counters)
            _accumulate(tokens, counters)
        orchestrator = {"cost_usd": cost, "tokens": tokens, "method": "heuristic-turns"}
    total = sum(slot["cost_usd"] for slot in by_agent.values()) + (orchestrator or {}).get("cost_usd", 0.0)
    feature = hl.find_feature(paths, feature_id)
    warn, limit = budget(config, feature)
    return {
        "feature_id": feature_id,
        "computed_at": hl.now_iso(),
        "pricing_as_of": as_of,
        "total_usd": round(total, 4),
        "by_agent": {k: {**v, "cost_usd": round(v["cost_usd"], 4)} for k, v in sorted(by_agent.items())},
        "orchestrator": orchestrator and {**orchestrator, "cost_usd": round(orchestrator["cost_usd"], 4)},
        "by_model_tokens": by_model,
        "unpriced_models": sorted(unpriced),
        "budget": {"warn_usd": warn, "limit_usd": limit, "status": budget_status(total, warn, limit)},
        "source": "live",
    }


def write_snapshot(paths: hl.Paths, feature_id: str, config: dict | None = None) -> dict:
    data = feature_cost(paths, feature_id, config, live=True)
    data["source"] = "snapshot"
    hl.dump_json(paths.feature(feature_id) / "cost.json", data)
    return data


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _log_hook_error(paths: hl.Paths, message: str) -> None:
    try:
        paths.state.mkdir(parents=True, exist_ok=True)
        with (paths.state / "hook-errors.log").open("a", encoding="utf-8") as handle:
            handle.write(f"{hl.now_iso()} ledger {message}\n")
    except OSError:
        pass


def _harness_agents(paths: hl.Paths) -> set[str]:
    try:
        registry = hl.load_yaml(paths.registry) or {}
    except (hl.HarnessError, OSError):
        return set()
    return {str(item.get("name")) for item in registry.get("agents") or [] if isinstance(item, dict)}


def cmd_hook(paths: hl.Paths, raw: str) -> int:
    """Registra una ejecucion de subagente del harness. Nunca bloquea la sesion."""
    try:
        payload = json.loads(raw or "{}")
        if payload.get("hook_event_name") != "SubagentStop":
            return 0
        transcript = locate_subagent_transcript(payload)
        if transcript is None:
            # Claude Code ejecuta subagentes internos sin transcript: solo importa si es del harness.
            if str(payload.get("agent_type")) in _harness_agents(paths):
                _log_hook_error(paths, f"sin transcript para {payload.get('agent_type')} {payload.get('agent_id')!r}: "
                                       "su runtime y su coste no quedan registrados")
            return 0
        run = parse_subagent_transcript(transcript)
        feature_id = run["header"].get("feature_id")
        if not feature_id or not hl.FEATURE_ID_RE.match(feature_id):
            if run["header_seen"] and str(payload.get("agent_type")) in _harness_agents(paths):
                _log_hook_error(paths, f"cabecera FEATURE_ID ilegible en {payload.get('agent_type')} "
                                       f"{payload.get('agent_id')!r}: usa 'FEATURE_ID: <ID>' en la primera linea")
            return 0  # subagente ajeno al flujo del harness
        if not (paths.feature(feature_id) / "state.yaml").is_file():
            _log_hook_error(paths, f"FEATURE_ID {feature_id} sin state.yaml; ejecucion no registrada")
            return 0
        try:
            models, as_of = pricing(hl.load_config(paths))
        except hl.HarnessError:
            models, as_of = {}, "?"
        cost, unpriced = _priced(run["usage"], models)
        hl.append_event(paths, feature_id, {
            "event": "subagent_stop",
            "agent": str(payload.get("agent_type") or "unknown")[:64],
            "agent_id": payload.get("agent_id"),
            "phase": run["header"].get("phase"),
            "attempt": run["header"].get("attempt"),
            "session_id": payload.get("session_id"),
            "transcript": hl.portable_path(payload.get("transcript_path")),
            "started_at": run["started_at"],
            "finished_at": run["finished_at"],
            "usage": run["usage"],
            "cost_usd": round(cost, 6),
            "unpriced_models": unpriced,
            "pricing_as_of": as_of,
        })
    except Exception as exc:  # noqa: BLE001 - un hook nunca debe romper la sesion
        _log_hook_error(paths, f"error inesperado: {exc!r}")
    return 0


def _k(value: int) -> str:
    return f"{value / 1000:.1f}k" if value >= 1000 else str(value)


def _render(report: dict) -> str:
    lines = [
        f"Feature {report['feature_id']} - coste estimado a precios API (USD, tarifas a {report['pricing_as_of']}, fuente {report.get('source')})",
        f"  {'agente':<14}{'ejec':>5}{'input':>9}{'cache_w':>9}{'cache_r':>9}{'output':>9}{'coste':>11}",
    ]
    for agent, slot in report["by_agent"].items():
        tok = slot["tokens"]
        lines.append(
            f"  {agent:<14}{slot['runs']:>5}{_k(tok['input']):>9}{_k(tok['cache_write_5m'] + tok['cache_write_1h']):>9}"
            f"{_k(tok['cache_read']):>9}{_k(tok['output']):>9}{'$' + format(slot['cost_usd'], '.4f'):>11}"
        )
    orch = report.get("orchestrator")
    if orch:
        tok = orch["tokens"]
        lines.append(
            f"  {'orquestador*':<14}{'-':>5}{_k(tok['input']):>9}{_k(tok['cache_write_5m'] + tok['cache_write_1h']):>9}"
            f"{_k(tok['cache_read']):>9}{_k(tok['output']):>9}{'$' + format(orch['cost_usd'], '.4f'):>11}"
        )
    budget_info = report["budget"]
    lines.append(f"  {'TOTAL':<55}{'$' + format(report['total_usd'], '.4f'):>11}")
    lines.append(
        f"  Presupuesto: aviso ${budget_info['warn_usd']:.2f} / limite ${budget_info['limit_usd']:.2f} -> {budget_info['status']}"
    )
    if orch:
        lines.append("  * orquestador: turnos de la sesion principal que mencionan la feature (estimacion heuristica)")
    if report.get("unpriced_models"):
        lines.append(f"  AVISO modelos sin precio (coste 0): {', '.join(report['unpriced_models'])} -> anadelos en harness.toml")
    return "\n".join(lines)


def cmd_cost(paths: hl.Paths, args: argparse.Namespace) -> int:
    config = hl.load_config(paths)
    if not config.get("cost", {}).get("enabled", True):
        print("Seguimiento de costes desactivado ([cost].enabled = false)")
        return 0
    if args.feature:
        if not hl.FEATURE_ID_RE.match(args.feature) or not paths.feature(args.feature).is_dir():
            print(f"Feature desconocida o sin estado: {args.feature}", file=sys.stderr)
            return 1
        if args.snapshot:
            report = write_snapshot(paths, args.feature, config)
        else:
            report = feature_cost(paths, args.feature, config, not args.no_orchestrator, args.live)
        if args.check:
            b = report["budget"]
            print(f"{b['status']} total=${report['total_usd']:.4f} warn=${b['warn_usd']:.2f} limit=${b['limit_usd']:.2f}")
            return 2 if b["status"] == "BUDGET_EXCEEDED" else 0
        print(json.dumps(report, indent=2, ensure_ascii=False) if args.json else _render(report))
        return 0
    rows = []
    for feature in hl.load_features(paths):
        fid = feature.get("id")
        if fid and paths.feature(fid).is_dir():
            report = feature_cost(paths, fid, config, not args.no_orchestrator, args.live)
            rows.append({"feature_id": fid, "status": feature.get("status"), "total_usd": report["total_usd"],
                         "budget": report["budget"]["status"]})
    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
    else:
        print(f"{'feature':<16}{'estado':<13}{'coste':>11}  presupuesto")
        for row in rows:
            print(f"{row['feature_id']:<16}{str(row['status']):<13}{'$' + format(row['total_usd'], '.4f'):>11}  {row['budget']}")
        print(f"{'TOTAL':<29}{'$' + format(sum(r['total_usd'] for r in rows), '.4f'):>11}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=None)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("hook")
    cost = sub.add_parser("cost")
    cost.add_argument("feature", nargs="?")
    cost.add_argument("--json", action="store_true")
    cost.add_argument("--check", action="store_true")
    cost.add_argument("--snapshot", action="store_true")
    cost.add_argument("--live", action="store_true")
    cost.add_argument("--no-orchestrator", action="store_true")
    args = parser.parse_args(argv)
    paths = hl.Paths(args.root)
    if args.command == "hook":
        return cmd_hook(paths, sys.stdin.read())
    try:
        return cmd_cost(paths, args)
    except hl.HarnessError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
