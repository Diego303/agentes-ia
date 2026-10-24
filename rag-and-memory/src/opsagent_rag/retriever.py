"""Recuperador léxico o híbrido (BM25 + embeddings, fusionados con Reciprocal Rank Fusion)."""

from __future__ import annotations

import math
from dataclasses import dataclass

from opsagent_rag.bm25 import BM25, tokenize
from opsagent_rag.chunking import Chunk
from opsagent_rag.embeddings import Embedder

RRF_K = 60  # constante habitual de RRF: suaviza el peso de las primeras posiciones


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float


class Retriever:
    def __init__(self, chunks: list[Chunk], embedder: Embedder | None = None) -> None:
        self.chunks = chunks
        self._bm25 = BM25([tokenize(f"{c.title} {c.section} {c.text}") for c in chunks])
        self._embedder = embedder
        self._vectors = embedder.embed([c.text for c in chunks]) if embedder and chunks else None

    @property
    def mode(self) -> str:
        return "hybrid" if self._vectors is not None else "bm25"

    def search(self, query: str, k: int = 4) -> list[Hit]:
        lexical = self._bm25.scores(tokenize(query))
        if self._vectors is None or self._embedder is None:
            ranked = sorted(range(len(self.chunks)), key=lambda i: lexical[i], reverse=True)
            return [Hit(self.chunks[i], lexical[i]) for i in ranked[:k] if lexical[i] > 0]

        query_vector = self._embedder.embed([query])[0]
        dense = [_cosine(query_vector, v) for v in self._vectors]
        fused: dict[int, float] = {}
        for scores in (lexical, dense):
            order = sorted(range(len(self.chunks)), key=lambda i: scores[i], reverse=True)
            for rank, i in enumerate(order):
                fused[i] = fused.get(i, 0.0) + 1.0 / (RRF_K + rank + 1)
        ranked = sorted(fused, key=fused.__getitem__, reverse=True)
        return [Hit(self.chunks[i], fused[i]) for i in ranked[:k]]


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm if norm else 0.0
