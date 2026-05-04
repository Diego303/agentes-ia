# USAGE — `web-app`

> SaaS, microservicios, librerías, APIs

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

- `software`
- `docs`
- `ideation`

## Cross-cutting agents

Se ejecutan en paralelo al flujo principal antes de **GATE#2**:

- `security-auditor`
- `compliance-officer`

## Gates

- **GATE#1** (`gate1_post_proposer`) — Después del Proposer, antes de Spec/Designer.
- **GATE#2** (`gate2_post_reviewer`) — Después del Implementer, antes de Verifier/Archiver.

## Verify stack

Ejecuta antes de Archiver. Si algo falla, vuelve a Implementer.

| Categoría | Herramienta |
|-----------|-------------|
| lint | `ruff` |
| tests | `pytest` |
| security | `secret-scanning` |
| markdown | `markdownlint` |

## Custom agents

_Ninguno en este perfil._

## Default feature seeds

| ID | Título | Dominio | Prio | Tags |
|----|--------|---------|------|------|
| `DEMO-001` | Feature de ejemplo: endpoint de health check | software | 1 | — |

---

Generado por `harness-cli` desde `profiles/<name>.yaml`.
