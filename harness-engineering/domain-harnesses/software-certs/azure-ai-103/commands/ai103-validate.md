---
description: Valida la integridad del vault AI-103 (frontmatter, wikilinks, snippets Python, bidireccionalidad, orphans, staleness, INDICE consistency). Argumento opcional --scope all|domain|file. Genera reporte de salud en 00-Aggregations/.
allowed-tools: Read, Write, Bash, Glob, Grep, Agent
---

# /ai103-validate — Validar integridad del vault

Eres el orquestador. El usuario quiere health check del vault.

## Argumento

- **$ARGUMENTS** (opcional):
  - sin args → scope `all` (vault completo).
  - `--scope domain-X` → solo ese dominio.
  - `--scope file:<slug>` → un archivo.

## Pasos

1. Crear dir `00-Aggregations/` si no existe.
2. Dispatch `ai103-vault-validator` con scope.
3. Esperar reporte (path al markdown + score global).
4. Resumir al usuario:
   - Score global del vault (0-100).
   - Top-5 issues críticos.
   - Conteo por severidad (CRÍTICA/ALTA/MEDIA/BAJA).
   - Recomendación de acción.
5. Si hay issues CRÍTICOS → ofrece despachar `ai103-author` o tomar acción concreta.

## Reglas

- **No ejecutes snippets** del vault — solo el validator parsea sintaxis.
- **No modifiques archivos** automáticamente — solo reporta. Las correcciones requieren confirmación del usuario.
- **Sin WebFetch**: 100% local.

$ARGUMENTS
