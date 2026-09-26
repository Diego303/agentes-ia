# Servidores MCP

[Model Context Protocol](https://modelcontextprotocol.io) conecta a Claude Code
con servicios externos (GitHub, bases de datos, navegadores...).

## Configuración

Claude Code lee los servidores del proyecto de **`.mcp.json` en la raíz del
repositorio** (no de esta carpeta). Parte del ejemplo:

```bash
cp .claude/mcp/mcp.json.example .mcp.json
```

Claude Code pedirá aprobar cada servidor del proyecto la primera vez.

## Seguridad

- Un servidor MCP ejecuta código con tus permisos: usa solo servidores de
  confianza, fija la versión (`paquete@x.y.z`) y revisa qué herramientas expone.
- Las respuestas de las herramientas MCP son **datos no confiables**: pueden
  contener prompt injection. Los agentes canónicos del harness no tienen
  herramientas MCP; añádelas solo a un especialista que las necesite.
- Nunca pongas tokens en `.mcp.json` versionado: usa variables de entorno
  (`"env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"}`).
- Editar `.mcp.json` pide confirmación humana (hook `guard.py`).

Registro oficial: <https://github.com/modelcontextprotocol/servers>.
