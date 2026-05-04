# USAGE — `clean`

> Estructura mínima para rellenar manualmente. Sin dominios completos.

## Quick start

1. Elige una feature en `feature_list.json` con `status: proposed`.
2. Crea `progress/<feature-id>/` (workspace por feature).
3. Ejecuta los agentes en orden:

   ```
   Explorer → Proposer → [GATE#1] → (Spec-writer ‖ Designer)
          → Task-planner → Implementer → [GATE#2] → Verifier → Archiver
   ```

4. Detente en cada gate; reanuda sólo con aprobación humana.
5. Cuando Archiver termina, marca la feature como `status: archived`.

## Domains

_Sin dominios pre-poblados._ Crea tus propios agentes en `.claude/agents/<dominio>/` siguiendo el contrato de 5 secciones.

## Cross-cutting agents

_Ninguno en este perfil._

## Gates

- **GATE#1** (`gate1_post_proposer`) — Después del Proposer, antes de Spec/Designer.
- **GATE#2** (`gate2_post_reviewer`) — Después del Implementer, antes de Verifier/Archiver.

## Verify stack

Ejecuta antes de Archiver. Si algo falla, vuelve a Implementer.

| Categoría | Herramienta |
|-----------|-------------|
| markdown | `markdownlint` |

## Custom agents

- `.claude/agents/example/sample-agent.md` (template: `sample-agent`)

## Default feature seeds

| ID | Título | Dominio | Prio | Tags |
|----|--------|---------|------|------|
| `SAMPLE-001` | Tu primera feature: rellena spec, design e implementación | custom | 1 | — |

## Notes

Este perfil te da el esqueleto del harness pero NO los agentes de software/infra/content.
Crea tus propios agentes en .claude/agents/<dominio>/ siguiendo el contrato de 5 secciones.
Mira docs/extending.md para guía paso a paso.

---

Generado por `harness-cli` desde `profiles/<name>.yaml`.
