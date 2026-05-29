---
description: Reporte de cobertura del vault vs curriculum oficial CKAD (CNCF + Linux Foundation Training). Cross-checks sub-puntos verbatim, calcula score ponderado por peso, recomienda próximos archivos a generar para máximo impacto.
allowed-tools: Read, Write, WebFetch, Bash, Glob, Grep, Agent
---

# /ckad-coverage — Coverage report vs curriculum oficial CKAD

## Pasos

1. Dispatch `ckad-coverage-analyst`.
2. El agente hace WebFetch del curriculum CKAD oficial (solo allowlist: cncf.io, training.linuxfoundation.org, kubernetes.io, github.com/cncf/curriculum).
3. Cross-check sub-puntos vs archivos vault.
4. Esperar reporte.
5. Mostrar al usuario:
   - Coverage global (file count + ponderado por peso de dominio).
   - Tabla por dominio (A 20 % / B 20 % / C 15 % / **D 25 %** / E 20 %).
   - Top-5 gaps críticos.
   - Próximos 10 archivos recomendados para máximo impacto.
   - Path del reporte completo (`00-Aggregations/coverage-report-<YYYYMMDD>.md`).

## Reglas

- Allowlist WebFetch obligatoria (cncf.io, training.linuxfoundation.org, kubernetes.io, github.com/cncf).
- Sin modificar archivos atómicos del vault.

$ARGUMENTS
