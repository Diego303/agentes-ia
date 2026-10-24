---
description: Genera diagrama Mermaid del grafo de wikilinks del vault (o sub-dominio). Útil para visualizar dependencias entre conceptos. Sin agente externo — orquestador-driven.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# /ckad-graph — Generar wikilink graph

## Argumento

- **$ARGUMENTS** (opcional): `--scope all|domain-X|sub-dominio`.

## Pasos

1. `Glob` para listar archivos del scope.
2. `grep -rohE "\[\[[a-zA-Z0-9_.-]+(\|[^]]+)?\]\]" --include="*.md"` y extraer pares (source, target).
3. Construir mermaid `graph LR` o `flowchart LR`:
   - Nodos: archivos `.md` atómicos.
   - Edges: cada wikilink.
   - Color/style por dominio (00, A, B, C, D, E).
4. Detectar y resaltar:
   - **Hubs** (>10 in-degree): nodos con muchos referenciantes.
   - **Orphans** (0 in-degree): nodos sin referencias entrantes.
   - **Sinks** (0 out-degree): nodos sin referencias salientes.
5. Escribir `00-Aggregations/wikilink-graph-<scope>.md` con el mermaid + leyenda + métricas.

## Output

```markdown
# 🕸️ Wikilink graph — <scope>

```mermaid
graph LR
  classDef foundational fill:#feca57
  classDef domainA fill:#48dbfb
  classDef domainB fill:#1dd1a1
  classDef domainC fill:#5f27cd
  classDef domainD fill:#ff6b6b
  classDef domainE fill:#ee5a6f
  classDef hub stroke:#000,stroke-width:4px

  A[00-kubectl-fundamentos]:::foundational --> B[A2-design-deployment]:::domainA
  ...
```

## Métricas
- Total nodos: N
- Total edges: N
- Hubs (>10 in-degree): [lista]
- Orphans (0 in-degree): [lista]
- Sinks (0 out-degree): [lista]

## Recomendaciones
- Connecting orphans: ...
- Hub overload: ...
```

## Reglas

- Si scope >40 archivos, el mermaid puede explotar — split en sub-graphs por sub-dominio.
- Solo análisis local, sin WebFetch.

$ARGUMENTS
