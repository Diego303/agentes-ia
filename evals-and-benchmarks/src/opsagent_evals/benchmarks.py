"""Benchmarks offline (sin modelo, deterministas, gratis): se ejecutan en cada CI.

    opsagent-bench                 # tabla con las métricas
    opsagent-bench --check         # código de salida 1 si alguna métrica baja del umbral
    opsagent-bench --json out.json

- Recuperación: recall@k y MRR de los runbooks relevantes (a nivel de documento). Con
  ``EMBEDDINGS_MODEL`` + ``LLM_GATEWAY_URL`` + ``LLM_GATEWAY_KEY`` compara BM25 con híbrido.
- Detección de prompt injection: precisión, recall y F1 del detector heurístico.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import yaml

from ops_mcp.integrations.tools.runbooks import RUNBOOKS_DIR
from opsagent_evals import DATASETS
from opsagent_guardrails import scan
from opsagent_rag import OpenAICompatibleEmbedder, Retriever, chunk_markdown, load_markdown_dir

# Umbrales: el valor medido en la línea base menos un margen. Subirlos es una decisión explícita.
THRESHOLDS = {
    "retrieval.bm25.recall@3": 0.85,
    "retrieval.bm25.mrr": 0.75,
    "injection.precision": 0.95,
    "injection.recall": 0.85,
}


def retrieval_metrics(retriever: Retriever, cases: list[dict], k: int = 3) -> dict[str, float]:
    recall_hits, reciprocal_ranks = 0, []
    for case in cases:
        ranked_docs: list[str] = []
        for hit in retriever.search(case["query"], k=20):
            if hit.chunk.doc_id not in ranked_docs:
                ranked_docs.append(hit.chunk.doc_id)
        relevant = set(case["relevant"])
        recall_hits += bool(relevant & set(ranked_docs[:k]))
        first = next((i for i, doc in enumerate(ranked_docs) if doc in relevant), None)
        reciprocal_ranks.append(1 / (first + 1) if first is not None else 0.0)
    return {f"recall@{k}": recall_hits / len(cases), "mrr": sum(reciprocal_ranks) / len(cases)}


def injection_metrics(corpus: dict[str, list[str]]) -> dict[str, float]:
    tp = sum(scan(t).suspicious for t in corpus["attacks"])
    fp = sum(scan(t).suspicious for t in corpus["benign"])
    fn = len(corpus["attacks"]) - tp
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1, "false_positives": float(fp)}


def run_all() -> dict[str, float]:
    chunks = [c for d in load_markdown_dir(RUNBOOKS_DIR) for c in chunk_markdown(d)]
    cases = yaml.safe_load((DATASETS / "retrieval.yaml").read_text(encoding="utf-8"))
    results: dict[str, float] = {}
    retrievers = {"bm25": Retriever(chunks)}
    if (model := os.getenv("EMBEDDINGS_MODEL")) and os.getenv("LLM_GATEWAY_URL"):
        embedder = OpenAICompatibleEmbedder(
            os.environ["LLM_GATEWAY_URL"], os.environ["LLM_GATEWAY_KEY"], model
        )
        retrievers["hybrid"] = Retriever(chunks, embedder=embedder)
    for name, retriever in retrievers.items():
        for metric, value in retrieval_metrics(retriever, cases).items():
            results[f"retrieval.{name}.{metric}"] = value
    corpus = yaml.safe_load((DATASETS / "injection.yaml").read_text(encoding="utf-8"))
    for metric, value in injection_metrics(corpus).items():
        results[f"injection.{metric}"] = value
    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", dest="json_path")
    args = parser.parse_args()

    results = run_all()
    failed = []
    print(f"{'métrica':34} {'valor':>7} {'umbral':>7}")
    for name, value in results.items():
        threshold = THRESHOLDS.get(name)
        status = "" if threshold is None else ("ok" if value >= threshold else "FALLA")
        if status == "FALLA":
            failed.append(name)
        print(f"{name:34} {value:7.3f} {threshold if threshold is not None else '':>7} {status}")
    if args.json_path:
        Path(args.json_path).write_text(json.dumps(results, indent=2))
    sys.exit(1 if args.check and failed else 0)


if __name__ == "__main__":
    main()
