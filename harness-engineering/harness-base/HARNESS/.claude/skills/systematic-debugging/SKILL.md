---
name: systematic-debugging
description: Investiga bugs mediante reproducción, causa raíz, hipótesis y verificación. Úsala antes de corregir un fallo, test roto, regresión o comportamiento intermitente, en un repair del harness (repair-request.yaml) y siempre que la causa aún no esté demostrada.
---

# Systematic Debugging

## Bucle

1. Reproduce el fallo con el caso más pequeño y registra comando, entrada y
   salida observada.
2. Traza el flujo real y localiza dónde aparece por primera vez el estado incorrecto.
3. Formula una hipótesis falsable. Cambia una variable cada vez.
4. Confirma la causa con una prueba que falle antes de la corrección.
5. Corrige en el punto compartido más cercano a la causa, dentro del alcance:
   un arreglo en la función común es un diff menor que parchear cada llamador
   y no deja a los demás rotos.
6. Ejecuta la prueba de reproducción y la regresión relevante.
7. Documenta evidencia y limitaciones. No declares resuelto un fallo que no
   pudiste reproducir o verificar.

## En un repair del harness

- Reproduce cada `failing_checks` con
  `python3 .claude/tools/run_acceptance.py --feature <ID> --only AC-NNN`
  (la ejecución parcial no sobrescribe los resultados completos).
- El arreglo se limita a `allowed_scope` de `repair-request.yaml`.
- Anota causa raíz y evidencia en `implementation.md` (`## Build <n>`).

## Escalado

Detente (`RESULT: blocked`) si la corrección exige cambiar requisitos, diseño o
aceptación, tocar datos de forma destructiva, credenciales o sistemas externos.
