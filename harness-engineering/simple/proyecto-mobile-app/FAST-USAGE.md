# FAST-USAGE.md — 4 prompts esenciales

> Copy-paste directo. Edita los placeholders cuando los haya.
>
> **Configuración actual**: flow_type = `simple`, perfil = `mobile-app`.
> Para cambiar el modo: `harness mode <manual|auto|yolo>`.
> Para cambiar el flow_type: re-inicializa el proyecto.

---

## Prompt 1 — Bootstrap (entender el harness)

Úsalo al abrir el proyecto en una sesión nueva, antes de pedir trabajo.

```
Lee HARNESS.md y .claude/agents/agent-registry.yaml.
Lee también .claude/feature_list.json.

Sin ejecutar nada todavía, dime:
1. Qué es este harness y cuál es el flujo SDD canónico.
2. Qué agentes están disponibles (agrupados por dominio y rol).
3. Qué features hay pendientes en feature_list.json.
4. Qué agentes son automáticos en el flujo y cuáles opcionales (on-demand).
5. En qué modo de orquestación está configurado (manual/auto).

Cuando termines, espera a que te dé una tarea o un plan.
```

---

## Prompt 2 — Arrancar feature (con plan + agentes opcionales)

Úsalo cuando tengas un plan/feature listo. Edita las dos partes marcadas.

```
[PEGA AQUÍ TU PLAN, FEATURE O TAREA. Puede ser tan corto como
"Implementar JWT auth con refresh rotativo" o tan largo como un
documento de 200 líneas.]

---

Agente orquestador, inicia el trabajo siguiendo HARNESS.md.

Este proyecto usa flujo SIMPLE: 4 agentes canónicos
(explorer → designer → builder → reviewer). El designer produce TODOS los
artefactos SDD upfront (proposal, requirements, design, tasks, acceptance,
sources). El reviewer se invoca DOS VECES, una en `review` y otra en
`verify_archive` (separadas por gate2).
[OPCIONAL — borra esta línea si no aplica:]
Usa también estos agentes adicionales: <agente-extra-1>, <agente-extra-2>

Recuerda:
- Si el modo es manual, espera mi confirmación entre fase y fase.
- Si el modo es auto, encadena agentes pero PARA OBLIGATORIAMENTE en gates
  humanos. Muestra preview antes de cada agente con 5s de countdown.
- Si el modo es yolo, AUTO-APRUEBA gates siguiendo HARNESS.md sección 7
  (lee AGENTS.md → toma decisión → llama auto_approve_gate() con rationale).
  Si la decisión va contra AGENTS.md → ABORTA y reporta.
- Actualiza state.yaml tras cada fase completada.
- Appendea a event.log en cada start/complete con tu agent ID.
```

---

## Prompt 3 — Continuar feature interrumpida

Úsalo si la sesión anterior se cortó o quieres retomar tras un gate.

```
Lee .claude/state/<feature-id>/state.yaml para entender
dónde quedó el flujo SDD de esta feature. Lee también:
- TODOS los artefactos existentes en .claude/state/<feature-id>/SDD/
- .claude/state/<feature-id>/event.log (formato JSONL)

El event.log te dice qué subagentes se han invocado y en qué orden.
Combinado con state.yaml + artefactos en SDD/, tienes contexto completo.

Aplica la lógica de recovery descrita en HARNESS.md sección 11:
- Si la última fase quedó "in_progress" sin completar: reinicia esa fase.
- Si quedó "completed" y la siguiente es un gate humano: espera mi /approve.
- Si quedó "completed" y la siguiente es ejecutable: continúa con esa fase.
- Si hay artefactos huérfanos (en SDD/ pero no en state.artifacts): repórtalos.
- Si event.log muestra fallos previos: tenlos en cuenta.

Antes de empezar, dime:
- En qué fase quedó (current_phase).
- Qué artefactos existen ya en SDD/.
- Qué eventos hay en event.log (lista los últimos 5).
- Qué fase vas a ejecutar a continuación.
- Si hay algo inconsistente que requiera mi intervención.
```

---

## Prompt 4 — Recomendación de agentes

Úsalo para elegir qué agentes opcionales usar antes de arrancar.

```
Lee .claude/agents/agent-registry.yaml. Dime los agentes disponibles
agrupados por:
- Automáticos (parte del flujo SDD canónico).
- Cross-cutting (se activan automáticamente por tags de feature).
- On-demand (se invocan solo si lo pido).

[OPCIONAL — describe la tarea que quieres abordar:]
Tarea: <DESCRIBE TU TAREA EN 1-3 LÍNEAS>

Si he pasado tarea: recomiéndame qué agentes on-demand deberían
participar y por qué. Ordena por relevancia. Para cada uno, indica:
- Nombre del agente.
- En qué fase del flujo encajaría.
- Por qué es relevante para esta tarea.
- Cómo invocarlo en el Prompt 2 (sintaxis exacta).
```

---

## Apéndice: variables del proyecto

- `bundle_dir`: `.claude/`
- `cliente`: `claude-code`
- `perfil`: `mobile-app`
- `dominios`: software, mobile, docs
