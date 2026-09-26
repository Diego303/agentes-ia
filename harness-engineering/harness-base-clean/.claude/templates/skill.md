---
name: nombre-de-la-skill
description: Qué hace y cuándo usarla, con las frases o situaciones que deben activarla. Menciona también cuándo NO usarla si hay skills parecidas. Máximo 1536 caracteres.
---

# nombre-de-la-skill

<!--
Plantilla de skill (no se descubre desde aquí). Para crear una:
1. Copia este archivo a .claude/skills/<nombre>/SKILL.md (el nombre de la carpeta
   es el comando /<nombre> y debe coincidir con `name`).
2. Opcional en el frontmatter:
   - disable-model-invocation: true   solo el humano la invoca (coste de contexto cero)
   - argument-hint: "[FEATURE-ID]"    ayuda de autocompletado
   - allowed-tools: Read, Grep         herramientas preaprobadas durante la skill
3. Para precargarla en un agente: añade su nombre a `skills:` en el frontmatter del agente.
4. python3 .claude/tools/validate_harness.py
Guía completa: skill skill-creator. Mantén el cuerpo por debajo de ~200 líneas y
mueve el detalle a archivos de la carpeta que se lean bajo demanda.
-->

## Resultado

Qué deja hecho la skill cuando termina.

## Procedimiento

1. Pasos concretos, en imperativo, explicando el porqué cuando no sea obvio.

## Límites

- Lo que la skill no hace y cuándo debe parar.
