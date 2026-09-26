---
name: feature-cost
description: Controla el gasto por feature del harness con datos reales de tokens - informe por agente y modelo, estado frente al presupuesto y palancas para reducirlo. Úsala al iniciar, reanudar, presentar GATE#1 o cerrar una feature; cuando el humano pregunte cuánto cuesta o ha costado algo ("coste", "gasto", "tokens", "presupuesto", "budget", "cuánto llevamos"); y siempre que una transición falle con BUDGET_EXCEEDED o el estado muestre BUDGET_WARN.
argument-hint: "[FEATURE-ID]"
---

# Feature cost

## Qué se mide y cómo

- **Subagentes** (la mayor parte del gasto): el hook `SubagentStop` ejecuta
  `ledger.py hook` al terminar cada subagente. Si el prompt empieza con la
  cabecera `FEATURE_ID: <ID>`, registra en `.claude/state/<ID>/event.log` un
  evento `subagent_stop` con el ID runtime, el modelo y los tokens de su
  transcript por categoría: input, output, escritura de caché (5 min y 1 h) y
  lectura de caché. Es automático y determinista: nadie escribe estos datos a mano.
- **Orquestador** (sesión principal): estimación heurística. Cuenta los turnos
  cuyo prompt humano o llamadas a herramientas mencionan el ID de la feature;
  si un turno menciona varias features, su coste se reparte entre ellas. Solo
  aparece en los informes: el límite de presupuesto se evalúa con los
  registros de subagentes, que son deterministas.
- **Precio**: tabla `[cost.pricing]` de `.claude/harness.toml` (USD por millón
  de tokens, clave = modelo sin sufijo de fecha; fast mode con su multiplicador).
  Es el coste equivalente a precios de API: con un plan de suscripción no es lo
  facturado, pero sirve para comparar features y detectar desvíos. Un modelo
  sin precio se marca como tal; nunca se inventa.

## Cuándo la usa el orquestador

1. **Al iniciar o reanudar**: `python3 .claude/tools/feature.py status <ID>`
   muestra el coste acumulado y el estado del presupuesto.
2. **En cada transición**: las que lanzan trabajo nuevo tienen la guard
   `within_budget`; si se supera el límite, la transición se rechaza con
   `BUDGET_EXCEEDED` antes de gastar más.
3. **En la línea de preview** tras cada fase: incluye el coste acumulado.
4. **En GATE#1**: añade al resumen el coste hasta el diseño y el presupuesto
   restante; es información para que el humano decida.
5. **Al archivar o cancelar**: `feature.py` congela el cálculo en `cost.json`.
   Muestra el informe final con `python3 .claude/tools/ledger.py cost <ID>`.

## Reglas de presupuesto

| Estado | Significado | Acción |
| --- | --- | --- |
| `BUDGET_OK` | por debajo de `warn_usd` | continúa |
| `BUDGET_WARN` | supera `warn_usd` | continúa y avisa al humano con el coste y lo que queda de flujo |
| `BUDGET_EXCEEDED` | supera el límite (`budget_usd` de la feature o `limit_usd`) | para; el humano amplía `budget_usd` en `feature_list.json` o cancela |

Ampliar el presupuesto es una decisión humana: no lo hagas por tu cuenta.

## Informe para el humano

```bash
python3 .claude/tools/ledger.py cost              # todas las features
python3 .claude/tools/ledger.py cost <ID>         # desglose por agente
python3 .claude/tools/ledger.py cost <ID> --json  # datos completos (por modelo y categoría)
python3 .claude/tools/ledger.py cost <ID> --live  # recalcula aunque exista cost.json
```

Presenta: total, desglose por agente, porcentaje del límite y una o dos
observaciones accionables (por ejemplo, "el 60 % del coste es lectura de caché
del orquestador: la sesión fue muy larga").

## Palancas para gastar menos sin perder calidad

1. **Alcance**: features pequeñas y bien delimitadas cuestan menos en todas las fases.
2. **Contexto**: `context.md` compacto evita que el designer y el builder
   re-exploren; el orquestador trabaja con los informes de retorno y
   `feature.py status`, sin releer todos los artefactos.
3. **Menos vueltas**: una aceptación precisa evita repairs; cada repair es un
   build y una verificación más.
4. **Modelo y esfuerzo por agente** (frontmatter de `.claude/agents/*.md`):
   p. ej. explorer con `haiku` en repositorios grandes y sencillos, o reviewer
   con `effort: medium` si la aceptación es muy determinista. Mide antes y después.
5. **Caché**: sin pausas largas entre turnos la caché sigue caliente; no edites
   `CLAUDE.md`, `HARNESS.md` ni `AGENTS.md` en mitad de una feature (invalidan
   la caché de todos los prompts).
6. **Fast mode**: duplica el precio en Opus; úsalo solo si la latencia importa.
7. **Skills**: `/skill-doctor` muestra cuánto contexto consume cada skill;
   desactiva las que no uses.

## Diagnóstico

- Coste 0 con subagentes lanzados: el prompt no empezaba con la cabecera
  `FEATURE_ID`, el hook `SubagentStop` no está en `.claude/settings.json` o hay
  errores en `.claude/state/hook-errors.log` (skill `harness-doctor`).
- "Uso sin precio conocido": un modelo sin tarifa (o fast mode sin
  multiplicador) bloquea el trabajo nuevo, porque sin precio no hay control de
  gasto. Añade el modelo a `[cost.pricing.models]` con la tarifa oficial y
  actualiza `as_of`.
- `event.log` y `cost.json` los gestionan las herramientas; no los edites (el
  hook de seguridad lo impide).
