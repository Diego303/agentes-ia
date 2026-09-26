# Arquitectura del harness

## Objetivos

- Contexto pequeño y especializado por agente; conocimiento persistido fuera
  de la ventana de contexto (`.claude/state/<ID>/`).
- Salida de la IA verificable con comandos y evidencia.
- Features interrumpibles y reanudables sin reconstruir la conversación.
- Trazabilidad de modelo, tokens, coste, artefactos y decisiones.
- Seguridad por defecto: fronteras deterministas frente a prompt injection.
- Base general, especializable por dominio sin tocar el core.

## Capas

1. **Instrucciones**: `CLAUDE.md` (importa `HARNESS.md` y `AGENTS.md`) para la
   sesión principal; cada subagente recibe solo su contrato (`omitClaudeMd`),
   `AGENTS.md` y las skills que precarga.
2. **Contrato**: `contracts/workflow.toml`. Las guards son funciones de
   `validate_harness.py`; el validador comprueba que todas existen.
3. **Motor**: `feature.py` aplica transiciones, congela la especificación en
   GATE#1 y mantiene coherentes `state.yaml`, `feature_list.json` y `event.log`.
4. **Evidencia**: `run_acceptance.py` (aceptación aprobada) y el veredicto
   estructurado del reviewer.
5. **Observabilidad**: `ledger.py` registra cada subagente desde su transcript
   (hook `SubagentStop`): ID runtime, modelo, tokens y coste.
6. **Seguridad**: `guard.py` (hook `PreToolUse`) y permisos de `settings.json`.

## Decisiones de diseño

| Decisión | Motivo |
| --- | --- |
| Un solo gate humano obligatorio | El antiguo GATE#2 aprobaba código antes de saber si pasaba la aceptación; el humano revisa el diff al hacer commit |
| Reviewer en un único pase | Una invocación menos por feature (menos coste) y un veredicto con toda la evidencia |
| Un solo repair automático | Corrección autónoma sin bucles abiertos ni deriva de alcance |
| Spec congelada por hash | Hace verificables "el builder no rediseña" y "la aceptación no cambió" |
| Motor de estado en lugar de edición manual | El LLM decide qué evento aplicar; el código decide si es legal |
| Runtimes y costes desde transcripts | Los modelos no conocen sus tokens; el hook los mide sin coste de contexto |
| Subconjunto YAML propio y solo stdlib | Mismo comportamiento en cualquier máquina, sin dependencias |
| Sin memoria de agente (`memory:`) | Estado oculto y no revisable; lo aprendido se promueve a `AGENTS.md` |
| Agentes sin herramientas web; red externa bloqueada en Bash | Menos superficie de inyección y de exfiltración |
| `guard.py` por listas blancas y sin distinguir mayúsculas; si falla, bloquea | Una regla que falla en abierto convierte cada fallo en una autorización silenciosa |
| Verificación de runtimes contra el transcript real | Una línea de `event.log` se puede falsificar; el transcript del subagente, mucho menos |

## Adaptaciones respecto a `HARNESS_REFERENCE.md`

Todas las mejoras de la referencia están incorporadas; estas se implementan de
otra forma por ser Claude Code (no Codex) o por ser más fiables así:

| Referencia | Aquí | Motivo |
| --- | --- | --- |
| `runtime-agents.yaml` escrito por el orquestador | eventos `subagent_stop` en `event.log`, escritos por el hook `SubagentStop` | ID runtime, modelo y tokens reales, sin depender del LLM |
| `gates/gate1.yaml`, `orchestration.lock.yaml` | bloques `gate1` y `lock` de `state.yaml` | un único archivo de estado, escrito solo por `feature.py` |
| `orchestration-plan.md` | contrato fijo + especialistas declarados en el registro | el flujo simple no necesita plan por feature |
| `acceptance.yaml` con `status` y `evidence` | acceptance inmutable; evidencia en `acceptance-results.json` | la spec aprobada se congela por hash |
| `blocked` terminal | `blocked` como espera humana con salidas explícitas | recuperar sin editar el estado a mano |
| `exploration.md` + `SDD/context.md` + `SDD/sources.md` | `SDD/context.md` (con `## Fuentes`) y columna Fuente en `requirements.md` | menos archivos, misma trazabilidad |
| `config.toml`: `max_depth = 1`, hilos concurrentes | agentes canónicos sin herramienta `Agent` (lo valida el validador) y `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` en `settings.json` | equivalente nativo de Claude Code |
| Modelos `gpt-5.6-*` y `model_reasoning_effort` | `model` y `effort` en el frontmatter de cada agente | equivalente nativo de Claude Code |
| `backend-feature-kickoff` | `feature-kickoff` | el core no asume stack |
| `plugin-eval` (CLI de Codex) | `plugin-eval` sobre `claude plugin eval`, `/skill-doctor` y `skill-creator` | herramientas nativas de Claude Code |
| Solo `GATE#1` humano; sin modos | GATE#1 obligatorio + modos `manual`/`auto`/`yolo` del harness original | yolo solo delega GATE#1 y nunca con tags sensibles |

## Límites deliberados

Un orquestador; un gate obligatorio; un repair; sin base de datos de memoria
ni vector store; sin motor de grafos externo; sin router de modelos; sin
revisores paralelos obligatorios; sin dependencias Python externas. Son
decisiones de simplicidad: se revisan solo ante una necesidad observada y
medible (ver `HARNESS.md` §14).

## Relación con harness, loop y graph engineering

- **Harness**: contratos, agentes, skills, plantillas, memoria persistente,
  validación y reglas de autoridad. No sustituye el juicio del modelo;
  delimita dónde actúa y qué evidencia deja.
- **Loop**: deliberadamente corto (`Builder → Reviewer → PASS | un repair | humano`).
- **Graph**: `workflow.toml` es el grafo; el orquestador lo recorre y
  `feature.py` impide aristas ilegales.
