---
name: plugin-eval
description: Evalúa una skill, un agente o un plugin local de Claude Code y explica qué arreglar primero - estructura, coste de contexto, activación (triggering) y efecto real frente a una línea base. Úsala cuando digan "evalúa esta skill", "¿por qué no se activa?", "¿cuánto contexto consume?", "compárala con la versión anterior", "qué debería arreglar primero" o "qué ejecuto ahora".
---

# Plugin Eval (Claude Code)

> Adapta la skill `plugin-eval` de la referencia (pensada para el CLI de Codex)
> a las herramientas nativas de Claude Code.

## Elige la herramienta

| Pregunta | Herramienta |
| --- | --- |
| ¿Está bien formada? | `python3 .claude/tools/validate_harness.py` (skills y agentes del harness); para plugins, `claude plugin validate <ruta>` |
| ¿Cuánto contexto consume y cuánto se usa? | `/skill-doctor` (tokens por turno, invocaciones y coste de 7 días; lo ejecuta el humano) |
| ¿Se activa cuando debe? | skill `skill-creator`, optimización de la description (consultas que deben y no deben activarla) |
| ¿Mejora el resultado frente a no tenerla? | skill del proyecto: `skill-creator` (`evals/evals.json`, con y sin la skill); plugin: `claude plugin eval <ruta> --runs 3 --max-cost-usd <límite>` |

## Procedimiento

1. Resuelve la ruta: skill en `.claude/skills/<nombre>/`, agente en
   `.claude/agents/<nombre>.md` o raíz de un plugin. Si solo te dan un nombre y
   es ambiguo, haz una pregunta corta.
2. Análisis estático: frontmatter válido, `description` con qué hace y cuándo
   usarla (máximo 1536 caracteres), cuerpo de menos de ~500 líneas, archivos
   referenciados que existen e instrucciones que explican el porqué.
3. Si piden medir: propone de 3 a 5 prompts realistas más 1 o 2 casos
   negativos cercanos, y la línea base. Acuerda el presupuesto antes de
   ejecutar: `claude plugin eval` y `skill-creator` lanzan sesiones reales.
4. Informe: **De un vistazo**, **Por qué importa**, **Arreglar primero** y
   **Siguiente paso** con el comando exacto que el humano puede ejecutar.

## Límites

- Distingue siempre estimación estática de medición real.
- `claude plugin eval` solo evalúa plugins, no skills sueltas de `.claude/skills/`.
- Nada que gaste dinero sin confirmación del humano (usa `--max-cost-usd`).
