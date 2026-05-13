# HARNESS.md — Contrato del harness

> Generado por harness-cli 0.4.0. NO editar a mano.
> Tus reglas locales van en AGENTS.md.

## 1. Resumen ejecutivo

Este proyecto usa harness-cli 0.4.0, sistema multi-agente con flujo SDD y gates humanos.

- **Perfil**: web-app
- **Cliente principal**: claude-code
- **Bundle directory**: `.claude/`
- **Tipo de flujo**: simple (4 agentes canónicos)
- **Dominios activos**: software, docs, ideation
- **Modo orquestación**: ver `.claude/harness.toml` campo `[orchestration].mode` (`manual` / `auto` / `yolo`)

**Combinatoria total**: 3 modos × 2 tipos de flujo = 6 modalidades de operación.
Cambia mode con `harness mode <manual|auto|yolo>`. El flow_type se fija al
`harness init`; cambiarlo requiere re-init.

## 2. Estructura del proyecto

- `HARNESS.md` (este archivo) — contrato. NO editar.
- `AGENTS.md` — reglas locales. Editable.
- `INSTRUCCIONES.md` — manual humano detallado.
- `FAST-USAGE.md` — 4 prompts copy-paste.
- `.claude/` — bundle operativo. Todo lo demás vive aquí.

## 3. Lectura obligatoria antes de actuar

1. Si existe `AGENTS.md`, sus reglas son obligatorias.
2. Lee `.claude/feature_list.json` para conocer features pendientes.
3. Si trabajas una feature en curso, lee `.claude/state/<feature-id>/state.yaml`.

## 4. Flujo SDD canónico

```
Explorer → Designer → GATE#1 → Builder → Reviewer(review) → GATE#2
                                                                ↓
                                            Reviewer(verify_archive) → DONE
```

`Designer` (simple) subsume Proposer + Spec-writer + Designer + Task-planner
del flujo complex. `Reviewer` se invoca dos veces: una en `review`
(post-Builder), otra en `verify_archive` (post-gate2).


## 5. Tabla operativa de fases

Tipo de flujo: **simple** (4 agentes canónicos: explorer, designer, builder, reviewer).

| # | Fase | Agente | Lee de | Escribe a | Siguiente |
|---|---|---|---|---|---|
| 1 | explore | explorer | feature_list.json[id] | `.claude/state/<id>/SDD/context.md` | design |
| 2 | design | designer | SDD/context.md, AGENTS.md | SDD/proposal.md, requirements.md, design.md, tasks.md, acceptance.yaml, sources.md | gate1 |
| 3 | gate1 | (humano o yolo) | SDD/* | state.yaml.gates.gate1 | implement |
| 4 | implement | builder | SDD/tasks.md, SDD/design.md, SDD/acceptance.yaml | mods en src/, SDD/implementation-notes.md | review |
| 5 | review | reviewer (fase 1/2) | diff vs main, SDD/* | SDD/review.md | gate2 |
| 6 | gate2 | (humano o yolo) | SDD/review.md, diff | state.yaml.gates.gate2 | verify_archive |
| 7 | verify_archive | reviewer (fase 2/2) | bootstrap/verify.sh, SDD/acceptance.yaml | SDD/verify-runs.jsonl, SDD/spec.lock.yaml, feature_list update | DONE |

> **Nota simple**: el `designer` produce los 6 artefactos de spec/design/tasks
> en un solo pase (subsume proposer + spec-writer + designer + task-planner del
> flujo complex). El `reviewer` se invoca **dos veces**: la primera como code
> reviewer (`review`), la segunda como verifier+archiver (`verify_archive`).


## 6. Cross-cutting (activación por tags)

Si `feature.tags` incluye:

- `security-critical`, `auth`, `crypto` → invoca `security-auditor` antes del `reviewer` en fase `review` (pre-gate2).
- `compliance`, `gdpr`, `audit` → invoca `compliance-officer` en gate2.
- `iac`, `terraform` → fase `verify_archive` ejecuta también `terraform-planner` antes del `reviewer` (fase 2/2).


## 7. Modos de orquestación

Lee `.claude/harness.toml` campo `[orchestration].mode`. Tres valores válidos: `manual`, `auto`, `yolo`.

### Modo `manual` (default)

Tras cada agente: para, espera confirmación humana antes de invocar el siguiente.
El humano dice "siguiente" o invoca el agente con un prompt específico.

### Modo `auto`

Encadena agentes automáticamente, **siempre parando obligatoriamente** en GATEs humanos.
Si `[orchestration.preview].show=true`, antes de invocar el siguiente agente imprime preview con countdown:

```
✓ explorer completado → SDD/context.md (1247 líneas, 4523 tokens, 12.3s)
→ Próximo: designer (opus, lee SDD/context.md, escribirá los 6 artefactos SDD)
  Esperando 5s antes de continuar. Pulsa cualquier tecla para pausar.
```


### Modo `yolo`

Encadena TODO sin parar, **incluyendo gates**.

**Cómo se gestionan los gates en yolo**:

Los gates **NO se eliminan**. Se **auto-aprueban con rationale registrado** en `state.yaml`.

Cuando el flujo llega a un gate en yolo, el orquestador debe:

1. Leer la entrada del gate en `.claude/state/<feature-id>/state.yaml`.
2. Tomar la decisión siguiendo la jerarquía:
   - **Primero**: `AGENTS.md` / `CLAUDE.md` (reglas locales). Precedencia absoluta.
   - **Segundo**: `HARNESS.md` (cross-cutting, security-critical, etc.).
   - **Tercero**: criterio propio basado en los artefactos del SDD/.
3. Llamar a `core.state.auto_approve_gate()` registrando:
   - `decision`: opción elegida (e.g. `"alt-B"`).
   - `decided_by`: literalmente `"yolo-mode"` (lo hard-codea la función).
   - `rationale`: 1-2 frases citando QUÉ regla aplicó.
   - `evidence`: path al input (e.g. `SDD/proposal.md`).

**Reglas innegociables en yolo**:

- `AGENTS.md` es ley. Si dice "siempre PostgreSQL", elige PostgreSQL aunque MongoDB parezca mejor.
- Si una decisión va contra `AGENTS.md`, **ABORTA y reporta conflicto**. No auto-apruebes a la fuerza.
- Si la feature tiene tags `security-critical`, el orquestador puede invocar agentes cross-cutting extra antes de auto-aprobar.

**Advertencia**:

Yolo no es para todos los proyectos. Úsalo solo si:

- Tienes `AGENTS.md` bien escrito con reglas explícitas.
- La feature está bien delimitada y sin decisiones críticas no documentadas.
- Aceptas el riesgo de que la IA tome una decisión que tú habrías tomado de otra forma.

Cambia el modo con: `harness mode <manual|auto|yolo>`.

## 8. event.log y verificación multi-agente

### Qué es

Cada feature tiene un archivo append-only `.claude/state/<feature-id>/event.log` en formato JSONL (una línea por evento).

### Quién escribe

**Cada subagente que se invoque debe escribir al menos dos líneas**:

- `started` cuando empieza su procedimiento.
- `completed` (o `failed`) cuando termina.

El campo `agent` en cada línea debe coincidir con el `name:` del frontmatter del subagente.

### Para qué sirve

1. **Verificar subagentes nativos**: si en `event.log` hay distintos `agent` IDs, confirma que el orquestador delegó en subagentes reales (no hizo todo él).
2. **Métrica de multiagencia**: `harness events <feature-id>` muestra `Unique agents: N`.
3. **Recovery**: el Prompt 3 (FAST-USAGE.md) lee `event.log` para reconstruir qué pasó si la sesión se interrumpió.

### Formato

```jsonl
{"timestamp": "ISO-8601-UTC", "feature_id": "<id>", "agent": "<name>", "event": "started"}
{"timestamp": "...", "feature_id": "<id>", "agent": "<name>", "event": "completed", "artifact": "SDD/<x>.md", "duration_ms": 12345}
```

Campos obligatorios: `timestamp`, `feature_id`, `agent`, `event`.
Opcionales: `artifact`, `duration_ms`, `tokens_in`, `tokens_out`, `cost_usd`, `error`, `notes`.

Eventos válidos: `started`, `completed`, `failed`, `blocked`, `resumed`.

### Cómo verificar

```bash
harness events <feature-id>
```

Muestra una tabla con timestamp/agent/event/details + resumen con número de agentes únicos.

## 9. Cómo invocar agentes

Cada agente vive en `.claude/agents/<nombre>.md` (formato Claude Code
subagent nativo desde 0.3.1: archivo `.md` plano con frontmatter
`name`/`description`/`tools`/`model`/`color`/`memory`).

En Claude Code: el cliente descubre los agentes automáticamente desde `.claude/agents/` y los despacha vía Task tool.


## 10. Cómo actualizar state.yaml

Tras completar una fase:

1. Lee `.claude/state/<feature-id>/state.yaml`.
2. Añade entry a `phase_history` con `status: completed`, `completed_at`, `artifact`.
3. Actualiza `current_phase` con la siguiente fase de la tabla.
4. Si la siguiente es un GATE, cambia `status` a `gate_blocked` y **PARA**.

## 11. Recovery: cómo retomar una sesión interrumpida

1. Lee `.claude/state/<feature-id>/state.yaml`.
2. Inspecciona `current_phase` y la última entrada de `phase_history`.
3. Lee TODOS los artefactos existentes en `.claude/state/<feature-id>/SDD/` para tener contexto completo.
4. Decide:
   - Si la última fase es `completed`: arranca la siguiente fase de la tabla.
   - Si la última fase es `in_progress`: la fase quedó a medias. **En caso de duda, reinicia esa fase** (borra el último entry de phase_history y vuelve a empezar).
   - Si hay artefactos en SDD/ no listados en `state.artifacts`: están huérfanos. Repórtalos al humano.
   - Si la fase actual es un gate (`gate_blocked`): espera aprobación humana antes de continuar.

## 12. Gates humanos

### GATE #1 (post-Designer)

El humano aprueba el design completo: el `designer` ya produjo en single
pass los 6 artefactos (proposal, requirements, design, tasks, acceptance,
sources). Si `proposal.md` contiene 2-3 alternativas, el humano elige una.

Sintaxis de aprobación:

- Claude Code: `/approve` o `/approve <alt-id>` (si hay alternativas), o `/reject <razón>`.
- Otros clientes: respuesta en texto plano "apruebo" / "apruebo alt-B" / "rechazo, motivo: ...".

### GATE #2 (post-Reviewer fase review)

El humano revisa el diff y `SDD/review.md` antes de pasar a
`verify_archive`. Sintaxis igual.

### GATE #3 (solo perfiles infra con `gate3_pre_apply`, pre-apply)

Antes de `terraform apply`. Humano revisa el plan. (Recomendado usar
flow `complex` para infra crítica.)


## 13. Agentes opcionales (on-demand)

Lista los agentes con `invocation: on-demand` del `agent-registry.yaml`.
Estos se invocan solo si:

- El humano los menciona explícitamente en el prompt de arranque (Prompt 2 de FAST-USAGE).
- El orquestador los detecta como necesarios según el contexto de la feature.

## 14. Reglas locales del proyecto

Si existe `AGENTS.md` en raíz, sus reglas son obligatorias y tienen precedencia sobre defaults pero **nunca sobre este HARNESS.md** (gates, flujo SDD, contratos).
