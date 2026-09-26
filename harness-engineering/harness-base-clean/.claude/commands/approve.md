---
description: Aprueba GATE#1 de una feature del harness (decisión humana). Uso /approve FEATURE-ID [alternativa o comentario]
argument-hint: "<FEATURE-ID> [alternativa o comentario]"
disable-model-invocation: true
---

Decisión humana explícita en GATE#1: **apruebo** la especificación. Argumentos: $ARGUMENTS

Como orquestador:

1. El primer argumento es el FEATURE-ID y el resto mi respuesta literal (puede
   indicar la alternativa elegida). Si falta el ID o la feature no está en
   `gate1_pending` (`python3 .claude/tools/feature.py status <ID>`), dímelo y no hagas nada más.
2. Registra la decisión con mi texto entre comillas simples (si contiene
   apóstrofos, usa comillas dobles y no incluyas `$` ni acentos graves):
   `python3 .claude/tools/feature.py transition <ID> approved --by human --response 'approve: <mi texto literal>'`
   Claude Code me pedirá confirmar el comando: esa confirmación es la firma del gate.
3. Si la transición se rechaza, muéstrame los motivos y para.
4. Si se acepta, continúa según el modo de `.claude/harness.toml`: en manual,
   dime el siguiente paso y espera; en auto o yolo, lanza el builder
   (`PHASE: implementation`, `ATTEMPT: 1`, `MODE: build`).
