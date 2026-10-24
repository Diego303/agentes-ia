# Changelog del bundle

La versión más reciente debe coincidir con `[harness].bundle_version` de
`harness.toml` (lo comprueba `validate_harness.py`).

## 0.8.0 · perfil `olas`

Mismo núcleo que `harness-base` 0.8.0 (motor, contratos, agentes, plantillas,
validador, guard y ledger idénticos; `make harness-drift` lo comprueba) más el
modo de olas: varias features a la vez, cada una en su worktree y con su
propia sesión.

- `scripts/ola.sh` (versión 3): `abrir`, `estado`, `integrar` (`--continuar`,
  `--abortar`) y `cerrar`. Generalizado del sistema de olas de un proyecto
  real: cualquier prefijo de ID con el patrón del harness, rama de
  integración configurable y la parte del stack (instalación, lockfiles,
  generadores, dependencias implícitas) en la cabecera. Nunca confirma
  commits, push ni descartes desde Claude Code.
- Skill `olas` y comando `/ola` para la sesión del árbol principal.
- `docs/planes/olas.md` (plantilla: reglas, conflictos, olas y dependencias
  implícitas) y `docs/planes/guia-olas.md` (manual del script).
- `AGENTS.md`: apartado «Paralelo» en Git y convención `depende de:` en las
  notas de `feature_list.json`; `feature-kickoff` la aplica al registrar.
- `HARNESS.md` §15; `harness.toml` con `profile = "olas"`;
  `bash scripts/ola.sh estado|ayuda` preaprobados en `settings.json`.
- `test_ola.py`: el script de punta a punta en un repo temporal con
  worktrees reales (dependencias, commit del worktree, squash, conflictos con
  `feature_list.json` automático, pasos del proyecto, verify en rojo,
  abortar y cerrar).

## 0.8.0

Base genérica al día: incorpora las correcciones y mejoras genéricas de los
dos harnesses derivados en uso real (avizor 0.6.0/0.7.0 y struo 0.6.0/0.7.0),
añade métricas agregadas y actualiza los precios. Nada específico de producto.
Las versiones 0.6 y 0.7 no existen en la base: corresponden a esos derivados.

### Correcciones (auditoría de 0.5.0, `HARNESS-GUIA-COMPLETA.md` §33)
- H-01: el lock se considera obsoleto por su **última actividad** (transición o
  subagente), no por su antigüedad.
- H-02: `retry_exploration` reinicia GATE#1, contadores, foto de git y
  `spec.lock.json`, como `replan`.
- H-03: los agentes canónicos fijan el ID completo del modelo
  (`claude-sonnet-5-5`, `claude-opus-5-5`); el validador avisa de alias
  (`agent_model_alias`) y de modelos sin precio (`agent_model_unpriced`).
- H-05: la siguiente acción del builder indica `MODE: repair` solo tras
  `repairable_failure`.
- H-06: el aviso de presupuesto salta en `min(warn_usd, 0.8 × límite)`.
- H-09: se retira la copia local de `skill-creator` (se usa la integrada).
- `feature.py add` rechaza presupuestos ≤ 0.

### Seguridad (`guard.py`, traído de avizor y struo y generalizado)
- Análisis léxico de comandos que respeta comillas y heredocs: un texto buscado
  (`grep "-> None"`, `rg "git"`) ya no es una redirección ni una invocación, y
  el cuerpo de un heredoc es texto.
- Solo el builder escribe por Bash: reviewer, especialistas y subagentes no
  registrados son de solo lectura (sin redirecciones fuera de los temporales,
  edición en el sitio, código en línea, `eval`/`source`, `xargs`/`find -exec`
  que escriben, formateadores o `--fix`/`--write`, informes de pruebas fuera de
  `/tmp`).
- Especialistas confinados: escriben su informe y, solo si el registro lo
  declara en `product_writes`, esas rutas del producto. Un subagente no
  registrado ya no escribe código del producto. Registro ilegible → bloqueo.
- Nuevo hook `Read|Grep|Glob` → `guard.py`: secretos y claves no se leen
  (tampoco con comodines). Lecturas indirectas por Bash (comodines como `.en?`,
  sustituciones, `xargs`, `grep -r` amplio): deny a subagentes, confirmación a
  la sesión principal. Escribir archivos de secretos: deny para todos.
- `scripts/ola.sh` (perfil `olas`, `harness-base-olas`): ningún subagente lo
  ejecuta y la sesión principal no puede usarlo con `--si` ni tocando
  `CLAUDECODE`. La regla vive en el núcleo para que sea idéntico en los dos
  perfiles; sin el script no tiene efecto.
- Instalaciones ampliadas (`npx`, `pnpm dlx/update/remove`, `cargo update`,
  `rustup install`...); `git tag --list` permitido; `rg` en la lista de lectura.

### Validador y aceptación
- Registro: `insertion`, `phase`, listas de `triggers_on_tags`,
  `triggers_on_paths` y `product_writes` (sin rutas protegidas, absolutas ni
  comodines iniciales), profundidad (`Agent`/`Task`) en todos los agentes.
- `[verification].required_regression` y `[verification.required_by_tag]`
  (opcionales): checks obligatorios exigidos por configuración o por tag.
- `[project].required_hooks`: hooks propios que `settings.json` debe llamar.
- El hook de guard debe cubrir también `Read|Grep|Glob` (`hook_guard_tools`).
- Checks que ocultan el código de salida (`|| true`, `; exit 0`) o encadenan a
  `head`/`less`/`more` se rechazan; `run_acceptance.py` ejecuta con
  `set -o pipefail` y conserva `XAUTHORITY`/`DISPLAY` (E2E en Linux).
- `FEATURE_ID_PATTERN` único (IDs como `F4-PORT-AGENT-01`, máx. 64 caracteres).

### Nuevos subcomandos (solo lectura)
- `feature.py specialists <ID> [--insertion ...] [--json]`: especialistas que
  tocan por tags y por rutas cambiadas desde `base_commit` (`triggers_on_paths`).
- `feature.py metrics [--state-dir RUTA] [--json]`: métricas agregadas (fases,
  PASS a la primera, repairs, intervenciones humanas, GATE#1, ejecuciones de
  subagentes, coste total/mediana/p90 y tiempo de ciclo).

### Precios (`as_of = 2026-10-24`, página oficial)
- Nuevos: `claude-sonnet-5-5` (caché a 0,05×) y `claude-haiku-5-5`, con tramo
  `long_context` (> 100 000 tokens de entrada por petición) que `ledger.py`
  aplica por petición; fast mode de Opus 4.8 publicado (2×).

### Sesiones largas
- Canario de contexto al principio de `CLAUDE.md`: el orquestador empieza cada
  respuesta con «Diego ·»; si deja de hacerlo, el contexto está saturado.
  `caveman` respeta el prefijo. Los subagentes no cargan `CLAUDE.md`
  (`omitClaudeMd: true`), así que sus informes no cambian.
- Skill `/new-session` (solo humana): genera un prompt de traspaso con lo que
  solo existe en la conversación y lo guarda en `.claude/handoff/` (fuera de
  git). El guard deja escribir ahí a la sesión principal, no a los subagentes;
  `Bash(date *)` preaprobado.

### Estructura
- El bundle mínimo vive en `HARNESS/` y los manuales humanos en
  `INSTRUCCIONES/` (fuera de lo que se copia a un proyecto): el orquestador y
  el explorer ya no cargan ni leen ~200 KB de documentación del harness.

## 0.5.0

Integra las mejoras de `HARNESS_REFERENCE.md` adaptadas a Claude Code, corrige
los defectos del bundle generado por harness-cli 0.4.0 y añade control de costes
y defensas de seguridad deterministas.

### Contratos y flujo
- Máquina de estados canónica en `contracts/workflow.toml` (fases, eventos,
  actores y guards ejecutables). Un solo gate humano obligatorio (GATE#1).
- Motor de estado `tools/feature.py`: único escritor de `state.yaml`; aplica el
  contrato, ejecuta las guards y sincroniza `feature_list.json` y `event.log`.
- Veredictos estructurados (`PASS`, `FAIL_REPAIRABLE`, `FAIL_NONREPAIRABLE`,
  `BLOCKED_TOOLING`) y un único repair automático.
- La especificación se congela al aprobar GATE#1 (`SDD/spec.lock.json`); el
  builder no puede cambiarla y la aceptación solo se ejecuta sobre la spec aprobada.
- `blocked` deja de ser un callejón sin salida: salidas humanas explícitas
  (`replan`, `retry_*`, `cancel`).
- Reviewer en un único pase (revisión + verificación + veredicto); desaparece
  GATE#2, que aprobaba código antes de conocer si pasaba la aceptación.

### Herramientas (stdlib, Python 3.9+)
- `validate_harness.py`: validador determinista del bundle y de cada feature,
  incluida la trazabilidad FR → tarea → check.
- `run_acceptance.py`: runner real (antes era un stub que devolvía éxito).
- `ledger.py`: registro automático de cada subagente (ID runtime, modelo,
  tokens, coste) vía hook `SubagentStop` e informe de coste por feature.
- `guard.py`: hook `PreToolUse` contra prompt injection y violaciones de propiedad.
- Tests en `.claude/tests/`.

### Agentes y skills
- Agentes reescritos: modelo y esfuerzo explícitos, `omitClaudeMd`, sin
  herramientas de red, tope de turnos, skills precargadas, informe de retorno
  estructurado y cláusula anti-inyección. El explorer ya puede escribir su
  artefacto; el registro refleja el flujo real.
- Skills nuevas: `feature-cost`, `acceptance-criteria`, `test-driven-development`,
  `secure-code-review`, `feature-kickoff`, `feature-resume`, `harness-doctor`,
  `project-bootstrap`, `sdd-feature-planning`, `systematic-debugging`,
  `verification-before-completion`, `eval-driven-development`, `plugin-eval`,
  `caveman`, `ponytail` y `skill-creator` (oficial de Anthropic).
- Comandos humanos `/approve` y `/reject` (el modelo no puede invocarlos).

### Seguridad (revisión adversarial)
- `guard.py` reescrito por listas blancas: un solo comando de una línea,
  rutas sin distinguir mayúsculas (discos de Windows y macOS), `.git/` e
  instrucciones protegidos a cualquier profundidad, especialistas confinados a
  su informe, git de solo lectura para subagentes (sin `--output` ni
  `--no-index`), sin red externa, instalaciones ni secretos, designer de solo
  lectura, detección de escrituras indirectas y fallo en cerrado.
- La firma humana de GATE#1 resiste ofuscaciones (comillas, abreviaturas).
- La aprobación exige la misma spec que se presentó (`spec_as_presented`) y
  los comandos de aceptación se listan al humano; los sensibles nunca los
  aprueba yolo y cualquier referencia a secretos se rechaza.
- Las guards de runtime verifican el transcript real del subagente.
- El runner no hereda secretos del entorno y redacta la evidencia.
- Presupuesto: solo registros de subagentes y bloqueo si hay uso sin precio.
- `caveman` y `ponytail` pasan a invocación solo humana.

### Correcciones
- `bootstrap/init.sh` inicializaba git dentro de `.claude/bootstrap/`.
- Referencias a funciones y comandos inexistentes (`core.state.*`,
  `core.sdd.*`, `harness events|mode|doctor...`) y a agentes que no existen.
- MCP documentado en `.mcp.json` (Claude Code no lee `.claude/mcp/servers.json`).
- Plantillas de agente y skill fuera de las carpetas de descubrimiento.
- Eliminados duplicados que derivaban (`.claude/HARNESS.md`, `docs/flow-tables.md`,
  `docs/concepts.md`) y el stub `check_traceability.py` (integrado en el validador).

## 0.4.0

Bundle `simple` / perfil `clean` generado por harness-cli 0.4.0.
