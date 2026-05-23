---
description: Genera un archivo específico de la lista AI-103 indicando su slug (sin extensión). Ej. /ai103-write plan-deployment-options-models-agents
allowed-tools: Read, Edit, Write, Bash, Glob, Grep, Agent, AskUserQuestion
---

# /ai103-write — Generar archivo específico por slug

Eres el **orquestador** del vault AI-103. El usuario te indica explícitamente qué archivo quiere generar.

## Argumento

- **$ARGUMENTS** = slug del archivo sin extensión (ej. `plan-deployment-options-models-agents`).

## Pasos

### 1. Validar slug

1. Comprueba que `$ARGUMENTS` esté en `INDICE-MAESTRO.md`.
2. Si no existe, pregunta al usuario con `AskUserQuestion` mostrándole los slugs más parecidos (`Glob` + edit-distance).
3. Si ya está `✅ completado`, pregunta si quiere **regenerarlo** (sobreescribir) o **abortar**.

### 2. Construir el brief

1. Lee `PLAN.md` y extrae la sección del slug.
2. Si el brief en PLAN.md es escueto o falta, expándelo siguiendo `/ai103-brief` antes de dispatchar.

### 3. (Opcional) Fact-checker

Si el archivo es factualmente denso → dispatcha `ai103-fact-checker` primero.

### 4. Dispatch al autor

Llama a `ai103-author` con el brief construido (mismo formato que en `/ai103-next`).

### 5. Revisión

Llama a `ai103-reviewer` con el path, brief y URLs.

### 6. Marcar completado

Edita `INDICE-MAESTRO.md` (`⬜` → `✅`).

### 7. Reportar

Devuelve resumen conciso al usuario + sugerencia de siguiente paso.

## ⚠️ Reglas

- Si el usuario no pasa argumento, ofrécele con `AskUserQuestion` los 4 archivos más estratégicos pendientes.
- Aplica los mismos límites de 2 ciclos de corrección antes de pedir intervención.
- No escribes tú; dispatcheas.

$ARGUMENTS
