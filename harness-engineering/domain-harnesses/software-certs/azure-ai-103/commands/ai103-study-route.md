---
description: Ruta de estudio personalizada por dominio. Order de archivos respetando prerequisitos (wikilinks foundational antes), agrupados por sesión de 60-90 min. Para preparar plan de revisión las semanas previas al examen.
allowed-tools: Read, Bash, Glob, Grep, AskUserQuestion
---

# /ai103-study-route — Ruta de estudio personalizada

## Pasos

1. Pregunta al usuario con `AskUserQuestion`:
   - **Tiempo total disponible** (horas): e.g., 20h, 40h, 80h.
   - **Tiempo por sesión** (min): e.g., 60, 90, 120.
   - **Dominios a priorizar**: e.g., todos / solo pesados / focus en B.
   - **Nivel actual**: principiante (todo desde 0) / intermedio (revisar) / experto (solo trampas).

2. Calcula plan:
   - Archivos por sesión = (tiempo_sesion_min / 15) × factor_dificultad.
   - Order:
     - 00-Foundational primero.
     - Domain A (descomposición A.1 → A.2 → A.3 → A.4).
     - Domain B (B.1 → B.2 → B.3, intercalado con E.1 ya que RAG/Search son cross).
     - Domain E.
     - Domain C, D.
     - Carryover AI-102 al final.
   - Respeta prerequisitos: wikilinks foundational antes de los que los usan.

3. Output al usuario:

```
📅 Plan de estudio AI-103 (X sesiones × Y min)

## Semana 1 — Foundational + Domain A
- **Sesión 1** (60 min): Foundational (00-*)
- **Sesión 2** (60 min): A.1 (foundry-service-selection + model-selection)
- ...

## Semana 2 — Domain B (peso máximo)
...

## Semana 3 — Domain E + B intercalado
...

## Semana N-1 — Mock exams
- /ai103-mock domain-a (60 min real)
- ...

## Última semana — Revisión final
- /ai103-study-pack all --type all
- /ai103-mock all (full exam simulation)
- /ai103-flashcards all (spaced repetition diaria)
```

4. Pregunta si quiere guardar el plan en `00-Aggregations/study-route-<fecha>.md`.

## Reglas

- Adapta el plan al perfil del usuario (no genérico).
- Última sesión de cada semana → mock exam.
- Última semana → solo agregados + flashcards.

$ARGUMENTS
