# 0003 · Tools en un servidor MCP stateless con OAuth 2.1 por scopes

**Estado**: aceptada

## Contexto

Las tools de operaciones las usarán este agente y otros: IDEs con MCP, otros agentes de la
plataforma.

## Decisión

Servidor MCP (SDK `mcp` 2.3) por Streamable HTTP en modo stateless con respuestas JSON. La
autorización sigue la especificación de MCP: resource server OAuth 2.1, metadatos de recurso
protegido, validación de audiencia, scope `ops:read` para todo y `ops:write` para efectos.
Tokens JWT del IdP en producción y tokens estáticos para tráfico interno y desarrollo.
Protección contra DNS rebinding con lista de `Host`.

## Alternativas

- **Tools dentro del agente**. Más simple, pero no se reutilizan y mezclan permisos.
- **API REST propia**. Cada cliente tendría que adaptarla; MCP es el estándar que ya hablan
  los clientes.
- **Sesiones con estado**. Necesarias solo para notificaciones del servidor o elicitación;
  el modo stateless permite escalar horizontalmente sin afinidad.

## Consecuencias

- Cualquier réplica atiende cualquier petición (HPA).
- La autorización por scopes vive en el servidor: aunque el agente se equivoque, sin
  `ops:write` no hay efectos.
