# Conceptos del harness

Este documento define el vocabulario que los agentes y el orquestador
deben compartir. Los conceptos se describen para el flow_type activo en
este proyecto: **simple**.

## Spec Driven Development (SDD)

Disciplina que separa **qué** se construye (spec) de **cómo** se
construye (implementación). El harness automatiza la transición entre
fases:

explorar → diseñar (genera todos los artefactos) → implementar → revisar →
verify_archive (verifica + archiva).


## Agente

Un archivo `<bundle>/agents/<name>.md` (formato Claude Code subagent
nativo desde 0.3.1) con frontmatter YAML obligatorio:

- `name` — kebab-case, coincide con el filename.
- `description` — frase con el patrón "Verbo. Usar cuando trigger.".
- `tools` — subset de {Read, Write, Edit, Bash, Grep, Glob, WebFetch,
  WebSearch, Task}.
- `model` — uno de {haiku, sonnet, opus, inherit}.
- `color` — hint visual por rol funcional (cyan/yellow/blue/purple/
  orange/green/red/gray/magenta/pink/teal).
- `memory: project` — scope del subagent.

El cuerpo Markdown contiene **5 secciones fijas**: Rol, Inputs esperados,
Procedimiento (con bloque `### Event logging`), Output (con sub-bloques
`### Siguiente paso` y `### Cuándo parar y pedir ayuda`), Anti-patterns.

## Skill

Procedimiento auxiliar invocable por un agente. Vive en
`<bundle>/skills/<name>/SKILL.md`. No es un agente: no tiene rol propio
en el flujo SDD.

## Gate humano

Punto del flujo SDD donde el orquestador para y espera aprobación
explícita de una persona (modo `manual`/`auto`) o auto-aprueba con
`rationale` registrado (modo `yolo`).

- **GATE#1** post-Designer: aprueba el diseño (spec/design/tasks
  generados upfront).
- **GATE#2** post-Reviewer: aprueba el code review antes de
  verify_archive.


## Modos de orquestación

`<bundle>/harness.toml` campo `[orchestration].mode`:

- `manual` (default) — para tras cada agente y en cada gate.
- `auto` — encadena agentes; PARA SIEMPRE en gates humanos.
- `yolo` — encadena TODO; gates auto-aprobados con `rationale` en
  `state.yaml`. Requiere `AGENTS.md` bien definido. Ver `HARNESS.md`
  sección 7 para mecánica completa.

## Tipo de flujo (flow_type)

Este proyecto usa **flow_type = `simple`** declarado en
`<bundle>/harness.toml.[project].flow_type`.

- `simple` — 4 agentes canónicos (explorer, designer, builder,
  reviewer). Designer subsume 4 fases del complex; reviewer se invoca
  dos veces.
- `complex` — 9 agentes canónicos (explorer, proposer, spec-writer,
  designer, task-planner, implementer, code-reviewer, verifier,
  archiver). Default en la mayoría de perfiles.

Cambiar `flow_type` requiere re-init del proyecto. Cambiar `mode` se
hace en caliente con `harness mode <X>`.

## Bundle

Carpeta `<bundle_dir>/` que contiene todo lo operativo del harness.
Su nombre depende del cliente principal: `.claude/` para Claude Code,
`.harness/` para clientes genéricos.

## Feature

Unidad de trabajo del flujo SDD. Tiene `id`, `title`, `domain`, `status`
y opcionalmente `tags`. Se declara en `feature_list.json` y su estado
en curso vive en `<bundle>/state/<id>/state.yaml`.

## state.yaml

Archivo per-feature que rastrea progreso (status, current_phase,
phase_history, gates con `decided_by`/`rationale`, artifacts, metrics).
Atómico vía `tempfile.mkstemp` + `os.replace`.

## event.log

Archivo JSONL append-only por feature en
`<bundle>/state/<id>/event.log`. Cada agente appendea
`started`/`completed`/`failed` con su `agent` ID. Permite a
`harness events <id>` verificar multi-agencia (≥ 2 agentes únicos).
