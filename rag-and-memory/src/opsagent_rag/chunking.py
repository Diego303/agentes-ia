"""Carga de documentos Markdown y troceado por secciones."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    text: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Chunk:
    id: str
    doc_id: str
    title: str
    section: str
    text: str


def load_markdown_dir(path: Path) -> list[Document]:
    """Un documento por ``.md``; el id es el nombre del archivo y el título, su primer ``#``."""
    docs = []
    for file in sorted(path.glob("*.md")):
        text = file.read_text(encoding="utf-8")
        match = re.search(r"^#\s+(.+)$", text, re.M)
        docs.append(Document(id=file.stem, title=match.group(1).strip() if match else file.stem, text=text))
    return docs


def chunk_markdown(doc: Document, max_chars: int = 1200) -> list[Chunk]:
    """Trocea por secciones ``##``; una sección larga se divide por párrafos.

    Trocear por la estructura del documento mantiene juntos el síntoma y su acción, que es
    lo que hace útil un runbook recuperado. Cada trozo lleva el título del documento y el de
    la sección para que BM25 y el modelo tengan contexto.
    """
    sections = re.split(r"^(?=##\s)", doc.text, flags=re.M)
    chunks: list[Chunk] = []
    for raw in sections:
        raw = raw.strip()
        if not raw:
            continue
        heading = re.match(r"^#{1,6}\s+(.+)$", raw, re.M)
        section = heading.group(1).strip() if heading else doc.title
        buffer = ""
        for paragraph in re.split(r"\n\s*\n", raw):
            if buffer and len(buffer) + len(paragraph) > max_chars:
                chunks.append(_make(doc, section, buffer, len(chunks)))
                buffer = ""
            buffer = f"{buffer}\n\n{paragraph}".strip()
        if buffer:
            chunks.append(_make(doc, section, buffer, len(chunks)))
    return chunks


def _make(doc: Document, section: str, text: str, index: int) -> Chunk:
    return Chunk(id=f"{doc.id}#{index}", doc_id=doc.id, title=doc.title, section=section, text=text)
