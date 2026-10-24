"""BM25 (Okapi) mínimo con tokenización para español e inglés."""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter

_STOPWORDS = set(
    """a al algo como con de del el en es esta este hay la las lo los mas me mi no o para pero por
    que se si sin su sus un una uno y ya the an and are as at be by for from has have how in is it
    of on or that the to was what when where which who why will with""".split()
)


def tokenize(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKD", text.lower())
    without_accents = "".join(c for c in normalized if not unicodedata.combining(c))
    return [t for t in re.findall(r"[a-z0-9]+", without_accents) if t not in _STOPWORDS and len(t) > 1]


class BM25:
    def __init__(self, corpus: list[list[str]], k1: float = 1.5, b: float = 0.75) -> None:
        self.k1, self.b = k1, b
        self.doc_freqs = [Counter(doc) for doc in corpus]
        self.doc_lens = [len(doc) for doc in corpus]
        self.avg_len = sum(self.doc_lens) / len(corpus) if corpus else 0.0
        df: Counter[str] = Counter()
        for doc in corpus:
            df.update(set(doc))
        n = len(corpus)
        self.idf = {term: math.log(1 + (n - freq + 0.5) / (freq + 0.5)) for term, freq in df.items()}

    def scores(self, query: list[str]) -> list[float]:
        result = []
        for freqs, length in zip(self.doc_freqs, self.doc_lens, strict=True):
            score = 0.0
            for term in query:
                tf = freqs.get(term, 0)
                if tf:
                    norm = tf + self.k1 * (1 - self.b + self.b * length / self.avg_len)
                    score += self.idf[term] * tf * (self.k1 + 1) / norm
            result.append(score)
        return result
