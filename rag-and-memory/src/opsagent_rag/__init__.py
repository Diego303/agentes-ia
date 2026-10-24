"""RAG y memoria del sistema de referencia.

- Recuperación léxica BM25 (sin dependencias, determinista, sirve de línea base en los
  benchmarks) y, si hay un modelo de embeddings, híbrida con Reciprocal Rank Fusion.
- Memoria de sesión con TTL y límite de sesiones (``SessionStore``).
"""

from opsagent_rag.chunking import Chunk, Document, chunk_markdown, load_markdown_dir
from opsagent_rag.embeddings import Embedder, OpenAICompatibleEmbedder
from opsagent_rag.memory import InMemorySessionStore, SessionStore
from opsagent_rag.retriever import Hit, Retriever

__all__ = [
    "Chunk",
    "Document",
    "Embedder",
    "Hit",
    "InMemorySessionStore",
    "OpenAICompatibleEmbedder",
    "Retriever",
    "SessionStore",
    "chunk_markdown",
    "load_markdown_dir",
]
