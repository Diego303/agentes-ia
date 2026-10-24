---
description: Genera flashcards Anki (TSV) desde archivo(s) del vault CKAD. Argumento: slug específico, sub-dominio o domain. Output 00-Aggregations/flashcards-<scope>.tsv + README de import.
allowed-tools: Read, Write, Bash, Glob, Grep, Agent
---

# /ckad-flashcards — Generar flashcards Anki CKAD

## Argumento

- **$ARGUMENTS**: slug, sub-dominio, dominio, `all`.

## Pasos

1. Validar scope.
2. Crear dir `00-Aggregations/` si no existe.
3. Dispatch `ckad-flashcard-generator` con scope y output path.
4. Esperar reporte.
5. Mostrar al usuario:
   - TSV path + README path.
   - Conteo total + breakdown por tipo (definición / comparativa / comando kubectl / trampa / recall / valor-exacto / apiVersion-lookup / YAML-field-path).
   - Quick instructions: `File → Import → seleccionar .tsv → mapear Front/Back/Tags → Import`.

## Reglas

- Si scope produce >100 cards → confirmar con usuario antes de generar (sesión Anki larga).
- TSV en UTF-8 con escape de comillas `""` para Anki compat.
- Para CKAD hands-on, asegura que al menos 30 % de las cards sean **comando kubectl exacto** y **YAML field path** (recall activo de tipeo).

$ARGUMENTS
