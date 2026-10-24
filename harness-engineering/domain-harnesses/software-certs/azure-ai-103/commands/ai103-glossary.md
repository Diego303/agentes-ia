---
description: Extrae términos técnicos con definiciones across todos los archivos del vault. Genera glossary consolidado A-Z. Útil para revisión final y verificar uso consistente de nomenclatura.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# /ai103-glossary — Glossary del vault

## Pasos

1. `Glob` para listar archivos atómicos.
2. Para cada uno, extrae:
   - **Bolds** (`**término**`) que aparezcan en TL;DR o en sección "Concepto en profundidad" como introducción de concepto.
   - **Resource types** verbatim (`Microsoft.X/Y`).
   - **Acrónimos** (e.g., RAG, RBAC, MI, FIC, PTU, TPM, RPM, RRF, BSP) — busca patrones MAYÚSCULAS.
   - **Componentes named** (e.g., "AIProjectClient", "Foundry Agent Service", "Microsoft Agent Framework").
3. Por cada término extraído:
   - Si aparece en N archivos, anota frequency.
   - Toma la definición del primer párrafo donde aparece (heurística: oración con verbo "es/son/contains/refers to").
4. Consolida A-Z:
   - Deduplica.
   - Group por categoría (Servicios / Roles / Resources / SDKs / Conceptos / Acrónimos).
5. Output `00-Aggregations/glossary-ai103.md`:

```markdown
# 📘 Glossary AI-103

## A
- **AIProjectClient** — Cliente Python principal de `azure-ai-projects` v2+ para acceder a Foundry projects. → ver [[genai-foundry-sdk-integration]]
- **A2A** (Agent-to-Agent) — Tool preview en Foundry Agent Service que permite que un agent invoque a otro. → ver [[agents-multi-agent-orchestration]]
- ...

## B
- ...

## Acrónimos
- **PTU** — Provisioned Throughput Units. Capacidad horaria reservada.
- **RAG** — Retrieval-Augmented Generation.
- ...
```

## Reglas

- Solo análisis local.
- Atribuye cada término al archivo donde se define mejor (primer aparición con definición clara).
- No inventar definiciones; usar lo que dicen los archivos.

$ARGUMENTS
