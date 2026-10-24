---
description: Revisa un archivo ya generado del vault AI-103 con ai103-reviewer y reporta dictamen y acciones correctivas si aplica.
allowed-tools: Read, Edit, Bash, Agent, AskUserQuestion
---

# /ai103-review — Revisar archivo existente

Eres el **orquestador**. El usuario te pide revisar (re-revisar) un archivo ya generado.

## Argumento

- **$ARGUMENTS** = slug del archivo sin extensión.

## Pasos

### 1. Localizar archivo y brief

1. Comprueba que el archivo `<slug>.md` exista.
2. Lee la sección de PLAN.md correspondiente al slug.

### 2. Dispatch al reviewer

Llama a `ai103-reviewer` con:
- Path al archivo.
- Brief original.
- URLs oficiales para cross-check.

### 3. Procesar dictamen

- **✅ APROBADO** → confirma estado `✅` en INDICE-MAESTRO.
- **⚠️ APROBADO CON OBSERVACIONES** → pregunta al usuario si quiere aplicar las mejoras sugeridas (dispatchar autor con observaciones) o aceptar como está.
- **❌ RECHAZADO** → pregunta al usuario si quiere re-generar con las acciones correctivas (dispatchar autor) o intervenir manualmente.

### 4. Reportar

Output al usuario:
- Dictamen final.
- Rúbrica con notas en cada dimensión.
- Observaciones/errores específicos.
- Acciones tomadas o sugeridas.

$ARGUMENTS
