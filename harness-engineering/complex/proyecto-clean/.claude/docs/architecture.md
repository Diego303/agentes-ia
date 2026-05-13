# Arquitectura del bundle

El bundle es **autocontenido**: copiar `<bundle_dir>/` a otro proyecto
preserva todos los agentes, plantillas, estado y configuración.

## Capas

1. **Configuración** (`harness.toml`, `settings.json`, `feature_list.json`):
   parámetros del proyecto y cola de trabajo.
2. **Bootstrap** (`bootstrap/`): scripts ejecutables para preparar el
   entorno (`init.sh`) y verificar (`verify.sh`).
3. **Estado** (`state/<feature-id>/`): `state.yaml` por feature
   (máquina de estados) más bundle SDD (`SDD/` con artefactos
   canónicos).
4. **Agentes** (`agents/<name>/SKILL.md`): los 36 agentes oficiales más
   espacio para agentes custom. Incluye `agent-registry.yaml`
   auto-generado.
5. **Skills** (`skills/<name>/SKILL.md`): procedimientos auxiliares.
6. **MCP** (`mcp/`): configuración de servidores Model Context Protocol.
7. **Cliente IA** (`commands/`, `hooks/`, `settings.json`): integración
   nativa con clientes que los soportan (Claude Code).
8. **Documentación interna** (`docs/`): qué es el harness, cómo extenderlo.
9. **Utilidades** (`tools/`): scripts auxiliares (acceptance runner,
   verificador de trazabilidad, etc.).

## Invariantes

- `<bundle>/agents/<name>/SKILL.md` es la ÚNICA ruta válida para un
  agente, sin capas intermedias.
- `state/<id>/SDD/spec.lock.yaml` cierra una feature: hashes SHA-256 de
  los artefactos canónicos.
- `harness.toml::project.bundle_dir` debe coincidir con el nombre real
  del directorio padre. `harness doctor` lo verifica.
