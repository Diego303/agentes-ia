---
description: Genera el siguiente archivo pendiente de la lista CKAD (lee INDICE-MAESTRO.md + PLAN.md, elige el siguiente ⬜ pendiente según orden pedagógico, dispatchа ckad-author, revisa con ckad-reviewer, marca completado).
allowed-tools: Read, Edit, Write, Bash, Glob, Grep, Agent, AskUserQuestion
---

# /ckad-next — Generar siguiente archivo pendiente

Eres el **orquestador** del vault CKAD. Tu misión es producir el siguiente archivo de apuntes con la misma calidad quirúrgica que los anteriores.

## Pasos a ejecutar

### 1. Identificar el siguiente archivo

1. Lee `/mnt/d/GitHub/LOCAL/DIEGO/APUNTES/ckad/INDICE-MAESTRO.md`.
2. Identifica los archivos con estado `⬜ pendiente`.
3. Elige el siguiente según el **orden pedagógico recomendado** del propio índice (00-Foundational → D (25 %) → A → B → E → C). Esto está documentado al final del INDICE.
4. Si hay varios candidatos al mismo nivel, ofrece al usuario una selección con `AskUserQuestion` proponiendo los 3-4 más relevantes por prioridad declarada (🔥🔥🔥).

### 2. Construir el brief

1. Lee `/mnt/d/GitHub/LOCAL/DIEGO/APUNTES/ckad/PLAN.md`.
2. Extrae la sección del slug elegido (formato: bloque `### <num>. \`<slug>\`` hasta el siguiente `###`).
3. El brief de PLAN.md ya es completo. Si por alguna razón está incompleto, **expándelo siguiendo `/ckad-brief`** antes de dispatchar.
4. Lee el archivo semilla de `apuntes-base/` declarado en el brief (si existe).

### 3. (Opcional) Pre-verificación fáctica

Si el archivo tiene **muchos hechos críticos** a verificar (apiVersions múltiples, defaults numéricos, version-gated features):

1. Dispatcha `ckad-fact-checker` con la lista de hechos y URLs.
2. Espera su dossier.
3. Inclúyelo en el brief para el autor.

### 4. Dispatch al autor

Llama a `ckad-author` con el siguiente prompt (sustituye `<...>`):

```
BRIEF:
- slug: <slug>
- path: /mnt/d/GitHub/LOCAL/DIEGO/APUNTES/ckad/<dominio>/<sub>/<slug>.md
- dominio: <00-foundational|A-design-build|B-deployment|C-observability|D-environment-config-security|E-services-networking> + descripción
- peso_en_examen: <X %>
- dificultad: <baja|media|alta>
- prioridad_examen: <🔥🔥🔥|🔥🔥|🔥>
- sub-puntos curriculum CKAD oficial cubiertos (verbatim de cncf.io / training.linuxfoundation.org):
  - <punto 1>
  - <punto 2>
- semilla apuntes-base: <path o N/A>
- URLs oficiales a verificar:
  - https://kubernetes.io/docs/...
  - https://kubernetes.io/docs/...
- wikilinks de salida sugeridos:
  - [[slug-relacionado-1]]
  - [[slug-relacionado-2]]
- trampas examen específicas a abordar:
  - <trampa 1>
  - <trampa 2>
- snippets de código requeridos:
  - kubectl imperativo: <qué patrón>
  - YAML manifest: <qué kind>
  - Helm: <sí/no>
  - Kustomize: <sí/no>
  - Dockerfile: <sí/no>
- diagramas mermaid esperados:
  - <tipo y propósito>

DOSSIER VERIFICADO (si fact-checker corrió):
<contenido del dossier>

INSTRUCCIÓN: Aplica ultrathink, ciclo de 3 iteraciones + rúbrica. Solo entrega cuando todas las 4 dimensiones ≥ 9. Escribe en el path indicado.
```

### 5. Revisión

Una vez el autor entregue:

1. Dispatcha `ckad-reviewer` con:
   - Path al archivo recién escrito.
   - El brief original.
   - URLs oficiales (kubernetes.io/docs/).

2. Espera el dictamen:
   - **✅ APROBADO** → ir al paso 6.
   - **⚠️ APROBADO CON OBSERVACIONES** → si observaciones son menores, marcar completado y anotar en LOG DE BAJA CONFIANZA; si son significativas, ir a re-dispatch.
   - **❌ RECHAZADO** → re-dispatchar `ckad-author` con las acciones correctivas del reviewer. Max 2 ciclos de corrección antes de pedir intervención al usuario.

### 6. Marcar completado

1. Edita `INDICE-MAESTRO.md` cambiando el estado del archivo de `⬜` a `✅`.
2. Actualiza el dashboard del INDICE (contadores generales y por dominio).

### 7. Reportar al usuario

Devuelve al usuario un mensaje **conciso** (< 250 palabras) que incluya:

- Path del archivo entregado.
- Highlights (3-5 bullets).
- Rúbrica final del autor + dictamen del reviewer.
- Próximo archivo sugerido (siguiente en orden pedagógico).
- Pregunta con `AskUserQuestion` si continuar (`/ckad-next`) o cambiar de archivo (`/ckad-write <slug>`).

## ⚠️ Reglas

- **No escribas el archivo tú mismo**. Dispatcha al autor.
- **No saltes la revisión** salvo que el usuario te lo indique explícitamente.
- **No batch sin permiso**: este comando produce **un solo** archivo. Para múltiples, usa `/ckad-batch`.
- Si todos los archivos están ✅, felicita al usuario y sugiere `/ckad-validate` + `/ckad-coverage`.

$ARGUMENTS
