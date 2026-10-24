---
name: harness-doctor
description: Diagnostica la integridad del harness - contratos, agentes, skills, hooks, configuración, estados, gates y artefactos - con el validador determinista y sus tests. Úsala cuando se pida auditar, validar o reparar el harness, después de modificarlo, o cuando una transición se rechace y no esté claro por qué.
---

# Harness Doctor

## Procedimiento

1. `python3 .claude/tools/validate_harness.py --json` (bundle y todas las features).
2. `python3 -m unittest discover -s .claude/tests -v` (tests de las herramientas).
3. Separa los errores del harness (configuración, contrato, agentes, skills,
   hooks) de los fallos de una feature (`--feature <ID>`).
4. Revisa `.claude/state/hook-errors.log`: errores de `guard.py` o `ledger.py`.
5. Comprueba que los hooks funcionan: tras cualquier subagente lanzado con la
   cabecera `FEATURE_ID`, `event.log` debe tener un `subagent_stop` con tokens
   mayores que cero.
6. Explica cada error: archivo, regla incumplida y corrección mínima.
7. Modifica archivos solo si el humano pidió reparar; después vuelve a validar
   y a pasar los tests.

## Salida

- `PASS` o `FAIL`
- errores y avisos con su corrección mínima
- comandos ejecutados para verificarlo

## Límites

- No declares sano el harness por inspección visual.
- No reescribas estado histórico para ocultar una inconsistencia: usa
  transiciones (`escalate`, `replan`, `cancel`).
- Los avisos no son errores; no los conviertas en bloqueantes.
