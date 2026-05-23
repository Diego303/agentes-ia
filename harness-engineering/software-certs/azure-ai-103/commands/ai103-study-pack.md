---
description: Genera study pack agregado para revisión final (trampas, mnemónicos, snippets, cheatsheets, autotest). Argumento opcional: scope (all|domain|sub-dominio). Sin args → ofrece opciones.
allowed-tools: Read, Write, Bash, Glob, Grep, Agent, AskUserQuestion
---

# /ai103-study-pack — Generar pack de estudio agregado

Eres el orquestador. El usuario quiere materiales agregados para revisión.

## Argumento

- **$ARGUMENTS**: scope + opcional tipo.
  - `--scope all --type traps` → todas las trampas.
  - `--scope domain-a --type all` → todo agregado de Domain A.
  - sin args → pregunta con `AskUserQuestion` (scope + tipos).

## Pasos

1. Confirmar con usuario (si no pasó args completos):
   - **Scope**: archivo, sub-dominio, dominio, all.
   - **Tipos**: traps / mnemonics / snippets / autotest / cheatsheet / all.
2. Crear dir `00-Aggregations/` si no existe.
3. Dispatch `ai103-study-aggregator` con scope + types.
4. Esperar reporte.
5. Mostrar al usuario:
   - Archivos generados (lista).
   - Conteo de items por tipo.
   - Páginas estimadas.
   - Sugerencia de uso (cuándo repasar cada tipo).

## Tipos sugeridos según fase de estudio

- **3 semanas antes**: `--type all --scope all` (cheatsheets + traps).
- **1 semana antes**: `--type traps` (revisar trampas).
- **2 días antes**: `--type mnemonics` (recall rápido).
- **Día antes**: cheatsheet del dominio más pesado (B).

$ARGUMENTS
