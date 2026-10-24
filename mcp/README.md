# mcp — servidor MCP base

Base para MCP servers propios, con un ejemplo de operaciones de plataforma (datos ficticios):
- tools asíncronas organizadas por carpetas;
- logging estructurado de cada llamada;
- autenticación OAuth 2.1 como resource server;
- Streamable HTTP sin estado;
- tests sin red.

SDK de Python [`mcp`](https://modelcontextprotocol.io) 2.3. Lo usa el
[agente de referencia](../reference-agent/).

## Estructura

```text
mcp/
├── pyproject.toml
├── src/ops_mcp/
│   ├── __main__.py            arranque: Streamable HTTP o --stdio
│   ├── server.py              build_server(): dependencias, tools y /healthz
│   ├── app.py                 app ASGI: HTTP sin estado y protección contra DNS rebinding
│   ├── auth.py                verificadores de tokens (JWT con JWKS o estáticos)
│   ├── config.py              configuración del proceso desde el entorno
│   ├── resources/             datos de ejemplo: servicios, despliegues y runbooks
│   └── integrations/
│       ├── common/            lo que comparten las tools
│       │   ├── deps.py        ToolDeps: lo que recibe cada tool al registrarse
│       │   ├── catalog.py     acceso a los datos (interfaz asíncrona)
│       │   ├── concurrency.py run_blocking y gather_limited
│       │   ├── logging.py     logger JSON a stderr y decorador logged_tool
│       │   ├── scopes.py      scopes OAuth y require_scope
│       │   ├── errors.py      errores previstos (ToolError)
│       │   └── models.py      modelos de salida compartidos
│       └── tools/
│           ├── __init__.py          registro: TOOLS y register_tools()
│           ├── service_status.py    simple: un archivo
│           ├── platform_overview.py simple
│           ├── deployments.py       simple
│           ├── runbooks/            compleja: index.py, models.py, tool.py
│           └── incidents/           compleja: store.py, models.py, tool.py
└── tests/
```

Una **tool simple** es un módulo. Una **tool compleja** (índice, almacén, varios modelos) es
una carpeta con sus piezas. Todas exponen `register(server, deps)`.

## Tools de ejemplo

| Tool | Tipo | Efectos | Qué muestra |
| --- | --- | --- | --- |
| `get_service_status(service)` | simple | lectura | parámetro con los valores válidos en el esquema y error accionable |
| `get_platform_overview()` | simple | lectura | consulta en abanico con `gather_limited` |
| `list_recent_deployments(service, limit)` | simple | lectura | límites en los parámetros |
| `search_runbooks(query, k)` | compleja | lectura | RAG con [`rag-and-memory`](../rag-and-memory/) y una librería síncrona en un hilo |
| `create_incident(service, severity, summary)` | compleja | **sí** (`ops:write`) | scope por tool y estado compartido con `asyncio.Lock` |

Criterios de diseño:

- **Pocas tools** cuya descripción dice *cuándo* usarlas.
- **Entradas acotadas** (`Literal`, rangos, servicios válidos en el esquema).
- **Salida estructurada** con modelos Pydantic.
- **Anotaciones** `read_only_hint` y `destructive_hint` para que el cliente decida qué pedir
  aprobar.
- **Errores previstos** con `ToolError` y un mensaje que dice cómo corregirse. Los
  inesperados no llegan al modelo: se registran y se devuelve una referencia (`call_id`).

Uno de los mensajes de despliegue de ejemplo contiene una prompt injection a propósito,
para las evals de seguridad.

## Concurrencia: tools asíncronas

Varios agentes pueden llamar a la misma tool a la vez. El servidor atiende cada petición en
una tarea del bucle de eventos:

- **Las tools son `async def`.** Mientras una espera (red, disco, otra API), el bucle atiende
  al resto. Mil llamadas esperando no ocupan mil hilos.
- **Las tools síncronas no escalan igual.** El SDK las ejecuta en un pool de 40 hilos, y con
  más llamadas lentas que hilos, el resto hace cola.
- **Nada que bloquee dentro de una tool asíncrona.** Un `time.sleep`, un `requests.get` o un
  cálculo largo congelan el servidor entero mientras duran.

| Situación | Qué usar | Ejemplo |
| --- | --- | --- |
| E/S con cliente asíncrono (httpx, asyncpg, aiobotocore) | `await` directamente | `catalog.py` (interfaz para fuentes reales) |
| Varias consultas independientes | `gather_limited(..., limit=8)`: a la vez, con un máximo en vuelo | `platform_overview.py` |
| Librería síncrona o CPU | `await run_blocking(fn, ...)`: va a un hilo de un pool limitado (8) | `runbooks/tool.py` |
| Estado compartido que se modifica | `asyncio.Lock` alrededor de leer y escribir | `incidents/store.py` |

`tests/test_mcp_async.py` lo comprueba:
- seis llamadas de 0,5 s tardan lo que una;
- cuatro búsquedas bloqueantes van en paralelo y el servidor responde a otra tool mientras
  tanto;
- diez incidentes simultáneos reciben IDs distintos.

El servidor no guarda sesiones (`stateless_http`), así que también escala en horizontal:
cualquier réplica atiende cualquier petición.

## Logging

`integrations/common/logging.py`:

- Todo va a **stderr**. Con el transporte stdio, stdout es el canal del protocolo.
- Por defecto, **JSON**, una línea por evento, listo para el colector de logs.
  `MCP_LOG_FORMAT=text` para desarrollo y `MCP_LOG_LEVEL` para el nivel.
- `@logged_tool` registra cada llamada como un evento `tool.call` con estos campos:
  - `tool`, `call_id` y `client_id`;
  - `duration_ms`;
  - `outcome`: `ok`, `tool_error` o `error`;
  - el `trace_id` de OpenTelemetry, para saltar del log a la traza.

  Los argumentos solo aparecen en DEBUG.
- En cada módulo, `log = get_logger(__name__)`. Los logs de uvicorn salen con el mismo
  formato.

```json
{"ts": "2026-10-24T19:27:59.345+00:00", "level": "INFO", "logger": "ops_mcp.tools", "msg": "tool.call", "tool": "get_platform_overview", "call_id": "8bd86783f27d", "client_id": "ops-agent", "trace_id": "856fed8949d86ec71734d7aa7eff58ef", "outcome": "ok", "duration_ms": 0.3}
```

## Autenticación

El servidor es un *resource server* OAuth 2.1 según la especificación de autorización de
MCP:
- publica `/.well-known/oauth-protected-resource`;
- responde 401 con `WWW-Authenticate`;
- valida que el token se emitió para este recurso (`validate_token_resource`).

El transporte exige `ops:read` para cualquier llamada. Las tools con efectos piden además
`ops:write` con `require_scope`.

| Modo | Variables | Uso |
| --- | --- | --- |
| JWT | `MCP_JWKS_URL`, `MCP_ISSUER_URL`, `MCP_RESOURCE_URL` | producción con un IdP (Entra ID, Keycloak): firma, emisor, audiencia y caducidad |
| Tokens estáticos | `MCP_TOKENS` (JSON token → client_id + scopes), `MCP_ISSUER_URL`, `MCP_RESOURCE_URL` | tráfico interno sin IdP y desarrollo |
| Sin auth | `MCP_AUTH_DISABLED=true` | solo local; el servidor avisa al arrancar |

Sin configuración no arranca: falla en cerrado. `MCP_ALLOWED_HOSTS` activa la protección
contra DNS rebinding; en Kubernetes, pon el nombre corto y el FQDN del Service.

## Ejecutar

```bash
uv run ops-mcp --stdio                    # para un cliente local que lo lanza como subproceso
MCP_AUTH_DISABLED=true uv run ops-mcp     # Streamable HTTP en :8000/mcp
uv run pytest mcp/tests                   # tests, sin red
```

Para explorarlo a mano, conecta el
[MCP Inspector](https://github.com/modelcontextprotocol/inspector) a
`http://localhost:8000/mcp`.

El SDK emite un span OpenTelemetry por cada `tools/call` y propaga `traceparent` en `_meta`,
así que las llamadas aparecen dentro de la traza del agente.

## Añadir una tool

1. ¿La necesita el modelo o es una API para humanos? Una tool por intención, no por
   endpoint.
2. Crea `integrations/tools/<nombre>.py` (o una carpeta si tiene varias piezas) con
   `register(server, deps)`, siguiendo `service_status.py`:
   - la función es `async def`;
   - lleva `@logged_tool(NAME)` debajo de `@server.tool(...)`;
   - la descripción dice cuándo usarla;
   - los parámetros tienen tipos cerrados y límites.
3. Añade su `register` a `TOOLS` en `integrations/tools/__init__.py`.
4. Si tiene efectos:
   - `read_only_hint=False`;
   - `require_scope(WRITE_SCOPE, ...)`;
   - una regla `side_effect=True` en la política del agente.
5. Test con `Client(build_server())` en memoria y, si toca la autenticación, por HTTP.
6. Lo nuevo que compartan varias tools va a `integrations/common/`.
