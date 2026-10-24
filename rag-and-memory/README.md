# rag-and-memory

Recuperación sobre documentos y memoria de sesión del agente, con una línea base que se mide.

## Recuperación

```text
runbooks/*.md ──► chunk_markdown (por secciones ##) ──► BM25 ─────────────┐
                                                       └► embeddings ──► RRF ──► top-k
```

- **Troceado por estructura** ([`chunking.py`](src/opsagent_rag/chunking.py)): cada sección
  `##` de un runbook es un fragmento que mantiene juntos el síntoma y su acción. Cada
  fragmento lleva el título del documento y el de su sección.
- **BM25 propio** ([`bm25.py`](src/opsagent_rag/bm25.py)): sin dependencias, determinista,
  con tokenización para español (sin tildes y sin palabras vacías). Es la línea base que
  cualquier mejora tiene que superar en el benchmark.
- **Híbrido opcional** ([`retriever.py`](src/opsagent_rag/retriever.py)): si hay un modelo
  de embeddings (vía el gateway, endpoint compatible `/v1/embeddings`), fusiona ambos
  rankings con *Reciprocal Rank Fusion*, que no necesita calibrar puntuaciones entre métodos.

La usa el servidor MCP (`search_runbooks`). El agente no hace RAG por su cuenta: la
recuperación es una tool más, con su propio contrato y su propia traza.

| Métrica (16 consultas parafraseadas) | BM25 | Umbral del CI |
| --- | ---: | ---: |
| recall@3 (a nivel de documento) | 0,94 | 0,85 |
| MRR | 0,83 | 0,75 |

```bash
uv run opsagent-bench                                         # solo BM25
EMBEDDINGS_MODEL=embeddings LLM_GATEWAY_URL=... LLM_GATEWAY_KEY=... uv run opsagent-bench   # + híbrido
```

**Cuándo pasar a un vector store.** Con unos cientos de fragmentos, el índice en memoria
basta y se reconstruye al arrancar. Con miles de documentos, actualizaciones continuas o
filtros por permisos, usa PostgreSQL con pgvector, que ya tienes para otros datos, antes que
un vector store dedicado (ver [`architecture/adr/0005`](../architecture/adr/0005-rag-bm25-primero.md)).

## Memoria

[`memory.py`](src/opsagent_rag/memory.py) guarda el historial de cada sesión con TTL y
expulsión LRU, detrás del protocolo `SessionStore`.

- **Append-only.** No se editan turnos anteriores: los bloques de *thinking* de los modelos
  actuales dejan de ser válidos si cambia el historial que los produjo.
- **Conversaciones largas.** La compactación la hace la API (*compaction*, *context editing*),
  no el cliente reescribiendo mensajes.
- **Varias réplicas.** `InMemorySessionStore` es de un proceso. Para escalar el agente,
  implementa el mismo protocolo sobre Redis o PostgreSQL (ver [`architecture/adr/0006`](../architecture/adr/0006-estado-de-sesion.md)).
- **Sin memoria a largo plazo a propósito.** Recordar entre sesiones abre la puerta a
  envenenar el contexto (ASI06). Si se añade, que sea revisable y con procedencia.
