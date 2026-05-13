# Tablas operativas del flujo SDD

Este proyecto usa flow_type **simple**. La tabla siguiente muestra
las fases canónicas con su agente, inputs, outputs y siguiente fase.

## Resumen — flow simple (4 agentes canónicos)

```
Explorer → Designer → [GATE#1] → Builder → Reviewer → [GATE#2]
        → Reviewer (verify_archive) → DONE
```

`Designer` (simple) subsume Proposer + Spec-writer + Designer +
Task-planner del flujo complex (produce los 6 artefactos SDD en
single pass). `Reviewer` se invoca **dos veces**: una en `review`
(post-Builder), otra en `verify_archive` (post-gate2).

## Tabla detallada (7 fases)

| # | Fase | Agente | Lee de | Escribe a | Siguiente |
|---|---|---|---|---|---|
| 1 | explore | explorer | `feature_list.json[id]` | `.claude/state/<id>/SDD/context.md` | design |
| 2 | design | designer | `SDD/context.md`, `AGENTS.md` | `SDD/proposal.md`, `requirements.md`, `design.md`, `tasks.md`, `acceptance.yaml`, `sources.md` | gate1 |
| 3 | gate1 | (humano o yolo) | `SDD/*` | `state.yaml.gates.gate1` | implement |
| 4 | implement | builder | `SDD/tasks.md`, `SDD/design.md`, `SDD/acceptance.yaml` | mods en `src/`, `SDD/implementation-notes.md` | review |
| 5 | review | reviewer (fase 1/2) | diff vs main, `SDD/*` | `SDD/review.md` | gate2 |
| 6 | gate2 | (humano o yolo) | `SDD/review.md`, diff | `state.yaml.gates.gate2` | verify_archive |
| 7 | verify_archive | reviewer (fase 2/2) | `bootstrap/verify.sh`, `SDD/acceptance.yaml` | `SDD/verify-runs.jsonl`, `SDD/spec.lock.yaml`, `feature_list.json` update | DONE |



## Cross-cutting (activación por feature.tags)

- `security-critical`, `auth`, `crypto` → invoca `security-auditor`
  antes de gate2.
- `compliance`, `gdpr`, `audit` → invoca `compliance-officer` en gate2.
- `iac`, `terraform` → la fase `verify_archive` ejecuta también
  `terraform-planner` antes del `reviewer` (fase 2/2).


## Modos de orquestación

Lee `.claude/harness.toml` campo `[orchestration].mode`.
Tres valores válidos: `manual` (default), `auto`, `yolo`. Detalle
completo en `HARNESS.md` sección 7.
