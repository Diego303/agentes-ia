# INSTRUCCIONES — proyecto-clean

> **Perfil**: `clean` — esqueleto sin dominios. 8 agentes de
> orquestación + 1 sample-agent. **17 archivos / ~21 KB.**

Este proyecto es el **esqueleto mínimo**: te da el contrato del flujo
SDD pero sin agentes de dominio (software/infra/content/docs/ideation).
Es ideal para:

- **Entender el sistema** sin distracciones de dominios.
- **Proyectos experimentales** donde aún no sabes qué dominio aplica.
- **Crear tu propio dominio custom** desde cero.

---

## Arranque (1 sola vez)

```bash
cd EJEMPLOS-BASE/proyecto-clean
./init.sh                      # git init + commit inicial
harness doctor                 # → 17 ok 0 warning(s) 0 error(s)
harness status                 # muestra SAMPLE-001 con next: Explorer
```

Tras esto, este proyecto ya es un repo git autónomo con su feature seed
(`SAMPLE-001`) lista para arrancar.

---

## Cómo trabajar con Claude Code

### Setup

Abre Claude Code en este directorio:

```bash
cd EJEMPLOS-BASE/proyecto-clean
claude
```

Las settings de Claude Code están en `.claude/settings.json` con
permisos seguros por defecto: lectura/edición/escritura limitadas a
este proyecto, deny para `rm -rf` y `git push --force`.

### Primer prompt: orientación

Cuando abras Claude Code por primera vez en este proyecto:

```
Lee AGENTS.md, CLAUDE.md y USAGE.md. Después dime:
1. Qué flujo SDD vamos a seguir.
2. Qué agentes están disponibles.
3. Qué feature está pendiente en feature_list.json.
4. Qué gates esperamos en este perfil.
```

Claude debería responder con un resumen del flujo `Explorer →
Proposer → [GATE#1] → (Spec-writer ‖ Designer) → Task-planner →
Implementer → [GATE#2] → Verifier → Archiver`, los 8 agentes
disponibles, la feature `SAMPLE-001`, y los gates 1 y 2.

### Trabajar la primera feature (paso a paso con Claude Code)

Para `SAMPLE-001` (la feature seed), sigue el flujo SDD:

#### Paso 1 — Explorer

```
Actúa como el agente Explorer descrito en .claude/agents/explorer.md.
La feature es SAMPLE-001 en feature_list.json. Mapea el repo y
produce progress/SAMPLE-001/exploration.md con las 5 secciones que
pide el agente: Contexto, Archivos relevantes, Patrones existentes,
Riesgos detectados, Áreas no claras.
```

Verifica el output:

```bash
cat progress/SAMPLE-001/exploration.md
harness status   # debería mostrar Last agent: Explorer, Next: Proposer
```

#### Paso 2 — Proposer

```
Actúa como Proposer (.claude/agents/proposer.md). Lee
progress/SAMPLE-001/exploration.md y produce
progress/SAMPLE-001/proposal.md con: Propuesta principal,
Alternativas descartadas (≥2), Scope (in/out), Trade-offs, Riesgos,
Preguntas abiertas. Detén el flujo en GATE#1.
```

#### Paso 3 — GATE#1 (humano)

**Tú** revisas `progress/SAMPLE-001/proposal.md`. Si apruebas:

```bash
echo "Aprobado por <tu-nombre> $(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  > progress/SAMPLE-001/gate1-approved.md
```

Si rechazas: añade feedback en un archivo nuevo y vuelve al Proposer
con el feedback.

#### Paso 4 — Spec-writer ‖ Designer (en paralelo)

```
Actúa como Spec-writer (.claude/agents/spec-writer.md). Lee
proposal.md aprobada y produce spec.md.
```

Y en otra conversación o tras la primera:

```
Actúa como Designer (.claude/agents/designer.md). Produce design.md
bajo el encabezado "## Architecture (Designer)".
```

#### Paso 5 — Task-planner

```
Actúa como Task-planner (.claude/agents/task-planner.md). Cruza
spec.md y design.md. Produce task-plan.md con tareas atómicas.
```

#### Paso 6 — Implementer

```
Actúa como Implementer (.claude/agents/implementer.md). Sigue
task-plan.md tarea a tarea. Para SAMPLE-001 (que es una feature de
ejemplo), implementa lo que decidieras en proposal.md.
Recuerda: implementation.md es OBLIGATORIO.
```

#### Paso 7 — GATE#2 (humano)

Revisa el diff (`git diff`) + `progress/SAMPLE-001/implementation.md`.
Aprueba o rechaza.

#### Paso 8 — Verifier → Archiver

```
Actúa como Verifier. Ejecuta el verify_stack del perfil clean
(markdownlint).
```

```
Actúa como Archiver. Cierra el ciclo: archive.md + update
feature_list.json::status a archived.
```

---

## Cómo trabajar con Codex / OpenAI Codex CLI

```bash
cd EJEMPLOS-BASE/proyecto-clean
codex                          # arranca codex CLI
```

Codex no usa `.claude/settings.json` (es de Claude Code), pero sí
puede leer todos los archivos del proyecto. Los prompts son similares
a los de Claude Code:

```
Lee AGENTS.md y .claude/agents/explorer.md. Actúa como ese agente para
SAMPLE-001 (definida en feature_list.json). Produce
progress/SAMPLE-001/exploration.md siguiendo el contrato de 5
secciones.
```

**Diferencias prácticas vs Claude Code**:

- Codex no tiene `Agent` tool subagentes. Cada agente lo invocas como
  prompt directo en la conversación principal.
- No tiene hooks pre/post tool use (los de `.claude/settings.json`).
  Si necesitas validación pre-commit, usa hooks de git (`.git/hooks/`)
  o un script propio.
- Permission model distinto: Codex pregunta en runtime para acciones
  riesgosas; Claude Code lee `.claude/settings.json::permissions`.

---

## Cómo trabajar con Cursor

Cursor tiene Composer (Cmd+I) y Chat. Para este flujo SDD:

1. Abre el repo en Cursor.
2. Composer + selecciona `.claude/agents/explorer.md` + `feature_list.json` + `AGENTS.md`.
3. Pídele actuar como Explorer y producir el artefacto.
4. Continúa fase a fase como con Claude Code.

Cursor **no respeta** `.claude/settings.json`; si necesitas hooks o
permisos, usa la configuración de Cursor (`.cursor/`).

---

## Cómo trabajar con GPT-4 / Claude.ai (chat web sin CLI)

Si trabajas desde la web sin CLI:

1. Copia el contenido del agente que toca:

   ```bash
   cat .claude/agents/explorer.md  # copia al portapapeles
   ```

2. En el chat web, pega como contexto:

   ```
   Voy a actuar contigo siguiendo este contrato de agente:
   
   <pega aquí el MD del agente>
   
   La feature es SAMPLE-001:
   <pega aquí la entrada de feature_list.json>
   
   Contexto del repo: <pega los archivos relevantes que el agente necesite>
   
   Produce el artefacto que pide la sección Output del agente.
   ```

3. Copia la respuesta a `progress/SAMPLE-001/exploration.md` (o el
   archivo que toque).

4. Verifica con `harness status` localmente.

---

## Cómo modificar este proyecto

### Añadir un agente custom

```bash
# 1. Crea el MD siguiendo el contrato de 5 secciones
mkdir -p .claude/agents/custom
cp .claude/agents/example/sample-agent.md .claude/agents/custom/mi-agente.md
# (Edítalo a tu gusto)

# 2. Añade su Siguiente paso y Cuándo parar al final del Output
# (ver formato en cualquier agente existente)

# 3. Documenta el handoff en AGENTS.md
# Edita AGENTS.md para mencionar dónde encaja en el flujo
```

### Añadir un dominio canónico (ej. software)

```bash
harness add-domain software
# → copia .claude/agents/software/{api-designer,code-reviewer,test-engineer}.md
# → actualiza harness.toml::domains.active
```

Tras esto, el flujo de tus features podrá invocar a esos 3 agentes
adicionales.

### Añadir un dominio custom (ej. data, ml, mobile)

```bash
harness add-domain data --custom
# → crea .claude/agents/data/agent.md como placeholder
# → editalo siguiendo el contrato de 5 secciones
```

### Añadir hooks de Claude Code

Edita `.claude/settings.json` para añadir hooks:

```json
{
  "permissions": { ... },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
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

Útil para auto-verificar tras cada edit.

### Añadir una skill de Claude Code

Skills son distintas de agentes en Claude Code. Para añadir una:

```bash
mkdir -p .claude/skills/mi-skill
cat > .claude/skills/mi-skill/SKILL.md <<'EOF'
---
name: mi-skill
description: Cuándo usarla
---

# mi-skill

Instrucciones cuando se use esta skill.
EOF
```

**Diferencia conceptual con agentes del harness**:
- **Agentes del harness** (`.claude/agents/<dominio>/<nombre>.md`):
  son contratos de roles del flujo SDD. Cualquier IA los lee como
  contexto para "actuar como". No tienen frontmatter especial.
- **Skills de Claude Code** (`.claude/skills/<name>/SKILL.md`): son
  capabilities que Claude Code activa con su herramienta `Skill`.
  Tienen frontmatter YAML obligatorio.

Si quieres convertir un agente del harness en una skill nativa de
Claude Code, añade frontmatter al MD:

```markdown
---
name: explorer
description: Mapea el contexto antes de proponer cambios
---

# Agent: Explorer
...
```

### Modificar el verify_stack

`clean` sólo tiene `markdownlint` en su verify_stack. Si quieres
añadir otro:

1. **Para este proyecto sólo**: edita `USAGE.md` documentando la
   herramienta extra. El Verifier la leerá de allí.
2. **Para el perfil entero (afecta a todos los proyectos generados
   con clean)**: edita
   `<repo-cli>/src/harness_cli/profiles/clean.yaml::verify_stack`.

---

## Primera feature recomendada

`SAMPLE-001` es perfecta para tu primer ciclo end-to-end porque:
- Es trivial: "rellena spec, design e implementación".
- Te obliga a recorrer las 8 fases del flujo SDD.
- No tiene cross-cutting (security/compliance) que compliquen GATE#2.
- El verify_stack es sólo `markdownlint`, ejecutable sin instalar
  nada extra (pip install pymarkdown o similar).

Tras completarla:
- Borra `SAMPLE-001` de `feature_list.json` y mueve `progress/SAMPLE-001/`
  a `archive/SAMPLE-001/` si quieres limpiar.
- Añade tu primera feature real con un `id` propio.

---

## Troubleshooting específico de este proyecto

### "harness status" no muestra SAMPLE-001 como esperado

Verifica que `feature_list.json` está intacto y que su `status` es
`proposed`:

```bash
cat feature_list.json
```

### "harness doctor" reporta error de algún agente faltante

Si borraste un agente por accidente:

```bash
# Re-renderiza desde el template
.venv/bin/python -c "
from harness_cli.core.profiles import load_profile
from harness_cli.core.renderer import render_profile
from pathlib import Path
import shutil
# Cuidado: esto sobrescribe TODO el proyecto
# Usar sólo para testing
"
# O más simple: re-init en otra carpeta y copia los archivos faltantes
harness init clean --target /tmp/clean-fresh
cp /tmp/clean-fresh/.claude/agents/<archivo-faltante> .claude/agents/
```

### Los agentes hablan español pero quiero que respondan en inglés

Edita `CLAUDE.md` y añade al final:

```markdown
## Idioma

Responde a todas las prompts en inglés a partir de ahora, aunque los
MDs de los agentes estén en español.
```

---

## Próximos pasos

1. Lee [`../../docs/concepts.md`](../../docs/concepts.md) para
   entender el modelo completo.
2. Lee [`../../docs/best-practices.md`](../../docs/best-practices.md)
   para la operativa real.
3. Cuando quieras un proyecto más completo, copia
   [`../proyecto-software/`](../proyecto-software/) que tiene todos
   los agentes de software + cross-cutting.
