# USAGE — `infra-only`

> IaC pura, sin código de aplicación

## Quick start

1. Elige una feature en `feature_list.json` con `status: proposed`.
2. Crea `progress/<feature-id>/` (workspace por feature).
3. Ejecuta los agentes en orden:

   ```
   Explorer → Proposer → [GATE#1] → (Spec-writer ‖ Designer)
          → Task-planner → Implementer → [GATE#2] → Verifier
          → [GATE#3] → Applier → Archiver
   ```

4. Detente en cada gate; reanuda sólo con aprobación humana.
5. Cuando Archiver termina, marca la feature como `status: archived`.

## Domains

- `infra`
- `docs`

## Cross-cutting agents

Se ejecutan en paralelo al flujo principal antes de **GATE#2**:

- `security-auditor`

## Gates

- **GATE#1** (`gate1_post_proposer`) — Después del Proposer, antes de Spec/Designer.
- **GATE#2** (`gate2_post_reviewer`) — Después del Implementer, antes de Verifier/Archiver.
- **GATE#3** (`gate3_pre_apply`) — Antes de operaciones irreversibles (terraform apply, kubectl apply).

## Verify stack

Ejecuta antes de Archiver. Si algo falla, vuelve a Implementer.

| Categoría | Herramienta |
|-----------|-------------|
| lint | `tflint` |
| validate | `terraform-validate` |
| security | `tfsec` |
| markdown | `markdownlint` |

## Custom agents

_Ninguno en este perfil._

## Default feature seeds

| ID | Título | Dominio | Prio | Tags |
|----|--------|---------|------|------|
| `DEMO-INFRA-001` | VPC base con subredes públicas y privadas | infra | 1 | security-critical, iac |

---

Generado por `harness-cli` desde `profiles/<name>.yaml`.
