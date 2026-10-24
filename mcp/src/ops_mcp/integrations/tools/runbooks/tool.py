"""Tool compleja: búsqueda en los runbooks (RAG).

La búsqueda es síncrona (BM25 en CPU y, en modo híbrido, una llamada HTTP síncrona para el
embedding de la consulta). Por eso va a un hilo con ``run_blocking``: si se ejecutara en el
bucle de eventos, mientras busca no atendería a ningún otro agente.
"""

from typing import Annotated

from mcp.server import MCPServer
from mcp.types import ToolAnnotations
from pydantic import Field

from ops_mcp.integrations.common import ToolDeps, logged_tool, run_blocking
from ops_mcp.integrations.tools.runbooks.models import RunbookHit

NAME = "search_runbooks"


def register(server: MCPServer, deps: ToolDeps) -> None:
    @server.tool(name=NAME, annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False))
    @logged_tool(NAME)
    async def search_runbooks(
        query: Annotated[str, Field(min_length=3, max_length=300)],
        k: Annotated[int, Field(ge=1, le=6)] = 3,
    ) -> list[RunbookHit]:
        """Busca en los runbooks de operaciones (síntomas, diagnóstico, mitigación, escalado y
        guía de severidad). Describe el síntoma con tus palabras, p. ej. "errores 503 tras un
        despliegue"."""
        hits = await run_blocking(deps.retriever.search, query, k)
        return [
            RunbookHit(
                runbook=h.chunk.doc_id,
                title=h.chunk.title,
                section=h.chunk.section,
                text=h.chunk.text,
                score=round(h.score, 4),
            )
            for h in hits
        ]
