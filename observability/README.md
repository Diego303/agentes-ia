# observability

Trazas, métricas y coste del sistema con OpenTelemetry y las convenciones semánticas GenAI
(`gen_ai.*`). Cada servicio llama a `setup_telemetry("<servicio>")` y todo lo demás sale
de los SDK o de dos context managers.

## Una petición, una traza

```text
POST /v1/chat                                   ops-agent (ASGI)
└─ invoke_agent ops-assistant                   gen_ai.conversation.id, tokens totales, opsagent.cost_usd, stop
   ├─ anthropic.messages.create                 SDK de Anthropic: modelo, tokens   ──► llm-gateway (callback otel)
   ├─ execute_tool get_service_status           gen_ai.tool.name, gen_ai.tool.type=extension
   │  └─ MCP send tools/call get_service_status SDK de MCP: traceparent en _meta
   │     └─ tools/call get_service_status       ops-mcp (span de servidor, misma traza)
   └─ execute_tool consult_change_advisor
      └─ POST /                                 httpx ──► change-advisor (ASGI, misma traza)
```

Verificado de punta a punta: el `trace_id` del span `invoke_agent` aparece en los spans de
ops-mcp y de change-advisor, que corren como procesos separados.

| Quién emite | Qué |
| --- | --- |
| SDK de Anthropic (2.x) | un span por llamada al modelo, con atributos GenAI y `traceparent` hacia el gateway |
| SDK de MCP (2.x) | spans de cliente y servidor por `tools/call`, con el contexto propagado en `_meta` |
| [`genai.py`](src/opsagent_telemetry/genai.py) | `invoke_agent` y `execute_tool`, eventos de guardrails, métricas `gen_ai.client.token.usage`, `opsagent.llm.cost` y `opsagent.guardrail.events` |
| instrumentación `httpx` y ASGI | propagación hacia y desde el change advisor y la API del agente |
| LiteLLM | sus propios spans (reintentos, fallback) |

[`pricing.py`](src/opsagent_telemetry/pricing.py) tiene los precios oficiales (con caché y
el tramo de contexto largo de Haiku). Un modelo sin precio devuelve `None`, no 0, para que
nunca parezca gratis.

## Configuración

Solo variables estándar:

- `OTEL_EXPORTER_OTLP_ENDPOINT`: OTLP/HTTP, en Kubernetes el collector.
- `OTEL_TRACES_EXPORTER=console`: para ver los spans en local.
- `OTEL_SERVICE_NAME`.

## Collector

[`collector/otel-collector.yaml`](collector/otel-collector.yaml) recibe OTLP, borra los
atributos con prompts y respuestas (aunque un servicio active el modo *content*), envía las
trazas a cualquier backend OTLP (Jaeger en local) y expone las métricas para Prometheus en
`:8889`. Lo despliega [`deploy/kubernetes`](../deploy/kubernetes/).

```bash
kubectl -n opsagent port-forward svc/jaeger 16686   # en kind → http://localhost:16686
```

## Qué mirar

- **Coste por conversación y por tool**: `opsagent.cost_usd` en `invoke_agent`, y la métrica
  `opsagent.llm.cost` por modelo.
- **Calidad operativa**: `opsagent.stop_reason` (`budget` o `refusal` frecuentes indican
  prompts o límites mal ajustados) y `opsagent.guardrail.events` por tipo y acción.
- **Latencia**: el span más largo de la traza suele ser el modelo; si es una tool, ahí está
  el cuello de botella.
