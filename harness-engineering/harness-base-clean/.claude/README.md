# .claude/ — Bundle operativo del harness

| Ruta | Contenido | ¿Se edita? |
| --- | --- | --- |
| `harness.toml` | modo, tags de gate humano, presupuestos y precios | sí (pide confirmación) |
| `contracts/workflow.toml` | máquina de estados canónica | solo cambiando también validador y tests |
| `agents/` | explorer, designer, builder, reviewer y `agent-registry.yaml` | con criterio; valida después |
| `skills/`, `commands/` | skills (procedencia en `skills/README.md`) y `/approve`, `/reject` | sí |
| `templates/` | esquemas de estado, aceptación, veredicto y repair; plantillas de agente y skill | con criterio |
| `tools/` | `feature.py`, `validate_harness.py`, `run_acceptance.py`, `ledger.py`, `guard.py` | solo con tests |
| `tests/` | tests de las herramientas | sí |
| `settings.json` | permisos y hooks (`guard.py`, `ledger.py`) | con cuidado: es la capa de seguridad |
| `feature_list.json` | cola de features | con `feature.py add`; el estado lo sincroniza el motor |
| `state/<ID>/` | memoria de cada feature | **no a mano**: lo escriben agentes y herramientas |
| `bootstrap/` | `init.sh` y `verify.sh` (regresión del proyecto) | `verify.sh`, sí |
| `docs/` | arquitectura y cómo extender | sí |
| `mcp/` | ejemplo de configuración MCP (`.mcp.json` va en la raíz) | sí |

Reglas del proyecto: `AGENTS.md` en la raíz. Contrato: `HARNESS.md`.
Tras cualquier cambio: `python3 .claude/tools/validate_harness.py` y
`python3 -m unittest discover -s .claude/tests -v`.
