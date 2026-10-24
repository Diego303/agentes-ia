---
description: Genera un mock exam estilo CKAD (performance-based hands-on + multi-choice conceptual + troubleshooting scenarios). Argumento opcional: slug o dominio (e.g., "D.6", "domain-d", "all"). Si no se pasa argumento, ofrece opciones.
allowed-tools: Read, Write, Bash, Glob, Grep, Agent, AskUserQuestion
---

# /ckad-mock — Generar mock exam CKAD

Eres el orquestador. El usuario pide un simulacro de examen CKAD.

## Argumento

- **$ARGUMENTS** = scope (slug, sub-dominio o `all`).
- Si no se pasa, ofrece con `AskUserQuestion`: el archivo top más reciente, su sub-dominio entero, su dominio entero, o `all`.

## Pasos

1. Resolver scope a lista de archivos source (usa `Glob` + paths conforme a la estructura jerárquica del vault).
2. Confirmar con usuario num_questions (default 15).
3. Dispatch `ckad-mock-exam-builder` con:
   - scope explícito
   - lista de archivos source
   - output path (`00-Mock-Exams/mock-<scope>-<YYYYMMDD>.md`)
   - num_questions
4. Esperar reporte del agente.
5. Mostrar al usuario:
   - Path generado.
   - Conteo de tareas por formato (performance create / modify / troubleshooting / multi-step scenario / conceptual).
   - Difficulty distribution (30 % baja / 50 % media / 20 % alta).
   - Duración recomendada (~6 min por tarea).
   - Sugerencia: "Cronómetro X min, simula condiciones reales. Permitido: kubernetes.io/docs/, helm.sh/docs/. No otros sitios."

## Reglas

- **No generes mock exam tú mismo** — dispatcha el agente.
- **Confirma scope** si es ambiguo.
- **Crea dir `00-Mock-Exams/`** si no existe (mkdir -p).
- Si scope es `all` con >50 archivos → confirma con usuario antes de proceder (será exam largo).
- CKAD real es **hands-on**, optimiza para tareas performance > conceptual (80/20).

$ARGUMENTS
