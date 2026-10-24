---
description: Genera un lote de archivos del vault AI-103 en serie (mismo dominio o lista específica). Útil para avanzar masa pero asume aprobación previa del usuario para no preguntar entre archivos. Ej. /ai103-batch A.1 o /ai103-batch plan-security
allowed-tools: Read, Edit, Write, Bash, Glob, Grep, Agent, AskUserQuestion
---

# /ai103-batch — Generar lote de archivos en serie

Eres el **orquestador**. El usuario te pide producir varios archivos seguidos.

## Argumento

- **$ARGUMENTS** = patrón de selección:
  - **Sub-área** (ej. `A.1`, `B.2`, `C.3`) → todos los archivos de esa sub-sección.
  - **Prefix de slug** (ej. `plan-security`) → todos los archivos que empiezan así.
  - **Lista explícita** separada por comas (ej. `plan-deployment-options-models-agents,plan-quotas-scaling-rate-limits`).
  - **Dominio completo** (ej. `domain-a`) → con confirmación del usuario por el volumen.

## Pasos

### 1. Resolver el set

1. Lee `INDICE-MAESTRO.md` y aplica el patrón.
2. Filtra solo los `⬜ pendientes`.
3. Lista los slugs resultantes.

### 2. Confirmación

Con `AskUserQuestion` muestra:
- Lista de slugs a generar.
- Total esperado.
- Tiempo estimado (~5-10 min por archivo en serie).
- Coste aproximado en consumo de tokens.

Pregunta confirmación: proceder / acotar / cancelar.

### 3. Loop de generación

Para cada slug en el set:

1. Construye el brief (siguiendo `/ai103-brief` internamente).
2. (Opcional) Dispatcha `ai103-fact-checker` si denso en hechos.
3. Dispatcha `ai103-author`.
4. Dispatcha `ai103-reviewer`.
5. Si dictamen ❌, re-dispatchar autor con correcciones (max 2 intentos por archivo).
6. Si tras 2 intentos sigue rechazado, **detén el batch** y reporta al usuario.
7. Marca `✅` en INDICE-MAESTRO.
8. Reporta progreso intermedio brevemente (1 línea).

### 4. Reporte final

Output al usuario con:

- Archivos completados (lista).
- Archivos pendientes en el set (si abortado).
- Rúbricas medias de las 4 dimensiones.
- Sugerencia de siguiente paso.

## ⚠️ Reglas

- **NUNCA generes batch sin confirmación previa**.
- **Detén el batch** si 3 archivos consecutivos requieren más de 1 ciclo de corrección — indica deriva de calidad.
- **Mantén contexto del orquestador limpio**: confía en el agente, no leas su output completo; lee el reporte conciso y el archivo en disco.
- Si el batch es muy grande (>10 archivos), divide en sub-batches y pide check-in cada 5.

$ARGUMENTS
