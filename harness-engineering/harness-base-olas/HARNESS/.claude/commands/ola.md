---
description: Olas de features en paralelo con scripts/ola.sh. Uso /ola [siguiente | abrir ID-A ID-B | estado | integrar ID | continuar | abortar | cerrar ID]
argument-hint: "[siguiente | abrir ID-A ID-B | estado | integrar ID | continuar | abortar | cerrar ID]"
disable-model-invocation: true
---

Olas: $ARGUMENTS

Sigue la skill `olas`. Esta sesión es la del árbol principal y no lleva
ninguna feature.

- Sin argumentos o con `siguiente`: dime qué features se pueden abrir ahora
  (olas.md §6) y espera mi confirmación.
- `abrir …`, `estado`, `integrar …`, `cerrar …`: ejecuta la orden de
  `scripts/ola.sh` correspondiente.
- `continuar`: `integrar --continuar`.
- `abortar`: `integrar --abortar`.

Nunca uses `--si` ni hagas commits ni push: dame el comando y lo lanzo yo
con `!`. Si hay conflictos, resuélvelos según olas.md §5 y continúa.
