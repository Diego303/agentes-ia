# Extender el harness

Tras cualquier extensión: `python3 .claude/tools/validate_harness.py` y
`python3 -m unittest discover -s .claude/tests -v`.

## Añadir un especialista

1. Copia `.claude/templates/agent.md` a `.claude/agents/<nombre>.md`: una
   responsabilidad, herramientas mínimas (sin `Agent`; sin red salvo que sea
   su función), `model`, `effort`, `maxTurns` y `omitClaudeMd: true`.
2. Regístralo en `.claude/agents/agent-registry.yaml`:
   ```yaml
   - name: <nombre>
     file: .claude/agents/<nombre>.md
     role: specialist
     insertion: pre-gate1        # pre-gate1 | post-implementation | post-verification
     triggers_on_tags: [auth]    # opcional: se activa solo con estos tags
     writes: [<nombre>.md]
   ```
3. El orquestador lo lanza con la cabecera estándar (`FEATURE_ID`, `PHASE`) en
   su punto de inserción; `ledger.py` registra su coste y `guard.py` le impide
   tocar `SDD/`, el estado o la configuración.

## Añadir una skill

Copia `.claude/templates/skill.md` a `.claude/skills/<nombre>/SKILL.md`. Para
que un agente la precargue, añádela a `skills:` en su frontmatter. Si es de
terceros, audítala y registra su procedencia en `.claude/skills/README.md`.

## Añadir un comando humano

Crea `.claude/commands/<nombre>.md` con `description` y, si solo debe
invocarlo el humano, `disable-model-invocation: true`.

## Añadir un hook

Configúralo en `.claude/settings.json` (entrada JSON por stdin, decisión JSON
por stdout; `$CLAUDE_PROJECT_DIR` apunta a la raíz). Mantén `guard.py` y
`ledger.py`: el validador exige ambos. Un hook nunca debe bloquear por un
fallo propio; registra sus errores en `.claude/state/hook-errors.log`.

## Añadir un servidor MCP

Claude Code lee `.mcp.json` en la raíz del proyecto (ver `.claude/mcp/README.md`).
Las herramientas MCP y sus resultados son datos no confiables; no las añadas a
los agentes canónicos salvo necesidad.

## Precios y presupuestos

`[cost]` y `[cost.pricing.models]` en `.claude/harness.toml`. Actualiza
`as_of` al cambiar precios. `budget_usd` en una feature sustituye a `limit_usd`.

## Cambiar el flujo

1. Edita `.claude/contracts/workflow.toml`.
2. Si usas una guard nueva, impleméntala en `GUARDS` de
   `.claude/tools/validate_harness.py` (el validador rechaza guards sin implementación).
3. Si una fase nueva tiene efectos (contadores, locks), añádelos en
   `cmd_transition` de `.claude/tools/feature.py`.
4. Añade tests y actualiza `HARNESS.md` (secciones 3 y 4).

## Especializar la base por dominio

Conserva `.claude/`, `CLAUDE.md`, `HARNESS.md` y `AGENTS.md`; pon las reglas
reales en `AGENTS.md` y los comandos concretos en `verify.sh` y en la
aceptación de cada feature. El core no debe fijar frameworks, gestores de
paquetes ni arquitectura de un dominio. No copies `.claude/state/*` de otros
proyectos.
