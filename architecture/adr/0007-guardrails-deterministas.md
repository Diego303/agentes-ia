# 0007 · Guardrails deterministas y aprobación humana

**Estado**: aceptada

## Contexto

El agente lee contenido de terceros (mensajes de commit, notas, respuestas de otro agente)
y puede declarar incidentes, que despiertan a personas. La prompt injection no tiene una
solución completa por detección.

## Decisión

- Lista blanca de tools y límites de llamadas y pasos.
- Toda tool con efectos requiere aprobación humana con los argumentos literales.
- Cada resultado de tool se redacta y se envuelve como dato.
- Un detector heurístico marca la sesión como contaminada: a partir de ahí, las tools con
  efectos se deniegan sin opción de aprobar.

## Alternativas

- **Clasificador LLM de inyección como única barrera**. Mejor recall, pero falla de forma
  probabilística, y un fallo concedería efectos.
- **Sin aprobación para incidentes**. Más autónomo; inaceptable mientras el coste de un falso
  positivo sea despertar a la guardia.

## Consecuencias

- Una inyección no detectada todavía necesita que un humano apruebe el efecto.
- Un falso positivo solo bloquea efectos en esa sesión; el usuario puede abrir otra.
- El detector se mide en CI (precisión y recall con umbral); su recall real será menor
  que en el corpus.
