---
description: Quiz corto (3-5 preguntas) sobre un tema específico. Útil para self-test rápido durante estudio. Dispatch ai103-mock-exam-builder con num_questions=5 y scope = slug.
allowed-tools: Read, Bash, Glob, Grep, Agent
---

# /ai103-quiz — Quiz corto sobre tema

## Argumento

- **$ARGUMENTS** = slug obligatorio (sin .md) — un solo archivo.

## Pasos

1. Verificar `<slug>.md` existe.
2. Dispatch `ai103-mock-exam-builder` con:
   - scope = `<slug>` (un solo archivo)
   - num_questions = 5
   - output a buffer (NO escribe a disk; queremos respuesta inline)
3. Mostrar al usuario las 5 preguntas + cronómetro mental sugerido (7-10 min).
4. Tras respuestas del usuario, mostrar el answer key + sources.

## Reglas

- Si el archivo no existe, sugiere los 3 más parecidos por nombre.
- Quizzes son rápidos, NO sustituyen mock exams.

$ARGUMENTS
