# Servidores MCP

[Model Context Protocol](https://modelcontextprotocol.io) permite a los agentes
hablar con servicios externos (GitHub, Postgres, Filesystem, Slack, etc.).

## Cómo configurar

1. Renombra `servers.json.example` a `servers.json`.
2. Edita `servers.json` con los servidores que necesites.
3. Tu cliente IA leerá esta configuración cuando arranque.

## Servidores recomendados por dominio

- **software**: github, filesystem, postgres-local.
- **infra**: terraform, aws, cloudflare.
- **content**: notion, slack, gdrive.

Consulta el [registry oficial de MCPs](https://github.com/modelcontextprotocol/servers) para más opciones.

## Ejemplo de servers.json

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "<tu-token>"
      }
    }
  }
}
```
