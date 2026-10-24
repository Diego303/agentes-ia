# evals-and-benchmarks

Cómo se sabe si el agente funciona y si un cambio lo mejora. Hay cuatro niveles, del más
barato al más caro:

| Nivel | Qué mide | Coste | Cuándo |
| --- | --- | --- | --- |
| Tests (`uv run pytest`) | que el bucle, los guardrails y los protocolos hacen lo que dicen, con un modelo con guion | 0 | cada commit |
| Benchmarks offline (`opsagent-bench --check`) | recuperación (recall@3, MRR) y detector de inyección (precisión, recall) con umbrales | 0 | cada commit (CI) |
| Evals de punta a punta (`opsagent-evals`) | el agente real con el modelo real: trayectoria, hechos, seguridad | $ | semanal en CI y antes de cambiar modelo, prompt o tools |
| Juez LLM calibrado (`--judge`, `--calibrate`) | calidad semántica con rúbrica, solo si el juez coincide con humanos | $ | junto a las evals |

## Evals del agente

[`datasets/agent_tasks.yaml`](datasets/agent_tasks.yaml): diagnóstico, congelación de cambios,
guía de severidad, aprobación humana, inyección en los datos y fuera de alcance. Cada caso
se evalúa primero con graders deterministas ([`graders.py`](src/opsagent_evals/graders.py)):

- `tools_called` / `tools_not_called`: la **trayectoria**. Acertar la respuesta saltándose el
  change advisor sigue siendo un fallo, y una tool denegada no cuenta como ejecutada.
- `answer_any`: hechos que deben aparecer (grupos de sinónimos).
- `stop`, `pending_tool`, `tainted`: comportamiento del bucle y de los guardrails.

Solo si los deterministas pasan, el juez evalúa la rúbrica. Así no se paga un juez para
detectar fallos que un `if` ya ve.

```bash
uv run opsagent-evals --case diag-payments-5xx      # un caso
uv run opsagent-evals --judge --repeat 3            # pass^3: el caso pasa las 3 veces
uv run opsagent-evals --judge --output reports/latest.json --min-pass 0.85
```

`--repeat` mide fiabilidad: un agente que acierta 2 de cada 3 veces no está listo, aunque
la media lo parezca.

## Juez calibrado

Un juez LLM sin calibrar mide su propio criterio. [`judge_calibration.yaml`](datasets/judge_calibration.yaml)
tiene respuestas con veredicto humano, incluidas respuestas plausibles pero incorrectas
(datos inventados, que siguen la inyección). `--calibrate` calcula accuracy y kappa de
Cohen. Con kappa < 0,6 el juez no debería bloquear nada. El juez usa salida estructurada
(`messages.parse` con un modelo Pydantic) y trata la respuesta evaluada como dato.

## Añadir un caso

1. Parte de un fallo real o de una conversación de producción (anonimizada).
2. Escribe primero las expectativas deterministas. La rúbrica, solo para lo que no se
   puede comprobar con código.
3. Ejecuta `--case <id> --repeat 3` antes y después del cambio que quieres evaluar.

## CI

El job `python` ejecuta tests y benchmarks en cada push. El job `live-evals` corre los lunes
y bajo demanda (`workflow_dispatch` con `live_evals=true`): calibra el juez y ejecuta las
evals con `--repeat 2`. Usa el secreto `ANTHROPIC_API_KEY` de un *environment* protegido.
