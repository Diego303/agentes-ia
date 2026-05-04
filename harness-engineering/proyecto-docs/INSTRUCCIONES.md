# INSTRUCCIONES — proyecto-docs

> **Generado con**: `harness init clean` + `harness add-domain docs`.
> **13 agentes**: 8 orquestación + 5 docs (technical-writer,
> doc-reviewer, changelog-curator, glossary-keeper, example-curator) +
> 1 sample. **22 archivos.**

Este proyecto está enfocado en **documentación pura**: docs sites,
guías, libros técnicos, READMEs corporativos, manuales. NO incluye
software ni infra ni cross-cutting de seguridad — sólo lo necesario
para producir docs de calidad.

Es ideal para:
- **Documentar un proyecto existente** (que vive en otro repo).
- **Mantener un libro técnico** o curso.
- **Generar guías de cliente / API docs** para producto SaaS sin tocar
  el código.
- **Centralizar docs internas** de equipo.

---

## Arranque (1 sola vez)

```bash
cd EJEMPLOS-BASE/proyecto-docs
./init.sh                      # git init + commit inicial
harness doctor                 # → 18 ok 0 warning(s) 0 error(s)
harness status                 # muestra SAMPLE-001 con next: Explorer
```

---

## Características del flujo en este proyecto

A diferencia de los otros ejemplos, aquí:

- **No hay cross-cutting** (security/compliance) — los docs no tocan
  PII directamente, así que no se invocan.
- **GATE#2 tiene 1 revisor**: doc-reviewer (sólo).
- **Post-archive** muy activo: changelog-curator, glossary-keeper y
  example-curator anexan a `archive.md` casi siempre.
- **Verify stack**: `markdownlint` (heredado de clean — debería tener
  además `lychee` para link checking, ver "Cómo modificar").

---

## Cómo trabajar con Claude Code

### Setup

```bash
cd EJEMPLOS-BASE/proyecto-docs
claude
```

### Primer prompt: orientación

```
Lee AGENTS.md, CLAUDE.md y USAGE.md. Dime:
1. Qué dominio está activo (debería ser docs).
2. Qué post-archive agents van a correr (changelog-curator,
   glossary-keeper, example-curator, decision-recorder si aplica).
3. Qué verify_stack ejecuta el Verifier.
```

### Trabajar la primera feature (SAMPLE-001)

Para `SAMPLE-001` ("Tu primera feature"), redefínela como una feature
real de docs. Por ejemplo: "Documentar cómo usar la API de Pagos".

#### Fase 1 — Explorer (mapea la docs existente)

```
Actúa como Explorer. La feature es DOC-001 "Documentar API de Pagos".
Mapea la docs existente del repo: estructura de docs/, convenciones de
naming, taxonomía (referencia/guía/tutorial), style guide si existe.
Identifica gaps en cobertura. Produce
progress/DOC-001/exploration.md.
```

#### Fase 2 — Proposer

```
Actúa como Proposer. Lee exploration.md. Propón:
1. Estructura de la nueva docs (qué archivos en qué carpetas).
2. ≥2 alternativas de organización (por ejemplo: guía única vs
   reference + tutoriales separados).
3. Scope: qué endpoints documentamos, cuáles dejamos para futuro.
Produce proposal.md.
```

GATE#1 humano.

#### Fase 3 — Spec-writer ‖ Designer

```
Actúa como Spec-writer. Define qué debe cubrir cada archivo de docs:
audiencia, longitud aprox, secciones obligatorias.
```

```
Actúa como Designer. Define la estructura: ruta de cada archivo en el
árbol, links entre archivos, taxonomía clara entre referencia y
tutorial. Produce design.md con "## Architecture (Designer)".
```

#### Fase 4 — Task-planner

```
Actúa como Task-planner. Convierte spec + design en tareas atómicas:
- [1] crear docs/api/payments.md (referencia)
- [2] crear docs/guides/payments-quickstart.md (tutorial)
- [3] actualizar docs/index.md con links
- [4] añadir ejemplo runnable en examples/payments/
```

#### Fase 5 — Technical Writer (Implementer especializado para docs)

En perfiles con `domain: docs`, Technical Writer **es** el "Implementer"
de docs. Pero a diferencia del Implementer genérico de software,
escribe markdown:

```
Actúa como Technical Writer (.claude/agents/docs/technical-writer.md).
Sigue task-plan.md. Escribe los archivos de docs reales bajo docs/.
Para cada API endpoint, incluye al menos un ejemplo ejecutable.
Produce progress/DOC-001/docs-written.md (lista de archivos producidos)
y progress/DOC-001/implementation.md.
```

**Importante**: el Implementer base genérico también puede correr —
Technical Writer es opcional/complementario. Si los dos corren, el
Implementer escribe el código (si lo hay) y Technical Writer escribe
los docs.

#### Fase 6 — GATE#2 + revisores paralelos

En docs hay **1 revisor activo**: doc-reviewer.

```
Actúa como Doc Reviewer (.claude/agents/docs/doc-reviewer.md). Revisa
los archivos de docs nuevos. Verifica:
- Precisión técnica (lo escrito coincide con lo implementado).
- Completitud (cada endpoint tiene ejemplo, cada ejemplo funciona).
- Consistencia (terminología, links, estilo).
- TODO/FIXME/TBD sin tracking (bloqueante).
Produce doc-review.md con veredicto go / needs-revision.
```

GATE#2: revisas el diff de docs + `doc-review.md`.

#### Fase 7 — Verifier

```
Actúa como Verifier. Ejecuta el verify_stack:
- markdownlint (lint de markdown)
- (Recomendado: añadir lychee para link checking, ver "Cómo
  modificar")
Verifica que cada criterio del spec tiene cobertura.
Produce verification.md.
```

#### Fase 8 — Archiver + post-archive

```
Actúa como Archiver. Cierra el ciclo: archive.md (## Summary) +
update feature_list.json.
```

```
Actúa como Changelog Curator. Si los docs son user-facing (públicas),
añade entrada al CHANGELOG.md y sub-sección "## Changelog entry" a
archive.md.
```

```
Actúa como Glossary Keeper. Si los docs introdujeron términos nuevos
(p. ej. "idempotency key", "payment intent"), añade a docs/glossary.md
y "## Glossary updates" a archive.md.
```

```
Actúa como Example Curator. Si añadiste ejemplos en examples/, ejecuta
los ejemplos relacionados y captura outputs en examples-run.md.
Anexa "## Examples updates" a archive.md.
```

```
Actúa como Decision Recorder (.claude/agents/ideation/decision-recorder.md
si está, o el del repo). Si la feature implicó decisión arquitectónica
sobre la docs (formato, taxonomía), crea ADR. Si no, escribe no-adr.md.
```

---

## Cómo trabajar con Codex

```bash
cd EJEMPLOS-BASE/proyecto-docs
codex
```

Codex maneja bien markdown. Para este proyecto:

```
Lee AGENTS.md, .claude/agents/docs/technical-writer.md, y
progress/DOC-001/spec.md. Actúa como Technical Writer y produce los
archivos de docs en docs/api/ siguiendo el spec.
```

Para los post-archive (changelog-curator, etc.), invoca cada uno como
prompt secuencial.

---

## Cómo trabajar con Cursor

Cursor tiene Composer (Cmd+I) ideal para multi-archivo:

1. Composer + selecciona los archivos del repo:
   - `.claude/agents/docs/technical-writer.md`
   - `progress/DOC-001/spec.md` y `design.md`
   - Archivos de docs hermanos (para mantener estilo consistente)
2. Pide actuar como Technical Writer y producir los archivos.

Cursor tiene buena integración con preview de markdown — útil para
revisar mientras escribes.

---

## Cómo trabajar con GPT-4 / Claude.ai (chat web)

Para docs es **especialmente friccional** copiar archivos a chat web.
Recomendación: si vas a usar chat web, exporta los archivos relevantes
a un único bundle:

```bash
# Crea un contexto consolidado para pegar en chat
cat AGENTS.md \
    .claude/agents/docs/technical-writer.md \
    progress/DOC-001/spec.md \
    progress/DOC-001/design.md \
    > /tmp/context.md
cat /tmp/context.md  # copia al portapapeles
```

Luego en el chat:

```
Voy a actuar contigo como Technical Writer. Aquí está el contexto:

<pega /tmp/context.md>

Produce los archivos de docs siguiendo el contrato. Devuélveme cada
archivo en un bloque de código separado con el path como comentario.
```

---

## Cómo modificar este proyecto

### Añadir lychee al verify_stack (link checking)

```bash
# Edita el verify_stack en USAGE.md (manual; sólo para este proyecto)
# o edita el perfil del CLI (afecta a futuros init):
#   vi <repo-cli>/src/harness_cli/profiles/clean.yaml
#   añade:
#   - links: lychee
```

Luego, en el agente Verifier, asegúrate de que la herramienta se
ejecuta:

```bash
# En el prompt al Verifier:
"Ejecuta:
1. markdownlint **/*.md
2. lychee --no-progress **/*.md
3. ..."
```

### Añadir vale (style linting)

vale es un linter de estilo para prosa (similar a un grammar checker
configurable). Útil para enforzar style guide.

```bash
# Instala vale
brew install vale  # o equivalente

# Configura en .vale.ini en la raíz
cat > .vale.ini <<'EOF'
StylesPath = .vale/styles
MinAlertLevel = suggestion

[*.md]
BasedOnStyles = Vale, write-good
EOF

mkdir -p .vale/styles/Vocab/Project
echo "harness" > .vale/styles/Vocab/Project/accept.txt

# Añade vale al verify_stack como hiciste con lychee
```

### Convertir a perfil content-studio

Si el alcance crece a content marketing (no solo docs):

```bash
harness add-domain content
harness add-domain ideation
# Actualiza harness.toml manualmente o re-init en otra carpeta
# con harness init content-studio --target ../proyecto-content
```

### Añadir un agente "spell-checker" custom

```bash
cat > .claude/agents/docs/spell-checker.md <<'EOF'
# Agent: Spell Checker (docs)

## Rol
Detecta errores ortográficos y typos en los archivos de docs nuevos
antes de GATE#2. Complementa al doc-reviewer (que mira precisión
técnica y completitud).

## Inputs esperados
- Archivos de docs nuevos o modificados.
- Diccionario del proyecto (opcional, en .vale/styles/Vocab/Project/).

## Procedimiento
1. Para cada archivo .md nuevo, ejecuta `aspell list` o equivalente.
2. Filtra falsos positivos contra el diccionario del proyecto.
3. Para cada typo real, reporta file:line:palabra:sugerencia.
4. Escribe progress/<id>/spell-check.md con: tabla de typos, veredicto.

## Output
- progress/<id>/spell-check.md.

**Siguiente paso**: GATE#2 — tu veredicto pesa junto al de doc-reviewer.

**Cuándo parar y pedir ayuda**:
- aspell no instalado: documenta y emite veredicto manual sobre los
  archivos abiertos en chat.
- >50 candidatos a typo (probable falso positivo del diccionario):
  para; pide al humano actualizar el diccionario.
- Términos técnicos confundidos con typos: registra en lista de
  excepciones, no los marques como bloqueo.

## Anti-patterns
- ❌ Corregir los typos tú directamente — eso es Technical Writer.
- ❌ Marcar nombres propios como typos.
- ❌ Reportar typos en archivos generados (no en source).
EOF
```

### Hook para auto-validar tras escribir docs

```json
// .claude/settings.json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'if echo \"$CLAUDE_FILE_PATHS\" | grep -qE \"\\.md$\"; then markdownlint $CLAUDE_FILE_PATHS 2>&1 || true; fi'"
          }
        ]
      }
    ]
  }
}
```

### Conectar a un docs site (Hugo, MkDocs, Docusaurus)

Este proyecto **no asume** un docs site específico. Si quieres
generar HTML, instala el static site generator y configúralo:

```bash
# Ejemplo con MkDocs
pip install mkdocs mkdocs-material
mkdocs new .   # crea mkdocs.yml + docs/index.md
# Edita mkdocs.yml para apuntar a tus docs
mkdocs serve   # preview en :8000
```

Y añade al verify_stack:

```bash
mkdocs build --strict   # falla si hay warnings (broken links, etc.)
```

---

## Primera feature recomendada

`SAMPLE-001` (la feature seed) la redefines como una feature real de
docs. Sugerencias:

| Tipo | Ejemplo | Por qué buena para arrancar |
|------|---------|-----------------------------|
| API reference | "Documentar GET /users" | Toca technical-writer + example-curator. |
| Guía conceptual | "Explicar cómo funciona la auth" | Toca technical-writer + glossary-keeper. |
| Tutorial | "Quickstart: tu primera petición a la API" | Toca technical-writer + example-curator. |
| Migration guide | "Migrar de v1 a v2" | Toca technical-writer + decision-recorder. |
| Changelog | "v1.5.0 release notes" | Toca technical-writer + changelog-curator. |

Cualquiera de las 5 ejercita el flujo completo en <2 horas.

---

## Troubleshooting específico de docs

### "Doc Reviewer aprueba pero los links se rompen en producción"

Doc Reviewer no ejecuta link checking automáticamente (depende del
verify_stack). Asegúrate de que `lychee` (o equivalente) está en el
verify_stack del Verifier — ver "Cómo modificar".

### "Glossary Keeper detectó muchos términos pero la mayoría son falsos positivos"

Edita la heurística del agente:

```bash
vi .claude/agents/docs/glossary-keeper.md
# Modifica el "Heurística objetiva" según tu proyecto:
# - umbral de frecuencia (≥3 usos por defecto, sube a ≥5 si tu repo es grande)
# - lista de términos estándar a excluir
```

### "Example Curator no puede ejecutar mis ejemplos porque requieren credenciales"

El agente respeta esto: marca como `# requires: credentials` en el
ejemplo y no lo ejecuta. Anótalo en `examples-run.md` como `skipped`.

### "Changelog Curator añadió entradas internas"

Anti-pattern conocido. Edita el agente para reforzar:

```bash
vi .claude/agents/docs/changelog-curator.md
# En anti-patterns ya está "Entradas internas: 'refactor del módulo X'".
# Si tu IA lo está violando, añade al prompt:
# "Antes de escribir la entrada, pregúntate: ¿un usuario externo nota
#  esto? Si no, NO lo añadas al CHANGELOG."
```

---

## Próximos pasos

1. Lee [`../../docs/best-practices.md`](../../docs/best-practices.md)
   sección "Sizing de features" — la sizing en docs es distinta (un
   archivo bien escrito puede ser una feature entera).
2. Configura tu docs site (MkDocs / Docusaurus / Hugo / etc.) si aún
   no está.
3. Considera añadir hooks que ejecuten `markdownlint` en cada save.
4. Si el alcance crece más allá de docs (ej. tutoriales con código
   ejecutable), considera añadir `harness add-domain software` para
   tener test-engineer disponible.
