# INSTRUCCIONES — proyecto-software

> **Perfil**: `web-app` — SaaS / API / librería / microservicio.
> **23 agentes**: 8 orquestación + 3 software + 5 docs + 6 ideation + 2
> cross-cutting (security-auditor, compliance-officer). **32 archivos.**

Este proyecto es el **más completo** de los ejemplos. Te da:

- El flujo SDD canónico de software con sub-agentes especializados
  (api-designer, test-engineer, code-reviewer).
- Pre-flow de ideation (brainstormer, critic, etc.) cuando una feature
  es muy abierta.
- Documentación en paralelo (technical-writer, doc-reviewer,
  changelog-curator, glossary-keeper, example-curator).
- **GATE#2 con 4 revisores paralelos** (code-reviewer + security-auditor
  + compliance-officer + doc-reviewer) que pueden bloquear el gate.

Es ideal para:
- **SaaS / APIs / librerías profesionales** que requieren security +
  compliance reviews.
- **Proyectos con cobertura de tests / docs significativa**.
- **Equipos pequeños o solos con asistente IA** que quieren disciplina
  industrial sin overhead humano.

---

## Arranque (1 sola vez)

```bash
cd EJEMPLOS-BASE/proyecto-software
./init.sh                      # git init + commit inicial
harness doctor                 # → 22 ok 0 warning(s) 0 error(s)
harness status                 # muestra DEMO-001 con next: Explorer
```

---

## Cómo trabajar con Claude Code

### Setup

```bash
cd EJEMPLOS-BASE/proyecto-software
claude
```

Las settings están en `.claude/settings.json` con permisos seguros:
read/edit/write limitados al proyecto, deny para `rm -rf` y
`git push --force`.

### Primer prompt: orientación

```
Lee AGENTS.md, CLAUDE.md y USAGE.md. Después dime:
1. Qué dominios tiene este proyecto activos.
2. Qué cross-cutting agents van a correr en GATE#2.
3. Qué verify_stack debe ejecutar el Verifier.
4. Qué feature está en feature_list.json.
```

Claude debería identificar: domains software/docs/ideation,
cross-cutting security-auditor + compliance-officer, verify_stack
ruff/pytest/secret-scanning/markdownlint, feature DEMO-001 (endpoint
de health check).

### Trabajar la primera feature (DEMO-001)

#### Fase 1 — Explorer

```
Actúa como Explorer (.claude/agents/explorer.md). Mapea el repo y
produce progress/DEMO-001/exploration.md.
```

#### Fase 2 — Proposer

```
Actúa como Proposer (.claude/agents/proposer.md). Lee
exploration.md y produce proposal.md.
```

#### Fase 3 — GATE#1 (humano)

Revisa `proposal.md`. Aprueba con:

```bash
echo "Aprobado por <tu-nombre> $(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  > progress/DEMO-001/gate1-approved.md
```

#### Fase 4 — Spec-writer ‖ Designer (paralelo)

```
Actúa como Spec-writer. Lee proposal.md aprobada y produce spec.md.
```

```
Actúa como Designer (.claude/agents/designer.md). Produce design.md
bajo el encabezado "## Architecture (Designer)".
```

#### Fase 4.b — Sub-agentes que anexan a design.md

Como `domain: software` está activo:

```
Actúa como API Designer (.claude/agents/software/api-designer.md).
Anexa la sección "## API contract" a design.md (si la feature toca API).
```

```
Actúa como Test Engineer (.claude/agents/software/test-engineer.md).
Anexa la sección "## Testing strategy" a design.md.
```

#### Fase 5 — Task-planner

```
Actúa como Task-planner. Cruza spec.md y design.md (con todas las
secciones anexadas). Produce task-plan.md.
```

#### Fase 6 — Implementer

```
Actúa como Implementer. Sigue task-plan.md tarea a tarea. Para
DEMO-001, implementa el endpoint de health check según spec/design.
Recuerda: implementation.md es OBLIGATORIO (cada tarea, una línea).
```

#### Fase 7 — Revisores paralelos (PRE-GATE#2)

En `web-app` corren **4 revisores** simultáneamente. Pídeselos en orden
o en paralelo (mejor en conversaciones distintas si tu IA lo permite):

```
Actúa como Code Reviewer (.claude/agents/software/code-reviewer.md).
Revisa el diff de Implementer y produce code-review.md con veredicto.
```

```
Actúa como Security Auditor
(.claude/agents/cross-cutting/security-auditor.md). Audita el diff y
produce security-audit.md.
```

```
Actúa como Compliance Officer
(.claude/agents/cross-cutting/compliance-officer.md). Audita PII /
licencias / retención. Produce compliance-review.md.
```

```
Actúa como Doc Reviewer (.claude/agents/docs/doc-reviewer.md). Revisa
los docs producidos por technical-writer (si los hay). Produce
doc-review.md.
```

**GATE#2 sólo se aprueba si los 4 emiten `go`.**

#### Fase 8 — GATE#2 (humano)

Revisa `git diff` + cada `*-review.md` / `*-audit.md`. Si todos `go`:

```bash
echo "Aprobado por <tu-nombre> $(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  > progress/DEMO-001/gate2-approved.md
```

#### Fase 9 — Verifier

```
Actúa como Verifier. Ejecuta el verify_stack de web-app:
- ruff check
- pytest
- secret-scanning (gitleaks o equivalente)
- markdownlint

Produce verification.md.
```

#### Fase 10 — Archiver + post-archive

```
Actúa como Archiver (.claude/agents/archiver.md). Cierra el ciclo:
archive.md (## Summary) + update feature_list.json.
```

Si la feature toca docs públicas, también:

```
Actúa como Changelog Curator (.claude/agents/docs/changelog-curator.md).
Anexa la entrada al CHANGELOG.md y la sub-sección "## Changelog entry"
a archive.md.
```

```
Actúa como Glossary Keeper. Si introdujimos terminología nueva, anexa
"## Glossary updates" a archive.md.
```

```
Actúa como Example Curator. Si la feature tocó superficie pública,
mantén ejemplos y anexa "## Examples updates" a archive.md.
```

---

## Cómo trabajar con Codex

```bash
cd EJEMPLOS-BASE/proyecto-software
codex
```

Codex no usa `.claude/settings.json` ni el Agent tool de Claude Code.
Cada agente lo invocas como prompt directo:

```
Sigue el contrato del agente en .claude/agents/explorer.md. Actúa como
ese agente para DEMO-001. Produce progress/DEMO-001/exploration.md.
```

Para los **revisores paralelos en GATE#2**, Codex no tiene paralelismo
nativo. Tienes 2 opciones:
1. **Secuencial**: invoca cada uno en sucesión.
2. **Múltiples sesiones de codex**: abre 4 terminales con `codex`,
   invoca un revisor en cada una.

Diferencia clave: los hooks de `.claude/settings.json` son ignorados
por Codex. Si necesitas validación pre-commit, usa `git hooks`
(`.git/hooks/pre-commit`).

---

## Cómo trabajar con Cursor

Cursor tiene **Composer** (Cmd+I) para changes multi-archivo y **Chat**
para conversación.

Para este flujo:

1. Composer + selecciona los archivos de contexto:
   - `.claude/agents/<agente>.md` (el agente que toca)
   - `progress/<feature-id>/<artefactos-previos>.md`
   - Archivos del repo que el agente necesite
2. Pide actuar como ese agente y producir el artefacto.

Cursor tiene reglas en `.cursor/rules/` — útil para reforzar el
contrato:

```bash
mkdir -p .cursor/rules
cat > .cursor/rules/sdd-contract.md <<'EOF'
# SDD Contract

Cuando el usuario te pida actuar como un agente del flujo SDD:
1. Lee primero el MD del agente en .claude/agents/<...>.md
2. Sigue el contrato de 5 secciones literalmente.
3. Produce SOLO el artefacto declarado en su sección Output.
4. NO invoques al siguiente agente; sólo deja el artefacto.
5. Para en cada gate humano.
EOF
```

---

## Cómo trabajar con GPT-4 / Claude.ai (chat web)

Sin CLI, copia-pega es la opción:

1. Para arrancar una fase, copia 3 cosas al chat:
   - El MD del agente actual.
   - Los artefactos previos (`exploration.md`, `proposal.md`, etc.).
   - Los archivos del repo relevantes (resumen de `feature_list.json`,
     archivos del código que el agente vaya a tocar).
2. Pídele actuar como ese agente.
3. Copia su output al archivo destino.
4. Verifica con `harness status` localmente.

Es más friccional pero funciona. Para proyectos largos, considera
usar un CLI (Claude Code, Codex, Cursor).

---

## Cómo modificar este proyecto

### Añadir un agente custom específico de tu stack

Ejemplo: añadir un `db-migrator` para features que toquen schema.

```bash
# 1. Crea el MD siguiendo el contrato de 5 secciones
cp .claude/agents/example/sample-agent.md \
   .claude/agents/software/db-migrator.md
# (Edítalo con Rol, Inputs, Procedimiento, Output, Anti-patterns,
#  Siguiente paso, Cuándo parar)
```

```bash
# 2. Documenta el handoff en AGENTS.md (sección "Sub-agentes que anexan a design.md")
# Edita la tabla añadiendo:
# | software/db-migrator | ## Migration plan | feature toca schema |
```

### Modificar permisos de Claude Code

Edita `.claude/settings.json::permissions`. Ejemplo:

```json
{
  "permissions": {
    "allow": [
      "Bash(git status)",
      "Bash(git diff:*)",
      "Bash(pytest:*)",
      "Bash(ruff:*)",
      "Read(./**)",
      "Edit(./**)",
      "Write(./**)"
    ],
    "deny": [
      "Bash(rm -rf:*)",
      "Bash(git push --force:*)"
    ]
  }
}
```

### Añadir hooks de Claude Code

Para auto-verificar tras cada edit:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "ruff check $CLAUDE_FILE_PATHS 2>&1 || true"
          }
        ]
      }
    ]
  }
}
```

Para validar al cierre de sesión:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "harness doctor --target $CLAUDE_PROJECT_DIR"
          }
        ]
      }
    ]
  }
}
```

### Añadir una skill de Claude Code

Las skills son distintas de los agentes del harness. Ejemplo de skill
para "explicar SDD":

```bash
mkdir -p .claude/skills/sdd-helper
cat > .claude/skills/sdd-helper/SKILL.md <<'EOF'
---
name: sdd-helper
description: Use when the user asks how SDD works, what gates do, or how to invoke an agent. Reads AGENTS.md and explains the flow.
---

# SDD Helper

Cuando el usuario pregunte sobre el flujo SDD:
1. Lee AGENTS.md.
2. Identifica en qué fase está la feature actual con `harness status`.
3. Explica el siguiente agente que debe correr y por qué.
4. Apunta al MD exacto del agente: `.claude/agents/<...>.md`.
EOF
```

Convertir un agente del harness en skill nativa de Claude Code:

```bash
# Edita el MD del agente y añade frontmatter al inicio
sed -i '1i\
---\
name: explorer\
description: Maps repo state before proposing changes\
---\
' .claude/agents/explorer.md
```

### Cambiar el verify_stack

Edita `<repo-cli>/src/harness_cli/profiles/web-app.yaml::verify_stack`.

Para este proyecto específico, también puedes documentar herramientas
extra en `USAGE.md` (regenerar con `harness print-usage web-app`
después).

### Añadir un dominio adicional (ej. infra)

```bash
harness add-domain infra
# → copia 5 agentes infra al proyecto
# → actualiza harness.toml::domains.active = ["software", "docs", "ideation", "infra"]
```

Pero atención: el perfil `web-app` no tiene `gate3_pre_apply`, así que
los agentes infra (terraform-planner, applier) no encajarán bien si
realmente vas a tocar infra. Para proyectos mixtos, considera empezar
con un perfil custom (ver `docs/extending.md`).

### Añadir un agente cross-cutting custom

Por ejemplo, un `accessibility-auditor` que revisa WCAG en GATE#2:

1. **Crea el template del CLI** (afecta a futuros init):
   ```bash
   cd <repo-cli>
   mkdir -p src/harness_cli/templates/cross_cutting/accessibility-auditor
   # Crea agent.md siguiendo el contrato
   ```

2. **Añade al YAML del perfil**:
   ```yaml
   # web-app.yaml
   cross_cutting:
     - security-auditor
     - compliance-officer
     - accessibility-auditor   # nuevo
   ```

3. **Re-genera proyectos existentes** (manualmente, o re-init).

---

## Primera feature recomendada

`DEMO-001` ("endpoint de health check") es buena para tu primer ciclo
end-to-end porque:

- **Es trivial técnicamente**: 1 endpoint `GET /healthz` que devuelve
  `200 OK`.
- **Tiene superficie pública**: ejercita api-designer + technical-writer
  + example-curator.
- **Tiene tests**: ejercita test-engineer + Implementer + Verifier.
- **NO tiene riesgo security alto**: security-auditor saldrá en `low`,
  permitiendo aprobar GATE#2 sin bloqueo.
- **NO toca PII**: compliance-officer saldrá en `info`.

Tras completarla, el siguiente paso natural es una feature que **sí**
toque PII o seguridad para ejercitar los cross-cutting en serio.

---

## Troubleshooting específico

### Los revisores paralelos "go" pero el código falla en producción

Verifica que **realmente** corriste los 4 revisores y leíste sus
outputs. Si tu IA "saltó" alguno (output sospechoso o muy corto),
re-ejecútalo con prompt más exigente:

```
Re-ejecuta el agente Code Reviewer leyendo el diff archivo por archivo
(no en bulk). Para cada archivo, identifica al menos un riesgo o
confirma explícitamente que no hay riesgos.
```

### `harness doctor` reporta drift en agentes que personalicé

Esperado. Drift detection es opt-in (`--check-drift`) y los warnings
son informativos. Si tus customizaciones son intencionales, ignora.

### "El verify_stack falla porque no tengo gitleaks instalado"

Edita el verify_stack del Verifier en su MD para usar otra herramienta
(p. ej. `trufflehog`), o instala gitleaks:

```bash
# Linux/Mac
brew install gitleaks  # o apt/dnf install
# Windows
choco install gitleaks
```

### "GATE#2 se aprueba pero security-auditor da `medium`"

`medium` no es bloqueante por defecto (sólo `high`/`critical`). Pero
**deberías documentar la mitigación** o aceptar la deuda en
`progress/<id>/risk-accepted.md`.

---

## Próximos pasos

1. Lee [`../../docs/best-practices.md`](../../docs/best-practices.md)
   para sizing de features y gate hygiene.
2. Configura tus hooks de `.claude/settings.json` para auto-validar.
3. Si vas a usar el flujo intensivamente, considera scripts wrapper
   para los prompts más comunes (un `bin/explorer.sh` que abra el chat
   con el contexto pre-cargado, etc.).
