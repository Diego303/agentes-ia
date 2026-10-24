"""Índice de los runbooks: trocea los Markdown por secciones y construye el recuperador."""

from __future__ import annotations

from pathlib import Path

from ops_mcp.integrations.common import RESOURCES_DIR, get_logger
from opsagent_rag import Retriever, chunk_markdown, load_markdown_dir

RUNBOOKS_DIR = RESOURCES_DIR / "runbooks"
log = get_logger(__name__)


def build_retriever(runbooks_dir: Path = RUNBOOKS_DIR) -> Retriever:
    """BM25 por defecto; híbrido si ``EMBEDDINGS_MODEL`` está configurado (ver opsagent-rag)."""
    docs = load_markdown_dir(runbooks_dir)
    chunks = [chunk for doc in docs for chunk in chunk_markdown(doc)]
    log.info("runbooks.indexed", extra={"documents": len(docs), "chunks": len(chunks)})
    return Retriever(chunks)
