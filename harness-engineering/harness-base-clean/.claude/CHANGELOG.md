# Changelog del bundle

La versión más reciente debe coincidir con `[harness].bundle_version` de
`harness.toml` (lo comprueba `validate_harness.py`).

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
