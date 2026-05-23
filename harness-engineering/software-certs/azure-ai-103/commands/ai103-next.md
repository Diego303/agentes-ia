---
description: Genera el siguiente archivo pendiente de la lista AI-103 (lee INDICE-MAESTRO.md + PLAN.md, elige el siguiente ⬜ pendiente según orden pedagógico, dispatchа ai103-author, revisa con ai103-reviewer, marca completado).
allowed-tools: Read, Edit, Write, Bash, Glob, Grep, Agent, AskUserQuestion
---

# /ai103-next — Generar siguiente archivo pendiente

Eres el **orquestador** del vault AI-103. Tu misión es producir el siguiente archivo de apuntes con la misma calidad quirúrgica que los anteriores.

## Pasos a ejecutar

### 1. Identificar el siguiente archivo

1. Lee `/mnt/d/GitHub/LOCAL/DIEGO/APUNTES/AI-103/INDICE-MAESTRO.md`.
2. Identifica los archivos con estado `⬜ pendiente`.
3. Elige el siguiente según el **orden pedagógico recomendado** del propio índice (foundational → A → B → E → C → D → carryover AI-102).
4. Si hay varios candidatos al mismo nivel, ofrece al usuario una selección con `AskUserQuestion` proponiendo los 3-4 más relevantes.

### 2. Construir el brief

1. Lee `/mnt/d/GitHub/LOCAL/DIEGO/APUNTES/AI-103/PLAN.md`.
2. Extrae la sección del slug elegido (formato: bloque entre `## <slug>` y el siguiente `## `).
3. Si el brief es escueto, **expándelo siguiendo /ai103-brief** antes de dispatchar.

### 3. (Opcional) Pre-verificación fáctica

Si el archivo tiene **muchos hechos críticos** a verificar (deployment types, providers ARM, SDK classes, comandos CLI):

1. Dispatcha `ai103-fact-checker` con la lista de hechos y URLs.
2. Espera su dossier.
3. Inclúyelo en el brief para el autor.

### 4. Dispatch al autor

Llama a `ai103-author` con el siguiente prompt (sustituye `<...>`):

```
BRIEF:
- slug: <slug>
- path: /mnt/d/GitHub/LOCAL/DIEGO/APUNTES/AI-103/<slug>.md
- dominio: <A|B|C|D|E|0-foundational> + descripción
- peso_en_examen: <X-Y %>
- dificultad: <baja|media|alta>
- sub-puntos temario AI-103 cubiertos (verbatim):
  - <punto 1>
  - <punto 2>
  - ...
- AI-102 carryover: <sí/no, qué partes>
- URLs oficiales a verificar:
  - <URL 1>
  - <URL 2>
- wikilinks de salida sugeridos:
  - [[archivo-1]]
  - [[archivo-2]]
- trampas examen específicas a abordar:
  - <trampa 1>
  - <trampa 2>
- snippets de código requeridos:
  - Python: <qué patrón>
  - Azure CLI: <qué comando>
  - Bicep: <sí/no>
  - REST: <sí/no>
- diagramas mermaid esperados:
  - <tipo y propósito>

DOSSIER VERIFICADO (si fact-checker corrió):
<contenido del dossier>

INSTRUCCIÓN: Aplica ultrathink, ciclo de 3 iteraciones + rúbrica. Solo entrega cuando todas las dimensiones ≥ 9. Escribe en el path indicado.
```

### 5. Revisión

Una vez el autor entregue:

1. Dispatcha `ai103-reviewer` con:
   - Path al archivo recién escrito.
   - El brief original.
   - URLs oficiales.

2. Espera el dictamen:
   - **✅ APROBADO** → ir al paso 6.
   - **⚠️ APROBADO CON OBSERVACIONES** → si observaciones son menores, marcar completado; si son significativas, ir a re-dispatch.
   - **❌ RECHAZADO** → re-dispatchar `ai103-author` con las acciones correctivas del reviewer. Max 2 ciclos de corrección antes de pedir intervención al usuario.

### 6. Marcar completado

1. Edita `INDICE-MAESTRO.md` cambiando el estado del archivo de `⬜` a `✅`.
2. Si PLAN.md tracking lleva contador, actualiza también.

### 7. Reportar al usuario

Devuelve al usuario un mensaje **conciso** (< 250 palabras) que incluya:

- Path del archivo entregado.
- Highlights (3-5 bullets).
- Rúbrica final del autor + dictamen del reviewer.
- Próximo archivo sugerido (siguiente en orden pedagógico).
- Pregunta con `AskUserQuestion` si continuar (`/ai103-next`) o cambiar de archivo (`/ai103-write <slug>`).

## ⚠️ Reglas

- **No escribas el archivo tú mismo**. Dispatcha al autor.
- **No saltes la revisión** salvo que el usuario te lo indique explícitamente.
- **No batch sin permiso**: este comando produce **un solo** archivo. Para múltiples, usa `/ai103-batch`.
- Si todos los archivos están ✅, felicita al usuario y sugiere `/ai103-status` para revisar.

$ARGUMENTS
