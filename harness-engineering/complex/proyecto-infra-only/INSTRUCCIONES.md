# INSTRUCCIONES.md — Manual humano

> Cómo usar este proyecto con harness-cli, paso a paso.
> Si solo quieres los prompts, ve a `FAST-USAGE.md`.

## Setup inicial

```bash
.claude/bootstrap/init.sh
```

Esto verifica el entorno y deja el proyecto listo. Si falla, el script te dice qué arreglar.

## Conceptos clave

### El flujo SDD

El harness sigue un flujo Spec Driven Development en **10 fases**:

1. **Explore** (explorer) — mapea el contexto del codebase.
2. **Propose** (proposer) — genera 2-3 alternativas técnicas.
3. **GATE #1** — humano elige alternativa.
4. **Spec & Design** (spec-writer + designer en paralelo) — formaliza requisitos y arquitectura.
5. **Tasks** (task-planner) — descompone en tareas atómicas.
6. **Implement** (implementer) — modifica código.
7. **Review** (code-reviewer) — verifica diff contra spec/design.
8. **GATE #2** — humano revisa.
9. **Verify** (verifier) — ejecuta `verify.sh` y `acceptance.yaml`.
10. **Archive** (archiver) — actualiza feature_list, genera `spec.lock.yaml`.


### Los gates humanos

Hay puntos donde el orquestador para y espera tu aprobación (o
auto-aprueba con rationale en modo yolo):

- **GATE #1** tras Proposer: eliges entre 2-3 alternativas técnicas.
- **GATE #2** tras Code-reviewer: revisas el diff antes del verifier.
- **GATE #3** (solo perfil infra) antes de `terraform apply`.


### Modo manual vs auto vs yolo

En `.claude/harness.toml`, campo `[orchestration].mode`:

- `manual` (default): tras cada agente, el orquestador espera tu confirmación.
- `auto`: el orquestador encadena agentes solo, **siempre** parando en gates humanos.
- `yolo`: encadena TODO sin parar; gates auto-aprobados con rationale en
  `state.yaml` (ver HARNESS.md sección 7 para mecánica completa).

Cambia el modo con: `harness mode <manual|auto|yolo>`.

### Modos × Tipos de flujo: las 6 combinaciones

El harness combina dos dimensiones ortogonales:

| Modo | Simple (4 agentes) | Complex (9 agentes) |
|---|---|---|
| **manual** | Para tras cada agente y en cada gate. Iteración aprendida. | Para tras cada agente y en cada gate. Máximo control. |
| **auto** | Encadena 4 agentes; para sólo en gates. Iteración rápida. | Encadena 9 agentes; para sólo en gates. Trabajo serio sin micro-management. |
| **yolo** | Encadena todo, gates auto-aprobados. Prototipos / scripts. | Encadena todo, gates auto-aprobados. Sólo si AGENTS.md está MUY bien escrito. |

**Recomendaciones por combinación**:

- **manual + complex**: máximo control, features críticas, primera vez con el harness.
- **auto + complex**: trabajo serio sin micro-management. Default razonable para producto.
- **yolo + complex**: sólo si AGENTS.md cubre todas las decisiones; útil en sprints de iteración rápida con un humano supervisando lateralmente.
- **manual + simple**: aprender el flow simple; comprender qué subsume el designer.
- **auto + simple**: iteración rápida con humano en gates. Buen balance para features pequeñas.
- **yolo + simple**: prototipos, scripts internos, features triviales bien delimitadas.

**Ejes de cambio**:

- Cambiar **mode**: en caliente con `harness mode <manual|auto|yolo>`.
- Cambiar **flow_type**: NO se cambia en caliente. Re-inicializa el proyecto
  con `harness init <profile> --target <new-path> --type <type>` y migra los
  artefactos relevantes.

## Uso por cliente IA

### Claude Code

1. Abre el proyecto en Claude Code.
2. Pega el **Prompt 1** de FAST-USAGE.md para que entienda el harness.
3. Pega el **Prompt 2** con tu plan/feature para arrancar el flujo.
4. Cuando llegue a un gate humano, el cliente parará. Responde con `/approve` (o equivalente) o `/reject <razón>`.

### Codex CLI

Igual que Claude Code pero en lugar de slash commands, responde con texto plano:
- "Apruebo la alternativa B" en lugar de `/approve B`.
- "Rechazo, motivo: ..." en lugar de `/reject ...`.

### Cursor

Similar a Claude Code. Apunta al cliente a leer HARNESS.md como instrucción inicial.

### Genérico (cualquier otro cliente)

1. Abre tu cliente con el repo.
2. Apunta al cliente a leer HARNESS.md como instrucción inicial.
3. Para invocar agentes, dale el path del SKILL.md correspondiente.

## Comandos útiles del harness CLI

- `harness doctor` — diagnóstico del proyecto.
- `harness next` — siguiente paso recomendado.
- `harness status` — estado de las features.
- `harness mode <manual|auto|yolo>` — cambia modo de orquestación.
- `harness add-domain <name>` — añadir dominio a este proyecto.
- `harness regenerate-registry` — reconstruye agent-registry.yaml.

## Resolución de problemas

- **Una feature está bloqueada** → mira `.claude/state/<id>/state.yaml` campo `current_phase`.
- **Quiero rehacer una fase** → edita `state.yaml` manualmente o usa `harness recover <feature> --fix`.
- **Sesión interrumpida** → usa el Prompt 3 de FAST-USAGE.md.
- **No sé qué agentes usar** → usa el Prompt 4 de FAST-USAGE.md.
