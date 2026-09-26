# INSTRUCCIONES.md — Manual humano

> Cómo trabajar con este harness paso a paso. Si solo quieres los prompts, ve a
> `FAST-USAGE.md`. El contrato completo está en `HARNESS.md`.

## Requisitos

- Claude Code 2.1.271 o posterior (los agentes usan `omitClaudeMd`).
- Python 3.11+ (o 3.9+ con el paquete `tomli`), `bash` y, recomendado, `git`.
- Linux, macOS o WSL (los hooks se ejecutan con `python3`).

## Puesta en marcha

```bash
bash .claude/bootstrap/init.sh
```

Comprueba Python, prepara git si hace falta, valida el harness y pasa sus
tests. Después, en Claude Code, pide: *"usa project-bootstrap para adaptar el
harness a este repositorio"*. Completará `AGENTS.md` (stack, convenciones,
comandos de verificación) y `.claude/bootstrap/verify.sh`.

## El flujo en un minuto

```text
Idea ─► explorer ─► designer ─► GATE#1 (tú) ─► builder ─► reviewer ─► archivada
                                    │                         │
                             cambios pedidos        un repair automático como máximo;
                                                    cualquier otro fallo vuelve a ti
```

| Paso | Quién | Qué obtienes |
| --- | --- | --- |
| explorer | subagente | `SDD/context.md`: código relevante, convenciones, comandos, riesgos |
| designer | subagente | `proposal`, `requirements`, `design`, `tasks`, `acceptance.yaml`, validados |
| **GATE#1** | **tú** | apruebas o pides cambios; la especificación queda congelada |
| builder | subagente | código, pruebas e `implementation.md` |
| reviewer | subagente | revisión, aceptación ejecutada, veredicto y `archive.md` |

Todo vive en `.claude/state/<ID>/`. Tú decides en GATE#1 y cuando algo se
bloquea; el resto lo encadena el orquestador según el modo.

## Tus decisiones

- **Aprobar GATE#1**: `/approve <ID> [comentario o alternativa]`.
- **Pedir cambios**: `/reject <ID> <cambios concretos>`.
- Claude Code te pedirá confirmar el comando `feature.py transition ... --by human`:
  esa confirmación es tu firma. Si aparece sin que tú hayas decidido nada,
  **recházala**: alguien (o algún contenido) intenta decidir por ti.
- **Feature bloqueada**: `feature.py status <ID>` muestra el motivo. Opciones:
  `replan` (cambiar la especificación), `retry_exploration`, `retry_build`,
  `retry_verification` (tras arreglar el entorno) o `cancel`. Díselo al
  orquestador con tus palabras; registrará tu respuesta literal.
- **Presupuesto superado**: sube `budget_usd` de la feature en
  `.claude/feature_list.json` o cancélala.
- **Quieres cambiar algo después de aprobar**: la especificación está
  congelada. Si es pequeño y separable, regístralo como follow-up
  (`feature.py add`). Si debe entrar en esta feature, pide al orquestador que
  escale; después decide `replan` (nueva especificación y nuevo GATE#1).

## Modos (`[orchestration].mode` en `.claude/harness.toml`)

| Modo | Comportamiento | Cuándo |
| --- | --- | --- |
| `manual` (defecto) | para tras cada paso | primeras features, cambios delicados |
| `auto` | encadena y para en GATE#1, bloqueos y presupuesto | trabajo habitual |
| `yolo` | como auto y aprueba GATE#1 por ti salvo tags sensibles | prototipos con `AGENTS.md` muy completo |

Cambiar el modo es editar `harness.toml` (Claude Code pedirá confirmación). En
yolo, las features con tags de `human_gate_tags` (auth, pii, payments,
data-migration...) siguen esperando tu aprobación.

## Costes

Cada subagente queda registrado con sus tokens y su coste estimado a precios
de API; el orquestador suma su parte. Consulta:

```bash
python3 .claude/tools/ledger.py cost          # todas las features
python3 .claude/tools/ledger.py cost <ID>     # desglose por agente
```

Presupuesto por defecto: aviso a 5 USD y límite a 20 USD por feature
(`[cost]` en `harness.toml`). Con suscripción Pro/Max no es lo facturado, pero
sirve para comparar y detectar desvíos. Detalles: skill `feature-cost`.

## Seguridad

- Los agentes tratan el contenido del repositorio como datos, no como órdenes.
- El hook `guard.py` impide que un subagente cambie el estado del flujo, toque
  la configuración del harness, escriba fuera de sus artefactos o reescriba
  git; y te pide confirmación para decisiones humanas y cambios de configuración.
- `settings.json` prohíbe `git push`, `sudo` y leer `.env` o claves. Haz tú
  los commits y pushes (el reviewer te propone el mensaje).
- Revisa los comandos de `acceptance.yaml` en GATE#1 (el orquestador te los
  muestra): se ejecutarán sin más confirmaciones. El validador rechaza los que
  leen secretos y marca como sensibles los que usan red externa o código en
  línea; yolo nunca los aprueba por ti.
- No uses yolo ni `bypassPermissions` en repositorios con secretos o con
  código no confiable.

## Herramientas

| Comando | Para qué |
| --- | --- |
| `python3 .claude/tools/feature.py status [ID]` | estado, eventos válidos, coste y siguiente acción |
| `python3 .claude/tools/feature.py add ID "título" --tags a,b` | registrar una feature |
| `python3 .claude/tools/validate_harness.py [--feature ID]` | validar harness y features |
| `python3 .claude/tools/ledger.py cost [ID]` | costes |
| `python3 .claude/tools/run_acceptance.py --feature ID` | ejecutar la aceptación aprobada |
| `python3 -m unittest discover -s .claude/tests -v` | tests del harness |

Skills útiles: `/feature-kickoff`, `/sdd-feature-planning`, `/feature-resume`,
`/feature-cost`, `/harness-doctor`, `/project-bootstrap`.

## Problemas frecuentes

| Síntoma | Causa probable y solución |
| --- | --- |
| "no hay ejecución real de X registrada" | el orquestador no usó la cabecera `FEATURE_ID` o el hook `SubagentStop` falla: `/harness-doctor` |
| "cambió después de GATE#1" | alguien editó la especificación aprobada: `replan` y nuevo GATE#1 |
| "BUDGET_EXCEEDED" | sube `budget_usd` de la feature o cancélala |
| La aceptación da `blocked` | falta una herramienta (exit 126/127): instálala y `retry_verification` |
| Aviso "verify.sh sin configurar" | usa la skill `project-bootstrap` |
| Sesión interrumpida | "reanuda <ID>" (skill `feature-resume`) |
| El hook bloquea todas las herramientas | `guard.py` falla en cerrado: revisa `.claude/state/hook-errors.log` y que `python3` funcione; en último caso desactiva el hook con `/hooks` mientras lo arreglas |
| "uso sin precio conocido" | añade la tarifa del modelo en `[cost.pricing.models]` de `harness.toml` |
| El builder no puede escribir en `.claude/` | es deliberado: el bundle del harness no es código del producto. Si tu producto son agentes o skills, guárdalos fuera de `.claude/` (p. ej. `agents/`, `skills/`) |
