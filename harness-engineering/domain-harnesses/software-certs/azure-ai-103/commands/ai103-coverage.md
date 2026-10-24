---
description: Reporte de cobertura del vault vs temario oficial Microsoft AI-103 Skills Measured. Cross-checks sub-puntos verbatim, calcula score ponderado por peso, recomienda próximos archivos a generar para máximo impacto.
allowed-tools: Read, Write, WebFetch, Bash, Glob, Grep, Agent
---

# /ai103-coverage — Coverage report vs temario oficial

## Pasos

1. Dispatch `ai103-coverage-analyst`.
2. El agente hace WebFetch del Skills Measured AI-103 (solo allowlist learn.microsoft.com).
3. Cross-check sub-puntos vs archivos vault.
4. Esperar reporte.
5. Mostrar al usuario:
   - Coverage global (file count + ponderado).
   - Tabla por dominio.
   - Top-5 gaps críticos.
   - Próximos 10 archivos recomendados.
   - Path del reporte completo.

## Reglas

- Allowlist WebFetch obligatoria (learn.microsoft.com, docs.microsoft.com).
- Sin modificar archivos.

$ARGUMENTS
