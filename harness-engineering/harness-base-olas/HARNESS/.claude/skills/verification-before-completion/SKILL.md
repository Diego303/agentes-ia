---
name: verification-before-completion
description: Impide afirmar que una tarea está terminada sin evidencia reciente. Úsala antes de decir completado, arreglado, verificado, listo o PASS, antes de devolver un informe con RESULT completed y antes de archivar una feature o entregar cambios de código.
---

# Verification Before Completion

## Regla

Una afirmación de finalización necesita una comprobación ejecutada sobre la
versión actual del trabajo y su resultado completo. Sin evidencia no hay "hecho".

## Procedimiento

1. Identifica los criterios obligatorios y sus comandos o procedimientos (en el
   harness: `acceptance.yaml` y la regresión del proyecto).
2. Ejecútalos después del último cambio relevante:
   `python3 .claude/tools/run_acceptance.py --feature <FEATURE_ID>`.
3. Lee exit codes y salida. No uses resultados anteriores ni resúmenes sin evidencia.
4. Relaciona cada afirmación con un check concreto (`AC-NNN` → resultado).
5. Si una comprobación no puede ejecutarse, informa `BLOCKED_TOOLING` o la
   limitación exacta. No la sustituyas por confianza.
6. Solo usa `PASS` o `RESULT: completed` si todos los criterios obligatorios pasan.

Frases que delatan falta de evidencia: "debería funcionar", "parece correcto",
"casi verde", "probablemente pasa", "lo comprobé antes".

## Salida mínima

- comando o procedimiento ejecutado
- resultado y exit code cuando aplique
- criterios no ejecutados y por qué
- veredicto
