---
description: Sugerencia inteligente del siguiente archivo a generar basado en prerequisitos (out-degree pending), impacto (in-degree desde archivos completados), peso en examen CKAD, y prioridad declarada. Orquestador-driven.
allowed-tools: Read, Bash, Glob, Grep
---

# /ckad-next-best — Siguiente archivo óptimo

## Pasos

1. Lee `INDICE-MAESTRO.md`. Identifica archivos ⬜ pendientes con sus pesos y prioridades.
2. Para cada pendiente, calcula score:
   - **Prerequisite unlock**: número de archivos completados que referencian este pendiente como wikilink. Más = más impacto.
   - **Domain weight**: peso del dominio (A=20, B=20, C=15, **D=25**, E=20).
   - **Declared priority**: 🔥🔥🔥=3, 🔥🔥=2, 🔥=1, none=0.
   - **Foundation factor**: si está en `00-Foundational/` → +2; si es el primero (.1) de un sub-dominio → +1.
   - **Difficulty penalty**: difficulty alta puede esperar; difficulty baja sube velocidad si en streak frio.
   - Score = (prerequisite_unlock × 2) + (domain_weight × declared_priority / 10) + foundation_factor.
3. Sort descending. Top 5.
4. Output al usuario:

```
🎯 Top 5 archivos recomendados a generar siguiente:

1. [[<slug>]] (Domain X, peso Y%, prioridad 🔥🔥🔥) — score 9.2
   - Referenciado por N archivos ya completados.
   - Foundational para sub-dominio Z.
   - Impacto estimado: alto.

2. [[<slug>]] (Domain X) — score 7.8
   - ...
```

5. Pregunta al usuario si quiere lanzar `/ckad-write <top-1>` directamente.

## Reglas

- Solo análisis local.
- No dispatcha autor automáticamente.

$ARGUMENTS
