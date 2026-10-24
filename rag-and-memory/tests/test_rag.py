import time

from opsagent_rag import Document, InMemorySessionStore, Retriever, chunk_markdown
from opsagent_rag.bm25 import tokenize

DOC = Document(
    id="high-error-rate",
    title="Tasa de errores 5xx elevada",
    text="# Tasa de errores 5xx elevada\n\n## Síntomas\n\nMás de un 2 % de respuestas 5xx.\n\n"
    "## Mitigación\n\nSi coincide con un despliegue reciente, haz rollback.",
)
OTHER = Document(
    id="kafka", title="Lag de Kafka", text="# Lag de Kafka\n\n## Síntomas\n\nEl consumer group acumula lag."
)


def test_chunks_follow_sections():
    chunks = chunk_markdown(DOC)
    assert [c.section for c in chunks] == ["Tasa de errores 5xx elevada", "Síntomas", "Mitigación"]
    assert all(c.doc_id == "high-error-rate" for c in chunks)


def test_tokenize_strips_accents_and_stopwords():
    assert tokenize("La Mitigación de los errores") == ["mitigacion", "errores"]


def test_bm25_ranks_relevant_section_first():
    retriever = Retriever(chunk_markdown(DOC) + chunk_markdown(OTHER))
    hits = retriever.search("rollback tras despliegue", k=2)
    assert hits[0].chunk.section == "Mitigación"
    assert retriever.mode == "bm25"


class FakeEmbedder:
    """Embeddings de juguete: un eje por palabra clave."""

    KEYS = ("rollback", "kafka", "errores")

    def embed(self, texts):
        return [[float(k in t.lower()) for k in self.KEYS] for t in texts]


def test_hybrid_mode_fuses_rankings():
    retriever = Retriever(chunk_markdown(DOC) + chunk_markdown(OTHER), embedder=FakeEmbedder())
    assert retriever.mode == "hybrid"
    assert retriever.search("kafka", k=1)[0].chunk.doc_id == "kafka"


def test_session_store_ttl_and_lru(monkeypatch):
    store = InMemorySessionStore(ttl_seconds=10, max_sessions=2)
    store.put("a", {"n": 1})
    store.put("b", {"n": 2})
    store.get("a")
    store.put("c", {"n": 3})  # expulsa "b", el menos usado
    assert store.get("b") is None and store.get("a") == {"n": 1}
    now = time.monotonic()
    monkeypatch.setattr(time, "monotonic", lambda: now + 11)
    assert store.get("a") is None
