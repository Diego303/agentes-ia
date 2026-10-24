# Caso de estudio: el harness en proyectos reales

El harness base se ha usado en dos proyectos propios mediante bundles derivados (0.6.0 y
0.7.0) que añaden especialistas y reglas de cada producto sin tocar el core (máquina de
estados, motor, guardias y ledger). Las correcciones genéricas que surgieron allí se
llevaron de vuelta al base en la versión 0.8.0.

| Proyecto | Qué es | Stack |
| --- | --- | --- |
| **struo** | App de escritorio de apuntes con repetición espaciada | Tauri (Rust) + frontend web |
| **avizor** | Copilot local de análisis de inversión | Python, FastAPI, PostgreSQL + pgvector, LangGraph |

Aquí solo se publican métricas agregadas, sin código ni especificaciones de ninguno de
los dos. El repositorio de struo todavía es privado.

## Métricas

Generadas con el propio harness, leyendo solo el estado de cada feature:

```bash
python3 .claude/tools/feature.py metrics --state-dir <repo>/.claude/state
```

| Métrica | struo | avizor |
| --- | ---: | ---: |
| Features que pasaron por el flujo | 36 | 6 |
| Archivadas | 36 | 5 (1 en GATE#1) |
| PASS en la primera verificación | 22/36 (61 %) | 3/5 (60 %) |
| Features que necesitaron el repair automático | 13 | 1 |
| GATE#1 presentados / con cambios pedidos | 41 / 1 | 7 / 0 |
| Features bloqueadas alguna vez (decisión humana) | 8 | 1 |
| Ejecuciones de subagentes | 316 | 69 |
| Coste por feature: mediana / p90 | 13,52 $ / 32,07 $ | 40,72 $ / 83,26 $ |
| Coste total | 590,46 $ | 213,41 $ |
| Tiempo de ciclo, de inicio a archivado: mediana | 3,4 h | 6,4 h |

Los costes son estimaciones a precio de lista de la API, calculadas por el hook
`SubagentStop` desde los tokens reales de cada transcript. No incluyen al orquestador.

## Qué dicen los datos

- **El repair único basta.** Cuatro de cada diez features fallan la primera verificación,
  y casi todas se arreglan con el único repair automático. Las 8 de struo que acabaron en
  `blocked` volvieron al flujo con una decisión humana explícita (replan o reintento). No
  hizo falta subir el límite de repairs, que es justo lo que pide `HARNESS.md` §14 antes de
  añadir complejidad.
- **Hay que vigilar GATE#1.** 40 de 41 especificaciones se aprobaron sin cambios. Puede ser
  buen diseño o aprobación sin leer. La siguiente métrica útil es el tiempo que pasa cada
  especificación en `gate1_pending`.
- **El coste se explica por el dominio.** Avizor cuesta unas 3 veces más por feature: más
  especialistas por feature (seguridad, arquitectura, honestidad) y features más grandes.
  Medirlo por agente (`ledger.py cost <ID>`) es lo que permite decidir qué especialista
  compensa.

## Qué volvió al base (0.8.0)

Del uso real salieron fallos y endurecimientos que no eran específicos del producto:

- El lock se marca obsoleto por inactividad, no por antigüedad. `retry_exploration`
  reinicia el gate. El aviso de presupuesto salta antes del límite.
- El guard analiza la shell respetando comillas y heredocs. El reviewer y los
  especialistas son de solo lectura también por Bash. Se bloquea la lectura de secretos
  con Read/Grep/Glob.
- Regresión obligatoria y checks exigidos por tag. Los especialistas se seleccionan de
  forma determinista por tags y por las rutas que cambian.
- Precios por tramo de contexto largo. Los agentes usan el ID de modelo completo para que
  un cambio de alias no deje el uso sin precio.

El detalle está en [`../harness-base/HARNESS/.claude/CHANGELOG.md`](../harness-base/HARNESS/.claude/CHANGELOG.md).
