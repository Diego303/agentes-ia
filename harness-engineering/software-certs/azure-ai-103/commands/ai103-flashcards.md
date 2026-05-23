---
description: Genera flashcards Anki (TSV) desde archivo(s) del vault. Argumento: slug específico, sub-dominio o domain. Output 00-Aggregations/flashcards-<scope>.tsv + README de import.
allowed-tools: Read, Write, Bash, Glob, Grep, Agent
---

# /ai103-flashcards — Generar flashcards Anki

## Argumento

- **$ARGUMENTS**: slug, sub-dominio, dominio.

## Pasos

1. Validar scope.
2. Crear dir `00-Aggregations/` si no existe.
3. Dispatch `ai103-flashcard-generator` con scope y output path.
4. Esperar reporte.
5. Mostrar al usuario:
   - TSV path + README path.
   - Conteo total + breakdown por tipo (definición/comparativa/comando/trampa/recall).
   - Quick instructions: `File → Import → seleccionar .tsv → mapear campos → Import`.

## Reglas

- Si scope produce >100 cards → confirmar con usuario antes de generar (sesión Anki larga).
- TSV en UTF-8 con escape de comillas `""` para Anki compat.

$ARGUMENTS
