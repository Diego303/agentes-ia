# Multi-agent orchestration

Este proyecto usa **Spec-Driven Development (SDD)** con una cadena de agentes
especializados, *gates* humanos entre ellos y revisores paralelos en GATE#2.

## Flujo completo

### Pre-flow (opcional, sólo si la feature es muy abierta o experimental)

```
[Brainstormer] → [Prior-Art Researcher] → [Hypothesis Formulator] → [Research Summarizer]
                                                                       ↓
                                                                   Proposer
```

Los agentes de `ideation/` viven **antes** de Explorer. Sólo se invocan
si el humano lo decide explícitamente. La salida final pre-flow son
artefactos en `progress/<id>/{brainstorm,prior-art,hypotheses,research-summary}.md`
que Proposer puede consultar opcionalmente.

### Pre-flow (infra)

```
[Drift Detector] → Explorer
```

Antes de Explorer en cualquier feature con `domain: infra`, **Drift Detector
debe correr** y producir `progress/<id>/drift-report.md`. Si reporta drift
crítico sin reconciliar, el flujo se detiene hasta resolución humana.

### Flujo principal SDD

```
Explorer → Proposer → [GATE#1] → (Spec-writer ‖ Designer) → Task-planner
       → Implementer → [GATE#2 + revisores paralelos] → Verifier → Archiver
```

`‖` indica paralelismo. Spec-writer y Designer corren simultáneamente
desde `proposal.md` aprobada. Convergen en `task-planner.md`.

### Sub-agentes que anexan a `design.md`

Designer escribe la sección base (`## Architecture (Designer)`). Los
siguientes sub-agentes pueden **anexar** secciones específicas según el
dominio del perfil:

| Sub-agente | Encabezado fijo en `design.md` | Cuándo |
|------------|-------------------------------|--------|
| `software/api-designer` | `## API contract` | feature toca endpoints/RPC/eventos |
| `software/test-engineer` | `## Testing strategy` | siempre en domain `software` |
| `infra/iac-designer` | `## IaC design` | siempre en domain `infra` |
| `content/content-strategist` | `## Content strategy` | siempre en domain `content` |

**Mecánica de append**: cada sub-agente busca su encabezado en `design.md`.
Si no existe, lo crea al final. Si existe, NO sobrescribe — añade al final
de la sección o crea `## <Nombre> (revisión 2)`. Los encabezados son la
única ubicación válida; no anexen al final del archivo sin encabezado.

### Revisores paralelos en GATE#2

Tras `implementation.md` y antes de Verifier, varios revisores corren **en
paralelo** según el perfil. Cada uno escribe su propio archivo y emite un
veredicto que puede bloquear GATE#2:

| Revisor | Output | Cuándo aplica | Bloquea GATE#2 si |
|---------|--------|---------------|-------------------|
| `code-reviewer` | `progress/<id>/code-review.md` | domain `software` | veredicto `no-go` |
| `security-auditor` | `progress/<id>/security-audit.md` | cross-cutting | hallazgo `high`/`critical` |
| `compliance-officer` | `progress/<id>/compliance-review.md` | cross-cutting | riesgo regulatorio sin mitigar |
| `doc-reviewer` | `progress/<id>/doc-review.md` | domain `docs` | veredicto `needs-revision` |
| `copy-editor` | `progress/<id>/copy-edit.md` | domain `content` | headings inconsistentes |
| `seo-reviewer` | `progress/<id>/seo-review.md` | domain `content` | keyword no en H1/meta |
| `fact-checker` | `progress/<id>/fact-check.md` | domain `content` | ≥1 incorrecta o ≥3 no-verificable |

GATE#2 se aprueba **sólo si todos los revisores aplicables emiten `go`** y
el humano aprueba.

### Gate#3 (sólo en `infra-only`)

```
Verifier → [GATE#3] → Applier → Archiver
```

- `terraform-planner` corre tras Verifier verde, produce `progress/<id>/terraform-plan.md`.
- `cost-estimator` anexa info, no bloquea.
- GATE#3 humano aprueba el apply.
- `applier` ejecuta, escribe `progress/<id>/apply.md`.

### Post-archive (paralelos a Archiver)

Tras Archiver escribir su `archive.md`, agentes adicionales **anexan
sub-secciones** al mismo archivo:

| Agente | Sub-encabezado en `archive.md` | Cuándo |
|--------|------------------------------|--------|
| `archiver` | `## Summary` (siempre primero) | siempre |
| `docs/changelog-curator` | `## Changelog entry` | feature user-facing |
| `docs/glossary-keeper` | `## Glossary updates` | introdujo terminología |
| `docs/example-curator` | `## Examples updates` | tocó superficie pública |
| `ideation/decision-recorder` | `## ADR reference` | hubo decisión arquitectónica no trivial |
| `content/distribution-planner` | `## Distribution plan reference` | domain `content` |

Cada uno escribe su sub-sección bajo su encabezado fijo. La feature se
marca `archived` en `feature_list.json` cuando todos los aplicables han
terminado.

## Contrato de agentes (5 secciones fijas)

Cada agente vive en `.claude/agents/<ruta>/<nombre>.md` y respeta:

1. **Rol** — responsabilidad única.
2. **Inputs esperados** — qué necesita.
3. **Procedimiento** — pasos numerados.
4. **Output** — qué produce + a quién pasa el testigo + cuándo parar.
5. **Anti-patterns** — qué NO hacer.

Dentro de **Output**, cada agente debe llevar dos sub-bloques al final:

- **Siguiente paso**: una línea con quién lee el artefacto.
- **Cuándo parar y pedir ayuda**: 3-4 bullets con escenarios de fallo
  comunes (inputs faltantes, ambigüedad irreductible, dependencia
  externa caída).

## Gates

Los gates son **checkpoints humanos**, no agentes:

- **GATE#1** (post-proposer): el humano aprueba propuesta antes de
  invertir en spec/diseño/implementación.
- **GATE#2** (post-implementation + revisores paralelos): el humano
  revisa código y todos los `*-review.md`/`*-audit.md` que emiten
  veredicto.
- **GATE#3** (pre-apply, sólo `infra-only`): el humano aprueba el
  `terraform-plan.md` antes de Applier.

## Workspace por feature

Cada feature en `feature_list.json` recibe `progress/<feature-id>/`. Los
artefactos son **append-only**: ningún agente edita archivos de agentes
previos. Si un agente está en desacuerdo con uno previo, escribe en el
suyo con referencia explícita.

## Protocolo común de manejo de errores

Cuando un agente no puede completar su trabajo:

1. **NO inventes** información ausente.
2. Documenta el bloqueo en `progress/<feature-id>/blockers.md` (o en una
   sección "Bloqueos" de tu propio output si tu rol lo permite).
3. **Para** y solicita revisión humana.
4. Si la falta de un input opcional tiene fallback (asumir baseline,
   marcar suposición), aplícalo y márcalo como suposición. Si NO tiene
   fallback razonable, para.
5. **Nunca** invoques al siguiente agente directamente — eso lo hace el
   orquestador (humano o `harness status`).

Ver cada agente para sus escenarios específicos de "Cuándo parar".

## Cross-cutting

Algunos perfiles declaran agentes *cross-cutting* (`security-auditor`,
`compliance-officer`) que se invocan en paralelo a los revisores de
GATE#2. Su contrato sigue las mismas 5 secciones.
