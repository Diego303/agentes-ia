# llm-gateway

[LiteLLM](https://docs.litellm.ai) como gateway entre los agentes y los proveedores de modelos.
Las aplicaciones usan el **SDK oficial de Anthropic** contra el endpoint `/v1/messages` del
gateway, sin capas de compatibilidad. El gateway centraliza lo que no debería repetir cada
aplicación:

| Responsabilidad | Dónde ([`litellm-config.yaml`](litellm-config.yaml)) |
| --- | --- |
| Claves de proveedor fuera de las apps | `api_key: os.environ/...`; las apps solo tienen la clave del gateway |
| Reintentos con backoff ante 429/5xx | `router_settings.num_retries` |
| Degradación Opus → Sonnet si el principal falla | `router_settings.fallbacks` |
| Tope de gasto | `litellm_settings.max_budget` (en memoria por réplica) |
| Embeddings de otro proveedor detrás de un alias | modelo `embeddings` → Voyage AI |
| Trazas enlazadas con las del agente | `callbacks: ["otel"]` |

Los nombres de modelo son los IDs oficiales (`claude-opus-5-5`, ...), así que la aplicación
no depende de alias propios del gateway.

## Verificado de punta a punta

Este config se probó con LiteLLM 1.106.3 real, delante de un mock de la API de Anthropic y
con el agente, MCP y A2A como procesos separados:

- `thinking: {type: adaptive}`, `output_config.effort` y las tools llegan intactos al
  proveedor (`drop_params: false`).
- La clave del gateway (`x-api-key`) se sustituye por la del proveedor. La del gateway nunca sale.
- Con el proveedor devolviendo 529 en Opus, hace 3 intentos y sirve la respuesta con
  Sonnet. El agente calcula el coste con el precio del modelo que respondió.

## Ejecutar en local

Con la imagen oficial (la misma que en Kubernetes):

```bash
docker run --rm -p 4000:4000 \
  -v "$PWD/llm-gateway/litellm-config.yaml:/etc/litellm/config.yaml:ro" \
  -e ANTHROPIC_API_KEY -e ANTHROPIC_API_BASE=https://api.anthropic.com -e LITELLM_MASTER_KEY=sk-gw-local \
  ghcr.io/berriai/litellm-non_root:v1.106.3 --config /etc/litellm/config.yaml --port 4000
```

O con pip: `pip install 'litellm[proxy]==1.106.3'` y
`litellm --config llm-gateway/litellm-config.yaml --port 4000`. Después:

```bash
LLM_GATEWAY_URL=http://localhost:4000 LLM_GATEWAY_KEY=sk-gw-local uv run opsagent
```

## En Kubernetes

El archivo se monta tal cual: `make k8s-config` crea el ConfigMap `llm-gateway-config` desde
`litellm-config.yaml` (no hay una segunda copia en los manifiestos) y
[`deploy/kubernetes/llm-gateway.yaml`](../deploy/kubernetes/llm-gateway.yaml) lo monta en
`/etc/litellm/config.yaml`. Las claves llegan del Secret `llm-gateway-secrets`.

## Límites y siguiente paso

- `max_budget` sin base de datos es un contador en memoria por réplica: una red de
  seguridad, no contabilidad. Para presupuestos y límites por agente o equipo, activa la
  base de datos de LiteLLM y emite una *virtual key* por consumidor.
- El fallback de LiteLLM cubre errores (caídas, cuota). Una negativa del modelo
  (`stop_reason: refusal`) es una respuesta 200: la gestiona el agente.
- En Kubernetes, el gateway es el único pod con salida a Internet (ver
  [`deploy/kubernetes/networkpolicies.yaml`](../deploy/kubernetes/networkpolicies.yaml)).
