---
name: sdd-feature-planning
description: Lleva una feature del harness desde intake hasta GATE#1 - lanza explorer y designer como subagentes reales, aplica las transiciones con el motor de estado y presenta la especificación para la decisión humana. Úsala cuando el humano pida iniciar, planificar o especificar una feature registrada ("arranca SAMPLE-001", "planifica la feature X"). No implementa ni aprueba el gate.
argument-hint: "[FEATURE-ID]"
---

# Planificación SDD de una feature

## Resultado

La feature en `gate1_pending` con `context.md`, `proposal.md`,
`requirements.md`, `design.md`, `tasks.md` y `acceptance.yaml` validados, y un
resumen para que el humano decida. Las reglas completas están en `HARNESS.md`
(secciones 4 a 7); esta skill es la secuencia.

## Procedimiento

1. Localiza la feature en `.claude/feature_list.json`; si no existe, usa
   `feature-kickoff`. Consulta el modo en `.claude/harness.toml`.
2. `python3 .claude/tools/feature.py start <ID>` y
   `python3 .claude/tools/feature.py transition <ID> start_exploration`.
3. Lanza el subagente `explorer` con la cabecera estándar:
   ```text
   FEATURE_ID: <ID>
   PHASE: exploration
   <petición del humano y contexto mínimo>
   ```
   Con `RESULT: completed`: `transition <ID> exploration_complete`.
4. Lanza el subagente `designer` (`PHASE: design`). Con `RESULT: completed`:
   `transition <ID> design_complete` (ejecuta la validación pre-gate).
5. Si el humano pidió especialistas antes del gate, ejecútalos ahora; si
   proponen cambios en la especificación, relanza el designer para
   reconciliarlos antes de presentar GATE#1.
6. Presenta GATE#1: recomendación, decisiones y supuestos a aprobar, riesgos,
   número de tareas, rutas de los artefactos, coste acumulado (skill
   `feature-cost`) y la lista literal de comandos de aceptación que imprimió
   `design_complete`, destacando los `[SENSIBLE]`. Indica cómo decidir: `/approve <ID> [comentario]` o
   `/reject <ID> <cambios>`. Después, **para**.
7. Modo manual: para también entre los pasos 3 y 4. Modo yolo: aplica la
   delegación de GATE#1 solo en las condiciones de `HARNESS.md` §6.

## Límites

- No lances el builder ni edites código del producto.
- No apruebes GATE#1 por tu cuenta (salvo la delegación yolo permitida).
- Si una transición se rechaza, corrige la causa dentro de tu autoridad (por
  ejemplo, relanzar el agente con la cabecera correcta) o escala con
  `transition <ID> escalate --reason "<motivo>"`. Nunca la esquives.
