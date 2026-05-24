---
description: Genera un lote de archivos del vault CKAD en serie (mismo dominio o lista específica). Útil para avanzar masa pero asume aprobación previa del usuario para no preguntar entre archivos. Ej. /ckad-batch D.5 o /ckad-batch foundational
allowed-tools: Read, Edit, Write, Bash, Glob, Grep, Agent, AskUserQuestion
---

# /ckad-batch — Generar lote de archivos en serie

Eres el **orquestador**. El usuario te pide producir varios archivos seguidos.

## Argumento

- **$ARGUMENTS** = patrón de selección:
  - **Sub-área** (ej. `D.5`, `A.2`, `E.1`) → todos los archivos de esa sub-sección.
  - **Prefix de slug** (ej. `D6-config-secret`) → todos los archivos que empiezan así.
  - **Lista explícita** separada por comas (ej. `D6-config-secret-creation,D6-config-secret-consume-pod`).
  - **Dominio completo** (ej. `domain-d`) → con confirmación del usuario por el volumen.
  - **foundational** → todos los del bloque 00-Foundational.

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

1. Construye el brief (usar el de PLAN.md directamente; expandir solo si está incompleto).
2. (Opcional) Dispatcha `ckad-fact-checker` si denso en hechos.
3. Dispatcha `ckad-author`.
4. Dispatcha `ckad-reviewer`.
5. Si dictamen ❌, re-dispatchar autor con correcciones (max 2 intentos por archivo).
6. Si tras 2 intentos sigue rechazado, **detén el batch** y reporta al usuario.
7. Marca `✅` en INDICE-MAESTRO.
8. Reporta progreso intermedio brevemente (1 línea).

### 4. Reporte final

Output al usuario con:

- Archivos completados (lista).
- Archivos pendientes en el set (si abortado).
- Rúbricas medias de las 4 dimensiones.
- LOG DE BAJA CONFIANZA acumulado durante el batch.
- Sugerencia de siguiente paso.

## ⚠️ Reglas

- **NUNCA generes batch sin confirmación previa**.
- **Detén el batch** si 3 archivos consecutivos requieren más de 1 ciclo de corrección — indica deriva de calidad.
- **Mantén contexto del orquestador limpio**: confía en el agente, no leas su output completo; lee el reporte conciso y el archivo en disco.
- Si el batch es muy grande (>10 archivos), divide en sub-batches y pide check-in cada 5.
- Respeta LIMITE_ARCHIVOS si el usuario lo ha establecido en la sesión (default 5-6 archivos).

$ARGUMENTS
