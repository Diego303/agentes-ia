# Extender el harness

Tras cualquier extensión: `python3 .claude/tools/validate_harness.py` y
`python3 -m unittest discover -s .claude/tests -v`.

## Añadir un especialista

1. Copia `.claude/templates/agent.md` a `.claude/agents/<nombre>.md`: una
   responsabilidad, herramientas mínimas (sin `Agent`; sin red salvo que sea
   su función), `model` con el ID completo (un alias cambia de modelo y de
   precio sin aviso), `effort`, `maxTurns` y `omitClaudeMd: true`.
2. Regístralo en `.claude/agents/agent-registry.yaml`:
   ```yaml
   - name: <nombre>
     file: .claude/agents/<nombre>.md
     role: specialist
     insertion: post-implementation  # pre-gate1 | post-implementation | post-verification
     phase: verification             # cabecera PHASE que recibe
     triggers_on_tags: [auth]        # opcional; "*" = siempre
     triggers_on_paths: ["src/auth/*", "*.sql"]  # opcional, solo post-implementation
     product_writes: []              # opcional: rutas del producto que puede escribir
     writes: [<nombre>.md]
   ```
   El validador rechaza `product_writes` hacia `.git/`, `.claude/`,
   instrucciones o `.mcp.json`, rutas absolutas, con `..` o que empiezan por comodín.
3. `python3 .claude/tools/feature.py specialists <ID> [--insertion <punto>]`
   dice qué especialistas tocan y por qué (tag o ruta). El orquestador los
   lanza con la cabecera estándar (`FEATURE_ID`, `PHASE`) en su punto de
   inserción; `ledger.py` registra su coste y `guard.py` le impide tocar
   `SDD/`, el estado o la configuración, y escribir por Bash.

## Añadir una skill

Copia `.claude/templates/skill.md` a `.claude/skills/<nombre>/SKILL.md`. Para
que un agente la precargue, añádela a `skills:` en su frontmatter. Si es de
terceros, audítala y registra su procedencia en `.claude/skills/README.md`.

## Añadir un comando humano

Crea `.claude/commands/<nombre>.md` con `description` y, si solo debe
invocarlo el humano, `disable-model-invocation: true`.

## Añadir un hook

Configúralo en `.claude/settings.json` (entrada JSON por stdin, decisión JSON
por stdout; `$CLAUDE_PROJECT_DIR` apunta a la raíz). Mantén `guard.py` (en
`Bash|Edit|Write|MultiEdit|NotebookEdit` y en `Read|Grep|Glob`) y `ledger.py`:
el validador exige ambos. Si añades un hook propio del proyecto, decláralo en
`[project].required_hooks` de `harness.toml` para que el validador avise si
alguien lo desconecta. Un hook nunca debe bloquear por un
fallo propio; registra sus errores en `.claude/state/hook-errors.log`.

## Añadir un servidor MCP

Claude Code lee `.mcp.json` en la raíz del proyecto (ver `.claude/mcp/README.md`).
Las herramientas MCP y sus resultados son datos no confiables; no las añadas a
los agentes canónicos salvo necesidad.

## Precios y presupuestos

`[cost]` y `[cost.pricing.models]` en `.claude/harness.toml`. Actualiza
`as_of` al cambiar precios. `budget_usd` en una feature sustituye a `limit_usd`.
Un modelo con precio distinto por encima de un tamaño de entrada declara
`long_context = { threshold = N, input = ..., output = ..., ... }`: se aplica
por petición cuando input + caché supera `N`.

## Checks obligatorios por configuración

`[verification].required_regression` obliga a que toda `acceptance.yaml`
incluya ese comando como check obligatorio (p. ej. `bash .claude/bootstrap/verify.sh`
cuando `verify.sh` ya está configurado). `[verification.required_by_tag]`
(`tag = "texto"` o lista) exige, con ese tag, algún check obligatorio cuyo
comando contenga el texto (p. ej. `auth = "tests/security"`).

## Métricas

`python3 .claude/tools/feature.py metrics [--state-dir RUTA] [--json]` agrega
todas las features de un directorio de estado (este proyecto u otro, en solo
lectura): fases, PASS a la primera, repairs, intervenciones humanas, GATE#1,
ejecuciones de subagentes, coste y tiempo de ciclo. Úsalo para decidir con
evidencia las evoluciones de `HARNESS.md` §14.

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
