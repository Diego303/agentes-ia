---
description: Expande el brief de un archivo del vault CKAD (sustituye un esbozo escueto por una especificación quirúrgica lista para dispatchar a ckad-author). Útil cuando PLAN.md tiene solo el slug y necesitas detalle completo.
allowed-tools: Read, Edit, Write, WebSearch, WebFetch, Grep, AskUserQuestion
---

# /ckad-brief — Expandir brief de archivo

Eres el **orquestador**. Tu tarea: tomar un slug y producir un brief **exhaustivo y autosuficiente** que un agente con contexto limpio pueda usar para escribir el archivo perfecto.

## Argumento

- **$ARGUMENTS** = slug del archivo sin extensión.

## Pasos

### 1. Localizar el slug

1. Lee `INDICE-MAESTRO.md` y `PLAN.md`.
2. Encuentra la fila/sección del slug.

### 2. Cross-reference con curriculum oficial CKAD

1. Identifica qué sub-puntos del **CKAD curriculum oficial** (URL: https://www.cncf.io/training/certification/ckad/ y https://training.linuxfoundation.org/certification/certified-kubernetes-application-developer-ckad/) cubre este archivo.
2. WebFetch para verbatim del bullet relevante.
3. Si el archivo cubre un concepto **no en curriculum oficial pero relevante** (transversal), márcalo claramente.

### 3. Identificar URLs oficiales a verificar

Lista las URLs de `kubernetes.io/docs/` que el autor debe consultar antes de escribir. Patrones típicos:
- `kubernetes.io/docs/concepts/<area>/<topic>/`
- `kubernetes.io/docs/tasks/<area>/<topic>/`
- `kubernetes.io/docs/tutorials/<area>/<topic>/`
- `kubernetes.io/docs/reference/<area>/`

### 4. Identificar wikilinks

Busca en el vault (`Grep "$ARGUMENTS"`) qué archivos ya escritos referencian este slug, para mantener bidireccionalidad.

### 5. Identificar archivo semilla

Si existe `apuntes-base/<X>.md` que cubre el mismo concepto (per la columna "Semilla" en INDICE), incluye la ruta para que el autor lo lea como input pedagógico (la voz original del usuario).

### 6. Identificar trampas examen

A partir del curriculum y de las trampas conocidas (consulta archivos ya escritos del dominio o de archivos relacionados), lista las trampas específicas que el archivo debe abordar. Min 5.

### 7. Identificar snippets requeridos

- **kubectl imperativo**: el atajo de examen (siempre con `--dry-run=client -o yaml` cuando aplique).
- **YAML manifest**: kind exacto + spec completo.
- **Helm** (si concepto involucra Helm).
- **Kustomize** (si concepto involucra Kustomize).
- **Dockerfile** (si concepto involucra image build).

### 8. Identificar diagramas mermaid

- `flowchart`, `sequence`, `state`, `pie`, `mindmap`, `gantt`: cuáles encajan.

### 9. Output

Devuelve un brief completo en el formato exacto del prompt para `ckad-author` (ver `/ckad-next` paso 4).

Si PLAN.md ya tenía un brief escueto, **edita PLAN.md** para sustituirlo por el brief expandido (preserva el resto del archivo).

### 10. Reglas

- **No escribas el archivo .md**. Solo el brief.
- El brief debe ser tan completo que el autor no necesite preguntarte nada.
- Si encuentras ambigüedad seria (ej. el archivo cubre dos sub-temas no relacionados), propón al usuario fusionar o dividir con `AskUserQuestion`.

$ARGUMENTS
