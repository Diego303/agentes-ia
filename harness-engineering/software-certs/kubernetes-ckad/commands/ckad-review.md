---
description: Revisa un archivo ya generado del vault CKAD con ckad-reviewer y reporta dictamen y acciones correctivas si aplica.
allowed-tools: Read, Edit, Bash, Agent, AskUserQuestion
---

# /ckad-review — Revisar archivo existente

Eres el **orquestador**. El usuario te pide revisar (re-revisar) un archivo ya generado.

## Argumento

- **$ARGUMENTS** = slug del archivo sin extensión.

## Pasos

### 1. Localizar archivo y brief

1. Comprueba que `<slug>.md` exista (busca en su carpeta declarada en INDICE).
2. Lee la sección de PLAN.md correspondiente al slug.

### 2. Dispatch al reviewer

Llama a `ckad-reviewer` con:
- Path al archivo.
- Brief original.
- URLs oficiales para cross-check (kubernetes.io/docs/...).

### 3. Procesar dictamen

- **✅ APROBADO** → confirma estado `✅` en INDICE-MAESTRO.
- **⚠️ APROBADO CON OBSERVACIONES** → pregunta al usuario si quiere aplicar las mejoras sugeridas (dispatchar autor con observaciones) o aceptar como está.
- **❌ RECHAZADO** → pregunta al usuario si quiere re-generar con las acciones correctivas (dispatchar autor) o intervenir manualmente.

### 4. Reportar

Output al usuario:
- Dictamen final.
- Rúbrica con notas en cada dimensión (Completitud / Exactitud / Alineación examen hands-on CKAD / Pedagogía).
- Observaciones/errores específicos.
- Acciones tomadas o sugeridas.

$ARGUMENTS
