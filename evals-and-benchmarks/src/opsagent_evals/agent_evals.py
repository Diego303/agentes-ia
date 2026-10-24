"""Evals de punta a punta con el modelo real (cuesta dinero: cada caso es una conversación).

    opsagent-evals                       # graders deterministas
    opsagent-evals --judge               # + juez LLM en los casos con rúbrica
    opsagent-evals --repeat 3            # fiabilidad: pass^k por caso
    opsagent-evals --calibrate           # acuerdo del juez con las etiquetas humanas
    opsagent-evals --min-pass 0.85       # código de salida 1 si la tasa de acierto es menor

Usa la misma configuración que el agente (``LLM_GATEWAY_URL``/``ANTHROPIC_API_KEY``,
``MCP_URL``, ``ADVISOR_URL``); sin URLs, MCP va por stdio y el advisor en proceso.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import yaml

from opsagent.config import Settings
from opsagent.llm import make_llm_client
from opsagent.runtime import build_runtime
from opsagent_evals import DATASETS
from opsagent_evals.graders import grade
from opsagent_evals.judge import agreement, judge

JUDGE_MODEL = os.getenv("OPSAGENT_JUDGE_MODEL", "claude-opus-5-5")


async def run_case(runtime, case: dict[str, Any]) -> dict[str, Any]:
    start = time.perf_counter()
    first = None
    result = (await runtime.agent.chat(case["input"])).to_dict()
    if result["stop"] == "approval_required" and "approve" in case:
        first = result
        result = (await runtime.agent.resolve_approval(result["session_id"], bool(case["approve"]))).to_dict()
    failures = grade(case.get("expect", {}), result, first)
    cost = result["cost_usd"] + (first["cost_usd"] if first else 0.0)
    return {
        "reply": result["reply"],
        "failures": failures,
        "cost_usd": cost,
        "seconds": time.perf_counter() - start,
    }


async def run(args: argparse.Namespace, cases: list[dict[str, Any]]) -> tuple[int, dict[str, Any]]:
    if args.case:
        cases = [c for c in cases if c["id"] in args.case]
    settings = Settings.from_env()
    runtime = build_runtime(settings)
    judge_client = make_llm_client(settings) if args.judge else None
    report: list[dict[str, Any]] = []
    try:
        for case in cases:
            runs = []
            for _ in range(args.repeat):
                outcome = await run_case(runtime, case)
                if judge_client and case.get("rubric") and not outcome["failures"]:
                    verdict = await judge(
                        judge_client, JUDGE_MODEL, case["rubric"], case["input"], outcome["reply"]
                    )
                    outcome["judge"] = verdict.model_dump()
                    if not verdict.passed:
                        outcome["failures"].append(f"juez: {verdict.reasoning}")
                runs.append(outcome)
            passed = sum(not r["failures"] for r in runs)
            report.append({"id": case["id"], "passed": passed, "runs": len(runs), "details": runs})
            mark = "PASS" if passed == len(runs) else "FAIL"
            print(
                f"[{mark}] {case['id']}: {passed}/{len(runs)}",
                *{f for r in runs for f in r["failures"]},
                sep="\n    ",
            )
    finally:
        await runtime.aclose()

    total_runs = sum(r["runs"] for r in report)
    pass_rate = sum(r["passed"] for r in report) / total_runs if total_runs else 0.0
    pass_all = sum(r["passed"] == r["runs"] for r in report) / len(report) if report else 0.0
    cost = sum(d["cost_usd"] for r in report for d in r["details"])
    summary = {
        "pass_rate": round(pass_rate, 3),
        f"pass^{args.repeat}": round(pass_all, 3),
        "cost_usd": round(cost, 4),
        "cases": len(report),
    }
    print(json.dumps(summary, ensure_ascii=False))
    return (0 if pass_rate >= args.min_pass else 1), {"summary": summary, "cases": report}


async def calibrate(args: argparse.Namespace, items: list[dict[str, Any]]) -> int:
    client = make_llm_client(Settings.from_env())
    labels = []
    for item in items:
        verdict = await judge(client, JUDGE_MODEL, item["rubric"], "(calibración)", item["answer"])
        labels.append(verdict.passed)
        if verdict.passed != item["human_pass"]:
            print(
                f"desacuerdo (humano={item['human_pass']}): {item['answer'][:90]}…\n    {verdict.reasoning}"
            )
    metrics = agreement([i["human_pass"] for i in items], labels)
    print(json.dumps({"judge_model": JUDGE_MODEL, **metrics}))
    return 0 if metrics["kappa"] >= args.min_kappa else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--dataset", default=str(DATASETS / "agent_tasks.yaml"))
    parser.add_argument("--case", action="append", help="ejecuta solo este id (repetible)")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--judge", action="store_true")
    parser.add_argument("--calibrate", action="store_true")
    parser.add_argument("--min-pass", type=float, default=0.8)
    parser.add_argument("--min-kappa", type=float, default=0.6)
    parser.add_argument("--output", help="ruta del informe JSON")
    args = parser.parse_args()
    if args.calibrate:
        items = yaml.safe_load((DATASETS / "judge_calibration.yaml").read_text(encoding="utf-8"))
        sys.exit(asyncio.run(calibrate(args, items)))
    cases = yaml.safe_load(Path(args.dataset).read_text(encoding="utf-8"))
    code, report = asyncio.run(run(args, cases))
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    sys.exit(code)


if __name__ == "__main__":
    main()
