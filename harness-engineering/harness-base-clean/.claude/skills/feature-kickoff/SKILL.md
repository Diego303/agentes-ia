---
name: feature-kickoff
description: Convierte una idea, ticket o petición todavía ambigua en una feature registrada y lista para el flujo del harness - resumen, alcance, tags, riesgos y preguntas clave. Úsala cuando el humano traiga algo nuevo que construir ("quiero añadir...", "tengo esta idea", "prepara el ticket X") y todavía no exista en feature_list.json. No diseña ni implementa.
---

# Feature kickoff

> Generaliza `backend-feature-kickoff` de la referencia: el core del harness no
> asume un stack concreto.

## Resultado

Una entrada nueva en `.claude/feature_list.json` (`status: proposed`) y un
resumen breve para arrancar el flujo.

## Procedimiento

1. Lee la petición, `AGENTS.md` y `feature_list.json`. Si la feature ya
   existe, trabaja con esa entrada en lugar de duplicarla.
2. Resume en lenguaje claro: problema, alcance propuesto (dentro y fuera),
   riesgos técnicos y preguntas abiertas.
3. Pregunta solo lo que bloquea alcance, aceptación o seguridad, con un máximo
   de tres preguntas concretas. Lo demás queda como supuesto explícito para el designer.
4. Propón ID (`MAYÚSCULAS-NNN`), título, tags y, si la feature es grande,
   presupuesto. Los tags sensibles (`security-critical`, `auth`, `crypto`,
   `payments`, `pii`, `compliance`, `data-migration`, `destructive`...) obligan
   a aprobación humana de GATE#1 incluso en modo yolo: no los omitas.
5. Con el visto bueno del humano, regístrala:
   `python3 .claude/tools/feature.py add <ID> "<título>" --tags a,b [--budget USD] [--notes "<contexto>"]`
6. Ofrece arrancar el flujo con la skill `sdd-feature-planning`.

## Límites

- No diseñes la solución ni escribas código.
- No conviertas suposiciones en requisitos: márcalas como supuestos.
- No arranques el flujo sin confirmación del humano.
