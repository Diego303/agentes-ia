---
description: Rechaza GATE#1 y pide cambios al designer (decisión humana). Uso /reject FEATURE-ID cambios-concretos
argument-hint: "<FEATURE-ID> <cambios concretos>"
disable-model-invocation: true
---

Decisión humana explícita en GATE#1: **pido cambios** en la especificación. Argumentos: $ARGUMENTS

Como orquestador:

1. El primer argumento es el FEATURE-ID y el resto los cambios que pido. Si no
   hay cambios concretos, pídemelos antes de hacer nada.
2. Registra la decisión con mi texto entre comillas simples (si contiene
   apóstrofos, usa comillas dobles y no incluyas `$` ni acentos graves):
   `python3 .claude/tools/feature.py transition <ID> changes_requested --by human --response '<mis cambios literales>'`
   Claude Code me pedirá confirmar el comando.
3. Relanza el designer (`PHASE: design`) indicando que es una revisión: leerá
   mis cambios en `state.yaml` (`gate1.response`) y modificará solo lo pedido.
4. Cuando termine, vuelve a presentar GATE#1.
