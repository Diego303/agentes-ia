# Extender el harness

Puedes añadir tres tipos de extensiones sin tocar el harness oficial.

## Añadir un agente custom

1. Crea `<bundle>/agents/<mi-agente>/SKILL.md` con frontmatter YAML
   (campos: `name`, `description`, `tools`, `model`) y las cinco
   secciones del contrato.
2. Ejecuta `harness regenerate-registry` para que aparezca en
   `agent-registry.yaml`.

Tu agente puede ser invocado desde el flujo (en una fase opcional) o
on-demand desde un prompt.

## Añadir una skill custom

1. Crea `<bundle>/skills/<mi-skill>/SKILL.md` con frontmatter
   (`name`, `description`, `allowed-tools`) y un cuerpo descriptivo.
2. Cualquier agente puede leerla cuando la necesite.

## Añadir un servidor MCP

1. Renombra `<bundle>/mcp/servers.json.example` a `servers.json`.
2. Edita el JSON añadiendo tu servidor. Consulta el [registry oficial
   de MCPs](https://github.com/modelcontextprotocol/servers).
3. Reinicia tu cliente IA para que cargue la configuración.
