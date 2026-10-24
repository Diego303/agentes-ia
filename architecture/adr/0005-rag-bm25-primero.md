# 0005 · RAG con BM25 como línea base medida

**Estado**: aceptada

## Contexto

El corpus son unos pocos runbooks. Los embeddings y los vector stores añaden coste,
dependencias y otro proveedor.

## Decisión

Troceado por secciones Markdown, BM25 propio y benchmark de recuperación en CI (recall@3 y
MRR con umbral). Híbrido con embeddings vía el gateway y RRF, activable cuando mejore las
métricas. La recuperación se expone como tool MCP.

## Alternativas

- **Vector store dedicado desde el principio**. Sobredimensionado para cientos de fragmentos.
- **Solo embeddings**. Peor con términos exactos (códigos de error, nombres de servicio)
  frecuentes en operaciones.

## Consecuencias

- Toda mejora de RAG se justifica con el benchmark, no por intuición.
- Al crecer el corpus (miles de documentos, permisos por documento, actualizaciones
  continuas): PostgreSQL con pgvector.
