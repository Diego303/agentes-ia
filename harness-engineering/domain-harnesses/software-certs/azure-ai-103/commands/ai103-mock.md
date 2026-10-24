---
description: Genera un mock exam estilo Microsoft AI-103 (case studies + multi-choice + drag-drop + ordering + hot-area). Argumento opcional: slug o dominio (e.g., "B.2", "domain-a", "all"). Si no se pasa argumento, ofrece opciones.
allowed-tools: Read, Write, Bash, Glob, Grep, Agent, AskUserQuestion
---

# /ai103-mock — Generar mock exam

Eres el orquestador. El usuario pide un simulacro de examen AI-103.

## Argumento

- **$ARGUMENTS** = scope (slug, sub-dominio o `all`).
- Si no se pasa, ofrece con `AskUserQuestion`: el archivo top más reciente, su sub-dominio entero, su dominio entero, o `all`.

## Pasos

1. Resolver scope a lista de archivos source (usa `Glob` + paths conforme a la estructura jerárquica del vault).
2. Confirmar con usuario num_questions (default 15).
3. Dispatch `ai103-mock-exam-builder` con:
   - scope explícito
   - lista de archivos source
   - output path (`00-Mock-Exams/mock-<scope>-<YYYYMMDD>.md`)
   - num_questions
4. Esperar reporte del agente.
5. Mostrar al usuario:
   - Path generado.
   - Conteo de preguntas por formato y difficulty.
   - Duración recomendada.
   - Sugerencia: "Cronómetro X min, simula condiciones de examen real (sin docs abiertos)."

## Reglas

- **No generes mock exam tú mismo** — dispatcha el agente.
- **Confirma scope** si es ambiguo.
- **Crea dir `00-Mock-Exams/`** si no existe (mkdir -p).
- Si scope es `all` con >50 archivos → confirma con usuario antes de proceder (será exam largo).

$ARGUMENTS
