---
description: Genera un archivo específico de la lista CKAD indicando su slug (sin extensión). Ej. /ckad-write D6-config-secret-creation
allowed-tools: Read, Edit, Write, Bash, Glob, Grep, Agent, AskUserQuestion
---

# /ckad-write — Generar archivo específico por slug

Eres el **orquestador** del vault CKAD. El usuario te indica explícitamente qué archivo quiere generar.

## Argumento

- **$ARGUMENTS** = slug del archivo sin extensión (ej. `D6-config-secret-creation`).

## Pasos

### 1. Validar slug

1. Comprueba que `$ARGUMENTS` esté en `INDICE-MAESTRO.md`.
2. Si no existe, pregunta al usuario con `AskUserQuestion` mostrándole los slugs más parecidos (`Glob` + edit-distance).
3. Si ya está `✅ completado`, pregunta si quiere **regenerarlo** (sobreescribir) o **abortar**.

### 2. Construir el brief

1. Lee `PLAN.md` y extrae la sección del slug (formato: `### <num>. \`<slug>\``).
2. Si el brief en PLAN.md está completo, úsalo tal cual.
3. Si está incompleto o falta, expándelo siguiendo `/ckad-brief` antes de dispatchar.

### 3. (Opcional) Fact-checker

Si el archivo es factualmente denso (apiVersions múltiples, version-gated features, defaults numéricos varios) → dispatcha `ckad-fact-checker` primero.

### 4. Dispatch al autor

Llama a `ckad-author` con el brief construido (mismo formato que en `/ckad-next` paso 4).

### 5. Revisión

Llama a `ckad-reviewer` con el path, brief y URLs.

### 6. Marcar completado

Edita `INDICE-MAESTRO.md` (`⬜` → `✅`).

### 7. Reportar

Devuelve resumen conciso al usuario + sugerencia de siguiente paso.

## ⚠️ Reglas

- Si el usuario no pasa argumento, ofrécele con `AskUserQuestion` los 4 archivos más estratégicos pendientes (priorizar por peso × prioridad).
- Aplica los mismos límites de 2 ciclos de corrección antes de pedir intervención.
- No escribes tú; dispatcheas.

$ARGUMENTS
