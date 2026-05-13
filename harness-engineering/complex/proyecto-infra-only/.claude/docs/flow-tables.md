# Tablas operativas del flujo SDD

Este proyecto usa flow_type **complex**. La tabla siguiente muestra
las fases canónicas con su agente, inputs, outputs y siguiente fase.

## Resumen — flow complex (9 agentes canónicos)

```
Explorer → Proposer → [GATE#1] → (Spec-writer ‖ Designer) → Task-planner
       → Implementer → Code-reviewer → [GATE#2]
       → Verifier → Archiver → DONE
```

`spec-writer` y `designer` corren en paralelo (`‖`) tras gate1.

## Tabla detallada (10 fases)

| # | Fase | Agente | Lee de | Escribe a | Siguiente |
|---|---|---|---|---|---|
| 1 | explore | explorer | `feature_list.json[id]` | `.claude/state/<id>/SDD/context.md` | propose |
| 2 | propose | proposer | `SDD/context.md` | `SDD/proposal.md` | gate1 |
| 3 | gate1 | (humano o yolo) | `SDD/proposal.md` | `state.yaml.gates.gate1` | spec_design |
| 4a | spec_design | spec-writer | `SDD/proposal.md`, `AGENTS.md` | `SDD/requirements.md` | tasks |
| 4b | spec_design | designer (paralelo) | `SDD/proposal.md` | `SDD/design.md` | tasks |
| 5 | tasks | task-planner | `SDD/requirements.md`, `SDD/design.md` | `SDD/tasks.md`, `SDD/acceptance.yaml` | implement |
| 6 | implement | implementer | `SDD/tasks.md` | mods en `src/`, `SDD/implementation-notes.md` | review |
| 7 | review | code-reviewer | diff vs main, `SDD/*` | `SDD/review.md` | gate2 |
| 8 | gate2 | (humano o yolo) | `SDD/review.md`, diff | `state.yaml.gates.gate2` | verify |
| 9 | verify | verifier | `bootstrap/verify.sh`, `SDD/acceptance.yaml` | `SDD/verify-runs.jsonl` | archive |
| 10 | archive | archiver | todo el `SDD/` | `SDD/spec.lock.yaml`, `feature_list.json` update | DONE |

**Para perfiles con `gate3_pre_apply`** (típicamente `infra-only`): tras
`verify` se inserta `gate3` y luego `applier` antes de `archive`.



## Cross-cutting (activación por feature.tags)

- `security-critical`, `auth`, `crypto` → invoca `security-auditor`
  antes de gate2.
- `compliance`, `gdpr`, `audit` → invoca `compliance-officer` en gate2.
- `iac`, `terraform` → la fase `verify` ejecuta también `terraform-planner`
  antes del `verifier`.


## Modos de orquestación

Lee `.claude/harness.toml` campo `[orchestration].mode`.
Tres valores válidos: `manual` (default), `auto`, `yolo`. Detalle
completo en `HARNESS.md` sección 7.
