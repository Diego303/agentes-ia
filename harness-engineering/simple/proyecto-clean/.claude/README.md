# .claude/ — Bundle operativo del harness

Esta carpeta contiene todo lo que el harness necesita para funcionar:

- `HARNESS.md` — copia del contrato (también en raíz; aquí para que el bundle sea autocontenido).
- `harness.toml` — configuración del proyecto.
- `feature_list.json` — cola de features.
- `settings.json` — configuración de cliente IA (Claude Code, etc.).
- `bootstrap/` — scripts init.sh y verify.sh.
- `state/` — estado de cada feature en curso (state.yaml + SDD/).
- `agents/` — agentes oficiales del harness + agent-registry.yaml + espacio para agentes custom.
- `skills/` — skills auxiliares (no son agentes; son procedimientos invocables).
- `mcp/` — configuración de servidores MCP.
- `commands/` — slash commands del cliente IA (Claude Code los descubre automáticamente).
- `hooks/` — hooks pre/post tool use.
- `docs/` — documentación interna del harness.
- `tools/` — utilidades auxiliares.

**NO edites archivos aquí a mano** salvo:

- `state/<feature>/state.yaml` en casos de recovery manual.
- `agents/<custom-agent>/SKILL.md` si añades agentes propios.
- `skills/<custom-skill>/SKILL.md` si añades skills propias.
- `mcp/servers.json` (renombra de `servers.json.example`) si configuras MCP.
- `harness.toml` para cambiar configuración (o usa `harness mode`).

Para reglas de tu proyecto: edita `AGENTS.md` en la raíz.
