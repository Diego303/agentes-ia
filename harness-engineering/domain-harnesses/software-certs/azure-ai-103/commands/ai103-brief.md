---
description: Expande el brief de un archivo del vault AI-103 (sustituye un esbozo escueto por una especificación quirúrgica lista para dispatchar a ai103-author). Útil cuando PLAN.md tiene solo el slug y necesitas detalle completo.
allowed-tools: Read, Edit, Write, WebSearch, WebFetch, Grep, AskUserQuestion
---

# /ai103-brief — Expandir brief de archivo

Eres el **orquestador**. Tu tarea: tomar un slug y producir un brief **exhaustivo y autosuficiente** que un agente con contexto limpio pueda usar para escribir el archivo perfecto.

## Argumento

- **$ARGUMENTS** = slug del archivo sin extensión.

## Pasos

### 1. Localizar el slug

1. Lee `INDICE-MAESTRO.md` y `PLAN.md`.
2. Encuentra la fila/sección del slug.

### 2. Cross-reference con temario oficial

1. Identifica qué sub-puntos del **AI-103 skills measured** (URL: https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-103) cubre este archivo.
2. Si aplica AI-102 carryover, identifica también los sub-puntos del AI-102 (URL: https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-102) que aplican.

### 3. Identificar URLs oficiales a verificar

Lista las URLs de Microsoft Learn que el autor debe consultar antes de escribir.

### 4. Identificar wikilinks

Busca en el vault (`Grep "$ARGUMENTS"`) qué archivos ya escritos referencian este slug, para mantener bidireccionalidad.

### 5. Identificar trampas examen

A partir del temario y de las trampas conocidas (consulta archivos ya escritos del dominio), lista las trampas específicas que el archivo debe abordar.

### 6. Identificar snippets requeridos

- Python (siempre, audience AI-103).
- Azure CLI (si hay provisioning/management).
- Bicep (si hay infraestructura).
- REST (si endpoints clave).

### 7. Identificar diagramas mermaid

- timeline, flowchart, sequence, pie, graph: cuáles encajan.

### 8. Output

Devuelve un brief completo en el formato exacto del prompt para `ai103-author` (ver `/ai103-next` paso 4).

Si PLAN.md ya tenía un brief escueto, **edita PLAN.md** para sustituirlo por el brief expandido (preserva el resto del archivo).

### 9. Reglas

- **No escribas el archivo .md**. Solo el brief.
- El brief debe ser tan completo que el autor no necesite preguntarte nada.
- Si encuentras ambigüedad seria (ej. el archivo cubre dos sub-temas no relacionados), propón al usuario fusionar o dividir con `AskUserQuestion`.

$ARGUMENTS
