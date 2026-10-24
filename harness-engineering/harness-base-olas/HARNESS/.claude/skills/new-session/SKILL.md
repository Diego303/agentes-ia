---
name: new-session
description: Genera un prompt de traspaso para continuar en una sesión nueva con todo el contexto que no está en disco. Solo la invoca el humano con /new-session, normalmente cuando falla el canario o el contexto está alto.
disable-model-invocation: true
argument-hint: "[foco opcional de la próxima sesión]"
---

# New session (handoff)

## Resultado

`.claude/handoff/<AAAAMMDD-HHMM>.md` con un prompt autocontenido, y el mismo
prompt en un bloque de código en tu respuesta.

## Procedimiento

1. Recoge el estado real, sin suponer nada:
   - `python3 .claude/tools/feature.py status` y `status <ID>` de cada feature activa o bloqueada.
   - `git status --porcelain` y `git log --oneline -5`.
   - `date +%Y%m%d-%H%M` para el nombre del archivo.
2. Repasa la conversación y extrae solo lo que no está en disco:
   - decisiones del humano y su motivo;
   - preferencias o restricciones que ha expresado;
   - trabajo a medias (qué, dónde, en qué punto);
   - hipótesis y hallazgos, separados en **verificado** (con evidencia: comando o archivo) y **sin verificar**;
   - lo que se descartó y por qué, para no repetirlo.
3. Escribe el prompt con la plantilla de abajo. Para lo que ya está en
   `.claude/state/<ID>/`, pon la ruta y no copies el contenido. Máximo unas 80 líneas.
4. Guárdalo en `.claude/handoff/<fecha>.md` y muéstralo íntegro en un bloque
   de código. Si $ARGUMENTS trae un foco, úsalo como objetivo.
5. Termina con: "Abre una sesión nueva (/clear) y pega el prompt".

## Plantilla

```text
Diego · Continúo una sesión anterior. Eres el orquestador del harness
(CLAUDE.md y HARNESS.md siguen vigentes).

## Objetivo
<qué se busca conseguir en esta sesión, en 1-3 líneas>

## Estado del harness
<por feature: ID, fase, GATE#1, siguiente acción (de feature.py status)>
Artefactos: .claude/state/<ID>/...

## Decisiones tomadas (no reabrir)
- <decisión> — <motivo>

## Preferencias del humano
- <...>

## Trabajo a medias
- <qué, archivo:línea, en qué punto quedó>

## Hallazgos
- Verificado: <hecho> (evidencia: <comando/archivo>)
- Sin verificar: <hipótesis>

## Descartado
- <opción> — <por qué>

## Siguiente paso exacto
<la primera acción concreta que debes hacer>

## No hacer
- <riesgos o atajos a evitar>

Antes de actuar: ejecuta `feature.py status`, confirma que el estado coincide
con este resumen y dime en 3 líneas qué vas a hacer.
```

## Límites

- No cambies el estado del flujo ni edites artefactos de features.
- No inventes: si algo no se puede comprobar, va en "Sin verificar".
- Nada de secretos ni contenido de `.env` en el handoff.
